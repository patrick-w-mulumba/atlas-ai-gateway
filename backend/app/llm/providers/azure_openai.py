import logging

from openai import (
    APIConnectionError,
    APITimeoutError,
    AsyncAzureOpenAI,
    InternalServerError,
    RateLimitError,
)
from openai.types.chat import ChatCompletion
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.core.exceptions import LLMServiceError
from app.llm.models import ChatRequest, ChatResponse
from app.llm.provider import LLMProvider

logger = logging.getLogger(__name__)


_llm_retry = retry(
    retry=retry_if_exception_type(
        (
            APITimeoutError,
            APIConnectionError,
            RateLimitError,
            InternalServerError,
        )
    ),
    wait=wait_exponential(
        multiplier=0.5,
        min=0.5,
        max=4,
    ),
    stop=stop_after_attempt(3),
    reraise=True,
)


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
            timeout=settings.azure_openai_timeout,
        )

    @_llm_retry
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
        try:
            response = await self._request(request)
        except (
            APITimeoutError,
            APIConnectionError,
            InternalServerError,
            RateLimitError,
            logger.error("LLM request failed after retries"),
        ) as exc:
            raise LLMServiceError(
                "The LLM provider is currently unavailable."
            ) from exc  # This preserves the original exception for logging/debugging
            # but app sees message above
            logger.error("LLM request failed after retries")

        content = response.choices[0].message.content or ""

        return ChatResponse(
            content=content,
            model=response.model,
            provider="azure-openai",
        )
