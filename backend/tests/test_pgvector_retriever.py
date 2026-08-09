import pytest
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
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
    )

    chunk_b = DocumentChunk(
        document_id=document.id,
        content="PostgreSQL database systems",
        embedding=[0.0, 1.0, 0.0] + [0.0] * 1533,
    )

    db_session.add_all(
        [
            chunk_a,
            chunk_b,
        ]
    )

    await db_session.commit()

    retriever = PgVectorRetriever(
        db_session,
    )

    results = await retriever.retrieve(
        embedding=[1.0, 0.0, 0.0] + [0.0] * 1533,
        top_k=2,
    )

    assert len(results) == 2
    assert results[0].chunk.content == "Python and AI engineering"
    assert results[0].score > results[1].score
