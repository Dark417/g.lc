"""Metric model and the MetricsSink port. No SDK imports."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Protocol


@dataclass(frozen=True)
class MetricPoint:
    name: str
    value: float
    unit: str = "None"  # CloudWatch units: Count, Milliseconds, Seconds, Bytes, None, ...
    # Dimensions multiply the number of metrics (each distinct combination is billed as its own metric):
    # use LOW-cardinality values only (model_id, slice). Never user_id, request_id or prompt text.
    dimensions: dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


class MetricsSink(Protocol):
    """Port: where metric points go. Adapters: CloudWatchSink (API), EmfSink (log lines)."""

    def put(self, points: list[MetricPoint]) -> None: ...

    def flush(self) -> None: ...


@dataclass
class CallRecord:
    """What one instrumented Converse call produced."""

    text: str
    stop_reason: str
    input_tokens: int
    output_tokens: int
    latency_ms: float  # model-reported (metrics.latencyMs)
    wall_ms: float  # measured by us, includes network + retries


@dataclass
class UsagePoint:
    timestamp: datetime
    input_tokens: float
    output_tokens: float
