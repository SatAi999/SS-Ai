"""FastAPI route — Vision (image analysis)"""
from __future__ import annotations
import logging
import uuid

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from vision.image_pipeline import process_upload
from agents.vision_agent import VisionAgent
from agents.safety_guardrail_agent import SafetyGuardrailAgent
from models.database import get_db
from models.orm_models import ImageRecord, Message, Session as DBSession
from models.schemas import VisionAnalysisResponse
from services.session_service import get_or_create_session

logger = logging.getLogger(__name__)
router = APIRouter()

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


@router.post("/analyze", response_model=VisionAnalysisResponse)
async def analyze_image(
    image: UploadFile = File(...),
    query: str = Form(default="What do you see in this image?"),
    language: str = Form(default="en"),
    session_id: str | None = Form(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Analyse a medical-context image and return healthcare guidance."""
    # Validate file type
    mime = image.content_type or ""
    if mime not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported image type: {mime}. Use JPEG, PNG, WebP.",
        )

    raw = await image.read()
    if not raw:
        raise HTTPException(status_code=422, detail="Empty image file")

    # Process and save image
    try:
        img_meta = await process_upload(raw, image.filename or "image.jpg", mime)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    # Ensure session
    session = await get_or_create_session(db, session_id, language)

    # Save image record
    db.add(ImageRecord(
        id=uuid.uuid4().hex,
        session_id=session.id,
        filename=img_meta["filename"],
        original_filename=img_meta["original_filename"],
        file_size=img_meta["file_size"],
        mime_type=img_meta["mime_type"],
        width=img_meta["width"],
        height=img_meta["height"],
    ))

    # Commit early so the DB write lock is released before model inference
    # (model loading can take minutes; holding the lock blocks all other requests)
    await db.commit()

    # Run vision + safety pipeline
    agent = VisionAgent()
    safety = SafetyGuardrailAgent()

    try:
        result = await agent.analyze(
            image_path=img_meta["saved_path"],
            query=query,
            language=language,
        )
    except Exception as e:
        logger.error("Vision analysis error: %s", e, exc_info=True)
        raise HTTPException(status_code=502, detail="Image analysis failed. Please try again.")

    safe_response = await safety.validate(result.response, language)

    # Save messages to DB
    db.add(Message(session_id=session.id, role="user", content=query, message_type="image"))
    db.add(Message(
        session_id=session.id,
        role="assistant",
        content=safe_response,
        message_type="text",
        severity=result.severity,
        agent_used=result.agent_used,
    ))

    return VisionAnalysisResponse(
        response=safe_response,
        session_id=session.id,
        severity=result.severity,
        suggestions=result.suggestions,
        emergency_alert=result.emergency_alert,
        observations=result.observations,
        agent_used=result.agent_used or "vision_agent",
        language=language,
    )
