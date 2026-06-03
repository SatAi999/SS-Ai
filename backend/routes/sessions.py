"""FastAPI route — Sessions"""
from __future__ import annotations
import logging

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from models.database import get_db
from models.orm_models import Session as DBSession, Message
from models.schemas import SessionOut, SessionCreate
from services.session_service import get_or_create_session

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/create", response_model=SessionOut)
async def create_session(
    body: SessionCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new chat session."""
    session = await get_or_create_session(db, session_id=None, language=body.language)
    return SessionOut(
        id=session.id,
        language=session.language,
        created_at=session.created_at,
        updated_at=session.updated_at,
        messages=[],
    )


@router.get("/{session_id}", response_model=SessionOut)
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve a session with its messages."""
    result = await db.execute(
        select(DBSession).where(DBSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    msg_result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at.asc())
    )
    messages = msg_result.scalars().all()

    return SessionOut(
        id=session.id,
        language=session.language,
        created_at=session.created_at,
        updated_at=session.updated_at,
        messages=messages,
    )


@router.get("/history")
async def get_history(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Paginated session history."""
    offset = (page - 1) * limit

    count_result = await db.execute(select(func.count(DBSession.id)))
    total = count_result.scalar()

    sessions_result = await db.execute(
        select(DBSession)
        .order_by(DBSession.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    sessions = sessions_result.scalars().all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "sessions": [
            {
                "id": s.id,
                "language": s.language,
                "created_at": s.created_at.isoformat(),
                "updated_at": s.updated_at.isoformat(),
            }
            for s in sessions
        ],
    }
