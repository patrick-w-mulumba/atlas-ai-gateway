import json
from unittest.mock import AsyncMock, patch

import pytest
from app.core.exceptions import LLMServiceError, llm_service_error_handler
from app.main import app
from fastapi import Request
from httpx import ASGITransport, AsyncClient


async def test_llm_service_error_returns_503() -> None:
    request = Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/rag/query",
            "headers": [],
        }
    )

    response = await llm_service_error_handler(
        request,
        LLMServiceError("provider unavailable"),
    )

    assert response.status_code == 503
    assert response.body == (
        b'{"error":{"code":"LLM_SERVICE_UNAVAILABLE",'
        b'"message":"The AI service is temporarily unavailable."}}'
    )


@pytest.mark.asyncio
async def test_llm_service_error_is_handled_by_fastapi() -> None:
    with patch(
        "app.rag.service.RAGService.answer",
        new=AsyncMock(side_effect=LLMServiceError("The LLM Provider is unavailable")),
    ):
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as client:
            response = await client.post(
                "/rag/query",
                json={
                    "question": "What is the refund policy?",
                    "top_k": 5,
                },
            )

        assert response.status_code == 503
        assert response.json() == {
            'error': {'code': 'LLM_SERVICE_UNAVAILABLE', 'message': 'The AI service is temporarily unavailable.'}}
