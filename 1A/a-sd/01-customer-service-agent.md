# #1 · Customer Service Agent (Amazon-style, autonomous with HITL)

> Prompt: "Design an autonomous support chatbot for an e-commerce site. Orders, refunds, returns, product questions, escalate to a human when needed."
> Full-length version exists (`customer-service-agent-sd.md`). This is the bank card.

## §0 Assumptions
- 50k DAU · 3 sessions/day · 6 turns → 900k turns/day · 10 QPS avg / 50 peak `(assume)`
- p95 TTFT < 1.5 s · p95 turn < 6 s · availability 99.9%
- PII present · refund/cancel are money · human queue exists
- Stack: FastAPI + Google ADK `LlmAgent` · Gemini Flash (Pro on hard turns) · Postgres+pgvector · Redis · Langfuse

## §1 Why an agent `[SW+AI]`
- Baseline: FAQ search + forms + humans. Breaks: free-text intent, one question spans orders+products+payments.
- Model adds: intent/entity extraction, answer synthesis, choosing *which* lookup next.
- **L2 workflow + one L3 step (tool selection).** Trigger: runtime tool sequencing across 3 systems. Not L4: one agent, ~8 tools.
- Cost of wrong: money (refunds) → policy gate in code + HITL.
- **L5:** frame containment rate as the business metric and show the AI metric (task success on golden set) rolls up; pre-empt "why not multi-agent per domain" with tool-count threshold (~15) and isolation need.

## §2 Crux
- Act only on verified data for *this* user; know when to stop and hand off.
- Toy vs trusted: grounded numbers, resumable sessions, idempotent side-effects, fast handoff with context, measured quality.

## §3 NFR / BoE
| NFR | Target | Enforcer |
|---|---|---|
| TTFT / turn | p95 1.5 s / 6 s | streaming, tool timeout 2 s, Flash default |
| Quality | task success ≥ 85% golden; grounded ≥ 95% | CI gate, judge |
| Cost | ≤ $0.01/turn → ~$9k/day | routing, prefix cache, 12k input cap |
| Safety | 0 unverified amounts/order IDs | output grounding check |
| Degrade | model down → smaller model → human queue | breaker |
- Tokens: 8k in / 300 out per turn → 7.5B tokens/day; Flash ≈ $0.3/M in → ~$2.3k in + out ≈ $4k/day `(assume)`.
- So what: Postgres suffices; cost is input-context dominated → cap history, summarize.

## §4 HLD
```
[SW] UI --SSE--> [SW] FastAPI gateway (JWT, rate/token quota, Idempotency-Key, session lock)
                          |
                 [SW+AI] ADK Runner: load session -> input guard -> LlmAgent loop -> output guard -> persist -> stream
                          |                 ^
        [SW] Postgres (sessions, events, tool_calls, memories<pgvector>, approvals)
                          |
   [SW+AI] Tools: get_orders | get_order_detail | get_transactions | search_products | search_history | request_refund(policy) | escalate
                          |
        [SW] RDS read replica | Payments API (idempotent) | Human console (same session)
                          |
   [SW+AI] Langfuse traces -> [AI] eval sampler / judge / golden set
```

## §5 Components — problem → design
- **Gateway `[SW]`:** dup sends → `Idempotency-Key` in Redis 24 h; token burn → 200k tokens/day/user; auth → `user_id` injected into tools, never model-controlled.
- **Session/state/memory `[SW+AI]`:** events (append-only) · state (typed JSONB, Pydantic-validated in `before_agent_callback`) · memory (per-session summary embedded). Rejoin = `GET /sessions/{id}` last 20 events. Concurrency = advisory lock per session, 409 on overlap. Context cap 12k; older turns summarized.
  - **L5:** ADK state is an untyped blackboard — name it and fix it with schema validation; state versioning for prompt migrations.
- **Agent loop `[SW+AI]`:** loop cap 6 tools/turn; Pydantic tool args; tool output wrapped as untrusted data; exit = final text or `escalate`.
- **Data tools `[SW+AI]`:** parameterized SQL with bound `user_id`, not NL2SQL. Read replica, 50-row cap, 2 s timeout. NL2SQL later behind `sqlglot` SELECT-only + views.
- **History RAG `[AI]`:** summaries embedded; `search_history` is a *tool*; `WHERE user_id` in SQL; cite dates.
- **Policy gate `[SW]`:** refund eligibility is a function; ≤ $50 auto, else approval + escalate.
- **Idempotency `[SW]`:** gateway key + `tool_calls.idem_key UNIQUE` + payments key. Never auto-retry side-effects.
- **Guardrails `[SW+AI]`:** input (PII redact, injection classifier), tool boundary (allow-list, schema, cap), output (every number/ID must match a tool result this turn).
- **HITL `[SW]`:** triggers in code; handoff packet = state + 20 events + summary; human reply is an event in the same session; agent paused via `state.escalated`.
- **Evals `[AI]`:** 300-item golden set; CI gate (tool acc ≥ 92%, success ≥ 85%, 0 policy violations); judge κ ≥ 0.7; 5% online sample; canary 10%/48 h.
  - **L5:** eval drift — golden set must be refreshed from escalations monthly; judge re-validated when the judge model changes.

