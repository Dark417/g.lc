# 05ops.01observability.98tradeoffs Observability Trade-offs

> When CloudWatch is enough, the knobs and practices, how it compares to Large Language Model (LLM)-native tools, and how it fails.

## Index

- [1. When to Use / Not](#1-when-to-use--not)
- [2. Knobs and Best Practices](#2-knobs-and-best-practices)
- [3. Comparison](#3-comparison)
- [4. Failure Modes](#4-failure-modes)

Back to [00index](05ops.01observability.00index.md).

## 1. When to Use / Not

CloudWatch covers health, cost, and audit; LLM-native tools cover prompt iteration.

- CloudWatch + invocation logging
  - Use: Amazon Web Services (AWS)-native stack, need health, cost and audit fast, no extra vendor
  - Don't: you need prompt versioning, eval datasets and trace User Interfaces (UIs) out of the box
- Custom metrics
  - Use: business or slice dimensions Bedrock lacks
  - Don't: per-user dimensions

## 2. Knobs and Best Practices

Each practice prevents a quiet failure.

- Turn on invocation logging early in dev
  - decide flags per environment
- Keep text delivery on only where prompts are not sensitive, or after redaction
- Set log retention (30 days here) and encrypt with a Customer Managed Key (CMK)
- Alarm on percentiles and on throttles, not on averages
- One wrapper for all model calls
  - consistent metrics and dimensions
- Pass `requestMetadata` with tenant and feature
  - attributable logs
- Dashboards
  - tokens/hour by model
  - p90 latency
  - throttles
  - `stopReason=max_tokens` rate (truncation signal)
- Cost attribution
  - tokens × unit price per model
  - kept in a table, not hard-coded

```python
# app/config/_05ops_01observability.py
class ObservabilitySettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="A_OBSERVABILITY_", env_file=".env", extra="ignore")

    namespace: str = "A/GenAI"  # the app IAM policy allows PutMetricData only in this namespace
    slice_name: str = "observability"  # value of the Slice dimension
    log_group: str = "/aws/bedrock/a-invocations"  # terraform output invocation_log_group
    sink: str = "cloudwatch"  # cloudwatch (PutMetricData) | emf (log line, extracted by CloudWatch)
    max_metrics_per_call: int = 1000  # PutMetricData limit per call: check the quota page
    query_deadline_s: float = 60.0
```

## 3. Comparison

| Option | What it is | Strength | Weakness | Choose when |
|---|---|---|---|---|
| CloudWatch (+ Bedrock logging) | Native metrics, logs, alarms | Zero setup, Identity and Access Management (IAM)-native, one bill | Weak LLM User Experience (UX) (no prompt diff, eval, sessions) | Health, cost, audit on AWS |
| Langfuse | Open-Source Software (OSS) LLM tracing, prompts, evals | Traces, sessions, prompt versions, self-host | You run it (or pay cloud) | Product teams iterating on prompts |
| LangSmith | LangChain's tracing and evals | Deep LangChain/LangGraph integration | Software as a Service (SaaS), tied to that ecosystem | LangChain-heavy stack |
| Datadog LLM Observability | Application Performance Monitoring (APM) extension for LLM calls | One pane with infra and APM | Cost; vendor | Already on Datadog |

- Default
  - CloudWatch for health, alarms, audit
  - add Langfuse (or similar) when prompt iteration and trace inspection matter
- Deciding variable
  - who looks at it (Site Reliability Engineers (SRE) vs prompt engineers)
  - where data may live

Pick: CloudWatch, unless prompt engineers need trace and prompt-version UIs.

## 4. Failure Modes

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Logging config silently replaced | One config per account/Region, another stack applies | Logs stop | One owner (this module); drift check |
| No logs appear | Role trust or policy wrong; CMK lacks Logs grant | Bedrock delivery errors, empty group | Check trust (SourceAccount), key policy |
| Prompts exposed | Wide read access on the log group | IAM review | Restrict, redact, short retention |
| Metric bill explodes | `user_id` in dimensions | Metric count in Billing | Drop dimension; use logs |

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Alarm never fires | Wrong `ModelId` dimension (profile vs model) | `INSUFFICIENT_DATA` | Check `ListMetrics`, fix dimension |
| Averages hide slowness | Alarm on mean latency | Users complain | Use p90 / p99 |
| Truncated answers unnoticed | `stopReason = max_tokens` | Custom `StopReason` metric | Alarm on its share; raise limit |
| `PutMetricData` throttled | One call per datum | `ThrottlingException` | Batch, or switch to Embedded Metric Format (EMF) |
