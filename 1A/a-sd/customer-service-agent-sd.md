# Customer Service Agent — System Design (Google ADK + FastAPI)

> Scope: one chatbot surface, one agent, boring infra. Every module = *problem → how the design solves it*.
> Tags: `[SW]` software/infra · `[AI]` model/prompt/retrieval/eval · `[SW+AI]` boundary.

---

## 0 · Assumptions (say these first)

| Question | Assumed answer | Why it matters |
|---|---|---|
| Scale | 50k DAU, 3 sessions/user/day, 6 turns/session → ~900k turns/day, ~10 QPS avg, ~50 QPS peak `(assume)` | Single Postgres + pgvector is fine; no vector DB |
| Domain | E-commerce: orders, refunds, shipping, product questions | Tools are read-heavy + 2 side-effecting actions |
| Latency class | Chat: p95 TTFT < 1.5 s, p95 full turn < 6 s | Streaming mandatory; tool calls must be fast |
| Cost of wrong | Wrong refund = money; wrong product answer = churn | Refund/cancel gated by policy + human |
| HITL allowed | Yes, human queue exists | Escalation is a first-class path, not a fallback |
| Data sensitivity | PII (name, address, order history) | Row-level auth on every tool; redact in logs |
| Build vs buy | Model via Gemini API; framework ADK; run on our infra | No Vertex Agent Engine yet — keep portability |

---

## 1 · Why an agent, which rung `[SW+AI]`

- **Without LLM:** FAQ search + web forms + human queue. Breaks because users describe problems in free text and one question spans 3 systems (orders + products + payments).
- **What the model adds:** intent understanding, entity extraction (which order?), answer synthesis, deciding *which* lookup comes next.
- **Autonomy ladder:**
  - `L0` no model · `L1` single call · `L2` workflow (code picks flow, LLM fills steps) · `L3` agent (model picks tool sequence) · `L4` multi-agent
- **Choice: L2 workflow with one L3 agentic step.**
  - Outer flow is code: `auth → load session → guardrail in → agent turn → guardrail out → persist → stream`
  - Inside "agent turn", the model picks tools (`get_orders`, `get_order_detail`, `search_products`, `search_history`, `request_refund`, `escalate`) because the tool sequence is not known at design time.
- **Trigger for L3:** open-ended tool sequencing across 3 systems. No trigger for L4 — one agent, more tools. Add a second agent only if the tool set exceeds ~15 or a domain needs isolated instructions.
- **Cost of wrong → HITL gates:** any side-effect above policy threshold (refund > $50, cancel after ship) → human; any turn where confidence/tools fail twice → human.

**One sentence:** *"This is an L2 workflow with one L3 agentic step at tool selection, because which lookups to chain is only known at runtime."*

---

## 2 · Crux

- **Hard part:** the agent must act only on *verified* data for *this* user, and must know when to stop and hand off. Everything else is plumbing.
- Critical success points:
  - Tool results are the only source of facts; the model never guesses an order number.
  - Session state survives reconnects and pod restarts.
  - Side-effects are idempotent.
  - Escalation is fast and carries full context to the human.
  - Quality is measured, not felt (golden set + judge + CSAT).
- **Business metric:** containment rate (resolved without human) × CSAT. AI metric (task success on golden set) rolls up into containment.

---

## 3 · High-level design `[SW+AI]`

```
 [SW] Web/Mobile chat UI  ──SSE──┐
                                 ▼
 [SW] FastAPI gateway  (authN, rate limit, idempotency key, session resolve)
        │
        ▼
 [SW+AI] Orchestrator (ADK Runner)  ──── one turn = one run ────┐
   1. load Session (events + state) ◄────────────────────────── [SW] Postgres
   2. input guardrail (regex/PII/injection classifier)                  sessions, events, state
   3. LlmAgent loop:                                                     tool_calls, evals, feedback
        model ──► tool call ──► tool result ──► model ... (max N)
             ▲                    │
             │       [SW+AI] Tools (FunctionTool, allow-listed)
             │         ├─ get_orders / get_order_detail   → [SW] RDS (orders, txns)
             │         ├─ search_products                 → [SW] RDS (commodities) + pgvector
             │         ├─ search_history                  → [AI] pgvector (past conversations)
             │         ├─ request_refund (policy gate)     → [SW] Payments API (idempotent)
             │         └─ escalate                        → [SW] Human queue
   4. output guardrail (grounding check, PII, tone)
   5. append events, persist state, stream tokens
        │
        ▼
 [SW+AI] Langfuse traces (span per LLM/tool call, tokens, $)  ──► [AI] eval pipeline (judge, golden set)
        │
        ▼
 [SW] Human agent console  (reads same session, replies into same event log)
```

