from app.core.config import get_settings
from app.embeddings.azure_openai import (
    AzureOpenAIEmbeddingProvider,
)
from app.embeddings.mock import MockEmbeddingProvider
from app.embeddings.provider import EmbeddingProvider


def create_embedding_provider() -> EmbeddingProvider:
    settings = get_settings()

    if settings.embedding_provider == "azure-openai":
        return AzureOpenAIEmbeddingProvider()

    if settings.embedding_provider == "mock":
        return MockEmbeddingProvider()

    raise ValueError(f"Unsupported embedding_provider: {settings.embedding_provider}")
