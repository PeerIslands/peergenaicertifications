from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv(find_dotenv(), override=True)


class Settings(BaseSettings):
    # Provider selection priority: openai -> gemini
    embedding_provider: str = os.getenv("EMBEDDING_PROVIDER", "openai")

    # OpenAI
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_embedding_model: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

    # Gemini removed

    # Infra
    chroma_dir: str = os.getenv("CHROMA_DIR", "./chroma_db")
    upload_dir: str = os.getenv("UPLOAD_DIR", "./uploads")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()

# Ensure directories exist at import time so the app can start cleanly.
Path(settings.chroma_dir).mkdir(parents=True, exist_ok=True)
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)


