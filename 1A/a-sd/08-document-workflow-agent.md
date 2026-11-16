# #8 · Document Workflow Agent (insurance claims / invoice processing with human review)

> Prompt: "Design a system that ingests claim submissions (PDFs, photos, emails), extracts data, validates against policy, decides or routes to an adjuster, and pays approved claims."

## §0 Assumptions
- 50k claims/day · 3–8 documents each · 20% need a human today → target 8% `(assume)`
- SLA: straight-through decision < 10 min; human-routed < 24 h
- Accuracy: extraction field-level ≥ 98% on critical fields; 0 wrong payouts above $1k without human
- Regulated: audit trail for every decision; explainability
- Stack: FastAPI + queue workers · Document AI / OCR + LLM extraction (Gemini Flash w/ vision) · rules engine (code) · Postgres · S3 · review UI · Langfuse

## §1 Why an agent `[SW+AI]`
- Baseline: OCR + templates + adjusters. Breaks: layout variety, free-text descriptions, email attachments.
- Model adds: robust extraction from messy docs, classification, summarization for reviewers, drafting customer letters.
- **L2 workflow. Not an agent.** Steps are fixed: `ingest → classify → extract → validate (rules) → decide (rules) → route/pay → notify`. The LLM fills extraction/classification/summary; code controls flow. No trigger for L3: task shape is known at design time.
- Say it: *"This should be a workflow, not an agent. I'll put one bounded agentic step only in the reviewer copilot (ad-hoc questions over the claim file)."*
- Cost of wrong: money + regulation → rules decide payouts; model outputs are inputs to rules with confidence.
- **L5:** the value is in **confidence routing** (auto vs review) tuned to a cost model, and in a feedback loop from adjuster corrections into extraction evals. Also pre-empt "why not fine-tune extraction" (do it only for high-volume stable doc types, after measuring).

## §2 Crux
- **Extraction you can trust enough to auto-decide, and honest routing when you can't.**
- Success points: per-field confidence · deterministic validation/decision rules · HITL queue with correction capture · idempotent payouts · full audit trail · eval by doc type.
- Business metric: straight-through rate at fixed error rate + cycle time; AI metric: field F1 by doc type.

## §3 NFR / BoE
| NFR | Target | Enforcer |
|---|---|---|
| Throughput | 50k claims × 5 docs = 250k docs/day ≈ 3/s avg, 15/s peak | worker autoscale |
| STP time | p95 < 10 min | queue SLAs |
| Extraction | critical F1 ≥ 98%; else route | confidence thresholds |
| Payout safety | > $1k or confidence < τ → human | decision rules |
| Audit | every field: source doc, bbox, model version, reviewer | provenance schema |
| Cost | ≤ $0.20/claim → $10k/day | Flash, OCR reuse, page selection |
- Tokens: ~5 pages × 1.5k + images → ~12k in / 1k out per doc → 250k docs → 3B tokens/day.

## §4 HLD
```
[SW] Intake (portal upload, email parser, API) -> S3 + claims row -> [SW] queue
  workers (workflow engine: Temporal or Step Functions):
    [AI] classify doc type (Flash)          -> [SW] route to per-type extractor
    [AI] extract fields w/ confidence + bbox (OCR + LLM, JSON schema)
    [SW] validate: schema, cross-doc consistency, policy lookup (RDS), fraud rules
    [SW] decide: rules table (auto-approve / auto-deny / review) with reasons
    [SW] route: review queue (priority by $ and SLA) | pay (idempotent) | notify ([AI] letter draft, templated)
[SW] Review UI: side-by-side doc + fields (bbox highlight), corrections captured -> [AI] eval set
[SW] Postgres (claims, documents, fields+provenance, decisions, reviews, evals) · [SW+AI] Langfuse
```

## §5 Components — problem → design
- **Intake `[SW]`:** dedup by content hash; virus scan; page split; email attachments fan-out; idempotent claim creation by `(channel, external_id)`.
- **Classification + extraction `[AI]`:** per doc type a JSON schema; prompt = schema + few-shot + page images; output validated; each field gets `confidence` (model-reported *and* consistency-derived: OCR agreement, regex validity, cross-doc match). Long docs: page selection via OCR keyword heuristics before LLM.
  - **L5:** model self-reported confidence is poorly calibrated; calibrate against reviewer corrections (reliability diagram) and set thresholds per field per doc type by cost of error.
