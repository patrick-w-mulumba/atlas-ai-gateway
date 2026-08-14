import asyncio

from app.db.database import AsyncSessionLocal
from app.embeddings.mock import MockEmbeddingProvider
from app.ingestion.service import IngestionService
from app.ingestion.simple_chunker import SimpleChunker
from app.ingestion.text_loader import TextLoader


async def main() -> None:

    embedding_provider = MockEmbeddingProvider()

    ingestion_service = IngestionService(
        loader=TextLoader(),
        chunker=SimpleChunker(chunk_size=200, overlap=20),
        embedding_provider=embedding_provider,
    )

    async with AsyncSessionLocal() as session:
        await ingestion_service.ingest(
            session=session,
            filename="refund_policy.txt",
            content_type="text/plain",
            content=b"Customers may request a refund within 30 days of purchase.",
            metadata={
                "department": "finance",
                "document_type": "policy",
                "version": "1",
            },
        )


if __name__ == "__main__":
    asyncio.run(main())