**One turn, end to end:**
1. UI POSTs `/chat` with `session_id`, `message`, `Idempotency-Key`.
2. Gateway checks JWT, rate limit, dedups by key.
3. Runner loads session (last 20 events + state dict) from Postgres.
4. Input guardrail runs; blocked → canned response, event logged.
5. Agent loop: model → `get_orders(user_id)` → model → `get_order_detail(order_id)` → model answer.
6. Output guardrail; persist events; stream via SSE.
7. Trace lands in Langfuse; async sampler queues 5% for judge eval.

---

## 4 · Modules — problem → design

### 4.1 Gateway `[SW]`
- **Problems:** duplicate sends on flaky mobile networks; one user burning tokens; unauthenticated tool access.
- **Design:**
  - `Idempotency-Key` header (client UUID per send). Gateway stores `key → response` in Redis, TTL 24 h. Replay returns stored response, no second run.
  - Token bucket per user: 30 msgs/min **and** 200k tokens/day. Token quota matters more than QPS.
  - JWT → `user_id`; injected into every tool call as a non-model parameter (model never sees or sets it).

### 4.2 Session, state, memory `[SW+AI]`
- **Three things people conflate — keep them separate:**

| Thing | What | Where | Lifetime |
|---|---|---|---|
| Session events | Append-only log of user/model/tool events (ADK `Event`) | Postgres `events` via `DatabaseSessionService` | Session |
| Session state | Small dict: `current_order_id`, `intent`, `escalated`, `turn_count` | Postgres `sessions.state` (JSONB) | Session; `user:` prefix persists across sessions |
| Long-term memory | Past conversation summaries, embedded | pgvector `conversation_memories` | Months |

- **Problems:** pod restart mid-chat; user closes tab and returns; two tabs open; state drift between replicas.
- **Design:**
  - **Persistence:** `DatabaseSessionService(db_url=POSTGRES)` — every event written before streaming the final token. Pod dies → next turn reloads from DB. No in-process state.
  - **Rejoin:** UI stores `session_id`. `GET /sessions/{id}` returns last 20 events + state; UI renders them; next `/chat` continues. Session considered "resumable" for 24 h idle, then closed and summarized into memory.
  - **Sync / concurrency:** one Postgres advisory lock per `session_id` during a run. Second concurrent turn on the same session → `409` with `retry_after`. Two tabs cannot interleave tool calls.
  - **Context assembly (what the model sees):** system prompt + `state` summary (3 lines) + last 20 events + memory hits (top-3, only if user query looks like it refers to past events). Hard cap 12k input tokens; older events summarized by a cheap model into a `state["summary"]`.
  - **ADK gotcha (name it):** state is an untyped shared dict. Enforce a Pydantic `SessionState` model in `before_agent_callback`; reject malformed writes. Tools write via `tool_context.state[...]`, never directly.

### 4.3 Agent loop `[SW+AI]`
- **Problems:** infinite tool loops; hallucinated tool args; model calls a tool that doesn't exist; runaway cost.
- **Design (ADK `LlmAgent`, Gemini 2.5 Flash, Pro on escalation-candidate turns):**
  - `max_tool_calls_per_turn = 6` in `before_tool_callback` — 7th call → force answer or escalate.
  - Tool schemas are Pydantic; ADK validates args before execution. Bad args → tool returns error string, model retries once, then escalates.
  - Every tool result is truncated to 2k tokens and wrapped: `<tool_result name=.. trusted=false>` — model is told tool content is data, not instructions.
  - Loop exit = model emits final text with no tool call, or `escalate` tool sets `EventActions(escalate=True)`.
  - `temperature=0.2`; tool choice `auto`; no free-form JSON parsing — ADK function calling only.

