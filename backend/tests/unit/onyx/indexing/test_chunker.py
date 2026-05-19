from typing import Any
from unittest.mock import Mock

import pytest

from onyx.configs.constants import DocumentSource
from onyx.connectors.models import Document
from onyx.connectors.models import TextSection
from onyx.configs.app_configs import USE_CHUNK_SUMMARY
from onyx.configs.app_configs import USE_DOCUMENT_SUMMARY
from onyx.indexing.chunker import Chunker
from onyx.indexing.embedder import DefaultIndexingEmbedder
from onyx.indexing.indexing_pipeline import process_image_sections
from onyx.llm.utils import MAX_CONTEXT_TOKENS
from tests.unit.onyx.indexing.conftest import MockHeartbeat


@pytest.mark.parametrize("enable_contextual_rag", [True, False])
def test_chunk_document(
    embedder: DefaultIndexingEmbedder, enable_contextual_rag: bool
) -> None:
    short_section_1 = "This is a short section."
    long_section = (
        "This is a long section that should be split into multiple chunks. " * 100
    )
    short_section_2 = "This is another short section."
    short_section_3 = "This is another short section again."
    short_section_4 = "Final short section."
    semantic_identifier = "Test Document"

    document = Document(
        id="test_doc",
        source=DocumentSource.WEB,
        semantic_identifier=semantic_identifier,
        metadata={"tags": ["tag1", "tag2"]},
        doc_updated_at=None,
        sections=[
            TextSection(text=short_section_1, link="link1"),
            TextSection(text=short_section_2, link="link2"),
            TextSection(text=long_section, link="link3"),
            TextSection(text=short_section_3, link="link4"),
            TextSection(text=short_section_4, link="link5"),
        ],
    )
    indexing_documents = process_image_sections([document])

    mock_llm_invoke_count = 0

    def mock_llm_invoke(
        self: Any, *args: Any, **kwargs: Any  # noqa: ARG001
    ) -> Mock:  # noqa: ARG001
        nonlocal mock_llm_invoke_count
        mock_llm_invoke_count += 1
        m = Mock()
        m.content = f"Test{mock_llm_invoke_count}"
        return m

    mock_llm = Mock()
    mock_llm.invoke = mock_llm_invoke

    chunker = Chunker(
        tokenizer=embedder.embedding_model.tokenizer,
        enable_multipass=False,
        enable_contextual_rag=enable_contextual_rag,
    )
    chunks = chunker.chunk(indexing_documents)

    assert len(chunks) == 5
    assert short_section_1 in chunks[0].content
    assert short_section_3 in chunks[-1].content
    assert short_section_4 in chunks[-1].content
    assert "tag1" in chunks[0].metadata_suffix_keyword
    assert "tag2" in chunks[0].metadata_suffix_semantic

    rag_tokens = MAX_CONTEXT_TOKENS * (
        int(USE_DOCUMENT_SUMMARY) + int(USE_CHUNK_SUMMARY)
    )
    for chunk in chunks:
        assert chunk.contextual_rag_reserved_tokens == (
            rag_tokens if enable_contextual_rag else 0
        )


def test_chunker_heartbeat(
    embedder: DefaultIndexingEmbedder, mock_heartbeat: MockHeartbeat
) -> None:
    document = Document(
        id="test_doc",
        source=DocumentSource.WEB,
        semantic_identifier="Test Document",
        metadata={"tags": ["tag1", "tag2"]},
        doc_updated_at=None,
        sections=[
            TextSection(text="This is a short section.", link="link1"),
        ],
    )
    indexing_documents = process_image_sections([document])

    chunker = Chunker(
        tokenizer=embedder.embedding_model.tokenizer,
        enable_multipass=False,
        callback=mock_heartbeat,
        enable_contextual_rag=False,
    )

    chunks = chunker.chunk(indexing_documents)

    assert mock_heartbeat.call_count == 1
    assert len(chunks) > 0


def test_chunker_uses_file_specific_document_chunker_only_for_file_documents(
    embedder: DefaultIndexingEmbedder, monkeypatch: pytest.MonkeyPatch
) -> None:
    import onyx.indexing.chunker as chunker_module

    file_document = Document(
        id="file_doc",
        source=DocumentSource.FILE,
        semantic_identifier="File Document",
        metadata={},
        doc_updated_at=None,
        sections=[TextSection(text="광고검출 시스템 개요", link="file-link")],
    )
    indexing_documents = process_image_sections([file_document])

    file_helper_called = False

    class StubDocumentChunker:
        def chunk(self, *args: object, **kwargs: object):  # noqa: ANN002, ANN003
            nonlocal file_helper_called
            file_helper_called = True
            return []

    def build_stub_document_chunker(**kwargs: object) -> StubDocumentChunker:  # noqa: ARG001
        return StubDocumentChunker()

    monkeypatch.setattr(
        chunker_module,
        "FILE_CONNECTOR_STRUCTURE_AWARE_CHUNKING",
        True,
        raising=False,
    )
    monkeypatch.setattr(
        chunker_module,
        "build_file_document_chunker",
        build_stub_document_chunker,
        raising=False,
    )

    chunker = Chunker(
        tokenizer=embedder.embedding_model.tokenizer,
        enable_multipass=False,
        enable_contextual_rag=False,
    )
    chunker.chunk(indexing_documents)

    assert file_helper_called is True
