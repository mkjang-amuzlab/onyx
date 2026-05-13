"""Search tools for MCP server - document and web search."""

from datetime import datetime
from typing import Any
from urllib.parse import urlparse

import httpx

from onyx.configs.constants import DocumentSource
from onyx.mcp_server.api import mcp_server
from onyx.mcp_server.output_policy import apply_mcp_output_policy
from onyx.mcp_server.search_backend_ce import search_indexed_sections_without_llm
from onyx.mcp_server.utils import get_http_client
from onyx.mcp_server.utils import get_indexed_sources
from onyx.mcp_server.utils import redact_sensitive_text
from onyx.mcp_server.utils import resolve_user_from_access_token
from onyx.mcp_server.utils import require_access_token
from onyx.utils.logger import setup_logger
from onyx.utils.variable_functionality import build_api_server_url_for_http_requests
from onyx.utils.variable_functionality import global_version

logger = setup_logger()


def _find_invalid_urls(urls: list[str]) -> list[str]:
    """Return URLs that are not valid http/https URLs."""
    invalid = []
    for url in urls:
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https") or not parsed.netloc:
                invalid.append(url)
        except Exception:
            invalid.append(url)
    return invalid


def _extract_error_detail(response: httpx.Response) -> str:
    """Extract a human-readable error message from a failed backend response.

    The backend returns OnyxError responses as
    ``{"error_code": "...", "detail": "..."}``.
    """
    try:
        body = response.json()
        if detail := body.get("detail"):
            return str(detail)
    except Exception:
        pass
    return f"Request failed with status {response.status_code}"


