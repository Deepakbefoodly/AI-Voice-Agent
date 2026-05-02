import asyncio
from typing import Any

from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

from src.config import GEMINI_API_KEY
from src.rag.embeddings import embed_text
from src.rag.prompt import get_rag_prompt
from src.rag.vector_store import similarity_search


DEFAULT_TOP_K = 3


def _get_llm() -> ChatGoogleGenerativeAI:
    """
    Create and return the LLM instance.
    """
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=GEMINI_API_KEY,
        temperature=0.3,
    )


def _format_docs(docs: list[dict[str, Any]]) -> str:
    """
    Convert retrieved vector-store results into a single context string.
    """
    if not docs:
        return ""

    formatted_docs: list[str] = []

    for index, doc in enumerate(docs, start=1):
        content = doc.get("content", "")
        metadata = doc.get("metadata", {})

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


def _build_chain():
    """
    Build the RAG generation chain.
    """
    prompt = get_rag_prompt()
    llm = _get_llm()
    parser = StrOutputParser()

    return prompt | llm | parser


def retrieve_context(
    question: str,
    top_k: int = DEFAULT_TOP_K,
) -> str:
    """
    Retrieve relevant context from the vector store for a question.
    """
    if not question or not question.strip():
        return ""

    query_embedding = embed_text(question)
    docs = similarity_search(
        query_embedding=query_embedding,
        top_k=top_k,
    )

    return _format_docs(docs)


def query(
    question: str,
    top_k: int = DEFAULT_TOP_K,
) -> str:
    """
    Sync RAG query function.

    Useful for REST APIs.
    """
    if not question or not question.strip():
        return "Please provide a valid question."

    context = retrieve_context(
        question=question,
        top_k=top_k,
    )

    chain = _build_chain()

    return chain.invoke(
        {
            "context": context,
            "input": question,
        }
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
    if not question or not question.strip():
        return "Please provide a valid question."

    context = await aretrieve_context(
        question=question,
        top_k=top_k,
    )

    chain = _build_chain()

    return await chain.ainvoke(
        {
            "context": context,
            "input": question,
        }
    )