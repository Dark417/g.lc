# 0fastapi — FastAPI And Python Service Engineering (L4 / L5)

> How a production Python service is built around FastAPI: the request path, caching, resiliency, data access, messaging, the AI provider layer, observability and security.
> Source: chat "X.Python/Fastapi" (Aug 26, 2026), map §10–§17.
> Language-level Python (asyncio, typing, Pydantic) lives in [0python.md](0python.md).
> Ratings are from Aug 2026: 🟢 defensible, 🟡 thin under probing, 🔴 gap.

## Index
- [0. One-minute version](#0-one-minute-version)
- [1. FastAPI request path](#1-fastapi-request-path)
- [2. Caching](#2-caching)
- [3. Resiliency](#3-resiliency)
- [4. Data access: Postgres, SQLAlchemy, Alembic](#4-data-access-postgres-sqlalchemy-alembic)
- [5. Messaging and event-driven backends](#5-messaging-and-event-driven-backends)
- [6. AI provider integration layer](#6-ai-provider-integration-layer)
- [7. Observability](#7-observability)
- [8. Security](#8-security)
- [9. Gaps and the one build that covers them](#9-gaps-and-the-one-build-that-covers-them)
- [Where this fits](#where-this-fits)
- [References](#references)

---

## 0. One-minute version
- **What:** FastAPI is Starlette (the web layer), plus Pydantic (validation), plus a dependency graph (`Depends`).
- **Why:** async by default, typed models, OpenAPI for free. The usual front door for an AI service.
- **How:** every request goes middleware, router, dependencies, endpoint, response model.
- **Catch:** sync code inside an async endpoint blocks the whole worker.
- 🗣 "FastAPI is Starlette plus Pydantic plus a dependency graph. Every question reduces to one of those three."

---

## 1. FastAPI request path

Plain idea: a request passes through layers, like a Spring filter chain. Each layer can reject it, enrich it or time it.

```
  uvicorn ─ Starlette (ASGI) ─ middleware stack ─ router ─ Depends graph ─ endpoint
                                 |                            |
                              exception handlers          Pydantic in/out models
```

- **L4**
  - Request lifecycle, end to end.
  - `Depends`
    - Cached once per request.
    - `yield` dependencies clean up after the response: the DB-session pattern.
  - Pydantic request and response models; `response_model` filters the output.
  - Bad path, query or body input returns 422 automatically.
  - `HTTPException` and custom exception handlers.
  - `APIRouter` with a prefix for versioning (`/v1`).
  - `lifespan` opens pools at startup and closes them at shutdown.
  - `BackgroundTasks` run in-process and are lost on a crash.
    - Defeater: anything that matters goes to a queue.
  - Auto OpenAPI with tags and examples.
  - REST basics:
    - Resource names, status codes, cursor pagination at scale, filters.
    - ETag / If-Match for optimistic concurrency; `Idempotency-Key` on POST.
  - Webhooks:
    - Verify the HMAC signature and a timestamp replay window.
    - Return 2xx fast, then process async.
    - Senders retry, so the handler must be idempotent.
- **L5**
  - Sync `def` endpoints run in anyio's thread pool, which defaults to 40 threads (anyio docs).
    - Async endpoints must never block. Mixing the two gives mystery latency cliffs.
  - Middleware runs outermost first.
    - `BaseHTTPMiddleware` adds overhead; pure ASGI middleware is lighter.
  - Streaming: `StreamingResponse`, SSE for LLM tokens.
    - Detect client disconnect with `request.is_disconnected()`.
  - Request body size limits.
  - Timeouts at three layers: client, uvicorn, upstream.
  - Versioning: URL vs header; deprecation headers; contract tests block breaking changes.
  - Errors: RFC 9457 problem details.
    - Map upstream provider errors to retryable vs terminal (§3).
    - Never leak provider payloads or PII in error bodies.
  - Capacity: `uvicorn --workers N` gives N processes, each with its own pool.
    - DB connections = workers × pool size.
  - SDK design: generate a client from OpenAPI, or hand-write a thin one; version it with the API.
- 🗣 "Sync endpoints borrow a thread; async endpoints share one loop. Block the loop and every request waits."
- Rating: 🟡, one production-ish service.

---

## 2. Caching

Plain idea: keep a copy of an expensive answer close by, and decide how stale it may get.

```
  in-process (lru_cache / TTLCache) ──> Redis (shared, TTL, eviction) ──> CDN / HTTP cache
     cheap, per-worker, inconsistent      consistent-ish, network hop       GETs only
```

- **L4**
  - `functools.lru_cache`
    - Unbounded by default, so it can leak memory.
    - Per process: N workers means N separate caches.
  - `cachetools.TTLCache` for in-process caching with expiry.
  - Redis cache-aside: GET, on miss compute, then `SET ... EX ttl`.
  - Key design: `svc:v1:entity:id`; include a schema version.
  - TTL is the default way to invalidate.
  - Serialize with orjson or msgpack; never unpickle untrusted data.
  - Redis basics:
    - Strings, hashes, sets, sorted sets, streams.
    - `SET NX EX` for locks and idempotency keys.
    - Eviction: `allkeys-lru` for a cache, `noeviction` for real data.
- **L5**
  - Stampede (many misses at once):
    - Single-flight lock per key (`SET NX` with a short TTL).
    - Probabilistic early refresh.
    - In-process request coalescing with a shared asyncio future.
  - Negative caching for "not found".
  - Cache-aside vs write-through vs write-behind.
    - Deciding variable: read / write ratio and tolerance for staleness.
  - Invalidation: event-driven on write, or TTL only; versioned keys instead of deletes.
  - Hot keys: local L1 cache in front of Redis L2.
  - `redis.asyncio`, pipelines, pool size per uvicorn worker.
  - **LLM-specific**
    - Exact-match cache: hash of model + params + normalized prompt.
    - Semantic cache: embedding similarity threshold.
      - Defeater: false hits. Never for personalized or PII prompts.
    - Provider prompt caching for long, stable system prompts.
    - Caching cuts cost and p50 latency, not p99 misses.
  - Any cache is eventually consistent. For exact read-after-write, bypass it or write through.
- 🗣 "A cache is a deliberate consistency bug you've agreed to. The TTL is the size of the bug."
- Rating: 🔴, Redis is on the resume with no bullet behind it.

---

## 3. Resiliency

Plain idea: assume every dependency will be slow or down sometimes. Bound the damage with timeouts, retries, breakers and limits.

```
  timeout ──> retry (backoff + jitter, idempotent only) ──> circuit breaker ──> fallback
     └─ bulkhead (Semaphore per dependency)   └─ rate limit (token bucket)   └─ idempotency key
```

- **L4**
  - Timeouts everywhere: `httpx.Timeout(connect, read, write, pool)`.
  - `tenacity`: `wait_exponential_jitter`, `stop_after_attempt`, `retry_if_exception_type`.
  - Retry only idempotent calls, or ones guarded by an idempotency key.
  - Error classes: 429, 5xx and timeouts are retryable; other 4xx are terminal.
  - Circuit breaker states: closed, open, half-open.
    - Python libraries are thin: `pybreaker`, `aiobreaker`.
  - Rate limiting:
    - Token bucket in Redis, via `INCR` + `EXPIRE` or an atomic Lua script.
    - Per-tenant keys; `slowapi` for FastAPI.
  - Idempotency: key in a header, `SET NX EX` in Redis, store the result, replay it on repeats.
- **L5**
  - Retry storms: retries × fan-out multiply load. Use retry budgets.
  - Never retry a timed-out call you can't prove idempotent.
    - An LLM call can be charged twice.
  - Bulkheads: one `asyncio.Semaphore` per provider, so one slow provider can't take all concurrency.
  - Deadline propagation: pass the remaining time budget to each hop.
  - Hedged requests for tail latency, only if idempotent and cheap.
  - Degradation ladder for AI features: cheaper model, cached answer, deterministic fallback, 503 with `Retry-After`.
  - Outbox pattern for "write DB + publish event" (§5).
  - Java mapping: Resilience4j ≈ tenacity + pybreaker + a manual Semaphore. No batteries-included equivalent.
- **Failure (canonical pattern)**
  - Provider p99 spikes, `httpx` timeout left at default, all async workers pinned.
  - Health check passes because it's a different route. Result: silent full outage.
  - Guardrail: explicit timeouts, bulkheads, and a readiness probe that checks dependencies.
- 🗣 "Retries without a budget are a DDoS you launch at yourself."
- Rating: 🟡, strong in Spring terms; write it once in Python.

---

## 4. Data access: Postgres, SQLAlchemy, Alembic

Plain idea: SQLAlchemy is the Python JPA; Alembic is the Python Liquibase.

- **L4**
  - SQLAlchemy 2.x `select()` style.
  - One `Session` per request through a `yield` dependency.
  - Async: `async_sessionmaker` + `asyncpg`.
  - Alembic `autogenerate`, then review the diff.
    - Defeater: it misses type changes and turns renames into drop + add.
  - Postgres default isolation is read committed.
  - Index the queries you actually run.
  - N+1 queries: fix with `selectinload` or `joinedload`.
- **L5**
  - Zero-downtime migrations (expand / contract): add nullable, backfill, add constraint, drop old.
  - Pool math under async workers.
  - `jsonb` for prompt and response audit, with GIN indexes.
  - Time-partitioned audit tables.
  - Advisory locks for single-writer jobs.
  - Defeater: pgbouncer transaction mode breaks prepared statements, which asyncpg uses.
- 🗣 "Alembic autogenerate is a draft, not a migration."
- Rating: 🟡; Postgres 🟢, SQLAlchemy / Alembic 🔴.

---

## 5. Messaging and event-driven backends

Plain idea: put slow or unreliable work on a queue, and make every consumer safe to run twice.

- **L4**
  - SQS / Pub/Sub consumer loop in Python.
    - Long polling; visibility timeout longer than processing time; batch delete.
  - At-least-once delivery, so consumers must be idempotent.
  - DLQ and redrive.
  - Lambda vs long-running worker (ECS, Cloud Run).
    - Deciding variable: burstiness and duration limits.
- **L5**
  - Outbox pattern.
  - Ordering (SQS FIFO `MessageGroupId`, Pub/Sub ordering keys) costs throughput.
  - Poison messages: max receives, then DLQ, alert, replay tool.
  - Queue depth as the autoscaling signal between API and workers.
  - Exactly-once is a myth at the transport; dedupe at the consumer with a key store.
  - GCP ↔ AWS mapping:

| GCP | AWS |
|---|---|
| Pub/Sub | SNS + SQS |
| Cloud Run / GKE | Fargate or Lambda / EKS |
| Cloud Tasks | SQS delay, EventBridge Scheduler |
| Secret Manager / Memorystore | Secrets Manager / ElastiCache |
| Cloud SQL / Cloud Build | RDS / CodeBuild |

- Rating: 🟢 on AWS, 🟡 on GCP names.

---

## 6. AI provider integration layer

Plain idea: the model sits behind your API like any other dependency. You add a guard, a router, a cache and tracing around it.

```
  client ──> FastAPI ──> guard (auth, PII redact, injection filter) ──> router (model / provider)
         ──> cache ──> provider adapter (Bedrock | Gemini | OpenAI) ──> stream / parse ──> trace + cost
```

- **L4**
  - Provider abstraction: LiteLLM is the boring default.
    - Hand-roll when streaming or tool-call formats differ too much.
  - Auth: Bedrock uses IAM; Vertex uses ADC / service accounts.
  - Structured output: JSON schema or tool schema, then parse with Pydantic. See [2prompt.md](2prompt.md).
  - Stream to the client with SSE.
  - Count tokens; cap `max_tokens`.
  - LLM calls are long, so they get their own timeout class.
- **L5**
  - Cost and latency:
    - Route cheap-first, escalate on failure.
    - Provider prompt caching for long system prompts.
    - Semantic cache that excludes PII.
    - Batch APIs for offline work; per-tenant budgets.
  - Safety:
    - Keep instructions and data separate; tool allowlists; validate outputs; no secrets in context.
    - Redact PII before the call (e.g. Presidio); redact logs; set retention.
  - Evals: model eval vs system eval.
    - LLM-as-judge validated against human labels (Cohen's kappa).
    - Small sets have a noise floor; Langfuse traces feed the dataset.
  - Orchestration:
    - Know when not to go multi-agent (reconciliation story: 4 of 5 steps were deterministic).
    - Typed handoffs; MCP as the tool contract.
    - ADK vs LangGraph: deciding variable is explicit control flow vs the Google ecosystem.
- 🗣 "You don't ship a model, you ship a contract around one: schema in, schema out, cost and trace on every call."
- Rating: 🟢, the differentiator; Vertex SDK hands-on is 🟡.

---

## 7. Observability

Plain idea: every request should leave logs, metrics and a trace you can find later by one ID.

- **L4**
  - JSON logs with `structlog`.
  - Request ID through a `contextvars` middleware.
  - RED metrics per route: rate, errors, duration.
  - Health vs readiness endpoints.
  - Runbook: symptom, dashboard, command, rollback.
- **L5**
  - OpenTelemetry auto-instrumentation for FastAPI, httpx and SQLAlchemy.
  - Manual spans around provider calls, with token and cost attributes.
  - Sampling strategy; redact prompts in logs.
  - SLOs per dependency.
  - Readiness that reflects dependency health without flapping.
- Rating: 🟢 concept, 🟡 OTel wiring in Python.

---

## 8. Security

Plain idea: authenticate every caller, give each one only what it needs, and treat model input as untrusted.

- **L4**
  - OAuth2 / OIDC flows.
  - JWT validation as a FastAPI dependency (`PyJWT` / `authlib`).
    - Fetch and cache JWKS; check `aud`, `iss`, `exp`.
  - Secrets from a secrets manager, not env files.
  - Least-privilege IAM; TLS everywhere; validate input with Pydantic.
- **L5**
  - Service-to-service auth: workload identity, SigV4 or mTLS, depending on the platform.
  - Token exchange for downstream calls.
  - KMS envelope encryption for stored prompts and PII.
  - PII classification and a data-flow diagram for compliance review.
  - Prompt injection is an authorization problem: tool permissions follow the user, not the agent.
- Rating: 🟢.

---

## 9. Gaps and the one build that covers them

| Priority | Area | Rating | Drill |
|---|---|---|---|
| 1 | §1 + §2 + §3 | 🟡 / 🔴 | Build the LLM gateway repo (below) |
| 2 | §4 SQLAlchemy / Alembic | 🔴 | One expand / contract migration in that repo |
| 3 | §5 GCP names | 🟡 | Recite the mapping table cold |

- **The LLM gateway repo**
  - `/v1/complete` with a provider abstraction over Bedrock and Gemini.
  - Redis cache, `tenacity` retries, token-bucket rate limit.
  - SSE streaming, JWT dependency, structlog + OTel.
  - Alembic-managed Postgres audit table.
  - pytest + httpx tests, GitHub Actions.
  - One repo closes most of the gaps above.

---

## Where this fits
- **Place:** L1.2 of [1a-bp.md](../1a-bp.md). The service shell around any agent.
- **Time it deserves:** after the current interview. Tomorrow, skim §1 and §6 only.
- **I should be able to…**
  - Walk a request through FastAPI and say where it can block.
  - Design an LLM response cache: key, TTL, stampede guard.
  - Explain why a timed-out LLM call must not be blindly retried.

## References
1. [FastAPI async docs](https://fastapi.tiangolo.com/async/) and [dependencies with yield](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/).
2. [BerriAI/litellm](https://github.com/BerriAI/litellm) — read `router.py` for fallback and routing.
3. [jd/tenacity](https://github.com/jd/tenacity) and [redis-py](https://github.com/redis/redis-py) — retries; asyncio client, `SET NX EX`.
4. [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/getting-started/) — FastAPI instrumentation.
