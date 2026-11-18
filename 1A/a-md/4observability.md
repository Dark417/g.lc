# 4observability — Tracing, Monitoring And Debugging Agents In The Cloud

> What to record for an agent run, how traces connect across hops, how to debug a bad answer when you can't attach a debugger, and which tools do this.
> Group 4 (quality and safety). Related: [4evals.md](4evals.md), [4access.md](4access.md), [1architecture.md](1architecture.md).
> Concept level, no code (AGENTS.md §8b). Last updated: 2026-11-16.

## Index
- [0. One-minute version](#0-one-minute-version)
- [1. Concept: trace is observability](#1-concept-trace-is-observability)
- [2. What to capture](#2-what-to-capture)
- [3. Connecting the hops](#3-connecting-the-hops)
- [4. Metrics and alerts](#4-metrics-and-alerts)
- [5. Debugging in the cloud](#5-debugging-in-the-cloud)
- [6. Tools at hand](#6-tools-at-hand)
- [7. System design view: choosing and building](#7-system-design-view-choosing-and-building)
- [8. Failure modes](#8-failure-modes)
- [Where this fits](#where-this-fits)
- [References](#references)

---

## 0. One-minute version
- **What:** observability for agents means a trace per run: every model call, tool call, retrieval and sub-agent, with content, tokens, cost and timing.
- **Why:** the same input can take different paths. You can't debug a wrong answer without seeing what the agent saw and did.
- **How:** instrument the harness with OpenTelemetry, carry one trace ID from client to tools, send spans to a backend, and add metrics and quality scores on top.
- **Catch:** traces hold user data. Capture content on purpose, redact it, and control access.
- 🗣 "For an agent, the trace is the stack trace. I can't fix what I can't replay."

---

## 1. Concept: trace is observability
`boundary` ★★★

- **Yes, tracing belongs here.** Observability = traces, metrics and logs. For agents, traces are the main tool.
- **Plain idea:** a trace is the story of one run as a tree of timed steps (spans).
- **Picture it:** "Why did the refund agent say the order wasn't found?"

```
 run r-91 (user u-7, session s-3)              4.8s  $0.031
 ├─ guardrail: input                           0.05s  pass
 ├─ model call 1 (plan)                        1.1s   tokens 4.2k in / 120 out
 ├─ tool: get_order(order_id="42")             0.4s   -> not found      <- first wrong thing
 ├─ model call 2                               1.3s   tokens 4.5k in / 90 out
 └─ guardrail: output                          0.1s   pass
```
- **Reading it:** the model passed "42" where the system uses "ORD-00000042". The fix is in the tool description, not the model.
- **How it works**
  1. The harness opens a span for the run and child spans for each step.
  2. Each span records inputs, outputs, timing, tokens and status.
  3. Spans are exported to a backend that rebuilds the tree.
  4. You search by user, session, run, error or score.
- **How agents differ from normal services**
  - The path isn't fixed, so you need the actual path, not the diagram.
  - Content (prompts, outputs) is needed to understand a failure.
  - "Worked" isn't the same as "correct", so quality scores sit beside latency and errors.
- 🗣 "The trace shows the first wrong step. Everything after it is usually a consequence."

---

## 2. What to capture
`software` ★★★

| Group | Fields | Why |
|---|---|---|
| Identity | trace, run, session, user and tenant IDs | find a run; filter by customer |
| Versions | model, prompt version, tool versions, policy version, harness build | explain behavior changes |
| Model call | model, input and output tokens, cached tokens, latency, stop reason, cost | spot cost and truncation |
| Context | what was in the window (or a pointer), retrieved chunk IDs | "what did it see?" |
| Tool call | name, arguments, result size, latency, error, retry count | wrong tool, bad args, slow tools |
| Control | guardrail verdicts, approvals, permission denials, stop reason | why a run stopped or was blocked |
| Outcome | final answer, state changes, user feedback, eval scores | tie quality to traces |

- **Standard:** OpenTelemetry GenAI semantic conventions define span and attribute names for model and agent calls. Their status was "Development" at last check, so names can still change; pin the version.
- **Content capture is a decision.** Full prompts help debugging and are the most sensitive data you hold. Options: capture everything with redaction and short retention, capture only metadata, or store content by reference in a restricted store.
- **Tag every run with versions.** "Behavior changed on Tuesday" is answerable only if prompt and model versions are on the trace.
- 🗣 "Every span carries who, which versions, what it saw, what it did, and what it cost."

---

## 3. Connecting the hops
`boundary` ★★★

- **Plain idea:** one trace ID must survive every boundary, or the story breaks into pieces.
- **Hops that drop context**

| Hop | How to carry it |
|---|---|
| Client to BFF to harness | W3C trace context header on each call |
| Harness to model gateway to provider | header on the call; gateway logs the same ID |
| Harness to MCP server | header or request metadata; MCP server logs it |
| Harness to remote agent (A2A) | header on the request; agent returns its own span IDs |
| Async jobs (queue, workers) | put the trace context in the message attributes |
| Human approval pause and resume | store the trace ID with the paused run; resume under it |

- **Sub-agents** get child spans under the parent run, so a multi-agent run is one tree.
- **Link, don't nest, across long gaps:** a resume a day later is a new trace linked to the first.
- 🗣 "I trace across queues and approval pauses, because that's where runs break."

---

## 4. Metrics and alerts
`software` ★★

| Metric | What it tells you | Alert when |
|---|---|---|
| Success rate (outcome or feedback) | quality | drops against baseline |
| Steps per run | loops and drift | median or tail rises |
| Stop-reason mix | health of control | more "hit step limit" or "budget" |
| Cost and tokens per task | spend | rises after a change |
| Latency (time to first token, total) | UX | tail latency over target |
| Tool error and retry rate, by tool | broken integrations | spike for one tool |
| Guardrail block rate | safety and false positives | sudden change |
| Provider error and rate-limit rate | upstream health | rises; triggers fallback |

- **Quality signals:** thumbs, edits, escalations, repeat questions, and online judge scores ([4evals.md](4evals.md)).
- **Sampling:** keep every error, low-score and flagged run; keep a few percent of the rest.
- 🗣 "Alert on cost per task and stop reasons, not just errors. Agents fail by drifting."

---

## 5. Debugging in the cloud
`boundary` ★★★

- **Plain idea:** in the cloud you debug from recordings, not by stepping through code. The trace is the recording.
- **The loop**
  1. **Find the run:** from the user report, feedback ID or alert, open the trace by session or run ID.
  2. **Find the first wrong span:** later steps are usually fallout.
  3. **Look at what the model saw** at that step: instructions, retrieved text, tool results, history.
  4. **Classify the cause**

| Symptom in the trace | Likely cause | Where to fix |
|---|---|---|
| Right tool, wrong arguments | tool description or schema unclear | tool definition, add examples |
| Wrong tool chosen | overlapping or vague tools | fewer, clearer tools |
| Relevant fact missing from context | retrieval miss or truncation | retriever, chunking, context trimming |
| Context huge, quality low late in the run | context bloat | trim, summarize, store by pointer |
| Same call repeated | no progress detection | stop rules in the loop |
| Tool returned an error the model ignored | error shape unclear | tool error messages |
| Answer ignores policy | rule only in the prompt | move to hooks and tool checks |
| Slow | long chain or a slow tool | parallelize, cache, smaller model for easy steps |
| Passed locally, fails in prod | different data, permissions or config | compare version stamps and credentials |

  5. **Replay:** rerun with the recorded inputs. Replay tool calls from recordings so side effects don't repeat. Graph frameworks let you load an earlier checkpoint and fork ([1graph.md](1graph.md) §3.1).
  6. **Fix, then add the case** to the eval set so it stays fixed ([4evals.md](4evals.md)).
- **Cloud-specific habits**
  - Put the run ID in every log line, so logs and traces join.
  - Use shadow runs or a canary to test a fix on real traffic without affecting users.
  - Keep a way to reproduce a production config locally: same prompt version, same model, recorded tool outputs.
  - Debug tools behind access control; redact PII; short retention.
  - For a managed runtime (AgentCore, Google's Agent Runtime), turn on its built-in tracing and export to your backend so logs aren't stranded.
- 🗣 "Open the trace, find the first wrong step, read what the model saw, fix the cause, add a test case."

---

## 6. Tools at hand
`software` ★★

| Tool | Type | Strength | Watch out | Choose when |
|---|---|---|---|---|
| OpenTelemetry | standard and SDKs | vendor-neutral spans; GenAI conventions | conventions still evolving | always the instrumentation layer |
| Langfuse | open source (MIT); cloud or self-host | OTel-native, prompts and evals, large community | self-host needs ClickHouse, Redis, object storage | default open-source backend |
| LangSmith | commercial | deep LangChain and LangGraph tracing, evals, deployment; OTel in and out | self-host is enterprise only | LangChain stack |
| Arize Phoenix | source-available | agent-aware traces, trajectory evals; OpenInference conventions | not OSI open source | agent-heavy, easy self-host |
| Braintrust | commercial | eval-first, experiments | not OTel-first | evals drive your workflow |
| Datadog LLM Observability | commercial | agent traces beside APM and infra | per-span billing can grow | you already run Datadog |
| OpenLLMetry, OpenInference | instrumentation libraries | auto-instrument model SDKs | pick one convention | add traces without code changes |
| SigNoz, Grafana, Honeycomb | general observability | one backend for everything | LLM views are thinner | one stack for app and agent |
| AgentCore Observability | managed (AWS) | traces and metrics for agents on AgentCore; OTel export to CloudWatch | AWS only | AWS managed runtime |
| Cloud Trace on Google Cloud | managed | traces for Google's agent platform | Google Cloud only | Google stack |
| OpenAI traces dashboard | built into Agents SDK | zero setup for OpenAI SDK runs | off under zero data retention; data leaves your cloud | quick start with that SDK |

- **The market moves.** Reports in 2026 included Helicone being acquired (Mintlify) and moving to maintenance mode, and a pending Galileo acquisition (Cisco). Prefer OTel-based tools so switching backends is cheap.
- **Pick:** OpenTelemetry instrumentation plus Langfuse by default; LangSmith if you're on LangChain; the cloud provider's tool if you're on a managed runtime; Datadog if the company already standardized on it.

---

## 7. System design view: choosing and building
`boundary` ★★★

| Decision | Options | How to decide |
|---|---|---|
| Instrumentation | vendor SDK vs OpenTelemetry | OpenTelemetry to avoid lock-in |
| Backend | self-host, SaaS, cloud-native | data sensitivity and ops capacity |
| Content capture | full, redacted, metadata only, by reference | by data class and retention rules |
| Sampling | all, tail-based, head-based percent | keep errors and low scores; sample the rest |
| Retention | days, weeks, months | debugging window vs privacy and cost |
| Quality signals | feedback only, judge scores, both | both; sample judge scoring to control cost |
| Access | open to engineers vs role-based | role-based; audit who reads traces |

- **Default:** OpenTelemetry in the harness and gateway, one trace ID end to end, full capture with PII redaction and 30-day retention in a role-restricted backend, 100% of errors and flagged runs kept, metrics for cost, steps and stop reasons, and online judge scores on a sample.

---

## 8. Failure modes
`boundary`

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Broken trace at async hop | trace context not in message attributes | orphan spans | propagate through queues and pauses |
| PII in traces | raw prompts stored widely | scanner on the trace store | redact at capture; restrict access |
| Cost blind spot | tokens not recorded per span | spend can't be attributed | token and cost attributes on every model span |
| Missing versions | prompts change without stamps | "it changed" with no cause | stamp versions on the trace |
| Trace volume explosion | capture everything forever | bill and query speed | tail sampling; retention |
| Sampled out the failure | head sampling drops rare errors | can't find the run | always keep errors and low scores |
| Backend lock-in | vendor SDK everywhere | migration cost | OpenTelemetry layer |

---

## Where this fits
- **Place:** L7 of [1a-bp.md](../1a-bp.md). The source of data for evals and debugging.
- **Time it deserves:** 25 minutes; §2, §3 and §5.
- **I should be able to…**
  - Say what a span for a model call and a tool call must carry.
  - Explain how one trace ID survives a queue and an approval pause.
  - Walk the debug loop on a wrong answer and name five common causes.
  - Pick a tool and say the deciding variable.

## References
1. [OpenTelemetry GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/) — span and attribute names (status: development).
2. [W3C Trace Context](https://www.w3.org/TR/trace-context/) — `traceparent`.
3. [Langfuse docs](https://langfuse.com/docs) — open-source tracing and evals.
4. [Arize Phoenix and OpenInference](https://arize.com/docs/phoenix) — agent tracing conventions.
5. [AI agent observability tools compared (2026)](https://www.morphllm.com/ai-agent-observability-tools) — licenses, OTel support, acquisitions.
