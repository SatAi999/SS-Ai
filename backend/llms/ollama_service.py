"""
Ollama Service — local inference via Ollama REST API.
Supports llama3, mistral, gemma, qwen, phi3 and any Ollama-served model.
"""
from __future__ import annotations
import logging
import httpx
from configs.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

OLLAMA_BASE = settings.ollama_base_url


class OllamaService:
    """Reusable async Ollama inference client."""

    def __init__(self, model: str | None = None):
        self.model = model or settings.ollama_chat_model
        self._http = httpx.AsyncClient(
            base_url=OLLAMA_BASE,
            timeout=120.0,
        )

    async def chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        try:
            resp = await self._http.post("/api/chat", json=payload)
            resp.raise_for_status()
            return resp.json()["message"]["content"].strip()
        except httpx.ConnectError:
            raise RuntimeError(
                f"Cannot connect to Ollama at {OLLAMA_BASE}. "
                "Ensure Ollama is running: `ollama serve`"
            )

    async def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """Raw generation endpoint for single-turn prompts."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature},
        }
        resp = await self._http.post("/api/generate", json=payload)
        resp.raise_for_status()
        return resp.json()["response"].strip()

    async def list_models(self) -> list[str]:
        """Return list of locally available Ollama models."""
        try:
            resp = await self._http.get("/api/tags")
            resp.raise_for_status()
            return [m["name"] for m in resp.json().get("models", [])]
        except Exception:
            return []

    async def is_available(self) -> bool:
        try:
            resp = await self._http.get("/api/tags", timeout=5.0)
            return resp.status_code == 200
        except Exception:
            return False

    async def aclose(self):
        await self._http.aclose()


# ── Factory ───────────────────────────────────────────────────
def get_ollama_service(model: str | None = None) -> OllamaService:
    return OllamaService(model=model)
