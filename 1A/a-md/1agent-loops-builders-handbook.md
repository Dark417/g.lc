# Agent Loops: A Builder's Handbook

## 1. The loop, precisely

An agent is an LLM that uses tools in a loop until a task is done. That is the whole idea, and it is worth being precise about it because almost every architectural decision downstream is a variation on this skeleton:

```python
def agent_loop(task, tools, model, max_steps=25):
    messages = [
        {"role": "system", "content": system_prompt(tools)},
        {"role": "user", "content": task},
    ]
    for step in range(max_steps):
        # 1. THINK — model decides next action given full context
        response = model.complete(messages, tools=tool_schemas(tools))

        # 2. TERMINATE — model emitted a final answer, no tool call
        if response.stop_reason == "end_turn":
            return response.text

        # 3. ACT — execute the tool call(s) the model requested
        messages.append(response.assistant_message)  # the tool_use block
        for call in response.tool_calls:
            result = tools[call.name](**call.arguments)  # side effects happen here
            messages.append(tool_result_message(call.id, result))

        # 4. OBSERVE — result is now in context; loop repeats with new state

    return "max_steps_exceeded"  # the most important branch most people forget
```

Four phases — **think → act → observe → repeat** — wrapped in a `while`/`for` with a hard ceiling. Everything else (planning, memory, multi-agent, reflection) is either a refinement of one of these phases or a structure built *around* this loop. If you internalize one thing, internalize that the loop is just software: a control-flow construct with an LLM at the decision point and a `switch` statement over tool names at the action point.

Two structural facts shape everything:

- **The context window is the agent's entire working memory.** There is no hidden state between steps except what you append to `messages`. Every tool result, every prior thought, every error is either in context or gone. This is why "context engineering" (Section 9) is the dominant skill, not prompt engineering.
- **The loop is non-deterministic.** The same task can take 3 steps or 14, call different tools, or loop forever. Traditional software is a contract between deterministic systems; an agent loop breaks that contract on purpose, and you pay for it in testing, observability, and cost.

### Workflow vs. agent — the distinction that decides your design

