import pytest
from app.llm.models import ChatMessage, ChatRequest
from app.llm.providers.mock import MockLLMProvider
from app.llm.service import LLMService


@pytest.mark.asyncio
async def test_llm_service_uses_provider() -> None:
    service = LLMService(
        provider=MockLLMProvider(),
    )

    request = ChatRequest(
        messages=[
            ChatMessage(
                role="user",
                content="Hello Atlas",
            ),
        ],
    )

    response = await service.chat(request)

    assert response.provider == "mock"
    assert response.model == "mock-model"
    assert response.content == "Mock response to: Hello Atlas"
