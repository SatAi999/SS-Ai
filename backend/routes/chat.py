"""FastAPI route — Chat (text conversations)"""
from __future__ import annotations
import logging

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from agents.orchestrator import get_orchestrator, OrchestrationRequest
from models.database import get_db
from models.orm_models import Message, Session as DBSession
from models.schemas import ChatRequest, ChatResponse
from services.session_service import get_or_create_session

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/message", response_model=ChatResponse)
async def send_message(
    req: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """Process a text message and return AI healthcare response."""
    # Validate input
    message = req.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="Message cannot be empty")

    # Ensure session exists
    session = await get_or_create_session(db, req.session_id, req.language)

    # Load recent conversation history (last 6 exchanges)
    result = await db.execute(
        select(Message)
        .where(Message.session_id == session.id)
        .order_by(Message.created_at.desc())
        .limit(12)
    )
    db_messages = result.scalars().all()
    history = [
        {"role": m.role, "content": m.content}
        for m in reversed(db_messages)
    ]

    # Save user message
    db.add(Message(
        session_id=session.id,
        role="user",
        content=message,
        message_type="text",
    ))

    # Run orchestrator
    orchestrator = get_orchestrator()
    orch_req = OrchestrationRequest(
        message=message,
        language=req.language,
        session_id=session.id,
        conversation_history=history,
    )

    try:
        orch_result = await orchestrator.process(orch_req)
    except Exception as e:
        logger.error("Orchestrator error: %s", e, exc_info=True)
        raise HTTPException(status_code=502, detail="AI service temporarily unavailable.")

    # Save assistant message
    db.add(Message(
        session_id=session.id,
        role="assistant",
        content=orch_result.response,
        message_type="text",
        severity=orch_result.severity,
        agent_used=orch_result.agent_used,
    ))

    return ChatResponse(
        response=orch_result.response,
        session_id=session.id,
        severity=orch_result.severity,
        suggestions=orch_result.suggestions or [],
        emergency_alert=orch_result.emergency_alert,
        agent_used=orch_result.agent_used,
        language=req.language,
    )
