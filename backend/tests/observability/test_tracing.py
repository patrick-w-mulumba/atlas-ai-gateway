from unittest.mock import MagicMock, patch

from app.observability.tracing import configure_tracing, create_tracer_provider
from opentelemetry.trace import TracerProvider


def test_create_tracer_provider() -> None:
    provider = create_tracer_provider(
        endpoint="http://localhost:4318/v1/traces",
    )

    assert isinstance(provider, TracerProvider)

    assert len(provider._active_span_processor._span_processors) > 0


def test_configure_tracing_disabled() -> None:
    with patch("app.observability.tracing.get_settings") as mock_settings:
        mock_settings.return_value.otel_enabled = False

        result = configure_tracing()

    assert result is None


def test_configure_tracing_enabled() -> None:
    mock_provider = MagicMock()

    with patch("app.observability.tracing.get_settings") as mock_settings:
        mock_settings.return_value.otel_enabled = True
        mock_settings.return_value.otel_endpoint = "http://localhost:4318/v1/traces"

        with patch(
            "app.observability.tracing.create_tracer_provider",
            return_value=mock_provider,
        ) as mock_create:
            with patch("app.observability.tracing.trace.set_tracer_provider") as mock_set_provider:
                configure_tracing()

                mock_create.assert_called_once_with(endpoint="http://localhost:4318/v1/traces")

                mock_set_provider.assert_called_once_with(mock_provider)

                result = configure_tracing()

                assert result is mock_provider
