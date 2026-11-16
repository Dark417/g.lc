# 1harness — The Harness, And How Loop And Graph Fit Inside It

> What a harness is, what's in it, and how loops and graphs nest inside it. Then how to choose a shape in a system design.
> Group 1 (agent core). Siblings: [1loop.md](1loop.md), [1graph.md](1graph.md), [1architecture.md](1architecture.md), [1orchestration.md](1orchestration.md).
> Concept level, no code (AGENTS.md §8b). Last updated: 2026-11-16.

## Index
- [0. One-minute version](#0-one-minute-version)
- [1. Concept](#1-concept)
- [2. What's inside a harness](#2-whats-inside-a-harness)
- [3. Harness, loop, graph: how they relate](#3-harness-loop-graph-how-they-relate)
- [4. The different ways people define them](#4-the-different-ways-people-define-them)
- [5. Design paradigms](#5-design-paradigms)
- [6. System design view: choosing a shape](#6-system-design-view-choosing-a-shape)
- [7. Failure modes](#7-failure-modes)
- [Where this fits](#where-this-fits)
- [References](#references)

---

## 0. One-minute version
- **What:** the harness is all the software around the model: prompt, tools, context, memory, permissions, control flow, tracing.
- **Why:** the model only predicts text. The harness turns that into actions that are safe, bounded and observable.
- **How:** the harness runs a control flow. That flow is a loop (the model decides the next step), a graph (your code decides), or one inside the other.
- **Catch:** more model control handles more cases but costs more, varies more, and is harder to test.
- 🗣 "Agent equals model plus harness. The harness is the product; the loop and the graph are two ways it decides what happens next."

---

## 1. Concept
`AI`

- **Plain idea:** the model is an engine. The harness is the rest of the car: steering, brakes, dashboard, and the rules of the road.
- **Picture it:** the same model inside two harnesses.
  - Harness A: one prompt, no tools, no limits. It answers, sometimes wrongly, and can't act.
  - Harness B: tools, retrieval, step limits, approval before writes, a trace per run. Same model, a usable product.
- **How it works**
  1. A request arrives. The harness builds the context: instructions, tools, relevant data, history.
  2. It calls the model and reads the reply: text or a tool call.
  3. It checks the reply against permissions and guardrails, then runs the tool or returns the answer.
  4. It records everything in a trace and updates state.
  5. Its control flow decides what comes next: another turn, the next node, a pause for a human, or stop.
- **The catch**
  - Most agent failures are harness failures: wrong context, vague tools, no stop condition, no permission check.
  - A better harness often beats a bigger model, but it's real engineering work.
- 🗣 "When an agent misbehaves, I look at the harness before I blame the model."

---

## 2. What's inside a harness
`boundary` ★★★

```
  request -> [ context manager ] -> model -> [ output parser ] -> [ policy check ] -> [ tool router ] -> world
                  ^                                                                         |
                  └──────────── state / memory <──── tracing on every step <────────────────┘
                      control flow (loop | graph) decides: next turn, next node, pause, stop
```

| Part | Job | Lives in which file |
|---|---|---|
| Model interface ★★ | one port for all providers; fallback model | [1architecture.md](1architecture.md) |
| Context manager ★★★ | decides what goes into the window each turn | 2context.md |
| Tool router ★★★ | validate args, check permission, run, shape the result | 3tools.md |
| State and memory ★★ | session state, checkpoints, long-term facts | 2memory-state.md |
| Control flow ★★★ | loop, graph, or both | [1loop.md](1loop.md), [1graph.md](1graph.md) |
| Hooks ★★ | deterministic code before and after model and tool calls | this doc §5 |
| Guardrails and approval ★★★ | block, redact, pause for a human | 4guardrails.md, 4access.md |
| Tracing ★★★ | every step, token, tool call and cost recorded | 4observability.md |

- **Hooks deserve a word:** they're plain code at fixed points.
  - Before a tool runs: check permission, redact, log.
  - After the model replies: validate schema, count tokens.
  - They're how you add rules the model can't skip.
  - Names differ by framework: ADK callbacks, Claude Agent SDK hooks, LangGraph nodes or middleware.
- 🗣 "Hooks are where the rules live. The model can ignore a prompt; it can't skip a hook."

---

## 3. Harness, loop, graph: how they relate
`AI` ★★★

- **Plain idea:** the harness is the container. Loop and graph are two styles of control flow it can run.
  - **Loop:** the model decides the next step, again and again, until done.
  - **Graph:** your code fixes the steps and the allowed moves between them.

### 3.1 Which contains which

```
  HARNESS (always)
  └── control flow
      ├── loop only               the model picks every step
      ├── graph only              fixed steps, LLM calls inside some steps
      ├── graph, loop in a node   fixed stages, freedom inside a stage
      ├── loop, graph as a tool   free agent that can call a fixed sub-flow
      └── graph of loops          several agents wired together (orchestration)
```

- **A loop is the simplest graph:** one node with an edge back to itself.
- **A graph with a cycle contains a loop.** For example, "write, review, rewrite until approved".
- **Both run inside a harness.** The harness supplies context, tools, state, policy and tracing to every node and every turn.

### 3.2 What can exist without what

| Thing | Needs a harness? | Needs a loop? | Needs a graph? |
|---|---|---|---|
| Single model call | thin one (prompt + parser) | no | no |
| Workflow (fixed steps) | yes | no | yes, usually a straight line or DAG |
| Single agent | yes | yes | no; formally a one-node graph |
| Enterprise process agent | yes | inside nodes | yes |
| Multi-agent system | yes, often one per agent | per agent | yes, the wiring between agents |

- Every agent has a harness, even a tiny one.
- A loop needs no graph framework. It's a bounded `while` around the model call.
- A graph needs no model-driven loop. A DAG of LLM calls is a workflow, not an agent.

### 3.3 The two nestings that matter in practice

- **Loop inside a graph node** ★★★ (the enterprise default)
  - Picture: a claims process with fixed stages: intake, check policy, decide, notify.
  - Inside "check policy", a small agent loop searches documents until it has an answer.
  - Why: stages are auditable; only the fuzzy part is free.
- **Graph inside a loop, as a tool** ★★
  - Picture: a support agent loops freely, but "issue refund" is a tool backed by a fixed workflow with checks and approval.
  - Why: the agent decides *when*; the workflow controls *how*.
- 🗣 "Graph for the process, loops inside the fuzzy steps, and a fixed workflow behind any risky tool."

---

## 4. The different ways people define them
`AI` ★★

- These words are used loosely. Say which meaning you mean.

| Term | Common meanings | Where you hear it |
|---|---|---|
| Agent | (a) a model using tools in a loop; (b) any LLM-powered app; (c) one node in a multi-agent graph | Anthropic uses (a); marketing uses (b) |
| Harness | (a) everything but the model; (b) the loop runner; (c) a test or eval rig | (a) in agent engineering; (c) in benchmarks ("eval harness") |
| Scaffold | the code around a model in a benchmark run | research papers, SWE-bench |
| Runtime | (a) the loop engine (ADK Runner); (b) the hosting platform (Bedrock AgentCore Runtime, Vertex Agent Engine) | two different layers; ask which |
| Workflow | fixed steps in code; the model doesn't choose the path | Anthropic's "workflows vs agents" |
| Graph | (a) a state machine with nodes and edges (LangGraph); (b) any wiring of agents | LangGraph, ADK graph workflows |
| Orchestration | (a) the control flow inside one agent; (b) coordinating many agents | context decides |

- **Anthropic's split:** workflows (code paths you write) vs agents (the model directs its own process and tool use).
- **"Agent = model + harness":** common in harness-engineering writing; the model is swappable, the harness is the product.
- **Loop engineering:** stacking loops on the base agent loop: verification loops, event-driven runs, and loops that improve the harness from traces. See [1loop.md](1loop.md).
- 🗣 "When someone says 'runtime', I ask: the loop engine, or the place it's hosted? They're different layers."

---

## 5. Design paradigms
`boundary` ★★★

- **Plain idea:** frameworks differ mostly in who owns the control flow.

| Paradigm | Who decides the next step | Examples | Good at | Weak at |
|---|---|---|---|---|
| Model-driven loop | the model, with tools and a prompt | Claude Agent SDK, Strands, OpenAI Agents SDK | open-ended tasks, fast to build | hard to audit, variable cost |
| Explicit graph (code-driven) | your code, with LLM steps inside | LangGraph, ADK workflow agents and graphs | audit, resume, approvals | more upfront design |
| Declarative / configured | a config or console setup | Bedrock Agents, ADK agent config | quick standard agents | escape hatches when needs grow |
| Durable workflow engine | a general workflow engine, LLM calls as steps | Temporal, AWS Step Functions | long runs, retries, crash recovery | not agent-aware; you build the agent parts |

- **"Own your control flow"** (12-factor agents): treat the loop as normal software you can read, pause, branch and resume.
- **Real systems mix paradigms:** a durable workflow engine outside, a graph for the process, model-driven loops inside nodes.
- 🗣 "The real choice isn't which framework. It's how much of the control flow I hand to the model."

---

## 6. System design view: choosing a shape
`boundary` ★★★

### 6.1 The deciding question
- **Is the path known before the run starts?**
  - Yes: workflow or graph.
  - Partly: graph with loops in the uncertain nodes.
  - No: agent loop, inside strong limits.

### 6.2 Pick and drop
- Start at row 1; move down only when a measured failure forces it.

| Step | Shape | Pick when | Drop when |
|---|---|---|---|
| 1 | Single call (+ retrieval) | one answer, one step | it needs actions or several steps |
| 2 | Workflow (chain, router, parallel) | steps known in advance | the path depends on what's found |
| 3 | Single agent loop + tools | open-ended, path unknown | it must be auditable step by step |
| 4 | Graph with loops in nodes | fixed stages, judgment inside each | stages keep changing |
| 5 | Multi-agent | context too big, or work runs in parallel | one agent passes the evals |

### 6.3 Other decisions the shape forces
- **State location:** keep the harness stateless and state in a store, so any worker can resume a run.
- **Long runs:** checkpoint after each step or node; put human pauses on a durable store, not a blocked thread.
- **Risky actions:** route them through fixed workflows with approval, even inside a free loop.
- **Cost:** loops multiply calls. Set step, token and time budgets per run.
- **Framework fit:** model-driven SDKs for coding or file agents; LangGraph or ADK graphs for business processes; a workflow engine when runs last hours or days.

### 6.4 Tools at hand

| Need | Options |
|---|---|
| Loop runner | Claude Agent SDK, Strands, OpenAI Agents SDK, ADK `LlmAgent`, plain code |
| Graph runtime | LangGraph, ADK workflow agents and graphs, Strands graph patterns |
| Durable execution | LangGraph checkpointers, Temporal, Step Functions |
| Hosting | Bedrock AgentCore, Vertex AI Agent Engine, your own container service |

- Default: one agent loop with strict limits, or a graph with loops inside nodes when the process has fixed stages. Go multi-agent only when evals show one agent can't do it.

---

## 7. Failure modes
`boundary`

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Runaway loop | no or weak stop condition | step count and cost per run spike | step, token and time budgets; a done signal |
| Wrong shape | free loop for a fixed process | inconsistent paths for the same task | move fixed steps into a graph |
| Rules in the prompt only | policy written as instructions | policy violations in traces | move rules into hooks and tool checks |
| Lost progress | state only in process memory | runs restart from zero after a crash | external state and checkpoints |
| Blurry terms | "runtime" or "agent" meaning different things | design reviews talk past each other | define terms in the design doc |

---

## Where this fits
- **Place:** L5 of [1a-bp.md](../1a-bp.md), the center of agent design. The other group-1 docs zoom into parts of it.
- **Time it deserves:** the first doc to read before an agentic design interview. About 30 minutes.
- **I should be able to…**
  - Name the harness parts and what each prevents.
  - Draw the five control-flow shapes and when each fits.
  - Explain loop-in-graph vs graph-in-loop with one example each.
  - Say which word ("runtime", "agent") I mean, and why it matters.

## References
1. [Anthropic — Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) — workflows vs agents.
2. [Harness engineering vs loop engineering](https://danicasimic.substack.com/p/harness-engineering-vs-loop-engineering) — how harness, loop and graph nest.
3. [HumanLayer — 12-factor agents](https://github.com/humanlayer/12-factor-agents) — own your control flow.
4. [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview) — graphs, checkpoints, interrupts.
5. [Google ADK — agents](https://google.github.io/adk-docs/agents/) — LLM agents and workflow agents.
