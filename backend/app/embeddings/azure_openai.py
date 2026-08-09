from openai import AsyncAzureOpenAI

from app.core.config import get_settings
from app.embeddings.provider import EmbeddingProvider


class AzureOpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self) -> None:
        settings = get_settings()

        if not settings.azure_openai_endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT is not configured")

        if not settings.azure_openai_api_key:
            raise ValueError("AZURE_OPENAI_API_KEY is not configured")

        self._model = settings.embedding_model
        self._dimensions = settings.embedding_dimensions

        self._client = AsyncAzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            timeout=30.0,
        )

    async def embed(
        self,
        text: str,
    ) -> list[float]:

        response = await self._client.embeddings.create(
            model=self._model,
            input=text,
            dimensions=self._dimensions,
        )

        return response.data[0].embedding
