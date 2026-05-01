# We will come back to this route later

import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.services.deepgram_ws_service import connect_deepgram, extract_transcript
from src.services.rag_service import rag_service

router = APIRouter()

@router.websocket("/ws/voice-agent")
async def voice_agent(ws: WebSocket):
    await ws.accept()

    try:
        deepgram_ws = await connect_deepgram()

        async def forward_audio():
            try:
                while True:
                    audio_chunk = await ws.receive_bytes()
                    await deepgram_ws.send(audio_chunk)
            except WebSocketDisconnect:
                await deepgram_ws.close()

        async def process_transcript():
            try:
                while True:
                    message = await deepgram_ws.recv()
                    transcript = extract_transcript(message)

                    if transcript:
                        # RAG + LLM processing
                        response = await rag_service.aquery(transcript)

                        await ws.send_json({
                            "transcript": transcript,
                            "response": response
                        })

            except Exception:
                await ws.close()

        await asyncio.gather(forward_audio(), process_transcript())

    except Exception:
        await ws.close()