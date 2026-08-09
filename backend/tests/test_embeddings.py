import pytest
from app.embeddings.mock import MockEmbeddingProvider


@pytest.mark.asyncio
async def test_mock_embedding_has_expected_dimensions() -> None:
    provider = MockEmbeddingProvider()

    embedding = await provider.embed("Python and AI engineering")

    assert len(embedding) == 1536


@pytest.mark.asyncio
async def test_mock_embedding_is_deterministic() -> None:
    provider = MockEmbeddingProvider()

    first = await provider.embed("Atlas AI Gateway")

    second = await provider.embed("Atlas AI Gateway")

    assert first == second
