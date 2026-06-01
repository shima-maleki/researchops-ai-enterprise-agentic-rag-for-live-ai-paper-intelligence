from __future__ import annotations

from backend.agents.graph import RagAgent
from backend.agents.tools import RetrieverTool
from backend.core.config import Settings, get_settings
from backend.services.embeddings import EmbeddingService
from backend.services.llm import ChatGenerationService
from backend.services.qdrant_store import QdrantStore


class RagService:
    def __init__(self, agent: RagAgent) -> None:
        self.agent = agent

    @classmethod
    def from_settings(cls, settings: Settings | None = None) -> RagService:
        settings = settings or get_settings()
        embedding_service = EmbeddingService.from_settings(settings)
        qdrant_store = QdrantStore.from_settings(settings)
        chat_generation_service = ChatGenerationService.from_settings(settings)

        return cls(
            agent=RagAgent(
                retriever_tool=RetrieverTool(
                    embedding_service=embedding_service,
                    qdrant_store=qdrant_store,
                ),
                chat_generation_service=chat_generation_service,
            )
        )

    def answer(self, message: str) -> dict:
        result = self.agent.invoke(message)
        return {
            "answer": result["answer"],
            "sources": result["sources"],
        }