### 4.4 Data access tools — "generate queries for RDS" `[SW+AI]`
- **Pushback:** free-form text-to-SQL against the transactions DB is the wrong default.
  - Risks: `WHERE user_id` omitted → data leak; `DELETE`; slow scans; non-deterministic tests.
- **Design: parameterized tools first, NL2SQL last.**
  - `get_orders(status?, since?)` · `get_order_detail(order_id)` · `get_transactions(order_id)` · `search_products(query, category?)`
  - Each tool = a fixed SQL statement with bound params + mandatory `user_id` from context. Read replica. Row limit 50. Statement timeout 2 s.
  - Model picks the tool and fills params; it never writes SQL.
  - **If** product questions genuinely need ad-hoc analytics (rare in support), add `run_readonly_sql(sql)` later:
    - read-only DB role, single schema of views with `user_id` filter baked in
    - `sqlglot` parse → allow only `SELECT`, single statement, `LIMIT ≤ 100`
    - result-set caps, 2 s timeout
- **Product search:** keyword on `products` first (Postgres `tsvector`). Add pgvector on product descriptions only if keyword misses > 20% on golden set.

### 4.5 RAG over conversation history `[AI]`
- **Problems:** "same issue as last week" — model has no idea; injecting all history blows context; retrieving another user's history.
- **Design:**
  - On session close: cheap model writes a ≤150-word summary (`issue, resolution, open items, order_ids`). Embed (`text-embedding-004`, 768-d). Store in `conversation_memories(user_id, session_id, summary, embedding, created_at)`.
  - `search_history(query)` tool: `WHERE user_id = :uid ORDER BY embedding <=> :q LIMIT 3` — user filter in SQL, not in prompt. HNSW index on `embedding`, partial index per tenant if multi-tenant.
  - Retrieval is a *tool the model calls*, not always-on injection. Cheaper, and the trace shows when it was used.
  - Return summaries with dates; the model must cite the date when referencing past issues (checked by output guardrail).

### 4.6 Decisions & policy gate `[SW+AI]`
- **Problem:** model "decides" a refund is fine; it isn't.
- **Design:** decisions with money attached are **code, not prompt**.
  - `request_refund(order_id, amount, reason)` → policy function: `eligible = within_30d and not_shipped_or_returned and amount <= order_total`.
  - `amount ≤ $50 and eligible` → execute. Otherwise → create `approval_request`, tell user "sent to a specialist", escalate.
  - Model's job: collect `order_id`, `reason`; explain outcome. Not: judge eligibility.

### 4.7 Idempotency `[SW]`
- **Where it bites:** retried `request_refund` = double refund.
- **Design:**
  - Tool-level key: `sha256(session_id, turn_id, tool_name, canonical_args)`. Stored in `tool_calls(idem_key UNIQUE)`. Replay returns stored result.
  - Payments API called with the same key as `Idempotency-Key` (Stripe-style).
  - Retries: LLM calls retry on 429/5xx, max 3, backoff + jitter. Side-effecting tools: never auto-retried; failure → tell user, log, escalate if needed.

### 4.8 Guardrails `[SW+AI]`
- **Input (`before_model_callback`):** PII regex redact for logs; prompt-injection classifier (small model, p95 < 100 ms); off-topic → canned redirect. Blocked turn still logged as event.
- **Tool boundary (`before_tool_callback`):** allow-list; arg schema; `user_id` injected; loop cap.
- **Output (`after_model_callback`):** every order/amount/date in the answer must appear in a tool result this turn (string match on structured fields) — mismatch → regenerate once, then escalate. Refusal template for legal/medical/threat topics.
- Rule: mechanical gates before prose rules. Prompt says "be helpful"; code says "no unverified numbers".

### 4.9 Human-in-the-loop `[SW]`
- **Triggers (code, not vibes):** `escalate` tool called · 2 tool failures in a turn · loop cap hit · policy gate denied · user says "human/agent/person" (regex) · sentiment classifier < threshold twice.
- **Handoff packet:** state dict + last 20 events + summary + open `approval_request`. Written as an event; human console reads the same session.
- Human reply is appended as an `author=human` event; agent is paused (`state["escalated"]=true`) until human releases. Same session, same log — no context re-entry.
- SLA: human pickup p50 < 2 min during hours; outside hours → ticket + email.

