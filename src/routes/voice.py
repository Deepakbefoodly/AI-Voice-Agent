from fastapi import APIRouter, UploadFile, File, HTTPException
from src.services.deepgram_service import transcribe_audio
from services.rag_service import rag_service

router = APIRouter()

@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    try:
        # Step 1: Read audio
        audio_bytes = await file.read()

        # Step 2: Speech-to-text (Deepgram)
        transcript = transcribe_audio(
            audio_bytes,
            file.content_type
        )

        if not transcript:
            return {
                "transcript": "",
                "response": "No speech detected"
            }

        # Step 3: RAG (LLM + knowledge base)
        response = rag_service.query(transcript)

        return {
            "transcript": transcript,
            "response": response
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))