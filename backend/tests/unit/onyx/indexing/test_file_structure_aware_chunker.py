from chonkie import SentenceChunker

from onyx.configs.constants import DocumentSource
from onyx.connectors.models import IndexingDocument
from onyx.connectors.models import TextSection
from onyx.indexing.chunking.file_section_chunker import build_file_document_chunker
from onyx.natural_language_processing.utils import BaseTokenizer


class CharTokenizer(BaseTokenizer):
    def encode(self, string: str) -> list[int]:
        return [ord(c) for c in string]

    def tokenize(self, string: str) -> list[str]:
        return list(string)

    def decode(self, tokens: list[int]) -> str:
        return "".join(chr(t) for t in tokens)


CHUNK_LIMIT = 200


def _make_document_chunker(chunk_token_limit: int = CHUNK_LIMIT):
    def token_counter(text: str) -> int:
        return len(text)

    return build_file_document_chunker(
        tokenizer=CharTokenizer(),
        blurb_splitter=SentenceChunker(
            tokenizer_or_token_counter=token_counter,
            chunk_size=128,
            chunk_overlap=0,
            return_type="texts",
        ),
        chunk_splitter=SentenceChunker(
            tokenizer_or_token_counter=token_counter,
            chunk_size=chunk_token_limit,
            chunk_overlap=0,
            return_type="texts",
        ),
    )


def _make_doc(sections: list[TextSection], doc_id: str = "file-doc") -> IndexingDocument:
    return IndexingDocument(
        id=doc_id,
        source=DocumentSource.FILE,
        semantic_identifier=doc_id,
        title="광고검출 문서",
        metadata={},
        sections=[],
        processed_sections=sections,
    )


def test_file_chunker_keeps_heading_with_body_section() -> None:
    dc = _make_document_chunker()
    doc = _make_doc(
        sections=[
            TextSection(
                text="개요 본문입니다. 광고검출 시스템의 목적을 설명합니다.",
                link="l1",
                heading="광고검출 시스템",
            )
        ]
    )

    chunks = dc.chunk(
        document=doc,
        sections=doc.processed_sections,
        title_prefix="",
        metadata_suffix_semantic="",
        metadata_suffix_keyword="",
        content_token_limit=CHUNK_LIMIT,
    )

    assert len(chunks) == 1
    assert "광고검출 시스템" in chunks[0].content
    assert "개요 본문입니다." in chunks[0].content


def test_file_chunker_starts_new_chunk_on_new_heading() -> None:
    dc = _make_document_chunker()
    doc = _make_doc(
        sections=[
            TextSection(
                text="아키텍처 설명입니다.",
                link="l1",
                heading="아키텍처",
            ),
            TextSection(
                text="운영 절차 설명입니다.",
                link="l2",
                heading="운영 절차",
            ),
        ]
    )

    chunks = dc.chunk(
        document=doc,
        sections=doc.processed_sections,
        title_prefix="",
        metadata_suffix_semantic="",
        metadata_suffix_keyword="",
        content_token_limit=CHUNK_LIMIT,
    )

    assert len(chunks) == 2
    assert "아키텍처" in chunks[0].content
    assert "운영 절차" in chunks[1].content