### 4.10 Evals `[AI]`
- **Golden set:** 300 conversations, labeled `expected_tools`, `expected_outcome`, `must_not_say`. Grows from escalations and thumbs-down.
- **Offline CI gate (every prompt/model/tool change):** tool-selection accuracy ≥ 92%, task success ≥ 85%, zero policy violations, p95 cost/turn ≤ budget. Fails → PR blocked.
- **LLM-as-judge:** Gemini Pro grades `grounded / helpful / policy_ok`. Validated on 200 human-labeled turns; ship only if Cohen's κ ≥ 0.7; re-validate monthly.
- **Online:** 5% sampled turns → judge; CSAT thumbs; containment rate dashboard. Canary new prompt on 10% for 48 h; auto-rollback if containment drops > 3 pts.
- Eval records are a table (`eval_runs`, `eval_results`), not a notebook.

### 4.11 Observability `[SW+AI]`
- Langfuse: trace per turn; span per LLM call (tokens in/out, $, latency), per tool (args hash, latency, error).
- Alerts: p95 TTFT > 2 s · tool error rate > 5% · escalation rate > 25% · $/turn > 2× baseline · judge `grounded` < 90% on daily sample.

---

## 5 · API `[SW]`

| Method | Path | Notes |
|---|---|---|
| `POST /sessions` | → `{session_id}` | JWT → user_id; creates row |
| `GET /sessions/{id}` | → `{state, events[-20:]}` | Rejoin |
| `POST /sessions/{id}/chat` | body `{message}`, header `Idempotency-Key` | SSE stream of `token / tool_call / tool_result / final / escalated` events |
| `POST /sessions/{id}/feedback` | `{turn_id, score, comment}` | Feeds eval |
| `POST /internal/sessions/{id}/human-reply` | human console | Appends event, releases agent |

- ADK ships `get_fast_api_app()`; use it for MVP0, wrap it with your gateway middleware (auth, idempotency, quotas) as you grow.

---

## 6 · Schema `[SW]` `[SW+AI]`

```
sessions(id, user_id, state JSONB, status, created_at, updated_at, closed_at)      idx(user_id, updated_at)
events(id, session_id, turn_id, author, type, content JSONB, tokens, created_at)   idx(session_id, id)
tool_calls(id, session_id, turn_id, tool, args JSONB, result JSONB, idem_key UNIQUE, latency_ms, error)
conversation_memories(id, user_id, session_id, summary, embedding vector(768), created_at)  hnsw(embedding)
approval_requests(id, session_id, type, payload JSONB, status, assignee, decided_at)
prompt_versions(id, name, version, text, model, created_at)   -- prompts are deployables
eval_runs(id, prompt_version_id, golden_set_version, metrics JSONB, passed)
feedback(id, session_id, turn_id, score, comment)
```
- One Postgres (RDS, multi-AZ). pgvector extension. Read replica for tool queries.
- Retention: events 90 d, memories 12 m, traces 30 d. PII redacted before Langfuse.

---

## 7 · Hygiene table `[SW]`

| Concern | Answer |
|---|---|
| AuthN/Z | JWT at gateway; `user_id` injected into tools; row-level filter in SQL |
| Idempotency | Gateway key (Redis) + tool key (Postgres UNIQUE) + payments key |
| Timeouts/retries | LLM 30 s, tool 2 s, retry 429/5xx ×3; no retry on side-effects |
| Rate limit | 30 msg/min, 200k tokens/day per user |
| Circuit breaker | Gemini breaker → fallback Flash-Lite → "try again shortly" + escalate option |
| Backpressure | Chat is sync (< 6 s). Summarization, embedding, evals are SQS jobs, DLQ |
| Caching | Exact-match answer cache for FAQ intents (TTL 1 h); prefix cache on system prompt |
| Consistency | Strong for sessions/tool_calls; eventual for memories index |
| Partitioning | By `user_id`; hot = last 24 h sessions |
| Failover | RDS multi-AZ, RPO ~0, RTO < 5 min; provider failover is Flash-Lite, not a second vendor (MVP) |
| Deploy | Prompts + model IDs in `prompt_versions`, canary 10% → 100%; rollback = flip row |
| PII | Redact before log/trace; encrypt at rest; DSAR = delete by user_id |

