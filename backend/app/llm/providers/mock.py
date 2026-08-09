from app.llm.models import ChatRequest, ChatResponse
from app.llm.provider import LLMProvider


class MockLLMProvider(LLMProvider):
    """Deterministic provider used for local development and testing."""

    async def chat(
        self,
        request: ChatRequest,
    ) -> ChatResponse:
        last_message = request.messages[-1]

        return ChatResponse(
            content=f"Mock response to: {last_message.content}",
            model=request.model or "mock-model",
            provider="mock",
        )