| | **Workflow** | **Agent** |
|---|---|---|
| Control flow | Predefined in *your* code | LLM decides at runtime |
| Path | Fixed DAG / known steps | Dynamic, discovered per-run |
| Predictability | High | Low |
| Cost / latency | Bounded, knowable | Variable, can spike |
| Debuggability | Easy (it's a flowchart) | Hard (traces, not stack traces) |
| Use when | Steps are known in advance | Steps can't be enumerated ahead of time |

The honest industry consensus (Anthropic, HumanLayer, most production teams): **most things billed as "agents" are mostly deterministic workflows with LLM steps sprinkled in at the right points.** That is a feature, not a failure. You reach for a true open-ended loop only when the task genuinely cannot be expressed as a graph you wrote yourself. The rest of this handbook spends a lot of words on the loop, but the meta-advice is: *start with the least agentic thing that works, add loop autonomy only when simpler structures fall short.*

---

## 2. Anatomy / architecture

A production loop has more moving parts than the 30-line skeleton. The components:

```
┌──────────────────────────────────────────────────────────────┐
│                        AGENT RUNTIME                           │
│                                                                │
│   ┌─────────────┐   prompt    ┌──────────────┐                 │
│   │  CONTEXT     │ ──────────► │    MODEL     │                 │
│   │  ASSEMBLER   │             │  (reasoner)  │                 │
│   │ - sys prompt │ ◄────────── │              │                 │
│   │ - history    │  tool_call  └──────────────┘                 │
│   │ - memory     │                    │                         │
│   │ - retrieved  │                    ▼                         │
│   └─────────────┘            ┌──────────────────┐               │
│         ▲                    │  TOOL DISPATCHER  │              │
│         │  observation       │  (switch on name) │              │
│         │                    └──────────────────┘               │
│         │                            │                          │
│   ┌─────┴────────┐    ┌──────────────┼───────────────┐         │
│   │  STATE STORE  │   │       TOOL REGISTRY           │         │
│   │ - checkpoints │   │  search │ code │ http │ MCP   │         │
│   │ - exec state  │   └───────────────────────────────┘         │
│   └──────────────┘                                              │
│                                                                 │
│   Cross-cutting: STOP CONDITIONS · ERROR HANDLER · OBSERVABILITY│
└─────────────────────────────────────────────────────────────────┘
```

**Model (the reasoner).** The decision-maker. Picks the next action. Capability here sets the ceiling: a smarter model recovers from errors and navigates ambiguity without you scripting it, which lets you remove orchestration scaffolding. Model routing matters — use a strong model for planning/final review, a cheap fast one for inner-loop mechanical steps.

**Context assembler.** Builds the prompt for *every* turn: system prompt + tool definitions + conversation history + retrieved knowledge + relevant memory. This is the single highest-leverage component. Token budget is finite; what you put in and leave out determines quality more than model choice past a point.

**Tool registry + dispatcher.** Tools are *just structured outputs* the model emits, mapped to functions you run. The dispatcher is a `switch`/dict-lookup on the tool name. The interface between your code and the model here is the **agent–computer interface (ACI)**: tool names, descriptions, argument schemas, and return formats. Treat it with the same care you'd give a public API or a human UI — bad tool docs are the #1 cause of agent failure that looks like "the model is dumb."

**State store.** Conversation state lives in context, but for durability you persist it: checkpoints (so a crashed or paused run resumes), execution state separate from business state, and the message thread itself. Durable execution (Temporal, DBOS, LangGraph checkpointers) lets a loop survive process restarts and human-in-the-loop pauses that last hours or days.

**Stop conditions.** The loop must terminate. Real stop conditions, in priority order:
1. Model emits a terminal response (no tool call).
2. Model calls an explicit `done`/`final_answer` tool (more reliable than "no tool call" — you can validate the output schema).
3. Hard step ceiling (`max_steps`).
4. Token/cost budget exceeded.
5. Wall-clock timeout.
6. Repeated-state / no-progress detector (same tool + same args N times → break).

You need *all* of these in production. The model will eventually loop forever on some input; the only question is whether your ceiling catches it cheaply or your bill catches it expensively.

**Error handler.** Tool calls fail (timeouts, bad args, 500s). The agentic move is to feed the error back into context as an observation and let the model retry/adapt — this is most of where "error recovery" comes from. But unbounded retry is a runaway-loop generator, so cap retries per tool and escalate to a human or abort after the cap.

**Observability.** Not optional. An agent that loops, calls the wrong tool, or hallucinates still returns a 200 within normal latency, so traditional APM reports a healthy system while quality silently rots. You need causal tracing (the execution path, not just the final output), per-step spans, cost attribution, and the ability to answer "why did the agent fail on step 6?" More in Section 10–11.

---

## 3. When to use a loop (and when not to)

### Use an agent loop when

- **Steps can't be enumerated ahead of time.** The path depends on intermediate results the model discovers (research, debugging, multi-round search-and-analysis). If you can't draw the flowchart, you may need the loop to discover it.
- **The branching factor is huge.** Diagnostic systems, anything juggling dozens of shifting variables where hardcoding every path is intractable.
- **Open-ended tool use over a long horizon.** Coding agents, "operate my computer," research assistants — tasks where success requires many tool calls whose sequence is data-dependent.
- **The value of autonomy exceeds the cost of unpredictability.** You can tolerate variable cost/latency and you've got observability + evals to manage the risk.

### Do NOT use a loop when

- **A workflow does the job.** If the steps are known, write the DAG. It's cheaper, faster, predictable, and debuggable. Prompt-chaining or routing (Section 4) covers a shocking fraction of "agent" use cases.
- **High-frequency, low-complexity, latency-sensitive.** Classification, extraction, simple Q&A at scale. A single augmented LLM call or a fixed chain has predictable cost and latency an agent can't match. A loop here is 4–15× the token cost for no benefit.
- **You can't tolerate the failure modes.** Irreversible, high-stakes actions without human checkpoints. If a wrong tool argument at step 2 silently corrupts everything downstream and there's no undo, don't hand the wheel to a non-deterministic system.
- **You have no observability or evals yet.** Shipping an open-ended loop blind is how you get silent quality degradation discovered by customers, hours later.

### A useful heuristic ladder (climb only as needed)

```
1. Single LLM call                          (cheapest, most predictable)
2. Augmented LLM (call + retrieval + tools)
3. Fixed workflow (prompt chain / router)
4. Workflow with a bounded loop (evaluator-optimizer)
5. Single agent, open loop, narrow toolset
6. Orchestrator + workers / multi-agent      (most powerful, least predictable)
```

Each rung up buys capability and costs predictability, money, and debuggability. The marginal cost of climbing is roughly *one extra LLM call's latency and error rate per step.* Most teams ship best on rungs 2–4 and only need 5–6 for genuinely open-ended problems.

---

## 4. Common patterns — exhaustive

Patterns split into three layers: the **building block** (augmented LLM), **workflow patterns** (you own control flow), and **agentic patterns** (the model owns control flow). The Anthropic taxonomy covers the first two cleanly; the agentic-loop patterns come from the research literature (ReAct, Reflexion, ToT, etc.) and production practice.

### 4.0 Building block — the Augmented LLM

The atom of every system: one LLM enhanced with **retrieval + tools + memory**. The model generates its own search queries, selects tools, and decides what to retain. Tune two interfaces: how it accesses these augmentations, and how well-documented/curated each augmentation is for *your* use case. Everything below composes augmented LLMs.

### Workflow patterns (predefined control flow)

**4.1 Prompt chaining.** Decompose a task into a fixed sequence of steps; each LLM call processes the previous output. Optional programmatic "gate" checks between steps to fail fast.
- *Use when:* the task cleanly factors into fixed subtasks, and trading latency for accuracy is worth it.
- *Example:* generate marketing copy → validate it meets criteria → translate it. Outline a doc → check the outline → write from it.

**4.2 Routing.** A classifier LLM (or cheap model) inspects the input and dispatches to one of several specialized downstream handlers.
- *Use when:* distinct input categories are better handled separately, and classification is reliable.
- *Example:* route customer queries to refund / technical / general handlers; route easy questions to a cheap model and hard ones to a strong model (cost optimization).

**4.3 Parallelization.** Run LLM calls concurrently, two flavors:
- *Sectioning:* split into independent subtasks run in parallel, aggregate. E.g. one model handles the query while another screens it for policy violations.
- *Voting:* run the *same* task multiple times for diverse outputs, then pick/aggregate (majority vote, best-of-N). E.g. review code for vulnerabilities with several passes; assess content against multiple criteria in parallel.
- *Use when:* subtasks parallelize for speed, or multiple attempts raise confidence.

**4.4 Orchestrator–workers.** A central LLM dynamically decomposes a task, delegates subtasks to worker LLMs, and synthesizes results. *The subtasks aren't predefined* — the orchestrator decides them based on input — which makes this the bridge between workflow and agent.
- *Use when:* you can't predict the subtasks in advance (unlike parallelization's fixed split).
- *Example:* a coding change that touches an unknown set of files; multi-source research where the orchestrator decides what to search.

