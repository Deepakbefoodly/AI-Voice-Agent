from fastapi import APIRouter, UploadFile, File, HTTPException
from src.services.deepgram_service import transcribe_audio

router = APIRouter()

@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    try:
        audio_bytes = await file.read()

        transcript = transcribe_audio(
            audio_bytes,
            file.content_type
        )

        return {
            "filename": file.filename,
            "transcript": transcript
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))