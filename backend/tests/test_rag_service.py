import pytest
from app.llm.models import ChatResponse
from app.rag.models import DocumentChunk, RetrievalResult
from app.rag.service import RAGService


class FakeEmbeddingProvider:
    async def embed(
        self,
        text: str,
    ) -> list[float]:
        return [0.1] * 1536


class FakeRetriever:
    async def retrieve(
        self,
        embedding: list[float],
        top_k: int = 5,
        filters: dict[str, str] | None = None,
    ) -> list[RetrievalResult]:

        return [
            RetrievalResult(
                chunk=DocumentChunk(
                    id="chunk-1",
                    document_id="doc-1",
                    content="Python is a programming language.",
                    filename="test.txt",
                ),
                score=0.95,
            )
        ]


class FakeLLMService:
    async def chat(
        self,
        request,
    ) -> ChatResponse:

        return ChatResponse(
            content="Python is a programming language.",
            model="mock-model",
            provider="mock",
        )


@pytest.mark.asyncio
async def test_rag_service_builds_grounded_response() -> None:

    service = RAGService(
        embedding_provider=FakeEmbeddingProvider(),
        retriever=FakeRetriever(),
        llm_service=FakeLLMService(),
    )

    response = await service.answer(
        question="What is Python?",
        top_k=3,
    )

    assert response.answer == "Python is a programming language."

    assert len(response.sources) == 1
    assert response.sources[0].score == 0.95
