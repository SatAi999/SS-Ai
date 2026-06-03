"""Emergency Triage Agent — detects dangerous symptoms and triggers escalation."""
from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import Optional

from llms.conversational_llm_service import get_llm_service
from prompts.agent_prompts import get_emergency_prompt

logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    response: str
    session_id: str = ""
    severity: Optional[str] = None
    suggestions: list[str] = field(default_factory=list)
    emergency_alert: Optional[dict] = None
    agent_used: str = "emergency_agent"
    observations: list[str] = field(default_factory=list)


# Keywords that trigger emergency routing
EMERGENCY_KEYWORDS_EN = {
    "unconscious", "not breathing", "chest pain", "heart attack",
    "stroke", "seizure", "heavy bleeding", "severe burn",
    "poisoning", "anaphylaxis", "choking", "head injury",
}
EMERGENCY_KEYWORDS_HI = {
    "बेहोश", "सांस नहीं", "सीने में दर्द", "दिल का दौरा",
    "दौरा", "तेज खून", "जहर", "दम घुट", "सिर की चोट",
}


class EmergencyAgent:
    """Handles acute emergency triage and escalation guidance."""

    def __init__(self):
        self.llm = get_llm_service()

    async def handle(
        self,
        message: str,
        language: str = "en",
        history: list[dict] | None = None,
    ) -> AgentResult:
        history = history or []
        severity = self._assess_severity(message, language)
        system = get_emergency_prompt(language)

        messages = [
            {"role": "system", "content": system},
            *history[-2:],
            {"role": "user", "content": message},
        ]

        response = await self.llm.chat(messages, temperature=0.3, max_tokens=400)

        emergency_alert = {
            "severity": severity,
            "message": response[:250],
            "action": self._get_action(severity, language),
        }

        suggestions = [
            ("Call 108 immediately" if language == "en" else "108 पर तुरंत कॉल करें"),
            ("Keep patient calm and still" if language == "en" else "रोगी को शांत रखें"),
        ]

        return AgentResult(
            response=response,
            severity=severity,
            suggestions=suggestions,
            emergency_alert=emergency_alert,
            agent_used="emergency_agent",
        )

    def _assess_severity(self, message: str, language: str) -> str:
        lower = message.lower()
        keywords = EMERGENCY_KEYWORDS_EN if language == "en" else EMERGENCY_KEYWORDS_HI
        if any(k in lower for k in keywords):
            return "critical"
        return "high"

    def _get_action(self, severity: str, language: str) -> str:
        if language == "hi":
            return "तुरंत 108 पर कॉल करें और नजदीकी अस्पताल जाएं।" if severity == "critical" else "जल्द अस्पताल जाएं।"
        return "Call 108 immediately and go to the nearest hospital." if severity == "critical" else "Visit a hospital soon."
