"""Symptom Analysis Agent"""
from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import Optional

from llms.conversational_llm_service import get_llm_service
from prompts.agent_prompts import get_symptom_prompt
from prompts.system_prompts import get_system_prompt

logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    response: str
    session_id: str = ""
    severity: Optional[str] = None
    suggestions: list[str] = field(default_factory=list)
    emergency_alert: Optional[dict] = None
    agent_used: str = ""
    observations: list[str] = field(default_factory=list)


class SymptomAgent:
    """Handles symptom reports and healthcare questions."""

    def __init__(self):
        self.llm = get_llm_service()

    async def handle(
        self,
        message: str,
        language: str = "en",
        history: list[dict] | None = None,
    ) -> AgentResult:
        history = history or []
        system = get_symptom_prompt(language)

        messages = [
            {"role": "system", "content": system},
            *history[-4:],
            {"role": "user", "content": message},
        ]

        response = await self.llm.chat(messages, temperature=0.5, max_tokens=600)

        severity, suggestions, emergency = _extract_severity(response, language)

        return AgentResult(
            response=response,
            severity=severity,
            suggestions=suggestions,
            emergency_alert=emergency,
            agent_used="symptom_agent",
        )


def _extract_severity(text: str, language: str) -> tuple:
    """Heuristic severity extraction from response text."""
    lower = text.lower()
    emergency = None

    if any(w in lower for w in ["emergency", "immediately", "call 108", "hospital now", "गंभीर", "तुरंत"]):
        severity = "high"
        emergency = {
            "severity": "high",
            "message": text[:200],
            "action": "Seek immediate medical attention" if language == "en" else "तुरंत चिकित्सा सहायता लें",
        }
    elif any(w in lower for w in ["consult", "doctor", "clinic", "डॉक्टर", "अस्पताल"]):
        severity = "medium"
    elif any(w in lower for w in ["monitor", "rest", "observe", "नज़र", "आराम"]):
        severity = "low"
    else:
        severity = None

    suggestions = _extract_suggestions(text)
    return severity, suggestions, emergency


def _extract_suggestions(text: str) -> list[str]:
    """Extract bullet-like suggestions from text."""
    suggestions = []
    for line in text.split("\n"):
        stripped = line.strip(" -•*")
        if len(stripped) > 20 and any(
            w in stripped.lower()
            for w in ["drink", "rest", "clean", "monitor", "consult", "avoid", "apply", "पीएं", "आराम"]
        ):
            suggestions.append(stripped[:100])
    return suggestions[:3]
