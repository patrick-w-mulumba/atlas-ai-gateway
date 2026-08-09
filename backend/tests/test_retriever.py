import pytest
from app.rag.models import DocumentChunk
from app.rag.providers.memory import MemoryRetriever


@pytest.mark.asyncio
async def test_memory_retriever_returns_relevant_chunks() -> None:
    chunks = [
        DocumentChunk(
            id="1",
            document_id="doc-1",
            content="Python is used for AI engineering.",
        ),
        DocumentChunk(
            id="2",
            document_id="doc-2",
            content="PostgreSQL is a relational database.",
        ),
    ]

    retriever = MemoryRetriever(chunks)

    results = await retriever.retrieve(
        "Python AI engineering",
    )

    assert len(results) == 1
    assert results[0].chunk.id == "1"