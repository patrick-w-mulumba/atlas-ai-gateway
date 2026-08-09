import pytest
from app.ingestion.simple_chunker import SimpleChunker


def test_chunker_splits_text() -> None:
    chunker = SimpleChunker(
        chunk_size=10,
        overlap=2,
    )

    chunks = chunker.chunk(
        "abcdefghijklmnopqrstuvwxyz",
    )

    assert len(chunks) > 1
    assert chunks[0] == "abcdefghij"
    assert chunks[1].startswith("ij")


def test_chunker_rejects_invalid_overlap() -> None:
    with pytest.raises(ValueError):
        SimpleChunker(
            chunk_size=10,
            overlap=10,
        )
