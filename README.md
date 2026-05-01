# AI-Voice-Agent
Building AI powered voice agent to perform an action based on the voice note send by user

"In Progress"

- Accepts audio (.wav, .mp3, etc.)
- We have added two ways to process audio,
  1. Via audio upload
  2. Using Websocket for streaming audio in real-time
- Uses Deepgram to convert from speech to text (STT)
- Integrated Langchain framework for,
  1. LLM Orchestration
  2. Tools to connect with external APIs
  3. Building RAG system
