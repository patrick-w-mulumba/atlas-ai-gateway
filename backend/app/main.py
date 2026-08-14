from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from app.api.routes.llm import router as llm_router
from app.api.routes.rag import router as rag_retriever
from app.observability.tracing import configure_tracing

app = FastAPI(
    title="Atlas AI Gateway",
    description="Production-oriented enterprise AI platform",
    version="0.1.0",
)

configure_tracing()

FastAPIInstrumentor.instrument_app(app)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}


app.include_router(llm_router)
app.include_router(rag_retriever)
