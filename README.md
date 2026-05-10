# AI-Voice-Agent
Building AI powered voice agent to perform an action based on the voice note sent by the user

"In Progress"

- Accepts audio (.wav, .mp3, etc.)
- We have added two ways to process audio,
  1. Via audio upload
  2. Using Websocket for streaming audio in real-time
- Uses Deepgram to convert from speech to text (STT)
- Integrated Langchain framework for,
  1. LLM Orchestration
  2. Tools to connect with external APIs
  3. Building the RAG system
- Using chroma vector db to store data embeddings to maintain context, have written some methods in `vector_store.py`
  to add embedded documents, run similarity search, fetching documents by id, etc.
- I used **Pydantic** input validation to reject suspicious/prompt-injection style inputs
- And **Guardrails AI** output validation to enforce a safe structured LLM response
- (Optional Layer) we are going to use a library like **ElevenLabs** for TTS to convert LLM response back to human like speech
- I have implemented **FastMCP** for Intent Tool and External API Tool
- 

