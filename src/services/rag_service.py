from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser

from src.config import GEMINI_API_KEY
from src.rag.vector_store import load_vector_store
from src.rag.prompt import get_rag_prompt


def _format_docs(docs):
    return "\n\n".join([doc.page_content for doc in docs])


class RAGService:

    def __init__(self):
        self.vector_store = load_vector_store()

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=GEMINI_API_KEY,
            temperature=0.3
        )
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
        self.prompt = get_rag_prompt()
        self.parser = StrOutputParser()

    # Sync (for REST APIs)
    def query(self, question: str) -> str:
        docs = self.retriever.invoke(question)
        context = _format_docs(docs)

        chain = self.prompt | self.llm | self.parser
        return chain.invoke({
            "context": context,
            "input": question
        })

    # Async (for WebSocket / streaming systems)
    async def aquery(self, question: str) -> str:
        docs = await self.retriever.ainvoke(question)
        context = _format_docs(docs)

        chain = self.prompt | self.llm | self.parser
        return await chain.ainvoke({
            "context": context,
            "input": question
        })


# Singleton instance (shared across app)
rag_service = RAGService()