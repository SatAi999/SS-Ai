"""General utility helpers."""
from __future__ import annotations
import re
import unicodedata


def truncate_text(text: str, max_words: int = 150) -> str:
    """Truncate text to a maximum word count, preserving sentences."""
    words = text.split()
    if len(words) <= max_words:
        return text
    truncated = " ".join(words[:max_words])
    # Try to end at a sentence boundary
    match = re.search(r"[.!?।][^.!?।]*$", truncated)
    if match:
        return truncated[: match.start() + 1]
    return truncated + "..."


def normalize_language(lang: str) -> str:
    """Normalize language code to supported values."""
    lang = lang.lower().strip()
    if lang in ("hi", "hin", "hindi"):
        return "hi"
    return "en"


def extract_severity(text: str) -> str:
    """Heuristically extract severity level from LLM response text."""
    lower = text.lower()
    if any(w in lower for w in ["critical", "emergency", "immediate", "life-threatening", "अति गंभीर"]):
        return "critical"
    if any(w in lower for w in ["high", "serious", "severe", "urgent", "गंभीर"]):
        return "high"
    if any(w in lower for w in ["moderate", "medium", "concern", "watch", "मध्यम"]):
        return "medium"
    return "low"


def clean_llm_response(text: str) -> str:
    """Remove common LLM artifacts."""
    # Remove leading/trailing whitespace
    text = text.strip()
    # Normalize unicode
    text = unicodedata.normalize("NFC", text)
    # Remove multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text
