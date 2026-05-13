"""Utility helpers for the Onyx MCP server."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any
from uuid import UUID

import httpx
from fastmcp.server.auth.auth import AccessToken
from fastmcp.server.dependencies import get_access_token
from sqlalchemy import select
from sqlalchemy.orm import Session

from onyx.configs.app_configs import MCP_SERVER_REDACT_SENSITIVE_OUTPUT
from onyx.configs.app_configs import MCP_SERVER_REDACT_SENSITIVE_INPUT
from onyx.configs.app_configs import MCP_SERVER_SUMMARY_MAX_CHARS
from onyx.db.models import User
from onyx.db.users import get_user_by_email
from onyx.utils.logger import setup_logger
from onyx.utils.variable_functionality import build_api_server_url_for_http_requests

logger = setup_logger()

# Shared HTTP client reused across requests
_http_client: httpx.AsyncClient | None = None

MCP_SERVER_REDACT_PERSON_NAMES = (
    os.environ.get("MCP_SERVER_REDACT_PERSON_NAMES", "true").lower() == "true"
)


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

_PERSON_NAME_CONTEXT_KEYWORDS = (
    "인원",
    "구성",
    "멤버",
    "참여",
    "담당",
    "책임",
    "팀",
    "조직",
    "배정",
    "연락",
    "작성자",
    "검토",
    "개발",
    "qa",
    "pm",
    "owner",
)

_KOREAN_NAME_STOPWORDS = {
    "개발",
    "구성",
    "인원",
    "멤버",
    "프로젝트",
    "플랫폼",
    "시스템",
    "서비스",
    "문서",
    "검토",
    "담당",
    "책임",
    "팀",
    "조직",
    "배정",
    "연락",
    "작성자",
    "참여",
    "안내",
    "요약",
    "설명",
    "분석",
    "검색",
    "답변",
    "출처",
    "근거",
    "매직",
    "플랫폼",
    "개발자",
    "담당자",
    "책임자",
    "매니저",
    "엔지니어",
    "연구원",
    "팀장",
}

_ENGLISH_PERSON_NAME_PATTERN = re.compile(
    r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2}\b"
)

_KOREAN_PERSON_NAME_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"(?<![가-힣])([가-힣]{2,3})(?=\s*님\b)"), "solo"),
    (
        re.compile(
            r"((?:PM|QA|개발자|담당자|책임자|매니저|엔지니어|연구원|팀장)\s+)([가-힣]{2,3})(?=(?:[\s,;/•\-\)\].]|$))"
        ),
        "role_prefix",
    ),
    (re.compile(r"(?<![가-힣])([가-힣]{2,3})(?=(?:[\s,;/•\-\)\].]|$))"), "solo"),
]


def _apply_redaction_patterns(text: str) -> str:
    """Apply shared sensitive-pattern redactions."""
    redacted = text
    for pattern, replacement in _REDACTION_PATTERNS:
        redacted = pattern.sub(replacement, redacted)
    return redacted


def _should_redact_person_names(text: str) -> bool:
    normalized = text.casefold()
    return any(keyword in normalized for keyword in _PERSON_NAME_CONTEXT_KEYWORDS)


def _redact_korean_person_name(match: re.Match[str]) -> str:
    candidate = match.group(1)
    if candidate in _KOREAN_NAME_STOPWORDS:
        return candidate
    return "[REDACTED_NAME]"


def _redact_korean_person_name_after_role(match: re.Match[str]) -> str:
    prefix = match.group(1)
    candidate = match.group(2)
    if candidate in _KOREAN_NAME_STOPWORDS:
        return match.group(0)
    return f"{prefix}[REDACTED_NAME]"


def redact_person_names(text: str) -> str:
    """Best-effort redaction of person names in MCP output text."""
    if not MCP_SERVER_REDACT_PERSON_NAMES or not text:
        return text
    if not _should_redact_person_names(text):
        return text

    redacted = _ENGLISH_PERSON_NAME_PATTERN.sub("[REDACTED_NAME]", text)
    for pattern, pattern_kind in _KOREAN_PERSON_NAME_PATTERNS:
        if pattern_kind == "role_prefix":
            redacted = pattern.sub(_redact_korean_person_name_after_role, redacted)
        else:
            redacted = pattern.sub(_redact_korean_person_name, redacted)
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

    redacted = _apply_redaction_patterns(text)
    redacted = redact_person_names(redacted)
    return redacted


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


async def resolve_user_from_access_token(
    access_token: AccessToken,
    db_session: Session,
) -> User:
    """Resolve the authenticated Onyx user for an MCP access token.

    MCP auth only verifies that the bearer token is accepted by `/me`. The search
    pipeline, however, needs the actual ORM `User` so that ACL filters can be
    constructed correctly.
    """
    user: User | None = None

    claims = access_token.claims or {}
    user_id = claims.get("id")
    if isinstance(user_id, str):
        try:
            parsed_user_id = UUID(user_id)
            user = db_session.scalar(
                select(User).where(User.id == parsed_user_id)
            )
        except ValueError:
            logger.warning(
                "Onyx MCP Server: Invalid token claim user id '%s' when resolving MCP user",
                user_id,
            )

    if user is None:
        email = claims.get("email")
        if isinstance(email, str) and email:
            user = get_user_by_email(email, db_session)

    if user is None:
        response = await get_http_client().get(
            f"{build_api_server_url_for_http_requests(respect_env_override_if_set=True)}/me",
            headers={"Authorization": f"Bearer {access_token.token}"},
        )
        response.raise_for_status()

        payload = response.json()
        user_id = payload.get("id")
        if isinstance(user_id, str):
            try:
                parsed_user_id = UUID(user_id)
                user = db_session.scalar(
                    select(User).where(User.id == parsed_user_id)
                )
            except ValueError:
                logger.warning(
                    "Onyx MCP Server: Invalid /me user id '%s' when resolving MCP user",
                    user_id,
                )

        if user is None:
            email = payload.get("email")
            if isinstance(email, str) and email:
                user = get_user_by_email(email, db_session)

    if user is None:
        raise RuntimeError("Failed to resolve authenticated user for MCP request")

    return user
