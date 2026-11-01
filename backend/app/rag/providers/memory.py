import uuid

from app.rag.models import DocumentChunk, RetrievalResult
from app.rag.retriever import Retriever


class MemoryRetriever(Retriever):
    def __init__(self, chunks: list[DocumentChunk]) -> None:
        self._chunks = chunks

    async def retrieve(
        self,
        embedding: list[float],
        tenant_id: uuid.UUID,
        top_k: int = 5,
        filters: dict[str, str] | None = None,
    ) -> list[RetrievalResult]:

        filtered_chunks = self._chunks

        if filters:
            filtered_chunks = [
                chunk
                for chunk in filtered_chunks
                if all(chunk.metadata.get(key) == value for key, value in filters.items())
            ]

        results = [
            RetrievalResult(
                chunk=chunk,
                score=1.0,
            )
            for chunk in filtered_chunks
        ]

        return results[:top_k]
