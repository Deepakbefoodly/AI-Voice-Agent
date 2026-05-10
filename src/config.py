from typing import Any
from pydantic_settings import BaseSettings
import os

from dotenv import load_dotenv

load_dotenv()

# Deepgram config
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
DEEPGRAM_URL = os.getenv("DEEPGRAM_URL")

# Gemini config
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Chroma config
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH")
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME")
CHROMA_TENANT_ID = os.getenv("CHROMA_TENANT_ID")
CHROMA_CLOUD_HOST = os.getenv("CHROMA_CLOUD_HOST")
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")

# ElevenLabs config
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")
ELEVENLABS_MODEL_ID = os.getenv("ELEVENLABS_MODEL_ID")
ELEVENLABS_OUTPUT_FORMAT = os.getenv("ELEVENLABS_OUTPUT_FORMAT")
TTS_OUTPUT_DIR = os.getenv("TTS_OUTPUT_DIR")

# MCP Tools config
MCP_TOOLS_URL = os.getenv("MCP_TOOLS_URL")
MCP_TOOLS_HOST = os.getenv("MCP_TOOLS_HOST")
MCP_TOOLS_PORT = os.getenv("MCP_TOOLS_PORT")
EXTERNAL_API_BASE_URL = os.getenv("EXTERNAL_API_BASE_URL")
EXTERNAL_API_KEY = os.getenv("EXTERNAL_API_KEY")
EXTERNAL_API_TIMEOUT_SECONDS = os.getenv("EXTERNAL_API_TIMEOUT_SECONDS")

class Config(BaseSettings):
    CORS_ORIGINS: list[str] = ["*"]
    CORS_HEADERS: list[str] = ["*"]
    APP_VERSION: str = "1"

settings = Config()

app_configs: dict[str, Any] = {
    "title": "AI Voice Agent Backend",
    "swagger_ui_parameters": {"displayRequestDuration": True},
}