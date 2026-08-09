from collections.abc import AsyncGenerator

import pytest_asyncio
from app.core.config import get_settings
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    settings = get_settings()

    engine = create_async_engine(
        settings.database_url,
    )

    async with engine.connect() as connection:
        transaction = await connection.begin()

        session = AsyncSession(
            bind=connection,
            join_transaction_mode="create_savepoint",
            expire_on_commit=False,
        )

        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()

    await engine.dispose()
