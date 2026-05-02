import os
from langchain_community.vectorstores import FAISS
from src.rag.embeddings import get_embeddings

INDEX_PATH = "faiss_index"

def load_vector_store():
    embeddings = get_embeddings()

    if not os.path.exists(INDEX_PATH):
        print("Creating FAISS index...")
        db = FAISS.from_texts(["default data"], embeddings)
        db.save_local(INDEX_PATH)

    return FAISS.load_local(
        INDEX_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )