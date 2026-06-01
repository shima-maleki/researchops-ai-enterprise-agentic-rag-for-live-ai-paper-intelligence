from __future__ import annotations

import logging
import uuid
from collections.abc import Iterable
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.http import models

from backend.core.config import Settings, get_settings

logger = logging.getLogger(__name__)

Payload = dict[str, Any]


class QdrantConfigurationError(RuntimeError):
    """Raised when Qdrant settings are missing or invalid."""


class QdrantStore:
    def __init__(
        self,
        client: QdrantClient,
        collection_name: str,
        vector_size: int,
    ) -> None:
        self.client = client
        self.collection_name = collection_name
        self.vector_size = vector_size

    @classmethod
    def from_settings(cls, settings: Settings | None = None) -> QdrantStore:
        settings = settings or get_settings()
        if not settings.qdrant_url:
            raise QdrantConfigurationError("QDRANT_URL is required")

        client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            timeout=10,
        )
        return cls(
            client=client,
            collection_name=settings.qdrant_collection_name,
            vector_size=settings.qdrant_vector_size,
        )

    def ensure_collection(self) -> None:
        if self.client.collection_exists(self.collection_name):
            logger.info("qdrant_collection_exists collection=%s", self.collection_name)
            return

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=models.VectorParams(
                size=self.vector_size,
                distance=models.Distance.COSINE,
            ),
        )
        logger.info(
            "qdrant_collection_created collection=%s vector_size=%s",
            self.collection_name,
            self.vector_size,
        )

    def upsert_papers(self, papers: Iterable[Payload]) -> int:
        points: list[models.PointStruct] = []

        for paper in papers:
            source_id = str(paper["id"])
            vector = paper["vector"]
            payload = dict(paper["payload"])
            payload.setdefault("source_id", source_id)
            points.append(
                models.PointStruct(
                    id=self._point_id(source_id),
                    vector=vector,
                    payload=payload,
                )
            )

        if not points:
            return 0

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )
        logger.info(
            "qdrant_points_upserted collection=%s count=%s",
            self.collection_name,
            len(points),
        )
        return len(points)

    def vector_search(
        self,
        query_vector: list[float],
        *,
        limit: int = 8,
        category: str | None = None,
    ) -> list[Payload]:
        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=self._category_filter(category),
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )

        return [
            {
                "id": point.id,
                "score": point.score,
                "payload": point.payload or {},
            }
            for point in response.points
        ]

    def payload_search(
        self,
        *,
        keyword: str | None = None,
        category: str | None = None,
        limit: int = 50,
    ) -> list[Payload]:
        points, _ = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=self._category_filter(category),
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )

        normalized_keyword = keyword.lower().strip() if keyword else None
        results: list[Payload] = []

        for point in points:
            payload = point.payload or {}
            if normalized_keyword and not self._payload_matches_keyword(
                payload,
                normalized_keyword,
            ):
                continue
            results.append({"id": point.id, "payload": payload})

        return results

    def _category_filter(self, category: str | None) -> models.Filter | None:
        if not category:
            return None

        return models.Filter(
            must=[
                models.FieldCondition(
                    key="category",
                    match=models.MatchValue(value=category),
                )
            ]
        )

    def _payload_matches_keyword(self, payload: Payload, keyword: str) -> bool:
        searchable_values = [
            payload.get("title", ""),
            payload.get("abstract", ""),
            " ".join(payload.get("authors", [])),
        ]
        return keyword in " ".join(searchable_values).lower()

    def _point_id(self, source_id: str) -> str:
        return str(uuid.uuid5(uuid.NAMESPACE_URL, source_id))
