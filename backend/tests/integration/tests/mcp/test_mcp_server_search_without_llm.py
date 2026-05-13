from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.types import CallToolResult
from mcp.types import TextContent

from tests.integration.common_utils.constants import MCP_SERVER_URL
from tests.integration.common_utils.managers.api_key import APIKeyManager
from tests.integration.common_utils.managers.cc_pair import CCPairManager
from tests.integration.common_utils.managers.document import DocumentManager
from tests.integration.common_utils.managers.pat import PATManager
from tests.integration.common_utils.managers.user import UserManager
from tests.integration.common_utils.managers.user_group import UserGroupManager
from tests.integration.common_utils.test_models import AccessType
from tests.integration.common_utils.test_models import DATestAPIKey
from tests.integration.common_utils.test_models import DATestCCPair
from tests.integration.common_utils.test_models import DATestUser

MCP_TOOL_NAME = "search_indexed_documents_without_llm"
STREAMABLE_HTTP_URL = f"{MCP_SERVER_URL.rstrip('/')}/?transportType=streamable-http"


def _run_with_mcp_session(
    headers: dict[str, str],
    action: Callable[[ClientSession], Awaitable[Any]],
) -> Any:
    async def _runner() -> Any:
        async with streamablehttp_client(STREAMABLE_HTTP_URL, headers=headers) as (
            read,
            write,
            _,
        ):
            async with ClientSession(read, write) as session:
                return await action(session)

    return asyncio.run(_runner())


def _extract_tool_payload(result: CallToolResult) -> dict[str, Any]:
    if result.isError:
        raise AssertionError(f"MCP tool returned error: {result}")

    text_blocks = [
        block.text
        for block in result.content
        if isinstance(block, TextContent) and block.text
    ]
    if not text_blocks:
        raise AssertionError("Expected textual content from MCP tool result")

    return json.loads(text_blocks[-1])


def _auth_headers(user: DATestUser, name: str) -> dict[str, str]:
    pat = PATManager.create(
        name=name,
        expiration_days=7,
        user_performing_action=user,
    )
    return {"Authorization": f"Bearer {pat.token}"}


def _seed_document_and_wait_for_indexing(
    cc_pair: DATestCCPair,
    content: str,
    api_key: DATestAPIKey,
    user_performing_action: DATestUser,
) -> None:
    DocumentManager.seed_doc_with_content(
        cc_pair=cc_pair,
        content=content,
        api_key=api_key,
    )
    CCPairManager.wait_for_indexing_completion(
        cc_pair=cc_pair,
        after=None,
        user_performing_action=user_performing_action,
    )


def test_mcp_search_without_llm_tool_is_listed_and_returns_sections(
    reset: None,
    admin_user: DATestUser,
) -> None:
    api_key = APIKeyManager.create(user_performing_action=admin_user)
    cc_pair = CCPairManager.create_from_scratch(user_performing_action=admin_user)
    doc_text = "MCP CE direct retrieval happy path"
    _seed_document_and_wait_for_indexing(
        cc_pair=cc_pair,
        content=doc_text,
        api_key=api_key,
        user_performing_action=admin_user,
    )

    headers = _auth_headers(admin_user, "mcp-search-without-llm")

    async def _flow(session: ClientSession) -> tuple[Any, CallToolResult]:
        await session.initialize()
        tools = await session.list_tools()
        result = await session.call_tool(
            MCP_TOOL_NAME,
            {
                "query": doc_text,
                "limit": 5,
            },
        )
        return tools, result

    tools_result, tool_result = _run_with_mcp_session(headers, _flow)

    tool_names = {tool.name for tool in tools_result.tools}
    assert MCP_TOOL_NAME in tool_names

    payload = _extract_tool_payload(tool_result)
    assert payload["query"] == doc_text
    assert payload["backend"] == "ce_direct_search"
    assert payload["retrieval_mode"] == "hybrid"
    assert "sections" in payload
    assert "documents" not in payload
    assert payload["total_results"] >= 1
    assert isinstance(payload["sections"], list)
    assert len(payload["sections"]) >= 1

    first_section = payload["sections"][0]
    assert "document_id" in first_section
    assert "chunk_ind" in first_section
    assert "semantic_identifier" in first_section
    assert "source_type" in first_section
    assert "score" in first_section
    assert "blurb" in first_section
    assert "content" in first_section
    assert "match_highlights" in first_section
    assert "metadata" in first_section


def test_mcp_search_without_llm_respects_acl(
    reset: None,
    admin_user: DATestUser,
) -> None:
    user_without_access = UserManager.create(name="mcp-no-access-user")
    privileged_user = UserManager.create(name="mcp-access-user")

    api_key = APIKeyManager.create(user_performing_action=admin_user)
    restricted_cc_pair = CCPairManager.create_from_scratch(
        access_type=AccessType.PRIVATE,
        user_performing_action=admin_user,
    )

    user_group = UserGroupManager.create(
        user_ids=[privileged_user.id],
        cc_pair_ids=[restricted_cc_pair.id],
        user_performing_action=admin_user,
    )
    UserGroupManager.wait_for_sync(
        user_performing_action=admin_user,
        user_groups_to_check=[user_group],
    )

    restricted_text = "MCP no llm restricted content"
    _seed_document_and_wait_for_indexing(
        cc_pair=restricted_cc_pair,
        content=restricted_text,
        api_key=api_key,
        user_performing_action=admin_user,
    )

    allowed_headers = _auth_headers(privileged_user, "mcp-without-llm-allowed")
    blocked_headers = _auth_headers(user_without_access, "mcp-without-llm-blocked")

    async def _call(session: ClientSession, query: str) -> CallToolResult:
        await session.initialize()
        return await session.call_tool(MCP_TOOL_NAME, {"query": query, "limit": 5})

    allowed_result = _run_with_mcp_session(
        allowed_headers,
        lambda session: _call(session, restricted_text),
    )
    blocked_result = _run_with_mcp_session(
        blocked_headers,
        lambda session: _call(session, restricted_text),
    )

    allowed_payload = _extract_tool_payload(allowed_result)
    blocked_payload = _extract_tool_payload(blocked_result)

    assert allowed_payload["total_results"] >= 1
    assert blocked_payload["total_results"] == 0
    assert blocked_payload["sections"] == []


def test_mcp_search_without_llm_invalid_time_cutoff_is_stable(
    reset: None,
    admin_user: DATestUser,
) -> None:
    headers = _auth_headers(admin_user, "mcp-without-llm-invalid-time")

    async def _call(session: ClientSession) -> CallToolResult:
        await session.initialize()
        return await session.call_tool(
            MCP_TOOL_NAME,
            {
                "query": "stability query",
                "time_cutoff": "not-a-date",
                "limit": 3,
            },
        )

    result = _run_with_mcp_session(headers, _call)
    payload = _extract_tool_payload(result)

    assert "sections" in payload
    assert "total_results" in payload
    assert payload["backend"] == "ce_direct_search"


def test_mcp_search_without_llm_no_indexed_sources_returns_empty_payload(
    reset: None,
    admin_user: DATestUser,
) -> None:
    headers = _auth_headers(admin_user, "mcp-without-llm-no-sources")

    async def _call(session: ClientSession) -> CallToolResult:
        await session.initialize()
        return await session.call_tool(
            MCP_TOOL_NAME,
            {
                "query": "no indexed sources yet",
                "limit": 3,
            },
        )

    result = _run_with_mcp_session(headers, _call)
    payload = _extract_tool_payload(result)

    assert payload["backend"] == "ce_direct_search"
    assert payload["total_results"] == 0
    assert payload["sections"] == []
