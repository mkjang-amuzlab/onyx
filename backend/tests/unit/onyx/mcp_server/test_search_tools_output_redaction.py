from __future__ import annotations

import asyncio
from typing import Any

from onyx.mcp_server.tools import search as mcp_search


class _DummyAccessToken:
    token = "fake-token"


class _DummyResponse:
    def __init__(self, payload: dict[str, Any], is_success: bool = True) -> None:
        self._payload = payload
        self.is_success = is_success
        self.status_code = 200

    def json(self) -> dict[str, Any]:
        return self._payload


class _DummyClient:
    def __init__(self, response: _DummyResponse) -> None:
        self.response = response
        self.calls: list[dict[str, Any]] = []

    async def post(self, endpoint: str, json: dict[str, Any], headers: dict[str, str]) -> _DummyResponse:  # noqa: A002
        self.calls.append({"endpoint": endpoint, "json": json, "headers": headers})
        return self.response


def test_search_indexed_documents_applies_output_policy(monkeypatch) -> None:
    monkeypatch.setattr(mcp_search, "require_access_token", lambda: _DummyAccessToken())
    monkeypatch.setattr(mcp_search, "get_indexed_sources", lambda _token: asyncio.sleep(0, result=["slack"]))
    monkeypatch.setattr(mcp_search.global_version, "is_ee_version", lambda: True)

    response = _DummyResponse(
        {
            "search_docs": [
                {
                    "semantic_identifier": "doc-1",
                    "content": "Email alice@example.com and phone 010-1234-5678.",
                    "source_type": "slack",
                    "link": "https://example.com",
                    "score": 0.9,
                }
            ]
        }
    )
    client = _DummyClient(response)
    monkeypatch.setattr(mcp_search, "get_http_client", lambda: client)

    result = asyncio.run(
        mcp_search.search_indexed_documents(query="test", source_types=None, time_cutoff=None, limit=10)
    )

    assert result["policy"]["mode"] == "masked_snippet"
    assert result["documents"][0]["content"] == (
        "Email [REDACTED_EMAIL] and phone [REDACTED_PHONE]."
    )


def test_open_urls_applies_summary_policy(monkeypatch) -> None:
    monkeypatch.setattr(mcp_search, "require_access_token", lambda: _DummyAccessToken())

    response = _DummyResponse(
        {
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
    )
    client = _DummyClient(response)
    monkeypatch.setattr(mcp_search, "get_http_client", lambda: client)

    result = asyncio.run(mcp_search.open_urls(urls=["https://example.com"]))

    assert result["policy"]["mode"] == "summary_only"
    assert "[REDACTED_EMAIL]" in result["results"][0]["content"]
    assert "Second sentence" in result["results"][0]["content"]


def test_search_web_applies_output_policy(monkeypatch) -> None:
    monkeypatch.setattr(mcp_search, "require_access_token", lambda: _DummyAccessToken())

    response = _DummyResponse(
        {
            "results": [
                {
                    "title": "Example alice@example.com",
                    "url": "https://example.com",
                    "snippet": "Call 010-1234-5678 for details.",
                }
            ]
        }
    )
    client = _DummyClient(response)
    monkeypatch.setattr(mcp_search, "get_http_client", lambda: client)

    result = asyncio.run(mcp_search.search_web(query="test", limit=5))

    assert result["policy"]["mode"] == "masked_snippet"
    assert result["results"][0]["title"] == "Example [REDACTED_EMAIL]"
    assert result["results"][0]["snippet"] == "Call [REDACTED_PHONE] for details."
