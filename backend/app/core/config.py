from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_name: str = "Atlas AI Gateway"
    app_env: str = "development"
    log_level: str = "INFO"

    database_url: str
    redis_url: str

    llm_provider: str = "mock"
    llm_model: str = "mock-model"

    embedding_provider: str = "mock"
    embedding_model: str = "mock-embedding"
    embedding_dimensions: int = Field(default=1536, gt=0)

    # azure_openai_endpoint: str | None = None
    # azure_openai_api_key: str | None = None
    azure_openai_api_version: str = "2024-10-21"
    azure_openai_timeout: float = Field(default=30.0, gt=0)

    otel_enabled: bool = False
    otel_endpoint: str | None = None

    rag_min_relevance_score: float = Field(default=0.7, ge=0.0, le=1.0)

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
