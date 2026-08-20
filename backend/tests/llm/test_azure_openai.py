from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.llm.providers.azure_openai import AzureOpenAIProvider
from openai import APIConnectionError
from tenacity import wait_none


@pytest.fixture
def provider() -> AzureOpenAIProvider:
    with patch("app.llm.providers.azure_openai.get_settings") as mock_settings:
        mock_settings.return_value.azure_openai_endpoint = "https://test.openai.azure.com"
        mock_settings.return_value.azure_openai_api_key = "test-key"
        mock_settings.return_value.azure_openai_api_version = "2024-10-21"
        mock_settings.return_value.llm_model = "test-model"

        return AzureOpenAIProvider()


@pytest.mark.asyncio
async def test_chat_returns_chat_response(provider: AzureOpenAIProvider) -> None:
    client = MagicMock()

    completion = MagicMock()
    completion.model = "test-model"
    completion.choices[0].message.content = "Hello from the test"

    client.chat.completions.create = AsyncMock(return_value=completion)

    provider._client = client

    request = MagicMock()
    request.model = None
    request.messages = []
    request.temperature = 0.2
    request.max_tokens = 100

    response = await provider.chat(request)

    assert response.content == "Hello from the test"
    assert response.model == "test-model"
    assert response.provider == "azure-openai"

    client.chat.completions.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_request_retries_connection_error(provider: AzureOpenAIProvider) -> None:
    client = MagicMock()

    completion = MagicMock()
    completion.model = "test-model"

    client.chat.completions.create = AsyncMock(
        side_effect=[
            APIConnectionError(
                message="temporary connection failure",
                request=MagicMock(),
            ),
            APIConnectionError(
                message="temporary connection failure",
                request=MagicMock(),
            ),
            completion,
        ],
    )

    provider._client = client

    request = MagicMock()
    request.model = None
    request.messages = []
    request.temperature = 0.2
    request.max_tokens = 100

    response = await provider._request.retry_with(
        wait=wait_none(),
    )(provider, request)

    assert response is completion
    assert client.chat.completions.create.await_count == 3


@pytest.mark.asyncio
async def test_request_does_not_retry_non_retryable_error(provider: AzureOpenAIProvider) -> None:
    client = MagicMock()

    client.chat.completions.create = AsyncMock(
        side_effect=ValueError("invalid request"),
    )

    provider._client = client

    request = MagicMock()
    request.model = None
    request.messages = []
    request.temperature = 0.2
    request.max_tokens = 100

    with pytest.raises(ValueError):
        await provider._request.retry_with(
            wait=wait_none(),
        )(provider, request)

    assert client.chat.completions.create.await_count == 1


async def test_provider_configures_client_timeout() -> None:
    with patch("app.llm.providers.azure_openai.get_settings") as mock_get_settings:
        mock_settings = MagicMock()

        mock_settings.azure_openai_endpoint = "https://test.openai.com"
        mock_settings.azure_openai_api_key = "test-key"
        mock_settings.azure_openai_api_version = "2024-10-21"
        mock_settings.llm_model = "test-model"
        mock_settings.azure_openai_timeout = 30.0

        mock_get_settings.return_value = mock_settings

        with patch("app.llm.providers.azure_openai.AsyncAzureOpenAI") as mock_client:
            AzureOpenAIProvider()

            mock_client.assert_called_once_with(
                azure_endpoint="https://test.openai.com",
                api_key="test-key",
                api_version="2024-10-21",
                timeout=30.0,
            )
