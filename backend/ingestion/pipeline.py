from __future__ import annotations

import logging

from backend.core.config import Settings, get_settings
from backend.ingestion.arxiv_client import ArxivClient
from backend.ingestion.normalizer import ArxivPaperNormalizer
from backend.services.embeddings import EmbeddingService
from backend.services.qdrant_store import QdrantStore

logger = logging.getLogger(__name__)


class IngestionPipeline:
    def __init__(
        self,
        arxiv_client: ArxivClient,
        normalizer: ArxivPaperNormalizer,
        embedding_service: EmbeddingService,
        qdrant_store: QdrantStore,
    ) -> None:
        self.arxiv_client = arxiv_client
        self.normalizer = normalizer
        self.embedding_service = embedding_service
        self.qdrant_store = qdrant_store

    @classmethod
    def from_settings(cls, settings: Settings | None = None) -> IngestionPipeline:
        settings = settings or get_settings()
        return cls(
            arxiv_client=ArxivClient(
                base_url=settings.arxiv_base_url,
                timeout_seconds=settings.external_request_timeout_seconds,
            ),
            normalizer=ArxivPaperNormalizer(),
            embedding_service=EmbeddingService.from_settings(settings),
            qdrant_store=QdrantStore.from_settings(settings),
        )

    def ingest(self, *, limit: int, categories: list[str]) -> dict[str, int | str]:
        raw_papers = self.arxiv_client.fetch_latest(categories=categories, limit=limit)
        papers = self.normalizer.normalize_many(raw_papers)
        embedding_texts = [paper.embedding_text for paper in papers]
        vectors = self.embedding_service.embed_texts(embedding_texts)

        points = [
            {
                "id": paper.id,
                "vector": vector,
                "payload": paper.payload(),
            }
            for paper, vector in zip(papers, vectors, strict=True)
        ]

        self.qdrant_store.ensure_collection()
        ingested_count = self.qdrant_store.upsert_papers(points)
        skipped_count = max(len(raw_papers) - len(papers), 0)

        logger.info(
            "ingestion_completed requested=%s normalized=%s ingested=%s skipped=%s",
            limit,
            len(papers),
            ingested_count,
            skipped_count,
        )

        return {
            "status": "ok",
            "ingested_count": ingested_count,
            "skipped_count": skipped_count,
        }