## §6 API / schema (compact)
- `POST /sessions` · `GET /sessions/{id}` · `POST /sessions/{id}/chat` (SSE: token|tool_call|tool_result|final|escalated) · `POST /sessions/{id}/feedback` · `POST /internal/.../human-reply`
- `sessions(id,user_id,state,status)` · `events(session_id,turn_id,author,type,content)` · `tool_calls(idem_key UNIQUE)` · `conversation_memories(user_id,embedding)` · `approval_requests` · `prompt_versions` · `eval_runs` · `feedback`

## §7 Hygiene (where it bites)
| Concern | Answer |
|---|---|
| AuthZ | user_id injected; row filter in SQL |
| Retries | LLM 429/5xx ×3; tools with side-effects never |
| Breaker | Gemini → Flash-Lite → human queue |
| Backpressure | chat sync; summarize/embed/eval async (SQS + DLQ) |
| Cache | FAQ exact-match 1 h; system-prompt prefix cache |
| Deploy | prompts/model IDs versioned rows; canary; rollback = flip |
| PII | redact before trace; DSAR delete by user_id |

## §8 Failure → fallback
- Provider down → smaller model → "queue for human" · Tool timeout → tell user, offer escalate · Retrieval empty → clarify, never invent · Loop cap → forced answer/escalate · Bad args → reject, 1 retry, escalate · Pod dies → turn failed, client replays key.

## §9 Pop-up questions
1. **Why is this an agent at all?** `[SW+AI]` — Only tool selection is agentic; everything around it is a workflow. Trigger is runtime chaining of lookups. Without it, we'd need an intent→flow table that breaks on compound questions.
2. **Two tabs send at once?** `[SW]` — Advisory lock on session; second gets 409 + retry. Events stay linear; no interleaved tool calls.
3. **Retrieval returns the wrong doc with high confidence?** `[AI]` — Output grounding check only accepts IDs/amounts that appear in tool results; history hits carry dates the model must cite; judge samples `grounded`.
4. **Refund executed twice on retry?** `[SW]` — Tool idem key + payments idempotency key; side-effects are not auto-retried.
5. **Prompt injection via product description?** `[SW+AI]` — Tool results wrapped as untrusted; allow-listed tools; side-effects gated by policy code, so an injected "refund everything" cannot execute.
6. **Cost doubles overnight — why?** `[SW+AI]` — Context growth; alert on $/turn, cap input at 12k, summarize, check for loop-cap hits.
7. **How do you know a new prompt is better?** `[AI]` — CI golden gate + 10% canary with containment/CSAT; rollback if −3 pts.
8. **L5: What changes at 10×?** — Read replica sharding by user, session table partitioning by month, Redis for hot session cache, second model provider behind the gateway, dedicated eval cluster.

## §10 Trade-offs + defeaters
| Decision | Chosen | Alt | Flips when |
|---|---|---|---|
| Autonomy | L2+L3 step | full L3/L4 | >15 tools / isolated domains |
| Data access | param tools | NL2SQL | real ad-hoc analytics |
| Vectors | pgvector | Vertex Vector Search | >10M vectors |
| HITL | same-session event | ticket system | helpdesk mandated |
- Defeaters: multi-agent per domain · model writes SQL · fine-tune first.

## §11 MVP ladder
- MVP0: ADK agent + Postgres sessions + 2 read tools + SSE; rejoin works.
- MVP1: idempotency, guardrails, escalate + console, Langfuse.
- MVP2: refund gate, memory RAG, golden set + CI + judge.
- MVP3: canary, cost dashboards, FAQ cache.

## §12 Memorization card
- Pitch: one ADK agent, allow-listed tools, Postgres sessions, code-owned policy gates, human handoff in-session.
- Autonomy: L2 + L3 tool selection; trigger = runtime chaining across 3 systems.
- Numbers: 50 QPS peak · TTFT 1.5 s · 6-tool cap · $50 gate · κ 0.7.
- Failures: double refund · lost session · ungrounded numbers.
- Defeaters: multi-agent · NL2SQL · fine-tune.
- MVP0→1→2: grounded answer + rejoin → idempotency+guard+HITL → refund gate+memory+evals.
- Done when: draw HLD in 4 min · explain events/state/memory · list HITL triggers.

## References
1. https://github.com/google/adk-python
2. https://google.github.io/adk-docs/sessions/
3. https://github.com/pgvector/pgvector
4. https://langfuse.com/docs/integrations/google-adk
