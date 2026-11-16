# #10 · Agent Platform (LLM gateway + agent runtime for 30 teams)

> Prompt: "Design the internal platform that 30 product teams use to build, run, evaluate, and pay for LLM agents — model access, tools, sessions, evals, cost, safety — without each team rebuilding it."

## §0 Assumptions
- 30 teams · 200 agents · 5M LLM calls/day · 3 model providers (Gemini, Claude, OSS on GPUs) `(assume)`
- Gateway latency overhead ≤ 20 ms p95; availability 99.95%
- Tenants = teams; chargeback per team; central safety policies + team-level overrides
- Stack: gateway (LiteLLM-style, Go/Python) · runtime (ADK/LangGraph on K8s) · tool registry (MCP) · Postgres · Redis · ClickHouse (traces/metrics) · Langfuse/OTel · object store

## §1 Why a platform (not "why an agent") `[SW]`
- Baseline: each team calls providers directly. Breaks: 30 copies of retries/caching/keys, no cost visibility, inconsistent safety, no shared evals, vendor lock-in per team.
- Platform adds: one model API, shared tools with per-user auth, sessions/memory, eval-as-a-service, cost/quota, safety, versioned deploys.
- Scope discipline: platform owns *plumbing*; teams own prompts, tools, and quality. Build-vs-buy: gateway = adopt OSS (LiteLLM) + harden; runtime = managed (Vertex Agent Engine / Bedrock AgentCore) vs self-hosted on K8s → choose self-hosted only if multi-cloud or data residency demands.
- **L5:** the hard questions are org: who is paged when a provider degrades, how quotas are negotiated, how a team's prompt change can't break another (isolation), and how to make the paved road *easier* than going around it.

## §2 Crux
- **One control plane for model calls and tool calls, with tenant isolation, cost attribution, and evals — that teams choose because it's faster than DIY.**
- Success points: gateway reliability (retries, failover, caching) · per-request attribution (team, agent, version, user) · tool registry with delegated user auth · session/memory service · eval service with judge calibration · policy engine (safety, PII) · deploy/rollback of prompts and models.
- Business metric: adoption (% of LLM traffic through platform), $ saved, incidents avoided; AI metric: eval coverage (% agents with CI eval gates).

## §3 NFR / BoE
| NFR | Target | Enforcer |
|---|---|---|
| Overhead | ≤ 20 ms p95 added | async logging, streaming passthrough |
| Availability | 99.95%; provider failover < 30 s | multi-provider routing, breakers |
| Isolation | tenant quotas; no cross-tenant data in cache/memory | key scoping, namespace per tenant |
| Attribution | 100% of calls tagged | required headers, reject untagged |
| Cost control | per-team monthly budget; hard stop at 120% | quota service |
| Safety | central PII/injection policies; per-team allow-listed tools | policy engine |
- 5M calls × 3k tokens = 15B tokens/day ≈ $30–60k/day → attribution and caching pay for the platform many times over. Traces: 5M spans/day → ClickHouse, 30 d hot.

## §4 HLD
```
Teams' agents (ADK/LangGraph, in their services or on the platform runtime)
        |  SDK / OpenAI-compatible API + required headers: X-Team, X-Agent, X-Agent-Version, X-User
        v
[SW] LLM Gateway: authn (service identity) -> quota/budget -> policy (PII redact, injection classifier, allow-listed models)
     -> router (model alias -> provider; fallbacks; region) -> cache (exact + prefix) -> provider adapters (retries, breakers)
     -> async emit: span (tokens, $, latency, version) -> [SW] ClickHouse / Langfuse
[SW] Tool Registry (MCP servers): catalog, schemas, per-tool auth mode (service | user-delegated OAuth), audit
[SW] Session & Memory Service: sessions/events (Postgres, tenant-namespaced), memory (pgvector), retention policies
[SW] Runtime (K8s): agent-as-container, job queue for long runs, checkpoints (Postgres), autoscale, sandbox pool
[AI] Eval Service: golden sets per agent, judge pool (calibrated), CI gate API, online sampling, A/B
[SW] Control plane: prompt/model version registry, canary, rollback, budgets, dashboards
```

## §5 Components — problem → design
- **Gateway `[SW]`:** problem = 30 retry implementations, no failover, key sprawl. Design: OpenAI-compatible surface + native passthrough; model *aliases* (`chat-fast`, `chat-strong`) mapped centrally; per-provider breakers; retry on 429/5xx with budget; streaming passthrough; provider keys only in gateway. Failover order per alias; shadow-compare providers before swapping.
  - **L5:** an alias change is a global prompt-behavior change → treat alias mappings as versioned deploys with canary, not config edits.
- **Quota/cost `[SW]`:** token bucket per team (RPM/TPM) + monthly $ budget from price table; soft alert 80%, hard stop 120%; per-user sub-quotas optional; cost computed from tokens at request time, reconciled with provider invoices monthly.
- **Attribution `[SW]`:** required headers; untagged → 400 in prod; span schema `{team, agent, version, user_hash, model, tokens_in/out, cached, $, latency, tool_calls}` → ClickHouse; dashboards per team/agent/version.
- **Cache `[SW]`:** exact-match keyed by (model, normalized prompt hash, tenant) TTL configurable per agent; prefix/KV caching via provider features; semantic cache off by default (quality risk) — opt-in with eval evidence.
- **Tool registry `[SW]`:** MCP servers registered with schema + auth mode; user-delegated tools require the user's OAuth token forwarded (never a shared service token); central audit of every tool call; allow-lists per agent; schema versioning with deprecation windows.
- **Sessions/memory `[SW]`:** hosted `SessionService` (ADK-compatible) with tenant namespaces, retention/PII policies, export/delete APIs; memory as pgvector per tenant; teams may bring their own.
- **Runtime `[SW]`:** two modes: sync (chat, < 10 s) and jobs (queue, checkpoints, resumable); sandbox pool for code-executing agents; per-agent resource limits; blue/green by agent version.
- **Eval service `[AI]`:** API to register golden sets, run evals on a version, judge with calibrated rubrics (shared κ-validation datasets), CI gate endpoint (`/evals/gate?agent&version` → pass/fail), online sampling of production traces, A/B assignment.
  - **L5:** platform *requires* an eval gate for prod promotion; adoption depends on making it trivial (templates, judge library) not on mandate alone.
