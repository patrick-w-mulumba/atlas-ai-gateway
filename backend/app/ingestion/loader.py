from abc import ABC, abstractmethod


class DocumentLoader(ABC):
    @abstractmethod
    async def load(
        self,
        content: bytes,
    ) -> str:
        raise NotImplementedError
