"""
Speech-to-Text Service
Primary:  OpenAI Whisper API
Fallback: Faster-Whisper (local CPU/GPU)
"""
from __future__ import annotations
import asyncio
import io
import logging
import tempfile
from pathlib import Path

from configs.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class STTService:
    """Async Speech-to-Text wrapper."""

    async def transcribe(
        self,
        audio_data: bytes,
        language: str = "en",
    ) -> dict:
        """
        Transcribe audio bytes.
        Returns {"text": str, "language": str, "confidence": float|None}
        """
        if settings.stt_provider == "whisper_api":
            return await self._whisper_api(audio_data, language)
        else:
            return await self._faster_whisper(audio_data, language)

    # ── OpenAI Whisper API ───────────────────────────────────
    async def _whisper_api(self, audio_data: bytes, language: str) -> dict:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.openai_api_key)

        # Map language codes
        whisper_lang = "hi" if language == "hi" else "en"

        audio_file = io.BytesIO(audio_data)
        audio_file.name = "audio.webm"

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: _call_whisper_api(client, audio_file, whisper_lang),
        )
        text = (response.text or "").strip()
        logger.info("Whisper transcription: %s chars", len(text))
        return {"text": text, "language": language, "confidence": None}

    # ── Faster-Whisper (local) ───────────────────────────────
    async def _faster_whisper(self, audio_data: bytes, language: str) -> dict:
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as f:
            f.write(audio_data)
            tmp_path = f.name

        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, self._run_faster_whisper, tmp_path, language
            )
            return result
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def _run_faster_whisper(self, audio_path: str, language: str) -> dict:
        from faster_whisper import WhisperModel

        model = WhisperModel(
            "small",
            device="cuda" if _cuda_available() else "cpu",
            compute_type="float16" if _cuda_available() else "int8",
        )
        lang_code = "hi" if language == "hi" else "en"
        segments, info = model.transcribe(audio_path, language=lang_code)
        text = " ".join(seg.text for seg in segments).strip()
        return {
            "text": text,
            "language": info.language,
            "confidence": float(info.language_probability),
        }


def _call_whisper_api(client, audio_file, language):
    """Sync call to Whisper API (run in executor)."""
    import openai
    return client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language=language,
        response_format="text",
    )


def _cuda_available() -> bool:
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


# ── Singleton ─────────────────────────────────────────────────
_stt_service: STTService | None = None


def get_stt_service() -> STTService:
    global _stt_service
    if _stt_service is None:
        _stt_service = STTService()
    return _stt_service
