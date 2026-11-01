import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_db
from app.embeddings.factory import create_embedding_provider
from app.embeddings.provider import EmbeddingProvider
from app.llm.factory import create_llm_provider
from app.llm.service import LLMService
from app.models.tenant import Tenant
from app.rag.providers.pgvector import PgVectorRetriever
from app.rag.retriever import Retriever
from app.rag.service import RAGService
from app.security.principal import Principal

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


async def get_current_principal(
    db: DBSession,
) -> Principal:

    settings = get_settings()

    # Temporary development-only principal.
    if settings.app_env != "development":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required.",
        )

    result = await db.execute(
        select(Tenant).where(
            Tenant.slug == "atlas-development",
            Tenant.is_active.is_(True),
        )
    )

    tenant = result.scalar_one_or_none()

    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Development tenant is unavailable.",
        )

    return Principal(
        subject_id=uuid.UUID("00000000-0000-4000-8000-000000000001"),
        tenant_id=tenant.id,
        roles=["admin"],
        permissions=["rag.query"],
        auth_type="development",
    )
