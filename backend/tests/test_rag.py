import pytest
from app.main import app
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_rag_query_returns_successful_response() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "rag/query",
            json={
                "question": "What is your refund policy?",
                "top_k": 5,
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert "sources" in body
        assert "answer" in body


@pytest.mark.asyncio
async def test_rag_query_rejects_empty_question() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "rag/query",
            json={
                "question": "",
                "top_k": 5,
            },
        )

        assert response.status_code == 422


@pytest.mark.asyncio
async def test_rag_query_validates_whitespace_question() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "rag/query",
            json={
                "question": "       ",
                "top_k": 5,
            },
        )

        assert response.status_code == 422
        assert response.json()["detail"][0]["msg"] == "Value error, question cannot be empty"


@pytest.mark.asyncio
async def test_rag_query_rejects_invalid_top_k() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "rag/query",
            json={
                "question": "What is your refund policy?",
                "top_k": 0,
            },
        )

        assert response.status_code == 422
