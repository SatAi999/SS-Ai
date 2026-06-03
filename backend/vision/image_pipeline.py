"""
Image Pipeline — validation, compression, format normalisation.
"""
from __future__ import annotations
import io
import logging
import uuid
from pathlib import Path

from PIL import Image, ImageOps

from configs.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_DIMENSION = 1024   # pixels
JPEG_QUALITY = 85


async def process_upload(
    raw_bytes: bytes,
    original_filename: str,
    mime_type: str,
) -> dict:
    """
    Validate, resize, compress and save an uploaded image.
    Returns metadata dict with saved path and image info.
    """
    # Validate MIME
    if mime_type not in ALLOWED_MIME_TYPES:
        raise ValueError(f"Unsupported image type: {mime_type}")

    # Validate size
    max_bytes = settings.max_image_size_mb * 1024 * 1024
    if len(raw_bytes) > max_bytes:
        raise ValueError(
            f"Image too large ({len(raw_bytes) // 1024} KB). "
            f"Max {settings.max_image_size_mb} MB."
        )

    # Open with Pillow
    img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
    orig_width, orig_height = img.size

    # Auto-rotate based on EXIF
    img = ImageOps.exif_transpose(img)

    # Resize if larger than max dimension
    if max(img.width, img.height) > MAX_DIMENSION:
        img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.LANCZOS)

    # Save to disk
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_id = uuid.uuid4().hex
    saved_filename = f"{file_id}.jpg"
    saved_path = upload_dir / saved_filename

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    compressed_bytes = buf.getvalue()

    saved_path.write_bytes(compressed_bytes)

    logger.info(
        "Image saved: %s (%d×%d → %d×%d, %d KB)",
        saved_filename, orig_width, orig_height,
        img.width, img.height,
        len(compressed_bytes) // 1024,
    )

    return {
        "filename": saved_filename,
        "original_filename": original_filename,
        "saved_path": str(saved_path),
        "file_size": len(compressed_bytes),
        "mime_type": "image/jpeg",
        "width": img.width,
        "height": img.height,
    }
