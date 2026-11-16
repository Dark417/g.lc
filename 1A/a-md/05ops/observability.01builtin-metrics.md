# observability.01builtin-metrics Picture and Built-In Bedrock Metrics

> Where each telemetry stream comes from, and the free `AWS/Bedrock` metrics per model.

## Index

- [1. Picture](#1-picture)
- [2. Built-In Metrics](#2-built-in-metrics)
  - [2.1 Core Metrics](#21-core-metrics)
  - [2.2 Newer Metrics and Guardrails](#22-newer-metrics-and-guardrails)
  - [2.3 Code: Tokens Over Time](#23-code-tokens-over-time)

Back to [00index](observability.00index.md).

## 1. Picture

Bedrock emits metrics and logs on its own; the wrapper adds custom metrics.

```text
 app ──converse──► Bedrock ──► AWS/Bedrock metrics (free, per ModelId)
  │                   └──────► invocation logs ─► CW Logs (a-invocations, KMS) + S3 large bodies
  │ wrapper
  └─► MetricsSink ─► PutMetricData / EMF line ─► CloudWatch (A/GenAI, ModelId × Slice)
                                    │
                    alarms (throttles, p90) ─► SNS a-alerts
                    GetMetricData (tokens/time) · Logs Insights (by model, caller)
```

Notice that only the wrapper knows your slice; Bedrock metrics know only the model.

## 2. Built-In Metrics

Namespace `AWS/Bedrock`, dimension `ModelId`.

- Check `ListMetrics` for the exact `ModelId` value when you call through an inference profile
- About one-minute granularity
- Statistics: `Sum`, `Average`, and percentiles via `ExtendedStatistics`

### 2.1 Core Metrics

| Metric | Meaning | Use |
|---|---|---|
| `Invocations` | Successful requests | Traffic |
| `InvocationLatency` | Request latency, ms | p90 / p99 alarm |
| `InputTokenCount` / `OutputTokenCount` | Tokens in and out | Cost, quota headroom |
| `InvocationThrottles` | Requests throttled (429) | Quota alarm |
| `InvocationClientErrors` / `InvocationServerErrors` | 4xx / 5xx | Bug vs outage |

- `InvocationLatency` excludes your side
  - retrieval, rerank, prompt building, retries

### 2.2 Newer Metrics and Guardrails

- Newer metrics (verify on the monitoring page)
  - time to first token for streaming
  - quota-usage estimates
  - prompt-cache token counts
- Guardrails publish their own namespace
  - `AWS/Bedrock/Guardrails`
  - invocations, latency, intervention counts (verify names)

### 2.3 Code: Tokens Over Time

- `GetMetricData` with `Sum` per period = cost proxy and capacity trend

```python
# app/infra/_05ops_01observability.py
def token_usage_over_time(model_id: str, hours: int = 24, period_s: int = 3600) -> list[UsagePoint]:
    end = datetime.now(UTC)
    start = end - timedelta(hours=hours)

    def q(qid: str, metric: str) -> dict[str, Any]:
        return {
            "Id": qid,
            "MetricStat": {
                "Metric": {
                    "Namespace": "AWS/Bedrock",
                    "MetricName": metric,
                    # must match how the model was called (model id vs inference profile id)
                    "Dimensions": [{"Name": "ModelId", "Value": model_id}],
                },
                "Period": period_s,
                "Stat": "Sum",
            },
            "ReturnData": True,
        }

    series: dict[str, dict[datetime, float]] = {"in": {}, "out": {}}
    token: str | None = None
    while True:  # results can be paginated (NextToken)
        kwargs: dict[str, Any] = {
            "MetricDataQueries": [q("in", "InputTokenCount"), q("out", "OutputTokenCount")],
            "StartTime": start,
            "EndTime": end,
            "ScanBy": "TimestampAscending",
        }
        if token:
            kwargs["NextToken"] = token
        resp = client("cloudwatch").get_metric_data(**kwargs)
        for r in resp["MetricDataResults"]:
            for ts, val in zip(r["Timestamps"], r["Values"], strict=True):
                series[r["Id"]][ts] = series[r["Id"]].get(ts, 0.0) + val
        token = resp.get("NextToken")
        if not token:
            break
    stamps = sorted(set(series["in"]) | set(series["out"]))
    return [UsagePoint(ts, series["in"].get(ts, 0.0), series["out"].get(ts, 0.0)) for ts in stamps]
```

- Catch
  - Wrong `ModelId` dimension ⇒ empty series and `INSUFFICIENT_DATA` alarms
