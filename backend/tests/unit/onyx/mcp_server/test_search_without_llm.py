from __future__ import annotations

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock
from unittest.mock import Mock
from unittest.mock import patch

from onyx.mcp_server.auth import OnyxTokenVerifier
from onyx.mcp_server.output_policy import apply_mcp_output_policy
from onyx.mcp_server.search_backend_ce import _normalize_source_types
from onyx.mcp_server.search_backend_ce import _parse_time_cutoff
from onyx.mcp_server.search_backend_ce import build_empty_search_response
from onyx.mcp_server.search_backend_ce import search_indexed_sections_without_llm
from onyx.mcp_server.search_backend_ce import section_to_payload
from onyx.mcp_server.utils import resolve_user_from_access_token


def test_build_empty_search_response_returns_section_shape() -> None:
    payload = build_empty_search_response(
        query="test query",
        filters_applied={},
        error="boom",
    )

    assert payload["query"] == "test query"
    assert payload["total_results"] == 0
    assert payload["sections"] == []
    assert payload["backend"] == "ce_direct_search"
    assert payload["retrieval_mode"] == "hybrid"
    assert payload["filters_applied"] == {}
    assert payload["error"] == "boom"


def test_section_to_payload_contains_required_raw_fields() -> None:
    chunk = Mock()
    chunk.document_id = "doc-1"
    chunk.chunk_id = 7
    chunk.semantic_identifier = "doc.md"
    chunk.source_links = {0: "https://example.com/doc"}  # dict[int, str] — real type
    chunk.blurb = "matched blurb"
    chunk.source_type = "file"
    chunk.boost = 1
    chunk.hidden = False
    chunk.metadata = {"k": "v"}
    chunk.score = 0.91
    chunk.match_highlights = ["matched phrase"]
    chunk.updated_at = datetime(2026, 5, 13)
    chunk.primary_owners = ["owner-a"]
    chunk.secondary_owners = ["owner-b"]

    section = Mock()
    section.center_chunk = chunk
    section.combined_content = "full combined content"

    payload = section_to_payload(section)

    assert payload["document_id"] == "doc-1"
    assert payload["chunk_ind"] == 7
    assert payload["semantic_identifier"] == "doc.md"
    assert payload["source_type"] == "file"
    assert payload["link"] == "https://example.com/doc"
    assert payload["score"] == 0.91
    assert payload["blurb"] == "matched blurb"
    assert payload["content"] == "full combined content"
    assert payload["match_highlights"] == ["matched phrase"]
    assert payload["metadata"] == {"k": "v"}
    assert payload["primary_owners"] == ["owner-a"]
    assert payload["secondary_owners"] == ["owner-b"]
    assert payload["hidden"] is False
    assert payload["boost"] == 1


def test_parse_time_cutoff_accepts_zulu_time() -> None:
    parsed = _parse_time_cutoff("2026-05-13T00:00:00Z")

    assert parsed is not None
    assert parsed.isoformat() == "2026-05-13T00:00:00+00:00"


def test_parse_time_cutoff_invalid_returns_none() -> None:
    assert _parse_time_cutoff("not-a-date") is None


def test_normalize_source_types_skips_invalid_values() -> None:
    normalized = _normalize_source_types(["slack", "not-real", "github"])

    assert normalized == ["slack", "github"]


def test_normalize_source_types_returns_none_when_all_values_invalid() -> None:
    assert _normalize_source_types(["bad1", "bad2"]) is None


@patch(
    "onyx.mcp_server.search_backend_ce.get_indexed_sources",
    new_callable=AsyncMock,
)
def test_helper_returns_empty_payload_when_no_sources(
    mock_get_indexed_sources: AsyncMock,
) -> None:
    mock_get_indexed_sources.return_value = []

    async def _run_test() -> dict:
        return await search_indexed_sections_without_llm(
            query="no sources",
            access_token=Mock(token="token"),
            source_types=None,
            time_cutoff=None,
            limit=5,
            db_session=Mock(),
            user=Mock(),
        )

    payload = asyncio.run(_run_test())

    assert payload["total_results"] == 0
    assert payload["sections"] == []
    assert payload["error"] == "No document sources are indexed yet."


def test_output_policy_attaches_raw_policy_for_new_tool() -> None:
    shaped = apply_mcp_output_policy(
        "search_indexed_documents_without_llm",
        {
            "query": "q",
            "total_results": 0,
            "sections": [],
            "backend": "ce_direct_search",
            "retrieval_mode": "hybrid",
            "filters_applied": {},
        },
    )

    assert shaped["policy"] == {
        "mode": "raw",
        "redaction_applied": False,
        "summary_applied": False,
    }


