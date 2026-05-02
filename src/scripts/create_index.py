# from langchain_community.vectorstores import FAISS
# from src.rag.embeddings import get_embeddings
#
# documents = [
#     "Your real documents go here",
# ]
#
# embeddings = get_embeddings()
#
# db = FAISS.from_texts(documents, embeddings)
# db.save_local("faiss_index")
#
# print("✅ Index created")