"""CloudWatch metrics (API + EMF), instrumented Converse, GetMetricData, Logs Insights."""

import json
import time
from datetime import UTC, datetime, timedelta
from typing import Any

from botocore.exceptions import ClientError

from app.a05_01_observability.config import get_observability_settings
from app.a05_01_observability.domain import CallRecord, MetricPoint, MetricsSink, UsagePoint
from app.shared.aws import client
from app.shared.config import get_settings
from app.shared.retry import backoff

# ---------------------------------------------------------------- 1.3 custom metrics: API adapter


class CloudWatchSink:
    """Buffers points and sends them with PutMetricData in batches.

    Why batch: one call per metric is slow and counts against the PutMetricData API rate limit.
    Catch: a call fails as a whole on a bad datum; and CloudWatch accepts at most 30 dimensions per metric.
    """

    def __init__(self, namespace: str | None = None, max_per_call: int | None = None) -> None:
        cfg = get_observability_settings()
        self._namespace = namespace or cfg.namespace
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
                MetricData=[_datum(p) for p in batch],
            )


def _datum(p: MetricPoint) -> dict[str, Any]:
    return {
        "MetricName": p.name,
        "Dimensions": [{"Name": k, "Value": v} for k, v in p.dimensions.items()],
        "Timestamp": p.timestamp,
        "Value": p.value,
        "Unit": p.unit,
        # "StorageResolution": 1,  # high-resolution (1 s) metrics cost more; default 60 s
    }


# ---------------------------------------------------------------- 1.3 custom metrics: EMF adapter


def format_emf(points: list[MetricPoint], namespace: str | None = None) -> list[str]:
    """Embedded Metric Format: one JSON log line per dimension set; CloudWatch extracts the metrics from the logs.

    Why: no PutMetricData call, no extra latency, works from Lambda/ECS stdout (awslogs/Firelens).
    Catch: the metrics appear only if the line reaches CloudWatch Logs; keep each line under the log event size limit.
    """
    ns = namespace or get_observability_settings().namespace
    grouped: dict[tuple[tuple[str, str], ...], list[MetricPoint]] = {}
    for p in points:
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
            **dict(dims),
            **{p.name: p.value for p in pts},
        }
        lines.append(json.dumps(doc, separators=(",", ":")))
    return lines


class EmfSink:
    """Prints EMF lines to stdout (collected by the container log driver)."""

    def put(self, points: list[MetricPoint]) -> None:
        for line in format_emf(points):
            print(line, flush=True)

    def flush(self) -> None:
        return None


def make_sink() -> MetricsSink:
    return EmfSink() if get_observability_settings().sink == "emf" else CloudWatchSink()


# ---------------------------------------------------------------- 1.1 instrumented Converse


def instrumented_converse(
    prompt: str,
    sink: MetricsSink,
    model_id: str | None = None,
    max_tokens: int = 300,
) -> CallRecord:
    """Converse + record latency, input/output tokens, stopReason, and errors as custom metrics.

    Use it as the single choke point for model calls. Catch: failures are counted too (Errors metric, then re-raise);
    stopReason as a dimension is low-cardinality (end_turn, max_tokens, ...).
    """
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
    wall_ms = (time.perf_counter() - t0) * 1000
    usage = resp["usage"]  # inputTokens, outputTokens, totalTokens
    stop = resp["stopReason"]  # end_turn | max_tokens | stop_sequence | tool_use | guardrail_intervened | ...
    record = CallRecord(
        text=resp["output"]["message"]["content"][0]["text"],
        stop_reason=stop,
        input_tokens=usage["inputTokens"],
        output_tokens=usage["outputTokens"],
        latency_ms=float(resp["metrics"]["latencyMs"]),
        wall_ms=wall_ms,
    )
    sink.put(
        [
            MetricPoint("Invocations", 1, "Count", dims),
            MetricPoint("InputTokens", record.input_tokens, "Count", dims),
            MetricPoint("OutputTokens", record.output_tokens, "Count", dims),
            MetricPoint("LatencyMs", record.latency_ms, "Milliseconds", dims),
            MetricPoint("WallMs", record.wall_ms, "Milliseconds", dims),
            MetricPoint("StopReason", 1, "Count", {**dims, "StopReason": stop}),
        ]
    )
    sink.flush()
    return record


# ---------------------------------------------------------------- 1.1 built-in metrics: GetMetricData


def token_usage_over_time(model_id: str, hours: int = 24, period_s: int = 3600) -> list[UsagePoint]:
    """Query AWS/Bedrock InputTokenCount and OutputTokenCount (Sum) over time with GetMetricData.

    Use for cost proxies and capacity trends. Catch: results can be paginated (NextToken) and the dimension
    value must match how the model was called (model id vs inference profile id): check ListMetrics.
    """
    end = datetime.now(UTC)
    start = end - timedelta(hours=hours)

    def q(qid: str, metric: str) -> dict[str, Any]:
        return {
            "Id": qid,
            "MetricStat": {
                "Metric": {
                    "Namespace": "AWS/Bedrock",
                    "MetricName": metric,
                    "Dimensions": [{"Name": "ModelId", "Value": model_id}],
                },
                "Period": period_s,
                "Stat": "Sum",
            },
            "ReturnData": True,
        }

    series: dict[str, dict[datetime, float]] = {"in": {}, "out": {}}
    token: str | None = None
    while True:
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


# ---------------------------------------------------------------- 1.2 invocation logs: Logs Insights

TOKENS_BY_MODEL_QUERY = (
    "fields @timestamp, modelId, input.inputTokenCount as inTok, output.outputTokenCount as outTok "
    "| stats count(*) as calls, sum(inTok) as inputTokens, sum(outTok) as outputTokens by modelId "
    "| sort outputTokens desc"
)  # field names follow the invocation log schema: verify against one real record


def logs_insights(query: str = TOKENS_BY_MODEL_QUERY, hours: int = 24) -> list[dict[str, str]]:
    """StartQuery then poll GetQueryResults until Complete; returns rows as dicts.

    Catch: queries are asynchronous and billed per GB scanned; results of a Running query are partial;
    always bound the time range. Statuses: Scheduled, Running, Complete, Failed, Cancelled, Timeout.
    """
    cfg = get_observability_settings()
    logs = client("logs")
    end = int(time.time())
    qid = logs.start_query(
        logGroupName=cfg.log_group,
        startTime=end - hours * 3600,
        endTime=end,
        queryString=query,
        limit=100,
    )["queryId"]
    deadline = time.monotonic() + cfg.query_deadline_s
    attempt = 0
    while True:
        resp = logs.get_query_results(queryId=qid)
        status = resp["status"]
        if status == "Complete":
            return [{c["field"]: c["value"] for c in row if c["field"] != "@ptr"} for row in resp["results"]]
        if status in ("Failed", "Cancelled", "Timeout"):
            raise RuntimeError(f"Logs Insights query {qid} ended {status}")
        if time.monotonic() >= deadline:
            logs.stop_query(queryId=qid)  # stop paying for a query nobody waits for
            raise TimeoutError(f"query {qid} still {status}")
        time.sleep(backoff(attempt, base=0.5, cap=5.0))
        attempt += 1
