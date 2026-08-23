from fastapi import Request
from fastapi.responses import JSONResponse


class AtlasError(Exception):
    """Base exception for application-level errors."""


class LLMServiceError(Exception):
    """Raised when the LLM Provider cannot complete a request."""


async def llm_service_error_handler(request: Request, exc: LLMServiceError) -> JSONResponse:
    return JSONResponse(
        status_code=503, content={"detail": "The AI Service is temporarily unavailable."}
    )
