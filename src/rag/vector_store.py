from langchain_community.vectorstores import FAISS
from src.rag.embeddings import get_embeddings

def load_vector_store():
    embeddings = get_embeddings()
    return FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)