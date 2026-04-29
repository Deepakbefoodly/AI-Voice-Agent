import requests
from src.config import DEEPGRAM_API_KEY, DEEPGRAM_URL

def transcribe_audio(audio_bytes, content_type):
    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": content_type
    }

    response = requests.post(
        DEEPGRAM_URL,
        headers=headers,
        params={"punctuate": "true", "model": "nova"},
        data=audio_bytes
    )

    if response.status_code != 200:
        raise Exception(response.text)

    result = response.json()

    return (
        result.get("results", {})
              .get("channels", [{}])[0]
              .get("alternatives", [{}])[0]
              .get("transcript", "")
    )