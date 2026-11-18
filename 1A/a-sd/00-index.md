# Agentic AI System Design Bank — Index

> 10 systems, chosen for (a) how often they are asked in Applied-AI loops and (b) how much of the agent surface they cover (tools, memory, HITL, long-running jobs, real-time, safety, platform).
> Each doc: assumptions → autonomy ladder → crux → NFR/BoE → HLD → components (problem → design) → API/schema → hygiene → failure modes → pop-up questions → trade-offs/defeaters → MVP ladder → memorization card → references.
> `[SW]` software · `[AI]` model/retrieval/eval · `[SW+AI]` boundary. `L5:` lines mark senior extensions.
>
> **Compression note:** these are ~1,800-word "bank" versions, not the 5–8k-word full template. Use `Generate #N` in a fresh chat for the long form; use `Drill #N` to be grilled.

| # | System | Prompt as asked | Why it's in the bank | Autonomy |
|---|---|---|---|---|
| 1 | Customer service agent (Amazon-style) | "Design an autonomous support chatbot for an e-commerce site: orders, refunds, product Qs, escalate to human." | Canonical. Tools + sessions + policy + HITL. | L2 + L3 step |
| 2 | Enterprise knowledge assistant | "Design an internal assistant over Confluence/Drive/Slack/Jira that respects permissions and can take actions." | Permission-aware RAG, freshness, actions. | L2 + L3 step |
| 3 | Data analyst agent (NL → SQL → chart) | "Design a chat-to-BI agent over the warehouse for business users." | Text-to-SQL, verification, semantic layer. | L3 |
| 4 | Coding agent (issue → PR) | "Design an agent that takes a GitHub issue and opens a tested PR." | Sandboxes, long loops, verification-by-execution. | L3 |
| 5 | Real-time voice agent | "Design a phone agent that books/reschedules appointments." | Latency budget, barge-in, streaming, telephony. | L2 + L3 step |
| 6 | Deep research agent | "Design an agent that researches a topic for 20 min and writes a cited report." | Long-running jobs, planning, citation grounding. | L3 (bounded L4) |
| 7 | Browser / computer-use agent | "Design an agent that completes web tasks (fill forms, book travel) on sites with no API." | Perception-action loop, safety, irreversibility. | L3 |
| 8 | Document workflow agent (claims / invoices) | "Design an agent that processes insurance claims end-to-end with human review." | Extraction + rules + HITL queues; workflow > agent. | L2 |
| 9 | SRE / incident response agent | "Design an on-call agent: alert → diagnose → propose/execute runbook." | Read-only autonomy, gated actions, blast radius. | L3 read / L2 write |
| 10 | Agent platform (gateway + runtime) | "Design the internal platform 30 teams use to build, run, eval, and pay for agents." | Multi-tenancy, cost, evals-as-a-service, versioning. | n/a (infra) |

## Cross-cutting patterns (learn once, reuse)

- **Autonomy ladder:** L0 no model → L1 single call → L2 workflow (code picks flow) → L3 agent (model picks tools) → L4 multi-agent. Always name the trigger for each rung up.
- **Three state kinds:** append-only event log · small typed state dict · long-term memory (summaries, embedded). Never conflate.
- **Three idempotency layers:** client key at gateway · tool key on side-effects · downstream API key.
- **Mechanical gates before prose rules:** schema validation, allow-lists, budget caps, grounding checks in code.
- **HITL triggers are code:** side-effect above threshold · N tool failures · loop cap · user asks · low-confidence classifier.
- **Evals are a component:** golden set table + judge validated with κ ≥ 0.7 + CI gate + online sample.
- **Long-running = job, not request:** > ~5 s → queue, checkpoint, resumable, SSE/WebSocket for progress.
- **Cost question always:** tokens/turn × turns/day × $/token; name the 2 levers (routing, caching).

## Drill order (recommended)

1 → 3 → 2 → 5 → 4 → 8 → 9 → 6 → 7 → 10. Start with the two you can build from your stack today; end with platform.

## Concept docs behind each design (added 2026-11-16)

- **How the two folders differ**
  - `a-md/` = component knowledge: how each part works and how to choose it.
  - `a-sd/` = applied designs: one system end to end, with numbers, in interview order.
  - Read the a-md docs first, then drill the design.

| # | Design | Read first in `../a-md/` |
|---|---|---|
| 1 | Customer service agent | 1harness, 1loop, 0edge-com §6, 4guardrails, 4access |
| 2 | Enterprise knowledge assistant | 3rag (handbook), 4access §2–3, 4security §6 |
| 3 | Data analyst agent | 4guardrails, 4security §2 (output handling), 6cost-latency |
| 4 | Coding agent | 5claude-sdk, 4access §6 (sandbox), 6durable, 4evals |
| 5 | Voice agent | 0edge-com, 6cost-latency §3, 2models |
| 6 | Deep research agent | 1orchestration, 6durable, 4evals |
| 7 | Browser agent | 4access, 4security, 4guardrails |
| 8 | Document workflow agent | 1graph, 6durable, 4access §4 |
| 9 | SRE incident agent | 4access, 4observability, 6durable |
| 10 | Agent platform | 1architecture, 5frameworks, 6llmops, 6cost-latency, 4observability, 7serving |

- **Updates these designs still need** (they predate the 2026-11-16 docs)
  - Treating the run separately from the client connection: event IDs, replay, cancel ([0edge-com](../a-md/0edge-com.md)).
  - Back-of-envelope from users to tokens per minute ([1architecture §7](../a-md/1architecture.md)).
  - A dedicated harness service, with gRPC or A2A between agent services ([1architecture §6](../a-md/1architecture.md)).
