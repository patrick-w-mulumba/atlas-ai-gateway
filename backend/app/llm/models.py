from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(
        description="Message role such as system, user, or assistant",
    )
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
