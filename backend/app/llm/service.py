from app.llm.models import ChatRequest, ChatResponse
from app.llm.provider import LLMProvider


class LLMService:
    def __init__(self, provider: LLMProvider) -> None:
        self._provider = provider

    async def chat(
        self,
        request: ChatRequest,
    ) -> ChatResponse:
        return await self._provider.chat(request)
