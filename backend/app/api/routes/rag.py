from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_principal, get_rag_service
from app.rag.models import ErrorResponse, RAGRequest, RAGResponse
from app.rag.service import RAGService
from app.security.principal import Principal

router = APIRouter(
    prefix="/rag",
    tags=["rag"],
)


@router.post(
    "/query",
    response_model=RAGResponse,
    status_code=200,
    summary="Query the knowledge base",
    description=(
        "Retrieve relevant knowledge-base content "
        "and generate an answer grounded in the retrieved context"
    ),
    responses={
        503: {
            "model": ErrorResponse,
            "description": "The AI service is temporarily unavailable.",
        },
    },
)
async def query(
    request: RAGRequest,
    rag_service: Annotated[RAGService, Depends(get_rag_service)],
    principal: Annotated[Principal, Depends(get_current_principal)],
) -> RAGResponse:
    return await rag_service.answer(
        question=request.question,
        tenant_id=principal.tenant_id,
        top_k=request.top_k,
        filters=request.filters,
    )
