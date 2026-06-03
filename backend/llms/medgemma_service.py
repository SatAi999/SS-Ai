"""
MedGemma Service — Multimodal medical reasoning with google/medgemma-4b-it.

Optimised for RTX 4070 Laptop GPU (8 GB VRAM) using 4-bit quantisation.
MedGemma is ONLY used when an image is present. All conversational
routing goes through the lightweight ConversationalLLMService.
"""
from __future__ import annotations
import asyncio
import logging
from pathlib import Path
from typing import Optional

from PIL import Image

from configs.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class MedGemmaService:
    """
    Lazy-loaded MedGemma wrapper.
    The model is loaded exactly once (on first use) to avoid VRAM pressure.
    """

    def __init__(self):
        self._processor = None
        self._model = None
        self._loaded = False
        self._lock = asyncio.Lock()

    # ── Model loading ────────────────────────────────────────
    def _load_model_sync(self):
        """Load model synchronously (called from thread pool)."""
        import torch
        from transformers import (
            AutoProcessor,
            AutoModelForImageTextToText,
            BitsAndBytesConfig,
        )

        logger.info("Loading MedGemma model: %s", settings.medgemma_model_id)

        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
        )

        login_kwargs = {}
        if settings.hugging_face_token:
            login_kwargs["token"] = settings.hugging_face_token

        processor = AutoProcessor.from_pretrained(
            settings.medgemma_model_id,
            **login_kwargs,
        )

        model = AutoModelForImageTextToText.from_pretrained(
            settings.medgemma_model_id,
            quantization_config=bnb_config,
            device_map="auto",
            **login_kwargs,
        )
        model.eval()

        self._processor = processor
        self._model = model
        self._loaded = True
        logger.info("MedGemma loaded successfully")

    async def _ensure_loaded(self):
        if not self._loaded:
            async with self._lock:
                if not self._loaded:
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, self._load_model_sync)

    # ── Inference ────────────────────────────────────────────
    def _infer_sync(self, image: Image.Image, prompt: str) -> str:
        import torch

        # Resize for VRAM efficiency
        image = image.resize((512, 512))

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": prompt},
                ],
            }
        ]

        inputs = self._processor.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        )
        inputs = {k: v.to(self._model.device) for k, v in inputs.items()}

        with torch.no_grad():
            output = self._model.generate(
                **inputs,
                max_new_tokens=300,
                do_sample=False,
                temperature=1.0,
            )

        # Decode only newly generated tokens
        new_tokens = output[0][inputs["input_ids"].shape[-1]:]
        response = self._processor.decode(new_tokens, skip_special_tokens=True)
        return response.strip()

    async def analyze_image(
        self,
        image_path: str,
        user_query: str,
        language: str = "en",
    ) -> str:
        """
        Run MedGemma multimodal inference on a medical image.
        Returns a safe, structured healthcare observation.
        """
        await self._ensure_loaded()

        from prompts.medgemma_prompts import build_medgemma_prompt

        image = Image.open(image_path).convert("RGB")
        prompt = build_medgemma_prompt(user_query, language)

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None, self._infer_sync, image, prompt
        )
        return result

    def is_available(self) -> bool:
        """Return True if MedGemma can be loaded (CUDA + transformers available)."""
        try:
            import torch
            return torch.cuda.is_available()
        except ImportError:
            return False


# ── Singleton ─────────────────────────────────────────────────
_medgemma_service: Optional[MedGemmaService] = None


def get_medgemma_service() -> MedGemmaService:
    global _medgemma_service
    if _medgemma_service is None:
        _medgemma_service = MedGemmaService()
    return _medgemma_service
