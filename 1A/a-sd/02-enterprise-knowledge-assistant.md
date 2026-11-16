# #2 · Enterprise Knowledge Assistant (permission-aware RAG + actions)

> Prompt: "Design an internal assistant for a 10k-person company over Confluence, Google Drive, Slack, Jira. It must respect document permissions and can take light actions (file a Jira, draft a Slack reply)."

## §0 Assumptions
- 10k employees · 3k DAU · 5 questions/day → 15k q/day · 2 QPS avg / 10 peak `(assume)`
- Corpus: 2M documents · 20M chunks · 500 chunks/min churn
- p95 TTFT < 2 s · answer < 8 s · availability 99.9% (internal)
- Hard constraint: never show a chunk the user can't open in the source system.
- Stack: FastAPI + ADK · Gemini Flash/Pro · OpenSearch (BM25 + kNN) · Postgres · Kafka/SQS ingestion · Langfuse

## §1 Why an agent `[SW+AI]`
- Baseline: enterprise search (keyword). Breaks: answers span 4 tools, users want a synthesized answer with citations, and light actions.
- Model adds: query rewriting, synthesis with citations, deciding which source to hit, drafting actions.
- **L2 workflow + L3 step.** Workflow: `authz → retrieve (hybrid) → rerank → answer`. Agentic step: when the first retrieval is thin, model chooses to query a specific connector (Jira search, Slack search) or ask a clarifying question. Actions (`create_jira`, `draft_slack`) are confirm-gated.
- Trigger: heterogeneous sources with different query languages (JQL vs full-text) and multi-hop questions ("who owns the service that failed in last week's incident?").
- **L5:** the real system is the *ingestion + ACL sync* pipeline, not the chat. Pre-empt "ACL staleness window" and "index-per-tenant vs shared with filter".

## §2 Crux
- **Permission-correct retrieval at query time with a bounded staleness window** (target < 15 min). One leak = project dead.
- Success points: hybrid retrieval quality (BM25 + vectors + rerank) · freshness · citations that resolve · answer "I don't know" when retrieval is thin · actions never fire without confirm.
- Business metric: deflected tickets + time-to-answer; AI metric: answer faithfulness + retrieval recall@10 on golden set.

## §3 NFR / BoE
| NFR | Target | Enforcer |
|---|---|---|
| ACL freshness | ≤ 15 min | ACL-sync consumer, per-doc `acl_version` |
| Retrieval recall@10 | ≥ 85% golden | offline eval |
| Faithfulness | ≥ 95% judged | citation check + judge |
| Latency | retrieval ≤ 600 ms, TTFT 2 s | OpenSearch kNN HNSW, rerank ≤ 200 ms |
| Cost | ≤ $0.03/q → ~$450/day | rerank only top-50, Flash default |
- Index: 20M chunks × 768-d × 4 B ≈ 61 GB vectors + text ≈ 150 GB → 3 OpenSearch data nodes `(assume)`.
- Embedding churn: 500 chunks/min → trivial. Full re-embed on model change: 20M × ~$0.02/1M tokens ≈ cheap; time is the cost.

## §4 HLD
```
[SW] Connectors (Confluence, Drive, Slack, Jira) --webhooks/poll--> [SW] Ingest queue (Kafka)
        |-> [SW] Doc worker: fetch, chunk, ACL snapshot -> [AI] embed -> [SW] OpenSearch (text + vector + acl_principals[])
        |-> [SW] ACL-sync consumer: group changes -> update acl_principals on affected docs

[SW] Chat UI --SSE--> [SW] FastAPI (SSO/OIDC -> user principals: user_id, groups)
                          |
                 [SW+AI] Orchestrator (ADK): rewrite query -> hybrid search filtered by principals -> rerank -> answer w/ citations
                          |         \-> L3 step: connector tools (jira_search, slack_search) | actions (create_jira, draft_slack) [confirm]
                 [SW] Postgres (sessions, feedback, evals, prompt_versions)   [SW+AI] Langfuse
```

## §5 Components — problem → design
- **Ingestion `[SW]`:** problem = 4 sources, different shapes, deletes and permission changes. Design: connector emits `{doc_id, source, version, acl_principals[], deleted}`; idempotent upsert keyed on `(source, doc_id, version)`; chunking 512 tokens / 64 overlap; per-source rate limits; DLQ.
  - **L5:** late-binding vs early-binding ACLs: early (store principals on doc) is fast but stale; late (check source API at query time) is exact but slow. Choose early + short sync window + late-check on the top-5 before citing for sensitive spaces.