def test_output_policy_redacts_without_raw_override(monkeypatch) -> None:
    from onyx.mcp_server import output_policy as policy

    monkeypatch.setattr(policy, "MCP_SERVER_OUTPUT_POLICY_MODE", "raw")
    monkeypatch.setattr(policy, "MCP_SERVER_ALLOW_RAW_OUTPUT", False)

    shaped = policy.apply_mcp_output_policy(
        "search_indexed_documents_without_llm",
        {
            "query": "alice@example.com",
            "total_results": 1,
            "sections": [
                {
                    "document_id": "doc-1",
                    "content": "Contact alice@example.com or call 010-1234-5678.",
                    "blurb": "alice@example.com",
                    "match_highlights": ["alice@example.com"],
                    "link": "https://example.com/doc",
                }
            ],
            "backend": "ce_direct_search",
            "retrieval_mode": "hybrid",
            "filters_applied": {},
        },
    )

    assert shaped["policy"] == {
        "mode": "redacted",
        "redaction_applied": True,
        "summary_applied": False,
    }
    assert shaped["query"] == "[REDACTED_EMAIL]"
    assert shaped["sections"][0]["content"] == (
        "Contact [REDACTED_EMAIL] or call [REDACTED_PHONE]."
    )
    assert shaped["sections"][0]["blurb"] == "[REDACTED_EMAIL]"
    assert shaped["sections"][0]["match_highlights"] == ["[REDACTED_EMAIL]"]
    assert shaped["sections"][0]["link"] == "https://example.com/doc"


@patch("onyx.mcp_server.auth.get_http_client")
def test_auth_verifier_captures_me_claims(mock_get_http_client: Mock) -> None:
    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "id": "11111111-1111-1111-1111-111111111111",
        "email": "user@example.com",
    }
    mock_get_http_client.return_value.get = AsyncMock(return_value=response)

    async def _run_test() -> object | None:
        return await OnyxTokenVerifier().verify_token("bearer-token")

    access_token = asyncio.run(_run_test())

    assert access_token is not None
    assert access_token.claims["id"] == "11111111-1111-1111-1111-111111111111"
    assert access_token.claims["email"] == "user@example.com"


@patch("onyx.mcp_server.utils.get_http_client")
def test_resolve_user_from_access_token_uses_claims_first(
    mock_get_http_client: Mock,
) -> None:
    access_token = Mock(
        token="token",
        claims={
            "id": "11111111-1111-1111-1111-111111111111",
            "email": "user@example.com",
        },
    )

    db_session = Mock()
    expected_user = Mock()
    db_session.scalar.return_value = expected_user

    async def _run_test() -> object:
        return await resolve_user_from_access_token(
            access_token,
            db_session,
        )

    resolved_user = asyncio.run(_run_test())

    assert resolved_user is expected_user
    mock_get_http_client.return_value.get.assert_not_called()


@patch("onyx.mcp_server.utils.get_http_client")
def test_resolve_user_from_access_token_falls_back_to_me_api(
    mock_get_http_client: Mock,
) -> None:
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = {
        "id": "11111111-1111-1111-1111-111111111111",
        "email": "user@example.com",
    }
    mock_get_http_client.return_value.get = AsyncMock(return_value=response)

    db_session = Mock()
    expected_user = Mock()
    db_session.scalar.return_value = expected_user

    async def _run_test() -> object:
        return await resolve_user_from_access_token(
            Mock(token="token"),
            db_session,
        )

    resolved_user = asyncio.run(_run_test())

    assert resolved_user is expected_user
    assert db_session.scalar.called


@patch("onyx.mcp_server.search_backend_ce.search_pipeline")
@patch(
    "onyx.mcp_server.search_backend_ce.get_indexed_sources",
    new_callable=AsyncMock,
)
def test_helper_uses_direct_search_pipeline(
    mock_get_indexed_sources: AsyncMock, mock_search_pipeline: Mock
) -> None:
    mock_get_indexed_sources.return_value = ["file"]
    mock_search_pipeline.return_value = []

    async def _run_test() -> dict:
        return await search_indexed_sections_without_llm(
            query="direct path",
            access_token=Mock(token="token"),
            source_types=None,
            time_cutoff=None,
            limit=5,
            db_session=Mock(),
            user=Mock(),
        )

    payload = asyncio.run(_run_test())

    assert mock_search_pipeline.called
    assert payload["backend"] == "ce_direct_search"
    assert payload["sections"] == []
