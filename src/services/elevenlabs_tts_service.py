# src/services/tts_service.py

import asyncio
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import requests
from src.config import (ELEVENLABS_VOICE_ID,
                    ELEVENLABS_API_KEY,
                    ELEVENLABS_MODEL_ID,
                    ELEVENLABS_OUTPUT_FORMAT,
                    TTS_OUTPUT_DIR)


ELEVENLABS_BASE_URL = "https://api.elevenlabs.io/v1"
DEFAULT_MEDIA_TYPE = "audio/mpeg"
MAX_TTS_TEXT_LENGTH = 1000


@dataclass(frozen=True)
class SpeechSynthesisResult:
    file_path: Path
    filename: str
    media_type: str

class TTSServiceError(RuntimeError):
    pass


class ElevenLabsTTSService:
    def __init__(self) -> None:
        self.api_key = ELEVENLABS_API_KEY
        self.voice_id = ELEVENLABS_VOICE_ID
        self.model_id = ELEVENLABS_MODEL_ID
        self.output_format = ELEVENLABS_OUTPUT_FORMAT

        self.output_dir = Path(TTS_OUTPUT_DIR).resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def synthesize(self, text: str) -> SpeechSynthesisResult:
        clean_text = self._validate_text(text)

        if not self.api_key:
            raise TTSServiceError("ElevenLabs API key is not configured.")

        if not self.voice_id:
            raise TTSServiceError("ElevenLabs voice ID is not configured.")

        filename = f"{uuid4().hex}.mp3"
        file_path = self.output_dir / filename

        url = f"{ELEVENLABS_BASE_URL}/text-to-speech/{self.voice_id}"

        headers = {
            "xi-api-key": self.api_key,
            "Accept": DEFAULT_MEDIA_TYPE,
            "Content-Type": "application/json",
        }

        params = {
            "output_format": self.output_format,
        }

        payload = {
            "text": clean_text,
            "model_id": self.model_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
            },
        }

        try:
            response = requests.post(
                url,
                headers=headers,
                params=params,
                json=payload,
                timeout=(10, 120),
            )
        except requests.RequestException as exc:
            raise TTSServiceError("Failed to call ElevenLabs TTS API.") from exc

        if response.status_code >= 400:
            raise TTSServiceError(
                f"ElevenLabs TTS request failed with status code {response.status_code}."
            )

        file_path.write_bytes(response.content)

        if not file_path.exists() or file_path.stat().st_size == 0:
            raise TTSServiceError("ElevenLabs returned an empty audio file.")

        return SpeechSynthesisResult(
            file_path=file_path,
            filename=filename,
            media_type=DEFAULT_MEDIA_TYPE,
        )

    async def asynthesize(self, text: str) -> SpeechSynthesisResult:
        return await asyncio.to_thread(self.synthesize, text)

    @staticmethod
    def _validate_text(text: str) -> str:
        if not text:
            raise TTSServiceError("TTS text cannot be empty.")

        clean_text = " ".join(text.split()).strip()

        if not clean_text:
            raise TTSServiceError("TTS text cannot be empty.")

        if len(clean_text) > MAX_TTS_TEXT_LENGTH:
            clean_text = clean_text[:MAX_TTS_TEXT_LENGTH].rsplit(" ", 1)[0]

        return clean_text


_tts_service = ElevenLabsTTSService()


def synthesize_speech(text: str) -> SpeechSynthesisResult:
    return _tts_service.synthesize(text)


async def asynthesize_speech(text: str) -> SpeechSynthesisResult:
    return await _tts_service.asynthesize(text)
