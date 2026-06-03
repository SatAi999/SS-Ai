"""Image service — higher-level image processing helpers."""
from __future__ import annotations
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def build_image_url(filename: str, base_url: str = "") -> str:
    """Construct public URL for a stored image."""
    return f"{base_url}/uploads/images/{filename}"


def delete_image_file(filename: str, upload_dir: str = "uploads/images") -> bool:
    """Delete an image file from disk. Returns True if deleted."""
    path = Path(upload_dir) / filename
    if path.exists():
        path.unlink()
        logger.info("Deleted image: %s", path)
        return True
    return False
