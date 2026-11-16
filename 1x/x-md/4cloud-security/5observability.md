# 5observability — Metrics, Logs, Traces, SLOs And Alerting (L5)

- **In plain words:** observability is being able to answer "what is wrong, where, and for whom" from the outside of a running system, without shipping new code to find out.
- Tag: `software`
- Source: upgraded from `1sd/00.base/12.observability.md` (2026-11-15)
- Related: [5cloud-availability.md](5cloud-availability.md) (SLOs, reliability patterns), [3kafka.md](3kafka.md) (consumer lag), [6eks.md](6eks.md) section 8, [6ecs.md](6ecs.md)

## Index

- [0. One-Minute Version](#o0)
- [1. Concept](#o1)
- [2. Architecture](#o2)
- [3. Metrics](#o3)
- [4. Logs](#o4)
- [5. Traces](#o5)
- [6. SLIs, SLOs And Error Budgets](#o6)
- [7. Alerting And On-Call](#o7)
- [8. Async And Data-Pipeline Observability](#o8)
- [9. Beyond The Three Pillars](#o9)
- [10. Cost Control](#o10)
- [11. Tool Comparison](#o11)
- [12. Failure Modes](#o12)
- [13. Interview Questions](#o13)
- [14. Pitfalls](#o14)
- [15. Where This Fits](#o15)
- [References](#refs)

---

<a id="o0"></a>
## 0. One-Minute Version

- **What:** metrics say *something is wrong*, traces say *where*, logs say *what exactly happened*; all three joined by a trace ID
- **Why:** with many services, a slow request has dozens of suspects; without telemetry, incidents take hours
- **How:** instrument once with OpenTelemetry, send through a collector to metric, log and trace stores; alert on SLO burn rate, not on CPU
- **Catch:** telemetry is expensive (cardinality, log volume, trace storage), so you budget and sample it like any other resource
- 🗣 "I define SLIs per user journey, page on multi-window burn rate, and debug from metric to exemplar trace to logs by trace ID."

---

<a id="o1"></a>
## 1. Concept ★★★

- **Plain idea:** monitoring checks the questions you knew to ask; observability lets you ask new ones during an incident.
- **Picture it:** a car dashboard (metrics) shows the engine is hot; the trip recorder (trace) shows it started on the hill; the mechanic's notes (logs) show the coolant leak.
- **How it works**
  1. Code emits telemetry: counters and histograms, structured log events, spans
  2. Every signal carries the same resource attributes (service, version, region) and, where possible, the trace ID
  3. A collector batches, filters, samples and routes it to backends
  4. SLIs are computed from metrics; alerts fire on SLO burn
  5. On-call follows a runbook from the alert to a dashboard, to a trace, to logs
- **The catch:** more telemetry is not more insight; unbounded labels and debug logs bury the signal and the bill
- 🗣 "Metrics for detection, traces for localization, logs for explanation."

| Pillar | Shape | Cheap at | Expensive at | Answers |
|---|---|---|---|---|
| Metrics | Numbers over time, aggregated | Long retention, alerting | Per-user detail (cardinality) | Is it broken? How bad? |
| Logs | Discrete events with fields | Exact detail of one event | Volume at high QPS | What happened to this request? |
| Traces | Tree of timed spans per request | Latency attribution across services | Storing 100% | Which hop is slow? |

---

<a id="o2"></a>
## 2. Architecture ★★

```text
app (OTel SDK / agent) --OTLP--> OTel Collector (agent or gateway)
     |                               | batch, filter, redact, tail-sample
     | /metrics scrape               +--> metrics: Prometheus / Mimir / CloudWatch
     +-- Prometheus                  +--> logs:    Loki / OpenSearch / CloudWatch Logs
                                     +--> traces:  Tempo / Jaeger / X-Ray
Grafana / Datadog UI <-- queries --  Alertmanager / PagerDuty <-- alert rules
```

- **SDK / agent:** auto-instrumentation for HTTP, gRPC, JDBC, Kafka clients (Java agent, Python distro)
- **Collector:** the control point; change sampling, redaction or vendor without redeploying apps
- **Agent vs gateway:** an agent per node (DaemonSet / sidecar) is close to the app; a gateway pool is needed for tail sampling, since all spans of a trace must reach the same instance (route by trace ID)
- **Backends:** separate stores per signal; correlation happens by shared IDs and attributes

---

<a id="o3"></a>
## 3. Metrics ★★★

- **Plain idea:** cheap numbers sampled over time, good for "is it normal right now?".

### 3.1 What to measure

| Method | For | Signals |
|---|---|---|
| RED | Request-driven services | Rate, Errors, Duration |
| USE | Resources (CPU, disk, pools, queues) | Utilization, Saturation, Errors |
| Four golden signals (Google SRE book) | Any user-facing system | Latency, Traffic, Errors, Saturation |

- Per component, the ones that matter
  - HTTP service: RPS, 5xx ratio, p50 / p99 latency, in-flight requests
  - Database: query latency, connections in use vs pool size, replication lag, lock waits
  - Cache: hit ratio, evictions, memory used
  - Queue / Kafka: consumer lag (messages and seconds), produce latency, DLQ depth
  - JVM: GC pause time, heap after GC, thread pool queue length

### 3.2 Metric types

| Type | Meaning | Use for | Catch |
|---|---|---|---|
| Counter | Only goes up | Requests, errors, bytes | Query its `rate()`, not the raw value |
| Gauge | Goes up and down | Queue depth, memory, connections | A scrape can miss spikes between samples |
| Histogram | Counts in buckets | Latency, sizes; percentiles at query time | Bucket edges decide accuracy; pick them around your SLO threshold |
| Summary | Percentiles computed in the client | Single-instance latency | Cannot be aggregated across instances |

- Percentiles cannot be averaged: the mean of ten pods' p99 is not the fleet p99; aggregate histogram buckets, then compute the percentile
- Native / exponential histograms (Prometheus native histograms, OTel exponential histograms) avoid hand-picked buckets

### 3.3 Cardinality ★★★

- **Plain idea:** every unique label combination is a separate time series stored forever-ish.
- Worked example: 50 endpoints × 5 status codes × 3 regions = 750 series; add `user_id` with 1M users and it is 750M series, which breaks most backends
- Rules
  - Labels must be bounded: endpoint template (`/orders/{id}`, not `/orders/123`), status class, region, version
  - High-cardinality detail (user, tenant, request) goes on traces and logs, not metric labels
  - Set a per-service series budget; drop or aggregate labels in the collector when exceeded
- **Exemplars:** a histogram bucket can carry a sample trace ID, so a p99 spike on a dashboard links straight to one slow trace

---

<a id="o4"></a>
## 4. Logs ★★

- **Plain idea:** one structured event per meaningful thing, searchable by any field.

```json
{"ts": "2026-07-01T15:30:00Z", "level": "ERROR", "service": "payment",
 "version": "1.42.0", "trace_id": "4bf92f35...", "span_id": "00f067aa...",
 "msg": "charge failed", "psp": "stripe", "error_code": "card_declined",
 "duration_ms": 245}
```

- Structured (JSON) with stable field names; `trace_id` on every line via MDC (Java) or context vars (Python)
- Levels: DEBUG off in production; INFO for business events; WARN for handled surprises (retry, fallback); ERROR for failed operations
- Pipeline: stdout → Fluent Bit / Vector / OTel Collector → Loki, OpenSearch, CloudWatch Logs, Splunk
- Tiering: hot (days, searchable), warm, archive to object storage for compliance
- Sampling: keep 100% of errors and slow requests, sample routine success logs
- Wide events: one rich event per request with many fields (the Honeycomb style) often beats ten thin log lines
- Never log secrets, tokens, full card numbers or raw PII; redact in the collector as a second line of defense
- Audit logs are a separate stream with no sampling and stricter retention ([7security.md](7security.md) section 19)

---

<a id="o5"></a>
## 5. Traces ★★★

- **Plain idea:** a trace is the timeline of one request across every service it touched.

```text
trace 4bf9...  total 250 ms
[gateway        ] 0 ------------------------------ 250
  [auth         ]   5 -- 25
  [catalog      ]       30 --------------------- 200
    [db query   ]         35 -------- 100   <- slowest span
    [cache get  ]                     105 - 120
```

- **Span:** one timed operation with attributes (route, DB statement summary, status)
- **Context propagation:** the W3C `traceparent` header carries trace ID and parent span ID across HTTP / gRPC; Zipkin's older B3 headers still appear
- **Sampling**

| Strategy | Decision point | Good at | Bad at |
|---|---|---|---|
| Head (probabilistic) | At the first span | Cheap, simple, consistent | Misses rare errors and slow paths |
| Tail | After the trace completes, in a collector gateway | Keeps all errors and slow traces, samples the rest | Must buffer whole traces; needs trace-ID-aware routing |
| Rate-limited / adaptive | Per endpoint quotas | Fair coverage of low-traffic endpoints | More configuration |

- Typical L5 answer: head-sample a small percentage for baseline, tail-sample 100% of errors and traces over the latency SLO
- Catch: a trace is only as complete as its weakest service; one uninstrumented hop breaks the tree, so auto-instrumentation is the baseline

---

<a id="o6"></a>
## 6. SLIs, SLOs And Error Budgets ★★★

- **Plain idea:** pick the few numbers users actually feel, set a target, and treat the allowed failure as a budget you spend on change.
- **SLI** = good events / valid events, measured as close to the user as possible (load balancer or client, not the pod)
  - Availability: non-5xx responses / all responses (exclude 4xx caused by clients)
  - Latency: requests under 300 ms / all requests
  - Freshness (pipelines): records processed within 5 min of arrival / all records
- **SLO** = target over a window: 99.9% over a rolling 30 days
- **Error budget** = 1 − SLO: 0.1% of 30 days ≈ 43 minutes of full outage, or the equivalent in partial failures
- **SLA** = a contract with penalties, set looser than the SLO so you have warning room
- Define SLOs per user journey (checkout, search), not per microservice
- Budget policy: budget left → ship faster; budget gone → freeze risky launches, spend effort on reliability
- 🗣 "SLIs are good-over-valid ratios at the edge; the SLO turns into an error budget, and burn rate drives both paging and release decisions."

---

<a id="o7"></a>
## 7. Alerting And On-Call ★★★

- **Plain idea:** page a human only when users are hurting or will be soon, and tell them what to do.

### 7.1 Symptoms, not causes

- Page on symptoms: error ratio, latency SLI, freshness
- Causes (CPU 85%, disk 70%) go to dashboards or tickets, unless they predict a hard failure (disk full in 4 hours)

### 7.2 Multi-window, multi-burn-rate alerts

- **Burn rate** = how fast you spend the budget relative to "exactly on target"; burn rate 1 uses the whole budget in the window
- Recommended starting point for a 30-day SLO (Google SRE Workbook, "Alerting on SLOs")

| Budget spent | Long window | Short window | Burn rate | Action |
|---|---|---|---|---|
| 2% | 1 hour | 5 minutes | 14.4 | Page |
| 5% | 6 hours | 30 minutes | 6 | Page |
| 10% | 3 days | 6 hours | 1 | Ticket |

- Fire only when both windows exceed the rate: the long window proves it is significant, the short window proves it is still happening (so the alert resets quickly after a fix)
- Worked example: 99.9% SLO, burn 14.4 means a 1.44% error ratio; sustained, the 30-day budget is gone in about 2 days

### 7.3 Good alert hygiene

- Every page has a runbook link: meaning, likely causes, first checks, how to mitigate, how to verify
- Severity levels: page now, fix in business hours, fix this sprint
- Group and deduplicate (Alertmanager grouping, inhibition of downstream alerts when the upstream is down)
- Track pages per shift and false-positive rate; delete alerts nobody acts on
- Annotate dashboards with deploys and flag changes: "what changed?" is the first incident question

### 7.4 Incident response, briefly

- Roles: incident commander, operations lead, communications
- Mitigate first (roll back, shift traffic, shed load), root-cause later
- Blameless postmortem with timeline, impact in SLO terms, and tracked action items

---

<a id="o8"></a>
## 8. Async And Data-Pipeline Observability ★★

- **Plain idea:** in queues and pipelines, "slow" shows up as a growing backlog, not a slow response.
- Consumer lag in **time**, not just messages: 10,000 messages behind means nothing until you know the rate
- End-to-end freshness: stamp the event time at the producer, measure `now − event_time` at the sink
- DLQ depth and age; poison-message rate
- Trace across a queue: inject `traceparent` into message headers; the consumer span uses a **span link** to the producer span (one batch can link many producers)
- Batch jobs: expected-run "dead man's switch" alerts (alert when a job did not report success by its deadline)
- Data quality checks (row counts, null ratios, schema drift) as SLIs for data platforms

---

<a id="o9"></a>
## 9. Beyond The Three Pillars ★★

| Signal | What it adds | Tools |
|---|---|---|
| Continuous profiling | Which function burns CPU or allocates memory in production, over time | Pyroscope, Parca, Datadog Profiler, async-profiler / JFR for the JVM |
| eBPF telemetry | Kernel-level network and syscall visibility without code changes | Cilium Hubble, Pixie, Grafana Beyla |
| Synthetic monitoring | Scripted probes from outside: is login working from three regions? | CloudWatch Synthetics, Checkly, Grafana synthetic monitoring |
| RUM (real user monitoring) | Browser and mobile latency as users see it (Core Web Vitals) | Datadog RUM, OTel browser SDK, Sentry |
| Error tracking | Grouped exceptions with stack traces and release tags | Sentry, Rollbar |

- Synthetic catches "nobody can log in" at 3 a.m. with no traffic; RUM catches "slow only on mobile in India"

---

<a id="o10"></a>
## 10. Cost Control ★★

- **Plain idea:** telemetry bills grow with traffic and labels; treat them as a budget with an owner.
- Levers, in order of impact
  1. Drop high-cardinality labels and unused metrics (usage analysis in the backend)
  2. Sample success logs and traces; keep errors and slow paths
  3. Shorten hot retention; archive to object storage
  4. Aggregate in the collector (recording rules, span metrics) before storage
- Derive RED metrics from spans (span metrics) instead of instrumenting twice
- Vendor pricing is per host, per GB ingested or per series; model it before choosing (exact prices change, check the current pricing pages)

---

<a id="o11"></a>
## 11. Tool Comparison ★★

| Option | What it is | Good at | Bad at | Choose when |
|---|---|---|---|---|
| OpenTelemetry | Vendor-neutral SDKs, protocol (OTLP) and collector | Instrument once, switch backends | Not a backend; logs support matured later than traces | Always, as the instrumentation layer |
| Prometheus + Grafana (+ Mimir, Loki, Tempo) | Open-source metrics, logs, traces stack | Kubernetes-native, PromQL, cost control | You run and scale it | Platform team, cost-sensitive |
| Datadog / New Relic / Dynatrace | Commercial all-in-one SaaS | Fast setup, correlation, APM | Cost grows quickly with hosts, logs and custom metrics | Small team, wants one pane |
| AWS CloudWatch + X-Ray | AWS-native metrics, logs, traces | Zero setup for AWS services, Container Insights | Weaker querying, cross-cloud | AWS-only, modest scale |
| ELK / OpenSearch | Search-first log store | Full-text search on logs | Heavy to run, expensive at volume | Log search is the main need |
| Jaeger / Zipkin | Open-source tracing backends | Simple self-hosted tracing | Only traces | Self-hosted tracing |

- Default: OpenTelemetry for instrumentation, then Grafana stack if you run a platform team, or one SaaS vendor if you don't

---

<a id="o12"></a>
## 12. Failure Modes

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Cardinality explosion | `user_id` or raw path as a label | Series count jumps; backend OOM; slow queries | Bounded labels; collector drop rules; per-service budgets |
| Alert fatigue | Cause-based and threshold alerts | Pages per shift high, many ignored | Burn-rate alerts on SLIs; delete unactioned alerts |
| Broken traces | One service drops `traceparent` | Orphan spans, short trees | Auto-instrumentation; propagation tests in CI |
| Blind during outage | Monitoring runs in the same region or cluster it watches | Dashboards down with the incident | Out-of-band monitoring and synthetics from another region |
| Wrong percentiles | Averaging p99s, summaries across pods | Fleet p99 looks too good | Aggregate histogram buckets |
| PII in logs | Logging request bodies | Audit or scanner finds it | Redaction in code and collector; field allowlists |
| Telemetry bill shock | Debug logs left on, 100% tracing | Ingest volume alerts | Sampling, retention tiers, ownership per team |

---

<a id="o13"></a>
## 13. Interview Questions

**Q1. A user says checkout is slow. How do you debug it?**
- L4: check latency dashboards for checkout, find a slow trace, see which span dominates, read that service's logs by trace ID
- L5 extra: start from the SLI (is it fleet-wide or one segment: region, version, tenant?), correlate with the deploy annotation, use exemplars to jump to slow traces, compare to a baseline trace, and mitigate (roll back) before root-causing

**Q2. How do you alert without waking people for nothing?**
- L4: alert on error rate and latency, not CPU; every alert has a runbook
- L5 extra: SLO-based multi-window multi-burn-rate alerts (14.4× over 1 h and 5 min pages; 1× over 3 days tickets), grouping and inhibition, and a review of pages per shift

**Q3. How do you trace through Kafka?**
- L4: put the trace ID in the message headers
- L5 extra: producer injects `traceparent`; the consumer starts a new span with a span link (batches link many producers); measure lag in seconds and end-to-end freshness from event time

**Q4. Your metrics bill tripled. What do you do?**
- L4: find the noisy metrics and remove them
- L5 extra: per-service series budgets, drop high-cardinality labels at the collector, move per-user detail to traces, sample success logs, shorten hot retention, derive RED from span metrics

**Q5. Head or tail sampling?**
- L4: head is simple and random; tail keeps interesting traces
- L5 extra: tail needs a gateway tier routed by trace ID with buffering; common mix is low head rate plus tail rules for errors and SLO-violating latency

---

<a id="o14"></a>
## 14. Pitfalls

- "I'll add logs" with no structure, aggregation or trace ID
- No traces in a microservice design: "how do you find the slow hop?" has no answer
- Alerting on CPU instead of user-facing symptoms
- No SLO named: no way to say "we are violating it"
- Fifty-panel dashboards: start with golden signals per journey
- `user_id` as a metric label

---

<a id="o15"></a>
## 15. Where This Fits

- Pattern: the operations layer every system design ends with ("how do you know it works?")
- Time it deserves: 4–6 focused hours; reuse it in every SD wrap-up
- I should be able to
  - Define an SLI as good / valid for a given journey and compute its error budget
  - Explain the burn-rate table and why two windows
  - Walk metric → exemplar → trace → logs during a mock incident
  - Explain cardinality with a number and how to cap it

<a id="refs"></a>
## References

- [OpenTelemetry documentation](https://opentelemetry.io/docs/)
- [Google SRE Workbook — Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/)
- [Google SRE Book — Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/)
- [Prometheus documentation — Metric types and histograms](https://prometheus.io/docs/practices/histograms/)
- [W3C Trace Context](https://www.w3.org/TR/trace-context/)
