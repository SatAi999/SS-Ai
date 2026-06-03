"""
Safety Guardrail Agent
Validates AI responses for healthcare safety:
- Removes diagnostic statements
- Removes medication recommendations
- Ensures appropriate disclaimers
- Detects overconfident claims
"""
from __future__ import annotations
import logging
import re

from llms.conversational_llm_service import get_llm_service

logger = logging.getLogger(__name__)

# Patterns that should NEVER appear in responses
UNSAFE_PATTERNS = [
    # Diagnoses
    r"\byou have\b.{0,40}\b(disease|infection|disorder|syndrome|cancer)\b",
    r"\bthis is\b.{0,20}\b(malaria|typhoid|tuberculosis|tb|covid|dengue|hiv)\b",
    r"\bdiagnosed with\b",
    r"\bdiagnosis is\b",
    # Medications
    r"\btake\b.{0,30}\b(paracetamol|amoxicillin|ibuprofen|dolo|crocin|antibiotic|tablet|capsule|mg)\b",
    r"\bprescribe\b",
    r"\bdosage of\b",
]

DISCLAIMER_EN = "\n\n*This is AI-assisted guidance only. Please consult a qualified healthcare professional for medical advice.*"
DISCLAIMER_HI = "\n\n*यह केवल AI-सहायक मार्गदर्शन है। कृपया चिकित्सा सलाह के लिए योग्य स्वास्थ्य पेशेवर से परामर्श करें।*"


class SafetyGuardrailAgent:
    """Post-processes AI responses for healthcare safety."""

    def __init__(self):
        self.llm = get_llm_service()
        self._patterns = [re.compile(p, re.IGNORECASE) for p in UNSAFE_PATTERNS]

    async def validate(self, response: str, language: str = "en") -> str:
        """
        Check and sanitize the response.
        If unsafe patterns detected, rewrite via LLM.
        Always append a disclaimer.
        """
        if not response:
            return response

        if self._has_unsafe_content(response):
            logger.warning("Unsafe content detected, rewriting response")
            response = await self._rewrite_safe(response, language)

        # Append disclaimer if not already present
        disc = DISCLAIMER_EN if language == "en" else DISCLAIMER_HI
        if "AI-assisted" not in response and "AI-सहायक" not in response:
            response = response.rstrip() + disc

        return response

    def _has_unsafe_content(self, text: str) -> bool:
        return any(p.search(text) for p in self._patterns)

    async def _rewrite_safe(self, response: str, language: str) -> str:
        system = (
            "You are a healthcare safety editor. "
            "Rewrite the following response to remove any disease diagnoses, "
            "medication recommendations, or overconfident medical conclusions. "
            "Keep the helpful parts. Use calm, supportive language. "
            f"Respond in {'Hindi' if language == 'hi' else 'English'}."
        )
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": f"Rewrite safely:\n{response}"},
        ]
        try:
            return await self.llm.chat(messages, temperature=0.3, max_tokens=400)
        except Exception:
            # If rewrite fails, return a generic safe response
            if language == "hi":
                return "यह स्थिति किसी स्वास्थ्य कार्यकर्ता या डॉक्टर के ध्यान की आवश्यकता हो सकती है। कृपया पेशेवर सलाह लें।"
            return "This situation may require attention from a healthcare worker or doctor. Please seek professional advice."
