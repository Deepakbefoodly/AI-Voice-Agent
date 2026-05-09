import asyncio
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from functools import lru_cache
from typing import Any

from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from guardrails import Guard
from pydantic import ValidationError

from src.services.elevenlabs_tts_service import synthesize_speech, asynthesize_speech
from src.config import GEMINI_API_KEY
from src.rag.embeddings import embed_text
from src.rag.prompt import get_rag_prompt
from src.rag.vector_store import similarity_search
from src.schemas.guardrail import RAGOutput, RAGQueryInput


logger = logging.getLogger(__name__)

DEFAULT_TOP_K = 3
SAFE_INPUT_ERROR = "Please provide a valid question."
SAFE_OUTPUT_ERROR = "I’m sorry, I couldn’t produce a safe response."

@dataclass(frozen=True)
class RAGVoiceResponse:
    answer: str
    audio_path: Path
    audio_filename: str
    audio_media_type: str


@lru_cache(maxsize=1)
def _get_llm() -> ChatGoogleGenerativeAI:
    """
    Create and return the LLM instance.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not configured.")

    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=GEMINI_API_KEY,
        temperature=0.3,
    )

@lru_cache(maxsize=1)
def _get_output_guard() -> Guard:
    try:
        return Guard.for_pydantic(output_class=RAGOutput)
    except TypeError:
        return Guard.for_pydantic(RAGOutput)

def _build_chain():
    """
        Build the RAG generation chain.
    """
    return get_rag_prompt() | _get_llm() | StrOutputParser()

def _format_docs(docs: list[dict[str, Any]]) -> str:
    """
    Convert retrieved vector-store results into a single context string.
    """
    if not docs:
        return ""

    formatted_docs: list[str] = []

    for index, doc in enumerate(docs, start=1):
        content = doc.get("content", "")
        metadata = doc.get("metadata", {}) or {}

        source = metadata.get("source")
        title = metadata.get("title")

        header_parts = [f"Document {index}"]

        if title:
            header_parts.append(f"Title: {title}")

        if source:
            header_parts.append(f"Source: {source}")

        header = " | ".join(header_parts)

        formatted_docs.append(f"{header}\n{content}")

    return "\n\n---\n\n".join(formatted_docs)

def _strip_json_fence(value: str) -> str:
    cleaned = value.strip()

    fenced_match = re.match(
        r"^```(?:json)?\s*(.*?)\s*```$",
        cleaned,
        flags=re.IGNORECASE | re.DOTALL,
    )

    if fenced_match:
        return fenced_match.group(1).strip()

    return cleaned

def _coerce_guarded_output(value: Any) -> RAGOutput:
    if isinstance(value, RAGOutput):
        return value

    if isinstance(value, dict):
        return RAGOutput.model_validate(value)

    if isinstance(value, str):
        return RAGOutput.model_validate_json(_strip_json_fence(value))

    return RAGOutput.model_validate(value)

def _validate_output(raw_output: str) -> str:
    guard = _get_output_guard()
    validation_result = guard.validate(_strip_json_fence(raw_output))

    validation_passed = getattr(validation_result, "validation_passed", True)
    if validation_passed is False:
        raise ValueError("Guardrails output validation failed.")

    validated_output = getattr(
        validation_result,
        "validated_output",
        validation_result,
    )

    return _coerce_guarded_output(validated_output).answer


def retrieve_context(
    question: str,
    top_k: int = DEFAULT_TOP_K,
) -> str:
    """
    Retrieve relevant context from the vector store for a question.
    """
    if not question or not question.strip():
        return ""

    validated_input = RAGQueryInput(
        question=question,
        top_k=top_k,
    )

    query_embedding = embed_text(validated_input.question)

    if not query_embedding:
        return ""

    docs = similarity_search(
        query_embedding=query_embedding,
        top_k=validated_input.top_k
,
    )

    return _format_docs(docs)


def query(
    question: str,
    top_k: int = DEFAULT_TOP_K,
) -> str:
    """
    Sync RAG query function. Useful for REST APIs.
    """
    try:
        validated_input = RAGQueryInput(
            question=question,
            top_k=top_k,
        )
    except ValidationError:
        logger.info("Rejected invalid RAG input.")
        return SAFE_INPUT_ERROR

    try:
        context = retrieve_context(
            question=validated_input.question,
            top_k=validated_input.top_k,
        )
        raw_output = _build_chain().invoke(
            {
                "context": context,
                "input": validated_input.question,
            }
        )

        return _validate_output(raw_output)

    except Exception as e:
        logger.exception("RAG query failed.", exc_info=e)
        return SAFE_OUTPUT_ERROR

def query_with_voice(question: str, top_k: int = 3) -> RAGVoiceResponse:
    answer = query(question=question, top_k=top_k)
    speech = synthesize_speech(answer)

    return RAGVoiceResponse(
        answer=answer,
        audio_path=speech.file_path,
        audio_filename=speech.filename,
        audio_media_type=speech.media_type,
    )



async def aretrieve_context(
    question: str,
    top_k: int = DEFAULT_TOP_K,
) -> str:
    """
    Async wrapper for retrieving relevant context.
    Chroma querying is sync here, so it is moved to a background thread.
    """
    return await asyncio.to_thread(
        retrieve_context,
        question,
        top_k,
    )


async def aquery(
    question: str,
    top_k: int = DEFAULT_TOP_K,
) -> str:
    """
    Async RAG query function.

    Useful for WebSocket or streaming systems.
    """
    try:
        validated_input = RAGQueryInput(
            question=question,
            top_k=top_k,
        )
    except ValidationError:
        logger.info("Rejected invalid async RAG input.")
        return SAFE_INPUT_ERROR

    try:
        context = await aretrieve_context(
            question=validated_input.question,
            top_k=validated_input.top_k,
        )

        raw_output = await _build_chain().ainvoke(
            {
                "context": context,
                "input": validated_input.question,
            }
        )

        return _validate_output(raw_output)

    except Exception as e:
        logger.exception("Async RAG query failed.", exc_info=e)
        return SAFE_OUTPUT_ERROR

async def aquery_with_voice(question: str, top_k: int = 3) -> RAGVoiceResponse:
    answer = await aquery(question=question, top_k=top_k)
    speech = await asynthesize_speech(answer)

    return RAGVoiceResponse(
        answer=answer,
        audio_path=speech.file_path,
        audio_filename=speech.filename,
        audio_media_type=speech.media_type,
    )


# class RAGService:
#     #  Backward-compatible `RAGService` class wrapper
#     def query(self, question: str, top_k: int = DEFAULT_TOP_K) -> str:
#         return query(
#             question=question,
#             top_k=top_k,
#         )
#
#     async def aquery(self, question: str, top_k: int = DEFAULT_TOP_K) -> str:
#         return await aquery(
#             question=question,
#             top_k=top_k,
#         )
