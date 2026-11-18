# 6cost-latency — Cost And Latency Engineering For Agents

> Where an agent's time and money go, the levers that cut them, and how to budget and attribute spend.
> Group 6 (production). Related: [2models.md](2models.md), [1architecture.md](1architecture.md) §7, [4observability.md](4observability.md).
> Concept level, no code (AGENTS.md §8b). Last updated: 2026-11-16. Numbers are order of magnitude unless cited.

## Index
- [0. One-minute version](#0-one-minute-version)
- [1. Concept: two formulas](#1-concept-two-formulas)
- [2. Cost levers](#2-cost-levers)
- [3. Latency levers](#3-latency-levers)
- [4. Worked example: cutting cost 5×](#4-worked-example-cutting-cost-5)
- [5. Budgets, quotas and attribution](#5-budgets-quotas-and-attribution)
- [6. Caching beyond the prompt](#6-caching-beyond-the-prompt)
- [7. System design view: choosing](#7-system-design-view-choosing)
- [8. Failure modes](#8-failure-modes)
- [Where this fits](#where-this-fits)
- [References](#references)

---

## 0. One-minute version
- **What:** agent cost is tokens × price × steps; agent latency is steps × (model time + tool time).
- **Why:** both multiply with steps, and loop cost grows faster than linearly because each step resends history.
- **How:** fewer steps, smaller models where they pass, cached prefixes, trimmed context, parallel tools, streaming.
- **Catch:** each lever can cost quality. Every change goes through the eval gate with cost and latency tracked beside quality.
- 🗣 "Cost and latency both scale with steps. The first lever is fewer steps, then smaller models, then caching."

---

## 1. Concept: two formulas
`boundary` ★★★

- **Cost per task** = Σ over steps (input tokens × input price + output tokens × output price), minus cache discounts, plus tool and infrastructure costs.
- **Latency per task** = time to first token + Σ over steps (model time + tool time), minus whatever runs in parallel.
- **Picture it:** a five-step agent.
  - Each model step: ~1.5 s; each tool: ~0.5 s. Five steps ≈ 10 s.
  - Each step resends history; step 5 sends far more tokens than step 1.
- **Why loop cost is quadratic:** if each step adds about 2k tokens, ten steps send roughly 140k input tokens in total, not 50k ([1aa-msg.md](1aa-msg.md) §6).
- **What users feel:** time to first visible progress, not total time. Streaming and progress events change perceived latency without changing cost.
- 🗣 "Users feel time to first token; finance feels tokens per task. I design for both."

---

## 2. Cost levers
`boundary` ★★★

| Lever | Mechanism | Typical saving | Risk |
|---|---|---|---|
| Fewer steps | workflow instead of loop for known paths; better tools that do more per call | large | less flexibility |
| Smaller model per step | route easy steps to cheaper tiers ([2models.md](2models.md)) | large on easy traffic | quality on edge cases |
| Prompt caching | stable prefix billed at a discount | large for long system prompts and tool lists | cache breaks if prefix changes |
| Context trimming | summarize old turns; prune tool results to pointers; cap retrieved chunks | medium to large | lost detail |
| Fewer tools in the prompt | send a relevant subset; tool search | medium | wrong tool missing |
| Output limits | cap output tokens; concise formats | small to medium | truncated answers |
| Reasoning effort | lower thinking budget on easy steps | medium | worse on hard steps |
| Batch for offline | batch APIs at a discount | about half on that work | hours of delay |
| Result caching | reuse answers to repeated questions ([§6](#6-caching-beyond-the-prompt)) | depends on repeat rate | stale or wrong reuse |

- **Order to try:** fewer steps, caching, trimming, smaller models, then the rest. The first three rarely hurt quality.

---

## 3. Latency levers
`boundary` ★★★

| Lever | Mechanism | Helps | Risk |
|---|---|---|---|
| Streaming | show tokens as they arrive | perceived latency | none for cost |
| Progress events | show tool steps ("checking order…") | perceived latency | UI work |
| Parallel tool calls | independent reads at once | real latency | ordering bugs on writes |
| Fewer steps | as above | real latency | flexibility |
| Smaller, faster models | fast tier for easy steps | real latency | quality |
| Prompt caching | faster first token on cached prefixes | real latency | as above |
| Tool speed | timeouts, caching, read replicas | real latency | staleness |
| Speculative work | start likely next steps early; discard if unused | real latency | wasted tokens |
| Region and provider | call the closest region | network time | data residency |

- **Latency budget example (voice agent):** users notice pauses beyond roughly a second, so voice designs budget every hop and avoid multi-step loops in the hot path. Chat tolerates more, with streaming.
- 🗣 "Stream for perceived speed, parallelize for real speed, and cut steps for both."

---

## 4. Worked example: cutting cost 5×
`boundary` ★★★

- **Start (assumptions):** a support agent, 6 steps per task, 10k input tokens per step on average, frontier model for every step, no caching.
  - Input per task ≈ 60k tokens; call that 1.0 unit of cost.
- **Changes, each measured on the eval set**
  1. Move the fixed "look up order, check policy" path into a workflow: 6 steps become 3. Cost ≈ 0.5.
  2. Order the prompt for caching; 6k of each 10k is a stable prefix billed at about a tenth. Cost ≈ 0.5 × (0.4 + 0.6 × 0.1) ≈ 0.23.
  3. Route two of three steps to a mid-tier model priced at about a fifth. Cost ≈ 0.23 × (1/3 + 2/3 × 0.2) ≈ 0.11.
  4. Trim history and cap tool results; input drops ~20%. Cost ≈ 0.09.
- **Result:** roughly 10× lower in this example. Real gains depend on your traffic; the order of levers is the lesson.
- **Check:** quality, task success and safety cases must hold at each step, or that change is rolled back.
- 🗣 "Workflow for the known path, cache the prefix, route easy steps down, trim context. Each change gated by evals."

---

## 5. Budgets, quotas and attribution
`software` ★★

- **Per-run budgets:** max steps, max tokens, max spend, max time. The harness stops and returns a partial result ([1loop.md](1loop.md) §3).
- **Per-user and per-tenant quotas:** tokens per day, concurrent runs. Enforced at the edge or gateway.
- **Attribution:** tag every model call with tenant, feature, agent and run IDs. Cost per task and per tenant become queryable ([4observability.md](4observability.md)).
- **Alerts:** cost per task above baseline; sudden rise in steps per run; cache hit ratio drop.
- **Unit economics:** cost per resolved ticket vs the human cost it replaces is the business number.
- 🗣 "Budgets per run, quotas per tenant, attribution on every call."

---

## 6. Caching beyond the prompt
`software` ★★

| Cache | What's stored | Hit when | Risk |
|---|---|---|---|
| Provider prompt cache | processed prompt prefix | same prefix | breaks on prefix change |
| Tool result cache | results of read tools | same tool and arguments within TTL | stale data |
| Retrieval cache | search results for a query | same query | stale index |
| Exact response cache | final answers | identical request and context | personalized answers leak |
| Semantic cache | answers to similar questions (by embedding) | similar enough | wrong answer reused; cross-user leaks |

- **Rules:** key caches by user or tenant where data is personal; set TTLs by data freshness; never semantic-cache answers that depend on the user's own data without that in the key.
- **Pick:** tool and retrieval caches first; semantic caching only for public, generic questions.

---

## 7. System design view: choosing
`boundary` ★★★

| Decision | Options | How to decide |
|---|---|---|
| Control shape | loop vs workflow | workflow for known paths to cut steps |
| Model per step | one vs routed | routed once traffic and cost justify it |
| Prompt layout | any vs cache-ordered | always cache-ordered |
| Parallelism | serial vs parallel reads | parallel for independent reads |
| Budgets | none vs per run and tenant | always |
| Response caching | none, exact, semantic | exact for public answers; semantic rarely |

- **Default:** cache-ordered prompts, workflows for fixed paths, per-step model routing after evals, parallel reads, streaming plus progress events, per-run budgets, per-tenant quotas, cost attribution on every span.

---

## 8. Failure modes
`boundary`

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Cost creep after a prompt change | more steps or longer context | cost per task trend | eval gate tracks cost |
| Cache hit ratio collapse | prefix changed | cached-token ratio | reorder; review prompt diffs |
| Runaway loop bill | missing budget | spend per run outliers | per-run caps |
| Noisy tenant | one tenant floods | per-tenant usage | quotas and isolation |
| Stale cached answers | long TTLs | user reports | TTL by freshness; invalidation |
| Latency spikes | slow tool or provider | tail latency by span | timeouts, fallback, parallelism |

---

## Where this fits
- **Place:** L8 of [1a-bp.md](../1a-bp.md). Production engineering on top of groups 1–5.
- **Time it deserves:** 20 minutes; §1, §2 and §4.
- **I should be able to…**
  - Write the cost and latency formulas and explain the quadratic loop cost.
  - List the cost levers in the order I'd try them.
  - Walk the worked example and show how evals gate each step.
  - Explain per-run budgets, per-tenant quotas and attribution.

## References
1. [Anthropic — prompt caching](https://docs.claude.com/en/docs/build-with-claude/prompt-caching) — prefix caching mechanics.
2. [Anthropic — Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) — prefer workflows when paths are known.
3. [Chip Huyen — AI Engineering (O'Reilly)](https://www.oreilly.com/library/view/ai-engineering/9781098166298/) — cost and latency chapters.
