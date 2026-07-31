# 04 — Architecture Combinations (from 1 component up to 8+)

Now we *compose*. Each level adds one capability. You should be able to
look at any product and say "that's a level-4 with hybrid retrieval" or
"that's a level-7 multi-agent." Stop climbing the ladder the moment your
problem is solved — every level adds latency, cost, and failure modes.

Notation: **`[LLM][Ctrl][Tools][Embed][VDB][Docs][Reranker][Mem][Plan][Eval][Guard][Trace][Async]`** — drop what you don't use.

---

## Level 1 — Pure LLM call
**`[LLM]`**
A single prompt → response. No tools, no memory, no retrieval. Examples:
spam classifier, summarizer endpoint.
- Latency: 1 RTT. Cost: lowest. Failure modes: hallucination, drift.
- Skip everything above this when the task is "one prompt does it."

## Level 2 — LLM + Controller
**`[LLM][Ctrl]`**
Add a loop with retries, timeouts, prompt templating, structured output
parsing. Now it's a *service*, not a script. The smallest "real" deploy.

## Level 3 — Tool-using agent (the MVP)
**`[LLM][Ctrl][Tools]`**
The model can call functions. ReAct or single-tool-call works here.
This is where most product features live: "AI that books a meeting,"
"AI that summarizes my Stripe data."
- *First* place to add: observability/tracing — debugging is impossible without it.

## Level 4 — Tool-using agent + RAG
**`[LLM][Ctrl][Tools] + [Embed][VDB][Docs]`**
Add retrieval over your own corpus. The agent answers questions about
*your data*. This is "chat with your docs" territory.
- Start with naive RAG. Add hybrid retrieval before adding more layers.

## Level 5 — + Reranker & hybrid retrieval
**`L4 + [Reranker]`** (and BM25 alongside vector)
Single biggest quality jump for RAG. Cheap to bolt on. Do this before
fancy paradigms.

## Level 6 — + Memory & guardrails (productionization)
**`L5 + [Mem][Guard][Trace][Cache]`**
Long-term memory per user, input/output filters, prompt-prefix cache,
real tracing dashboards. The system now survives contact with real
users.

## Level 7 — + Planner / multi-step agent
**`L6 + [Plan]`** (Plan-and-Execute, or Orchestrator-Worker)
For tasks that need 3+ tool calls in a non-trivial order. The planner is
either a dedicated prompt or a separate cheap model. Add only when L6
plateaus — planners are a common over-engineering trap.

## Level 8 — + Multi-agent / role specialization
**`L7 + multiple agents`** (researcher / coder / reviewer)
Different prompts, different tools per role, a coordinator that routes
or hands off. Use when one prompt is doing too many jobs and bloats.
Beware: token costs multiply.

## Level 9 — + Async / durable execution
**`L8 + [Async]`** (Temporal/Inngest, queues, checkpoints)
For agents that run minutes-to-hours. Required for deep research,
overnight batch agents, anything that survives a server restart.

## Level 10 — + Evaluation harness as a first-class system
**`L9 + [Eval]`** (golden sets, LLM-judge, regression suite in CI)
At this point you ship prompt/model changes weekly and can't trust
"feels better." Evals become the merge gate.

---

## Visualizing the climb

```
L1  prompt
L2  prompt + loop
L3  prompt + loop + tools                    ← MVP
L4  L3 + retrieval (RAG)                     ← "chat my docs"
L5  L4 + hybrid + rerank                     ← quality production RAG
L6  L5 + memory + guardrails + traces        ← real users
L7  L6 + planner                             ← complex multi-step
L8  L7 + multi-agent
L9  L8 + durable async                       ← long-running
L10 L9 + eval harness                        ← weekly shipping
```

## Anti-patterns when combining

- **Multi-agent before you need it.** Two agents talking to each other
  burns tokens for no quality gain on simple tasks.
- **Vector DB before you need it.** If your knowledge fits in a 200KB
  markdown file, just paste it (or use prompt caching).
- **Planner without observability.** You will not be able to debug
  failed plans without traces.
- **GraphRAG / advanced RAG before reranker.** Try the boring fix first.
- **Skipping guardrails for "internal" tools.** Internal users prompt-inject too.
- **No eval harness with frequent model swaps.** You can't tell if your
  swap from Sonnet to Haiku regressed unless you measured.

## Cost & latency intuition

Each level roughly multiplies cost and latency. A user-facing chat at L8
might cost 20–100× a single L1 prompt and take 5–30s instead of 1s.
That's fine when it's the right tool, ruinous when it isn't.

Next: the **agent flow** loop itself, in detail. → `05-agent-flows.md`
