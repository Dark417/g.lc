# 05ops.01observability Generative Artificial Intelligence (GenAI) Observability

> Metrics, logs, and traces for Bedrock calls: health, cost, and audit for a Large Language Model (LLM) service.

## Index

- [1. Source and Scope](#1-source-and-scope)
- [2. One-Minute Version](#2-one-minute-version)
- [3. File Index](#3-file-index)
  - [3.1 Telemetry Layers](#31-telemetry-layers)
  - [3.2 Acting on Telemetry](#32-acting-on-telemetry)
  - [3.3 Decisions and Interview](#33-decisions-and-interview)
- [4. Code Map](#4-code-map)
- [5. Gaps](#5-gaps)
- [References](#references)

## 1. Source and Scope

Lectures: AIP-C01 #46 (slides p.109–110); preview of #195–#206 at the depth needed here.

- Scope: Python + Terraform
- Terraform: `terraform/` module `05ops_01observability`
  - invocation log group + logging config
  - two alarms
  - app policy
- Code: Python `app/*/_05ops_01observability.py` (slice `observability`)
- Numbers
  - Amazon Bedrock and CloudWatch docs, read 2026-11
  - metric names match the Bedrock monitoring page
  - newer ones are marked "verify"

## 2. One-Minute Version

Metrics tell you something is wrong, logs tell you what, traces tell you where.

- What
  - Three layers of Generative Artificial Intelligence (GenAI) telemetry
    - metrics (numbers)
    - logs (payloads)
    - traces (call trees)
  - Bedrock gives metrics for free and logs on request
  - You add custom metrics and tracing
- Why
  - LLM failures are quiet
    - slow, throttled, truncated, expensive, or wrong, with Hypertext Transfer Protocol (HTTP) 200
  - Tokens are the cost unit
    - token metrics are your bill forecast
- How
  - Built-in `AWS/Bedrock` metrics per `ModelId`: latency, tokens, throttles, errors
  - Model invocation logging writes each request/response to CloudWatch Logs and/or Simple Storage Service (S3)
  - Wrap the model call once
    - record latency, tokens, `stopReason`, errors as custom metrics
  - Alarm on throttles and p90 latency
  - Query logs with Logs Insights
- Catch
  - Invocation logs hold prompts and answers
    - Personally Identifiable Information (PII) store; encrypt, restrict, expire
  - Dimensions multiply metric count and cost
    - low cardinality only
  - Percentiles beat averages for latency
  - No ground truth here
    - observability shows health
    - evaluations show quality ([04safety.03evaluations](../04safety/04safety.03evaluations.00index.md))
- 🗣 "Metrics tell you something is wrong, logs tell you what, traces tell you where."
- 🗣 "Tokens are the cost and the capacity unit, so graph tokens before anything else."
- 🗣 "Never log a prompt you would not want read in an audit."

## 3. File Index

Read top to bottom: the three telemetry layers, then alarms and tracing.

### 3.1 Telemetry Layers

- [01builtin-metrics](05ops.01observability.01builtin-metrics.md)
  - Picture, `AWS/Bedrock` metrics, querying tokens over time
- [02invocation-logging](05ops.01observability.02invocation-logging.md)
  - Model invocation logging, what to log and not, Logs Insights
- [03custom-metrics](05ops.01observability.03custom-metrics.md)
  - `PutMetricData` vs Embedded Metric Format (EMF), cardinality, the instrumented Converse wrapper

### 3.2 Acting on Telemetry

- [04alarms-tracing](05ops.01observability.04alarms-tracing.md)
  - Alarms, tracing basics

### 3.3 Decisions and Interview

- [98tradeoffs](05ops.01observability.98tradeoffs.md)
  - When to use / not, knobs, best practices, comparison, failure modes
- [99interview](05ops.01observability.99interview.md)
  - L4 + L5 questions, L5-only design questions

## 4. Code Map

Python only; the layer-first paths below replace the old slice package.

| Concept / scenario | Concept file | Python |
|---|---|---|
| Metric model + sink port | 03 | `app/domain/_05ops_01observability.py` `MetricPoint`, `MetricsSink` |
| PutMetricData adapter with batching | 03 | `app/infra/_05ops_01observability.py` `CloudWatchSink` |
| EMF formatter + sink | 03 | `infra` `format_emf`, `EmfSink` |
| Instrumented Converse (latency, tokens, stopReason, errors) | 03 | `infra` `instrumented_converse` |
| Built-in token metrics over time | 01 | `infra` `token_usage_over_time` |
| Logs Insights over invocation logs | 02 | `infra` `logs_insights` |

| Concept / scenario | Concept file | Python |
|---|---|---|
| One instrumented call, sink from config | 03 | `app/service/_05ops_01observability.py` `ask` |
| Representational State Transfer (REST) | — | `app/api/_05ops_01observability.py` `router` (`/observability`) |

## 5. Gaps

Known gaps between this doc and the code.

- Tracing (X-Ray/OTel), dashboards as code, anomaly-detection alarms
- Guardrail metrics queries, streaming time-to-first-token
- S3 delivery config and Athena over invocation logs

## References

- [aws-samples/amazon-bedrock-samples (observability)](https://github.com/aws-samples/amazon-bedrock-samples)
- [Monitor Amazon Bedrock with CloudWatch](https://docs.aws.amazon.com/bedrock/latest/userguide/monitoring-cw.html)
- [Monitor model invocation using CloudWatch Logs and S3](https://docs.aws.amazon.com/bedrock/latest/userguide/model-invocation-logging.html)
- [CloudWatch Embedded Metric Format specification](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Embedded_Metric_Format_Specification.html)
- [OpenTelemetry GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
