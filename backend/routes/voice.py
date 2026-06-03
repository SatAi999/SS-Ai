"""FastAPI route — Voice (STT + TTS)"""
from __future__ import annotations
import logging

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import Response

from voice.stt_service import get_stt_service
from voice.tts_service import get_tts_service
from models.schemas import TranscriptionResponse, SynthesisRequest

logger = logging.getLogger(__name__)
router = APIRouter()

MAX_AUDIO_BYTES = 25 * 1024 * 1024  # 25 MB


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    audio: UploadFile = File(..., description="Audio file (webm/mp3/wav)"),
    language: str = Form(default="en"),
):
    """Transcribe uploaded audio using Whisper."""
    if not audio.content_type or not audio.content_type.startswith(("audio/", "video/")):
        raise HTTPException(status_code=422, detail="Invalid audio file type")

    data = await audio.read()
    if len(data) > MAX_AUDIO_BYTES:
        raise HTTPException(status_code=413, detail="Audio file too large (max 25 MB)")

    if len(data) < 100:
        raise HTTPException(status_code=422, detail="Audio file is too small or empty")

    stt = get_stt_service()
    try:
        result = await stt.transcribe(data, language=language)
    except Exception as e:
        logger.error("STT error: %s", e)
        raise HTTPException(status_code=502, detail="Speech-to-text failed. Please try again.")

    return TranscriptionResponse(**result)


@router.post("/synthesize")
async def synthesize_speech(req: SynthesisRequest):
    """Convert text to speech audio."""
    tts = get_tts_service()
    try:
        audio_bytes = await tts.synthesize(req.text, language=req.language)
    except Exception as e:
        logger.error("TTS error: %s", e)
        raise HTTPException(status_code=502, detail="Text-to-speech failed.")

    if not audio_bytes:
        raise HTTPException(status_code=502, detail="TTS returned empty audio.")

    return Response(
        content=audio_bytes,
        media_type="audio/mpeg",
        headers={"Content-Disposition": "inline; filename=response.mp3"},
    )
