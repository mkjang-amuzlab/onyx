"""Shared helpers for computing chat/search policy.

This module centralizes the policy decisions that are needed by both the web
chat flow and the Slack (federated) flow.

These helpers are intentionally pure and must remain aligned with the
heuristics historically implemented in `onyx.chat.process_message`.
"""

from __future__ import annotations

from dataclasses import dataclass

from onyx.chat.models import ExtractedContextFiles
from onyx.chat.models import SearchParams
from onyx.configs.constants import DEFAULT_PERSONA_ID
from onyx.configs.constants import DocumentSource
from onyx.context.search.models import BaseFilters
from onyx.tools.models import SearchToolUsage


@dataclass(frozen=True, slots=True)
class ChatSearchPolicy:
    """Normalized, reusable search policy decisions for a single chat turn."""

    # IDs and forcing behavior used by tool construction and search scoping.
    search_params: SearchParams

    # A lightweight hint that callers can use to bias prompting/routing toward
    # internal search (without changing tool availability).
    prefer_internal_search: bool

    # Whether federated Slack search should be enabled for the request.
    enable_slack_search: bool


def should_enable_slack_search(
    persona_id: int,
    filters: BaseFilters | None,
) -> bool:
    """Return True if federated Slack search should be enabled.

    Parity with the historical `onyx.chat.process_message._should_enable_slack_search`:
    - Source type filter exists and includes Slack, OR
    - Default persona with no source type filter.
    """

    source_types = filters.source_type if filters else None
    return (source_types is not None and DocumentSource.SLACK in source_types) or (
        persona_id == DEFAULT_PERSONA_ID and source_types is None
    )


def determine_search_params(
    persona_id: int,
    project_id: int | None,
    extracted_context_files: ExtractedContextFiles,
) -> SearchParams:
    """Resolve vector DB scoping filters and search-tool forcing for a chat turn.

    This is a direct extraction of the logic historically implemented in
    `onyx.chat.process_message.determine_search_params`.
    """

    is_custom_persona = persona_id != DEFAULT_PERSONA_ID

    project_id_filter: int | None = None
    persona_id_filter: int | None = None
    if extracted_context_files.use_as_search_filter:
        if is_custom_persona:
            persona_id_filter = persona_id
        else:
            project_id_filter = project_id

    search_usage = SearchToolUsage.AUTO
    if not is_custom_persona and project_id:
        has_context_files = bool(extracted_context_files.uncapped_token_count)
        files_loaded_in_context = bool(extracted_context_files.file_texts)

        if extracted_context_files.use_as_search_filter:
            search_usage = SearchToolUsage.ENABLED
        elif files_loaded_in_context or not has_context_files:
            search_usage = SearchToolUsage.DISABLED

    return SearchParams(
        project_id_filter=project_id_filter,
        persona_id_filter=persona_id_filter,
        search_usage=search_usage,
    )


def compute_chat_search_policy(
    *,
    persona_id: int,
    project_id: int | None,
    extracted_context_files: ExtractedContextFiles,
    filters: BaseFilters | None,
) -> ChatSearchPolicy:
    """Compute the shared internal-search and Slack-search policy for a turn."""

    search_params = determine_search_params(
        persona_id=persona_id,
        project_id=project_id,
        extracted_context_files=extracted_context_files,
    )

    enable_slack_search = should_enable_slack_search(persona_id, filters)

    # "Prefer internal search" is a hint (not a forcing setting). Today, the
    # strongest signal we have is that knowledge exists but couldn't be loaded
    # into the prompt and thus must be retrieved via internal search.
    prefer_internal_search = bool(extracted_context_files.use_as_search_filter)

    return ChatSearchPolicy(
        search_params=search_params,
        prefer_internal_search=prefer_internal_search,
        enable_slack_search=enable_slack_search,
    )

