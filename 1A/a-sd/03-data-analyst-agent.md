# #3 · Data Analyst Agent (NL → SQL → chart, over the warehouse)

> Prompt: "Design a chat-to-BI agent for business users over Databricks/Snowflake/BigQuery. Users ask 'why did EU revenue drop last week' and get a verified answer with a chart."

## §0 Assumptions
- 2k analysts/PMs · 20 questions/day each → 40k q/day · 1 QPS avg / 8 peak `(assume)`
- Warehouse: 300 tables, 20 "gold" marts; queries must finish < 30 s or be async
- p95 answer < 15 s for simple, async for > 30 s · accuracy target: execution accuracy ≥ 85% on golden set
- Cost of wrong: wrong number in an exec deck → trust collapse. Read-only always.
- Stack: FastAPI + ADK · Gemini Pro (SQL) / Flash (explain) · semantic layer (dbt metrics / Unity Catalog) · Postgres · Langfuse

## §1 Why an agent `[SW+AI]`
- Baseline: dashboards + analysts. Breaks: long-tail questions, analyst queue.
- Model adds: NL → SQL over a *constrained* schema, error repair from SQL errors, narrative explanation.
- **L3 agent, bounded.** Loop: `pick tables → draft SQL → validate → execute → inspect → repair (≤ 3) → answer`. Model decides retries and follow-up queries ("why" needs a breakdown query). Not L4.
- Trigger: the query plan (which tables, how many follow-ups) is unknown until the data is seen.
- **L5:** the win is the **semantic layer**: expose metrics/dimensions, not raw tables. Text-to-metric-query has ~2× the accuracy of text-to-raw-SQL. Also pre-empt "how do you stop the model from inventing a `revenue` column".

## §2 Crux
- **Verified correctness of numbers**, not fluency. A pretty wrong chart is worse than no chart.
- Success points: schema scoping (≤ 8 tables in context) · deterministic validation (parse, allow-list, cost estimate) · execution feedback loop · show the SQL and let users pin it · golden set of (question, gold SQL, gold result).
- Business metric: analyst tickets deflected + adoption; AI metric: execution accuracy on golden set.

## §3 NFR / BoE
| NFR | Target | Enforcer |
|---|---|---|
| Correctness | exec accuracy ≥ 85%; 0 write queries | sqlglot gate + read-only role |
| Latency | simple p95 15 s; complex async ≤ 5 min | query cost estimate → route |
| Warehouse spend | ≤ $2/query avg | `EXPLAIN`/bytes-scanned cap, LIMIT, partition filter required |
| Cost LLM | ≤ $0.05/q → $2k/day | Pro for SQL only, Flash elsewhere |
| Security | row/column policies of the *user* | run as user (OAuth passthrough) |
- Tokens: 6k in (schema + examples) / 500 out × ≤ 4 loop iters → ~25k/q · 40k q → 1B/day.

## §4 HLD
```
[SW] Chat UI --SSE--> [SW] FastAPI (SSO, user token)
                          |
   [SW+AI] ADK LlmAgent loop:
     1 [AI] table/metric retrieval (pgvector over schema docs + past validated Qs)  -> ≤ 8 tables, 20 columns
     2 [AI] draft SQL (Pro)  -> 3 [SW] validate: sqlglot parse, SELECT-only, allow-listed tables, LIMIT, partition filter, cost estimate
     4 [SW] execute (read-only role, user passthrough, 30 s timeout, 10k-row cap)
     5 [AI] inspect result -> repair on error/empty (≤ 3) or follow-up query for "why"
     6 [AI] narrative + chart spec (Vega-Lite JSON) ; [SW] render
   [SW] Postgres: sessions, queries(sql, hash, result_sample, verified), golden_set, schema_docs(embedding)
   [SW] Warehouse (Databricks SQL / BigQuery)   [SW+AI] Langfuse
```

## §5 Components — problem → design
- **Schema retrieval `[AI]`:** problem = 300 tables don't fit; wrong table = wrong answer. Design: index `schema_docs` (table, column descriptions, sample values, join keys, owner) + `verified_queries` (past thumbs-up Q→SQL). Retrieve top-8 tables by embedding + BM25 on column names. Inject few-shot verified queries (top-3).
  - **L5:** curate a **gold layer** and hide raw tables; retrieval quality is bounded by documentation quality → make table owners own their descriptions (ownership angle).
