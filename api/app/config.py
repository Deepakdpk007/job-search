"""Application settings loaded from environment variables."""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    database_url: str = "postgresql+asyncpg://jobsearch:jobsearch@localhost:5432/jobsearch"
    database_url_sync: str = "postgresql+psycopg://jobsearch:jobsearch@localhost:5432/jobsearch"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: str = "http://localhost:3000"

    # Ingestion
    ingestion_user_agent: str = "job-search-mvp/0.1"
    ingestion_request_timeout: int = 20
    ingestion_concurrency: int = 5

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
