# keeping websocket on hold for now, we will use it after basic flow implementation

import websockets
import json
from src.config import DEEPGRAM_API_KEY

DEEPGRAM_WS_URL = "wss://api.deepgram.com/v1/listen?punctuate=true&model=nova"

async def connect_deepgram():
    return await websockets.connect(
        DEEPGRAM_WS_URL,
        extra_headers={
            "Authorization": f"Token {DEEPGRAM_API_KEY}"
        }
    )

def extract_transcript(message: str) -> str:
    data = json.loads(message)

    return (
        data.get("channel", {})
            .get("alternatives", [{}])[0]
            .get("transcript", "")
    )