**4.5 Evaluator–optimizer.** One LLM generates, a second evaluates and gives feedback, loop until the evaluator is satisfied (or a cap).
- *Use when:* you have clear eval criteria *and* iterative refinement measurably helps — the two tells are that a human's articulated feedback demonstrably improves the output, and that an LLM can produce comparable feedback.
- *Example:* literary translation with nuance critique; multi-round search where an evaluator decides if more searching is warranted. This is a *bounded loop* — the cheapest agentic pattern, and the one to reach for before going fully open-ended.

### Agentic patterns (model owns control flow)

**4.6 ReAct (Reason + Act).** The canonical loop. The model interleaves a *reasoning trace* ("Thought:") with *actions* ("Action: search[...]") and consumes *observations*, repeating until done. Most "tool-calling agents" are ReAct under the hood — modern function-calling APIs make the Thought/Action/Observation structure native. This is your default open-loop pattern.
- *Use when:* general-purpose tool use where the model should reason about each step.
- *Watch:* reasoning traces eat tokens; the model can rationalize bad actions in its "thoughts." Keep the toolset small.

**4.7 Plan-and-Execute (Plan-and-Solve).** Split into a *planner* that produces a multi-step plan up front and an *executor* that runs steps (often with a smaller/cheaper model), re-planning when reality diverges.
- *Why:* ReAct re-reasons from scratch every step (expensive, drift-prone over long horizons). Planning once and executing is cheaper and stays on-goal for long tasks.
- *Use when:* long-horizon tasks with many steps; you want fewer expensive reasoning calls.
- *Variants:* ReWOO (reason without observation — plan all tool calls up front, then execute), LLMCompiler (parallel DAG execution of the plan).

