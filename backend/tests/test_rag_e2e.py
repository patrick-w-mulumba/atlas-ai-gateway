import pytest

from uuid import uuid4

from app.ingestion.chunker import Chunker
from app.ingestion.service import IngestionService
from app.ingestion.loader import DocumentLoader
from app.ingestion.simple_chunker import SimpleChunker
from app.ingestion.text_loader import TextLoader
from app.llm.models import ChatResponse
from app.models.tenant import Tenant
from app.rag.providers.pgvector import PgVectorRetriever
from app.rag.service import RAGService
from httpx._decoders import TextChunker


class TestEmbeddingProvider:
    async def embed(self, text: str) -> list[float]:

        if "refund" in text.lower():
            return [1.0, 0.0, 0.0] + [0.0] * 1533

        return [0.0, 1.0, 0.0] + [0.0] * 1533


class TestLLMService:
    async def chat(self, request):
        return ChatResponse(
            content="Customers can request a refund within 30 days of purchase.",
            model="test-model",
            provider="test",
        )


class TestDocumentLoader(DocumentLoader):
    async def load(self, content:bytes) -> str:
        return content.decode("utf-8")


class TestChunker(Chunker):
    def chunk(self, text: str) -> list[str]:
        return [text]


@pytest.mark.asyncio
async def test_rag_end_to_end(db_session, tenant) -> None:

    embedding_provider = TestEmbeddingProvider()

    ingestion_service = IngestionService(
        loader=TextLoader(),
        chunker=SimpleChunker(
            chunk_size=200,
            overlap=20,
        ),
        embedding_provider=embedding_provider,
    )

    document = await ingestion_service.ingest(
        session=db_session,
        tenant_id=tenant.id,
        filename="refund_policy.txt",
        content_type="text/plain",
        content=(b"Customers may request a refund within 30 days of purchase."),
    )

    retriever = PgVectorRetriever(
        session=db_session,
    )

    rag_service = RAGService(
        embedding_provider=embedding_provider,
        retriever=retriever,
        llm_service=TestLLMService(),
    )

    response = await rag_service.answer(
        question="How long do I have to request a refund?",
        tenant_id=tenant.id,
        top_k=3,
    )

    assert "30 days" in response.answer

    assert len(response.sources) >= 1
    assert response.sources[0].document_id == str(document.id)

    assert response.sources[0].score > 0.9
    assert "refund" in response.sources[0].content.lower()

    assert response.sources[0].filename == "refund_policy.txt"


@pytest.mark.asyncio
async def test_rag_service_rejects_irrelevant_context(db_session, tenant) -> None:

    embedding_provider = TestEmbeddingProvider()

    ingestion_service = IngestionService(
        loader=TextLoader(),
        chunker=SimpleChunker(
            chunk_size=200,
            overlap=20,
        ),
        embedding_provider=embedding_provider,
    )

    await ingestion_service.ingest(
        session=db_session,
        tenant_id=tenant.id,
        filename="refund_policy.txt",
        content_type="text/plain",
        content=b"Customers may request a refund within 30 days of purchase.",
    )

    retriever = PgVectorRetriever(session=db_session)

    rag_service = RAGService(
        embedding_provider=embedding_provider,
        retriever=retriever,
        llm_service=TestLLMService(),
        min_relevance_score=0.7,
    )

    response = await rag_service.answer(
        question="What is our parental leave policy?",
        tenant_id=tenant.id,
        top_k=3,
    )

    assert response.sources == []
    assert "dont have enough information" in response.answer

@pytest.mark.asyncio
async def test_rag_end_to_end_enforces_tenant_isolation(db_session, tenant) -> None:
    tenant_a = tenant
    tenant_b = Tenant(
        name="Tenant B",
        slug=f"tenant-b-{uuid4().hex}",
    )

    db_session.add(tenant_b)
    await db_session.flush()

    ingestion_service = IngestionService(
        loader=TestDocumentLoader(),
        chunker=TestChunker(),
        embedding_provider=TestEmbeddingProvider(),
    )

    document_a = await ingestion_service.ingest(
        session=db_session,
        tenant_id=tenant_a.id,
        filename="tenant_a_refund_policy.txt",
        content_type="text/plain",
        content=b"Customers may request a refund within 30 days of purchase.",
    )

    document_b = await ingestion_service.ingest(
        session=db_session,
        tenant_id=tenant_b.id,
        filename="tenant_b_refund_policy.txt",
        content_type="text/plain",
        content=b"Customers may request a refund within 90 days of purchase.",
    )