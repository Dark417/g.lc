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
