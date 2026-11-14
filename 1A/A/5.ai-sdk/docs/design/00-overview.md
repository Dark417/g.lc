# 00 · Overview

## Problem

- Four agent frameworks compete for the same job:
  - **Google ADK**
  - **LangGraph** (with LangChain v1 agents)
  - **Strands Agents** (AWS)
  - **Claude**: the Agent SDK, plus the raw Messages API tool runner
- Each one ships its own words for the same ideas:
  - agent, graph, swarm, sub-agent, workflow
  - session, checkpointer, memory, store
  - hook, callback, middleware, plugin
  - tool, toolset, MCP client
- Each one also integrates differently with the managed agent services of AWS and GCP.
  - AWS: Bedrock, AgentCore.
  - GCP: Vertex AI, Agent Engine.
- Docs show each piece alone. Nobody shows **all of them wired together, side by side, behind one API**.

## What we build

- **One FastAPI service, one entrance** (`POST /v1/runs`).
- A **pluggable adapter registry**. Each framework is one adapter.
- Each adapter exposes **patterns**. A pattern is a small runnable demo of the framework's main components.
  - ADK: `LlmAgent`, `SequentialAgent`, `ParallelAgent`, `LoopAgent`, a custom `BaseAgent`, transfer and `AgentTool`, the ADK 2 graph `Workflow`.
  - LangGraph: the prebuilt ReAct agent, a hand-built `StateGraph`, `create_agent` with middleware, a supervisor, map-reduce with `Send`, human-in-the-loop with `interrupt`.
  - Strands: `Agent`, agents-as-tools, `Swarm`, `GraphBuilder`, structured output.
  - Claude: Agent SDK with hooks and permissions, subagents, external MCP servers, and the Messages API tool runner.
- **Three provider branches** for every pattern:
  - `raw`: direct model APIs; we own all state on local disk.
  - `bedrock`: AWS-managed model, memory, knowledge base, browser, code sandbox, guardrails, and tracing.
  - `vertex`: GCP-managed model, sessions, memory bank, RAG engine, safety, and tracing.
- **Shared, framework-neutral capabilities** that every adapter plugs in:
  - Tools: local Python, an allowlisted CLI, a Playwright browser, and a code sandbox.
  - MCP: our own server, plus an external one (Playwright MCP).
  - RAG: local store, Bedrock Knowledge Base, or Vertex RAG Engine.
  - Session lock, sessions, and long-term memory.
  - Guardrails.
  - OpenTelemetry tracing.
  - An eval harness that scores every framework × pattern × provider the same way.

## Who it's for

- An engineer choosing between these frameworks.
- An engineer who must make an agent work on AWS or GCP managed services, not just a laptop.
- Readers of projects 1–4. This project generalises them: project 2 was ADK only, project 3 was Claude only.

## Success metrics

- **Coverage**: every cell of the component matrix (`02-component-matrix.md`) is one of:
  - implemented in code,
  - or marked as a documented gap with the reason.
- **One contract**: all adapters return the same event stream. A client or eval never branches on the framework.
- **Keyless tests**: `uv run pytest` runs every pattern of every framework end to end with scripted models. No API key, no cloud account.
- **Cloud switch is config only**: going `raw` → `bedrock` → `vertex` changes env vars, not code paths in the patterns.
- **Observable**: one request produces one trace. The trace covers HTTP → adapter → agent → model and tool spans, in Jaeger locally and Cloud Trace or X-Ray in the cloud.

## Non-goals

- A product. The demo domain ("engineering research assistant") is there to make the tools meaningful.
- A rich UI. A static playground page plus OpenAPI `/docs` is enough. The API is the product.
- Benchmarking framework speed or quality. The eval harness exists to show *how* to evaluate, not to crown a winner.
- Full IaC for every managed service. We provide provisioning scripts and the exact console or CLI steps instead.
- Multi-tenant auth. `user_id` is taken from the request, as in a trusted internal service.

## Build vs buy

| Need | Choice | Why |
|---|---|---|
| Agent loop | **Buy**: each framework | That is the point of the project. |
| One entrance across frameworks | **Build**: a thin adapter registry | Neither LiteLLM nor any framework normalises *agent* events across ADK, LangGraph, Strands, and Claude. |
| Model routing | **Buy**: each framework's native model class | Shows how each one targets Bedrock and Vertex. LiteLLM appears only where ADK needs it for Bedrock. |
| Sessions and memory | **Buy** per provider | AgentCore Memory, Agent Engine Sessions, and Memory Bank are the "managed structures" we want to see. |
| RAG index | **Buy** in cloud, build locally | Bedrock KB and Vertex RAG Engine in cloud; an illustration hashing store locally. |
| Tracing | **Buy**: OpenTelemetry | Every framework emits or can emit OTel. One exporter config covers all of them. |
| Eval harness | **Build** a thin harness; **buy** native evaluators | One scorer across frameworks; we also show ADK `AgentEvaluator`, Vertex Gen AI eval, and AgentCore Evaluations. |

## Challenge to the brief (read this)

- **"Every framework × every branch."**
  - 4 frameworks × ~6 patterns × 3 providers is about 70 combinations.
  - Writing 70 demos would be bloat. Instead:
    - Patterns are written **once per framework**.
    - The provider is injected through a **provider profile**: model class, session backend, memory, RAG, browser, guardrail.
    - So a pattern runs on all three branches with no `if provider == …` inside it.
  - Where a framework has a *native* cloud integration, the profile picks it. Examples:
    - Strands + `AgentCoreMemorySessionManager`.
    - ADK + `VertexAiSessionService`.
    - LangGraph + `AgentCoreMemorySaver`.
  - Where it has none, we say so in the matrix, not hide it.
- **"Claude SDK on Bedrock and Vertex."**
  - The Agent SDK runs the Claude Code CLI as a child process.
  - Bedrock and Vertex are therefore selected by **environment variables**, not client objects.
  - Its sessions are local JSONL files. No AWS or GCP session service plugs into it.
  - We map our session id to the CLI session id and resume it. We also show the Messages API path, which accepts real Bedrock and Vertex client objects.
- **"Exhaustive."**
  - Exhaustive *components*, minimal *code per component*.
  - Each component appears once, in the pattern where it is most natural, and is named in the catalog (`GET /v1/catalog`).
  - So you can find it.

## Documents in this folder

| File | Covers |
|---|---|
| `01-architecture.md` | One entrance, adapter contract, event model, request flow, code layout |
| `02-component-matrix.md` | Every framework's components, which pattern shows each, and support per provider |
| `03-cloud-branches.md` | What `raw`, `bedrock`, and `vertex` swap: model, sessions, memory, RAG, browser, sandbox, guardrails, runtime, tracing |
| `04-tools-mcp-rag-state.md` | Neutral tools and how each framework wraps them, CLI allowlist, Playwright, MCP, RAG, session lock, memory |
| `05-evals-and-otel.md` | Eval harness, native evaluators, OTel setup per framework |
| `06-mvp-ladder.md` | Build order and why |
| `07-state-and-memory.md` | Checkpoints, recovery, conversation vs context, long-term memory, history, cache servers; one suite per branch |
