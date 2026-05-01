from langchain.prompts import PromptTemplate

def get_rag_prompt():
    return PromptTemplate(
        input_variables=["context", "question"],
        template="""
        You are a helpful AI assistant.
        
        Rules:
        - Answer ONLY using the provided context
        - If answer is not found, say "I don't know"
        - Keep answers concise and natural
        
        Context:
        {context}
        
        Question:
        {question}
        """
    )