from __future__ import annotations

from onyx.mcp_server import output_policy as policy


def test_search_documents_policy_masks_sensitive_content(monkeypatch) -> None:
    monkeypatch.setattr(policy, "MCP_SERVER_OUTPUT_POLICY_MODE", "hybrid")
    monkeypatch.setattr(policy, "MCP_SERVER_ALLOW_RAW_OUTPUT", False)
    monkeypatch.setattr(policy, "MCP_SERVER_SEARCH_RESULT_MODE", "masked_snippet")

    payload = {
        "documents": [
            {
                "semantic_identifier": "doc-1",
                "content": "Contact alice@example.com or call 010-1234-5678 for details.",
                "source_type": "slack",
                "link": "https://example.com",
                "score": 0.99,
            }
        ],
        "total_results": 1,
        "query": "test",
    }

    result = policy.apply_mcp_output_policy("search_indexed_documents", payload)

    assert result["policy"]["mode"] == "masked_snippet"
    assert result["policy"]["redaction_applied"] is True
    assert result["policy"]["summary_applied"] is False
    assert result["documents"][0]["content"] == (
        "Contact [REDACTED_EMAIL] or call [REDACTED_PHONE] for details."
    )


def test_search_documents_policy_redacts_person_names(monkeypatch) -> None:
    monkeypatch.setattr(policy, "MCP_SERVER_OUTPUT_POLICY_MODE", "hybrid")
    monkeypatch.setattr(policy, "MCP_SERVER_ALLOW_RAW_OUTPUT", False)
    monkeypatch.setattr(policy, "MCP_SERVER_SEARCH_RESULT_MODE", "masked_snippet")

    payload = {
        "documents": [
            {
                "semantic_identifier": "doc-people",
                "content": "매직플랫폼 개발 인원 구성: PM 홍길동, 개발자 김철수, QA 이영희.",
                "source_type": "slack",
                "link": "https://example.com",
                "score": 0.99,
            }
        ],
        "total_results": 1,
        "query": "인원 구성",
    }

    result = policy.apply_mcp_output_policy("search_indexed_documents", payload)

    assert result["policy"]["mode"] == "masked_snippet"
    assert result["policy"]["redaction_applied"] is True
    assert result["documents"][0]["content"] == (
        "매직플랫폼 개발 인원 구성: PM [REDACTED_NAME], 개발자 [REDACTED_NAME], QA [REDACTED_NAME]."
    )


def test_open_urls_policy_summarizes_and_redacts(monkeypatch) -> None:
    monkeypatch.setattr(policy, "MCP_SERVER_OUTPUT_POLICY_MODE", "hybrid")
    monkeypatch.setattr(policy, "MCP_SERVER_ALLOW_RAW_OUTPUT", False)
    monkeypatch.setattr(policy, "MCP_SERVER_OPEN_URL_MODE", "summary_only")

    payload = {
        "results": [
            {
                "url": "https://example.com",
                "title": "Example",
                "content": (
                    "First sentence mentions alice@example.com. "
                    "Second sentence has more context. "
                    "Third sentence closes it."
                ),
            }
        ]
    }

    result = policy.apply_mcp_output_policy("open_urls", payload)

    assert result["policy"]["mode"] == "summary_only"
    assert result["policy"]["summary_applied"] is True
    assert result["policy"]["redaction_applied"] is False
    assert "[REDACTED_EMAIL]" in result["results"][0]["content"]
    assert "Fourth sentence" not in result["results"][0]["content"]


def test_search_web_policy_masks_sensitive_result_fields(monkeypatch) -> None:
    monkeypatch.setattr(policy, "MCP_SERVER_OUTPUT_POLICY_MODE", "hybrid")
    monkeypatch.setattr(policy, "MCP_SERVER_ALLOW_RAW_OUTPUT", False)
    monkeypatch.setattr(policy, "MCP_SERVER_SEARCH_RESULT_MODE", "masked_snippet")

    payload = {
        "results": [
            {
                "title": "Example alice@example.com",
                "url": "https://example.com",
                "snippet": "Contact 010-1234-5678 for details.",
            }
        ]
    }

    result = policy.apply_mcp_output_policy("search_web", payload)

    assert result["policy"]["mode"] == "masked_snippet"
    assert result["policy"]["redaction_applied"] is True
    assert result["policy"]["summary_applied"] is True
    assert result["results"][0]["title"] == "Example [REDACTED_EMAIL]"
    assert result["results"][0]["snippet"] == "Contact [REDACTED_PHONE] for details."


def test_search_web_policy_redacts_person_names(monkeypatch) -> None:
    monkeypatch.setattr(policy, "MCP_SERVER_OUTPUT_POLICY_MODE", "hybrid")
    monkeypatch.setattr(policy, "MCP_SERVER_ALLOW_RAW_OUTPUT", False)
    monkeypatch.setattr(policy, "MCP_SERVER_SEARCH_RESULT_MODE", "masked_snippet")

    payload = {
        "results": [
            {
                "title": "매직플랫폼 개발 인원 구성 홍길동",
                "url": "https://example.com",
                "snippet": "PM 김철수, 개발자 이영희, QA 박민수",
            }
        ]
    }

    result = policy.apply_mcp_output_policy("search_web", payload)

    assert result["policy"]["redaction_applied"] is True
    assert result["policy"]["summary_applied"] is True
    assert "[REDACTED_NAME]" in result["results"][0]["title"]
    assert "[REDACTED_NAME]" in result["results"][0]["snippet"]


def test_raw_mode_can_pass_through_when_explicitly_allowed(monkeypatch) -> None:
    monkeypatch.setattr(policy, "MCP_SERVER_OUTPUT_POLICY_MODE", "raw")
    monkeypatch.setattr(policy, "MCP_SERVER_ALLOW_RAW_OUTPUT", True)

    payload = {"results": [{"content": "secret@example.com"}]}

    result = policy.apply_mcp_output_policy("open_urls", payload)

    assert result["policy"]["mode"] == "raw"
    assert result["results"][0]["content"] == "secret@example.com"
