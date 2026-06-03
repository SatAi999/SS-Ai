"""Image utility helpers."""
from __future__ import annotations
from pathlib import Path
import imghdr


def get_image_mime(data: bytes) -> str | None:
    """Detect image MIME type from raw bytes."""
    kind = imghdr.what(None, h=data)
    mapping = {"jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp", "gif": "image/gif"}
    return mapping.get(kind)


def is_valid_image(data: bytes, max_mb: float = 10.0) -> bool:
    """Check image data is valid and within size limit."""
    if not data:
        return False
    size_mb = len(data) / (1024 * 1024)
    if size_mb > max_mb:
        return False
    mime = get_image_mime(data)
    return mime is not None


def safe_filename(original: str) -> str:
    """Sanitize an uploaded filename."""
    stem = Path(original).stem
    suffix = Path(original).suffix.lower()
    allowed_ext = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
    if suffix not in allowed_ext:
        suffix = ".jpg"
    safe = "".join(c for c in stem if c.isalnum() or c in "-_")[:40] or "image"
    return f"{safe}{suffix}"
