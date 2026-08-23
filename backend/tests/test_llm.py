import pytest
from app.llm.models import ChatMessage, ChatMessageRole, ChatRequest
from app.llm.providers.mock import MockLLMProvider
from app.llm.service import LLMService
from pydantic import ValidationError


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


def test_chat_request_rejects_zero_max_tokens() -> None:
    with pytest.raises(ValidationError):
        ChatRequest(
            messages=[
                ChatMessage(
                    role=ChatMessageRole.USER,
                    content="Hello Atlas",
                )
            ],
            max_tokens=0,
        )


def test_chat_request_rejects_max_tokens_above_limit() -> None:
    with pytest.raises(ValidationError):
        ChatRequest(
            messages=[
                ChatMessage(
                    role=ChatMessageRole.USER,
                    content="Hello Atlas",
                )
            ],
            max_tokens=4097,
        )


def test_chat_request_accpets_max_tokens_limit() -> None:
    with pytest.raises(ValidationError):
        ChatRequest(
            messages=[
                ChatMessage(
                    role=ChatMessageRole.USER,
                    content="Hello Atlas",
                )
            ],
            max_tokens=4097,
        )
