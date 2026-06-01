from __future__ import annotations

from backend.core.config import Settings, get_settings
from backend.schemas.papers import PaperMetadata
from backend.services.qdrant_store import QdrantStore


class PaperSearchService:
    def __init__(self, qdrant_store: QdrantStore) -> None:
        self.qdrant_store = qdrant_store

    @classmethod
    def from_settings(cls, settings: Settings | None = None) -> PaperSearchService:
        return cls(qdrant_store=QdrantStore.from_settings(settings or get_settings()))

    def search(
        self,
        *,
        keyword: str | None = None,
        category: str | None = None,
        limit: int = 50,
    ) -> list[PaperMetadata]:
        results = self.qdrant_store.payload_search(
            keyword=keyword,
            category=category,
            limit=limit,
        )

        return [
            PaperMetadata(
                title=str(payload.get("title", "")),
                authors=self._authors(payload.get("authors", [])),
                published_date=str(payload.get("published_date", "")),
                url=str(payload.get("pdf_url", "")),
                category=str(payload.get("category", "")),
            )
            for result in results
            for payload in [result["payload"]]
        ]

    def _authors(self, value: object) -> list[str]:
        if isinstance(value, list):
            return [str(author) for author in value]
        if isinstance(value, str):
            return [value]
        return []
