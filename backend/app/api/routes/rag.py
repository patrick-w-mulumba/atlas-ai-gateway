from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_rag_service
from app.rag.models import RAGRequest, RAGResponse
from app.rag.service import RAGService

router = APIRouter(
    prefix="/rag",
    tags=["rag"],
)


@router.post("/query", response_model=RAGResponse)
async def query(
    request: RAGRequest,
    rag_service: Annotated[RAGService, Depends(get_rag_service)],
) -> RAGResponse:
    return await rag_service.answer(
        question=request.question,
        top_k=request.top_k,
    )
