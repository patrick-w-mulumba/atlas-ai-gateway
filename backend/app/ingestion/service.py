from sqlalchemy.ext.asyncio import AsyncSession

from app.embeddings.provider import EmbeddingProvider
from app.ingestion.chunker import Chunker
from app.ingestion.loader import DocumentLoader
from app.models.document import Document
from app.models.document_chunk import DocumentChunk


class IngestionService:
    def __init__(
        self,
        loader: DocumentLoader,
        chunker: Chunker,
        embedding_provider: EmbeddingProvider,
    ) -> None:
        self._loader = loader
        self._chunker = chunker
        self._embedding_provider = embedding_provider

    async def ingest(
        self,
        session: AsyncSession,
        filename: str,
        content_type: str,
        content: bytes,
    ) -> Document:

        text = await self._loader.load(content)

        chunks = self._chunker.chunk(text)

        document = Document(
            filename=filename,
            content_type=content_type,
        )

        session.add(document)

        await session.flush()

        for chunk in chunks:
            embedding = await self._embedding_provider.embed(chunk)

            document_chunk = DocumentChunk(
                document_id=document.id,
                content=chunk,
                embedding=embedding,
            )

            session.add(document_chunk)

        await session.commit()

        return document
