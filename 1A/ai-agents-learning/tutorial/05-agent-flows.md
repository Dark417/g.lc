# 05 — Classical Agent Flows

A *flow* is the **control structure inside one agent run**: how the loop
iterates, when it stops, who chooses the next step. Levels in `04` told
you which components exist; flows tell you *how the controller drives
them*.

There are roughly **eight classical flows**. Most production agents are
one of these or a small hybrid.

---

## Flow 1 — Single-shot
```
input → LLM → output
```
No loop. One call. Used for: classification, extraction, summarization,
single-turn answers. Cheap, deterministic-ish, easy to eval.

## Flow 2 — Sequential chain (pipeline)
```
input → LLM₁ → LLM₂ → LLM₃ → output
```
Hand-coded steps. Each step does one thing well (outline → draft → edit;
translate → summarize → tag). Branch with `if/else` between steps.

## Flow 3 — Router / dispatcher
```
input → classifier → ┬→ specialist A
                     ├→ specialist B
                     └→ specialist C → output
```
Cheap model picks the lane, expensive model serves it. Common in support
bots, IDE assistants, code-review tools.

## Flow 4 — ReAct loop (Reason–Act–Observe)
```
loop:
  Thought → Action(tool) → Observation
  if done: emit Final Answer
```
The canonical tool-using agent. Model emits a tool call, you execute it,
feed the result back as an "observation," repeat until the model emits a
final answer (or you cap iterations).
- **Stop conditions**: model says done, max iterations, max wall-clock,
  tool-call budget exceeded.

## Flow 5 — Plan-and-Execute
```
input → Planner → [step₁, step₂, …, stepN]
                    ↓ executor runs steps (possibly in parallel)
                    ↓ optionally replans on failure
                  output
```
Plan once, execute many. Cheaper than ReAct because you don't pay for
re-reasoning every turn. Works when the task decomposes cleanly.

## Flow 6 — Reflection / Self-refine
```
draft → critique → revise → critique → revise → …
                        (until pass or budget exhausted)
```
The agent (or a sibling agent) reviews its own output and iterates.
Cheap quality lift on writing, code, math. Pairs with an oracle (tests
pass? schema valid? eval score ≥ X?).

## Flow 7 — Orchestrator–Worker (delegation tree)
```
Orchestrator
  ├── Worker A (sub-task)
  ├── Worker B (sub-task)      ← may run in parallel
  └── Worker C (sub-task)
Orchestrator → synthesizes → output
```
The orchestrator decomposes a task at runtime (unlike Plan-and-Execute's
single up-front plan), dispatches to workers, and merges results. Used
in research agents, multi-file code agents. Workers can spawn workers
(recursive).

## Flow 8 — Multi-agent collaboration
Several agents with **distinct roles** talk in a structured protocol:
- **Round-robin / turn-taking** (AutoGen GroupChat).
- **Handoff** (Swarm / Agents SDK): agent A says "next is agent B."
- **Debate**: two agents argue, a judge picks (high quality, high cost).
- **Hierarchical**: manager assigns, workers report up.

Distinct from Flow 7 because each agent has its own *persona, prompt,
and toolset*, not just a sub-task.

---

## Two flows worth naming separately

### Flow 4b — Computer-use loop
ReAct but the action space is `click(x,y)`, `type(text)`, `key(...)` and
the observation is a screenshot or DOM snapshot. Same shape, different
risk profile. Always sandbox, always log.

### Flow 5b — Deep Research (long-horizon plan-execute-replan)
Plan-and-Execute with periodic replanning, durable checkpoints, and a
"notes" scratchpad that grows over time. Runs for minutes-to-hours.
Needs queue/async infra (Level 9).

---

## Choosing a flow

| If your task… | Use |
|---|---|
| Always has the same shape | Flow 2 (chain) |
| Has a few input variants | Flow 3 (router) |
| Needs to use tools opportunistically | Flow 4 (ReAct) |
| Has 3–10 steps you can list in advance | Flow 5 (plan-execute) |
| Has a measurable quality bar | Flow 6 (reflection) |
| Naturally splits into parallel sub-tasks | Flow 7 (orchestrator-worker) |
| Has clear role specialization | Flow 8 (multi-agent) |
| Drives a GUI / OS | Flow 4b (computer-use) |
| Runs for hours | Flow 5b (deep research) |

## Stop conditions — the part everyone forgets

Every flow with a loop **must** have at least three terminators:
1. **Logical**: model emits `done` / final answer.
2. **Budget**: max iterations, max tool calls, max tokens, max wall-clock.
3. **Safety**: forbidden tool sequence, repeated identical tool calls,
   tool errors over threshold.

Without these, agents loop forever or burn money in flop-houses of
their own reasoning.

## Anatomy of one ReAct iteration (reference)

```
1. assemble prompt:
     system + tools-schema + history + (RAG context) + user
2. model() → response
3. if response has tool_calls:
       for each tool_call:
           validate args against schema
           run tool (with timeout, with auth)
           append tool_result to history
       loop
   else:
       return response.text
4. check budgets; if exceeded → return partial + warning
```

Almost every framework (LangGraph, AutoGen, Anthropic SDK agents) is a
variation on this. Knowing the shape lets you read any of them.

Next: matching flows + architectures to **real product use cases**. →
`06-use-case-recommendations.md`
