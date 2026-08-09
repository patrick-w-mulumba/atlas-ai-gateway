from app.core.config import get_settings
from app.llm.provider import LLMProvider
from app.llm.providers.azure_openai import AzureOpenAIProvider
from app.llm.providers.mock import MockLLMProvider


def create_llm_provider() -> LLMProvider:
    settings = get_settings()

    if settings.llm_provider == "azure-openai":
        return AzureOpenAIProvider()

    if settings.llm_provider == "mock":
        return MockLLMProvider()

    raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
