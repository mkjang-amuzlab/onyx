from __future__ import annotations

from onyx.chat.models import ExtractedContextFiles
from onyx.chat.search_policy import compute_chat_search_policy
from onyx.chat.search_policy import should_enable_slack_search
from onyx.configs.constants import DEFAULT_PERSONA_ID
from onyx.configs.constants import DocumentSource
from onyx.context.search.models import BaseFilters
from onyx.tools.models import SearchToolUsage


def _make_context(
    *,
    use_as_search_filter: bool = False,
    file_texts: list[str] | None = None,
    uncapped_token_count: int | None = None,
) -> ExtractedContextFiles:
    return ExtractedContextFiles(
        file_texts=file_texts or [],
        image_files=[],
        use_as_search_filter=use_as_search_filter,
        total_token_count=0,
        file_metadata=[],
        uncapped_token_count=uncapped_token_count,
    )


class TestComputeChatSearchPolicy:
    def test_internal_content_intent_prefers_search(self) -> None:
        """When internal content exists but can't fit in context, prefer internal search."""
        policy = compute_chat_search_policy(
            persona_id=DEFAULT_PERSONA_ID,
            project_id=123,
            extracted_context_files=_make_context(
                use_as_search_filter=True,
                file_texts=[],
                uncapped_token_count=7000,
            ),
            filters=None,
        )

        assert policy.prefer_internal_search is True
        assert policy.search_params.search_usage == SearchToolUsage.ENABLED
        assert policy.search_params.project_id_filter == 123
        assert policy.search_params.persona_id_filter is None

    def test_conversational_only_does_not_force_search(self) -> None:
        """For conversational-only requests, do not force internal search."""
        policy = compute_chat_search_policy(
            persona_id=DEFAULT_PERSONA_ID,
            project_id=None,
            extracted_context_files=_make_context(
                use_as_search_filter=False,
                file_texts=[],
                uncapped_token_count=None,
            ),
            filters=None,
        )

        assert policy.prefer_internal_search is False
        assert policy.search_params.search_usage != SearchToolUsage.ENABLED


class TestSlackSearchEnablementParity:
    def test_filter_includes_slack_enables_slack_search(self) -> None:
        filters = BaseFilters(source_type=[DocumentSource.SLACK])
        assert should_enable_slack_search(persona_id=999, filters=filters) is True

    def test_filter_excludes_slack_disables_slack_search(self) -> None:
        filters = BaseFilters(source_type=[DocumentSource.WEB])
        assert (
            should_enable_slack_search(persona_id=DEFAULT_PERSONA_ID, filters=filters)
            is False
        )

    def test_default_persona_no_source_filter_enables_slack_search(self) -> None:
        filters = BaseFilters(source_type=None)
        assert (
            should_enable_slack_search(persona_id=DEFAULT_PERSONA_ID, filters=filters)
            is True
        )

    def test_custom_persona_no_source_filter_disables_slack_search(self) -> None:
        filters = BaseFilters(source_type=None)
        assert should_enable_slack_search(persona_id=42, filters=filters) is False

