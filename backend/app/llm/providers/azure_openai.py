from openai import AsyncAzureOpenAI
from openai.types.chat import ChatCompletion
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.llm.models import ChatRequest, ChatResponse
from app.llm.provider import LLMProvider


class AzureOpenAIProvider(LLMProvider):
    def __init__(self) -> None:
        settings = get_settings()

        if not settings.azure_openai_endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT is not configured")

        if not settings.azure_openai_api_key:
            raise ValueError("AZURE_OPENAI_API_KEY is not configured")

        self._model = settings.llm_model

        self._client = AsyncAzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
        )

    @retry(
        retry=retry_if_exception_type(Exception),
        wait=wait_exponential(
            multiplier=1,
            min=1,
            max=8,
        ),
        stop=stop_after_attempt(3),
    )
    async def _request(
        self,
        request: ChatRequest,
    ) -> ChatCompletion:
        return await self._client.chat.completions.create(
            model=request.model or self._model,
            messages=[
                {
                    "role": message.role.value,
                    "content": message.content,
                }
                for message in request.messages
            ],
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

    async def chat(
        self,
        request: ChatRequest,
    ) -> ChatResponse:
        response = await self._request(request)

        content = response.choices[0].message.content or ""

        return ChatResponse(
            content=content,
            model=response.model,
            provider="azure-openai",
        )
