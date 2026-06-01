from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ResearchOps AI"
    app_version: str = "0.1.0"
    environment: str = "local"
    log_level: str = "INFO"

    openai_api_key: str | None = Field(default=None, repr=False)
    openai_chat_model: str = "gpt-4.1-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    qdrant_url: str | None = None
    qdrant_api_key: str | None = Field(default=None, repr=False)
    qdrant_collection_name: str = "research_papers"
    qdrant_vector_size: int = 1536
    arxiv_base_url: str = "https://export.arxiv.org/api/query"
    external_request_timeout_seconds: float = 15.0

    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
