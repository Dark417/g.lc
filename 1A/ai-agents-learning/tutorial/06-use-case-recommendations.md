# 06 — Use Cases → Architectures (the decision table)

This is the document to keep open when you're scoping a new agent
feature. For each category we list: typical user goal, recommended
**architecture level** (from `04`), recommended **flow** (from `05`),
key non-functional constraints, and the trade-offs you accept.

> Reading guide: pick the row that matches your product, then drop down
> a level if you can. Less is almost always more.

---

## A. Real-time conversational

### A1. Customer support chat (FAQ + account lookups)
- **Level**: 5–6  (RAG + reranker + guardrails + traces)
- **Flow**: 3 (router) → 4 (ReAct) for ticket actions, fallback to human
- **Why**: most questions are FAQs (RAG); some need account tools
  (lookup order, issue refund).
- **Constraints**: <2s first token; PII guardrails; deterministic answers
  for policy questions.
- **Trade-offs**: cheaper router model up front saves cost but adds a
  hop; aggressive caching helps but stale answers hurt trust.

### A2. Sales / lead-qualification bot
- **Level**: 4–5
- **Flow**: 2 (chain) — qualify → score → handoff
- **Why**: structured pipeline; rarely needs free-form tools.
- **Trade-offs**: simpler than support; route to humans early.

### A3. Coding assistant in-IDE (Copilot-style)
- **Level**: 7 (RAG over repo + planner + tools + caching)
- **Flow**: 4 (ReAct) with tight tool budget; 5 for refactors
- **Why**: needs file read/write, search, type-check; speed matters.
- **Trade-offs**: aggressive prompt caching; treat repo as RAG corpus or
  pass code structure via AST/tools, not embeddings only.

### A4. Voice agent (phone / kiosk)
- **Level**: 4–6
- **Flow**: 3 (router) + 4 (ReAct) with very small tool surface
- **Constraints**: <500ms latency budget per turn; streaming TTS; barge-in.
- **Trade-offs**: smaller/faster model (Haiku/Flash); cut RAG depth.

---

## B. Knowledge work & content

### B5. Internal "chat with our wiki/docs"
- **Level**: 5 (hybrid RAG + reranker)
- **Flow**: 1 (single-shot) over retrieved chunks
- **Why**: the boring answer. Don't add agents until users complain RAG
  can't multi-hop.
- **Trade-offs**: re-embed on every doc model change; budget for that.

### B6. Long-form research / analyst report
- **Level**: 9 (durable + planner + multi-agent + RAG)
- **Flow**: 5b (deep research) or 7 (orchestrator-worker)
- **Constraints**: minutes to hours; checkpointing; user can leave and
  come back.
- **Trade-offs**: most expensive class of agent. Strict eval harness.

### B7. Document generation (contracts, RFPs, decks)
- **Level**: 5 + reflection
- **Flow**: 2 (chain: outline→draft→sections→edit) + 6 (reflection)
- **Trade-offs**: templated sections give consistency; reflection catches
  schema violations.

### B8. Summarization / classification at scale
- **Level**: 2–3
- **Flow**: 1 (single-shot), parallelized
- **Why**: workflow not agent. Don't over-build.
- **Trade-offs**: batch APIs (Anthropic, OpenAI) cut cost ~50%.

---

## C. Commerce & transactions

### C9. Shopping / product-discovery assistant
- **Level**: 5–6 (hybrid RAG over catalog + tools)
- **Flow**: 4 (ReAct) with tools: `search_catalog`, `compare`, `add_to_cart`
- **Constraints**: structured outputs for cards; inventory freshness.
- **Trade-offs**: hybrid retrieval matters (SKU codes ≠ semantic); rerank.

### C10. Ordering / booking system (food, travel, scheduling)
- **Level**: 6–7 (tools + memory + guardrails + planner)
- **Flow**: 4 (ReAct) for short, 5 (plan-execute) for multi-leg
  itineraries
- **Constraints**: **idempotent tools**, confirm before `commit_*` calls,
  human-in-the-loop for high-value actions.
- **Trade-offs**: spend the engineering on tool contracts, not on prompt
  cleverness.

