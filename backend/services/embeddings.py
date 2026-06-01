from __future__ import annotations

from openai import OpenAI

from backend.core.config import Settings, get_settings


class EmbeddingConfigurationError(RuntimeError):
    """Raised when embedding settings are missing or invalid."""


class EmbeddingService:
    def __init__(self, client: OpenAI, model: str) -> None:
        self.client = client
        self.model = model

    @classmethod
    def from_settings(cls, settings: Settings | None = None) -> EmbeddingService:
        settings = settings or get_settings()
        if not settings.openai_api_key:
            raise EmbeddingConfigurationError("OPENAI_API_KEY is required")

        return cls(
            client=OpenAI(api_key=settings.openai_api_key),
            model=settings.openai_embedding_model,
        )

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        response = self.client.embeddings.create(
            model=self.model,
            input=texts,
        )
        return [embedding.embedding for embedding in response.data]
