"""
Master Orchestrator — routes user requests to the correct agent pipeline.
"""
from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Optional

from orchestrator.intent_classifier import classify_intent
from agents.symptom_agent import SymptomAgent
from agents.vision_agent import VisionAgent
from agents.emergency_agent import EmergencyAgent
from agents.vitals_agent import VitalsAgent
from agents.safety_guardrail_agent import SafetyGuardrailAgent
from llms.conversational_llm_service import get_llm_service
from prompts.agent_prompts import AGENT_ROUTING_PROMPT

logger = logging.getLogger(__name__)


@dataclass
class OrchestrationRequest:
    message: str
    language: str = "en"
    session_id: Optional[str] = None
    image_path: Optional[str] = None
    conversation_history: list[dict] | None = None


@dataclass
class OrchestrationResponse:
    response: str
    session_id: str
    severity: Optional[str] = None
    suggestions: list[str] = None
    emergency_alert: Optional[dict] = None
    agent_used: Optional[str] = None
    observations: list[str] = None

    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []
        if self.observations is None:
            self.observations = []


class MasterOrchestrator:
    def __init__(self):
        self.llm = get_llm_service()
        self.safety = SafetyGuardrailAgent()
        self.symptom = SymptomAgent()
        self.vision = VisionAgent()
        self.emergency = EmergencyAgent()
        self.vitals = VitalsAgent()

    async def process(self, req: OrchestrationRequest) -> OrchestrationResponse:
        import uuid
        session_id = req.session_id or str(uuid.uuid4())

        try:
            # ── Image path present → vision pipeline ──────
            if req.image_path:
                result = await self.vision.analyze(
                    image_path=req.image_path,
                    query=req.message,
                    language=req.language,
                )
                safe = await self.safety.validate(result.response, req.language)
                result.response = safe
                result.session_id = session_id
                return result

            # ── Classify intent ───────────────────────────
            intent = await classify_intent(req.message, req.language)
            logger.info("Intent: %s | msg: %.60s", intent, req.message)

            history = req.conversation_history or []

            # ── Route by intent ───────────────────────────
            if intent in ("emergency", "critical"):
                result = await self.emergency.handle(req.message, req.language, history)

            elif intent in ("symptom_report", "health_question"):
                result = await self.symptom.handle(req.message, req.language, history)

            elif intent == "vitals_check":
                result = await self.vitals.handle(req.message, req.language, history)

            else:
                # General conversation — lightweight LLM
                result = await self._general_chat(req, history, intent)

            # ── Safety pass ───────────────────────────────
            safe_response = await self.safety.validate(result.response, req.language)
            result.response = safe_response
            result.session_id = session_id
            return result

        except Exception as e:
            logger.error("Orchestrator error: %s", e, exc_info=True)
            fallback = (
                "मुझे अभी कुछ समस्या हो रही है। कृपया दोबारा कोशिश करें।"
                if req.language == "hi"
                else "I encountered an issue. Please try again."
            )
            return OrchestrationResponse(
                response=fallback,
                session_id=session_id,
                agent_used="fallback",
            )

    async def _general_chat(
        self, req: OrchestrationRequest, history: list[dict], intent: str
    ) -> OrchestrationResponse:
        from prompts.system_prompts import get_system_prompt

        messages = [
            {"role": "system", "content": get_system_prompt(req.language)},
            *history[-6:],
            {"role": "user", "content": req.message},
        ]
        response = await self.llm.chat(messages, temperature=0.6, max_tokens=512)
        return OrchestrationResponse(
            response=response,
            session_id="",
            agent_used=f"general_chat_{intent}",
        )


# ── Singleton ─────────────────────────────────────────────────
_orchestrator: MasterOrchestrator | None = None


def get_orchestrator() -> MasterOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = MasterOrchestrator()
    return _orchestrator
