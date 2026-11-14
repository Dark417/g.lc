# Evals

Evals answer "did the agent do the right thing" with data, not vibes. Two kinds here:

| Folder | What it checks | Metric | Needs |
|---|---|---|---|
| `tools/` | The root agent calls the right local tool with the right args | `tool_trajectory_avg_score` (exact name+args match), `response_match_score` (ROUGE vs expected text) | model |
| `knowledge/` | Policy answers are grounded in the knowledge base | `response_match_score` only (tool args like the search query are too free-form to match exactly) | model |

Each folder has a `test_config.json`; ADK reads criteria per folder. Thresholds are deliberately loose; tighten as you learn what the agent does.

## Run

```bash
uv sync --extra eval            # heavy deps, only for evals
export GOOGLE_API_KEY=...

# ADK CLI (nice table output)
uv run adk eval app/agents evals/tools/local_tools.evalset.json --config_file_path evals/tools/test_config.json
uv run adk eval app/agents evals/knowledge/policies.evalset.json --config_file_path evals/knowledge/test_config.json

# or via pytest (same evaluator)
uv run pytest -m eval -s
```

The default `pytest` run only validates the eval-set JSON files (no API key).

## Authoring cases

The easiest way: run `uv run adk web app/agents`, have the conversation, then in the Eval tab click "Add current session to eval set". It writes the same JSON format as the hand-written files here.

## Beyond this

- `final_response_match_v2` and `rubric_based_final_response_quality_v1` use an LLM judge; add them to `criteria` when ROUGE gets too crude.
- Track results over time: `--eval_storage_uri` (CLI) or `eval_set_results_manager` (Python) can persist runs.
- Run evals in CI on a schedule, not per PR (cost and flakiness).
