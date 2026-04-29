from typing import Any
from pydantic_settings import BaseSettings
import os

from dotenv import load_dotenv

load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")
DEEPGRAM_URL = os.getenv("DEEPGRAM_URL")

class Config(BaseSettings):
    CORS_ORIGINS: list[str] = ["*"]
    CORS_HEADERS: list[str] = ["*"]
    APP_VERSION: str = "1"

settings = Config()

app_configs: dict[str, Any] = {
    "title": "AI Voice Agent Backend",
    "swagger_ui_parameters": {"displayRequestDuration": True},
}