### C11. Payments / billing agent
- **Level**: 7 with strict guardrails
- **Flow**: 4 (ReAct) with two-phase commit (preview → confirm)
- **Constraints**: every monetary action needs explicit confirmation;
  log immutably; rate-limit.
- **Trade-offs**: lean toward workflow not agent for anything that
  touches money.

---

## D. Operations & monitoring

### D12. Observability / on-call triage
- **Level**: 6–7 (tools + traces + memory of past incidents)
- **Flow**: 4 (ReAct) with tools for logs/metrics/traces; 6 (reflection)
  to suggest fix.
- **Constraints**: read-only by default; suggest commands, don't run
  destructive ones unattended.
- **Trade-offs**: memory of prior incidents is a huge quality boost.

### D13. Security / SOC alert triage
- **Level**: 7 (RAG over runbooks + tools + multi-agent)
- **Flow**: 7 (orchestrator-worker): triage → enrich → classify → draft response
- **Constraints**: append-only audit trail; no auto-remediation without
  approval.
- **Trade-offs**: false positives are cheap, false negatives are catastrophic
  — tune toward recall.

### D14. DevOps / SRE assistant (infra changes)
- **Level**: 7 + sandbox + durable
- **Flow**: 4 (ReAct) with **dry-run tools** and explicit approval gates
- **Trade-offs**: every `apply` is a planned change; never auto-apply.

### D15. Data / analytics agent ("ask my warehouse")
- **Level**: 6 (RAG over schema + SQL tool + sandbox)
- **Flow**: 4 (ReAct) with retry on SQL error
- **Constraints**: read-only role, query timeouts, row caps, cost guard.
- **Trade-offs**: semantic-layer / metric-store integration > raw SQL.

---

## E. Long-running & autonomous

### E16. Email / inbox agent
- **Level**: 8 (tools + memory + multi-agent: classifier+drafter)
- **Flow**: 8 (multi-agent) or 3 (router)
- **Constraints**: draft-only by default; user confirms send.

### E17. Autonomous research / web crawler
- **Level**: 9 (durable + planner + browser + RAG)
- **Flow**: 5b (deep research)
- **Trade-offs**: needs robust budgets; checkpoint every step.

### E18. Robotic / IoT / embodied agent
- **Level**: 7 + computer-use-style action layer
- **Flow**: 4b (perceive-act) with strict safety envelope.

---

## F. Creative & media

### F19. Image / video generation pipeline
- **Level**: 3–5 (chain through model APIs)
- **Flow**: 2 (chain) + 6 (reflection by judge model)
- **Trade-offs**: deterministic seeds for repro; cache aggressively.

### F20. Game NPC / companion
- **Level**: 6 (memory-heavy)
- **Flow**: 4 (ReAct) with persona prompt + episodic memory
- **Trade-offs**: latency vs depth; tier with cheap model for chit-chat.

---

## Quick selector

```
Is the task one prompt, no tools?          → L1, Flow 1
Same shape every time, several steps?      → L2, Flow 2
Heterogeneous inputs?                      → +Flow 3 (router)
Needs your private knowledge?              → L4–5 (RAG +rerank), Flow 1 or 4
Real users, real money on the line?        → L6 (guardrails+traces+memory)
Decomposable into clear sub-tasks?         → L7, Flow 5 or 7
Distinct roles / personas?                 → L8, Flow 8
Runs >30s and must survive restarts?       → L9, Flow 5b
Ship updates weekly?                       → L10 (eval harness)
```

---

## The honest trade-off summary

| You gain… | You pay… |
|---|---|
| Quality from RAG | Index maintenance, re-embedding, retrieval latency |
| Quality from reranker | One extra API call per query |
| Quality from reflection | 2–3× tokens |
| Adaptability from ReAct | Variable cost & latency, harder eval |
| Decomposition from planner | A planning failure breaks everything downstream |
| Specialization from multi-agent | N× tokens, coordination bugs |
| Durability from async | Operational complexity (queues, workers) |
| Confidence from evals | Engineering time on golden sets |

Next: **MCP, tooling, and where to put configs** in your project. →
`07-mcp-and-config.md`
