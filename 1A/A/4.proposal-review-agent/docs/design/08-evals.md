# 08 · Evals

## What we measure

| Layer | Test | Needs a model? | Where |
|---|---|---|---|
| Verdict aggregation | Exhaustive table tests of `aggregate()` | no | `tests/test_verdicts.py` |
| Validation | Hallucinated codes dropped, skipped hard rules ⇒ `unclear`, severity forced from DB | no | `tests/test_verdicts.py` |
| Pipeline wiring | AssessmentService with a scripted LLM | no | `tests/test_ingestion_assessment.py` |
| Role gating, memory, history, attachments | Real ADK loop with a scripted model | no | `tests/test_agent.py`, `tests/test_api.py` |
| Stores | pgvector, ADK sessions on Postgres, MongoDB | no (real servers) | `tests/test_stores.py` (integration) |
| **Verdict accuracy** | Golden proposals vs seed rules | **yes** | `evals/verdicts.json`, `python -m app.evals.run` |
| Agent behaviour | "can I…" triggers `assess_proposal`; answer leads with the verdict | yes | same runner, `--via-agent` |

## Golden set (`backend/evals/verdicts.json`)

Each case:

```json
{
  "id": "kids-app-no-consent",
  "proposal": "Launch a mobile game for 10-year-olds that collects email addresses without asking parents.",
  "expected_verdict": "NON_COMPLIANT",
  "must_cite": ["PRIV-003"],
  "must_not_verdict": ["COMPLIANT"]
}
```

Scoring per case:

- `verdict_match`: exact match with `expected_verdict`
- `citation_recall`: fraction of `must_cite` codes present in findings as `violated` or `unclear`
- `safety`: never produce a verdict in `must_not_verdict`

Suite pass criteria (from `00-overview.md`):

- verdict accuracy ≥ 90%
- **zero** safety failures
- mean citation recall ≥ 0.8

## Running

```bash
cd backend
uv run python -m app.cli seed            # loads sample rules + documents
uv run python -m app.evals.run           # AssessmentService directly (fast, isolates the pipeline)
uv run python -m app.evals.run --via-agent   # full agent loop (slower; also checks tool choice)
uv run pytest -m eval                    # same, as a test
```

## Why not only ADK's evaluator

- ADK's `tool_trajectory_avg_score` compares tool **arguments** exactly. The `proposal` argument is free text the model paraphrases, so it would fail on correct behaviour.
- The thing that matters here is the *verdict*, which is structured. We score it directly.
- ADK evalsets remain a good fit for conversational regressions later; `adk web` can record them from real sessions.

## Workflow

1. A reviewer disagrees with a verdict in production → copy the proposal into `verdicts.json` with the correct verdict.
2. Run the suite. Fix the rule text, the prompt, or the retrieval.
3. Re-run. Ship only when accuracy holds and safety is zero.
