from abc import ABC, abstractmethod

from app.llm.models import ChatRequest, ChatResponse


class LLMProvider(ABC):
    """Interface implemented by all LLM providers."""

    @abstractmethod
    async def chat(
        self,
        request: ChatRequest,
    ) -> ChatResponse:
        """Generate a response from the LLM."""
        raise NotImplementedError
