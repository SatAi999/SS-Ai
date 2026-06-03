"""Vitals Interpretation Agent"""
from __future__ import annotations
import re
import logging
from dataclasses import dataclass, field
from typing import Optional

from llms.conversational_llm_service import get_llm_service
from prompts.agent_prompts import get_vitals_prompt

logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    response: str
    session_id: str = ""
    severity: Optional[str] = None
    suggestions: list[str] = field(default_factory=list)
    emergency_alert: Optional[dict] = None
    agent_used: str = "vitals_agent"
    observations: list[str] = field(default_factory=list)


# Normal ranges
VITAL_RANGES = {
    "spo2":        (95, 100),   # %
    "pulse":       (60, 100),   # bpm
    "temperature": (36.1, 37.2),  # °C
    "systolic_bp": (90, 140),   # mmHg
    "diastolic_bp":(60, 90),    # mmHg
}


class VitalsAgent:
    """Interprets entered vitals and flags abnormal values."""

    def __init__(self):
        self.llm = get_llm_service()

    async def handle(
        self,
        message: str,
        language: str = "en",
        history: list[dict] | None = None,
    ) -> AgentResult:
        history = history or []
        system = get_vitals_prompt(language)

        # Try to extract numbers from message
        parsed = _parse_vitals(message)
        observations = _assess_vitals(parsed, language)

        enhanced_message = message
        if observations:
            enhanced_message = (
                f"Vitals detected: {parsed}\n"
                f"Preliminary assessment: {'; '.join(observations)}\n"
                f"User query: {message}"
            )

        messages = [
            {"role": "system", "content": system},
            *history[-4:],
            {"role": "user", "content": enhanced_message},
        ]

        response = await self.llm.chat(messages, temperature=0.4, max_tokens=400)
        severity = "high" if any("danger" in o.lower() for o in observations) else "low" if observations else None

        return AgentResult(
            response=response,
            severity=severity,
            suggestions=observations[:3],
            agent_used="vitals_agent",
            observations=observations,
        )


def _parse_vitals(text: str) -> dict:
    """Extract numeric vital values from free text."""
    result = {}
    # SpO2
    m = re.search(r"(?:spo2|oxygen|o2)[^\d]*(\d{2,3})", text, re.IGNORECASE)
    if m:
        result["spo2"] = float(m.group(1))
    # Pulse
    m = re.search(r"(?:pulse|heart rate|hr)[^\d]*(\d{2,3})", text, re.IGNORECASE)
    if m:
        result["pulse"] = float(m.group(1))
    # Temperature
    m = re.search(r"(?:temp|temperature)[^\d]*(\d{2,3}(?:\.\d)?)", text, re.IGNORECASE)
    if m:
        result["temperature"] = float(m.group(1))
    # BP
    m = re.search(r"(\d{2,3})\s*/\s*(\d{2,3})", text)
    if m:
        result["systolic_bp"] = float(m.group(1))
        result["diastolic_bp"] = float(m.group(2))
    return result


def _assess_vitals(parsed: dict, language: str) -> list[str]:
    observations = []
    for key, value in parsed.items():
        low, high = VITAL_RANGES.get(key, (None, None))
        if low is None:
            continue
        if value < low:
            label = key.replace("_", " ").upper()
            obs = f"{label} is LOW ({value}) — may need attention"
            if language == "hi":
                obs = f"{label} कम है ({value}) — ध्यान की ज़रूरत हो सकती है"
            observations.append(obs)
        elif value > high:
            label = key.replace("_", " ").upper()
            obs = f"{label} is HIGH ({value}) — may need attention"
            if language == "hi":
                obs = f"{label} अधिक है ({value}) — ध्यान की ज़रूरत हो सकती है"
            observations.append(obs)
    return observations
