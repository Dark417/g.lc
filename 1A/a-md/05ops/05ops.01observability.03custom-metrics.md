# 05ops.01observability.03custom-metrics Custom Metrics and the Instrumented Call

> Add the dimensions Bedrock lacks through one wrapper, sent by Application Programming Interface (API) or by Embedded Metric Format (EMF) log line, with low cardinality.

## Index

- [1. Why Custom Metrics](#1-why-custom-metrics)
- [2. Metric Model and Sink Port](#2-metric-model-and-sink-port)
- [3. PutMetricData](#3-putmetricdata)
- [4. Embedded Metric Format](#4-embedded-metric-format)
- [5. Dimension Cardinality](#5-dimension-cardinality)
- [6. Instrumented Converse](#6-instrumented-converse)

Back to [00index](05ops.01observability.00index.md).

## 1. Why Custom Metrics

Bedrock metrics don't know your slice, tenant tier, `stopReason`, or business outcome.

- One wrapper for all model calls
  - consistent metrics and dimensions
- The sink is chosen from config: `cloudwatch` or `emf`

## 2. Metric Model and Sink Port

```python
# app/domain/_05ops_01observability.py
@dataclass(frozen=True)
class MetricPoint:
    name: str
    value: float
    unit: str = "None"  # CloudWatch units: Count, Milliseconds, Seconds, Bytes, None, ...
    # Each distinct dimension combination is billed as its own metric: LOW-cardinality values only.
    dimensions: dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


class MetricsSink(Protocol):
    """Port: where metric points go. Adapters: CloudWatchSink (API), EmfSink (log lines)."""

    def put(self, points: list[MetricPoint]) -> None: ...

    def flush(self) -> None: ...
```

## 3. PutMetricData

The API path: batch many points per call.

- Documented up to 1,000 metrics per call (check the quota page)
- Cost = per metric (distinct name + dimension set) per month + API calls
- Why batch
  - one call per metric is slow
  - and counts against the `PutMetricData` API rate limit

```python
# app/infra/_05ops_01observability.py
class CloudWatchSink:
    def __init__(self, namespace: str | None = None, max_per_call: int | None = None) -> None:
        cfg = get_observability_settings()
        self._namespace = namespace or cfg.namespace  # A/GenAI: IAM allows PutMetricData only here
        self._max = max_per_call or cfg.max_metrics_per_call
        self._buffer: list[MetricPoint] = []

    def put(self, points: list[MetricPoint]) -> None:
        self._buffer.extend(points)
        if len(self._buffer) >= self._max:
            self.flush()

    def flush(self) -> None:
        while self._buffer:
            batch, self._buffer = self._buffer[: self._max], self._buffer[self._max :]
            client("cloudwatch").put_metric_data(
                Namespace=self._namespace,
                MetricData=[_datum(p) for p in batch],  # StorageResolution 1 s costs more; default 60 s
            )
```

- Catch
  - A call fails as a whole on a bad datum
  - CloudWatch accepts at most 30 dimensions per metric

## 4. Embedded Metric Format

The log path: CloudWatch extracts metrics from a JavaScript Object Notation (JSON) log line.

- Write a JSON log line with an `_aws.CloudWatchMetrics` block
- No API call and no throttling from your code
- Good in Lambda and containers (awslogs / Firelens stdout)

```python
# app/infra/_05ops_01observability.py
def format_emf(points: list[MetricPoint], namespace: str | None = None) -> list[str]:
    ns = namespace or get_observability_settings().namespace
    grouped: dict[tuple[tuple[str, str], ...], list[MetricPoint]] = {}
    for p in points:  # one line per dimension set
        grouped.setdefault(tuple(sorted(p.dimensions.items())), []).append(p)
    lines: list[str] = []
    for dims, pts in grouped.items():
        doc: dict[str, Any] = {
            "_aws": {
                "Timestamp": int(max(p.timestamp for p in pts).timestamp() * 1000),
                "CloudWatchMetrics": [
                    {
                        "Namespace": ns,
                        "Dimensions": [[k for k, _ in dims]],
                        "Metrics": [{"Name": p.name, "Unit": p.unit} for p in pts],
                    }
                ],
            },
            **dict(dims),  # dimension values as top-level fields
            **{p.name: p.value for p in pts},  # metric values as top-level fields
        }
        lines.append(json.dumps(doc, separators=(",", ":")))
    return lines


class EmfSink:
    """Prints EMF lines to stdout (collected by the container log driver)."""

    def put(self, points: list[MetricPoint]) -> None:
        for line in format_emf(points):
            print(line, flush=True)
```

- Catch
  - Metrics appear only if the line reaches CloudWatch Logs
  - Keep each line under the log event size limit
  - Same cardinality cost as the API path

## 5. Dimension Cardinality

Each dimension combination is a billed metric.

- `model_id` × `slice` = small, fine
- `user_id`, `request_id`, prompt hash
  - metric explosion and a surprise bill
- High-cardinality questions belong in logs (Logs Insights), not metrics
  - see [02invocation-logging](05ops.01observability.02invocation-logging.md)
- Tenant tier (not tenant id) is acceptable as a dimension

## 6. Instrumented Converse

The single choke point for model calls.

→ Start a wall clock.  
→ Call Converse.  
→ On error: count `Errors` with `ErrorCode`, flush, re-raise.  
→ On success: record invocations, tokens, model latency, wall time, `StopReason`.

```python
# app/infra/_05ops_01observability.py
def instrumented_converse(prompt: str, sink: MetricsSink, model_id: str | None = None, max_tokens: int = 300) -> CallRecord:
    cfg = get_observability_settings()
    model_id = model_id or get_settings().fast_model_id
    dims = {"ModelId": model_id, "Slice": cfg.slice_name}
    t0 = time.perf_counter()
    try:
        resp = client("bedrock-runtime").converse(
            modelId=model_id,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": max_tokens, "temperature": 0.0},
        )
    except ClientError as e:
        sink.put([MetricPoint("Errors", 1, "Count", {**dims, "ErrorCode": e.response["Error"]["Code"]})])
        sink.flush()
        raise
    wall_ms = (time.perf_counter() - t0) * 1000  # includes network + retries
    usage = resp["usage"]  # inputTokens, outputTokens, totalTokens
    stop = resp["stopReason"]  # end_turn | max_tokens | stop_sequence | tool_use | guardrail_intervened | ...
    record = CallRecord(
        text=resp["output"]["message"]["content"][0]["text"],
        stop_reason=stop,
        input_tokens=usage["inputTokens"],
        output_tokens=usage["outputTokens"],
        latency_ms=float(resp["metrics"]["latencyMs"]),  # model-reported
        wall_ms=wall_ms,
    )
    sink.put(
        [
            MetricPoint("Invocations", 1, "Count", dims),
            MetricPoint("InputTokens", record.input_tokens, "Count", dims),
            MetricPoint("OutputTokens", record.output_tokens, "Count", dims),
            MetricPoint("LatencyMs", record.latency_ms, "Milliseconds", dims),
            MetricPoint("WallMs", record.wall_ms, "Milliseconds", dims),
            MetricPoint("StopReason", 1, "Count", {**dims, "StopReason": stop}),  # low-cardinality dimension
        ]
    )
    sink.flush()
    return record
```

```python
# app/service/_05ops_01observability.py
def ask(prompt: str) -> dict[str, Any]:
    """One instrumented model call; the sink comes from config (cloudwatch or emf)."""
    return asdict(instrumented_converse(prompt, make_sink()))
```

- Catch
  - `WallMs` vs `LatencyMs` separates your side from the model's
  - `StopReason=max_tokens` share = truncation signal
