# src/routes/voice_rag.py

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from src.services.rag_service import aquery_with_voice

router = APIRouter(prefix="/rag", tags=["rag"])


class VoiceRAGRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(default=3, ge=1, le=10)


@router.post("/voice")
async def voice_rag(payload: VoiceRAGRequest) -> FileResponse:
    result = await aquery_with_voice(
        question=payload.question,
        top_k=payload.top_k,
    )

    if not result.audio_path.exists():
        raise HTTPException(
            status_code=500,
            detail="Audio generation failed.",
        )

    return FileResponse(
        path=result.audio_path,
        media_type=result.audio_media_type,
        filename=result.audio_filename,
    )