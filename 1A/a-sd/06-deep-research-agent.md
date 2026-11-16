# #6 · Deep Research Agent (long-running, cited report)

> Prompt: "Design an agent that, given a question ('compare vector DBs for 100M-scale'), researches for 10–20 minutes across the web and internal docs and returns a cited report."

## §0 Assumptions
- 5k users · 2 reports/day each → 10k jobs/day · job 5–20 min · 500 concurrent `(assume)`
- Sources: web search + fetch, internal docs (from #2), optional data tools
- Target: faithfulness ≥ 95% (every claim cited and supported), completeness judged ≥ 4/5, cost ≤ $1.50/job
- Cost of wrong: medium — reader can check citations; confident fabrication is the failure to prevent
- Stack: FastAPI + job workers · LangGraph (checkpointed) or ADK `SequentialAgent`/`ParallelAgent` · Gemini Pro (plan/write) / Flash (read/extract) · Postgres · S3 · Langfuse

## §1 Why an agent `[SW+AI]`
- Baseline: search engine + human reading 30 tabs. Breaks: hours of work; no synthesis.
- Model adds: query decomposition, judging source relevance, extraction, synthesis with citations.
- **L3 agent with a bounded L4 fan-out.** Planner produces sub-questions (code caps at 6); each sub-question runs as a parallel *worker* (same agent code, different input, isolated context) → results merged → writer. Workers are parallelism, not "specialist agents".
- Trigger: number and shape of sub-questions unknown until initial search; per-branch context isolation keeps each worker under 100k tokens.
- Cost of wrong: fabricated citation → hard gate: every citation must resolve to a fetched-and-stored source; unsupported claims cut.
- **L5:** the report is a *job* with checkpoints, cost budget, and partial delivery; the org question is search API cost and crawl politeness (robots, rate limits, caching fetched pages across users).

## §2 Crux
- **Grounded synthesis under a budget**: plan → gather (bounded) → verify → write, with citations that are mechanically checkable.
- Success points: decomposition quality · source triage (skip junk fast) · dedup + caching of fetched pages · claim-to-source verification · streaming progress so users trust a 15-min wait · budget caps.
- Business metric: report acceptance (thumbs, reuse) + time saved; AI metric: citation faithfulness + coverage vs rubric.

## §3 NFR / BoE
| NFR | Target | Enforcer |
|---|---|---|
| Job time | p50 8 min, cap 25 min | wall-clock budget |
| Budget | ≤ 1.5M tokens, ≤ 60 fetches, ≤ 20 searches per job | budget guard |
| Faithfulness | ≥ 95% claims supported | citation verifier + judge |
| Progress UX | update every ≤ 20 s | SSE from checkpoints |
| Resumability | worker death → resume at last checkpoint | checkpointer |
| Cost | ≤ $1.50/job → $15k/day | Flash for reading, Pro for plan/write |
- 10k jobs × 1.2M tokens avg = 12B tokens/day; ~80% Flash → $5–8k model + $3k search API `(assume)`.

## §4 HLD
```
[SW] UI --SSE progress--> [SW] FastAPI -> [SW] job queue -> [SW] workers (LangGraph graph, Postgres checkpoints)
   graph:
     [AI] clarify (optional, 1 turn) -> [AI] plan: sub-questions (≤6) + rubric
     -> [SW] fan-out ParallelAgent: per sub-question worker
            [AI] search (n≤4) -> [SW] fetch+cache (dedup by URL hash, robots, 10 s) -> [AI] extract claims+quotes (Flash)
     -> [SW] merge: notes table (claim, quote, source_id, confidence)
     -> [AI] gap check vs rubric -> loop once if gaps
     -> [AI] write report (Pro) with [n] citations
     -> [SW] citation verifier: every [n] -> stored source; quote appears in source text (fuzzy) ; drop/flag unsupported
     -> [SW] deliver (markdown + sources) ; [AI] async judge sample
[SW] Postgres (jobs, checkpoints, sources, claims, reports, evals) · [SW] S3 (fetched pages) · [SW+AI] Langfuse
```

## §5 Components — problem → design
- **Planner `[AI]`:** problem = bad decomposition = bad report. Design: Pro produces `{sub_questions[], rubric[], stop_criteria}` as JSON (schema-validated); code caps 6; rubric drives the gap check and the eval.
- **Gather workers `[SW+AI]`:** each has its own context; returns structured notes only (≤ 3k tokens), never raw pages → merge stays small. Source triage: Flash scores relevance 0–1 on snippet before fetch; fetch only ≥ 0.6.
- **Fetch layer `[SW]`:** shared cache (URL hash → S3, TTL 7 d), robots.txt respect, per-domain rate limit, 10 s timeout, readability extraction, size cap 200 kB. This is where cost and politeness live.
  - **L5:** cross-user cache hit rate is a big cost lever (popular topics); PDF/JS-heavy pages need a headless fallback with a separate budget.
- **Claim ledger `[SW+AI]`:** table `claims(job_id, text, quote, source_id, confidence)`; writer may cite only ledger rows; verifier fuzzy-matches quotes to stored source text (≥ 0.8 similarity) → unsupported claims removed and listed under "unverified".
- **Loop control `[SW]`:** gap check may trigger one more gather round; hard caps on tokens/fetches/time; on cap → write with what exists and label coverage.
- **Progress + resumability `[SW]`:** every node writes a checkpoint; UI subscribes to `job_events` (plan ready, 3/6 sub-questions done, writing); worker death → resume node; cancel supported.
- **Evals `[AI]`:** 100 questions with expert rubrics; scores: rubric coverage (judge, κ-validated), citation faithfulness (mechanical + judge), cost/time; CI gate on planner/writer prompt changes; A/B on report acceptance.
  - **L5:** faithfulness ≠ correctness — sources can be wrong; add source-quality scoring (domain reputation, date) and show it.

## §6 API / schema
- `POST /jobs {question, scope: web|internal|both, depth}` → `job_id` · `GET /jobs/{id}` · `GET /jobs/{id}/events` (SSE) · `POST /jobs/{id}/cancel` · `GET /reports/{id}`
- `jobs(id,user_id,question,status,budget,cost,checkpoint_step)` · `sources(id,job_id,url,hash,title,fetched_at,s3_uri,quality)` · `claims(...)` · `reports(id,job_id,markdown,unverified[])` · `fetch_cache(url_hash,s3_uri,ttl)` · `evals`

## §7 Hygiene
| Concern | Answer |
|---|---|
| AuthZ | internal-doc branch reuses #2's permission filter |
| Idempotency | job key (user, question hash, day); fetch cache |
| Timeouts | fetch 10 s, node 3 min, job 25 min |
| Rate limit | per-user jobs/day; per-domain crawl limits; search API quota |
| Backpressure | bounded worker pool; queue depth alert; degrade depth when saturated |
| Cache | fetch cache 7 d; search results 1 h; embeddings of sources for dedup |
| Observability | span per node/worker; $ per job; faithfulness per report |
| Retention | fetched pages 7 d; reports per user policy |

## §8 Failure → fallback
- Search API down → internal-only report with banner · Fetch failures > 50% → fewer sources, label coverage · Budget hit → partial report, "unverified" section · Writer omits citations → regenerate once, then flag · Worker death → resume.

## §9 Pop-up questions
1. **Why multi-agent here when you argue against it elsewhere?** — Fan-out for context isolation and parallel latency, capped at 6, identical code; not specialists.
2. **Fabricated citation?** — Writer cites ledger rows only; verifier matches quotes to stored text; unsupported → removed.
3. **20-minute job dies at 18?** — Checkpoint per node; resume; partial delivery.
4. **Cost per job explodes?** — Budget guard on tokens/fetches/time; Flash for reading; cache; depth tiers.
5. **User cancels?** — Cancel flag checked between nodes; workers stop; partial report offered.
6. **How do you eval a report?** — Rubric coverage by judge (κ-validated), mechanical faithfulness, human spot checks.
7. **L5: politeness/legal for crawling?** — robots.txt, rate limits, cache, respect paywalls; search API terms.
8. **L5: what changes at 10×?** — Dedicated fetch fleet, cross-user cache, tiered depth, spot workers, search vendor mix.

## §10 Trade-offs + defeaters
| Decision | Chosen | Alt | Flips |
|---|---|---|---|
| Orchestration | LangGraph checkpoints | Temporal | cross-service durable steps |
| Fan-out | parallel workers ≤ 6 | sequential | strict cost ceiling |
| Citations | ledger + verifier | trust model | never |
| Reading model | Flash | Pro | extraction quality < bar |
- Defeaters: "put all pages in a 1M context and write" · "specialist agents per domain" · "no progress UI, just wait".

## §11 MVP ladder
- MVP0: plan → sequential search/fetch/extract → write with citations → verifier; sync CLI.
- MVP1: job queue, checkpoints, SSE progress, budget guard, fetch cache.
- MVP2: parallel workers, gap-check loop, claim ledger, 50-question eval.
- MVP3: internal-doc branch, source quality scores, depth tiers, cost dashboards.

## §12 Memorization card
- Pitch: checkpointed plan-gather-verify-write job with a claim ledger and mechanical citation verification.
- Autonomy: L3 + capped parallel fan-out; trigger = unknown sub-question count, context isolation.
- Numbers: ≤ 6 sub-Qs · 60 fetches · 1.5M tokens · 25 min · 95% faithfulness.
- Failures: fabricated citation · runaway cost · lost long job.
- Defeaters: 1M-context dump · specialist agents · no progress.
- MVP0→1→2: sync pipeline with verifier → jobs + checkpoints + progress → parallel + ledger + evals.
- Done when: draw the graph with checkpoints · explain the verifier · defend the fan-out cap.

## References
1. https://github.com/langchain-ai/open_deep_research
2. https://github.com/langchain-ai/langgraph
3. https://www.anthropic.com/engineering/built-multi-agent-research-system
4. https://google.github.io/adk-docs/agents/workflow-agents/
