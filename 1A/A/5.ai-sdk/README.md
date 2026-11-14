# 5.ai-sdk — four agent frameworks, three clouds, one entrance

One FastAPI service. One endpoint (`POST /v1/runs`). Pluggable adapters:

| Framework | Patterns (each shows a set of the framework's main components) |
|---|---|
| **Google ADK** (`adk`) | `single` · `sequential` · `parallel` · `loop` · `coordinator` · `custom` · `workflow` · `memory` |
| **LangGraph** (`langgraph`) | `react` · `graph` · `middleware` · `supervisor` · `map_reduce` · `hitl` · `memory` |
| **Strands Agents** (`strands`) | `single` · `agents_as_tools` · `swarm` · `graph` · `structured` · `memory` |
| **Claude** (`claude`) | `agent_sdk` · `subagents` · `external_mcp` · `messages_api` |
| **No framework** (`diy`) | `loop`: the agent loop and all its state, built by hand |

Every pattern runs on three **provider branches**:

| Branch | Model | Sessions / memory | RAG | Browser / sandbox | Guardrail | Hosting | Tracing |
|---|---|---|---|---|---|---|---|
| `raw` | Claude API, Gemini API | SQLite, files | local store | local Chromium | regex | Docker / k8s | Jaeger |
| `bedrock` | Bedrock Converse, Claude in Bedrock | AgentCore Memory | Bedrock KB | AgentCore Browser, Code Interpreter | Bedrock Guardrails | AgentCore Runtime | X-Ray (ADOT) |
| `vertex` | Vertex Gemini, Claude on Vertex | Agent Engine Sessions, Memory Bank | RAG Engine | local Chromium | Model Armor | Agent Engine, Cloud Run | Cloud Trace |

All patterns share:

- **Tools**: calculator, time, RAG `search_docs`, `remember`/`recall`, allowlisted `run_cli`, Playwright `browse`, sandboxed `run_code`.
- **MCP**: our `workbench` server, plus Playwright MCP.
- One **event stream**.
- **OpenTelemetry**.
- An **eval harness**.

Start with [`docs/design/00-overview.md`](docs/design/00-overview.md). The component-by-component map is [`02-component-matrix.md`](docs/design/02-component-matrix.md).

## What you'll learn

- How each framework names and composes the same ideas:
  - agent, workflow, graph, swarm, sub-agent;
  - session, checkpointer, memory, store;
  - callback, hook, middleware, plugin.
- How each framework plugs into **AWS and GCP managed agent services**, and where it doesn't (documented gaps).
- How to put several frameworks behind **one API contract**, so clients and evals never branch on the framework.
- How to test all of it **without an API key**: scripted models per framework.

## Quickstart (local, `raw`)

```bash
cd 5.ai-sdk/backend
cp .env.example .env              # set ANTHROPIC_API_KEY and/or GOOGLE_API_KEY
uv sync
uv run playwright install chromium   # for the browse tool (or set PLAYWRIGHT_CHROMIUM_PATH)
uv run uvicorn app.main:app --reload
```

- Playground: <http://localhost:8000>. Pick a framework, pattern, and provider, then watch the events stream.
- API docs: <http://localhost:8000/docs>.

```bash
curl -s localhost:8000/v1/catalog | jq '.frameworks[] | {name, patterns: [.patterns[].name]}'

curl -s localhost:8000/v1/runs -H 'content-type: application/json' -d '{
  "framework": "langgraph", "pattern": "supervisor", "provider": "raw",
  "message": "What is 17% of 2340, and what does AgentCore Memory store?"}' | jq '.output, [.events[].type]'

# Human-in-the-loop: the graph pauses before run_cli...
curl -s localhost:8000/v1/runs -H 'content-type: application/json' \
  -d '{"framework":"langgraph","pattern":"hitl","message":"Run uname -s"}' | jq '.session_id, .events[-1]'
# ...and resumes when you approve
curl -s localhost:8000/v1/runs -H 'content-type: application/json' \
  -d '{"framework":"langgraph","pattern":"hitl","session_id":"<id>","resume":{"approve":true}}' | jq .output
```

- With tracing: `docker compose -f deploy/docker-compose.yaml up --build`. Traces appear at <http://localhost:16686>.

## State and memory (one suite per branch)

The `memory` patterns and `diy:loop` show every layer of agent state. Details: [`docs/design/07-state-and-memory.md`](docs/design/07-state-and-memory.md).

| Layer | `raw` · `diy:loop` | `bedrock` · `langgraph:memory` | `vertex` · `adk:memory` |
|---|---|---|---|
| Checkpoint per step | SQLite + Redis write-through | AgentCore / DynamoDB + S3 / ElastiCache Valkey | resumable invocations on Agent Engine Sessions |
| Recover after a crash | `resume: {"recover": true}` | same → `astream(None)` | same → `run_async(invocation_id=…)` |
| Time travel | checkpoints + fork | `aget_state_history` + fork | invocations + `rewind_async` + fork |
| Context | window / token budget / summary / Anthropic compaction | `trim_messages` + `RemoveMessage` summary | `EventsCompactionConfig` |
| Long-term | LLM extract → consolidate → recall | `AgentCoreMemoryStore` | Memory Bank + `PreloadMemoryTool` |
| Cache server | Redis: lock, checkpoint, LLM cache; prompt caching | Valkey checkpoints, `ValkeyCache` node cache | Memorystore lock; Gemini context cache |

- Strands adds `agent.state` and summarising conversation management.
- The Claude Agent SDK adds a `RedisSessionStore`, so CLI sessions resume on any replica.
- With `REDIS_URL` set, every framework shares a distributed session lock.

```bash
# crash a turn on purpose, then recover it: finished tool calls are not re-run
curl -s localhost:8000/v1/runs -H 'content-type: application/json' -d '{"framework":"diy","pattern":"loop",
  "message":"17% of 2340 and the UTC time?","options":{"crash_after_step":3}}' | jq '.session_id, .events[-1]'
curl -s localhost:8000/v1/runs -H 'content-type: application/json' \
  -d '{"framework":"diy","pattern":"loop","session_id":"<id>","resume":{"recover":true}}' | jq .output
# time travel
curl -s localhost:8000/v1/sessions/<id>/checkpoints | jq '.[] | {checkpoint_id, label}'
curl -s localhost:8000/v1/sessions/<id>/fork -H 'content-type: application/json' -d '{"checkpoint_id":"<cid>"}'
curl -s localhost:8000/v1/sessions/<id>/history
curl -s "localhost:8000/v1/users/demo-user/memories?framework=diy"
```

## Request and events

```jsonc
// POST /v1/runs  (or /v1/runs/stream for SSE)
{"framework": "adk", "pattern": "parallel", "provider": "vertex",
 "message": "...", "session_id": null, "user_id": "demo-user",
 "vendor": "anthropic",                // optional: Claude vs Gemini where the branch has both
 "resume": null,                       // LangGraph hitl
 "options": {"deny_tools": ["browse"], "mcp": true, "max_iterations": 3}}
```

- Events: `session`, `agent`, `tool_call`, `tool_result`, `delta`, `message`, `state`, `interrupt`, `done`, `error`.
- They are identical for every framework.
- A session is bound to one `framework:pattern:provider`.
  - A second concurrent request on the same session gets `409`.
  - So does reusing a session with another target.

## Going to the cloud

- The branches are selected per request.
- Configure the managed services you want. The ones you leave unset stay local.
  - AWS: [`infra/aws/README.md`](infra/aws/README.md): AgentCore Memory, KB, Guardrails, Browser, Code Interpreter, AgentCore Runtime.
  - GCP: [`infra/gcp/README.md`](infra/gcp/README.md): Agent Engine Sessions and Memory Bank, RAG Engine, Model Armor, Cloud Run, Agent Engine.
- Deploying the service: [`docs/DEPLOY.md`](docs/DEPLOY.md).

## Evals

```bash
uv run python -m app.evals.run --targets adk:single:raw,langgraph:react:raw,strands:single:raw,claude:messages_api:raw --judge
uv run pytest -m eval tests/test_eval_adk.py   # ADK's own AgentEvaluator on an .evalset.json
```

## Layout

```
5.ai-sdk/
  backend/            FastAPI + all four frameworks (one deployable)
    app/core          adapter contract, registry, session lock, RunScope
    app/adapters      adk/ langgraph/ strands/ claude/ diy/  (patterns, models, persistence, translation)
    app/state         cache-server client, LLM response cache
    app/providers     raw / bedrock / vertex profiles
    app/tools app/rag app/memory app/guardrails app/mcp   neutral capabilities
    app/runtimes      AgentCore Runtime + Agent Engine entrypoints
    app/evals         harness, scorers, Vertex eval
    data/corpus       the RAG corpus (notes on these frameworks and services)
    evals/            cases.yaml, ADK evalset
  deploy/             docker-compose (+ OTel collector, Jaeger), k8s/
  infra/aws infra/gcp provisioning scripts and steps
  docs/               design/ (start here), DEPLOY.md
```

## References

1. Repos:
   - [google/adk-python](https://github.com/google/adk-python) · [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) · [strands-agents/sdk-python](https://github.com/strands-agents/sdk-python) · [anthropics/claude-agent-sdk-python](https://github.com/anthropics/claude-agent-sdk-python)
   - [aws/bedrock-agentcore-sdk-python](https://github.com/aws/bedrock-agentcore-sdk-python) · [langchain-ai/langchain-aws](https://github.com/langchain-ai/langchain-aws) (incl. `langgraph-checkpoint-aws`) · [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp)
2. Docs:
   - [ADK](https://google.github.io/adk-docs/) · [LangGraph](https://langchain-ai.github.io/langgraph/) · [Strands](https://strandsagents.com/) · [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview)
   - [Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/) · [Vertex AI Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview)
   - [OpenTelemetry GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
3. Posts:
   - [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
   - [AWS: Introducing Strands Agents](https://aws.amazon.com/blogs/opensource/introducing-strands-agents-an-open-source-ai-agents-sdk/)