- **Validation `[SW]`:** hard rules (dates ordered, totals sum, policy active, claimant matches policy); mismatches lower confidence or force review; fraud rules (duplicate invoice numbers, image reuse hash).
- **Decision `[SW]`:** rules table versioned (`decision_rules(version, condition, outcome, reason)`); outcomes: auto-approve ≤ $1k & all critical fields ≥ τ; auto-deny on hard policy exclusions (still human-visible); else review. Every decision stores rule version + inputs → explainable.
- **HITL queue `[SW]`:** priority = f($, SLA, confidence); reviewer sees fields with bbox highlights; corrections written as `field_corrections` → nightly eval + threshold recalibration; second reviewer for > $10k.
- **Payout `[SW]`:** idempotency key `claim_id:decision_version`; payment API key; ledger row before call; reconciliation job.
- **Reviewer copilot `[SW+AI]`:** the one agentic step: Q&A over the claim file with retrieval of doc pages; read-only; answers cite page/bbox.
- **Evals `[AI]`:** labeled set per doc type (500 docs each for top-5 types); field F1, STP rate at fixed error; CI gate on prompt/model change; shadow mode for new extractor versions (run both, compare) before promotion.

## §6 API / schema
- `POST /claims` (multipart or refs) · `GET /claims/{id}` · `POST /claims/{id}/review {corrections, decision}` · `GET /queues/review?priority`
- `documents(claim_id, s3_uri, type, type_conf, pages)` · `fields(doc_id, name, value, confidence, bbox, page, model_version)` · `decisions(claim_id, outcome, rule_version, inputs JSONB, reasons[])` · `reviews(claim_id, reviewer, corrections JSONB)` · `payouts(claim_id, idem_key UNIQUE, amount, status)`

## §7 Hygiene
| Concern | Answer |
|---|---|
| AuthZ | reviewers by region/line; PII masked outside role |
| Idempotency | intake hash; payout key; workflow steps idempotent |
| Timeouts/retries | extraction retry ×2 on transient; never retry payout blindly |
| Backpressure | queue depth → autoscale; SLA-based priority |
| Consistency | claims ledger strong; eval store eventual |
| Deploy | extractor versions shadow → canary → promote; rules versioned |
| Retention | docs per regulation (7 y); traces redacted 30 d |

## §8 Failure → fallback
- OCR/LLM down → queue holds; SLA alert; manual mode · Low confidence → review · Cross-doc conflict → review with diff · Payment API fail → ledger pending, retry with same key · Schema violation → re-extract once → review.

## §9 Pop-up questions
1. **Why not an agent?** — Fixed steps; agency adds non-determinism to a regulated decision. Workflow with LLM steps.
2. **Model reads the amount wrong?** — Confidence + cross-checks (OCR agreement, totals sum) → review; calibrated thresholds.
3. **Double payout?** — Idempotency key + ledger-before-call + reconciliation.
4. **Explain a denial to a regulator?** — Decision row: rule version, inputs with provenance (doc, bbox, model version).
5. **New document type appears?** — Classifier "unknown" → review; corrections seed a schema; shadow extractor.
6. **How do you improve STP safely?** — Lower thresholds per field where calibrated error cost allows; measure error rate; never blanket.
7. **L5: fine-tune or prompt?** — Prompt + schema first; fine-tune only top doc types with ≥ 5k labels and stable layouts; keep eval identical.
8. **L5: fraud?** — Deterministic rules + anomaly features; LLM summaries for investigators, not decisions.

## §10 Trade-offs + defeaters
| Decision | Chosen | Alt | Flips |
|---|---|---|---|
| Control | workflow (L2) | agent | never for payouts |
| Engine | Temporal/Step Functions | custom queue | very small volume |
| Extraction | OCR + LLM JSON | LLM-only vision | short docs, low volume |
| Decisions | rules table | model decides | never |
- Defeaters: "agent decides claims" · "fine-tune first" · "confidence from the model is enough".

## §11 MVP ladder
- MVP0: one doc type, upload → extract JSON → rules → review UI; no payouts.
- MVP1: workflow engine, queue, confidence + validation, idempotent payouts ≤ $1k.
- MVP2: 5 doc types, calibration from corrections, shadow extractor versions, eval gate.
- MVP3: reviewer copilot, fraud rules, SLA-priority queues.

## §12 Memorization card
- Pitch: LLM extraction with per-field confidence feeding a versioned rules engine; humans review what the numbers can't justify.
- Autonomy: L2 workflow; one read-only agentic copilot; no trigger for L3 on the decision path.
- Numbers: 250k docs/day · F1 98% · $1k auto cap · STP 8% review · $0.20/claim.
- Failures: mis-extracted amount · double payout · unexplainable decision.
- Defeaters: agent decides · fine-tune first · uncalibrated confidence.
- MVP0→1→2: one-type extract+rules+review → workflow + idempotent pay → calibration + shadow + evals.
- Done when: argue workflow-not-agent in 30 s · explain confidence calibration · draw provenance schema.

## References
1. https://github.com/temporalio/samples-python
2. https://cloud.google.com/document-ai/docs
3. https://ai.google.dev/gemini-api/docs/structured-output
4. https://github.com/google/adk-python
