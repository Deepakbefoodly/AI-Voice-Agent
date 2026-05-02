from functools import lru_cache

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from src.config import GEMINI_API_KEY


EMBEDDING_MODEL = "embedding-2"


@lru_cache(maxsize=1)
def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """
    Return a cached Google Generative AI embeddings client.
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not configured.")

    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=GEMINI_API_KEY,
    )


def embed_text(text: str) -> list[float]:
    """
    Generate an embedding vector for a single query/text string.
    """
    cleaned_text = text.strip() if text else ""

    if not cleaned_text:
        return []

    embeddings = get_embeddings()
    return embeddings.embed_query(cleaned_text)


def embed_documents(texts: list[str]) -> list[list[float]]:
    """
    Generate embedding vectors for multiple document strings.
    """
    cleaned_texts = [text.strip() for text in texts if text and text.strip()]

    if not cleaned_texts:
        return []

    embeddings = get_embeddings()
    return embeddings.embed_documents(cleaned_texts)