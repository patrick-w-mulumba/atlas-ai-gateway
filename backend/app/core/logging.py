import logging

from opentelemetry import trace


class OpenTelemetryLoggingFilter(logging.Filter):
    """Add Opentelemetry trace context to log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        span = trace.get_current_span()
        context = span.get_span_context()

        if context.is_valid:
            record.trace_id = format(context.trace_id, "032x")
            record.span_id = format(context.span_id, "016x")
        else:
            record.trace_id = "-"
            record.span_id = "-"

        return True


def configure_logging() -> None:
    handler = logging.StreamHandler()

    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s "
            "trace_id=%(trace_id)s span_id=%(span_id)s %(message)s"
        )
    )

    handler.addFilter(OpenTelemetryLoggingFilter())

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    # logging.getLogger().addFilter(OpenTelemetryLoggingFilter())


def get_trace_context() -> dict[str, str]:
    span = trace.get_current_span()
    context = span.get_span_context()

    if not context.is_valid:
        return {}

    return {
        "trace_id": format(context.trace_id, "032x"),
        "span_id": format(context.span_id, "016x"),
    }
