"""
Medical Image Analyzer — adapter-based architecture.

Supports:
  - MedGemma (local, 4-bit quantised)
  - OpenAI GPT-4o Vision (cloud)

Add new vision models by implementing the _analyze_* methods below.
"""
from __future__ import annotations
import base64
import logging
from pathlib import Path

from configs.settings import get_settings
from prompts.medgemma_prompts import build_medgemma_prompt
from prompts.system_prompts import VISION_SYSTEM_PROMPT

logger = logging.getLogger(__name__)
settings = get_settings()


class MedicalImageAnalyzer:
    """Unified vision analysis adapter."""

    async def analyze(
        self,
        image_path: str,
        user_query: str,
        language: str = "en",
    ) -> dict:
        """
        Analyse a medical-context image and return a structured result.

        Returns:
            {
              "raw_response": str,
              "observations": list[str],
              "concern_level": str,
              "suggestions": list[str],
              "provider": str,
            }
        """
        if settings.vision_provider == "medgemma":
            return await self._analyze_medgemma(image_path, user_query, language)
        else:
            return await self._analyze_openai_vision(image_path, user_query, language)

    # ── MedGemma ─────────────────────────────────────────────
    async def _analyze_medgemma(
        self, image_path: str, user_query: str, language: str
    ) -> dict:
        from llms.medgemma_service import get_medgemma_service

        service = get_medgemma_service()
        if not service.is_available():
            logger.warning("MedGemma unavailable (no CUDA), falling back to OpenAI Vision")
            return await self._analyze_openai_vision(image_path, user_query, language)

        raw = await service.analyze_image(image_path, user_query, language)
        return _parse_structured_response(raw, provider="medgemma")

    # ── OpenAI GPT-4o Vision ─────────────────────────────────
    async def _analyze_openai_vision(
        self, image_path: str, user_query: str, language: str
    ) -> dict:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=settings.openai_api_key)

        # Encode image as base64
        image_bytes = Path(image_path).read_bytes()
        b64 = base64.b64encode(image_bytes).decode("utf-8")

        prompt = build_medgemma_prompt(user_query, language)

        response = await client.chat.completions.create(
            model=settings.openai_vision_model,
            messages=[
                {"role": "system", "content": VISION_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{b64}",
                                "detail": "low",
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                },
            ],
            max_tokens=600,
            temperature=0.3,
        )

        raw = response.choices[0].message.content.strip()
        return _parse_structured_response(raw, provider="openai_vision")


def _parse_structured_response(raw: str, provider: str) -> dict:
    """
    Extract structured fields from the model's text response.
    Simple heuristic parsing — works with the numbered format from prompts.
    """
    observations: list[str] = []
    suggestions: list[str] = []
    concern_level = "moderate"

    lines = raw.split("\n")
    for line in lines:
        stripped = line.strip(" -•*123456789.:")
        if not stripped:
            continue
        lower = line.lower()
        if "observ" in lower or "visible" in lower or "appear" in lower:
            observations.append(stripped)
        elif "suggest" in lower or "care" in lower or "clean" in lower or "escalat" in lower:
            suggestions.append(stripped)
        if "critical" in lower or "emergency" in lower or "immediately" in lower:
            concern_level = "high"
        elif "mild" in lower or "minor" in lower or "low" in lower:
            concern_level = "low"

    return {
        "raw_response": raw,
        "observations": observations[:5],
        "concern_level": concern_level,
        "suggestions": suggestions[:4],
        "provider": provider,
    }


# ── Singleton ─────────────────────────────────────────────────
_analyzer: MedicalImageAnalyzer | None = None


def get_image_analyzer() -> MedicalImageAnalyzer:
    global _analyzer
    if _analyzer is None:
        _analyzer = MedicalImageAnalyzer()
    return _analyzer
