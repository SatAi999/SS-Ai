"""
RAG Ingestion — load healthcare documents into ChromaDB.

Usage:
    python -m rag.ingestion
"""
from __future__ import annotations
import hashlib
import logging
import textwrap
from pathlib import Path

logger = logging.getLogger(__name__)

# Sample built-in healthcare knowledge snippets
HEALTHCARE_KNOWLEDGE = [
    {
        "content": textwrap.dedent("""
            Wound Care Basics:
            - Clean wounds gently with clean water
            - Apply gentle pressure to stop bleeding
            - Cover with a clean bandage
            - Watch for signs of infection: redness spreading, warmth, pus, increasing pain
            - Seek medical attention if wound is deep, won't stop bleeding, or shows infection signs
        """).strip(),
        "category": "wound_care",
        "language": "en",
    },
    {
        "content": textwrap.dedent("""
            Dehydration Warning Signs:
            - Dry mouth and lips
            - Dark yellow urine or no urine
            - Sunken eyes
            - Dizziness when standing
            - Skin that doesn't spring back quickly when pinched
            Management: ORS (oral rehydration solution), clean water, rest
            Seek help: if vomiting prevents drinking, infant or elderly patient, confusion
        """).strip(),
        "category": "dehydration",
        "language": "en",
    },
    {
        "content": textwrap.dedent("""
            Fever Management:
            - Normal temperature: 36.1–37.2°C
            - Fever: above 37.5°C
            - Cool the person with damp cloths, light clothing
            - Ensure good fluid intake
            - Seek medical attention: temperature above 39°C, fever in infant under 3 months,
              fever with stiff neck, rash, difficulty breathing, or lasting more than 3 days
        """).strip(),
        "category": "fever",
        "language": "en",
    },
    {
        "content": textwrap.dedent("""
            Maternal Health — Danger Signs in Pregnancy:
            - Heavy vaginal bleeding
            - Severe headache
            - Blurred vision or seeing spots
            - Severe abdominal pain
            - Baby not moving
            - Swollen hands/face
            - Fever
            - Difficulty breathing
            Any of these require IMMEDIATE medical attention.
        """).strip(),
        "category": "maternal_health",
        "language": "en",
    },
    {
        "content": textwrap.dedent("""
            Child Health — Warning Signs Requiring Medical Attention:
            - High fever (>38.5°C in infant, >39°C in older child)
            - Difficulty breathing / fast breathing
            - Refusing to eat or drink for 12+ hours
            - Persistent vomiting or diarrhea (risk of dehydration)
            - Unusual drowsiness or difficulty waking
            - Bulging fontanelle in infants
            - Convulsions / seizures
        """).strip(),
        "category": "child_health",
        "language": "en",
    },
    {
        "content": textwrap.dedent("""
            हाथ धोने का महत्व (Hand Hygiene):
            - खाना खाने से पहले और बाद में
            - शौच के बाद
            - बच्चे को छूने से पहले
            - घाव या बीमार व्यक्ति की देखभाल के बाद
            20 सेकंड तक साबुन और पानी से धोएं।
            हाथ धोना कई बीमारियों को रोकता है।
        """).strip(),
        "category": "hygiene",
        "language": "hi",
    },
]


def ingest_documents() -> int:
    from rag.chroma_service import get_chroma_service

    service = get_chroma_service()

    docs = [d["content"] for d in HEALTHCARE_KNOWLEDGE]
    metas = [{"category": d["category"], "language": d["language"]} for d in HEALTHCARE_KNOWLEDGE]
    ids = [hashlib.md5(d.encode()).hexdigest() for d in docs]

    service.add_documents(docs, metas, ids)
    count = service.count()
    logger.info("Knowledge base now contains %d documents", count)
    return count


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    n = ingest_documents()
    print(f"Ingested {n} documents successfully")
