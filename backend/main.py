"""
SehatSakhi AI — FastAPI Application Entry Point
"""
import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from configs.settings import get_settings
from models.database import init_db
from routes import voice, vision, chat, sessions, health

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("sehatsakhi")

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────
    logger.info("Starting SehatSakhi AI backend…")

    # Initialize database
    await init_db()
    logger.info("Database initialized")

    # Create upload directory
    os.makedirs(settings.upload_dir, exist_ok=True)
    logger.info("Upload directory ready: %s", settings.upload_dir)

    yield

    # ── Shutdown ─────────────────────────────────────────────
    logger.info("SehatSakhi AI backend shutting down")


app = FastAPI(
    title="SehatSakhi AI",
    description="Voice-first AI healthcare platform for ASHA workers",
    version="1.0.0",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ───────────────────────────────────────────────────
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(voice.router, prefix="/api/voice", tags=["Voice"])
app.include_router(vision.router, prefix="/api/vision", tags=["Vision"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["Sessions"])

# ── Static files (uploaded images) ───────────────────────────
if os.path.exists(settings.upload_dir):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/", include_in_schema=False)
async def root():
    return {"message": "SehatSakhi AI is running", "docs": "/docs"}
