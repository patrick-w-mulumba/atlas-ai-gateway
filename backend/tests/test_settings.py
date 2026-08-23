import pytest
from app.core.config import Settings
from pydantic import ValidationError


def test_azure_openai_timeout_must_be_positive() -> None:
    with pytest.raises(ValidationError):
        Settings(
            database_url="postgresql://test",
            redis_url="redis://test",
            azure_openai_timeout=0,
        )


def test_rag_min_relevance_score_must_be_between_zero_and_one() -> None:
    with pytest.raises(ValidationError):
        Settings(
            database_url="postgresql://test",
            redis_url="redis://test",
            rag_min_relevance_score=1.5,
        )


def test_embedding_dimensions_must_be_positive() -> None:
    with pytest.raises(ValidationError):
        Settings(
            database_url="postgresql://test",
            redis_url="redis://test",
            embedding_dimensions=0,
        )
