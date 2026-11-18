# 1orchestration — Agent Orchestration (Multi-Agent)

> When to use more than one agent, the patterns for wiring them, how they share information, and how to keep their work consistent.
> Group 1 (agent core). Wire-level detail: [1aa-msg.md](1aa-msg.md). Single-agent shapes: [1harness.md](1harness.md).
> Concept level, no code (AGENTS.md §8b). Last updated: 2026-11-16.

## Index
- [0. One-minute version](#0-one-minute-version)
- [1. Concept](#1-concept)
- [2. Why split, and why not](#2-why-split-and-why-not)
- [3. Orchestration patterns](#3-orchestration-patterns)
- [4. How agents share information](#4-how-agents-share-information)
- [5. Consistency: distributed systems first](#5-consistency-distributed-systems-first)
- [6. System design view: choosing a pattern](#6-system-design-view-choosing-a-pattern)
- [7. Failure modes](#7-failure-modes)
- [Where this fits](#where-this-fits)
- [References](#references)

---

## 0. One-minute version
- **What:** several agents, each with its own context and tools, coordinated to finish one task.
- **Why:** to isolate context, run work in parallel, or give parts different tools and permissions.
- **How:** a lead agent delegates (supervisor), agents pass control (handoff), or agents are called like tools.
- **Catch:** more tokens, more latency, and errors that compound across agents. Anthropic reports multi-agent runs using about 15× the tokens of a chat.
- 🗣 "I go multi-agent only when one agent's context or toolset can't hold the job, and the task is worth the extra tokens."

---

## 1. Concept
`AI`

- **Plain idea:** a team instead of one generalist. A lead hands pieces to specialists and combines their work.
- **Picture it:** a research question, "compare three vendors' security posture".
  - The lead plans: one sub-agent per vendor.
  - Three sub-agents search in parallel, each with a clean context.
  - Each returns a short summary, not its whole search history.
  - The lead compares and writes the answer.
- **How it works**
  1. A lead (or a router) decides how to split the task.
  2. Each sub-agent gets a focused task, its own context and its own tools.
  3. Sub-agents work, sometimes in parallel.
  4. Results come back compressed: summaries or structured records.
  5. The lead combines them, checks them, and may send more work.
- **The catch**
  - Each agent sees only part of the picture. Decisions made in one context can conflict with another.
  - Debugging means following several traces.
  - Cost rises fast. Multi-agent pays off only on high-value tasks.
- 🗣 "Sub-agents are mostly about context: each gets a clean window, and only the summary comes back."

---

## 2. Why split, and why not
`boundary` ★★★

| Reason to split | Example | What it buys |
|---|---|---|
| Context isolation | each source searched by its own agent | smaller, cleaner windows; less context rot |
| Parallel work | many independent subtasks | lower wall-clock time |
| Different tools or permissions | read-only researcher vs write-capable executor | least privilege per agent |
| Different models | cheap model for triage, strong one for decisions | lower cost per task |
| Team ownership | another team's agent behind an API | independent deploys |

| Reason not to split | Why |
|---|---|
| Tasks are tightly coupled | agents make conflicting choices without shared context (Cognition's "Don't build multi-agents" argument) |
| One agent passes the evals | extra agents add cost and failure points for nothing |
| Low-value, high-volume tasks | about 15× chat tokens doesn't pay off (Anthropic, Jun 2025) |
| Strict latency targets | handoffs and extra calls add seconds |

- **Evidence both ways:** Anthropic reports its multi-agent research setup beat a single agent by 90.2% on an internal research eval, for parallel, breadth-first research. Coding and other tightly coupled tasks often go the other way.
- 🗣 "Parallel and separable: consider multi-agent. Coupled and sequential: keep one agent."

---

## 3. Orchestration patterns
`AI` ★★★

```
  Supervisor            Handoff                 Agents as tools          Hierarchy
     [lead]          [A] -> [B] -> [C]        [agent] --calls--> [sub]   [lead]
    /  |   \         (control moves)          (control returns)          /    \
  [a] [b]  [c]                                                       [lead2]  [lead3]
```

| Pattern | How control moves | Good at | Weak at | Seen in |
|---|---|---|---|---|
| Supervisor / orchestrator–workers ★★★ | lead delegates, gets results back, decides next | dynamic splitting, research | lead is a bottleneck and single point of failure | Anthropic research system, LangGraph supervisor |
| Handoff / router ★★★ | an agent passes the conversation to a specialist and steps out | customer service triage | context lost or bloated at the handoff | OpenAI Agents SDK handoffs, ADK agent transfer |
| Agents as tools ★★ | a sub-agent is called like a function and returns a result | clean interface, lead keeps control | sub-agent can't ask the user anything | ADK `AgentTool`, Claude Agent SDK subagents |
| Hierarchy ★ | supervisors of supervisors | very large tasks | deep chains, slow, hard to debug | large research or ops systems |
| Peer / swarm ★ | agents hand work to each other with no fixed lead | flexible collaboration | hard to bound and test | Strands swarm patterns |
| Debate / voting ★ | several agents answer, then judge or vote | accuracy on hard judgments | multiplies cost | evaluation and review |
| Pipeline ★★ | fixed sequence of agents | known stages | rigid | a graph whose nodes are agents |

- **Two questions decide most designs**
  - Does the specialist take over the conversation (handoff), or answer and return (tool)?
  - Is the split fixed in code (pipeline, graph) or decided by a model (supervisor)?
- 🗣 "Handoff gives away control; agent-as-tool lends it and gets it back."

---

## 4. How agents share information
`boundary` ★★

| Method | How | Good at | Risk |
|---|---|---|---|
| Shared state | all agents read and write one state record or session | simple, everyone sees the same facts | conflicting writes; bloated shared context |
| Message passing | agents send task and result messages | clear boundaries, testable | lost detail at each hop |
| Shared store | results written to files, a DB or an artifact store; agents pass references | big outputs without bloating context | needs naming and cleanup |
| Protocol across systems | A2A between agents on different stacks; MCP for tools | team and vendor independence | network failures, auth, versioning |

- **Compress at the boundary:** sub-agents return summaries or structured records, not raw transcripts.
- **Pass references, not blobs:** large outputs go to storage; the message carries a path or ID.
- **Within one framework,** agents usually share a session or state. **Across teams or vendors,** use A2A (agent to agent) and keep MCP for tools. Wire formats: [1aa-msg.md](1aa-msg.md).
- 🗣 "Inside one runtime, share state. Across teams, use a protocol. Either way, pass summaries and references."

---

## 5. Consistency: distributed systems first
`software` ★★★

- **Plain idea:** a multi-agent system is a distributed system whose workers happen to be LLMs. The old rules still apply.
- **Ground truths**
  - Exactly-once delivery across machines isn't possible. Use at-least-once plus idempotent actions.
  - Atomicity exists only inside one database transaction. Anything across services is a saga with compensations.
  - Keep the coordinator stateless and the state durable, so any coordinator can resume after a crash.
- **The ledger pattern**
  - A job record and one step record per subtask, in a database.
  - Each step has a deterministic ID and a dedup key, so the same work can't be queued twice.
  - Workers lease steps with a timeout; an expired lease means the worker died, and the step is retried.
  - Every external action carries an idempotency key, so retries don't double-charge.
  - Calls to other services go through an outbox, written in the same transaction as the step update.
- **Agent-specific additions**
  - Decompose without overlap: the lead writes each subtask's scope and its exclusions.
  - Validate sub-agent output against a schema before merging.
  - Conflicts between sub-agents go to the lead or a human, never "last write wins".
- 🗣 "The ledger is always right; the world catches up to it. That's true whether workers are services or agents."

---

## 6. System design view: choosing a pattern
`boundary` ★★★

### 6.1 Decision path
1. Can one agent pass the evals? Then stop here.
2. Are the subtasks independent? Supervisor with parallel workers.
3. Is it routing by intent to specialists? Handoff, or a router node in a graph.
4. Does the lead need results back to keep reasoning? Agents as tools.
5. Are the stages fixed? A pipeline or graph of agents ([1graph.md](1graph.md)).
6. Do agents live in different teams or stacks? A2A between them.

### 6.2 Trade-offs to state out loud

| Trade-off | Lean one way | Lean the other |
|---|---|---|
| Single vs multi | one agent: cheaper, coherent | multi: parallel, isolated, pricier |
| Dynamic vs fixed split | supervisor: adapts | pipeline: predictable, auditable |
| Shared state vs messages | shared: simple | messages: clean boundaries |
| Strong lead model vs cheap workers | quality of plan and synthesis | cost per subtask |

### 6.3 Tools at hand

| Need | Options |
|---|---|
| Supervisor and graphs of agents | LangGraph, ADK (sub-agents, workflow agents), Strands graph / swarm |
| Handoffs | OpenAI Agents SDK, ADK agent transfer |
| Sub-agents as tools | Claude Agent SDK subagents, ADK `AgentTool` |
| Cross-team agents | A2A protocol |
| Durable coordination | ledger tables + queue; Temporal or Step Functions |

- **How each framework manages sub-agents:** compared side by side in [5frameworks.md](5frameworks.md) §4.
- **Where sub-agents run:** inside one process (cheapest), as separate services over gRPC when you own both sides, or behind A2A across teams ([1architecture.md](1architecture.md) §6.2).
- Default: one lead agent with sub-agents as tools for parallel reads, writes kept with the lead, a ledger for anything that changes data, and a per-run token budget across all agents.

---

## 7. Failure modes
`boundary`

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Duplicate work | overlapping subtask scopes | same sources fetched twice; cost spikes | explicit scopes and exclusions; dedup keys |
| Conflicting decisions | coupled tasks split across contexts | merged output contradicts itself | keep coupled work in one agent; lead resolves |
| Lost context at handoff | summary drops a key fact | specialist asks again or acts wrongly | structured handoff payload; required fields |
| Token blowup | many agents, long contexts | cost per task far above single-agent baseline | per-run budget; fewer, cheaper workers |
| Stuck job | worker dies mid-step | step lease expired; job not finished | lease timeout and retry; stateless coordinator |
| Double side effect | retried step re-runs an action | duplicate charges or emails | idempotency keys; outbox |

---

## Where this fits
- **Place:** L4.6 of [1a-bp.md](../1a-bp.md). How agents combine, built on the single-agent shapes in [1harness.md](1harness.md).
- **Time it deserves:** 25 minutes; §2, §3 and §5 first.
- **I should be able to…**
  - Give three reasons to split and three not to.
  - Compare supervisor, handoff and agent-as-tool in one sentence each.
  - Explain the ledger pattern and why it makes retries safe.
  - Say when A2A is needed and when shared state is enough.

## References
1. [Anthropic — How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) (via [Simon Willison's notes](https://simonwillison.net/2025/Jun/14/multi-agent-research-system/)) — token costs, 90.2% result.
2. [Cognition — Don't build multi-agents](https://cognition.ai/blog/dont-build-multi-agents) — context sharing argument.
3. [OpenAI Agents SDK — handoffs](https://openai.github.io/openai-agents-python/handoffs/) — handoff vs agents-as-tools.
4. [A2A protocol](https://a2a-protocol.org/) — agent-to-agent across systems.
5. [LangGraph multi-agent](https://docs.langchain.com/oss/python/langgraph/overview) — supervisor and graph patterns.
