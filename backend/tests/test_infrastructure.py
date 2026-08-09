import pytest
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


@pytest.mark.asyncio
async def test_postgres_connection() -> None:
    engine = create_async_engine(
        "postgresql+asyncpg://atlas:atlas_dev_password@localhost:5432/atlas"
    )

    async with engine.connect() as connection:
        result = await connection.execute(text("SELECT 1"))

    assert result.scalar() == 1

    await engine.dispose()


@pytest.mark.asyncio
async def test_redis_connection() -> None:
    redis = Redis.from_url(
        "redis://localhost:6379/0",
        decode_responses=True,
    )

    result = await redis.ping()

    assert result is True

    await redis.aclose()
