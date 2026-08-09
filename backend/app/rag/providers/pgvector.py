from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
    ) -> list[RetrievalResult]:

        statement = (
            select(
                DocumentChunk,
                DocumentChunk.embedding.cosine_distance(embedding).label("distance"),
            )
            .order_by(DocumentChunk.embedding.cosine_distance(embedding))
            .limit(top_k)
        )

        result = await self._session.execute(statement)

        rows = result.all()

        results: list[RetrievalResult] = []

        for chunk, distance in rows:
            results.append(
                RetrievalResult(
                    chunk=RagDocumentChunk(
                        id=str(chunk.id),
                        document_id=str(chunk.document_id),
                        content=chunk.content,
                    ),
                    score=1.0 - float(distance),
                )
            )

        return results
