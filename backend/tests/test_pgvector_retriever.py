from uuid import uuid4

import pytest
from app.models import DocumentChunk
from app.models.document import Document
from app.models.tenant import Tenant
from app.rag.providers.pgvector import PgVectorRetriever


@pytest.mark.asyncio
async def test_pgvector_retriever_returns_nearest_chunk(
    db_session,
    tenant,
) -> None:
    document = Document(
        tenant_id=tenant.id,
        filename="test.txt",
        content_type="text/plain",
    )

    db_session.add(document)

    await db_session.flush()

    chunk_a = DocumentChunk(
        tenant_id=tenant.id,
        document_id=document.id,
        content="Python and AI engineering",
        embedding=[1.0, 0.0, 0.0] + [0.0] * 1533,
        document_metadata={},
    )

    chunk_b = DocumentChunk(
        tenant_id=tenant.id,
        document_id=document.id,
        content="PostgreSQL database systems",
        embedding=[0.0, 1.0, 0.0] + [0.0] * 1533,
    )

    db_session.add_all([chunk_a, chunk_b])

    await db_session.commit()

    retriever = PgVectorRetriever(db_session)

    results = await retriever.retrieve(
        embedding=[1.0, 0.0, 0.0] + [0.0] * 1533,
        tenant_id=tenant.id,
        top_k=2,
    )

    assert len(results) == 2
    assert results[0].chunk.content == "Python and AI engineering"
    assert results[0].score > results[1].score


@pytest.mark.asyncio
async def test_pgvector_retriever_filters_by_metadata(
    db_session,
    tenant,
) -> None:
    embedding = [1.0, 0.0, 0.0] + [0.0] * 1533

    finance_document = Document(
        tenant_id=tenant.id,
        filename="finance_policy.txt",
        content_type="text/plain",
        document_metadata={
            "department": "finance",
            "document_type": "policy",
        },
    )

    hr_document = Document(
        tenant_id=tenant.id,
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
        tenant_id=tenant.id,
        content="Finance refund policy",
        embedding=embedding,
        document_metadata={
            "department": "finance",
            "document_type": "policy",
        },
    )

    hr_chunk = DocumentChunk(
        document_id=hr_document.id,
        tenant_id=tenant.id,
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
        tenant_id=tenant.id,
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
    tenant,
) -> None:
    embedding = [1.0, 0.0, 0.0] + [0.0] * 1533

    finance_v3 = Document(
        tenant_id=tenant.id,
        filename="finance_policy_v3.txt",
        content_type="text/plain",
        document_metadata={
            "department": "finance",
            "document_type": "policy",
            "version": "3",
        },
    )

    finance_v2 = Document(
        tenant_id=tenant.id,
        filename="finance_policy_v2.txt",
        content_type="text/plain",
        document_metadata={
            "department": "finance",
            "document_type": "policy",
            "version": "2",
        },
    )

    hr_v3 = Document(
        tenant_id=tenant.id,
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
                tenant_id=tenant.id,
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
                tenant_id=tenant.id,
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
                tenant_id=tenant.id,
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
        tenant_id=tenant.id,
        top_k=5,
        filters={
            "department": "finance",
            "version": "3",
        },
    )

    assert len(results) == 1
    assert results[0].chunk.content == "Finance policy version 3"
    assert results[0].chunk.filename == "finance_policy_v3.txt"


@pytest.mark.asyncio
async def test_pgvector_retriever_enforces_tenant_isolation(
        db_session,
        tenant,
) -> None:
    embedding = [1.0, 0.0, 0.0] + [0.0] * 1533

    # Tenant A is provided by the existing tenant fixture

    tenant_a = tenant

    # Create Tenant B.
    tenant_b = Tenant(
        name="Tenant B",
        slug=f"tenant-b-{uuid4().hex}",
    )

    db_session.add(tenant_b)
    await db_session.flush()

    # Create one document for each tenant.
    document_a = Document(
        tenant_id=tenant_a.id,
        filename="tenant_a_policy.txt",
        content_type="text/plain",
    )

    document_b = Document(
        tenant_id=tenant_b.id,
        filename="tenant_b_policy.txt",
        content_type="text/plain",
    )

    db_session.add_all([document_a, document_b])
    await db_session.flush()

    # Both tenants deliberately have identical embeddings.
    chunk_a = DocumentChunk(
        tenant_id=tenant_a.id,
        document_id=document_a.id,
        content="Tenant A confidential refund policy",
        embedding=embedding,
        document_metadata={"department": "finance"},
    )

    chunk_b = DocumentChunk(
        tenant_id=tenant_b.id,
        document_id=document_b.id,
        content="Tenant B confidential refund policy",
        embedding=embedding,
        document_metadata={"department": "finance"},
    )

    db_session.add_all([chunk_a, chunk_b])
    await db_session.commit()

    retriever = PgVectorRetriever(session=db_session)

    # Retrieve as Tenant A.
    results_a = await retriever.retrieve(
        embedding=embedding,
        tenant_id=tenant_a.id,
        top_k=10,
    )

    # Retrieve as Tenant B.
    results_b = await retriever.retrieve(
        embedding=embedding,
        tenant_id=tenant_b.id,
        top_k=10,
    )

    # Tenant A must only see its own document.
    assert len(results_a) == 1
    assert results_a[0].chunk.document_id == str(document_a.id)
    assert results_a[0].chunk.content == "Tenant A confidential refund policy"

    # Tenant B must only see its own document
    assert len(results_b) == 1
    assert results_b[0].chunk.document_id == str(document_b.id)
    assert results_b[0].chunk.content == "Tenant B confidential refund policy"


@pytest.mark.asyncio
async def test_pgvector_retriever_enforces_tenant_isolation_with_metadata_filters(
        db_session, tenant,
) -> None:
    from uuid import uuid4

    embedding = [1.0, 0.0, 0.0] + [0.0] * 1533

    # Tenant A is provided by the existing tenant fixture

    tenant_a = tenant

    # Create Tenant B.
    tenant_b = Tenant(
        name="Tenant B",
        slug=f"tenant-b-{uuid4().hex}",
    )

    db_session.add(tenant_b)
    await db_session.flush()

    # Create one document for each tenant.
    document_a = Document(
        tenant_id=tenant_a.id,
        filename="tenant_a_finance.txt",
        content_type="text/plain",
    )

    document_b = Document(
        tenant_id=tenant_b.id,
        filename="tenant_b_finance.txt",
        content_type="text/plain",
    )

    db_session.add_all([document_a, document_b])
    await db_session.flush()

    # Both tenants deliberately have identical embeddings.
    db_session.add_all([
        DocumentChunk(
            tenant_id=tenant_a.id,
            document_id=document_a.id,
            content="Tenant A finance policy",
            embedding=embedding,
            document_metadata={"department": "finance"},
        ),
        DocumentChunk(
            tenant_id=tenant_b.id,
            document_id=document_b.id,
            content="Tenant B finance policy",
            embedding=embedding,
            document_metadata={"department": "finance"},
            ),
        ]
    )

    await db_session.commit()

    retriever = PgVectorRetriever(session=db_session)

    results = await retriever.retrieve(
        embedding=embedding,
        tenant_id=tenant_a.id,
        top_k=10,
        filters={"department": "finance"},
    )

    assert len(results) == 1
    assert results[0].chunk.document_id == str(document_a.id)
    assert results[0].chunk.content == "Tenant A finance policy"
