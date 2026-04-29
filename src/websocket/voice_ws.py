# We are not using websockets for now

import asyncio
import websockets
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.config import DEEPGRAM_API_KEY

router = APIRouter()

DEEPGRAM_WS_URL = "wss://api.deepgram.com/v1/listen?punctuate=true&model=nova"

@router.websocket("/ws/transcribe")
async def websocket_transcribe(client_ws: WebSocket):
    await client_ws.accept()

    try:
        # Connect to Deepgram WebSocket
        async with websockets.connect(
            DEEPGRAM_WS_URL,
            extra_headers={
                "Authorization": f"Token {DEEPGRAM_API_KEY}"
            }
        ) as deepgram_ws:

            async def send_audio():
                """Receive audio from client and forward to Deepgram"""
                try:
                    while True:
                        data = await client_ws.receive_bytes()
                        await deepgram_ws.send(data)
                except WebSocketDisconnect:
                    await deepgram_ws.close()

            async def receive_transcript():
                """Receive transcription from Deepgram and send to client"""
                try:
                    while True:
                        message = await deepgram_ws.recv()
                        result = json.loads(message)

                        transcript = (
                            result.get("channel", {})
                                  .get("alternatives", [{}])[0]
                                  .get("transcript", "")
                        )

                        if transcript:
                            await client_ws.send_text(transcript)

                except Exception:
                    await client_ws.close()

            await asyncio.gather(send_audio(), receive_transcript())

    except Exception as e:
        await client_ws.close()