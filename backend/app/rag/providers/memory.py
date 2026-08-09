from app.rag.models import DocumentChunk, RetrievalResult
from app.rag.retriever import Retriever


class MemoryRetriever(Retriever):
    def __init__(self, chunks: list[DocumentChunk]) -> None:
        self._chunks = chunks

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[RetrievalResult]:

        query_words = set(query.lower().split())

        results: list[RetrievalResult] = []

        for chunk in self._chunks:
            content_words = set(chunk.content.lower().split())

            overlap = query_words.intersection(content_words)

            if overlap:
                score = len(overlap) / len(query_words)

                results.append(
                    RetrievalResult(
                        chunk=chunk,
                        score=score,
                    )
                )

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:top_k]
