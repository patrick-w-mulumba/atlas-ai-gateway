from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from redis.asyncio import Redis
from sqlalchemy import text

from app.api.routes.llm import router as llm_router
from app.api.routes.rag import router as rag_retriever
from app.core.config import get_settings
from app.core.exceptions import LLMServiceError, llm_service_error_handler
from app.core.logging import configure_logging
from app.db.database import AsyncSessionLocal, engine
from app.observability.tracing import configure_tracing

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    tracer_provider = configure_tracing()
    try:
        yield
    finally:
        if tracer_provider is not None:
            tracer_provider.shutdown()

        await engine.dispose()


app = FastAPI(
    title="Atlas AI Gateway",
    description="Production-oriented enterprise AI platform",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_exception_handler(LLMServiceError, llm_service_error_handler)

configure_tracing()

FastAPIInstrumentor.instrument_app(app)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/readiness")
async def readiness_check() -> dict[str, str]:
    settings = get_settings()
    database_status = "ok"
    redis_status = "ok"

    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
    except Exception:
        database_status = "unavailable"

    try:
        redis = Redis.from_url(settings.redis_url, decode_responses=True)
        await redis.ping()
        await redis.aclose()

    except Exception:
        redis_status = "unavailable"

    if (database_status != "ok") or (redis_status != "ok"):
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "database": database_status,
                "redis": redis_status,
            },
        )

    return {
        "status": "ready",
        "database": database_status,
        "redis": redis_status,
    }


app.include_router(llm_router)
app.include_router(rag_retriever)
