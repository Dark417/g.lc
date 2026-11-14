# 05 · Evals and OpenTelemetry

## Evals: one harness, plus each ecosystem's native evaluator

### Our harness (`app/evals/`)

- **Cases**: `backend/evals/cases.yaml`.

```yaml
- id: calc-percent
  input: "What is 17% of 2340? Use the calculator."
  expect:
    tools: [calculator]          # trajectory: these tool names must appear (any order)
    contains: ["397.8"]          # answer must contain
- id: docs-agentcore-memory
  input: "What does AgentCore Memory store? Search the docs and cite the source file."
  expect:
    tools: [search_docs]
    contains: ["agentcore"]
    rubric: "Mentions short-term events and long-term memory records, and cites a corpus file."
```

- **Targets**: `framework:pattern:provider`, e.g. `adk:single:raw`, `strands:swarm:bedrock`. They run through `RunService`: the same entrance, the same events.
- **Scorers** (pure functions over `RunResult`):

| Scorer | Measures | Needs a model? |
|---|---|---|
| `tool_trajectory` | recall of expected tool names in `tool_call` events; precision reported too | no |
| `contains` | case-insensitive substring match on the final output | no |
| `latency` / `tool_calls` | wall time, number of tool calls | no |
| `llm_judge` | 1–5 against `rubric`, judged by `JUDGE_MODEL` (Claude) | yes |

- **Output**: a framework × case matrix in Markdown and JSON (`evals/out/`).
- **Running it**:

```bash
uv run python -m app.evals.run --targets adk:single:raw,langgraph:react:raw,strands:single:raw,claude:messages_api:raw
uv run pytest -m eval   # opt-in; needs keys
```

- **Keyless CI**: the harness itself is tested with scripted adapters, so scorers and the matrix are covered without models.

### Native evaluators (how each ecosystem does it)

| Ecosystem | Tool | What we ship |
|---|---|---|
| ADK | `AgentEvaluator.evaluate()` on `.evalset.json` (`tool_trajectory_avg_score`, `response_match_score`) | `evals/adk/research.evalset.json` + `tests/test_eval_adk.py` (`-m eval`) |
| Vertex | Gen AI evaluation service: `vertexai.evaluation.EvalTask` with pointwise metrics on a dataset of `{prompt, response, reference}` | `app/evals/vertex_eval.py` turns our harness results into an `EvalTask` dataset and runs it |
| AgentCore | AgentCore Evaluations: online/on-demand evaluators over AgentCore Observability traces | `infra/aws/README.md` section 7; spans from AgentCore Runtime feed it |
| LangGraph | LangSmith `evaluate()` / `agentevals` trajectory matchers | Noted only. Our trajectory scorer is the same idea without a SaaS dependency |
| Strands | `strands-agents-evals` | Noted only, same reason |

- **Why build a harness at all**:
  - The native evaluators each read their own trace or session format.
  - Comparing frameworks needs one input format and one event format. Our wire contract already is that.

## OpenTelemetry

### One provider, many emitters

```
FastAPI span (opentelemetry-instrumentation-fastapi)
 └─ agent.run  {agent.framework, agent.pattern, agent.provider, session.id, enduser.id}
     ├─ ADK:       invoke_agent / call_llm / execute_tool        (ADK native, OTel GenAI semconv)
     ├─ LangGraph: LangGraph / ChatModel / Tool spans            (OpenInference LangChain instrumentor)
     ├─ Strands:   invoke_agent / chat / execute_tool            (Strands native, GenAI semconv)
     ├─ Claude SDK: CLI exports claude_code.* spans, metrics, and logs itself (env passthrough)
     └─ Messages API: Anthropic spans                            (OpenInference Anthropic instrumentor)
```

- `app/telemetry.py` builds **one** global `TracerProvider` and `MeterProvider` at startup.
  - ADK and Strands use the global provider automatically. They emit GenAI semantic-convention spans.
  - LangChain/LangGraph and the Anthropic SDK are instrumented with OpenInference instrumentors.
  - The **Claude Agent SDK** runs a CLI subprocess with its own exporter. We pass `CLAUDE_CODE_ENABLE_TELEMETRY=1`, `OTEL_*_EXPORTER=otlp`, `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_RESOURCE_ATTRIBUTES=session.id=…` through `ClaudeAgentOptions(env=…)`.
    - Its spans arrive in the same backend, correlated by `session.id`.
- **Metrics** (ours):
  - `agent.runs` counter, by framework / pattern / provider / outcome;
  - `agent.run.duration` histogram.

### Exporters (`OTEL_EXPORTER`)

| Value | Goes to | Use |
|---|---|---|
| `none` | nowhere | tests (default) |
| `console` | stdout | quick look |
| `otlp` | `OTEL_EXPORTER_OTLP_ENDPOINT` (collector) | local Jaeger via `deploy/docker-compose.yaml`; on AWS the ADOT collector → X-Ray / CloudWatch |
| `gcp` | Cloud Trace (`opentelemetry-exporter-gcp-trace`) | Cloud Run / GKE |

- **Content capture**: prompt and response text in spans is **off** by default (`OTEL_CAPTURE_CONTENT=false`). Traces often outlive the retention policy of the data in them.

### Local stack

- `docker compose -f deploy/docker-compose.yaml up`:
  - `backend`;
  - `otel-collector`: OTLP in; Jaeger and a debug exporter out;
  - `jaeger` UI on `:16686`.
- Phoenix (`arize-phoenix`) is a drop-in alternative OTLP target. It renders OpenInference LLM spans richly. There is a commented service in the compose file.
