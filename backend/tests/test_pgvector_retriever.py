import pytest
from app.models import DocumentChunk
from app.models.document import Document
from app.rag.providers.pgvector import PgVectorRetriever


@pytest.mark.asyncio
async def test_pgvector_retriever_returns_nearest_chunk(
    db_session,
) -> None:
    document = Document(
        filename="test.txt",
        content_type="text/plain",
    )

    db_session.add(document)

    await db_session.flush()

    chunk_a = DocumentChunk(
        document_id=document.id,
        content="Python and AI engineering",
        embedding=[1.0, 0.0, 0.0] + [0.0] * 1533,
        metadata={},
    )

    chunk_b = DocumentChunk(
        document_id=document.id,
        content="PostgreSQL database systems",
        embedding=[0.0, 1.0, 0.0] + [0.0] * 1533,
    )

    db_session.add_all([chunk_a, chunk_b])

    await db_session.commit()

    retriever = PgVectorRetriever(db_session)

    results = await retriever.retrieve(
        embedding=[1.0, 0.0, 0.0] + [0.0] * 1533,
        top_k=2,
    )

    assert len(results) == 2
    assert results[0].chunk.content == "Python and AI engineering"
    assert results[0].score > results[1].score


@pytest.mark.asyncio
async def test_pgvector_retriever_filters_by_metadata(
    db_session,
) -> None:
    embedding = [1.0, 0.0, 0.0] + [0.0] * 1533

    finance_document = Document(
        filename="finance_policy.txt",
        content_type="text/plain",
        document_metadata={
            "department": "finance",
            "document_type": "policy",
        },
    )

    hr_document = Document(
        filename="hr_policy.txt",
        content_type="text/plain",
        document_metadata={
            "department": "hr",
            "document_type": "policy",
        },
    )

    db_session.add_all([finance_document, hr_document])

    await db_session.flush()

    finance_chunk = DocumentChunk(
        document_id=finance_document.id,
        content="Finance refund policy",
        embedding=embedding,
        document_metadata={
            "department": "finance",
            "document_type": "policy",
        },
    )

    hr_chunk = DocumentChunk(
        document_id=hr_document.id,
        content="HR parental leave policy",
        embedding=embedding,
        document_metadata={
            "department": "hr",
            "document_type": "policy",
        },
    )

    db_session.add_all([finance_chunk, hr_chunk])

    await db_session.commit()

    retriever = PgVectorRetriever(session=db_session)

    results = await retriever.retrieve(
        embedding=embedding,
        top_k=5,
        filters={
            "department": "finance",
        },
    )

    assert len(results) == 1
    assert results[0].chunk.content == "Finance refund policy"
    assert results[0].chunk.filename == "finance_policy.txt"
    assert results[0].chunk.metadata["department"] == "finance"


@pytest.mark.asyncio
async def test_pgvector_retriever_filters_by_multiple_metadata_fields(
    db_session,
) -> None:
    embedding = [1.0, 0.0, 0.0] + [0.0] * 1533

    finance_v3 = Document(
        filename="finance_policy_v3.txt",
        content_type="text/plain",
        document_metadata={
            "department": "finance",
            "document_type": "policy",
            "version": "3",
        },
    )

    finance_v2 = Document(
        filename="finance_policy_v2.txt",
        content_type="text/plain",
        document_metadata={
            "department": "finance",
            "document_type": "policy",
            "version": "2",
        },
    )

    hr_v3 = Document(
        filename="hr_policy_v3.txt",
        content_type="text/plain",
        document_metadata={
            "department": "hr",
            "document_type": "policy",
            "version": "3",
        },
    )

    db_session.add_all([finance_v3, finance_v2, hr_v3])

    await db_session.flush()

    db_session.add_all(
        [
            DocumentChunk(
                document_id=finance_v3.id,
                content="Finance policy version 3",
                embedding=embedding,
                document_metadata={
                    "department": "finance",
                    "document_type": "policy",
                    "version": "3",
                },
            ),
            DocumentChunk(
                document_id=finance_v2.id,
                content="Finance policy version 2",
                embedding=embedding,
                document_metadata={
                    "department": "finance",
                    "document_type": "policy",
                    "version": "2",
                },
            ),
            DocumentChunk(
                document_id=hr_v3.id,
                content="HR policy version 3",
                embedding=embedding,
                document_metadata={
                    "department": "hr",
                    "document_type": "policy",
                    "version": "3",
                },
            ),
        ]
    )

    await db_session.commit()

    retriever = PgVectorRetriever(session=db_session)

    results = await retriever.retrieve(
        embedding=embedding,
        top_k=5,
        filters={
            "department": "finance",
            "version": "3",
        },
    )

    assert len(results) == 1
    assert results[0].chunk.content == "Finance policy version 3"
    assert results[0].chunk.filename == "finance_policy_v3.txt"
