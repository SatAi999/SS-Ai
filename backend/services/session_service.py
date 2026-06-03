"""Session service — create or retrieve DB sessions."""
from __future__ import annotations
import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.orm_models import Session as DBSession


async def get_or_create_session(
    db: AsyncSession,
    session_id: str | None,
    language: str = "en",
) -> DBSession:
    """Return existing session or create a new one."""
    if session_id:
        result = await db.execute(
            select(DBSession).where(DBSession.id == session_id)
        )
        existing = result.scalar_one_or_none()
        if existing:
            existing.updated_at = datetime.utcnow()
            return existing

    new_session = DBSession(
        id=str(uuid.uuid4()),
        language=language,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(new_session)
    await db.flush()
    return new_session
