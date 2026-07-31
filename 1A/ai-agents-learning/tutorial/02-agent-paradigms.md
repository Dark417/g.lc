# 02 — Agent Paradigms & Workflow Patterns

A *paradigm* is the **shape of the loop**: who decides, who calls tools,
how many models are involved, and how control flows. Picking one is the
single biggest architecture decision you make.

Anthropic's "Building Effective Agents" essay (2024) made a useful split:

- **Workflows**: LLMs are *steps* in a predefined pipeline. You, the
  engineer, write the control flow.
- **Agents**: the LLM *is* the control flow. It chooses what to do next.

Most production systems are workflows with one or two agent steps inside.
Pure agent loops are powerful but expensive, slow, and harder to debug.

---

## A. Workflow patterns (you write the graph)

### 1. Prompt chaining (sequential)
Output of step 1 → input of step 2 → step 3. Optional gate checks between
steps. Use when: the task decomposes into a fixed sequence (e.g.
*outline → draft → edit*).

### 2. Routing / Classifier-first
A small model classifies the input, then dispatches to a specialist
prompt or model. Use when: inputs are heterogeneous (support: billing vs
technical vs returns).

### 3. Parallelization
- **Sectioning**: split a task into independent subtasks, run in parallel,
  merge. (Summarize 50 docs in parallel.)
- **Voting**: run the same prompt N times, majority-vote / pick best.
  Self-consistency. Good for high-stakes single answers.

### 4. Orchestrator–worker
A "lead" LLM breaks a task into subtasks and dispatches each to a
"worker" LLM, then synthesizes. Useful when subtasks aren't known in
advance (research agents, multi-file refactors).

### 5. Evaluator–optimizer (critic loop)
LLM generates → LLM critiques → LLM revises → repeat until pass. Like
test-driven generation. Good when you have a clear quality bar that's
easier to *check* than to *produce*.

---

## B. Agent patterns (the LLM drives)

### 6. ReAct (Reason + Act)
The classic loop: model emits *Thought → Action → Observation* until it
decides to answer. Almost every "tool-using agent" descends from this.

### 7. Plan-and-Execute
Plan once up front (cheap-model planner), then execute steps (possibly
in parallel) without re-planning each turn. Cheaper than ReAct, less
adaptive.

### 8. Tree of Thoughts / Graph of Thoughts
Model explores multiple branches of reasoning, scores them, prunes. Used
for puzzles, math, search problems. Rarely needed in product code.

### 9. Reflection / Self-refine
Agent reviews its own work after a draft and revises. A built-in critic
step. Cheap quality boost.

### 10. Multi-agent collaboration
Several role-playing agents (researcher, coder, reviewer) take turns or
debate. AutoGen, CrewAI, MetaGPT, Anthropic's Claude swarms.
- **Hierarchical**: manager + workers (orchestrator-worker on steroids).
- **Debate / consensus**: agents argue, a judge picks.
- **Swarm / handoff**: agents pass control by naming the next agent
  (OpenAI Swarm, Agents SDK).

### 11. Computer-use / Embodied agent
Agent perceives a screenshot or DOM and emits clicks/keystrokes. The
"action space" is huge; needs strong guardrails.

### 12. Deep Research / Long-horizon
Plan → search → read → take notes → plan again → … over minutes or
hours. Requires durable state, checkpointing, and a UI that tolerates
latency. (OpenAI Deep Research, Perplexity, Anthropic Research.)

---

## C. RAG paradigms (often combined with the above)

- **Naive RAG**: embed query → top-k → stuff into context. Fine for FAQs.
- **Hybrid RAG**: BM25 + vector, score-fused. Big quality win, low cost.
- **Reranked RAG**: retrieve 50, rerank to top 5 with a cross-encoder.
- **HyDE**: generate a hypothetical answer, embed *that*, then retrieve.
- **GraphRAG**: build a knowledge graph from the corpus, traverse it.
- **Agentic RAG**: retrieval is a *tool* the agent calls — possibly
  multiple times, refining queries.

---

## D. Memory paradigms

- **Stateless**: every request starts fresh. Default.
- **Buffer**: keep the last N turns verbatim.
- **Summary**: summarize older turns into a running summary.
- **Episodic + semantic**: store events as records, embed them, retrieve
  by similarity to current query (Mem0, Letta).
- **Hierarchical (MemGPT-style)**: tiered memory — context window,
  recall, archival — with the agent paging between them.

---

## How to pick (cheat sheet)

| Symptom | Try |
|---|---|
| Task is the same every time | Workflow (chain) |
| Inputs vary, outputs are structured | Routing |
| Slow because of N similar calls | Parallelization |
| Quality plateaus on one prompt | Evaluator–optimizer |
| You can't enumerate subtasks ahead of time | Orchestrator–worker or ReAct |
| Needs to use 3+ tools mid-conversation | ReAct / agent loop |
| Multi-hour research task | Plan-and-Execute + checkpointing |
| Open-ended with clear sub-roles | Multi-agent |
| Search over your docs | Hybrid RAG (start here) |

Next: the **frameworks** that implement these. → `03-frameworks.md`
