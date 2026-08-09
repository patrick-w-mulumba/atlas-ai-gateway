from app.rag.models import DocumentChunk, RetrievalResult
from app.rag.retriever import Retriever


class MemoryRetriever(Retriever):
    def __init__(self, chunks: list[DocumentChunk]) -> None:
        self._chunks = chunks

    async def retrieve(
        self,
        embedding: list[float],
        top_k: int = 5,
    ) -> list[RetrievalResult]:

        results = [
            RetrievalResult(
                chunk=chunk,
                score=1.0,
            )
            for chunk in self._chunks
        ]

        return results[:top_k]
