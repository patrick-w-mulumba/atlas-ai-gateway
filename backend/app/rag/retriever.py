from abc import ABC, abstractmethod

from app.rag.models import RetrievalResult


class Retriever(ABC):
    @abstractmethod
    async def retrieve(
        self,
        embedding: list[float],
        top_k: int = 5,
    ) -> list[RetrievalResult]:
        raise NotImplementedError
