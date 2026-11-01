from abc import ABC, abstractmethod
from uuid import UUID

from app.rag.models import RetrievalResult


class Retriever(ABC):
    @abstractmethod
    async def retrieve(
        self,
        embedding: list[float],
        tenant_id: UUID,
        top_k: int = 5,
        filters: dict[str, str] | None = None,
    ) -> list[RetrievalResult]:
        raise NotImplementedError
