from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# ── Shared ────────────────────────────────────────────────────
SeverityLevel = Literal["low", "medium", "high", "critical"]
LanguageCode = Literal["en", "hi"]


# ── Chat ──────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    language: LanguageCode = "en"
    session_id: Optional[str] = None


class EmergencyAlert(BaseModel):
    severity: SeverityLevel
    message: str
    action: str = ""


class ChatResponse(BaseModel):
    response: str
    session_id: str
    severity: Optional[SeverityLevel] = None
    suggestions: list[str] = Field(default_factory=list)
    emergency_alert: Optional[EmergencyAlert] = None
    agent_used: Optional[str] = None
    language: LanguageCode = "en"


# ── Voice ─────────────────────────────────────────────────────
class TranscriptionResponse(BaseModel):
    text: str
    language: str
    confidence: Optional[float] = None


class SynthesisRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)
    language: LanguageCode = "en"


# ── Vision ────────────────────────────────────────────────────
class VisionAnalysisResponse(BaseModel):
    response: str
    session_id: str
    severity: Optional[SeverityLevel] = None
    suggestions: list[str] = Field(default_factory=list)
    emergency_alert: Optional[EmergencyAlert] = None
    observations: list[str] = Field(default_factory=list)
    concern_level: Optional[str] = None
    agent_used: str = "vision_agent"
    language: LanguageCode = "en"


# ── Session ───────────────────────────────────────────────────
class SessionCreate(BaseModel):
    language: LanguageCode = "en"


class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    message_type: str
    severity: Optional[SeverityLevel] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SessionOut(BaseModel):
    id: str
    language: str
    created_at: datetime
    updated_at: datetime
    messages: list[MessageOut] = Field(default_factory=list)

    class Config:
        from_attributes = True


# ── Health ────────────────────────────────────────────────────
class HealthResponse(BaseModel):
    status: str
    version: str
    llm_provider: str
    stt_provider: str
    tts_provider: str
    vision_provider: str
