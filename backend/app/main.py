from fastapi import FastAPI

app = FastAPI(
    title="Atlas AI Gateway",
    description="Production-oriented enterprise AI platform",
    version="0.1.0",
)

@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}
