from typing import Any

from src.scripts.chroma_connection import get_chroma_collection


def add_documents(
    ids: list[str],
    documents: list[str],
    embeddings: list[list[float]],
    metadatas: list[dict[str, Any]] | None = None,
) -> None:
    """
    Add or update documents in the ChromaDB collection.

    Args:
        ids: Unique IDs for each document chunk.
        documents: Text chunks to store.
        embeddings: Embedding vectors for each document.
        metadatas: Optional metadata for each document.
    """
    if not ids or not documents or not embeddings:
        return

    if len(ids) != len(documents):
        raise ValueError("ids and documents must have the same length.")

    if len(documents) != len(embeddings):
        raise ValueError("documents and embeddings must have the same length.")

    if metadatas is None:
        metadatas = [{} for _ in documents]

    if len(metadatas) != len(documents):
        raise ValueError("metadatas and documents must have the same length.")

    collection = get_chroma_collection()

    collection.upsert(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )


def similarity_search(
    query_embedding: list[float],
    top_k: int = 4,
    where: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """
    Search similar documents from ChromaDB using a query embedding.

    Args:
        query_embedding: Embedding vector of the query.
        top_k: Number of similar documents to return.
        where: Optional Chroma metadata filter.

    Returns:
        List of matched documents with content, metadata, distance, and id.
    """
    if not query_embedding:
        return []

    collection = get_chroma_collection()

    query_kwargs: dict[str, Any] = {
        "query_embeddings": [query_embedding],
        "n_results": top_k,
        "include": ["documents", "metadatas", "distances"],
    }

    if where:
        query_kwargs["where"] = where

    results = collection.query(**query_kwargs)

    ids = results.get("ids", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    matches: list[dict[str, Any]] = []

    for index, document in enumerate(documents):
        matches.append(
            {
                "id": ids[index] if index < len(ids) else None,
                "content": document,
                "metadata": metadatas[index] if index < len(metadatas) else {},
                "distance": distances[index] if index < len(distances) else None,
            }
        )

    return matches


def get_document_by_id(document_id: str) -> dict[str, Any] | None:
    """
    Get a single document from ChromaDB by ID.

    Args:
        document_id: Document ID.

    Returns:
        Document data or None.
    """
    if not document_id:
        return None

    collection = get_chroma_collection()

    result = collection.get(
        ids=[document_id],
        include=["documents", "metadatas"],
    )

    ids = result.get("ids", [])
    documents = result.get("documents", [])
    metadatas = result.get("metadatas", [])

    if not ids:
        return None

    return {
        "id": ids[0],
        "content": documents[0] if documents else "",
        "metadata": metadatas[0] if metadatas else {},
    }


def delete_documents(ids: list[str]) -> None:
    """
    Delete documents from ChromaDB by IDs.

    Args:
        ids: List of document IDs to delete.
    """
    if not ids:
        return

    collection = get_chroma_collection()
    collection.delete(ids=ids)


def delete_documents_by_metadata(where: dict[str, Any]) -> None:
    """
    Delete documents matching a metadata filter.

    Args:
        where: Chroma metadata filter.
    """
    if not where:
        return

    collection = get_chroma_collection()
    collection.delete(where=where)


def count_documents() -> int:
    """
    Count documents in the ChromaDB collection.

    Returns:
        Number of stored documents.
    """
    collection = get_chroma_collection()
    return collection.count()


def reset_collection() -> None:
    """
    Delete all documents from the current ChromaDB collection.

    Useful during local development or re-indexing.
    """
    collection = get_chroma_collection()

    existing = collection.get(include=[])

    ids = existing.get("ids", [])

    if ids:
        collection.delete(ids=ids)


def list_documents(
    limit: int = 20,
    offset: int = 0,
) -> list[dict[str, Any]]:
    """
    List documents from ChromaDB.

    Args:
        limit: Maximum number of documents to return.
        offset: Number of documents to skip.

    Returns:
        List of documents.
    """
    collection = get_chroma_collection()

    result = collection.get(
        limit=limit,
        offset=offset,
        include=["documents", "metadatas"],
    )

    ids = result.get("ids", [])
    documents = result.get("documents", [])
    metadatas = result.get("metadatas", [])

    items: list[dict[str, Any]] = []

    for index, document_id in enumerate(ids):
        items.append(
            {
                "id": document_id,
                "content": documents[index] if index < len(documents) else "",
                "metadata": metadatas[index] if index < len(metadatas) else {},
            }
        )

    return items