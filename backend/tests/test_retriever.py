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
            filename="python.txt",
        ),
        DocumentChunk(
            id="2",
            document_id="doc-2",
            content="PostgresSQL is a relational database.",
            filename="postgresql.txt",
        ),
    ]

    retriever = MemoryRetriever(chunks)

    embedding = [0.1] * 1536

    results = await retriever.retrieve(embedding=embedding, top_k=1)

    assert len(results) == 1
    assert results[0].chunk.id == "1"
    assert results[0].score == 1.0


@pytest.mark.asyncio
async def test_memory_retriever_with_filters_by_metadata() -> None:
    chunks = [
        DocumentChunk(
            id="finance-chunk",
            document_id="finance-doc",
            content="Finance refund policy",
            metadata={
                "department": "finance",
                "document_type": "policy",
            },
            filename="refund_policy.txt",
        ),
        DocumentChunk(
            id="hr-chunk",
            document_id="hr-doc",
            content="HR parental leave policy",
            metadata={
                "department": "hr",
                "document_type": "policy",
            },
            filename="refund_policy.txt",
        ),
    ]

    retriever = MemoryRetriever(chunks)

    results = await retriever.retrieve(
        embedding=[1.0, 0.0, 0.0],
        top_k=5,
        filters={
            "department": "finance",
        },
    )

    assert len(results) == 1

    assert results[0].chunk.metadata["department"] == "finance"

    assert results[0].chunk.content == "Finance refund policy"
