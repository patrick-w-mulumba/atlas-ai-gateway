from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.core.config import get_settings


def create_tracer_provider(
    endpoint: str,
) -> TracerProvider:
    resource = Resource.create(
        {
            "service.name": "atlas",
        }
    )

    provider = TracerProvider(resource=resource)

    exporter = OTLPSpanExporter(endpoint=endpoint)

    provider.add_span_processor(BatchSpanProcessor(exporter))

    return provider


tracer = trace.get_tracer("atlas")


def configure_tracing() -> None:
    settings = get_settings()

    if not settings.otel_enabled:
        return

    provider = create_tracer_provider(
        endpoint=settings.otel_endpoint,
    )

    trace.set_tracer_provider(provider)