---

## 8 · Failure modes → fallback `[SW+AI]`

| Failure | Fallback |
|---|---|
| Gemini down | Breaker → smaller model; if both down → "queue me for a human" |
| Tool timeout | Tell user which system is slow; offer escalate; no silent retry |
| Retrieval empty | Model says it found nothing, asks a clarifying question — never invents |
| Loop runaway | Cap at 6; forced answer or escalate; alert on cap rate > 2% |
| Hallucinated args | Pydantic reject → one retry → escalate |
| Grounding check fails | Regenerate once → escalate |
| Duplicate send | Idempotency replay |
| Pod dies mid-turn | Turn marked failed; UI retries with same key; session reloads from DB |

---

## 9 · Trade-offs

| Decision | Chosen | Alternative | Flips when |
|---|---|---|---|
| Autonomy | L2 + one L3 step | Full L3 / L4 | > 15 tools or isolated domains |
| Data access | Parameterized tools | NL2SQL | Genuine ad-hoc analytics need |
| Vector store | pgvector | Vertex Vector Search | > 10M vectors or < 50 ms p99 needed |
| Session store | Postgres `DatabaseSessionService` | Vertex Agent Engine sessions | Going all-in on Vertex managed runtime |
| Memory | Summaries per closed session | Raw-turn embeddings | Need turn-level recall (rare) |
| HITL | Same session, human event | Separate ticket system | Existing helpdesk is mandatory |

**Defeaters (wrong framings):**
- "Use multi-agent per domain" → one agent + tools is simpler, cheaper, and easier to eval; split only on tool count or isolation.
- "Let the model write SQL" → leaks and non-determinism; parameterized tools solve 95%.
- "Fine-tune for accuracy" → errors are retrieval/tool/prompt errors; fix those first, measure, then consider.

---

## 10 · MVP ladder

- **MVP0 (week 1):** FastAPI + ADK `LlmAgent` + `DatabaseSessionService` on Postgres + `get_orders`, `get_order_detail` + SSE. Demo: ask about an order, get grounded answer, close tab, reopen, continue.
- **MVP1:** idempotency (gateway + tools), input/output guardrails, `escalate` tool + human console, Langfuse.
- **MVP2:** `request_refund` with policy gate, session summarization + pgvector `search_history`, golden set + CI gate + judge.
- **MVP3:** canary/rollback for prompts, cost dashboards, FAQ cache, sentiment trigger.

---

## 11 · Memorization card

- **Pitch:** One ADK agent with allow-listed tools over orders/products/history, persisted sessions in Postgres, code-owned policy gates, human handoff in the same session.
- **Autonomy:** L2 workflow, one L3 step at tool selection — trigger: runtime tool sequencing across 3 systems.
- **5 numbers:** 50 QPS peak · p95 TTFT 1.5 s · 6 tool calls/turn cap · $50 refund gate · κ ≥ 0.7 judge.
- **3 failure modes:** double refund · stale/lost session · ungrounded numbers.
- **3 defeaters:** multi-agent by default · model writes SQL · fine-tune first.
- **MVP0 → 1 → 2:** grounded order answer + rejoin → idempotency + guardrails + HITL → refund gate + memory + evals.
- **Done when:** draw the diagram in 4 min · explain state vs events vs memory without notes · list every HITL trigger from memory.

---

## References

1. ADK Python repo — `google/adk-python` (sessions, `DatabaseSessionService`, callbacks, `get_fast_api_app`): https://github.com/google/adk-python
2. ADK docs — Sessions, State, Memory: https://google.github.io/adk-docs/sessions/
3. ADK docs — Callbacks (guardrail hooks): https://google.github.io/adk-docs/callbacks/
4. pgvector: https://github.com/pgvector/pgvector
5. Langfuse ADK integration: https://langfuse.com/docs/integrations/google-adk
