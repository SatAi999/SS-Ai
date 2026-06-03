"""
Intent Classifier — lightweight keyword + LLM-based intent detection.
Fast keyword pass first; LLM only if ambiguous.
"""
from __future__ import annotations
import re
import logging

logger = logging.getLogger(__name__)

# ── Keyword rules (fast, no LLM) ─────────────────────────────
KEYWORD_MAP: list[tuple[str, list[str]]] = [
    ("emergency", [
        "unconscious", "not breathing", "chest pain", "heart attack",
        "stroke", "seizure", "choking", "anaphylaxis", "poison",
        "heavy bleeding", "severe burn", "बेहोश", "दम घुट", "दिल का दौरा",
    ]),
    ("vitals_check", [
        "blood pressure", "bp", "pulse", "spo2", "oxygen level",
        "temperature", "fever degree", "heart rate", "रक्तचाप", "नब्ज",
    ]),
    ("symptom_report", [
        "pain", "swelling", "fever", "cough", "vomiting", "diarrhea",
        "rash", "wound", "bleeding", "burn", "bruise", "headache",
        "दर्द", "सूजन", "बुखार", "खांसी", "उल्टी", "दस्त", "घाव",
    ]),
    ("pregnancy", [
        "pregnant", "pregnancy", "trimester", "contractions", "fetal",
        "गर्भ", "गर्भवती", "प्रसव", "डिलीवरी",
    ]),
    ("child_health", [
        "baby", "infant", "child", "toddler", "newborn", "vaccination",
        "बच्चा", "शिशु", "नवजात", "टीका",
    ]),
    ("nutrition", [
        "diet", "nutrition", "food", "vitamin", "deficiency", "malnutrition",
        "खाना", "पोषण", "विटामिन", "कमी",
    ]),
    ("education", [
        "how to", "what is", "explain", "teach", "hygiene", "prevent",
        "कैसे", "क्या है", "बताएं", "स्वच्छता",
    ]),
    ("greeting", [
        "hello", "hi", "namaste", "good morning", "नमस्ते", "हेलो",
    ]),
]


async def classify_intent(message: str, language: str = "en") -> str:
    """Return intent string. Fast path: keyword match; LLM fallback."""
    lower = message.lower()

    for intent, keywords in KEYWORD_MAP:
        if any(kw in lower for kw in keywords):
            return intent

    # LLM-based classification for ambiguous messages
    return await _llm_classify(message, language)


async def _llm_classify(message: str, language: str) -> str:
    from llms.conversational_llm_service import get_llm_service
    llm = get_llm_service()

    prompt = (
        "Classify the following message into ONE intent category. "
        "Categories: emergency, symptom_report, vitals_check, pregnancy, "
        "child_health, elderly_care, nutrition, education, greeting, general_health.\n"
        f"Message: {message}\n"
        "Respond with ONLY the category name, nothing else."
    )
    try:
        result = await llm.chat(
            [{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=20,
        )
        intent = result.strip().lower().replace(" ", "_")
        valid = {
            "emergency", "symptom_report", "vitals_check", "pregnancy",
            "child_health", "elderly_care", "nutrition", "education",
            "greeting", "general_health",
        }
        return intent if intent in valid else "general_health"
    except Exception as e:
        logger.warning("Intent classification LLM error: %s", e)
        return "general_health"
