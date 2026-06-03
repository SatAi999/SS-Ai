"""
Conversational LLM Service — supports OpenAI, Groq, and Ollama.
All providers expose the same async interface.
"""
from __future__ import annotations
import logging
from typing import AsyncIterator
from configs.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ConversationalLLMService:
    """Unified chat LLM interface for all providers."""

    def __init__(self):
        self.provider = settings.llm_provider
        self._client = None

    def _get_openai_client(self):
        if self._client is None:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        return self._client

    def _get_groq_client(self):
        if self._client is None:
            from groq import AsyncGroq
            self._client = AsyncGroq(api_key=settings.groq_api_key)
        return self._client

    async def chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        """Send a chat completion request and return the full response text."""
        try:
            if self.provider == "openai":
                return await self._openai_chat(messages, temperature, max_tokens)
            elif self.provider == "groq":
                return await self._groq_chat(messages, temperature, max_tokens)
            elif self.provider == "ollama":
                return await self._ollama_chat(messages, temperature, max_tokens)
            else:
                raise ValueError(f"Unknown LLM provider: {self.provider}")
        except Exception as e:
            logger.error("LLM chat error (%s): %s", self.provider, e)
            raise

    async def _openai_chat(self, messages, temperature, max_tokens) -> str:
        client = self._get_openai_client()
        response = await client.chat.completions.create(
            model=settings.openai_chat_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()

    async def _groq_chat(self, messages, temperature, max_tokens) -> str:
        client = self._get_groq_client()
        response = await client.chat.completions.create(
            model=settings.groq_chat_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()

    async def _ollama_chat(self, messages, temperature, max_tokens) -> str:
        import httpx
        payload = {
            "model": settings.ollama_chat_model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{settings.ollama_base_url}/api/chat",
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["message"]["content"].strip()

    async def stream_chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> AsyncIterator[str]:
        """Streaming chat — yields text chunks. OpenAI and Groq only for now."""
        if self.provider == "openai":
            client = self._get_openai_client()
            async with client.chat.completions.stream(
                model=settings.openai_chat_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            ) as stream:
                async for chunk in stream:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        yield delta
        elif self.provider == "groq":
            client = self._get_groq_client()
            stream = await client.chat.completions.create(
                model=settings.groq_chat_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
        else:
            # Fallback: non-streaming for Ollama
            text = await self.chat(messages, temperature, max_tokens)
            yield text


# ── Singleton ─────────────────────────────────────────────────
_llm_service: ConversationalLLMService | None = None


def get_llm_service() -> ConversationalLLMService:
    global _llm_service
    if _llm_service is None:
        _llm_service = ConversationalLLMService()
    return _llm_service