- **Policy engine `[SW+AI]`:** central rules: PII redaction on logs, injection classifier on tool outputs (optional per agent), blocked content categories, model allow-list per data classification (e.g., PHI only to approved providers/regions).
- **Versioning `[SW]`:** prompts, model aliases, tool schemas as versioned artifacts; canary by % or user cohort; instant rollback; changelog per agent.

## §6 API / schema
- `POST /v1/chat/completions` (+ headers) · `POST /v1/agents/{id}/runs` · `GET /v1/runs/{id}` · `POST /v1/sessions…` · `GET /v1/tools` · `POST /v1/evals/gate` · `GET /v1/costs?team&period`
- `tenants` · `agents(id, team, versions[])` · `model_aliases(alias, provider, model, fallback[], version)` · `quotas` · `spans` (ClickHouse) · `tools(id, schema, auth_mode, owner)` · `tool_calls_audit` · `sessions/events` · `golden_sets` · `eval_runs` · `policies`

## §7 Hygiene
| Concern | Answer |
|---|---|
| AuthN | service identity (mTLS/OIDC) per team; user identity forwarded for delegated tools |
| Idempotency | run ids; tool audit dedup; gateway retries only idempotent calls |
| Timeouts | per-alias timeouts; streaming keepalive |
| Rate limit | per-team TPM/RPM + $ budgets |
| Breaker/failover | per provider + region; alias fallback chain |
| Backpressure | jobs queue; shed low-priority tenants first (tiers) |
| Consistency | quotas eventually consistent (Redis), reconciled; sessions strong |
| Multi-tenancy | namespace per tenant in DB/cache/memory; noisy-neighbor limits |
| Observability | 100% span capture (sampled bodies), SLOs per alias |
| Deploy | alias/prompt canaries; rollback; changelog |
| Retention/PII | redact-at-ingest; per-tenant retention; delete API |

## §8 Failure → fallback
- Provider outage → alias fallback; degraded banner via header · Quota exhausted → 429 with reset; emergency raise flow · Cache poisoning risk → tenant-scoped keys · ClickHouse lag → spans buffered (Kafka), never block requests · Bad alias deploy → rollback in seconds.

## §9 Pop-up questions
1. **Why not let teams call providers directly?** — Cost blindness, no failover, inconsistent safety, no shared evals; platform must be faster to adopt than DIY.
2. **Buy vs build?** — Gateway: adopt OSS (LiteLLM) and harden; runtime: managed unless multi-cloud/residency; evals: build thin service over Langfuse/OTel.
3. **Team A's prompt change breaks Team B?** — Isolation: per-agent versions, aliases changed only via canaried deploys, no shared mutable prompts.
4. **Cross-tenant leak via cache?** — Tenant in cache key; memory namespaces; tests in CI.
5. **How do you charge back?** — Attribution headers → spans → price table → monthly reconciliation with invoices.
6. **Semantic cache?** — Off by default; opt-in with eval evidence; TTL by freshness class.
7. **L5: ratchet quality org-wide?** — Eval gate required for prod, judge library with calibration sets, dashboards that make regressions visible per team.
8. **L5: 10× calls?** — Gateway horizontally scaled, regional deployments, Kafka for spans, provider quota negotiation, tiered shedding.

## §10 Trade-offs + defeaters
| Decision | Chosen | Alt | Flips |
|---|---|---|---|
| Gateway | OSS + harden | custom | never initially |
| Runtime | managed | self-hosted K8s | multi-cloud / residency |
| Attribution | mandatory headers | best-effort | never |
| Semantic cache | opt-in | default on | strong eval evidence |
- Defeaters: "one super-agent framework everyone must use" · "cache everything semantically" · "platform owns prompts".

## §11 MVP ladder
- MVP0: gateway with aliases, keys, retries, attribution spans; one team migrated.
- MVP1: quotas/budgets, dashboards, provider failover, prompt/alias versioning + rollback.
- MVP2: tool registry (MCP) with delegated auth + audit, session service.
- MVP3: eval service + CI gate, policy engine, jobs runtime with checkpoints.

## §12 Memorization card
- Pitch: one gateway for models, one registry for tools, hosted sessions, evals-as-a-service, all attributed and budgeted per team.
- Level: infra; the "agent" question becomes isolation, attribution, and eval gates.
- Numbers: 5M calls/day · 20 ms overhead · 99.95% · 120% hard stop · 30 d hot traces.
- Failures: cross-tenant leak · alias change breaks everyone · cost with no owner.
- Defeaters: one mandated framework · semantic cache by default · platform owns prompts.
- MVP0→1→2: gateway+attribution → quotas+failover+versioning → tools+sessions.
- Done when: draw control vs data plane · list span schema · argue managed vs self-hosted runtime.

## References
1. https://github.com/BerriAI/litellm
2. https://github.com/modelcontextprotocol (tool registry standard)
3. https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview
4. https://github.com/langfuse/langfuse
5. https://opentelemetry.io/docs/specs/semconv/gen-ai/
