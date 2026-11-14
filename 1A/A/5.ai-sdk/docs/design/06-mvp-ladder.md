# 06 · MVP ladder

Each rung is a vertical slice you can demo with `curl`. Build in this order.

| Rung | Demo | Adds | Why this order |
|---|---|---|---|
| **MVP0** | `POST /v1/runs {"framework":"adk","pattern":"single","provider":"raw"}` → answer with a `calculator` tool call in `events` | FastAPI entrance, `AdapterRegistry`, event contract, session lock, `RunScope`, neutral tools, ADK `single` | Proves the one-entrance contract with the framework the repo already knows |
| **MVP1** | Same request with `"framework": "langgraph" \| "strands" \| "claude"` | One adapter per framework, `single`-equivalent pattern each, tool wrappers | The registry is only proven when a second framework plugs in without touching the core |
| **MVP2** | `"pattern": "sequential" \| "swarm" \| "supervisor" \| "subagents" ..."` | All multi-agent patterns per framework | The "main components" of each framework, the core of the brief |
| **MVP3** | Agent searches docs, browses a URL, runs `date`, files a ticket over MCP | RAG, CLI, Playwright, MCP server and clients, Playwright MCP | External tools, wired the same way into all four |
| **MVP4** | `"provider": "bedrock"` and `"vertex"` | Provider profiles: models, AgentCore Memory, Bedrock KB, AgentCore Browser and Code Interpreter, Agent Engine Sessions and Memory Bank, RAG Engine, guardrails | Cloud last *within the code*: every pattern already works, so a cloud failure is a config problem, not a design problem |
| **MVP5** | Trace in Jaeger; eval matrix printed | OTel setup, eval harness, native evaluators | Measurement once behaviour exists |
| **MVP6** | Same image on k8s; AgentCore Runtime and Agent Engine entrypoints | Dockerfile, compose, k8s, CI, runtime wrappers, provisioning scripts | Deployment last; nothing above depends on it |
| **MVP7** | Crash a run and recover it; fork from a checkpoint; recall across sessions; two replicas share one Redis | State suites per branch (`diy:loop`, `langgraph:memory`, `adk:memory`), Strands/Claude unique parts, cache servers, state API | State is where agents break in production. It comes after the patterns exist, so each suite can reuse them |

## Commit plan (one commit per step, pushed)

1. Design docs (this folder).
2. Backend core: entrance, registry, contracts, providers, tools, MCP server, RAG, memory, guardrails, telemetry, tests.
3. ADK adapter: 7 patterns + tests.
4. LangGraph adapter: 6 patterns + tests.
5. Strands adapter: 5 patterns + tests.
6. Claude adapter: 4 patterns + tests.
7. Evals, deploy (compose, k8s, runtimes, infra scripts), CI, README / AGENTS / DEPLOY.
8. State suite: design doc 07, then cache server + state API, then one suite per branch, then the Strands / Claude unique parts.

## Explicitly deferred

- A real frontend (the playground page is enough to explore).
- Streaming token deltas for every framework. Adapters emit `message` per agent turn. Token-level `delta` only where the framework streams cheaply (ADK, Strands).
- Durable distributed session lock (documented PRODUCTION swap).
- Terraform for AWS and GCP managed agent services. Provisioning is by script, because several of these APIs are newer than the providers' Terraform coverage.
