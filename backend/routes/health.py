"""FastAPI route — Health check"""
from fastapi import APIRouter
from models.schemas import HealthResponse
from configs.settings import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="ok",
        version="1.0.0",
        llm_provider=settings.llm_provider,
        stt_provider=settings.stt_provider,
        tts_provider=settings.tts_provider,
        vision_provider=settings.vision_provider,
    )
