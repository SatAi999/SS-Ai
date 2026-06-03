"""Vision Agent — combines image analysis with conversational context."""
from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import Optional

from vision.medical_image_analyzer import get_image_analyzer
from llms.conversational_llm_service import get_llm_service
from prompts.system_prompts import get_system_prompt

logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    response: str
    session_id: str = ""
    severity: Optional[str] = None
    suggestions: list[str] = field(default_factory=list)
    emergency_alert: Optional[dict] = None
    agent_used: str = "vision_agent"
    observations: list[str] = field(default_factory=list)


class VisionAgent:
    """Analyses medical images and returns conversational healthcare guidance."""

    def __init__(self):
        self.analyzer = get_image_analyzer()
        self.llm = get_llm_service()

    async def analyze(
        self,
        image_path: str,
        query: str,
        language: str = "en",
        history: list[dict] | None = None,
    ) -> AgentResult:
        # Step 1: Get structured vision analysis
        vision_result = await self.analyzer.analyze(image_path, query, language)

        # Step 2: Convert raw analysis into natural conversational response
        natural_response = await self._naturalise(vision_result, query, language)

        # Step 3: Determine severity
        severity = _map_concern_to_severity(vision_result.get("concern_level", ""))

        # Build emergency alert if needed
        emergency = None
        if severity in ("high", "critical"):
            emergency = {
                "severity": severity,
                "message": natural_response[:200],
                "action": "Seek medical evaluation" if language == "en" else "चिकित्सा मूल्यांकन लें",
            }

        return AgentResult(
            response=natural_response,
            severity=severity,
            suggestions=vision_result.get("suggestions", []),
            emergency_alert=emergency,
            agent_used=f"vision_agent_{vision_result.get('provider', 'unknown')}",
            observations=vision_result.get("observations", []),
        )

    async def _naturalise(self, vision_result: dict, query: str, language: str) -> str:
        """Use conversational LLM to make the raw vision output field-friendly."""
        raw = vision_result.get("raw_response", "")
        observations = "; ".join(vision_result.get("observations", []))
        suggestions = "; ".join(vision_result.get("suggestions", []))

        system_msg = get_system_prompt(language)
        user_msg = (
            f"The user asked: {query}\n\n"
            f"Visual observations from the image: {observations}\n"
            f"Initial suggestions: {suggestions}\n\n"
            "Convert this into a calm, simple, conversational response for a rural "
            "healthcare worker. Do NOT diagnose. Keep it under 150 words. "
            f"Respond in {'Hindi' if language == 'hi' else 'English'}."
        )

        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ]
        return await self.llm.chat(messages, temperature=0.5, max_tokens=300)


def _map_concern_to_severity(concern: str) -> Optional[str]:
    mapping = {
        "low": "low",
        "moderate": "medium",
        "medium": "medium",
        "high": "high",
        "critical": "critical",
    }
    return mapping.get(concern.lower())