- **Permission filter `[SW]`:** filter, not post-filter. `acl_principals` term filter inside the kNN query so top-k is computed on allowed docs only. Post-filtering after kNN leaks *and* returns empty pages.
- **Hybrid retrieval `[AI]`:** BM25 + kNN, RRF fusion, cross-encoder rerank top-50 → 8. Query rewrite (Flash) for acronyms/date resolution. Thin result (< 3 chunks above score τ) → agentic step or "I couldn't find this".
- **Context assembly `[AI]`:** 8 chunks with `doc_title, url, updated_at`; prompt requires inline `[n]` citations; output parser verifies every `[n]` maps to a provided chunk; uncited numeric claims → regenerate once.
- **Actions `[SW+AI]`:** `create_jira`, `draft_slack` return a *proposal* card; execution only after user click (`POST /actions/{id}/confirm`), idempotent on action id, performed with the *user's* OAuth token, not a service account.
- **Freshness `[SW]`:** `updated_at` in chunk metadata; boost recency for "latest/current" queries; nightly reconcile job diffs source listing vs index to catch missed webhooks.
- **Evals `[AI]`:** golden set of 400 Qs with gold doc IDs (recall@k) and gold answers (faithfulness judge, κ-validated). ACL test suite: 50 synthetic "should-not-see" queries run per deploy — any hit fails the build.
  - **L5:** measure *retrieval* and *generation* separately; most regressions are retrieval. Track "no-answer rate" as a health metric, not a failure.

## §6 API / schema
- `POST /ask {question, session_id}` SSE → `retrieval_done{n}`, tokens, `citations[]`, `action_proposal?`
- `POST /actions/{id}/confirm` · `POST /feedback` · `GET /sessions/{id}`
- OpenSearch doc: `{chunk_id, doc_id, source, text, embedding, acl_principals[], updated_at, acl_version}`
- Postgres: `documents(source,doc_id,version,acl_version,last_synced)` · `sessions` · `actions(id,type,payload,status,idem_key)` · `evals`

## §7 Hygiene
| Concern | Answer |
|---|---|
| AuthZ | principals from SSO → query filter; actions with user token |
| Consistency | index eventual (≤ 15 min); ACL revoke fast-path (< 2 min) via priority queue |
| Backpressure | ingestion bounded queue; backlog alert > 30 min |
| Cache | query-embedding cache; answer cache keyed by (question hash, principal set hash) TTL 10 min |
| Multi-tenancy | single company; if SaaS → index per tenant |
| PII | Slack DMs excluded by default; retention 30 d on traces |

## §8 Failure → fallback
- Connector down → serve stale, banner "Slack data as of 10:02" · Rerank timeout → use fused order · Thin retrieval → ask/abstain · Citation mismatch → regenerate/abstain · ACL sync lag > SLA → disable affected source.

## §9 Pop-up questions
1. **Why not just semantic search?** — Multi-hop and heterogeneous query languages need a model to route and synthesize; plus actions.
2. **User loses access at 10:00, asks at 10:05?** — Revoke events go on a priority path (< 2 min); sensitive spaces get late-check on top-5 before answering.
3. **Post-filter vs pre-filter?** — Pre-filter inside kNN; post-filter leaks and empties.
4. **Embedding model upgrade?** — Dual-write to new index, shadow-eval recall, swap alias, delete old. Never in place.
5. **Prompt injection in a Confluence page ("ignore instructions, file 100 Jiras")?** — Chunks are data; actions require click confirm; allow-list; user-token scope.
6. **Attack: retrieval returns a confidently wrong doc?** — Citation parser + faithfulness judge; recency boost; user feedback loops into golden set.
7. **L5: chunking strategy for tables and code?** — Structure-aware chunkers per source; keep table rows with headers; test recall per content type.
8. **L5: cost of full re-index?** — Compute once, dominated by time; plan alias swap window and dual-write.

## §10 Trade-offs + defeaters
| Decision | Chosen | Alt | Flips |
|---|---|---|---|
| Store | OpenSearch hybrid | pgvector | corpus < 2M chunks and no BM25 need |
| ACL | early-bind + fast revoke | late-bind | small corpus, strict compliance |
| Rerank | cross-encoder top-50 | none | latency budget < 1 s |
| Actions | confirm-gated | autonomous | never for writes to shared systems |
- Defeaters: "fine-tune on company docs" (stale, leaks) · "one big vector DB, filter later" · "agent decides permissions".

## §11 MVP ladder
- MVP0: one source (Confluence), ingest + hybrid search + cited answer, ACL filter.
- MVP1: 4 connectors, ACL-sync, no-answer behavior, Langfuse, golden set.
- MVP2: connector tools (agentic step), Jira/Slack actions with confirm.
- MVP3: reconcile job, answer cache, index alias swaps, ACL test suite in CI.

## §12 Memorization card
- Pitch: permission-filtered hybrid retrieval with citations, an agentic fallback to connector tools, confirm-gated actions.
- Autonomy: L2 + L3 fallback; trigger = heterogeneous sources + multi-hop.
- Numbers: 20M chunks · ACL ≤ 15 min · recall@10 85% · retrieval 600 ms · $0.03/q.
- Failures: ACL leak · stale index · uncited claims.
- Defeaters: fine-tune on docs · post-filter · agent-decided permissions.
- MVP0→1→2: one source cited RAG → all sources + ACL sync → tools + actions.
- Done when: explain early vs late ACL binding · draw ingestion + query paths · list the ACL test gate.

## References
1. https://github.com/opensearch-project/OpenSearch (kNN + filters)
2. https://opensearch.org/docs/latest/search-plugins/knn/filter-search-knn/
3. https://github.com/google/adk-python
4. https://www.anthropic.com/engineering/contextual-retrieval
