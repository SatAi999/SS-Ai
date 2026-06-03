"""
ChromaDB RAG Service — vector store for healthcare knowledge base.
"""
from __future__ import annotations
import logging
from pathlib import Path
from typing import Optional

from configs.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class ChromaService:
    """Wrapper around ChromaDB for healthcare knowledge retrieval."""

    COLLECTION_NAME = "healthcare_knowledge"

    def __init__(self):
        self._client = None
        self._collection = None

    def _get_collection(self):
        if self._collection is None:
            import chromadb

            Path(settings.chroma_persist_dir).mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(
                path=settings.chroma_persist_dir
            )
            self._collection = self._client.get_or_create_collection(
                name=self.COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    def query(
        self,
        query_text: str,
        n_results: int = 3,
        where: Optional[dict] = None,
    ) -> list[dict]:
        """Retrieve relevant documents for a query."""
        try:
            col = self._get_collection()
            if col.count() == 0:
                return []

            results = col.query(
                query_texts=[query_text],
                n_results=min(n_results, col.count()),
                where=where,
            )

            docs = []
            for i, doc in enumerate(results["documents"][0]):
                docs.append({
                    "content": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else None,
                })
            return docs
        except Exception as e:
            logger.warning("ChromaDB query error: %s", e)
            return []

    def add_documents(
        self,
        documents: list[str],
        metadatas: list[dict],
        ids: list[str],
    ) -> None:
        """Add documents to the knowledge base."""
        col = self._get_collection()
        col.add(documents=documents, metadatas=metadatas, ids=ids)
        logger.info("Added %d documents to ChromaDB", len(documents))

    def get_context_for_query(self, query: str, language: str = "en") -> str:
        """Return formatted context string from relevant docs."""
        docs = self.query(query, n_results=3)
        if not docs:
            return ""
        context = "\n\n".join(
            f"[Reference {i+1}]: {d['content']}" for i, d in enumerate(docs)
        )
        return context

    def count(self) -> int:
        try:
            return self._get_collection().count()
        except Exception:
            return 0


# ── Singleton ─────────────────────────────────────────────────
_chroma: ChromaService | None = None


def get_chroma_service() -> ChromaService:
    global _chroma
    if _chroma is None:
        _chroma = ChromaService()
    return _chroma
