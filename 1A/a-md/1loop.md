# 1loop — The Agent Loop And Loop Types

> How the agent loop works, the kinds of loops stacked on top of it, and how to bound and choose them.
> Group 1 (agent core). Container: [1harness.md](1harness.md). Fixed-step sibling: [1graph.md](1graph.md).
> Concept level, no code (AGENTS.md §8b). Last updated: 2026-11-16.

## Index
- [0. One-minute version](#0-one-minute-version)
- [1. Concept](#1-concept)
- [2. Anatomy of one turn](#2-anatomy-of-one-turn)
- [3. Stopping the loop](#3-stopping-the-loop)
- [4. Loop patterns inside one agent](#4-loop-patterns-inside-one-agent)
- [5. Loops around the agent](#5-loops-around-the-agent)
- [6. System design view: when and how to loop](#6-system-design-view-when-and-how-to-loop)
- [7. Failure modes](#7-failure-modes)
- [Where this fits](#where-this-fits)
- [References](#references)

---

## 0. One-minute version
- **What:** the model calls a tool, reads the result, and decides again, until the task is done.
- **Why:** some tasks can't be planned in advance; the next step depends on what the last step found.
- **How:** think, act, observe, repeat, inside step, token and time limits.
- **Catch:** the same task can take 3 steps or 14. Cost, latency and behavior vary run to run.
- 🗣 "An agent is a model in a loop with tools. My job is making that loop bounded, observable and safe."

---

## 1. Concept
`AI`

- **Plain idea:** like a detective. Look at the evidence, decide what to check next, check it, update, repeat until the case is solved.
- **Picture it:** "Why did yesterday's batch job fail?"
  1. Read the job status: failed at step 3.
  2. Read the step-3 logs: timeout calling the vendor API.
  3. Check the vendor's status page: outage 2–4am.
  4. Answer: vendor outage; rerun after recovery.
  - Nobody could have written those four steps in advance. Each depended on the last result.
- **How it works**
  1. **Think:** the model sees the task, history and tool results, then picks an action.
  2. **Act:** the harness runs the chosen tool (after checks).
  3. **Observe:** the result is added to the context.
  4. **Repeat or stop:** the model either acts again or returns a final answer; the harness enforces limits.
- **The catch**
  - The context window is the loop's only memory. Whatever isn't in it is forgotten.
  - Each turn adds latency and tokens; long loops get slow and expensive.
  - Errors compound: a bad tool result at step 2 can steer every later step.
- 🗣 "The loop's memory is the context window. If it's not in context, the agent doesn't know it."

---

## 2. Anatomy of one turn
`boundary` ★★★

```
  state ──> build context ──> model ──> reply
              ^                          ├─ final answer ──> validate ──> return
              |                          └─ tool call ──> policy check ──> run tool ──> result
              └──────────── append result, update state, check budgets <─────────┘
```

- **State per turn:** messages so far, tool results, task status, counters (steps, tokens, spend).
- **Build context:** the harness picks what goes in. Old turns get trimmed or summarized.
- **Policy check:** is this tool allowed, for this user, with these arguments? Does it need approval?
- **Tool result shaping:** keep results small and structured; long outputs are cut or stored with a pointer.
- **Errors are results too:** a failed tool call goes back to the model as a clear error, so it can try another way.
- 🗣 "A tool error isn't a crash. It's an observation the model can act on."

---

## 3. Stopping the loop
`boundary` ★★★

- **Plain idea:** a loop without a reliable stop is a bill without a limit.

| Stop condition | Meaning | Returns |
|---|---|---|
| Done signal | the model gives a final answer, or calls a `finish` tool | the result |
| Step limit | e.g. 25 turns | partial result + "hit step limit" |
| Budget limit | tokens or money per run | partial result + reason |
| Time limit | wall-clock deadline | partial result + reason |
| Repeated failure | same error N times, or no progress | escalate to a human |
| Human stop | user cancels, or an approval is denied | current state, saved |

- **Always log the stop reason.** It's the first thing to check when a run looks wrong.
- **"No progress" is the hard one:** the agent loops on the same tool with similar arguments. Detect repeats and stop.
- 🗣 "Every loop needs a done signal and a ceiling, and I log which one fired."

---

## 4. Loop patterns inside one agent
`AI` ★★★

| Pattern | How it works | Good at | Cost |
|---|---|---|---|
| ReAct ★★★ | reason, act, observe, step by step | the default for tool use | many small turns |
| Plan, then execute ★★ | make a plan first, then run the steps; re-plan on surprises | long tasks; plan is visible and checkable | plan can go stale |
| Reflection ★★ | after a draft, the model critiques and revises its own work | quality on writing and reasoning | extra calls; can over-edit |
| Evaluator–optimizer ★★★ | one model generates, another judges, repeat until it passes | clear criteria to check against | bounded loop; cheapest agentic pattern |
| Code-as-action ★ | the model writes code to call tools, run in a sandbox | many tool calls per turn, data work | needs a sandbox |

- **Plan-then-execute vs ReAct:** a plan helps on long tasks and for showing users what will happen; ReAct adapts better when each step reveals new facts. Many agents do both: a short plan, then ReAct steps.
- **Evaluator–optimizer is a loop with a fixed exit:** it stops when the grader passes or a cap is hit. Reach for it before an open-ended loop.

---

## 5. Loops around the agent
`boundary` ★★

- **Plain idea:** the agent loop is the inner loop. Production systems add loops around it.

| Loop | Trigger | What it automates |
|---|---|---|
| Agent loop | a task | doing the work |
| Verification loop | each output | correctness: a grader checks the result and sends failures back |
| Event-driven loop | webhook, schedule, queue message, chat message | running at scale without a person starting each run |
| Improvement loop | production traces | getting better: failures become eval cases; prompts and tools get fixed |

- **The improvement loop is the one that compounds:**
  1. Collect traces of failed or overridden runs.
  2. Label why they failed.
  3. Add them to the eval set.
  4. Fix the prompt, tool or flow; re-run evals; ship.
- Some teams let an analysis agent propose these fixes. A human should still approve harness changes.
- 🗣 "The inner loop does the task; the outer loop turns its failures into tests."

---

## 6. System design view: when and how to loop
`boundary` ★★★

### 6.1 Use a loop when
- Steps can't be listed ahead of time; they depend on what's found.
- The branching is too large to hard-code.
- You can tolerate variable cost and latency.
- You already have tracing and evals to catch regressions.

### 6.2 Don't use a loop when
- The steps are known: write a workflow (see [1graph.md](1graph.md)).
- It's high-volume, simple and latency-sensitive: classification, extraction.
- A wrong action can't be undone and there's no human checkpoint.

### 6.3 Decisions inside a loop

| Decision | Options | How to decide |
|---|---|---|
| How many tools | few focused tools vs many | fewer tools, clearer choices; split into sub-agents if it grows |
| Step budget | low (5–10) vs high (25–50+) | match task length; set from eval runs, not a guess |
| Model per step | one model vs routed | cheap model for simple steps if evals hold |
| Where state lives | in memory vs external store | external if runs are long, pausable or must survive a crash |
| Human approval | none, on writes, on everything | by blast radius: approve anything irreversible |
| Parallel tool calls | off vs on | on for independent reads; off for dependent writes |

### 6.4 Owning the loop
- **Own your control flow:** you should be able to read, pause, branch and resume the loop.
- **State as a reducer:** each turn is `new state = f(old state, event)`. That makes runs replayable and resumable.
- **Human as a tool:** "ask a human" can be a tool, with the same pause and resume as any long call.
- Framework or plain code? A plain loop is enough to start. Adopt a framework for checkpoints, streaming and tracing, but make sure you could rewrite its loop yourself.
- Default: ReAct with a small toolset, a step and budget ceiling, approval on writes, and a verifier loop on outputs that matter.

---

## 7. Failure modes
`boundary`

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Infinite loop | no done signal; repeated tool calls | steps per run hit the ceiling | finish tool; repeat detection; budgets |
| Context bloat | every tool result kept in full | tokens per turn grow; quality drops late in runs | trim, summarize, store big results by pointer |
| Error cascade | bad result early, trusted later | wrong answers with plausible traces | validate tool results; verifier loop |
| Wrong tool | vague names or overlapping tools | tool-choice errors in evals | clearer descriptions; fewer tools |
| Silent cost growth | longer runs after a prompt change | cost per task trend | budgets per run; eval gate tracks cost |

---

## Where this fits
- **Place:** L4.4 of [1a-bp.md](../1a-bp.md). The engine inside the harness.
- **Time it deserves:** 20 minutes; §1, §3 and §6 first.
- **I should be able to…**
  - Walk one turn: context, model, check, tool, observe.
  - List six stop conditions and say which one I log.
  - Name the loop types and pick one for a given task.
  - Explain when a loop is the wrong tool.

## References
1. [Anthropic — Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) — augmented LLM, evaluator–optimizer, agents.
2. [ReAct paper (Yao et al., 2022)](https://arxiv.org/abs/2210.03629) — reasoning plus acting.
3. [HumanLayer — 12-factor agents](https://github.com/humanlayer/12-factor-agents) — own your control flow, state as reducer.
4. [Harness engineering vs loop engineering](https://danicasimic.substack.com/p/harness-engineering-vs-loop-engineering) — agent, verification, event-driven and improvement loops.
