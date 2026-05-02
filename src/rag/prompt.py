from langchain_core.prompts import ChatPromptTemplate

def get_rag_prompt():
    return ChatPromptTemplate.from_template(
        """
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

def multi_agent_prompt():
    return ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant."),
        ("human", "Context:\n{context}\n\nQuestion:\n{input}")
    ])