@mcp_server.tool()
async def search_indexed_documents(
    query: str,
    source_types: list[str] | None = None,
    document_set_names: list[str] | None = None,
    time_cutoff: str | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    """
    Search the user's knowledge base indexed in Onyx.
    Use this tool for information that is not public knowledge and specific to the user,
    their team, their work, or their organization/company.

    Note: In CE mode, this tool uses the chat endpoint internally which invokes an LLM
    on every call, consuming tokens and adding latency.
    Additionally, CE callers receive a truncated snippet (blurb) instead of a full document chunk,
    but this should still be sufficient for most use cases. CE mode functionality should be swapped
    when a dedicated CE search endpoint is implemented.

    In EE mode, the dedicated search endpoint is used instead.

    To find a list of available sources, use the `indexed_sources` resource.
    To find available document set names, use the `document_sets` resource.
    Returns chunks of text as search results with snippets, scores, and metadata.

    Example usage:
    ```
    {
        "query": "What is the latest status of PROJ-1234 and what is the next development item?",
        "source_types": ["jira", "google_drive", "github"],
        "document_set_names": ["Engineering Docs", "Product Specs"],
        "time_cutoff": "2025-11-24T00:00:00Z",
        "limit": 10,
    }
    ```
    """
    redacted_query = redact_sensitive_text(query)
    logger.info(
        "Onyx MCP Server: document search: redacted_query='%s', sources=%s, limit=%s",
        redacted_query,
        source_types,
        limit,
    )

    # Parse time_cutoff string to datetime if provided
    time_cutoff_dt: datetime | None = None
    if time_cutoff:
        try:
            time_cutoff_dt = datetime.fromisoformat(time_cutoff.replace("Z", "+00:00"))
        except ValueError as e:
            logger.warning(
                f"Onyx MCP Server: Invalid time_cutoff format '{time_cutoff}': {e}. Continuing without time filter."
            )
            # Continue with no time_cutoff instead of returning an error
            time_cutoff_dt = None

    # Initialize source_type_enums early to avoid UnboundLocalError
    source_type_enums: list[DocumentSource] | None = None

    # Get authenticated user from FastMCP's access token
    access_token = require_access_token()

    try:
        sources = await get_indexed_sources(access_token)
    except Exception as e:
        # Error fetching sources (network error, API failure, etc.)
        logger.error(
            "Onyx MCP Server: Error checking indexed sources: %s",
            e,
            exc_info=True,
        )
        return apply_mcp_output_policy(
            "search_indexed_documents",
            {
                "documents": [],
                "total_results": 0,
                "query": query,
                "error": f"Failed to check indexed sources: {str(e)}.",
            },
        )

    if not sources:
        logger.info("Onyx MCP Server: No indexed sources available for tenant")
        return apply_mcp_output_policy(
            "search_indexed_documents",
            {
                "documents": [],
                "total_results": 0,
                "query": query,
                "message": (
                    "No document sources are indexed yet. Add connectors or upload data "
                    "through Onyx before calling onyx_search_documents."
                ),
            },
        )

    # Convert source_types strings to DocumentSource enums if provided.
    # Any unrecognised value is rejected immediately so the caller knows the
    # filter was NOT applied (silent ignore causes phantom-filter bugs).
    if source_types is not None:
        source_type_enums = []
        invalid_types: list[str] = []
        for src in source_types:
            try:
                source_type_enums.append(DocumentSource(src.lower()))
            except ValueError:
                invalid_types.append(src)

        if invalid_types:
            valid_values = sorted(s.value for s in DocumentSource)
            return apply_mcp_output_policy(
                "search_indexed_documents",
                {
                    "documents": [],
                    "total_results": 0,
                    "query": query,
                    "error": (
                        f"Invalid source_type(s): {invalid_types}. "
                        f"Valid values are: {valid_values}"
                    ),
                },
            )

    # Build filters dict only with non-None values
    filters: dict[str, Any] | None = None
    if source_type_enums or document_set_names or time_cutoff_dt:
        filters = {}
        if source_type_enums:
            filters["source_type"] = [src.value for src in source_type_enums]
        if document_set_names:
            filters["document_set"] = document_set_names
        if time_cutoff_dt:
            filters["time_cutoff"] = time_cutoff_dt.isoformat()

    is_ee = global_version.is_ee_version()
    base_url = build_api_server_url_for_http_requests(respect_env_override_if_set=True)
    auth_headers = {"Authorization": f"Bearer {access_token.token}"}

    search_request: dict[str, Any]
    if is_ee:
        # EE: use the dedicated search endpoint (no LLM invocation)
        search_request = {
            "search_query": redacted_query,
            "filters": filters,
            "num_docs_fed_to_llm_selection": limit,
            "run_query_expansion": False,
            "include_content": True,
            "stream": False,
        }
        endpoint = f"{base_url}/search/send-search-message"
        error_key = "error"
        docs_key = "search_docs"
        content_field = "content"
    else:
        # CE: fall back to the chat endpoint (invokes LLM, consumes tokens)
        search_request = {
            "message": redacted_query,
            "stream": False,
            "chat_session_info": {},
        }
        if filters:
            search_request["internal_search_filters"] = filters
        endpoint = f"{base_url}/chat/send-chat-message"
        error_key = "error_msg"
        docs_key = "top_documents"
        content_field = "blurb"

    try:
        response = await get_http_client().post(
            endpoint,
            json=search_request,
            headers=auth_headers,
        )
        if not response.is_success:
            error_detail = _extract_error_detail(response)
            return apply_mcp_output_policy(
                "search_indexed_documents",
                {
                    "documents": [],
                    "total_results": 0,
                    "query": redacted_query,
                    "error": error_detail,
                },
            )
        result = response.json()

        # Check for error in response
        if result.get(error_key):
            return apply_mcp_output_policy(
                "search_indexed_documents",
                {
                    "documents": [],
                    "total_results": 0,
                    "query": redacted_query,
                    "error": result.get(error_key),
                },
            )

        documents = [
            {
                "semantic_identifier": doc.get("semantic_identifier"),
                "content": doc.get(content_field),
                "source_type": doc.get("source_type"),
                "link": doc.get("link"),
                "score": doc.get("score"),
            }
            for doc in result.get(docs_key, [])
        ]

        # NOTE: search depth is controlled by the backend persona defaults, not `limit`.
        # `limit` only caps the returned list; fewer results may be returned if the
        # backend retrieves fewer documents than requested.
        documents = documents[:limit]

        logger.info(
            f"Onyx MCP Server: Internal search returned {len(documents)} results"
        )
        return apply_mcp_output_policy(
            "search_indexed_documents",
            {
                "documents": documents,
                "total_results": len(documents),
                "query": redacted_query,
            },
        )
    except Exception as e:
        logger.error(f"Onyx MCP Server: Document search error: {e}", exc_info=True)
        return apply_mcp_output_policy(
            "search_indexed_documents",
            {
                "error": f"Document search failed: {str(e)}",
                "documents": [],
                "query": redacted_query,
            },
        )


@mcp_server.tool()
async def search_web(
    query: str,
    limit: int = 5,
) -> dict[str, Any]:
    """
    Search the public internet for general knowledge, current events, and publicly available information.
    Use this tool for information that is publicly available on the web,
    such as news, documentation, general facts, or when the user's private knowledge base doesn't contain relevant information.

    Returns web search results with titles, URLs, and snippets (NOT full content). Use `open_urls` to fetch full page content.

    Example usage:
    ```
    {
        "query": "React 19 migration guide to use react compiler",
        "limit": 5
    }
    ```
    """
    redacted_query = redact_sensitive_text(query)
    logger.info(
        "Onyx MCP Server: Web search: redacted_query='%s', limit=%s",
        redacted_query,
        limit,
    )

    access_token = require_access_token()

    try:
        request_payload = {"queries": [redacted_query], "max_results": limit}
        response = await get_http_client().post(
            f"{build_api_server_url_for_http_requests(respect_env_override_if_set=True)}/web-search/search-lite",
            json=request_payload,
            headers={"Authorization": f"Bearer {access_token.token}"},
        )
        if not response.is_success:
            error_detail = _extract_error_detail(response)
            return apply_mcp_output_policy(
                "search_web",
                {
                    "error": error_detail,
                    "results": [],
                    "query": redacted_query,
                },
            )
        response_payload = response.json()
        results = response_payload.get("results", [])
        return apply_mcp_output_policy(
            "search_web",
            {
                "results": results,
                "query": redacted_query,
            },
        )
    except Exception as e:
        logger.error(f"Onyx MCP Server: Web search error: {e}", exc_info=True)
        return apply_mcp_output_policy(
            "search_web",
            {
                "error": f"Web search failed: {str(e)}",
                "results": [],
                "query": redacted_query,
            },
        )


@mcp_server.tool()
async def open_urls(
    urls: list[str],
) -> dict[str, Any]:
    """
    Retrieve the complete text content from specific web URLs.
    Use this tool when you need to access full content from known URLs,
    such as documentation pages or articles returned by the `search_web` tool.

    Useful for following up on web search results when snippets do not provide enough information.

    Returns the full text content of each URL along with metadata like title and content type.

    Example usage:
    ```
    {
        "urls": ["https://react.dev/versions", "https://react.dev/learn/react-compiler","https://react.dev/learn/react-compiler/introduction"]
    }
    ```
    """
    logger.info(f"Onyx MCP Server: Open URL: fetching {len(urls)} URLs")

    invalid_urls = _find_invalid_urls(urls)
    if invalid_urls:
        return apply_mcp_output_policy(
            "open_urls",
            {
                "error": (
                    f"Invalid URL(s): {invalid_urls}. "
                    "All URLs must start with http:// or https:// and include a valid host."
                ),
                "results": [],
            },
        )

    access_token = require_access_token()

    try:
        response = await get_http_client().post(
            f"{build_api_server_url_for_http_requests(respect_env_override_if_set=True)}/web-search/open-urls",
            json={"urls": urls},
            headers={"Authorization": f"Bearer {access_token.token}"},
        )
        if not response.is_success:
            error_detail = _extract_error_detail(response)
            return apply_mcp_output_policy(
                "open_urls",
                {
                    "error": error_detail,
                    "results": [],
                },
            )
        response_payload = response.json()
        results = response_payload.get("results", [])
        return apply_mcp_output_policy(
            "open_urls",
            {
                "results": results,
            },
        )
    except Exception as e:
        logger.error(f"Onyx MCP Server: URL fetch error: {e}", exc_info=True)
        return apply_mcp_output_policy(
            "open_urls",
            {
                "error": f"URL fetch failed: {str(e)}",
                "results": [],
            },
        )


@mcp_server.tool()
async def search_indexed_documents_without_llm(
    query: str,
    source_types: list[str] | None = None,
    time_cutoff: str | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    """
    Search the user's knowledge base using direct CE retrieval without any LLM invocation.
    This tool returns raw section-level search results for advanced use cases where
    you need access to unprocessed retrieval output without chat-based processing.

    Use this when you need direct access to indexed documents without the latency
    or cost of LLM-based document selection or ranking.

    Returns section-based raw retrieval payloads with full metadata.

    To find a list of available sources, use the `indexed_sources` resource.
    To find available document sets, use the `document_sets` resource.

    Example usage:
    ```
    {
        "query": "technical specification for feature X",
        "source_types": ["confluence", "github"],
        "limit": 10,
    }
    ```
    """
    from onyx.db.engine.sql_engine import get_session_with_current_tenant

    redacted_query = redact_sensitive_text(query)
    logger.info(
        "Onyx MCP Server: search without llm: query=%s, limit=%s",
        redacted_query,
        limit,
    )

    access_token = require_access_token()

    try:
        with get_session_with_current_tenant() as db_session:
            user = await resolve_user_from_access_token(access_token, db_session)
            result = await search_indexed_sections_without_llm(
                query=redacted_query,
                access_token=access_token,
                source_types=source_types,
                time_cutoff=time_cutoff,
                limit=limit,
                db_session=db_session,
                user=user,
            )
            return apply_mcp_output_policy(
                "search_indexed_documents_without_llm",
                result,
            )
    except Exception as e:
        logger.error(
            "Onyx MCP Server: search without llm failed: %s", e, exc_info=True
        )
        return apply_mcp_output_policy(
            "search_indexed_documents_without_llm",
            {
                "query": redacted_query,
                "total_results": 0,
                "sections": [],
                "backend": "ce_direct_search",
                "retrieval_mode": "hybrid",
                "filters_applied": {},
                "error": f"Document search failed: {str(e)}",
            },
        )
