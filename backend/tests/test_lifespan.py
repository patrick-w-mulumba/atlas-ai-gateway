from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from app.main import app, lifespan


@pytest.mark.asyncio
async def test_lifespan_disposes_database_engine() -> None:
    mock_engine = AsyncMock()

    with patch("app.main.engine", mock_engine):
        async with lifespan(None):
            pass

    mock_engine.dispose.assert_awaited_once()


@pytest.mark.asyncio
async def test_lifespan_shuts_down_tracer_provider() -> None:
    tracer_provider = MagicMock()

    mock_engine = MagicMock()
    mock_engine.dispose = AsyncMock()

    with (
        patch("app.main.configure_tracing", return_value=tracer_provider),
        patch("app.main.engine", mock_engine),
    ):
        async with lifespan(app):
            pass

    tracer_provider.shutdown.assert_called_once()
    mock_engine.dispose.assert_awaited_once()
