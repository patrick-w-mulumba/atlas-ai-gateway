from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.rag.models import DocumentChunk as RagDocumentChunk
from app.rag.models import RetrievalResult
from app.rag.retriever import Retriever


class PgVectorRetriever(Retriever):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def retrieve(
        self,
        embedding: list[float],
        top_k: int = 5,
        filters: dict[str, str] | None = None,
    ) -> list[RetrievalResult]:

        statement = select(
            DocumentChunk,
            Document,
            DocumentChunk.embedding.cosine_distance(embedding).label("distance"),
        ).join(Document, Document.id == DocumentChunk.document_id)

        if filters:
            for key, value in filters.items():
                statement = statement.where(
                    DocumentChunk.document_metadata[key].as_string() == value
                )

        statement = statement.order_by(DocumentChunk.embedding.cosine_distance(embedding)).limit(
            top_k
        )

        result = await self._session.execute(statement)

        rows = result.all()

        results: list[RetrievalResult] = []

        for chunk, document, distance in rows:
            results.append(
                RetrievalResult(
                    chunk=RagDocumentChunk(
                        id=str(chunk.id),
                        document_id=str(chunk.document_id),
                        content=chunk.content,
                        metadata=chunk.document_metadata,
                        filename=document.filename,
                    ),
                    score=1.0 - float(distance),
                )
            )

        return results
