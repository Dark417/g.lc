# 1graph — Workflows And Graphs

> Fixed control flow for agent systems: the workflow patterns, how a state graph works, and how graphs and loops combine.
> Group 1 (agent core). Container: [1harness.md](1harness.md). Model-driven sibling: [1loop.md](1loop.md).
> Concept level, no code (AGENTS.md §8b). Last updated: 2026-11-16.

## Index
- [0. One-minute version](#0-one-minute-version)
- [1. Concept](#1-concept)
- [2. The five workflow patterns](#2-the-five-workflow-patterns)
- [3. How a state graph works](#3-how-a-state-graph-works)
- [4. Graphs and loops together](#4-graphs-and-loops-together)
- [5. System design view: choosing and building a graph](#5-system-design-view-choosing-and-building-a-graph)
- [6. Failure modes](#6-failure-modes)
- [Where this fits](#where-this-fits)
- [References](#references)

---

## 0. One-minute version
- **What:** a graph is a set of steps (nodes) and allowed moves between them (edges), with shared state.
- **Why:** when the process is known, fixed paths are cheaper, faster, testable and auditable.
- **How:** each node does work (code or an LLM call) and updates state; edges, sometimes conditional, pick the next node.
- **Catch:** you must design the process upfront; when the real path doesn't fit, the graph gets complicated.
- 🗣 "I put what I know into the graph and only what I don't know into a loop."

---

## 1. Concept
`AI`

- **Plain idea:** a flowchart that runs. Boxes are steps, arrows are the allowed next steps.
- **Picture it:** an invoice process.
  - Extract fields (LLM), then validate totals (code).
  - If amount > $10k, go to manager approval (human); else go straight to payment.
  - Notify the vendor (code).
  - The model reads the messy PDF. Code and people decide what happens.
- **How it works**
  1. Define the state: the data every node can read and write.
  2. Define nodes: each is a function, an LLM call, an agent, or a human step.
  3. Define edges: fixed ("always go to B") or conditional ("if X, go to C").
  4. A runtime moves through the graph, saving state after each node.
  5. It stops at an end node, or pauses for a human and resumes later.
- **The catch**
  - Graphs need the process to be known. Discovery tasks don't fit.
  - Big graphs with many branches become hard to read and change.
- 🗣 "A graph is a flowchart that runs, with state saved after every box."

---

## 2. The five workflow patterns
`AI` ★★★

- **Plain idea:** most production "agents" are built from these five shapes (Anthropic's taxonomy).

| Pattern | Shape | Use when | Example |
|---|---|---|---|
| Prompt chaining | A, then B, then C, with checks between | the task splits into fixed steps | outline, check outline, write |
| Routing | classify, then send to one handler | input types need different handling | refund vs technical vs general; cheap vs strong model |
| Parallelization | several calls at once, then combine | subtasks are independent, or you want several votes | screen for policy while answering; best-of-N review |
| Orchestrator–workers | a lead model splits the task at runtime, workers do parts | subtasks can't be known in advance | change touching an unknown set of files |
| Evaluator–optimizer | generate, grade, revise until it passes | clear criteria and revision helps | translation with a critic |

- **Two of these blur into agents:**
  - Orchestrator–workers decides its subtasks at runtime, the bridge to multi-agent (see [1orchestration.md](1orchestration.md)).
  - Evaluator–optimizer is a bounded loop (see [1loop.md](1loop.md)).
- 🗣 "Chain, route, parallelize, orchestrate, evaluate. Most agents are a mix of these five."

---

## 3. How a state graph works
`boundary` ★★★

- **Plain idea:** a state graph adds memory and pause / resume to a flowchart.

| Piece | What it is | Why it matters |
|---|---|---|
| State | one typed record shared by all nodes | every node sees the same facts; easy to inspect |
| Node | one step: code, LLM call, agent or human | small, testable units |
| Edge | fixed move to the next node | known path |
| Conditional edge | code picks the next node from state | branching without the model deciding |
| Reducer | rule for merging updates, e.g. append to a list | parallel branches don't overwrite each other |
| Checkpoint | state saved after each node | resume after a crash; time-travel debugging |
| Interrupt | pause and wait for outside input | human approval without a blocked thread |
| Subgraph | a graph used as one node | reuse and hide complexity |
| Fan-out / fan-in | send work to many nodes, then join | parallel work over a dynamic list |

- **DAG vs cyclic graph**
  - DAG (no cycles): pure workflow; always finishes.
  - Cycles: retries, review loops, agent loops; needs stop conditions like any loop.
- **Checkpoints change the design**
  - A run can pause for a day and resume on another server.
  - Defeater: a node that resumes may run again from its start. Side-effecting nodes must be idempotent.
- **Where you meet it**
  - LangGraph: state graph with checkpointers, interrupts, subgraphs and fan-out.
  - Google ADK: workflow agents (sequential, parallel, loop); graph workflows in ADK 2.x.
  - Strands: graph and swarm patterns for multi-agent setups.
  - General workflow engines (Temporal, Step Functions): durable steps, not agent-aware.
- 🗣 "Checkpoints make runs resumable; idempotent nodes make resuming safe."

### 3.1 Thread, run and checkpoint, in a multi-user service
- **Thread** = the session. Its ID keys everything saved for that conversation.
- **Run** = one invocation on that thread. **Checkpoint** = a snapshot saved after each node.
- **Many users:** many threads in one shared checkpoint store. The graph code is shared and holds no per-user data.
- **Pause and resume:** an interrupt saves a checkpoint and stops. Resume loads the latest checkpoint for that thread, on any server.
- **Time travel:** load an older checkpoint to replay or fork a run. It's a debugging tool.
- **Costs:** checkpoints pile up (prune or set retention) and contain user data (encrypt, apply retention rules).
- **Not the same as long-term memory:** checkpoints belong to one thread. Facts that should cross threads go in a separate store ([1architecture.md](1architecture.md) §5).

---

## 4. Graphs and loops together
`AI` ★★★

```
  [intake] -> [classify] --refund--> [ refund node: agent loop over order tools ] -> [approve?] -> [notify]
                         --other---> [ answer node: RAG + single call ] ---------------------------> [notify]
```

- **Loop inside a node** (most common)
  - The graph fixes the stages; one node runs a small agent loop for the fuzzy part.
  - The loop's budget is the node's budget.
- **Graph inside a loop**
  - A free agent calls a tool that runs a fixed sub-workflow, e.g. a refund with checks and approval.
- **A cycle is a loop**
  - "Review, fix, review again" is a loop drawn as a graph. It needs a max-iterations exit.
- **Graph of agents**
  - Nodes are whole agents; edges are handoffs. That's multi-agent orchestration ([1orchestration.md](1orchestration.md)).
- 🗣 "The graph says which stages happen; the loop handles the parts nobody could script."

---

## 5. System design view: choosing and building a graph
`boundary` ★★★

### 5.1 Graph or loop?

| Signal | Lean graph | Lean loop |
|---|---|---|
| Steps known in advance | yes | no |
| Audit and compliance needs | high | low |
| Needs human approval mid-run | yes | possible, harder |
| Run length | minutes to days (with checkpoints) | seconds to minutes |
| Cost predictability needed | high | low |
| Task is exploration or research | no | yes |

- Default: a graph for any business process; loops only inside nodes that need discovery.

### 5.2 Decisions when building one

| Decision | Options | How to decide |
|---|---|---|
| Who picks the next step | code (conditional edges) vs an LLM router node | code when a rule exists; LLM router for fuzzy intent |
| State shape | one big state vs per-node inputs | one typed state; keep it small and versioned |
| Persistence | none, checkpoints, full durable engine | checkpoints for pauses; engine for hours or days with retries |
| Parallelism | fan-out per item vs sequential | fan-out for independent items; cap concurrency |
| Human steps | interrupt in graph vs separate ticket system | interrupt when the reviewer acts in the same app |
| Framework | LangGraph, ADK graph / workflow agents, Step Functions, Temporal, plain code | team stack and need for checkpoints and interrupts |

### 5.3 Tools at hand

| Tool | Type | Good at | Choose when |
|---|---|---|---|
| LangGraph | agent graph library | checkpoints, interrupts, mixing code and LLM steps | Python / JS team, complex agent flows |
| ADK workflow agents and graphs | agent framework | Gemini / Google Cloud, sequential and parallel steps | Google stack; ADK is already the harness |
| Step Functions | AWS workflow service | managed, visual, retries, long runs | AWS shop; steps are mostly service calls |
| Temporal | durable workflow engine | crash-proof long runs, code-first | runs last hours or days; many retries |
| Plain code | functions and if statements | simplest; no new dependency | small fixed flows |

- Default: plain code for small chains; LangGraph or ADK graphs when you need checkpoints and human pauses; a workflow engine when runs are long and must survive anything.

---

## 6. Failure modes
`boundary`

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Double side effect | node re-runs after resume or retry | duplicate payments or emails | idempotency keys; split side effects into their own node |
| Graph sprawl | every edge case becomes a branch | graph hard to read; changes break paths | subgraphs; move fuzzy branches into one agent node |
| Router misroutes | LLM router on unclear categories | wrong-handler rate in evals | rules first; clearer labels; an "other" route |
| Stuck at interrupt | approval never comes | runs pending past their deadline | timeouts and escalation on interrupts |
| State drift | nodes write conflicting fields | odd values mid-run | typed state; reducers; one owner per field |

---

## Where this fits
- **Place:** L4.5 of [1a-bp.md](../1a-bp.md). The fixed half of agent control flow.
- **Time it deserves:** 20 minutes; §2 and §5.1 first.
- **I should be able to…**
  - Name the five workflow patterns with one example each.
  - Explain checkpoints and why resumed nodes must be idempotent.
  - Draw a graph with a loop inside a node for a business process.
  - Choose between LangGraph, ADK graphs, Step Functions and Temporal.

## References
1. [Anthropic — Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) — the five workflow patterns.
2. [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview) — state, checkpoints, interrupts.
3. [Google ADK — workflow agents](https://google.github.io/adk-docs/agents/workflow-agents/) — sequential, parallel, loop agents.
4. [Choosing an agent framework in late 2026](https://www.developersdigest.tech/blog/choosing-an-agent-framework-late-2026) — framework states, including ADK 2.x graphs.
