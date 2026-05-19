from collections import defaultdict
from typing import Any

from onyx.configs.constants import DocumentSource
from onyx.indexing.models import DocAwareChunk
from onyx.llm.multi_llm import LLMRateLimitError
from onyx.llm.utils import llm_response_to_string
from onyx.llm.utils import MAX_CONTEXT_TOKENS
from onyx.natural_language_processing.utils import BaseTokenizer
from onyx.natural_language_processing.utils import tokenizer_trim_middle
from onyx.prompts.contextual_retrieval import CONTEXTUAL_RAG_PROMPT1
from onyx.prompts.contextual_retrieval import CONTEXTUAL_RAG_PROMPT2
from onyx.prompts.contextual_retrieval import DOCUMENT_SUMMARY_PROMPT
from onyx.utils.logger import setup_logger

logger = setup_logger()


def _group_file_chunks(chunks: list[DocAwareChunk]) -> tuple[list[DocAwareChunk], dict[str, list[DocAwareChunk]]]:
    non_file_chunks = []
    file_chunks_by_doc: dict[str, list[DocAwareChunk]] = defaultdict(list)

    for chunk in chunks:
        if chunk.source_document.source == DocumentSource.FILE:
            file_chunks_by_doc[chunk.source_document.id].append(chunk)
        else:
            non_file_chunks.append(chunk)

    return non_file_chunks, file_chunks_by_doc


def _add_file_document_summary(
    chunks_by_doc: list[DocAwareChunk],
    llm: Any,
    tokenizer: BaseTokenizer,
    trunc_doc_summary_tokens: int,
) -> list[int] | None:
    if not chunks_by_doc or chunks_by_doc[0].contextual_rag_reserved_tokens == 0:
        return None

    doc_tokens = tokenizer.encode(chunks_by_doc[0].source_document.get_text_content())
    doc_content = tokenizer_trim_middle(doc_tokens, trunc_doc_summary_tokens, tokenizer)
    response = llm.invoke(
        DOCUMENT_SUMMARY_PROMPT.format(document=doc_content),
        max_tokens=MAX_CONTEXT_TOKENS,
    )
    doc_summary = llm_response_to_string(response)

    for chunk in chunks_by_doc:
        chunk.doc_summary = doc_summary

    return doc_tokens


def _add_file_chunk_contexts(
    chunks_by_doc: list[DocAwareChunk],
    llm: Any,
    tokenizer: BaseTokenizer,
    trunc_doc_chunk_tokens: int,
    doc_tokens: list[int] | None,
) -> None:
    if not chunks_by_doc or chunks_by_doc[0].contextual_rag_reserved_tokens == 0:
        return

    doc_tokens = doc_tokens or tokenizer.encode(
        chunks_by_doc[0].source_document.get_text_content()
    )
    doc_content = tokenizer_trim_middle(doc_tokens, trunc_doc_chunk_tokens, tokenizer)
    doc_info = doc_content if chunks_by_doc[0].doc_summary == "" else chunks_by_doc[0].doc_summary

    if not doc_info:
        response = llm.invoke(
            DOCUMENT_SUMMARY_PROMPT.format(document=doc_content),
            max_tokens=MAX_CONTEXT_TOKENS,
        )
        doc_info = llm_response_to_string(response)

    context_prompt1 = CONTEXTUAL_RAG_PROMPT1.format(document=doc_info)

    for chunk in chunks_by_doc:
        try:
            response = llm.invoke(
                f"{context_prompt1}\n\n{CONTEXTUAL_RAG_PROMPT2.format(chunk=chunk.content)}",
                max_tokens=MAX_CONTEXT_TOKENS,
            )
            chunk.chunk_context = llm_response_to_string(response)
        except LLMRateLimitError as e:
            logger.exception(f"Rate limit adding file chunk summary: {e}", exc_info=e)
            chunk.chunk_context = ""
        except Exception as e:  # noqa: BLE001
            logger.exception(f"Error adding file chunk summary: {e}", exc_info=e)
            chunk.chunk_context = ""


def enrich_file_chunks_with_context(
    *,
    chunks: list[DocAwareChunk],
    llm: Any,
    tokenizer: BaseTokenizer,
    chunk_token_limit: int,
    trunc_doc_summary_tokens: int,
    trunc_doc_chunk_tokens: int,
) -> list[DocAwareChunk]:
    del chunk_token_limit

    _, file_chunks_by_doc = _group_file_chunks(chunks)
    for chunks_by_doc in file_chunks_by_doc.values():
        doc_tokens = _add_file_document_summary(
            chunks_by_doc=chunks_by_doc,
            llm=llm,
            tokenizer=tokenizer,
            trunc_doc_summary_tokens=trunc_doc_summary_tokens,
        )
        _add_file_chunk_contexts(
            chunks_by_doc=chunks_by_doc,
            llm=llm,
            tokenizer=tokenizer,
            trunc_doc_chunk_tokens=trunc_doc_chunk_tokens,
            doc_tokens=doc_tokens,
        )

    return chunks
