from __future__ import annotations

from backend.agents.graph import RagAgent
from backend.agents.tools import RetrieverTool
from backend.core.config import Settings, get_settings
from backend.services.embeddings import EmbeddingService
from backend.services.llm import ChatGenerationService
from backend.services.qdrant_store import QdrantStore


class RagService:
    def __init__(
        self,
        agent: RagAgent,
        retriever_tool: RetrieverTool,
        chat_generation_service: ChatGenerationService,
    ) -> None:
        self.agent = agent
        self.retriever_tool = retriever_tool
        self.chat_generation_service = chat_generation_service

    @classmethod
    def from_settings(cls, settings: Settings | None = None) -> RagService:
        settings = settings or get_settings()
        embedding_service = EmbeddingService.from_settings(settings)
        qdrant_store = QdrantStore.from_settings(settings)
        chat_generation_service = ChatGenerationService.from_settings(settings)
        retriever_tool = RetrieverTool(
            embedding_service=embedding_service,
            qdrant_store=qdrant_store,
        )

        return cls(
            agent=RagAgent(
                retriever_tool=retriever_tool,
                chat_generation_service=chat_generation_service,
            ),
            retriever_tool=retriever_tool,
            chat_generation_service=chat_generation_service,
        )

    def answer(self, message: str) -> dict:
        result = self.agent.invoke(message)
        return {
            "answer": result["answer"],
            "sources": result["sources"],
        }

    def stream_answer(self, message: str):
        retrieved_papers = self.retriever_tool.search(message)
        sources = self._format_sources(retrieved_papers)

        if not retrieved_papers:
            yield {
                "type": "delta",
                "content": (
                    "I could not find enough relevant ingested papers to answer "
                    "this question. Try ingesting more papers or asking a more "
                    "specific research question."
                ),
            }
            yield {"type": "sources", "sources": sources}
            yield {"type": "done"}
            return

        for delta in self.chat_generation_service.stream_answer(
            user_message=message,
            retrieved_papers=retrieved_papers,
        ):
            yield {"type": "delta", "content": delta}

        yield {"type": "sources", "sources": sources}
        yield {"type": "done"}

    def _format_sources(self, retrieved_papers: list[dict]) -> list[dict[str, str]]:
        seen_urls: set[str] = set()
        sources: list[dict[str, str]] = []

        for paper in retrieved_papers:
            url = paper.get("url", "")
            title = paper.get("title", "")
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            sources.append({"title": title, "url": url})

        return sources
