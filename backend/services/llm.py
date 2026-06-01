from __future__ import annotations

from openai import OpenAI

from backend.agents.state import PaperContext
from backend.core.config import Settings, get_settings
from backend.services.embeddings import EmbeddingConfigurationError


class ChatGenerationService:
    def __init__(self, client: OpenAI, model: str) -> None:
        self.client = client
        self.model = model

    @classmethod
    def from_settings(cls, settings: Settings | None = None) -> ChatGenerationService:
        settings = settings or get_settings()
        if not settings.openai_api_key:
            raise EmbeddingConfigurationError("OPENAI_API_KEY is required")

        return cls(
            client=OpenAI(api_key=settings.openai_api_key),
            model=settings.openai_chat_model,
        )

    def generate_answer(
        self,
        *,
        user_message: str,
        retrieved_papers: list[PaperContext],
    ) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are ResearchOps AI, an assistant for AI research "
                        "paper intelligence. Answer using only the retrieved "
                        "paper context. If the retrieved context does not "
                        "contain enough evidence, say that the available "
                        "papers do not provide enough information. Do not "
                        "fabricate paper titles, authors, dates, URLs, or "
                        "claims. Format the answer in readable Markdown with "
                        "short paragraphs and bullets when useful."
                    ),
                },
                {
                    "role": "user",
                    "content": self._build_prompt(user_message, retrieved_papers),
                },
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content or ""

    def stream_answer(
        self,
        *,
        user_message: str,
        retrieved_papers: list[PaperContext],
    ):
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are ResearchOps AI, an assistant for AI research "
                        "paper intelligence. Answer using only the retrieved "
                        "paper context. If the retrieved context does not "
                        "contain enough evidence, say that the available "
                        "papers do not provide enough information. Do not "
                        "fabricate paper titles, authors, dates, URLs, or "
                        "claims. Format the answer in readable Markdown with "
                        "short paragraphs and bullets when useful."
                    ),
                },
                {
                    "role": "user",
                    "content": self._build_prompt(user_message, retrieved_papers),
                },
            ],
            temperature=0.2,
            stream=True,
        )

        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    def _build_prompt(
        self,
        user_message: str,
        retrieved_papers: list[PaperContext],
    ) -> str:
        context_blocks = []
        for index, paper in enumerate(retrieved_papers, start=1):
            context_blocks.append(
                "\n".join(
                    [
                        f"Paper {index}",
                        f"Title: {paper['title']}",
                        f"Authors: {', '.join(paper['authors'])}",
                        f"Published: {paper['published_date']}",
                        f"Category: {paper['category']}",
                        f"URL: {paper['url']}",
                        f"Abstract: {paper['abstract']}",
                    ]
                )
            )

        return "\n\n".join(
            [
                f"Question: {user_message}",
                "Retrieved paper context:",
                "\n\n".join(context_blocks),
            ]
        )
