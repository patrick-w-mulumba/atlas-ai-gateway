from app.embeddings.factory import create_embedding_provider
from app.embeddings.mock import MockEmbeddingProvider


def test_create_mock_embedding_provider() -> None:
    provider = create_embedding_provider()

    assert isinstance(provider, MockEmbeddingProvider)
