from chonkie import SentenceChunker

from onyx.configs.constants import SECTION_SEPARATOR
from onyx.connectors.models import Section
from onyx.connectors.models import SectionType
from onyx.indexing.chunking.document_chunker import DocumentChunker
from onyx.indexing.chunking.image_section_chunker import ImageChunker
from onyx.indexing.chunking.section_chunker import AccumulatorState
from onyx.indexing.chunking.section_chunker import SectionChunkerOutput
from onyx.indexing.chunking.tabular_section_chunker import TabularChunker
from onyx.indexing.chunking.text_section_chunker import TextChunker
from onyx.natural_language_processing.utils import BaseTokenizer


class FileTextChunker(TextChunker):
    def chunk_section(
        self,
        section: Section,
        accumulator: AccumulatorState,
        content_token_limit: int,
    ) -> SectionChunkerOutput:
        heading = (section.heading or "").strip()
        if not heading:
            return super().chunk_section(
                section=section,
                accumulator=accumulator,
                content_token_limit=content_token_limit,
            )

        heading_prefix = heading
        if section.text:
            heading_prefix = f"{heading}{SECTION_SEPARATOR}{section.text}"

        section_with_heading = section.model_copy(update={"text": heading_prefix})
        flushed_payloads = accumulator.flush_to_list()
        result = super().chunk_section(
            section=section_with_heading,
            accumulator=AccumulatorState(),
            content_token_limit=content_token_limit,
        )
        return SectionChunkerOutput(
            payloads=flushed_payloads + result.payloads,
            accumulator=result.accumulator,
        )


def build_file_document_chunker(
    *,
    tokenizer: BaseTokenizer,
    blurb_splitter: SentenceChunker,
    chunk_splitter: SentenceChunker,
    mini_chunk_splitter: SentenceChunker | None = None,
) -> DocumentChunker:
    document_chunker = DocumentChunker(
        tokenizer=tokenizer,
        blurb_splitter=blurb_splitter,
        chunk_splitter=chunk_splitter,
        mini_chunk_splitter=mini_chunk_splitter,
    )
    document_chunker._dispatch = {
        SectionType.TEXT: FileTextChunker(
            tokenizer=tokenizer,
            chunk_splitter=chunk_splitter,
        ),
        SectionType.IMAGE: ImageChunker(),
        SectionType.TABULAR: TabularChunker(tokenizer=tokenizer),
    }
    return document_chunker