- **SQL validation gate `[SW]`:** `sqlglot` AST → reject non-SELECT, multiple statements, tables not in allow-list, missing partition predicate on large tables, cross joins; enforce `LIMIT 10000`; dry-run cost estimate (`EXPLAIN` / BigQuery dry_run bytes) → > threshold → ask user or route async. Mechanical, not prompt.
- **Execution loop `[SW+AI]`:** errors fed back verbatim (`column X not found`), max 3 repairs; empty result → model checks filters (date ranges, casing) once, then reports "no rows, here's why". Identical SQL hash within 10 min → cached result.
- **Verification `[SW+AI]`:** show SQL + row count + date range used; "sanity checks" tool: totals vs known metric from semantic layer (±5%) → mismatch flagged in answer. Users can **pin** a Q→SQL as verified → enters few-shot pool + golden set.
- **Async path `[SW]`:** cost estimate > τ or timeout → job on queue, status endpoint, notify in chat; checkpoint the plan so repair loops resume.
- **Charting `[AI]`:** model emits Vega-Lite spec validated by JSON schema; renderer is deterministic; no image generation.
- **Evals `[AI]`:** 300 (Q, gold SQL, gold result) items; **execution accuracy** = result set match (order-insensitive, tolerance). CI gate on prompt/schema-doc changes. Judge only for narrative quality (κ-validated).
  - **L5:** schema drift breaks the golden set — nightly re-run gold SQL; failures flag stale items, not model regressions.

## §6 API / schema
- `POST /ask {question, session_id}` SSE → `tables_chosen`, `sql`, `validation`, `rows_preview`, `chart_spec`, `answer`
- `POST /queries/{id}/pin` · `GET /jobs/{id}` · `POST /feedback`
- `queries(id, session_id, question, sql, sql_hash, tables[], bytes_est, status, result_uri, verified, user_id)`
- `schema_docs(table, column, description, sample_values, embedding)` · `verified_queries(question, sql, embedding)` · `golden_set`

## §7 Hygiene
| Concern | Answer |
|---|---|
| AuthZ | user OAuth passthrough → warehouse row/column policies apply; read-only role |
| Idempotency | query hash cache; jobs idempotent on id |
| Timeouts | 30 s sync; async beyond; warehouse statement timeout |
| Rate limit | per-user daily bytes-scanned budget |
| Cache | result cache by (sql_hash, user policy hash) 10 min |
| Deploy | schema docs + prompts versioned; golden gate |
| PII | result previews capped; no raw rows into traces |

## §8 Failure → fallback
- Wrong table → show tables chosen, one-click "use X instead" · SQL error → 3 repairs → show error, hand to analyst · Cost too high → ask to narrow / async · Empty → explain filters · Model down → "search verified questions" (no LLM) mode.

## §9 Pop-up questions
1. **Why not text-to-SQL on the whole schema?** — Context and accuracy; scope to ≤ 8 tables via retrieval, prefer semantic layer.
2. **Model hallucinates a column?** — AST validation against catalog; error fed back; 3-repair cap.
3. **How do you know the number is right?** — Execution accuracy on golden set; sanity checks vs semantic-layer metrics; SQL shown; pinning.
4. **User without access to `salary` asks about payroll?** — Passthrough auth; warehouse enforces; agent never has broader rights.
5. **A "why" question?** — Agentic follow-ups: breakdown by dimension, compare periods; loop cap 4 queries; narrative cites each.
6. **Warehouse bill explodes?** — Dry-run cost gate, partition predicate required, per-user budget, result cache.
7. **L5: semantic layer vs raw SQL?** — Metric queries ~2× accuracy and consistent definitions; raw SQL as escape hatch behind stronger gate.
8. **L5: multi-warehouse?** — Dialect via sqlglot transpile; per-warehouse validators; catalog abstraction.

## §10 Trade-offs + defeaters
| Decision | Chosen | Alt | Flips |
|---|---|---|---|
| Target | semantic layer + gold tables | raw schema | no dbt/UC metrics exist |
| SQL model | Pro | Flash | golden accuracy within 2 pts |
| Validation | sqlglot AST gate | prompt rules | never |
| Long queries | async job | wait | never wait > 30 s in chat |
- Defeaters: fine-tune on our SQL (schema drifts) · let the agent write to a scratch schema · judge SQL with an LLM instead of executing it.

## §11 MVP ladder
- MVP0: 5 gold tables, retrieval-free schema in prompt, sqlglot gate, execute, show SQL + table.
- MVP1: schema retrieval, repair loop, Vega chart, Langfuse, 100-item golden set.
- MVP2: pinning/verified pool, cost gate + async, sanity checks.
- MVP3: semantic layer integration, per-user budgets, nightly golden re-run.

## §12 Memorization card
- Pitch: retrieval-scoped NL→SQL with an AST gate, execute-and-repair loop, shown SQL, execution-accuracy evals.
- Autonomy: L3 bounded; trigger = plan depends on data seen.
- Numbers: ≤ 8 tables · 3 repairs · 85% exec accuracy · 30 s sync cap · $2/query warehouse.
- Failures: wrong table · hallucinated column · runaway warehouse cost.
- Defeaters: fine-tune SQL · agent writes · LLM-graded SQL.
- MVP0→1→2: gated SQL on 5 tables → retrieval + repair + chart → pinning + cost/async.
- Done when: recite the validation gate list · explain execution accuracy · argue semantic layer.

## References
1. https://github.com/tobymao/sqlglot
2. https://github.com/vanna-ai/vanna (retrieval-augmented text-to-SQL pattern)
3. https://docs.databricks.com/aws/en/genie/
4. https://github.com/google/adk-python
