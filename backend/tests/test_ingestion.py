import pytest
from app.embeddings.mock import MockEmbeddingProvider
from app.ingestion.service import IngestionService
from app.ingestion.simple_chunker import SimpleChunker
from app.ingestion.text_loader import TextLoader
from app.models.document_chunk import DocumentChunk
from sqlalchemy import select


@pytest.mark.asyncio
async def test_document_ingestion(
    db_session,
) -> None:

    service = IngestionService(
        loader=TextLoader(),
        chunker=SimpleChunker(
            chunk_size=20,
            overlap=5,
        ),
        embedding_provider=MockEmbeddingProvider(),
    )

    document = await service.ingest(
        session=db_session,
        filename="test.txt",
        content_type="text/plain",
        content=b"Python is useful for building AI applications with FastAPI.",
    )

    assert document.filename == "test.txt"

    result = await db_session.execute(
        select(DocumentChunk).where(DocumentChunk.document_id == document.id)
    )

    chunks = result.scalars().all()

    assert len(chunks) > 1
    assert all(len(chunk.embedding) == 1536 for chunk in chunks)
