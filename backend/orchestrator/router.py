"""
Orchestrator router — maps intent to agent.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class AgentType(str, Enum):
    SYMPTOM = "symptom"
    EMERGENCY = "emergency"
    VITALS = "vitals"
    VISION = "vision"
    GENERAL = "general"


# Intent → Agent mapping
INTENT_TO_AGENT: dict[str, AgentType] = {
    "emergency": AgentType.EMERGENCY,
    "symptom_report": AgentType.SYMPTOM,
    "vitals_check": AgentType.VITALS,
    "pregnancy": AgentType.SYMPTOM,
    "child_health": AgentType.SYMPTOM,
    "elderly_care": AgentType.SYMPTOM,
    "nutrition": AgentType.GENERAL,
    "education": AgentType.GENERAL,
    "greeting": AgentType.GENERAL,
    "general_health": AgentType.GENERAL,
}

# Emergency keywords that override normal routing
EMERGENCY_KEYWORDS = [
    "chest pain", "heart attack", "stroke", "unconscious", "not breathing",
    "bleeding heavily", "seizure", "convulsion", "poisoning", "snake bite",
    "severe burn", "छाती में दर्द", "दिल का दौरा", "बेहोश", "सांस नहीं",
]


def route_intent(intent: str, message: str) -> AgentType:
    """Determine which agent should handle this request."""
    msg_lower = message.lower()
    for kw in EMERGENCY_KEYWORDS:
        if kw in msg_lower:
            return AgentType.EMERGENCY

    return INTENT_TO_AGENT.get(intent, AgentType.GENERAL)
