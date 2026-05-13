"""CE direct search helper for MCP tool without LLM invocation."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fastmcp.server.auth.auth import AccessToken
from onyx.db.models import User

from onyx.configs.constants import DocumentSource
from onyx.context.search.models import BaseFilters
from onyx.context.search.models import ChunkSearchRequest
from onyx.context.search.pipeline import merge_individual_chunks
from onyx.context.search.pipeline import search_pipeline
from onyx.db.search_settings import get_current_search_settings
from onyx.document_index.factory import get_default_document_index
from onyx.mcp_server.utils import get_indexed_sources
from onyx.utils.logger import setup_logger

logger = setup_logger()


def build_empty_search_response(
    *,
    query: str,
    filters_applied: dict[str, Any],
    error: str | None = None,
) -> dict[str, Any]:
    """Build an empty section-based response payload."""
    payload = {
        "query": query,
        "total_results": 0,
        "sections": [],
        "backend": "ce_direct_search",
        "retrieval_mode": "hybrid",
        "filters_applied": filters_applied,
    }
    if error:
        payload["error"] = error
    return payload


def section_to_payload(section: Any) -> dict[str, Any]:
    """Map a merged section object to the MCP raw response shape."""
    chunk = section.center_chunk
    return {
        "document_id": chunk.document_id,
        "chunk_ind": chunk.chunk_id,
        "semantic_identifier": chunk.semantic_identifier or "Unknown",
        "source_type": chunk.source_type,
        "link": chunk.source_links.get(0) if chunk.source_links else None,
        "score": chunk.score,
        "blurb": chunk.blurb,
        "content": section.combined_content,
        "match_highlights": chunk.match_highlights,
        "updated_at": chunk.updated_at.isoformat() if chunk.updated_at else None,
        "metadata": chunk.metadata,
        "primary_owners": chunk.primary_owners,
        "secondary_owners": chunk.secondary_owners,
        "hidden": chunk.hidden,
        "boost": chunk.boost,
    }


def _parse_time_cutoff(time_cutoff: str | None) -> datetime | None:
    """Parse ISO 8601 time cutoff string to datetime, tolerating invalid input."""
    if not time_cutoff:
        return None
    try:
        return datetime.fromisoformat(time_cutoff.replace("Z", "+00:00"))
    except ValueError:
        logger.warning(f"Invalid time_cutoff format: {time_cutoff}, ignoring")
        return None


def _normalize_source_types(source_types: list[str] | None) -> list[str] | None:
    """Normalize source type strings to DocumentSource values, skipping invalid entries."""
    if source_types is None:
        return None

    normalized: list[str] = []
    for source_type in source_types:
        try:
            normalized.append(DocumentSource(source_type.lower()).value)
        except ValueError:
            logger.warning(f"Invalid source type: {source_type}, skipping")
            continue
    return normalized or None


async def search_indexed_sections_without_llm(
    *,
    query: str,
    access_token: AccessToken,
    source_types: list[str] | None,
    time_cutoff: str | None,
    limit: int,
    db_session: Any,
    user: User,
) -> dict[str, Any]:
    """Execute direct CE retrieval without LLM invocation."""
    logger.info(
        "Onyx MCP Server: search without llm: query=%s, limit=%s",
        query,
        limit,
    )

    available_sources = await get_indexed_sources(access_token)
    if not available_sources:
        logger.info("Onyx MCP Server: No indexed sources available")
        return build_empty_search_response(
            query=query,
            filters_applied={},
            error="No document sources are indexed yet.",
        )

    normalized_source_types = _normalize_source_types(source_types)
    parsed_time_cutoff = _parse_time_cutoff(time_cutoff)

    filters_applied: dict[str, Any] = {}
    if normalized_source_types:
        filters_applied["source_type"] = normalized_source_types
    if parsed_time_cutoff:
        filters_applied["time_cutoff"] = parsed_time_cutoff.isoformat()

    base_filters: BaseFilters | None = None
    if normalized_source_types or parsed_time_cutoff:
        base_filters = BaseFilters(
            source_type=[DocumentSource(s) for s in normalized_source_types]
            if normalized_source_types
            else None,
            time_cutoff=parsed_time_cutoff,
        )

    try:
        search_settings = get_current_search_settings(db_session)
        document_index = get_default_document_index(search_settings, None, db_session)

        chunk_request = ChunkSearchRequest(
            query=query,
            user_selected_filters=base_filters,
            limit=limit,
            hybrid_alpha=None,
        )
        chunks = search_pipeline(
            chunk_search_request=chunk_request,
            document_index=document_index,
            user=user,
            persona_search_info=None,
            db_session=db_session,
        )
        sections = merge_individual_chunks(chunks)[:limit]

        logger.info(
            "Onyx MCP Server: direct retrieval returned %s sections", len(sections)
        )

        return {
            "query": query,
            "total_results": len(sections),
            "sections": [section_to_payload(section) for section in sections],
            "backend": "ce_direct_search",
            "retrieval_mode": "hybrid",
            "filters_applied": filters_applied,
        }
    except Exception as e:
        logger.error(
            "Onyx MCP Server: direct retrieval failed: %s", e, exc_info=True
        )
        return build_empty_search_response(
            query=query,
            filters_applied=filters_applied,
            error=f"Search failed: {str(e)}",
        )
