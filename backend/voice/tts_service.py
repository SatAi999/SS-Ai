"""
Text-to-Speech Service
Primary:  ElevenLabs API
Fallback: edge-tts (free, Microsoft Neural TTS via Edge browser)
"""
from __future__ import annotations
import asyncio
import io
import logging

from configs.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Language → voice mapping for edge-tts
EDGE_TTS_VOICES = {
    "en": "en-IN-NeerjaNeural",
    "hi": "hi-IN-SwaraNeural",
}


class TTSService:
    """Async Text-to-Speech wrapper."""

    async def synthesize(self, text: str, language: str = "en") -> bytes:
        """
        Convert text to audio bytes (MP3/WAV).
        """
        # Truncate long text to avoid API abuse
        text = text.strip()[:1500]
        if not text:
            return b""

        if settings.tts_provider == "elevenlabs":
            return await self._elevenlabs(text, language)
        else:
            return await self._edge_tts(text, language)

    # ── ElevenLabs ───────────────────────────────────────────
    async def _elevenlabs(self, text: str, language: str) -> bytes:
        voice_id = (
            settings.elevenlabs_voice_id_hi
            if language == "hi"
            else settings.elevenlabs_voice_id_en
        )
        try:
            from elevenlabs.client import AsyncElevenLabs
            client = AsyncElevenLabs(api_key=settings.elevenlabs_api_key)
            audio_gen = await client.generate(
                text=text,
                voice=voice_id,
                model="eleven_multilingual_v2",
            )
            # Collect async iterator chunks
            chunks = []
            async for chunk in audio_gen:
                chunks.append(chunk)
            return b"".join(chunks)
        except Exception as e:
            logger.warning("ElevenLabs failed (%s), falling back to edge-tts", e)
            return await self._edge_tts(text, language)

    # ── edge-tts (free fallback) ─────────────────────────────
    async def _edge_tts(self, text: str, language: str) -> bytes:
        import edge_tts

        voice = EDGE_TTS_VOICES.get(language, EDGE_TTS_VOICES["en"])
        communicate = edge_tts.Communicate(text, voice)
        buffer = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                buffer.write(chunk["data"])
        return buffer.getvalue()


# ── Singleton ─────────────────────────────────────────────────
_tts_service: TTSService | None = None


def get_tts_service() -> TTSService:
    global _tts_service
    if _tts_service is None:
        _tts_service = TTSService()
    return _tts_service
