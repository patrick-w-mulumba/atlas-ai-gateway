import pytest
from app.rag.models import DocumentChunk
from app.rag.providers.memory import MemoryRetriever


@pytest.mark.asyncio
async def test_memory_retriever_returns_chunks() -> None:
    chunks = [
        DocumentChunk(
            id="1",
            document_id="doc-1",
            content="Python is used for AI engineering.",
        ),
        DocumentChunk(
            id="2",
            document_id="doc-2",
            content="PostgresSQL is a relational database.",
        ),
    ]

    retriever = MemoryRetriever(chunks)

    embedding = [0.1] * 1536

    results = await retriever.retrieve(embedding=embedding, top_k=1)

    assert len(results) == 1
    assert results[0].chunk.id == "1"
    assert results[0].score == 1.0
