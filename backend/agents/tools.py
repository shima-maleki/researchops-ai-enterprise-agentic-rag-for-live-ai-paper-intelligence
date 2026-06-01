from __future__ import annotations

from backend.agents.state import PaperContext
from backend.services.embeddings import EmbeddingService
from backend.services.qdrant_store import QdrantStore


class RetrieverTool:
    def __init__(
        self,
        embedding_service: EmbeddingService,
        qdrant_store: QdrantStore,
        top_k: int = 8,
    ) -> None:
        self.embedding_service = embedding_service
        self.qdrant_store = qdrant_store
        self.top_k = top_k

    def search(self, query: str) -> list[PaperContext]:
        query_vector = self.embedding_service.embed_texts([query])[0]
        results = self.qdrant_store.vector_search(
            query_vector,
            limit=self.top_k,
            category=self._infer_category(query),
        )

        return [self._to_paper_context(result) for result in results]

    def _to_paper_context(self, result: dict) -> PaperContext:
        payload = result["payload"]
        return {
            "title": str(payload.get("title", "")),
            "authors": self._authors(payload.get("authors", [])),
            "abstract": str(payload.get("abstract", "")),
            "published_date": str(payload.get("published_date", "")),
            "category": str(payload.get("category", "")),
            "url": str(payload.get("pdf_url", "")),
            "score": float(result.get("score", 0.0)),
        }

    def _infer_category(self, query: str) -> str | None:
        for category in ["cs.AI", "cs.CL", "cs.LG", "cs.IR"]:
            if category.lower() in query.lower():
                return category
        return None

    def _authors(self, value: object) -> list[str]:
        if isinstance(value, list):
            return [str(author) for author in value]
        if isinstance(value, str):
            return [value]
        return []
