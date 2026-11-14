# Evals

Project 2 used ADK's evaluator. Here the harness is written by hand (`app/evals/harness.py`) so the moving parts are visible:

1. **Runner**: sends the case input through the real `ClaudeChatService` and collects the reply + trace.
2. **Trajectory check**: every `expected_tools` entry must appear (by suffix) among the `tool_call` events. Subagent calls show up as the built-in `Task` tool; tools inside subagents are not visible to the root trace, which is why the DB/RAG cases only assert `Task`.
3. **LLM judge**: `claude` grades the reply against the case's `rubric` with structured output (`Verdict{score, reasoning}`), and the case passes if `score >= min_score`.

`evals/cases.json` holds the cases. `min_score` is per case.

## Run

```bash
export ANTHROPIC_API_KEY=...
uv run python -m app.evals.run            # table + JSON report in data/generated/eval-report.json
# or
uv run pytest -m eval -s
```

The default `pytest` run exercises the harness with fakes (no key).

## What ADK gave you for free that you now own

- Case authoring UI (`adk web` -> Eval tab). Here: edit JSON.
- Multiple runs per case and averaging. Here: run the suite N times yourself.
- Rubric-based metrics with tuned judge prompts. Here: one judge prompt, tune it.
- Result persistence. Here: one JSON file.

That's the build-vs-buy tradeoff in one paragraph.
