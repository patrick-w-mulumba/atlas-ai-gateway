from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.embeddings.factory import create_embedding_provider
from app.embeddings.provider import EmbeddingProvider
from app.llm.factory import create_llm_provider
from app.llm.service import LLMService
from app.rag.providers.pgvector import PgVectorRetriever
from app.rag.retriever import Retriever
from app.rag.service import RAGService

DBSession = Annotated[
    AsyncSession,
    Depends(get_db),
]


def get_embedding_provider() -> EmbeddingProvider:
    return create_embedding_provider()


def get_llm_service() -> LLMService:
    return LLMService(
        provider=create_llm_provider(),
    )


async def get_retriever(
    db: DBSession,
) -> Retriever:
    return PgVectorRetriever(
        session=db,
    )


EmbeddingProviderDependency = Annotated[
    EmbeddingProvider,
    Depends(get_embedding_provider),
]


RetrieverDependency = Annotated[
    Retriever,
    Depends(get_retriever),
]


LLMServiceDependency = Annotated[
    LLMService,
    Depends(get_llm_service),
]


def get_rag_service(
    embedding_provider: EmbeddingProviderDependency,
    retriever: RetrieverDependency,
    llm_service: LLMServiceDependency,
) -> RAGService:
    return RAGService(
        embedding_provider=embedding_provider,
        retriever=retriever,
        llm_service=llm_service,
    )


RAGServiceDependency = Annotated[
    RAGService,
    Depends(get_rag_service),
]
