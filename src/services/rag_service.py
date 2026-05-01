from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA

from src.config import GEMINI_API_KEY
from src.rag.vector_store import load_vector_store
from src.rag.prompt import get_rag_prompt

class RAGService:

    def __init__(self):
        self.vector_store = load_vector_store()

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=GEMINI_API_KEY,
            temperature=0.3
        )

        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 3}),
            chain_type_kwargs={
                "prompt": get_rag_prompt()
            }
        )

    # Sync (for REST APIs)
    def query(self, question: str) -> str:
        return self.qa_chain.run(question)

    # Async (for WebSocket / streaming systems)
    async def aquery(self, question: str) -> str:
        return await self.qa_chain.arun(question)


# Singleton instance (shared across app)
rag_service = RAGService()