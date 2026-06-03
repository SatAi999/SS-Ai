from __future__ import annotations
from functools import lru_cache
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ──────────────────────────────────────────────────
    app_name: str = "SehatSakhi AI"
    environment: Literal["development", "production", "test"] = "development"
    secret_key: str = "change-me-in-production"
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    # ── LLM ──────────────────────────────────────────────────
    llm_provider: Literal["openai", "groq", "ollama"] = "openai"
    openai_api_key: str = ""
    openai_chat_model: str = "gpt-4o-mini"
    openai_vision_model: str = "gpt-4o"
    groq_api_key: str = ""
    groq_chat_model: str = "llama3-70b-8192"
    ollama_base_url: str = "http://localhost:11434"
    ollama_chat_model: str = "llama3"

    # ── Voice ─────────────────────────────────────────────────
    stt_provider: Literal["whisper_api", "faster_whisper"] = "whisper_api"
    tts_provider: Literal["elevenlabs", "edge_tts"] = "elevenlabs"
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id_en: str = "21m00Tcm4TlvDq8ikWAM"
    elevenlabs_voice_id_hi: str = "pNInz6obpgDQGcFmaJgB"

    # ── Vision ────────────────────────────────────────────────
    vision_provider: Literal["medgemma", "openai_vision"] = "openai_vision"
    medgemma_model_id: str = "google/medgemma-4b-it"
    hugging_face_token: str = ""

    # ── Database ──────────────────────────────────────────────
    database_url: str = "sqlite+aiosqlite:///./sehatsakhi.db"

    # ── RAG ───────────────────────────────────────────────────
    chroma_persist_dir: str = "./chroma_db"

    # ── Uploads ───────────────────────────────────────────────
    upload_dir: str = "./uploads/images"
    max_image_size_mb: int = 10

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
