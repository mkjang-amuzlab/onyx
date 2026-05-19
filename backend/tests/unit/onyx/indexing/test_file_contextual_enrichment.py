from typing import cast

from onyx.configs.constants import DocumentSource
from onyx.connectors.models import IndexingDocument
from onyx.connectors.models import TextSection
from onyx.indexing.file_contextual_enrichment import enrich_file_chunks_with_context
from onyx.indexing.models import DocAwareChunk
from onyx.llm.model_response import Choice
from onyx.llm.model_response import Message
from onyx.llm.model_response import ModelResponse
from onyx.natural_language_processing.utils import BaseTokenizer


class CharTokenizer(BaseTokenizer):
    def encode(self, string: str) -> list[int]:
        return [ord(c) for c in string]

    def tokenize(self, string: str) -> list[str]:
        return list(string)

    def decode(self, tokens: list[int]) -> str:
        return "".join(chr(t) for t in tokens)


class MockLLM:
    def __init__(self) -> None:
        self.calls = 0
        self.config = type("Config", (), {"max_input_tokens": 4096})()

    def invoke(self, *args: object, **kwargs: object) -> ModelResponse:  # noqa: ANN002, ANN003
        self.calls += 1
        return ModelResponse(
            id=f"test-{self.calls}",
            created="2024-01-01T00:00:00Z",
            choice=Choice(message=Message(content=f"summary-{self.calls}")),
        )


def _make_chunk(content: str, doc_id: str = "file-doc") -> DocAwareChunk:
    document = IndexingDocument(
        id=doc_id,
        source=DocumentSource.FILE,
        semantic_identifier=doc_id,
        title="광고검출 문서",
        metadata={},
        sections=[],
        processed_sections=[TextSection(text=content, link="file-link")],
    )
    return DocAwareChunk(
        source_document=document,
        chunk_id=0,
        blurb=content[:20],
        content=content,
        source_links={0: "file-link"},
        image_file_id=None,
        section_continuation=False,
        title_prefix="",
        metadata_suffix_semantic="",
        metadata_suffix_keyword="",
        contextual_rag_reserved_tokens=64,
        doc_summary="",
        chunk_context="",
        mini_chunk_texts=None,
        large_chunk_id=None,
    )


def test_file_enrichment_generates_short_doc_summary_for_file_chunks() -> None:
    llm = MockLLM()
    tokenizer = CharTokenizer()
    chunks = [_make_chunk("광고검출 시스템 개요입니다.")]

    enriched = enrich_file_chunks_with_context(
        chunks=chunks,
        llm=cast(object, llm),
        tokenizer=tokenizer,
        chunk_token_limit=256,
        trunc_doc_summary_tokens=3000,
        trunc_doc_chunk_tokens=3000,
    )

    assert enriched[0].doc_summary


def test_file_enrichment_generates_chunk_context_without_overwriting_content() -> None:
    llm = MockLLM()
    tokenizer = CharTokenizer()
    chunks = [_make_chunk("광고검출 운영 절차 설명입니다.")]

    enriched = enrich_file_chunks_with_context(
        chunks=chunks,
        llm=cast(object, llm),
        tokenizer=tokenizer,
        chunk_token_limit=256,
        trunc_doc_summary_tokens=3000,
        trunc_doc_chunk_tokens=3000,
    )

    assert enriched[0].chunk_context
    assert "광고검출" in enriched[0].content
