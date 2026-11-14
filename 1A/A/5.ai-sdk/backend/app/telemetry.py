"""OpenTelemetry: one global TracerProvider + MeterProvider for every framework.

Who emits what (docs/design/05-evals-and-otel.md):
  FastAPI         opentelemetry-instrumentation-fastapi (HTTP server spans)
  RunService      `agent.run` span + agent.runs / agent.run.duration metrics (ours)
  ADK, Strands    native GenAI spans via the *global* provider; nothing to configure
  LangGraph       OpenInference LangChain instrumentor
  Messages API    OpenInference Anthropic instrumentor
  Claude SDK      the CLI subprocess exports itself; we pass OTEL_* env (adapters/claude)

OTEL_EXPORTER: none | console | otlp | gcp.
"""

import logging

from opentelemetry import metrics, trace
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from app.config import Settings

log = logging.getLogger(__name__)
_configured = False

tracer = trace.get_tracer("ai-sdk")
meter = metrics.get_meter("ai-sdk")
runs_counter = meter.create_counter("agent.runs", description="Agent runs by target and outcome")
run_duration = meter.create_histogram("agent.run.duration", unit="s", description="Run wall time")


def setup_telemetry(settings: Settings) -> None:
    """Idempotent. Call once at startup, before any framework creates spans."""
    global _configured
    if _configured or settings.otel_exporter == "none":
        return
    _configured = True
    resource = Resource.create(
        {"service.name": settings.otel_service_name, "service.namespace": settings.app_name}
    )
    tp = TracerProvider(resource=resource)
    readers = []
    if settings.otel_exporter == "console":
        tp.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
        readers.append(PeriodicExportingMetricReader(ConsoleMetricExporter(), 60_000))
    elif settings.otel_exporter == "otlp":
        from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

        base = settings.otel_exporter_otlp_endpoint.rstrip("/")
        tp.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=f"{base}/v1/traces")))
        readers.append(
            PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=f"{base}/v1/metrics"))
        )
    elif settings.otel_exporter == "gcp":
        from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter

        tp.add_span_processor(
            BatchSpanProcessor(CloudTraceSpanExporter(project_id=settings.google_cloud_project))
        )
    trace.set_tracer_provider(tp)
    metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=readers))
    _instrument_libraries()
    log.info("OpenTelemetry exporter: %s", settings.otel_exporter)


def _instrument_libraries() -> None:
    for module, cls in (
        ("openinference.instrumentation.langchain", "LangChainInstrumentor"),
        ("openinference.instrumentation.anthropic", "AnthropicInstrumentor"),
    ):
        try:
            mod = __import__(module, fromlist=[cls])
            getattr(mod, cls)().instrument()
        except Exception as e:  # an instrumentor failing must never take the API down
            log.warning("could not instrument %s: %s", module, e)


def instrument_app(app, settings: Settings) -> None:
    if settings.otel_exporter == "none":
        return
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

    FastAPIInstrumentor.instrument_app(app, excluded_urls="healthz")


def claude_cli_otel_env(settings: Settings, session_id: str, user_id: str) -> dict[str, str]:
    """Env for the Claude Code CLI so its own telemetry lands in the same backend.

    Correlate with our spans by the `session.id` resource attribute.
    """
    if settings.otel_exporter != "otlp":
        return {}
    return {
        "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
        "OTEL_METRICS_EXPORTER": "otlp",
        "OTEL_LOGS_EXPORTER": "otlp",
        "OTEL_EXPORTER_OTLP_PROTOCOL": "http/protobuf",
        "OTEL_EXPORTER_OTLP_ENDPOINT": settings.otel_exporter_otlp_endpoint,
        "OTEL_SERVICE_NAME": f"{settings.otel_service_name}-claude-cli",
        "OTEL_RESOURCE_ATTRIBUTES": f"session.id={session_id},enduser.id={user_id}",
    }
