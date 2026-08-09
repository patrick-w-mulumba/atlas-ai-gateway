from enum import StrEnum

from pydantic import BaseModel, Field


class ChatMessageRole(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    DEVELOPER = "developer"


class ChatMessage(BaseModel):
    role: str = ChatMessageRole
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]

    model: str | None = None

    temperature: float = Field(
        default=0.2,
        ge=0.0,
        le=2.0,
    )

    max_tokens: int | None = Field(
        default=None,
        gt=0,
    )


class ChatResponse(BaseModel):
    content: str
    model: str
    provider: str
