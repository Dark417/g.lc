# observability.99interview Observability Interview Questions

> L4 + L5 answers on what to monitor, telemetry layers, invocation logging, Embedded Metric Format (EMF), dimensions, and cost attribution.

## Index

- [1. Core Questions](#1-core-questions)
  - [1.1 What to Monitor](#11-what-to-monitor)
  - [1.2 Metrics vs Logs vs Traces](#12-metrics-vs-logs-vs-traces)
  - [1.3 Invocation Logging and Its Risk](#13-invocation-logging-and-its-risk)
  - [1.4 PutMetricData vs EMF](#14-putmetricdata-vs-emf)
  - [1.5 Which Dimensions](#15-which-dimensions)
- [2. L5-Only Questions](#2-l5-only-questions)
  - [2.1 Cost Attribution per Tenant](#21-cost-attribution-per-tenant)
  - [2.2 Latency Doubled, Bedrock Flat](#22-latency-doubled-bedrock-flat)

Back to [00index](observability.00index.md).

## 1. Core Questions

Each question has a bounded L4 answer and an L5 extension.

### 1.1 What to Monitor

**Q:** What would you monitor for a Bedrock-backed service?

**L4 answer**

- Latency percentiles
- Throttles, errors
- Input/output tokens per model
- Alarms to Simple Notification Service (SNS); dashboards by model

**L5 extra**

- Add `stopReason` mix, guardrail interventions, cache hit rate
- Quality is separate: evaluations, user feedback

See [01builtin-metrics](observability.01builtin-metrics.md).

### 1.2 Metrics vs Logs vs Traces

**Q:** Metrics vs logs vs traces for Large Language Model (LLM) apps?

**L4 answer**

- Metrics: aggregates and alarms
- Logs: per-request payloads
- Traces: step timing across components

**L5 extra**

- Cost and cardinality
  - metrics cheap per series
  - logs per Gigabyte (GB)
  - traces sampled
- Use logs for high-cardinality questions

### 1.3 Invocation Logging and Its Risk

**Q:** How do you turn on invocation logging and what's the risk?

**L4 answer**

- One logging configuration
  - CloudWatch group and/or Simple Storage Service (S3)
  - flags per data type
- Risk: prompts and completions are stored

**L5 extra**

- Encrypt, retain briefly, restrict, redact
- Large payloads to S3
- One config per account/Region ⇒ single owner

See [02invocation-logging](observability.02invocation-logging.md).

### 1.4 PutMetricData vs EMF

**Q:** PutMetricData vs EMF?

**L4 answer**

- Application Programming Interface (API) call with batching vs a log line CloudWatch converts to metrics

**L5 extra**

- EMF avoids API throttling and latency but depends on log delivery
- Same cardinality cost either way

See [03custom-metrics](observability.03custom-metrics.md).

### 1.5 Which Dimensions

**Q:** Which dimensions do you attach?

**L4 answer**

- Model id, slice/feature, maybe environment

**L5 extra**

- Never request or user ids
  - each combination is a billed metric

## 2. L5-Only Questions

Depth, scale, and design ownership.

### 2.1 Cost Attribution per Tenant

**Q:** Design cost attribution per tenant.

→ Pass tenant in `requestMetadata` → invocation logs.  
→ Logs Insights or an S3/Athena job sums tokens per tenant × price table.  
→ Tenant-tier (not tenant-id) as metric dimension for alarms.  
→ Reconcile with the bill monthly; alert on tenants above quota.

### 2.2 Latency Doubled, Bedrock Flat

**Q:** Latency doubled after a release but Bedrock metrics look flat. Where do you look?

- Bedrock `InvocationLatency` excludes your side
  - retrieval, rerank, prompt size growth, retries
- Compare wall time vs model-reported `latencyMs` from the wrapper
- Traces by span
- Check `InputTokenCount` growth
  - longer prompts = slower
