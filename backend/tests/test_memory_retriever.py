import pytest
from app.rag.models import DocumentChunk
from app.rag.providers.memory import MemoryRetriever


@pytest.mark.asyncio
async def test_memory_retriever_returns_relevant_chunks(tenant) -> None:
    chunks = [
        DocumentChunk(
            id="chunk-1",
            document_id="doc-1",
            filename="python_ai.txt",
            content="Python and AI engineering",
            metadata={
                "department": "engineering",
                "document_type": "guide",
            },
        ),
        DocumentChunk(
            id="chunk-2",
            document_id="doc-2",
            filename="database.txt",
            content="PostgreSQL database systems",
            metadata={
                "department": "engineering",
                "document_type": "guide",
            },
        ),
    ]

    retriever = MemoryRetriever(chunks)

    results = await retriever.retrieve(
        embedding=[1.0, 0.0, 0.0],
        tenant_id=tenant.id,
        top_k=2,
    )

    assert len(results) == 2
    assert results[0].chunk.content == "Python and AI engineering"
    assert results[0].chunk.filename == "python_ai.txt"
    assert results[0].score >= results[1].score


@pytest.mark.asyncio
async def test_memory_retriever_filters_by_metadata(tenant) -> None:
    chunks = [
        DocumentChunk(
            id="finance-chunk",
            document_id="finance-doc",
            content="Finance refund policy",
            metadata={
                "department": "finance",
                "document_type": "policy",
            },
            filename="finance-refund.pdf",
        ),
        DocumentChunk(
            id="hr-chunk",
            document_id="hr-doc",
            content="HR parental leave policy",
            metadata={
                "department": "hr",
                "document_type": "policy",
            },
            filename="hr-policy.pdf",
        ),
    ]

    retriever = MemoryRetriever(chunks)

    results = await retriever.retrieve(
        embedding=[1.0, 0.0, 0.0],
        tenant_id=tenant.id,
        top_k=5,
        filters={
            "department": "finance",
        },
    )

    assert len(results) == 1
    assert results[0].chunk.metadata["department"] == "finance"
    assert results[0].chunk.content == "Finance refund policy"
