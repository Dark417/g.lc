# 2models — The Model Layer: Choosing, Routing, Caching

> How to pick models for an agent, route between them, use caching and batch modes, and treat model changes as deploys.
> Group 2 (supporting components). Related: [6cost-latency.md](6cost-latency.md), [1architecture.md](1architecture.md) §3.3 (gateway), [7serving.md](7serving.md).
> Concept level, no code (AGENTS.md §8b). Last updated: 2026-11-16. Prices and limits change often; numbers here are order of magnitude unless cited.

## Index
- [0. One-minute version](#0-one-minute-version)
- [1. Concept](#1-concept)
- [2. What to compare when picking a model](#2-what-to-compare-when-picking-a-model)
- [3. Model tiers and reasoning effort](#3-model-tiers-and-reasoning-effort)
- [4. Routing patterns](#4-routing-patterns)
- [5. Prompt caching and batch](#5-prompt-caching-and-batch)
- [6. API model vs open-weight model](#6-api-model-vs-open-weight-model)
- [7. Model changes are deploys](#7-model-changes-are-deploys)
- [8. System design view: choosing](#8-system-design-view-choosing)
- [9. Failure modes](#9-failure-modes)
- [Where this fits](#where-this-fits)
- [References](#references)

---

## 0. One-minute version
- **What:** the model layer is which models you call, for which steps, through which provider, with which settings.
- **Why:** model choice is the biggest single lever on quality, latency and cost.
- **How:** set a quality bar with evals, then use the cheapest model that passes it per step; route hard cases up; cache the stable prompt prefix.
- **Catch:** a bigger context window isn't more usable context, and a model upgrade can silently change behavior.
- 🗣 "I pick the cheapest model that passes the eval for each step, not one model for everything."

---

## 1. Concept
`AI` ★★★

- **Plain idea:** like staffing. A senior engineer for the design review, a junior for the routine tickets. Paying senior rates for everything is waste; giving juniors the hard calls is risk.
- **Picture it:** a support agent with three kinds of model call.
  - Classify intent: a small, fast model.
  - Answer with tools: a mid-tier model.
  - Rare hard cases (disputes, long reasoning): a frontier model with more reasoning effort.
- **How it works**
  1. Define steps and their quality bar (from evals).
  2. Try models per step, smallest first.
  3. Keep the cheapest that passes; add a fallback for outages.
  4. Pin versions; re-run evals before any change.
- **The catch:** every extra model is another thing to evaluate, monitor and upgrade.
- 🗣 "Different steps deserve different models. Evals decide which."

---

## 2. What to compare when picking a model
`AI` ★★★

| Dimension | Why it matters for agents | How to check |
|---|---|---|
| Task quality | wrong answers, wrong tools | your eval set, not public benchmarks |
| Tool-use reliability | correct tool and arguments across many steps | step-level evals ([4evals.md](4evals.md)) |
| Structured output | schema adherence | strict or schema-enforced modes ([2prompt.md](2prompt.md)) |
| Latency | time to first token, tokens per second | measure from your region |
| Cost | input, output and cached-input prices | the provider's pricing page |
| Context window | how much fits | test quality near your real lengths |
| Rate limits | tokens and requests per minute | your quota tier |
| Data policy and region | retention, training use, residency | contract and docs |

- **Context window vs usable context:** quality often drops as context grows ("context rot"). Test at your real sizes ([2context](2context-engineering-handbook.md)).
- **Benchmarks are a shortlist, not a decision.** Your eval set decides.
- 🗣 "Benchmarks pick the shortlist; my eval set picks the model."

---

## 3. Model tiers and reasoning effort
`AI` ★★

| Tier | Typical use | Strength | Cost |
|---|---|---|---|
| Small and fast | classification, extraction, routing, simple tool calls | latency, price | lower quality on reasoning |
| Mid | most agent steps | balance | moderate |
| Frontier | planning, hard reasoning, synthesis, coding | quality | highest price, slower |

- **Reasoning effort (thinking budget):** many models can spend more tokens thinking before answering.
  - More effort: better on hard problems, slower, more output tokens billed.
  - Less effort: faster and cheaper on easy steps.
  - Treat it as a per-step setting, tuned by evals.
- **Example lineup (late 2026):** providers offer small, mid and frontier tiers, for example Anthropic's Haiku, Sonnet, Opus and the Mythos-class tier. Names and prices change; check current docs.

---

## 4. Routing patterns
`boundary` ★★★

| Pattern | How it works | Good at | Weak at | Choose when |
|---|---|---|---|---|
| Static per step | each step has a fixed model | simple, predictable | no adaptivity | most systems; start here |
| Classifier router | a small model or rules pick the model per request | saves cost on easy traffic | router errors | mixed easy and hard traffic |
| Cascade | try the cheap model; escalate if a check fails | cheap on average | extra latency on escalations | a cheap, reliable check exists |
| Fallback | switch provider or model on errors | availability | quality may differ | always, for outages |
| Ensemble or vote | several models answer; judge or vote | accuracy | multiplies cost | rare high-stakes decisions |

- **Where routing lives:** in the harness (per step) or in the gateway (aliases like "fast" and "strong").
- **Cascade needs a verifier:** schema check, grounding check or confidence signal. Without one, you can't tell when to escalate.
- 🗣 "Static per step first, a cascade when I have a cheap check, and a fallback always."

---

## 5. Prompt caching and batch
`software` ★★★

- **Prompt caching: plain idea.** If many requests start with the same text, the provider keeps that prefix processed and charges less for reusing it.
- **How it works**
  1. Put stable content first: instructions, tool definitions, fixed documents.
  2. Put volatile content last: history, retrieved text, the new message.
  3. Mark or rely on cache points (provider-specific).
  4. Repeated prefixes hit the cache: lower input cost and faster first token.
- **Numbers (cite and check):** Anthropic prices cache reads at a fraction of base input price (about one tenth), with a premium on cache writes; caches expire after minutes unless refreshed or extended. Other providers cache automatically with their own discounts.
- **The catch:** any change near the start of the prompt (a timestamp, a reordered tool list) breaks the cache for everything after it.
- **Batch APIs:** submit many requests for asynchronous processing, typically at about half price, with results in hours. Use for offline work: evals, backfills, document processing. Not for chat.
- 🗣 "Stable first, volatile last. A timestamp at the top of the prompt can double my bill."

---

## 6. API model vs open-weight model
`boundary` ★★

| Option | What it is | Good at | Bad at | Choose when |
|---|---|---|---|---|
| Provider API | hosted frontier and mid models | best quality, no infrastructure | data leaves your boundary (per contract); rate limits | default |
| Cloud model hub | the same or similar models via your cloud (Bedrock, Google's platform) | contracts, region, IAM on one cloud | model availability lags sometimes | enterprise on one cloud |
| Self-hosted open weights | you run the model ([7serving.md](7serving.md)) | control, data residency, cost at very high steady volume | GPU ops, lower top quality | strict data rules, huge steady volume, specialized small models |

- **Fine-tuning, high level:** consider it after prompting and retrieval are exhausted, for format consistency, style, or making a small model match a big one on one narrow task. It adds a training and evaluation pipeline to maintain.
- **Default:** provider API through a gateway; self-host only with a clear data or volume reason.

---

## 7. Model changes are deploys
`software` ★★★

- **Pin exact model versions.** An alias that silently moves to a new snapshot changes behavior without a deploy.
- **Before switching:** run the eval gate, compare cost and latency, canary on live traffic ([6llmops.md](6llmops.md)).
- **Deprecations:** providers retire models on a schedule. Track dates; keep the eval set ready to qualify a replacement.
- **Prompts are model-specific.** A prompt tuned for one model may need changes for another.
- 🗣 "A model version is a dependency version. I pin it and upgrade it through the same gate as code."

---

## 8. System design view: choosing
`boundary` ★★★

| Decision | Options | How to decide |
|---|---|---|
| Models per step | one model vs per-step | per-step once cost or latency matters |
| Routing | static, classifier, cascade | static first; cascade with a cheap verifier |
| Access | direct SDK vs gateway | gateway with several models or teams |
| Caching | none vs structured prefix | always structure for caching |
| Offline work | real-time vs batch API | batch for anything not user-facing |
| Hosting | API, cloud hub, self-hosted | data policy and steady volume |

- **Default:** a mid-tier model for most steps, a small model for classification, a frontier model for rare hard cases; static routing per step plus a fallback provider; prompts ordered for caching; batch for evals; versions pinned.

---

## 9. Failure modes
`boundary`

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Silent behavior change | unpinned alias moved | eval scores drift with no deploy | pin versions |
| Cache never hits | volatile text at the top of the prompt | cached-token ratio near zero | reorder prompt |
| Router misroutes | classifier errors | quality drop on routed traffic | evaluate the router; cascade with a check |
| Outage | single provider | error rate spike | fallback provider in the gateway |
| Long-context quality drop | stuffing the window | quality falls with length | trim, retrieve, summarize |
| Deprecation surprise | model retired | provider notice | track dates; qualify replacements early |

---

## Where this fits
- **Place:** L2 and L8 of [1a-bp.md](../1a-bp.md). Feeds cost and latency design.
- **Time it deserves:** 20 minutes; §2, §4 and §5.
- **I should be able to…**
  - Name the dimensions for choosing a model, and why my eval set beats benchmarks.
  - Compare static, classifier, cascade and fallback routing.
  - Explain how prompt caching works and what breaks it.
  - Say why a model upgrade goes through the eval gate.

## References
1. [Anthropic — prompt caching](https://docs.claude.com/en/docs/build-with-claude/prompt-caching) — cache pricing and placement.
2. [Anthropic — batch processing](https://docs.claude.com/en/docs/build-with-claude/batch-processing) — asynchronous batch discount.
3. [OpenAI — prompt caching guide](https://platform.openai.com/docs/guides/prompt-caching) — automatic caching.
4. [Chroma — context rot](https://research.trychroma.com/context-rot) — quality vs context length.
