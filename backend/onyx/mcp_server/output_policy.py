"""Output shaping helpers for MCP tools."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from onyx.configs.app_configs import MCP_SERVER_ALLOW_RAW_OUTPUT
from onyx.configs.app_configs import MCP_SERVER_OPEN_URL_MODE
from onyx.configs.app_configs import MCP_SERVER_OUTPUT_POLICY_MODE
from onyx.configs.app_configs import MCP_SERVER_SEARCH_RESULT_MODE
from onyx.mcp_server.utils import build_safe_summary
from onyx.mcp_server.utils import redact_sensitive_output_text


@dataclass(frozen=True, slots=True)
class MCPOutputPolicyDecision:
    mode: str
    redaction_applied: bool
    summary_applied: bool


def _attach_policy(payload: dict[str, Any], decision: MCPOutputPolicyDecision) -> dict[str, Any]:
    enriched = deepcopy(payload)
    enriched["policy"] = {
        "mode": decision.mode,
        "redaction_applied": decision.redaction_applied,
        "summary_applied": decision.summary_applied,
    }
    return enriched


def _mask_text(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    return redact_sensitive_output_text(value)


def _summary_text(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    return build_safe_summary(value)


def _redact_structure(value: Any, *, preserve_keys: set[str] | None = None) -> Any:
    if isinstance(value, str):
        return redact_sensitive_output_text(value)
    if isinstance(value, list):
        return [_redact_structure(item, preserve_keys=preserve_keys) for item in value]
    if isinstance(value, dict):
        preserved = preserve_keys or set()
        redacted: dict[str, Any] = {}
        for key, item in value.items():
            if key in preserved:
                redacted[key] = item
            else:
                redacted[key] = _redact_structure(item, preserve_keys=preserve_keys)
        return redacted
    return value


def _apply_result_item_masking(item: dict[str, Any]) -> dict[str, Any]:
    masked_item = deepcopy(item)
    for key, value in list(masked_item.items()):
        if key in {"url", "link"}:
            continue
        if isinstance(value, str):
            masked_item[key] = _mask_text(value)
    return masked_item


_SEARCH_WEB_SUMMARY_FIELDS = {"snippet", "content", "text", "description", "body"}


def _apply_result_item_summary(item: dict[str, Any]) -> dict[str, Any]:
    summarized_item = deepcopy(item)
    for key, value in list(summarized_item.items()):
        if key in {"url", "link"}:
            continue
        if isinstance(value, str):
            summarized = _summary_text(value)
            summarized_item[key] = _mask_text(summarized)
    return summarized_item


def _apply_search_documents_policy(payload: dict[str, Any]) -> dict[str, Any]:
    mode = MCP_SERVER_SEARCH_RESULT_MODE
    if MCP_SERVER_OUTPUT_POLICY_MODE == "raw" and MCP_SERVER_ALLOW_RAW_OUTPUT:
        return _attach_policy(
            payload,
            MCPOutputPolicyDecision(mode="raw", redaction_applied=False, summary_applied=False),
        )

    documents = list(payload.get("documents") or [])
    processed_documents: list[dict[str, Any]] = []
    redaction_applied = False

    for doc in documents:
        if not isinstance(doc, dict):
            continue
        processed_doc = deepcopy(doc)
        content = processed_doc.get("content")
        if isinstance(content, str):
            masked = _mask_text(content)
            if masked != content:
                redaction_applied = True
            processed_doc["content"] = masked
        processed_documents.append(processed_doc)

    processed = deepcopy(payload)
    processed["documents"] = processed_documents
    decision = MCPOutputPolicyDecision(
        mode=mode,
        redaction_applied=redaction_applied,
        summary_applied=False,
    )
    return _attach_policy(processed, decision)


def _apply_open_urls_policy(payload: dict[str, Any]) -> dict[str, Any]:
    mode = MCP_SERVER_OPEN_URL_MODE
    if MCP_SERVER_OUTPUT_POLICY_MODE == "raw" and MCP_SERVER_ALLOW_RAW_OUTPUT:
        return _attach_policy(
            payload,
            MCPOutputPolicyDecision(mode="raw", redaction_applied=False, summary_applied=False),
        )

    results = list(payload.get("results") or [])
    processed_results: list[dict[str, Any]] = []
    redaction_applied = False
    summary_applied = False

    for result in results:
        if not isinstance(result, dict):
            continue
        processed_result = deepcopy(result)
        content = processed_result.get("content")
        if isinstance(content, str):
            summarized = _summary_text(content)
            if summarized != content:
                summary_applied = True
            masked = _mask_text(summarized)
            if masked != summarized:
                redaction_applied = True
            processed_result["content"] = masked
        processed_results.append(processed_result)

    processed = deepcopy(payload)
    processed["results"] = processed_results
    decision = MCPOutputPolicyDecision(
        mode=mode,
        redaction_applied=redaction_applied,
        summary_applied=summary_applied,
    )
    return _attach_policy(processed, decision)


def _apply_search_web_policy(payload: dict[str, Any]) -> dict[str, Any]:
    mode = MCP_SERVER_SEARCH_RESULT_MODE
    if MCP_SERVER_OUTPUT_POLICY_MODE == "raw" and MCP_SERVER_ALLOW_RAW_OUTPUT:
        return _attach_policy(
            payload,
            MCPOutputPolicyDecision(mode="raw", redaction_applied=False, summary_applied=False),
        )

    results = list(payload.get("results") or [])
    processed_results: list[dict[str, Any]] = []
    redaction_applied = False
    summary_applied = False

    for result in results:
        if not isinstance(result, dict):
            continue
        if any(
            key in _SEARCH_WEB_SUMMARY_FIELDS and isinstance(value, str)
            for key, value in result.items()
        ):
            processed_result = _apply_result_item_summary(result)
            if processed_result != result:
                summary_applied = True
                redaction_applied = True
        else:
            processed_result = _apply_result_item_masking(result)
            if processed_result != result:
                redaction_applied = True
        processed_results.append(processed_result)

    processed = deepcopy(payload)
    processed["results"] = processed_results
    decision = MCPOutputPolicyDecision(
        mode=mode,
        redaction_applied=redaction_applied,
        summary_applied=summary_applied,
    )
    return _attach_policy(processed, decision)


def _apply_search_without_llm_policy(payload: dict[str, Any]) -> dict[str, Any]:
    if MCP_SERVER_OUTPUT_POLICY_MODE == "raw" and MCP_SERVER_ALLOW_RAW_OUTPUT:
        return _attach_policy(
            payload,
            MCPOutputPolicyDecision(
                mode="raw",
                redaction_applied=False,
                summary_applied=False,
            ),
        )

    processed = deepcopy(payload)
    sections = list(processed.get("sections") or [])
    processed_sections: list[dict[str, Any]] = []
    redaction_applied = False

    for section in sections:
        if not isinstance(section, dict):
            continue
        processed_section = _redact_structure(
            section,
            preserve_keys={"link", "url"},
        )
        if processed_section != section:
            redaction_applied = True
        processed_sections.append(processed_section)

    processed["sections"] = processed_sections
    return _attach_policy(
        processed,
        MCPOutputPolicyDecision(
            mode="redacted",
            redaction_applied=redaction_applied,
            summary_applied=False,
        ),
    )


def apply_mcp_output_policy(tool_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Apply tool-specific output shaping before returning MCP payloads."""
    cloned = deepcopy(payload)

    if tool_name == "search_indexed_documents":
        return _apply_search_documents_policy(cloned)
    if tool_name == "search_indexed_documents_without_llm":
        return _apply_search_without_llm_policy(cloned)
    if tool_name == "search_web":
        return _apply_search_web_policy(cloned)
    if tool_name == "open_urls":
        return _apply_open_urls_policy(cloned)

    return _attach_policy(
        cloned,
        MCPOutputPolicyDecision(mode="passthrough", redaction_applied=False, summary_applied=False),
    )
