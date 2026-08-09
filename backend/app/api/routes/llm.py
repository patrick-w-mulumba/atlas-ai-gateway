from fastapi import APIRouter

from app.llm.factory import create_llm_provider
from app.llm.models import ChatRequest, ChatResponse
from app.llm.service import LLMService

router = APIRouter(
    prefix="/llm",
    tags=["LLM"],
)


llm_service = LLMService(
    provider=create_llm_provider(),
)


@router.post(
    "/chat",
    response_model=ChatResponse,
)
async def chat(request: ChatRequest) -> ChatResponse:
    return await llm_service.chat(request)
