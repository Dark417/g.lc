# 6durable — Durable, Long-Running And Background Agents

> How agent runs survive crashes, wait hours for people or events, run on schedules, and report results later.
> Group 6 (production). Related: [1graph.md](1graph.md) §3, [1architecture.md](1architecture.md) §5–6, [0edge-com.md](0edge-com.md) §4.
> Concept level, no code (AGENTS.md §8b). Last updated: 2026-11-16.

## Index
- [0. One-minute version](#0-one-minute-version)
- [1. Concept](#1-concept)
- [2. Three levels of durability](#2-three-levels-of-durability)
- [3. How durable execution works](#3-how-durable-execution-works)
- [4. Background and scheduled agents](#4-background-and-scheduled-agents)
- [5. Waiting: people, events, timers](#5-waiting-people-events-timers)
- [6. System design view: choosing](#6-system-design-view-choosing)
- [7. Failure modes](#7-failure-modes)
- [Where this fits](#where-this-fits)
- [References](#references)

---

## 0. One-minute version
- **What:** a durable run keeps its progress outside the process, so it can pause, crash and resume without losing or repeating work.
- **Why:** real agent tasks take minutes to days: approvals, waiting for a vendor, research jobs, nightly batches.
- **How:** save state at step boundaries (checkpoints or an event history), make side effects idempotent, run on workers from a queue, notify the client when done.
- **Catch:** resuming means some step may run twice. Durability without idempotency doubles payments.
- 🗣 "Long-running work is a job, not a request: queued, checkpointed, resumable, and idempotent."

---

## 1. Concept
`boundary` ★★★

- **Plain idea:** like a saved game. If the power cuts, you reload from the last save, not from the start.
- **Picture it:** a contract-review agent.
  1. A user uploads 40 contracts; the API returns a job ID at once.
  2. Workers review contracts in parallel; each finished contract is saved.
  3. One worker crashes at contract 23; another picks it up from the saved list.
  4. Three contracts need a lawyer's approval; the job waits two days.
  5. The lawyer approves; the job finishes and emails a report.
- **How it works**
  1. Turn the request into a job record with an ID.
  2. Workers take steps from a queue and save results after each.
  3. Waits (approval, timers, events) are stored states, not sleeping threads.
  4. On crash, a new worker resumes from the last saved step.
  5. The client follows progress by stream, polling or notification.
- **The catch:** you must design what "a step" is, and make each one safe to repeat.

---

## 2. Three levels of durability
`software` ★★★

| Level | How | Survives | Good at | Choose when |
|---|---|---|---|---|
| Session state only | history in a store; a run lives in one process | restarts between runs | chat | runs under ~30 seconds |
| Checkpointed graph | state saved after each node (LangGraph, ADK sessions, Strands session managers) | crashes mid-run; pauses for people | agent flows with approvals | runs of minutes to days with a few waits |
| Durable workflow engine | an engine records each step's result and replays (Temporal, Step Functions, others) | anything: crashes, deploys, long timers | long, retry-heavy, multi-service processes | hours or days, many external calls |

- **Rule of thumb:** move down a level only when the run length or retry needs force it.
- 🗣 "Session store for chat, checkpoints for pauses, a workflow engine when it must survive anything for days."

---

## 3. How durable execution works
`software` ★★★

- **Plain idea:** record the result of every step that touches the outside world. On restart, replay the record instead of redoing the work.
- **Mechanism (workflow-engine style)**
  1. The workflow code is deterministic: the same inputs produce the same decisions.
  2. Calls with side effects (model calls, tools, APIs) run as separate activities.
  3. The engine stores each activity's result in an event history.
  4. After a crash, the engine re-runs the workflow code, feeding stored results instead of calling again.
  5. Only the unfinished step actually executes.
- **What this means for agents**
  - A model call is non-deterministic, so it must be an activity; its output is recorded once and reused on replay.
  - Retries and timeouts are configured per activity.
  - Waiting a week is a stored timer, not a sleeping process.
- **Checkpointed graphs are lighter:** they save state after each node; a resumed node restarts from its beginning, so idempotency matters even more there ([1graph.md](1graph.md)).
- **Options:** Temporal, AWS Step Functions (which added native AgentCore Harness integration in 2026), and libraries such as Restate, Inngest and DBOS that add durable steps to normal code.
- 🗣 "Model calls are activities: run once, recorded, replayed. That's how a crash doesn't re-bill or re-act."

---

## 4. Background and scheduled agents
`boundary` ★★

| Trigger | Example | Delivery of results |
|---|---|---|
| Schedule | nightly report, weekly cleanup | email, dashboard, chat message |
| Event | new ticket, webhook, file uploaded | write back to the system, notify |
| Queue message | batch of documents | job status, results store |
| User request, long | research report, code change | run ID, progress stream, notification |

- **Same harness, different trigger:** the agent code doesn't care who started it ([1architecture.md](1architecture.md) §2).
- **Identity for unattended runs:** a scheduled run acts as a service identity or a stored delegation, with narrower rights than an interactive user ([4access.md](4access.md)).
- **Concurrency control:** cap concurrent jobs per tenant; one active run per resource when they'd conflict.
- **Results:** store them durably; notify; never rely on the client being connected.
- **Cost:** batch model APIs fit non-urgent background work ([2models.md](2models.md) §5).

---

## 5. Waiting: people, events, timers
`boundary` ★★

- **Human approval:** pause with a stored request, an expiry and an escalation path ([0edge-com.md](0edge-com.md) §6).
- **External events:** wait for a webhook (payment settled, vendor replied); correlate it to the run by an ID.
- **Timers:** "retry tomorrow", "remind in 3 days" are stored timers.
- **Timeouts on every wait:** what happens if no one answers? Escalate, cancel, or take a safe default.
- **State drift while waiting:** re-check facts on resume; an approval for a $200 refund doesn't cover a $900 one.

---

## 6. System design view: choosing
`boundary` ★★★

| Decision | Options | How to decide |
|---|---|---|
| Sync vs job | stream in request vs job ID | job beyond ~30 seconds or with waits |
| Durability level | session, checkpoints, workflow engine | run length, retries, number of external calls |
| Step size | fine vs coarse | small enough to retry cheaply; big enough to limit overhead |
| Side effects | in-line vs separate idempotent step | separate, keyed |
| Waits | in-process sleep vs stored wait | stored, always |
| Notification | stream, poll, push, email | stream while open; push or email after |

| Tool | Type | Choose when |
|---|---|---|
| LangGraph checkpoints, ADK sessions | framework state | agent flows with pauses |
| Temporal | durable workflow engine | long, retry-heavy runs; code-first teams |
| Step Functions | managed AWS workflow | AWS shops; steps mostly AWS service calls |
| SQS or Pub/Sub plus workers | queue | simple jobs with your own state table |
| Managed runtimes (AgentCore, Agent Runtime) | hosted sessions with long runs | want less to operate |

- **Default:** a job table plus queue plus workers for anything over ~30 seconds, framework checkpoints for approvals, a workflow engine only when runs last hours with many external calls, idempotency keys on every write.

---

## 7. Failure modes
`boundary`

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Double side effect on resume | step re-runs | duplicate actions | idempotency keys; separate side-effect steps |
| Lost job | worker died, no lease timeout | job stuck in "running" | leases with timeouts; reaper |
| Stuck wait | approval or event never arrives | jobs pending past deadline | timeouts and escalation |
| Replay breaks | non-deterministic code in workflow logic | replay errors | model calls as activities |
| Stale approval | state changed during wait | audit mismatch | re-validate on resume |
| Orphan results | client gone | results never seen | durable storage plus notification |

---

## Where this fits
- **Place:** L8 of [1a-bp.md](../1a-bp.md); extends [1graph.md](1graph.md) and [1architecture.md](1architecture.md).
- **Time it deserves:** 15 minutes; §2 and §3.
- **I should be able to…**
  - Name the three durability levels and when to use each.
  - Explain replay and why model calls must be recorded activities.
  - Design a background job with waits, timeouts and notification.

## References
1. [Temporal — workflows and activities](https://docs.temporal.io/workflows) — deterministic replay.
2. [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence) — checkpoints and resume.
3. [AWS Step Functions](https://docs.aws.amazon.com/step-functions/) — managed workflows.
4. [AgentCore release notes](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/release-notes.md) — Step Functions and Harness integration.
