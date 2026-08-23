import logging

from app.core.logging import OpenTelemetryLoggingFilter, configure_logging
from opentelemetry.sdk.trace import TracerProvider


def test_logging_filter_add_trace_context(caplog) -> None:
    logger = logging.getLogger("test")

    logger.addFilter(OpenTelemetryLoggingFilter())

    with caplog.at_level(logging.INFO):
        logger.info("test message")

    record = caplog.records[0]

    assert hasattr(record, "trace_id")
    assert hasattr(record, "span_id")


def test_logging_filter_without_active_span(caplog) -> None:
    logger = logging.getLogger("test")

    logger.addFilter(OpenTelemetryLoggingFilter())

    with caplog.at_level(logging.INFO):
        logger.info("test message")

    record = caplog.records[0]

    assert record.trace_id == "-"
    assert record.span_id == "-"


def test_logging_filter_with_active_span(caplog) -> None:
    logger = logging.getLogger("test")

    logger.addFilter(OpenTelemetryLoggingFilter())

    provider = TracerProvider()
    tracer = provider.get_tracer("test")

    with tracer.start_as_current_span("test_span"):
        with caplog.at_level(logging.INFO):
            logger.info("test message")

    record = caplog.records[0]

    assert record.trace_id != "-"
    assert record.span_id != "-"


def test_logging_inside_span_has_matching_trace_if(caplog) -> None:
    logger = logging.getLogger("test")

    logger.addFilter(OpenTelemetryLoggingFilter())

    provider = TracerProvider()
    tracer = provider.get_tracer("test")

    with tracer.start_as_current_span("rag.retrieval") as span:
        expected_trace_id = format(
            span.get_span_context().trace_id,
            "032x",
        )

        with caplog.at_level(logging.INFO):
            logger.info("RAG retrieval message")

    record = caplog.records[0]

    assert record.trace_id == expected_trace_id
    assert record.span_id != "-"


def test_configure_logging_add_trace_filer() -> None:
    configure_logging()

    root_logger = logging.getLogger()

    assert root_logger.handlers

    handler = root_logger.handlers[0]

    assert any(isinstance(log_filter, OpenTelemetryLoggingFilter) for log_filter in handler.filters)
