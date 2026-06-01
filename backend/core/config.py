from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ResearchOps AI"
    app_version: str = "0.1.0"
    environment: str = "local"
    log_level: str = "INFO"

    openai_api_key: str | None = Field(default=None, repr=False)
    qdrant_url: str | None = None
    qdrant_api_key: str | None = Field(default=None, repr=False)
    arxiv_base_url: str = "https://export.arxiv.org/api/query"

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