**4.8 Reflection / Self-critique / Reflexion.** After acting, the model critiques its own output (or a separate critic does) and revises. *Reflexion* adds persistent self-reflective memory across attempts: failures become written lessons fed into the next try.
- *Use when:* output quality benefits from iteration and you have a signal (tests, eval, the model's own critique) to reflect on.
- *Relation:* evaluator-optimizer is the workflow version (you own the loop); reflection is the model owning it.

**4.9 Tree-of-Thoughts (ToT) / Language Agent Tree Search (LATS).** Explore multiple reasoning branches, evaluate them, backtrack from dead ends — search over a tree of partial solutions instead of a single linear chain. LATS combines this with tool use and reflection (MCTS-style).
- *Use when:* problems with large solution spaces where exploration + backtracking pays (puzzles, planning, hard reasoning).
- *Cost:* expensive — many model calls per problem. Rarely worth it in production vs. plan-execute + reflection.

**4.10 CodeAct (code as action).** Instead of emitting JSON tool calls, the agent writes and executes **code** as its action; the interpreter's output is the observation. Tools become library functions the generated code calls. HuggingFace `smolagents` is built around this.
- *Why:* code is more expressive than fixed tool schemas — control flow, composition, and data manipulation come free; one code action can replace several tool-call round-trips.
- *Watch:* you must sandbox execution (it runs arbitrary code). Higher capability, higher blast radius.

**4.11 Multi-agent / Hub-and-spoke (orchestrator with sub-agents).** A lead/orchestrator agent spawns specialist sub-agents (researcher, planner, implementer, reviewer, tester), each with its *own context window and toolset*, coordinating via handoffs or a shared store.
- *Why it works:* **context isolation.** Each sub-agent gets a clean, focused context for its job; the orchestrator only sees distilled results, not the sub-agent's full reasoning. This is the dominant reason multi-agent beats a single mega-context agent on complex tasks — not "specialization" per se, but keeping each context window relevant.
- *Coordination styles:*
  - *Handoff:* control transfers from one agent to another (OpenAI Agents SDK's core abstraction). Good for routing-style flows (triage → specialist).
  - *Hub-and-spoke with file/store handoff:* orchestrator delegates, sub-agents write results to a shared location (files in `docs/`, a blackboard, a state object), orchestrator reads and synthesizes. Robust because handoffs are durable artifacts, not just messages.
  - *Blackboard:* agents read/write a shared workspace; loosely coupled, good when contributions are independent.
- *Hard constraint to know:* in many runtimes (e.g. Claude Code), **sub-agents can't spawn sub-agents** — only the top-level session orchestrates. That forces a hub-and-spoke topology with file-based handoffs rather than arbitrary nesting. Design for one level of delegation.
- *Cost reality:* multi-agent is ~15× the tokens of a single chat turn and ~4× a single agent. Use it when the task is high-value and parallelizable, not by default.

**4.12 Network / swarm.** Agents talk peer-to-peer with no central orchestrator, deciding among themselves who acts next. Maximum flexibility, maximum unpredictability and cost. Rarely the right production choice; useful for simulation/research.

### Pattern selection cheat-sheet

| Task shape | Pattern |
|---|---|
| Fixed known steps | Prompt chaining |
| Distinct input categories | Routing |
| Independent subtasks, want speed | Parallelization (sectioning) |
| Need confidence / guardrails | Parallelization (voting) |
| Subtasks unknown until runtime | Orchestrator–workers |
| Clear quality criteria + refinement helps | Evaluator–optimizer |
| General open-ended tool use | ReAct |
| Long horizon, many steps | Plan-and-Execute (+ re-plan) |
| Output needs iteration on a signal | Reflection / Reflexion |
| Huge search space, backtracking pays | ToT / LATS |
| Action = data manipulation / composition | CodeAct |
| Complex task, parallel specialties | Multi-agent hub-and-spoke |

---

## 5. Own your control flow (the production discipline)

The most useful production framing comes from the **12-factor agents** philosophy: the best agents are *mostly software*, with the LLM owning only the decisions it must. Key factors worth lifting into any design:

- **Own your control flow.** Don't outsource the loop to a framework you don't understand. The loop is a `switch` over tool calls plus a context append — write it, or at least be able to read every line of the one you adopt. This buys you the ability to break, pause, branch, and inject deterministic steps anywhere.
- **Tools are structured outputs.** A "tool call" is just the model emitting JSON that your code dispatches on. Demystifying this lets you treat the model's output as data and route it however you like (including to a human).
- **Own your prompts and your context window.** Don't let the framework decide what goes into the model. Context assembly is your application logic; keep full control of it. You don't even have to use the standard chat message format if a custom serialization works better.
- **Unify execution state and business state; launch/pause/resume via simple APIs.** Make runs durable and inspectable. An agent that can serialize its state, pause for a human, and resume hours later is production-grade; one that only lives in a process's memory is a demo.
- **Small, focused agents over one giant agent.** Narrow scope = smaller context, fewer tools, more reliable. Compose small agents rather than building one omniscient loop.
- **Contact humans as a first-class tool.** "Ask a human" should be a tool the agent can call, with the same launch/pause/resume durability. Human-in-the-loop isn't a bolt-on; it's an action.
- **Stateless reducer mental model.** Think of the loop as `new_state = f(state, event)` — a reducer over an event stream. This makes it testable, replayable, and resumable.

The throughline: **agents are software with LLM decision points, not magic.** Treat the LLM as one (unreliable, expensive, powerful) function call inside an otherwise normal, well-engineered system.

---

## 6. Frameworks

The framework's actual job is to manage the loop and the surrounding plumbing: calling the model with the right messages/tools/config, parsing tool calls, dispatching them, appending observations, handling errors, persisting state, and giving you observability hooks. That plumbing has more parts than people credit. Frameworks differ mostly in *how much of it they handle vs. how much you still build*, and in their opinions about multi-agent, state, and typing.

As of mid-2026 the landscape (verify current versions — this space moves monthly):

| Framework | Owner | Sweet spot | Notes |
|---|---|---|---|
| **LangGraph** | LangChain Inc. | Stateful, durable production workflows; explicit graph control flow | Graph/state-machine model: nodes + edges, checkpointing, human-in-the-loop, conditional branching, parallel/cyclic graphs. The default for "serious stateful agent in Python." Most enterprise-verified deployments. Steeper concept curve. |
| **OpenAI Agents SDK** | OpenAI | Low-friction GPT-centric agents; clean handoffs | Small opinionated wrapper around the loop. Core abstractions: agents, handoffs, guardrails, sessions. 2026 added native sandboxing, sub-agents, filesystem tools, first-class MCP. Type-safe, debuggable. Lock-in toward OpenAI. |
| **Claude Agent SDK** | Anthropic | Autonomous coding/research on Claude; long-horizon | Wrapper around the loop with first-class support for Claude features (computer use, prompt caching, memory primitives, Files API). Converged on a shape similar to OpenAI's SDK. |
| **Pydantic AI** | Pydantic team | Type-safe, composable, moderately-scoped agents in Python | Brings Pydantic's validation discipline to agents/tools: typed inputs, outputs, dependencies. Read-every-line minimalism. Augment with other libs for big multi-agent/checkpointing systems — at which point ask if you wanted LangGraph. |
| **CrewAI** | CrewAI | Role-based multi-agent collaboration | Working multi-agent system in 20–50 lines. Best when the task maps cleanly to roles (planner/researcher/writer). Less control than LangGraph. |
| **Microsoft Agent Framework** | Microsoft | .NET / Azure-native teams | AutoGen + Semantic Kernel merged; v1.0 GA April 2026. General-purpose runtime; first-class Python/C#/Java. |
| **Google ADK** | Google | Multimodal agents, GCP-native, A2A interop | Strong for multimodal + cross-framework interop (A2A protocol). |
| **smolagents** | HuggingFace | Code-execution (CodeAct) agents | Minimal; agent writes/runs Python as its action. Great for learning the CodeAct pattern. |
| **LangChain (v1.0)** | LangChain Inc. | Single-agent ReAct loops, huge integration library | ~700 connectors as of 2026; better than its reputation. Use for breadth of integrations; graduate to LangGraph for state. |
| **LlamaIndex** | LlamaIndex | RAG-centric agents | When retrieval is the central problem. |
| **Letta (ex-MemGPT)** | Letta | Long-term memory agents | Memory as a first-class, persisted concern. |
| **DSPy** | Stanford | Optimizing prompts/pipelines programmatically | Compile prompts against metrics instead of hand-tuning. Different axis than the others. |
| **Mastra / Vercel AI SDK** | — | TypeScript-first teams | Mastra = broadest TS feature set; Vercel AI SDK = streaming web UI. |

**Choosing, in one breath:** Python + stateful/durable/regulated → **LangGraph**. Python + type-safety + moderate scope → **Pydantic AI**. All-in on one vendor, want shortest path to prod → that vendor's SDK (**OpenAI Agents SDK** / **Claude Agent SDK** / **Google ADK**), accepting lock-in. Role-based multi-agent prototype fast → **CrewAI**. TypeScript → **Mastra** (or Vercel AI SDK for streaming UIs). RAG-heavy → **LlamaIndex**. Learning the mechanics → **roll your own loop first**, then adopt.

**The contrarian-but-correct take:** for your *first* real agent, write the loop yourself (the 30 lines in Section 1, hardened). You'll understand every failure, and you'll be able to read any framework's source after. Many strong production teams roll their own stack precisely because frameworks add abstraction layers that complicate debugging and encourage unnecessary complexity. Adopt a framework when you need its specific plumbing (durable state, checkpointing, a big integration library), not by default.

---

## 7. Integrations

**Model Context Protocol (MCP).** The emerging standard for connecting agents to external tools/data/services via a uniform server interface. Instead of writing a bespoke client per API, you point the agent at MCP servers and it discovers their tools. First-class in OpenAI Agents SDK, Google ADK, LangChain, Claude Code, etc. Build your own with FastMCP (Python) or the TS SDK; test with MCP Inspector. Useful servers in practice: filesystem, GitHub, a search provider (Brave/Tavily/Exa), a browser/devtools server, a code-intelligence server (Serena), docs retrieval (Context7), sequential-thinking. **Caveat:** hundreds of MCP tools in one context is itself a context-engineering problem — each tool definition costs tokens and dilutes the model's tool selection. Curate; don't dump every server in.

**Tool/function calling.** The native integration layer below MCP. The model emits a structured call; you validate args (Pydantic / JSON Schema), execute, return a result. Best practices: small focused toolsets, unambiguous names, rich descriptions with examples, return *useful* error messages (the model reads them), and design return shapes the model can actually use (token-efficient, not a 50KB JSON dump).

**Retrieval / knowledge.** Vector stores (pgvector, Qdrant, Pinecone) + an embedding model for RAG; the agent generates queries and consumes results as observations. Increasingly hybrid: pre-inference embedding retrieval *plus* agentic "go fetch more" tools. LlamaIndex/LangChain provide the plumbing.

**Memory.** Short-term = the context window (ephemeral, per-run). Long-term = persisted across runs: episodic (what happened), semantic (facts/preferences), procedural (learned how-tos). Backends: a DB + retrieval, or purpose-built memory layers (Letta/MemGPT, Mem0, Zep). Memory is retrieval into context, governed by the same token-budget discipline.

**Durable execution / orchestration.** Temporal, DBOS, Prefect, Inngest, Restate — for long-running, resumable, fault-tolerant loops (survive restarts, pause for human approval for days, retry idempotently). LangGraph documents integrations with several of these.

**Observability / evals.** Langfuse (open-source baseline, OpenTelemetry-first), LangSmith (LangChain-native), Braintrust (eval-science focus), Arize Phoenix (OTel/open-source), plus framework-native tracing (OpenAI, Microsoft Foundry). Instrument LLM calls *and* tool invocations as spans.

**Human-in-the-loop.** Approval gates, edit-the-plan, "ask a human" as a tool. HumanLayer and framework-native interrupt/resume primitives (LangGraph `interrupt`). Essential for high-stakes actions.

---

## 8. Best practices

**Design.**
- *Start simple; add agency only when it pays.* Climb the ladder (Section 3) one rung at a time. The best system is the least agentic one that meets the bar.
- *Maintain simplicity, prioritize transparency, craft the ACI.* These three (Anthropic's core principles) carry most of the weight. Transparency = explicitly show the agent's plan/steps. ACI = invest in tool docs and tool testing as much as you would prompts.
- *Small focused agents over monoliths.* Narrow scope, fewer tools, smaller context → more reliable. Compose.
- *Own your control flow, prompts, and context.* (Section 5.)

**Tools / ACI.**
- Few, well-chosen tools beat many overlapping ones. Each tool dilutes selection and costs tokens.
- Name tools unambiguously; write descriptions a competent intern could follow; include examples and edge cases. *Poke-yoke* the args (make wrong usage hard).
- Return token-efficient, model-usable results. Errors are messages to the model — make them actionable.
- Build an eval for your tools and let a coding agent optimize them against it.

**Loop hygiene.**
- Always set `max_steps`, a token/cost budget, a wall-clock timeout, and a no-progress detector. All four.
- Prefer an explicit `final_answer`/`done` tool with a validated output schema over "model stopped calling tools."
- Feed errors back as observations for recovery, but cap retries and escalate.

**Context engineering.** (Expanded in Section 9 — it's that important.) Curate what's in the window every turn; compact aggressively; isolate context per sub-agent; retrieve just-in-time rather than front-loading everything.

**Evaluation.** Three layers, all needed:
1. *Unit evals on discrete steps* (did it pick the right tool with right args?).
2. *LLM-as-judge regression suites* for subjective output quality, run in CI to gate releases.
3. *Production trace sampling* with online scoring to catch drift the offline set misses.
Convert every production failure into an eval case. Use multi-turn evals — single-turn ones miss goal drift, tone drift, and contradiction that only emerge as context accumulates. Build the eval set from one real, manually-validated run before you scale.

**Operational.**
- Trace everything (causal, span-level: model calls + tool calls + reasoning). Without it you can't answer "why did step 6 fail?"
- Attribute cost per trace/session/tenant.
- Idempotent tools where possible (retries shouldn't double-charge a card).
- Sandbox code execution and untrusted tool output.

**Process (maps to a staged build):** design doc → define functionalities/phases → **MVP0** (skeleton: one model, one tool, hardcoded loop, no memory) → **MVP1** (real toolset, retrieval, basic eval) → **MVP2** (multi-agent / durable state / observability / CI eval gates). Validate one complete path end-to-end before encoding it as reusable structure (a skill/sub-agent records a *proven* process, not a speculative one).

---

## 9. Context engineering (the dominant skill)

Since the loop is "LLMs using tools in a loop," and the loop's only memory is the context window, the central engineering problem has shifted from *prompt* engineering (wording one call) to *context* engineering (curating the whole window across many turns). Models exhibit **context rot**: as the window grows, attention to any given token degrades — more context is not strictly better, and a bloated window actively *lowers* quality. So context is a finite resource you budget.

Tactics, roughly in order of impact:

- **Compaction / summarization.** When history grows long, summarize older turns into a compact form and drop the raw tokens. The agent keeps the gist, not the transcript. Essential for long-horizon loops; without it you hit the window and degrade.
- **Sub-agent context isolation.** The real reason multi-agent works: each sub-agent runs a clean, focused context for its narrow job; the orchestrator only ingests the *result*, never the sub-agent's full reasoning trace. This keeps every window relevant. (Section 4.11.)
- **Just-in-time retrieval over front-loading.** Don't stuff everything the agent *might* need into the system prompt. Give it tools to fetch context when needed (read a file, search the KB). Pre-inference embedding retrieval + agentic fetch, hybridized.
- **Structured note-taking / scratchpad.** Let the agent persist findings to an external file/memory and re-read selectively, rather than carrying everything in-context.
- **Tool-result curation.** Don't dump raw 50KB API responses into context; project them to the fields the model needs.
- **System-prompt discipline.** Tools, instructions, and few-shot examples all compete for the same budget. Trim ruthlessly; measure quality, not prompt length.

The mental model: **every turn, you are re-deciding what the model gets to see.** That decision, not model choice past a threshold, sets your quality ceiling.

---

## 10. Concerns and failure modes

The six agent-specific failure modes (distinct from generic LLM failures) you must design against:

1. **Tool misuse.** Right tool, wrong arguments — or wrong tool, or right tools in the wrong order. A bad arg at step 2 silently corrupts every downstream step. The most common and most insidious production failure. *Mitigate:* arg validation, tool evals, constrained schemas, dry-run/confirm for destructive ops.
2. **Context loss / corruption.** Multi-turn state gets lost or mangled, especially when several tools mutate shared context. *Mitigate:* compaction, isolation, explicit state stores, idempotency.
3. **Goal drift.** Over a long conversation the agent wanders off the original objective; tone drifts; it contradicts itself. *Mitigate:* re-anchor the goal each turn (plan-execute keeps the plan in view), multi-turn evals, periodic "are we still on task?" checks.
4. **Retry / runaway loops.** The agent cycles — same reasoning, same tool — looking busy in the logs while making zero progress, burning tokens. *Mitigate:* no-progress detector, step/cost/time ceilings, loop-break on repeated state.
5. **Cascading errors (multi-agent).** One agent's bad output becomes another's input; errors compound across the network. *Mitigate:* validate at handoff boundaries, isolate, keep topologies shallow (hub-and-spoke, one delegation level).
6. **Silent quality degradation.** No error code, no exception, normal latency, 200 response — and the answer is wrong. Discovered hours later by a downstream consequence. *This is the defining agent risk.* APM cannot see it; only quality evaluation can. *Mitigate:* production trace sampling + online scoring + LLM-as-judge, failure clustering, alerting on quality not just errors.

Cross-cutting concerns:

- **Cost.** Loops multiply token spend: roughly 1× chat → 4× single agent → 15× multi-agent. An unbounded or runaway loop is a financial incident. Budget caps and routing (cheap model for mechanical steps) are not optional.
- **Latency.** Each loop iteration is a model round-trip; deep loops feel slow. Parallelize where independent; cap depth.
- **Security.** The agent executes actions and ingests untrusted content (tool results, retrieved docs, web pages) into a context that drives further actions → **prompt injection** and tool-poisoning. Treat all tool output as untrusted input. Sandbox code execution. Least-privilege tools. Human approval for irreversible/sensitive actions. Don't put secrets where a hijacked agent could exfiltrate them.
- **Non-determinism / reproducibility.** Same input, different path. Makes testing hard and bug repro harder. Trace everything; build eval sets; pin seeds/temperature where you can.
- **Debuggability.** You get traces, not stack traces. Causal, span-level tracing is the only way to answer "why step 6?" Logs show outputs; traces show the execution path.
- **Over-engineering.** The most common *meta*-failure: reaching for an open loop or multi-agent swarm when a chain or router would do. More agency = more ways to fail.

---

## 11. Trade-offs

The five dimensions that predict whether an agentic system survives production: **cost, latency, efficacy, assurance (safety/correctness guarantees), reliability.** Most architecture choices trade these against each other.

| Choice | You gain | You give up |
|---|---|---|
| Workflow → open loop | Handles open-ended tasks, error recovery, less scripting | Predictability, bounded cost/latency, easy debugging |
| Single agent → multi-agent | Context isolation, parallel specialties, higher ceiling on complex tasks | ~4× more cost, cascading-error risk, coordination complexity |
| More tools | Broader capability | Diluted tool selection, token cost, more misuse surface |
| Bigger context | More info available | Context rot (quality drops), higher cost/latency |
| Stronger model everywhere | Better decisions, less scaffolding | Cost; often overkill for mechanical inner-loop steps |
| Framework | Plumbing handled, faster start, ecosystem | Abstraction you must understand, debugging opacity, possible lock-in |
| Roll your own | Full control, total transparency, no lock-in | You build (and maintain) state, retries, observability yourself |
| Vendor SDK | Shortest prototype→prod path, first-class vendor features | Structural lock-in to one model ecosystem |
| Durable execution | Resumable, fault-tolerant, human-in-loop over days | Infra complexity, more moving parts |
| Reflection / ToT / voting | Higher quality on hard tasks | Multiplied calls → cost + latency |
| Plan-execute vs ReAct | Cheaper long-horizon, less drift | Less adaptive mid-task; re-plan overhead |
| Human-in-the-loop | Assurance on high-stakes actions | Latency (human time), throughput cap |
| Autonomy (YOLO/auto-approve) | Velocity, low friction | Blast radius on mistakes; only safe with sandboxing + reversibility |

**The master trade-off:** *autonomy vs. control.* Every step up the agency ladder hands the LLM more of the control flow, buying flexibility at the cost of predictability, cost-boundedness, and debuggability. The engineering art is giving the model exactly as much rope as the task requires and not one inch more — deterministic code everywhere you can, LLM decisions only where you must.

---

## 12. A reference build (mapping the loop to a staged MVP)

To ground this against an execution-first, MVP-staged process:

**Design doc.** State the task, why a loop (vs. a workflow), the toolset, stop conditions, the eval criteria, and the cost/latency budget. If you can't justify why a workflow won't do, stop here and build the workflow.

**MVP0 — skeleton.** Hand-written loop (Section 1). One strong model. 2–3 hardcoded tools with validated args. `max_steps` + `final_answer` tool + cost cap. No memory, no retrieval, no framework. Run one real task end-to-end and read the full trace by hand. Goal: prove the loop closes and terminates correctly.

**MVP1 — capability.** Real toolset (curate, don't dump). Add retrieval if the task needs knowledge. Add basic tracing (Langfuse) and a tiny eval set (the MVP0 run becomes case #1). Add error-feedback-into-context with retry caps. Add a no-progress detector. Goal: it handles the happy path + common failures reliably.

**MVP2 — production shape.** Pick the pattern the task actually needs: evaluator-optimizer if quality needs iteration; plan-execute if long-horizon; hub-and-spoke sub-agents if it factors into specialties (one delegation level, file/store handoffs). Add durable state if runs are long or need human pauses. Add CI eval gates (LLM-as-judge regression), production trace sampling + online scoring, cost attribution. Add human-in-the-loop on any irreversible action. Now adopt a framework if its plumbing (LangGraph checkpointing, etc.) earns its abstraction.

The discipline that ties it together: **validate one complete path manually before encoding it as reusable structure** (a sub-agent, a skill, a graph). Agentic structure should record a *proven* process, never a speculative one — otherwise you've built a non-deterministic system on top of an unvalidated assumption, which is two compounding sources of silent failure.

---

## References

**Canonical / foundational**
- Anthropic — *Building Effective Agents* (the taxonomy: augmented LLM, 5 workflow patterns, autonomous loop): https://www.anthropic.com/research/building-effective-agents
- Anthropic — *Effective Context Engineering for AI Agents* ("LLMs using tools in a loop"; context rot, compaction, sub-agent isolation): https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Anthropic — *Writing Effective Tools for AI Agents* (ACI, tool evals, simple agentic loops): https://www.anthropic.com/engineering/writing-tools-for-agents
- Anthropic cookbook (runnable pattern implementations): https://github.com/anthropics/anthropic-cookbook
- HumanLayer — *12-Factor Agents* (own your control flow / prompts / context; agents are mostly software): https://github.com/humanlayer/12-factor-agents

**Pattern / research lineage (read the repos/papers)**
- ReAct (Reason+Act): https://github.com/ysymyth/ReAct  ·  paper: https://arxiv.org/abs/2210.03629
- Reflexion (self-reflective memory): https://github.com/noahshinn/reflexion  ·  paper: https://arxiv.org/abs/2303.11366
- Tree of Thoughts: https://github.com/princeton-nlp/tree-of-thought-llm  ·  paper: https://arxiv.org/abs/2305.10601
- Plan-and-Solve prompting: https://arxiv.org/abs/2305.04091
- LATS (Language Agent Tree Search): https://github.com/lapisrocks/LanguageAgentTreeSearch
- CodeAct (code as action) / smolagents: https://github.com/huggingface/smolagents

**Frameworks (source = the real docs)**
- LangGraph: https://github.com/langchain-ai/langgraph
- OpenAI Agents SDK: https://github.com/openai/openai-agents-python
- Claude Agent SDK: https://github.com/anthropics/claude-agent-sdk-python
- Pydantic AI: https://github.com/pydantic/pydantic-ai
- CrewAI: https://github.com/crewAIInc/crewAI
- LlamaIndex: https://github.com/run-llama/llama_index
- Letta (MemGPT): https://github.com/letta-ai/letta
- DSPy: https://github.com/stanfordnlp/dspy

**Integrations / observability**
- Model Context Protocol (spec + servers): https://github.com/modelcontextprotocol  ·  servers: https://github.com/modelcontextprotocol/servers
- FastMCP (build MCP servers in Python): https://github.com/jlowin/fastmcp
- Langfuse (open-source tracing/evals): https://github.com/langfuse/langfuse
- Arize Phoenix (OTel-first observability): https://github.com/Arize-ai/phoenix
- Temporal (durable execution): https://github.com/temporalio/temporal

**Comparisons / current landscape (blog, secondary)**
- Speakeasy — agent framework comparison (LangGraph/PydanticAI/CrewAI/OpenAI SDK/Mastra/Vercel): https://www.speakeasy.com/blog/ai-agent-framework-comparison
- Langfuse — open-source agent frameworks compared: https://langfuse.com/blog/2025-03-19-ai-agent-comparison
- Latitude — agent failure modes (the six failure modes): https://latitude.so/blog/ai-agent-failure-detection-guide
- Braintrust — agent observability guide 2026: https://www.braintrust.dev/articles/agent-observability-complete-guide-2026

**Curated lists (for digging further)**
- Awesome LLM-powered agents / agent patterns: https://github.com/e2b-dev/awesome-ai-agents
- Anthropic Building Effective Agents pattern map: https://www.agentpatterns.ai/