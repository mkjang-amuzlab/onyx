"""Utility helpers for the Onyx MCP server."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

import httpx
from fastmcp.server.auth.auth import AccessToken
from fastmcp.server.dependencies import get_access_token
from pydantic import BaseModel
from pydantic import TypeAdapter

from onyx.configs.app_configs import MCP_SERVER_REDACT_SENSITIVE_OUTPUT
from onyx.configs.app_configs import MCP_SERVER_REDACT_SENSITIVE_INPUT
from onyx.configs.app_configs import MCP_SERVER_SUMMARY_MAX_CHARS
from onyx.utils.logger import setup_logger
from onyx.utils.variable_functionality import build_api_server_url_for_http_requests


class DocumentSetEntry(BaseModel):
    """Minimal document-set shape surfaced to MCP clients.

    Projected from the backend's DocumentSetSummary to avoid coupling MCP to
    admin-only fields (cc-pair summaries, federated connectors, etc.).
    """

    name: str
    description: str | None = None


logger = setup_logger()

# Shared HTTP client reused across requests
_http_client: httpx.AsyncClient | None = None


@dataclass(frozen=True, slots=True)
class AccessibleDocumentSet:
    """Lightweight document-set wrapper returned by the MCP helper."""

    name: str
    payload: dict[str, Any]

    def model_dump(self, mode: str = "json") -> dict[str, Any]:  # noqa: ARG002
        return self.payload

_REDACTION_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # Email
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"), "[REDACTED_EMAIL]"),
    # International/KR phone numbers
    (re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,3}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{4}\b"), "[REDACTED_PHONE]"),
    # Korean resident registration number
    (re.compile(r"\b\d{6}[- ]?[1-4]\d{6}\b"), "[REDACTED_KR_RRN]"),
    # Credit card-ish pattern (13~19 digits with optional separators)
    (re.compile(r"\b(?:\d[ -]?){13,19}\b"), "[REDACTED_CARD]"),
]


def _apply_redaction_patterns(text: str) -> str:
    """Apply shared sensitive-pattern redactions."""
    redacted = text
    for pattern, replacement in _REDACTION_PATTERNS:
        redacted = pattern.sub(replacement, redacted)
    return redacted


def require_access_token() -> AccessToken:
    """
    Get and validate the access token from the current request.

    Raises:
        ValueError: If no access token is present in the request.

    Returns:
        AccessToken: The validated access token.
    """
    access_token = get_access_token()
    if not access_token:
        raise ValueError(
            "MCP Server requires an Onyx access token to authenticate your request"
        )
    return access_token


def get_http_client() -> httpx.AsyncClient:
    """Return a shared async HTTP client."""
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(timeout=60.0)
    return _http_client


def redact_sensitive_text(text: str) -> str:
    """Redact likely sensitive entities from MCP client-provided text."""
    if not MCP_SERVER_REDACT_SENSITIVE_INPUT or not text:
        return text

    return _apply_redaction_patterns(text)


def redact_sensitive_output_text(text: str) -> str:
    """Redact likely sensitive entities from MCP output text."""
    if not MCP_SERVER_REDACT_SENSITIVE_OUTPUT or not text:
        return text

    return _apply_redaction_patterns(text)


def build_safe_summary(text: str, max_chars: int | None = None) -> str:
    """Build a short deterministic summary that avoids direct raw leakage."""
    if not text:
        return text

    summary_max_chars = max_chars or MCP_SERVER_SUMMARY_MAX_CHARS
    redacted = redact_sensitive_output_text(text)
    normalized = " ".join(redacted.split())
    normalized = normalized.replace('"', "").replace("'", "")

    # Keep only the first few sentences to avoid verbatim long-form leakage.
    sentence_candidates = re.split(r"(?<=[.!?])\s+", normalized)
    summary = " ".join(sentence_candidates[:3]).strip()
    if not summary:
        summary = normalized[:summary_max_chars].strip()

    if len(summary) > summary_max_chars:
        summary = summary[: summary_max_chars - 3].rstrip() + "..."
    return summary


async def shutdown_http_client() -> None:
    """Close the shared HTTP client when the server shuts down."""
    global _http_client
    if _http_client is not None:
        await _http_client.aclose()
        _http_client = None


async def get_indexed_sources(
    access_token: AccessToken,
) -> list[str]:
    """
    Fetch indexed document sources for the current user/tenant.

    Returns:
        List of indexed source strings. Empty list if no sources are indexed.
    """
    headers = {"Authorization": f"Bearer {access_token.token}"}
    try:
        response = await get_http_client().get(
            f"{build_api_server_url_for_http_requests(respect_env_override_if_set=True)}/manage/indexed-sources",
            headers=headers,
        )
        response.raise_for_status()
        payload = response.json()
        sources = payload.get("sources", [])
        if not isinstance(sources, list):
            raise ValueError("Unexpected response shape for indexed sources")
        return [str(source) for source in sources]
    except (httpx.HTTPStatusError, httpx.RequestError, ValueError):
        # Re-raise known exception types (httpx errors and validation errors)
        logger.error(
            "Onyx MCP Server: Failed to fetch indexed sources",
            exc_info=True,
        )
        raise
    except Exception as exc:
        # Wrap unexpected exceptions
        logger.error(
            "Onyx MCP Server: Unexpected error fetching indexed sources",
            exc_info=True,
        )
        raise RuntimeError(f"Failed to fetch indexed sources: {exc}") from exc


_DOCUMENT_SET_ENTRIES_ADAPTER = TypeAdapter(list[DocumentSetEntry])


async def get_accessible_document_sets(
    access_token: AccessToken,
) -> list[AccessibleDocumentSet]:
    """Fetch document sets accessible to the current user."""
    headers = {"Authorization": f"Bearer {access_token.token}"}
    try:
        response = await get_http_client().get(
            f"{build_api_server_url_for_http_requests(respect_env_override_if_set=True)}/manage/document-set?get_editable=false",
            headers=headers,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list):
            raise ValueError("Unexpected response shape for document sets")

        document_sets: list[AccessibleDocumentSet] = []
        for item in payload:
            if isinstance(item, dict):
                document_sets.append(
                    AccessibleDocumentSet(
                        name=str(item.get("name") or ""),
                        payload=item,
                    )
                )
        return document_sets
    except (httpx.HTTPStatusError, httpx.RequestError, ValueError):
        logger.error(
            "Onyx MCP Server: Failed to fetch accessible document sets",
            exc_info=True,
        )
        raise
    except Exception as exc:
        logger.error(
            "Onyx MCP Server: Unexpected error fetching accessible document sets",
            exc_info=True,
        )
        raise RuntimeError(f"Failed to fetch accessible document sets: {exc}") from exc
