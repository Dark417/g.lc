# AI Agent Harness — Priority-Ordered Map, Engineering Playbook, Study Guide

**Ordering rule everywhere:** ranked by *priority for an L4 harness engineer* = (how often it decides system quality) × (how often it's asked). Root first, then descending. Within each section, items are ranked too.

**Legend**
- Significance ★★★★★ 5 = decides whether the system works; ★☆☆☆☆ 1 = vocabulary.
- Study level:
  - **L1 Recognize** — know the name and one sentence.
  - **L2 Explain** — what it is, why it exists.
  - **L3 Mechanism** — explain A→B: how it works step by step and *why that way*.
  - **L4 Trade-offs** — argue the 2–3 decisions, when it fails, what you'd pick and why.
  - **L5 Design + implement** — whiteboard it and have working code you've run.

---

## Part 1 — Dependency tree (everything, rooted)

Read top-down: a child depends on its parent existing. `⇐` = also depends on.

```
AGENT SYSTEM (harness)
│
├── 1. TARGET  — what "done" means                          ★★★★★
│   ├── task definition & scope (input → acceptable output)
│   ├── success metric (task success rate, cost/task, p95 latency)
│   ├── non-goals / blast radius (what it must never do)
│   └── workflow-vs-agent decision  ⇐ task predictability
│
├── 2. LOOP  — the harness core                             ★★★★★  ⇐ 1
│   ├── LLM call = (system, messages, tools) → text | tool_calls
│   ├── state (messages + scratchpad + task status)
│   ├── termination (done-tool, max turns, budget, timeout)
│   ├── error handling & retries
│   ├── planning / re-planning
│   ├── reflection (evaluator–optimizer)
│   └── interrupts → 4. HITL gates
│
├── 3. TOOLS  — how the loop touches the world              ★★★★★  ⇐ 2
│   ├── schema (name, description, JSON args)
│   ├── granularity & selection
│   ├── side effects: read vs write, idempotency
│   ├── result handling (truncate, structure, errors)
│   ├── parallel calls
│   ├── execution sandbox / code exec / browser
│   └── MCP (12) as one transport for tools
│
├── 4. SAFETY & PERMISSIONS  — bounding the loop            ★★★★★  ⇐ 2,3
│   ├── permission model: allowlist per tool / mode / user
│   ├── human-in-the-loop gates (approve before irreversible)
│   ├── prompt injection defense (untrusted tool results)
│   ├── least privilege, sandboxing, network egress
│   ├── data exfiltration & secrets
│   └── input/output guardrails (classifiers, rules)
│
├── 5. CONTEXT  — what the model sees each turn             ★★★★★  ⇐ 2,3
│   ├── context window & token budget
│   ├── system prompt
│   ├── assembly order: system → memory → retrieved → history → tool results
│   ├── compaction / summarization
│   ├── tool-result pruning
│   ├── prompt caching (stable prefix)
│   ├── just-in-time loading, skills / instruction files
│   └── few-shot examples
│
├── 6. EVAL  — proving it works, catching regressions       ★★★★★  ⇐ 1
│   ├── golden task set (from 1.)
│   ├── outcome eval vs trajectory eval
│   ├── failure taxonomy
│   ├── LLM-as-judge (calibrated)
│   ├── CI regression on prompt/tool/model change
│   ├── online eval / feedback sampling
│   └── benchmarks (SWE-bench, τ-bench…)
│
├── 7. OBSERVABILITY & OPS  — running it                    ★★★★☆  ⇐ 2,3
│   ├── tracing: trace/task, span/LLM call, span/tool call
│   ├── token + cost accounting, budgets
│   ├── prompt & tool versioning
│   ├── rate limits, backoff, model fallback
│   ├── latency budget, streaming
│   └── caching (prompt, result)
│
├── 8. RAG  — grounding the model in your data              ★★★★☆  ⇐ 3 (retrieval is a tool), 5
│   ├── ingest → chunk → embed → index
│   ├── query → hybrid search → rerank → inject
│   ├── citations / grounding
│   ├── agentic RAG (iterative retrieval)
│   ├── retrieval eval (recall@k, faithfulness)
│   └── freshness / re-indexing
│
├── 9. STATE & PERSISTENCE  — surviving time and crashes    ★★★☆☆  ⇐ 2
│   ├── checkpoint per turn, resume
│   ├── session vs task identity
│   ├── idempotency keys for write tools
│   ├── async execution, queues
│   └── durable execution engines
│
├── 10. MEMORY  — across sessions                           ★★★☆☆  ⇐ 5, 8, 9
│   ├── in-context (short-term) vs external (long-term)
│   ├── scratchpad / working memory
│   ├── episodic · semantic · procedural
│   ├── write policy (what/when/dedup/consent)
│   └── retrieval into context (⇐ 8)
│
├── 11. ORCHESTRATION  — more than one loop                 ★★★☆☆  ⇐ 2, 9
│   ├── workflow patterns: chain, route, parallelize, orchestrator–workers, evaluator–optimizer
│   ├── subagent (own context, narrow tools, returns summary)
│   ├── handoffs & shared state
│   ├── topologies (hierarchical, pipeline, swarm)
│   └── coordination failure modes
│
├── 12. MCP  — tool interop protocol                        ★★☆☆☆  ⇐ 3
│   ├── server / client / host
│   ├── primitives: tools, resources, prompts
│   ├── transport: stdio, HTTP
│   ├── auth (OAuth), tool poisoning
│   └── vs. plain function calling
│
├── 13. MODEL LAYER EXTRAS                                  ★★☆☆☆  ⇐ 2
│   ├── structured output
│   ├── extended thinking / reasoning
│   ├── model routing (cheap ↔ strong)
│   ├── sampling params
│   ├── multimodal input
│   └── fine-tuning / RL (boundary — not harness work)
│
└── 14. SERVING & PRODUCT                                   ★★☆☆☆  ⇐ 7, 9
    ├── sync stream vs async job UX
    ├── multi-tenancy & isolation
    ├── canary / rollout of prompts & models
    └── cost model per user
```

---

## Part 2 — Components, ranked, with the engineering playbook

Item format: **name** · significance · study level → *Do* (what the engineer builds/decides) · *Ask* (questions to settle) · *Metrics* · *Patterns/principles*.

### 1. TARGET ★★★★★

**1.1 Task definition & scope** · ★★★★★ · L5
- Do: write the one-page: input, acceptable output, examples of good/bad, hard constraints.
- Ask: Is the path predictable (→ workflow) or open-ended (→ agent)? What's the unit of work? Who consumes the output?
- Metrics: task success rate on golden set; % tasks needing human rescue.
- Patterns: start from 20 real examples, not a spec; "thin vertical slice" MVP0.

**1.2 Success metric & budget** · ★★★★★ · L4
- Do: pick one primary (success rate) + two guardrails (cost/task, p95 latency).
- Ask: What's the cost of a wrong action vs. a no-op? What latency does the UX tolerate?
- Metrics: success %, $/task, p50/p95 seconds, turns/task.
- Patterns: set a per-task token budget on day one; it forces every other design.

**1.3 Workflow vs. agent decision** · ★★★★★ · L4
- Do: default to a deterministic pipeline with LLM steps; upgrade to a loop only if branching can't be enumerated.
- Ask: Can I draw the flowchart? If yes → workflow. Does the number of steps depend on intermediate results? → agent.
- Metrics: variance of turns/task (high variance = agent territory).
- Patterns: Anthropic taxonomy (chain → route → parallel → orchestrator → evaluator → agent). Add autonomy last.

**1.4 Non-goals & blast radius** · ★★★★☆ · L3
- Do: enumerate irreversible actions; each gets a gate (§4.2).
- Ask: What can this thing delete, send, pay, or leak?
- Patterns: read-only first; earn write access per tool.

### 2. LOOP ★★★★★

**2.1 Loop skeleton (ReAct)** · ★★★★★ · L5
- Do: `while True: r = llm(ctx, tools); if r.tool_calls: exec, append results; else break; check budgets`.
- Ask: Where does state live between turns? What is appended after a tool call (raw vs. trimmed)?
- Metrics: turns/task, tokens/turn, loop-abort rate.
- Patterns: reason→act→observe; model never executes, harness does; keep the loop dumb and the tools smart.

**2.2 Termination conditions** · ★★★★★ · L5
- Do: explicit `finish(result)` tool + max_turns + token/cost cap + wall-clock timeout + "no progress" detector.
- Ask: What does a partial result look like when a cap trips? Is it surfaced or silently dropped?
- Metrics: % tasks ending by cap vs. by finish; avg turns-to-finish.
- Patterns: every cap emits a structured reason; never rely on the model to stop itself.

**2.3 State (messages + scratchpad + status)** · ★★★★★ · L5
- Do: single state object per task; messages array is append-only; status enum (running/waiting_human/done/failed).
- Ask: What must survive a crash? What is derived vs. source-of-truth?
- Patterns: state as a typed struct, not loose dicts; serializable every turn (→ §9).

**2.4 Error handling & retries** · ★★★★★ · L5
- Do: classify errors: transient API (retry w/ backoff), tool error (return to model as structured error), malformed output (re-prompt once), unrecoverable (fail task with reason).
- Ask: Can this retry cause a duplicate side effect? (→ idempotency §3.3)
- Metrics: retry rate, error-class distribution.
- Patterns: errors are model-readable data; bounded retries; fail loud.

**2.5 Planning / re-planning** · ★★★★☆ · L4
- Do: plan step producing a todo list the model updates; re-plan trigger on N consecutive failures.
- Ask: Is a plan needed, or does it just burn tokens on 3-step tasks?
- Patterns: plan-as-scratchpad file; keep plan in context, prune history.

**2.6 Reflection / evaluator–optimizer** · ★★★☆☆ · L3
- Do: separate critic call with a rubric; cap iterations at 2–3.
- Ask: Is the critic actually better than the generator? If not, it's noise.
- Metrics: quality delta per iteration vs. cost.

**2.7 Interrupts (hook to §4.2)** · ★★★★☆ · L4
- Do: tool call marked `requires_approval` → persist state, set `waiting_human`, resume on decision.
- Patterns: interrupt = checkpoint + status change, not a blocking thread.

### 3. TOOLS ★★★★★

**3.1 Tool schema design** · ★★★★★ · L5
- Do: verb-noun names, description says *when* to use and *when not*; tight JSON schema with enums; examples in description.
- Ask: Could a new engineer pick the right tool from descriptions alone? Then the model can.
- Metrics: wrong-tool rate, invalid-args rate.
- Patterns: descriptions are prompts; fewer, clearer tools; no two tools with overlapping purpose.

**3.2 Result handling** · ★★★★★ · L5
- Do: truncate/paginate large outputs; return structured JSON, not dumps; include an `error` field.
- Ask: What's the max bytes a result may add to context? Where does the rest go (file, pointer)?
- Metrics: avg tokens per tool result; context growth per turn.
- Patterns: return a pointer + summary; let the model fetch more.

**3.3 Side effects, read vs write, idempotency** · ★★★★★ · L4
- Do: tag tools read/write; write tools take an idempotency key; never retry a write blindly.
- Ask: What happens on duplicate call after a timeout?
- Patterns: same as payments/queues: idempotent writes, at-least-once execution.

**3.4 Granularity & selection** · ★★★★☆ · L4
- Do: 5–15 tools per agent; composite tools for common multi-step ops; hide tools by mode.
- Ask: Is the model choosing among 40 tools? Split into subagents or gate by task.
- Metrics: tool-selection accuracy on golden set.

**3.5 Permissions / allowlists (hook to §4.1)** · ★★★★☆ · L4
- Do: tool availability computed per (user, task, mode); enforced in harness, not prompt.

**3.6 Parallel tool calls** · ★★★☆☆ · L3
- Do: execute independent calls concurrently; preserve order in results.
- Ask: Are these calls independent? Any shared mutable state?

**3.7 Code execution sandbox** · ★★★☆☆ · L3
- Do: isolated container/VM, no network by default, time/memory limits, ephemeral FS.
- Patterns: sandbox as a tool; treat generated code as untrusted input.

**3.8 Computer / browser use** · ★☆☆☆☆ · L1

### 4. SAFETY & PERMISSIONS ★★★★★

**4.1 Permission model** · ★★★★★ · L5
- Do: policy layer: `allow(tool, args, principal, mode) → allow | deny | ask`. Default deny for writes.
- Ask: Who is the principal — the user, the agent, or a service account? Whose authority does a call run under?
- Metrics: denied-call rate, ask-rate, false-deny complaints.
- Patterns: least privilege; policy in code, not prompt; modes (read-only / ask-per-write / auto).

**4.2 Human-in-the-loop gates** · ★★★★★ · L5
- Do: irreversible actions → show intent + diff/preview → approve/deny/edit → resume.
- Ask: Which actions are irreversible? What does "preview" mean for each (email body, SQL, diff)?
- Metrics: approval rate, time-to-approve, gated-action error rate.
- Patterns: propose-then-apply; batch approvals; approval fatigue is a real failure mode.

**4.3 Prompt injection** · ★★★★★ · L4
- Do: treat all tool results, docs, web, emails as untrusted; wrap and label; never let untrusted text grant permissions; gate writes triggered right after untrusted reads.
- Ask: Which context slots are trusted vs. untrusted? Can an injected instruction cause a write tool call?
- Metrics: injection test-suite pass rate.
- Patterns: privilege separation; instruction/data separation; the harness, not the model, enforces limits.

**4.4 Sandboxing & egress** · ★★★★☆ · L3
- Do: no ambient credentials; network allowlist; secrets never in context.

**4.5 Data exfiltration** · ★★★☆☆ · L3
- Ask: Can the model put secrets in a URL, tool arg, or output? Scan outbound args.

**4.6 Input/output guardrails** · ★★★☆☆ · L2
- Do: cheap classifier or rules pre/post; block or route to human.

### 5. CONTEXT ★★★★★

**5.1 Context window & token budget** · ★★★★★ · L4
- Do: allocate slots (system 5%, memory 5%, retrieved 20%, history 50%, tool results 20%); enforce.
- Ask: What gets evicted first? Is eviction deterministic?
- Metrics: tokens/turn, % turns near cap, tokens per successful task.
- Patterns: budget per slot; measure before optimizing.

**5.2 Context assembly** · ★★★★★ · L5
- Do: one function `build_context(state) → messages`; stable prefix first (cacheable), volatile last.
- Ask: Is the assembly deterministic and testable in isolation?
- Patterns: assembly is pure; stable → volatile ordering.

**5.3 System prompt** · ★★★★★ · L5
- Do: role, hard rules, tool usage guidance, output format; versioned in repo.
- Ask: Does anything here change per request? Move it out of the prefix.
- Metrics: eval delta per prompt version.

**5.4 Compaction / summarization** · ★★★★☆ · L4
- Do: at ~70% of cap, summarize oldest turns preserving decisions, open todos, file/entity IDs; drop raw tool dumps.
- Ask: What information loss is acceptable? Where is the full transcript kept?
- Metrics: task success before vs. after compaction.
- Patterns: summarize structurally (decisions/open items/artifacts), not prose.

**5.5 Tool-result pruning** · ★★★★☆ · L4
- Do: after N turns, replace old raw results with one-line summaries or pointers.

**5.6 Prompt caching** · ★★★☆☆ · L3
- Do: keep system prompt + tool schemas + static docs byte-identical across calls.
- Metrics: cache hit rate, cost delta.

**5.7 Just-in-time loading / skills** · ★★★☆☆ · L3
- Do: instruction bundles loaded when relevant instead of everything up front.
- Ask: Which instructions are needed for <20% of tasks? Those move to JIT.

**5.8 Context rot / lost-in-the-middle** · ★★☆☆☆ · L2
- Patterns: put critical instructions at start and end; less context often wins.

**5.9 Few-shot examples** · ★★☆☆☆ · L2

### 6. EVAL ★★★★★

**6.1 Golden task set** · ★★★★★ · L5
- Do: 20→200 real tasks with expected outcome + checker (exact, contains, judge); stored in repo.
- Ask: Does the set cover each failure class? Are checkers deterministic where possible?
- Metrics: pass rate, per-category pass rate.
- Patterns: evals are unit tests; grow the set from production failures.

**6.2 Failure taxonomy** · ★★★★★ · L4
- Do: label every failure: wrong tool / bad args / hallucinated result / loop / early stop / injection / context loss.
- Patterns: fix the top bucket, re-run, repeat.

**6.3 CI regression** · ★★★★☆ · L4
- Do: run golden set on every prompt/tool/model change; block merge on drop > threshold.
- Ask: How much nondeterminism? Run N samples, gate on mean.

**6.4 Outcome vs. trajectory eval** · ★★★★☆ · L3
- Do: outcome = final result correct; trajectory = tool sequence sane, no forbidden calls, turns ≤ k.

**6.5 LLM-as-judge** · ★★★☆☆ · L3
- Do: rubric-driven grader; calibrate against 50 human labels; report agreement.
- Ask: Is judge agreement with humans > 80%? If not, don't trust it.

**6.6 Online eval / feedback** · ★★★☆☆ · L2
- Do: sample production traces, thumbs, human review queue; feed back into 6.1.

**6.7 Benchmarks** · ★☆☆☆☆ · L1

### 7. OBSERVABILITY & OPS ★★★★☆

**7.1 Tracing** · ★★★★★ · L5
- Do: trace per task; span per LLM call (prompt, response, tokens, latency) and per tool call (args, result, error); OTel-compatible.
- Ask: Can I replay a failed task from its trace?
- Patterns: trace ID in every log line; store full prompts (redacted).

**7.2 Token & cost accounting** · ★★★★★ · L4
- Do: per-call → per-task → per-user rollups; budget alerts; kill-switch.
- Metrics: $/task, tokens/task, cache hit rate.

**7.3 Prompt & tool versioning** · ★★★★☆ · L3
- Do: prompts in repo, hashed, referenced in traces.

**7.4 Rate limits, backoff, fallback** · ★★★★☆ · L4
- Do: jittered exponential backoff on 429/5xx; queue; secondary model fallback.
- Ask: Does fallback change behavior enough to invalidate evals?

**7.5 Latency & streaming** · ★★★☆☆ · L3
- Do: stream tokens/events; parallelize tools; track TTFT and total.

**7.6 Caching (result / semantic)** · ★★☆☆☆ · L2

**7.7 Gateway** · ★☆☆☆☆ · L1

### 8. RAG ★★★★☆

**8.1 Chunking** · ★★★★★ · L4
- Do: structure-aware chunks (headings, functions); 200–800 tokens; overlap; keep metadata.
- Ask: What does a user's question map to — a paragraph, a section, a function?
- Metrics: recall@k on retrieval eval set.
- Patterns: chunking is the #1 lever; fix it before touching models.

**8.2 Pipeline (ingest→embed→index→query→inject)** · ★★★★★ · L5
- Do: build it end-to-end once with pgvector; versioned index.

**8.3 Hybrid search + reranking** · ★★★★☆ · L4
- Do: vector + BM25 merged (RRF) → cross-encoder rerank top-50 → top-5.
- Ask: Are queries keyword-heavy (IDs, names)? Then BM25 matters a lot.
- Metrics: recall@k before/after rerank.

**8.4 Citations / grounding** · ★★★★☆ · L3
- Do: inject chunks with IDs; require the model to cite; verify cited IDs exist.

**8.5 Retrieval eval** · ★★★★☆ · L3
- Metrics: recall@k, MRR, faithfulness, answer relevance.

**8.6 Agentic RAG** · ★★★☆☆ · L3
- Do: `search(query)` as a tool the loop calls repeatedly; model refines queries.

**8.7 Embeddings & vector store** · ★★★☆☆ · L2
- Ask: Dimension/cost/latency; managed vs. pgvector (boring wins).

**8.8 Freshness / re-indexing** · ★★☆☆☆ · L2

**8.9 Query rewriting / HyDE** · ★☆☆☆☆ · L1

### 9. STATE & PERSISTENCE ★★★☆☆

**9.1 Checkpointing & resume** · ★★★★☆ · L4
- Do: persist state after every turn; resume from last checkpoint on crash/approval.
- Ask: Is state serializable? Are in-flight tool calls replay-safe?

**9.2 Idempotency keys** · ★★★★☆ · L3
- Do: key = hash(task_id, turn, tool, args); tool stores and dedups.

**9.3 Session vs. task** · ★★★☆☆ · L2

**9.4 Async execution / queues** · ★★★☆☆ · L3
- Do: task enqueued; worker runs loop; client polls or gets webhook.

**9.5 Durable execution engines** · ★☆☆☆☆ · L1

### 10. MEMORY ★★★☆☆

**10.1 In-context vs. external** · ★★★★☆ · L3
- Do: anything beyond one session goes to a store and is retrieved (§8).

**10.2 Scratchpad / working memory** · ★★★☆☆ · L3
- Do: a file or field the agent reads/writes; survives compaction.

**10.3 Write policy** · ★★★☆☆ · L3
- Ask: What's worth remembering? Who consented? How does it decay/dedup?

**10.4 Episodic / semantic / procedural** · ★★☆☆☆ · L2

### 11. ORCHESTRATION ★★★☆☆

**11.1 Workflow patterns** · ★★★★☆ · L4
- Do: chain, route, parallelize, orchestrator–workers, evaluator–optimizer; pick the simplest that fits.

**11.2 Subagent** · ★★★☆☆ · L4
- Do: child loop with fresh context + narrow tools; returns a structured summary.
- Ask: Am I doing this for context isolation or parallelism? If neither, don't.
- Patterns: return summaries, not transcripts.

**11.3 Handoffs & shared state** · ★★☆☆☆ · L2

**11.4 Coordination failure modes** · ★★☆☆☆ · L2
- Duplicated work, conflicting writes, unbounded cost, lost context.

**11.5 Topologies / frameworks** · ★☆☆☆☆ · L1 (LangGraph, OpenAI Agents SDK, Claude Agent SDK, CrewAI, AutoGen — verify current before choosing)

### 12. MCP ★★☆☆☆

**12.1 What it is / vs. function calling** · ★★★☆☆ · L3
- Function calling = the model-side mechanism; MCP = protocol to discover and call tools across clients.

**12.2 Server/client/host, primitives, transport** · ★★☆☆☆ · L2

**12.3 Auth & tool poisoning** · ★★☆☆☆ · L2

### 13. MODEL LAYER EXTRAS ★★☆☆☆

**13.1 Structured output** · ★★★☆☆ · L3 — prefer tool-call schema for structure.
**13.2 Model routing** · ★★☆☆☆ · L2
**13.3 Extended thinking** · ★★☆☆☆ · L2
**13.4 Sampling params** · ★☆☆☆☆ · L1
**13.5 Multimodal** · ★☆☆☆☆ · L1
**13.6 Fine-tuning / RL** · ★☆☆☆☆ · L1 (boundary)

### 14. SERVING & PRODUCT ★★☆☆☆

**14.1 Sync vs. async UX** · ★★☆☆☆ · L2
**14.2 Multi-tenancy** · ★★☆☆☆ · L2
**14.3 Canary / rollout** · ★★☆☆☆ · L2
**14.4 Cost model** · ★★☆☆☆ · L2

---

## Part 3 — Study guide (ranked from root; each item says what "done" looks like)

Study order = list order. Finish a level before descending. Time split: L5 60%, L4 25%, L3 10%, L2+L1 5%.

### Level 5 — Design + implement · target: whiteboard it cold, and have code you've run

| # | Item | Sig | You're done when you can… | How to get there |
|---|---|---|---|---|
| 1 | 1.1 Task definition | ★★★★★ | Write the one-pager + 20 golden examples for your project in 30 min | Do it for your project first, before any code |
| 2 | 2.1 Loop skeleton | ★★★★★ | Write the `while` loop from memory in Python incl. tool dispatch | Build MVP0: one tool, one loop, prints trace |
| 3 | 2.2 Termination | ★★★★★ | Name 5 stop conditions and what each returns | Add `finish` tool + max_turns + cost cap; log stop reason |
| 4 | 2.3 State | ★★★★★ | Show a typed state struct and say what survives a crash | Pydantic/dataclass; serialize to JSON every turn |
| 5 | 3.1 Tool schema | ★★★★★ | Rewrite a bad tool description and explain why the model now picks it | Write 5 tools; measure wrong-tool rate on golden set |
| 6 | 3.2 Result handling | ★★★★★ | Explain truncate-vs-pointer and your byte cap | Add a 200-line file tool; watch context blow up; fix it |
| 7 | 5.2 Context assembly | ★★★★★ | Draw the message order and say why stable→volatile | One pure `build_context(state)` function with unit tests |
| 8 | 5.3 System prompt | ★★★★★ | Show two versions and the eval delta between them | Version in repo; run golden set per change |
| 9 | 2.4 Error handling | ★★★★★ | Classify 4 error types and the response to each | Inject failures (kill API, bad args); assert behavior |
| 10 | 4.1 Permission model | ★★★★★ | Write `allow(tool,args,principal,mode)` and defend default-deny | Implement policy fn; modes read-only/ask/auto |
| 11 | 4.2 HITL gates | ★★★★★ | Walk approve→persist→resume without a blocking thread | Gate one write tool; resume from checkpoint |
| 12 | 6.1 Golden task set | ★★★★★ | Run it in one command and read per-category pass rate | 20 tasks + checkers in repo; grows from failures |
| 13 | 7.1 Tracing | ★★★★★ | Replay a failed task from its trace | Span per LLM/tool call; Langfuse or plain JSON |
| 14 | 8.2 RAG pipeline | ★★★★★ | Build ingest→pgvector→query→inject end-to-end | One evening; measure recall@5 |

### Level 4 — Trade-offs · target: argue the 2–3 deciding choices and name the failure modes

| # | Item | Sig | You're done when you can… | How to get there |
|---|---|---|---|---|
| 1 | 1.3 Workflow vs agent | ★★★★★ | Take any prompt and say chain/route/agent in 30 s with a reason | Classify 10 real tasks; read Anthropic taxonomy |
| 2 | 4.3 Prompt injection | ★★★★★ | Describe an attack via a tool result and the harness-level defense | Build one injected doc; watch your agent fall; fix |
| 3 | 5.1 Token budget | ★★★★★ | Give a slot allocation and eviction order | Instrument tokens/turn; plot growth |
| 4 | 3.3 Idempotency | ★★★★★ | Explain duplicate-write on retry and the key scheme | Map to your queue/payments experience |
| 5 | 6.2 Failure taxonomy | ★★★★★ | Bucket 20 failed traces and pick the fix order | Label your own failures |
| 6 | 7.2 Cost accounting | ★★★★★ | Quote $/task for your project and where it goes | Roll up per task; add a cap |
| 7 | 8.1 Chunking | ★★★★★ | Say why chunking beats model swaps and pick a size | Try 3 chunkers; compare recall@k |
| 8 | 1.2 Success metric | ★★★★★ | Name primary + 2 guardrail metrics for any agent | Set for your project |
| 9 | 5.4 Compaction | ★★★★☆ | Say what a summary must keep and when it fires | Implement at 70% cap; eval before/after |
| 10 | 5.5 Tool-result pruning | ★★★★☆ | Explain pointer-vs-summary after N turns | Implement; measure tokens/turn |
| 11 | 2.5 Planning | ★★★★☆ | Say when a plan step is worth its tokens | Add/remove plan step; compare on golden set |
| 12 | 2.7 Interrupts | ★★★★☆ | Explain interrupt = checkpoint + status | Read LangGraph interrupt impl |
| 13 | 3.4 Tool granularity | ★★★★☆ | Defend 5–15 tools and when to split into subagents | Count wrong-tool rate vs tool count |
| 14 | 3.5 Per-tool permissions | ★★★★☆ | Explain enforcement in harness vs prompt | Part of 4.1 |
| 15 | 6.3 CI regression | ★★★★☆ | Handle nondeterminism in a pass/fail gate | N runs, gate on mean |
| 16 | 7.4 Rate limits / fallback | ★★★★☆ | Backoff design + why fallback invalidates evals | Reuse your AWS retry patterns |
| 17 | 8.3 Hybrid + rerank | ★★★★☆ | Explain RRF and when BM25 matters | Add BM25 + reranker; measure |
| 18 | 9.1 Checkpointing | ★★★★☆ | Say what's replay-safe and what isn't | Persist state per turn; kill & resume |
| 19 | 11.1 Workflow patterns | ★★★★☆ | Sketch all five in a minute | Cookbook `patterns/agents` |
| 20 | 11.2 Subagent | ★★★☆☆ | Give the two legitimate reasons and the return contract | Add one subagent that returns a summary |

### Level 3 — Mechanism · target: explain A→B step by step and why that way (no build required)

| Item | Sig | You're done when you can… |
|---|---|---|
| 1.4 Non-goals / blast radius | ★★★★☆ | List irreversible actions for a given agent |
| 8.4 Citations | ★★★★☆ | Explain ID injection + verification |
| 8.5 Retrieval eval | ★★★★☆ | Define recall@k, MRR, faithfulness |
| 2.6 Reflection | ★★★☆☆ | Say when a critic is worth it |
| 3.6 Parallel tools | ★★★☆☆ | Explain independence check |
| 3.7 Sandbox | ★★★☆☆ | List isolation controls |
| 4.4 Egress / 4.5 Exfiltration | ★★★☆☆ | Describe secrets-in-URL leak and the scan |
| 5.6 Prompt caching | ★★★☆☆ | Explain byte-identical prefix |
| 5.7 JIT / skills | ★★★☆☆ | Say what moves out of the prefix |
| 6.4 Outcome vs trajectory | ★★★★☆ | Give one check of each |
| 6.5 LLM-as-judge | ★★★☆☆ | Explain calibration against humans |
| 7.3 Versioning · 7.5 Streaming | ★★★☆☆ | Hash-in-trace; TTFT |
| 8.6 Agentic RAG | ★★★☆☆ | Retrieval-as-tool loop |
| 9.2 Idempotency keys · 9.4 Async | ★★★☆☆ | Key scheme; enqueue/poll |
| 10.1–10.3 Memory basics | ★★★☆☆ | Store→retrieve→inject; write policy |
| 12.1 MCP vs function calling | ★★★☆☆ | One-sentence distinction |
| 13.1 Structured output | ★★★☆☆ | Why tool-call schema |

### Level 2 — Explain what + why (one paragraph each, no mechanism)
4.6 Guardrails · 5.8 Context rot · 5.9 Few-shot · 6.6 Online eval · 7.6 Caching · 8.7 Embeddings/vector store · 8.8 Freshness · 9.3 Session vs task · 10.4 Memory types · 11.3 Handoffs · 11.4 Coordination failures · 12.2–12.3 MCP internals/auth · 13.2 Routing · 13.3 Thinking · 14.x Serving

### Level 1 — Recognize (one sentence)
3.8 Computer use · 6.7 Benchmarks · 7.7 Gateway · 8.9 HyDE · 9.5 Durable execution · 11.5 Topologies/frameworks · 13.4–13.6 Sampling/multimodal/fine-tuning

---

## References

1. [anthropics/anthropic-cookbook](https://github.com/anthropics/anthropic-cookbook) — runnable loop, tool use, RAG; `patterns/agents` matches §11.1.
2. [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) — checkpointing + interrupts (§2.7, §9.1) as a reference implementation.
3. [Anthropic — Building effective agents](https://www.anthropic.com/research/building-effective-agents) — §1.3 and §11.1.
4. [Anthropic — Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — §5.
5. [Model Context Protocol docs](https://modelcontextprotocol.io/) — §12.
6. [Simon Willison — prompt injection series](https://simonwillison.net/series/prompt-injection/) — §4.3.