# Context Engineering: A Top-Down Handbook for Agentic Systems

> Strategic and execution-oriented. Read top-to-bottom once for the full picture; use as a lookup after. Interview prep (L4/L5) is at the end.

---

## 0 — The Definition and the One Mental Model

**Context engineering is the discipline of deciding what occupies an LLM's context window at each step of a task — so the model has exactly what it needs, no more and no less, to produce the right next action.**

Prompt engineering asks "how do I phrase one instruction well." Context engineering asks "how do I manage the entire information environment of a model across a long, multi-step task." The unit of work moves from *a string* to *a system that assembles strings*.

The mental model that makes everything else fall into place:

> An LLM is a **stateless function**: `output = f(context)`. It remembers nothing between calls. The *only* thing that determines output quality is the bytes you place in the window for that one call.

Everything — your vector DB, tools, history, scratchpad, memory — is just **infrastructure for choosing which bytes go in**. So the whole field reduces to one recurring question, which you should hold in your head for the entire document:

> *At this exact step, for this exact decision, what is the minimal, highest-signal set of tokens that lets the model act correctly?*

Every technique below is an answer to that question.

---

## 1 — The Problem Being Solved

### 1.1 The window is scarce and contended

Windows are finite (≈200K for Claude; ~128K–1M elsewhere). It *feels* large until you run an agent that reads files, calls tools returning fat JSON, accumulates a long conversation, pulls retrieved docs, and carries dozens of tool schemas. One verbose tool result — a stack trace, an HTML page, a 2,000-row query — can eat 20K tokens. Four of those and the "huge" window is gone.

### 1.2 More context is not better — quality *degrades* with length

This is the central, counterintuitive fact: even when content *fits*, models get worse as the window fills. Named failure modes:

| Failure mode | What happens |
|---|---|
| **Context rot** | As tokens grow, the model's ability to recall/use any given token declines. Quality decays non-linearly with length. |
| **Lost in the middle** | Models attend well to the start and end, poorly to the middle. Mid-context info is nearly invisible. |
| **Distraction** | Irrelevant-but-plausible content pulls the model off-task onto tangents. |
| **Confusion** | Superfluous tool defs or near-duplicate facts cause wrong-tool calls and self-contradiction. |
| **Clash** | Two pieces of context disagree (old plan vs. new); the model can't reconcile and acts erratically. |

Upshot: **context is a budget you spend, and spending it badly is worse than not spending it.** The job is curation, not accumulation.

### 1.3 Why agents make this acute

A single Q&A turn is forgiving — you assemble context once. An **agent runs a loop**: model → tool → result → model → tool → …, for dozens or hundreds of turns, each appending to the window. Without active management the window grows monotonically until it (a) overflows or (b) rots into uselessness. Long-horizon agentic tasks are *the* domain where context engineering stops being optional and becomes the thing that decides whether the system works.

---

## 2 — Anatomy of a Context Window

The window is stacked layers you assemble fresh on each call. Knowing the layers is prerequisite to managing them.

```
┌─────────────────────────────────────────────┐
│ 1. System prompt / instructions             │  stable: role + rules
├─────────────────────────────────────────────┤
│ 2. Tool definitions (schemas)               │  which actions exist
├─────────────────────────────────────────────┤
│ 3. Retrieved knowledge (RAG, docs, memory)  │  facts pulled on demand
├─────────────────────────────────────────────┤
│ 4. Conversation / message history           │  grows every turn
├─────────────────────────────────────────────┤
│ 5. Tool results / observations              │  often biggest + noisiest
├─────────────────────────────────────────────┤
│ 6. Working state / scratchpad / plan        │  agent's notes to self
├─────────────────────────────────────────────┤
│ 7. Current user query / next instruction    │  the actual ask (put near end)
└─────────────────────────────────────────────┘
```

Each layer is a lever — include, compress, externalize, or drop. Structural facts to internalize:

- **Layers 1–2 are mostly static** but cost tokens on *every* call. A 10K-token prompt with 40 tool schemas is a 10K tax per turn, paid repeatedly.
- **Layers 4–5 grow unbounded** unless managed. ~80% of your effort lives here.
- **Layer 6 is your most powerful and most underused lever.** Externalizing state is how you escape the window's limits.
- **Position matters** (lost-in-the-middle): stable rules near the top, live instruction near the bottom, nothing critical buried mid-context.

---

## 3 — The Goal and Success Criteria

**Goal:** maximize *signal-to-noise* at every decision point, under a fixed token budget, across an arbitrarily long task.

You optimize three things that trade off:

1. **Completeness** — is everything the model *needs* present?
2. **Conciseness** — is everything it *doesn't* need absent?
3. **Coherence** — is what's present non-contradictory and well-ordered?

A perfectly engineered context is the *smallest set of tokens that is still complete and coherent*. Anthropic calls this the "right altitude": specific enough to guide behavior, general enough not to overfit or bloat.

**How you know it's working:**

- Tokens per turn stay roughly flat even as the task runs long.
- The model rarely re-asks for info it already had.
- Tool-selection accuracy stays high (no confusion-driven wrong calls).
- Cost and latency per task are predictable, not exploding with turn count.
- The agent finishes long tasks without losing the goal mid-run.

---

## 4 — The Five Strategies (the canonical map)

The field converged on a clean taxonomy (LangChain's Write/Select/Compress/Isolate, plus Offload from Anthropic). **Every technique is one of these verbs.** Learn them and you have the whole map.

### 4.1 WRITE — persist context *outside* the window

Get information out of the window into external storage: costs no tokens, recallable when needed.

- **Scratchpads** — the agent writes plans/notes/intermediate results to a file or state object; each turn reads back only the relevant slice. Anthropic's research agents persist their plan to memory precisely because a >200K context risks truncation — the plan must survive.
- **Memory** (longer-lived, cross-session): *episodic* (what happened), *semantic* (facts about user/world), *procedural* (how to do things).
- **Files as memory** — the most robust form. State lives on a filesystem; context holds only pointers (paths) plus what's needed now. This is how coding agents handle repos larger than any window.

> Principle: the filesystem is unlimited; the window is not. Treat the window as L1 cache, external storage as RAM/disk.

### 4.2 SELECT — pull the *right* context in, on demand

Out of everything you *could* include, choose only what this step needs.

- **RAG** — embed a corpus, retrieve top-k relevant chunks per query, inject only those. "Select" applied to documents.
- **Tool selection (RAG-over-tools)** — with 100 tools, don't inline 100 schemas (confusion); retrieve the ~5 relevant ones. Tool-selection retrieval can improve tool-use accuracy several-fold.
- **Memory selection** — fetch only memories relevant to the current task.
- **Dynamic few-shot** — pick the most relevant examples per query rather than hardcoding a fixed set.

Eternal tension: **recall vs. precision.** Too little → missing context, wrong answer. Too much → noise, distraction, rot. Tuning k, chunk size, re-ranking, thresholds *is* the work.

### 4.3 COMPRESS — keep only tokens that carry signal

When context must persist but is too large, shrink it.

- **Summarization** — replace long history (or a long tool output) with a shorter summary; can be recursive, hierarchical, or at boundaries (Cognition compresses full state with a fine-tuned model when handing off between agents).
- **Trimming/pruning** — drop by heuristic (oldest first, lowest-relevance first). Cheaper than summarizing, lossier.
- **Tool-result distillation** — the highest-ROI compression: a tool returns 10K tokens of JSON; you keep the 200 the model needs, *at the tool boundary, before it hits the window.*

> Watch-out: summarization is lossy and fails silently — it can drop the one fact that mattered. For high-stakes context, prefer *selection*, or summarize with a prompt/model tuned to preserve decisions and constraints.

### 4.4 ISOLATE — split context across boundaries

Don't put everything in one context. Partition.

- **Multi-agent / sub-agents** — each sub-agent gets its own clean window scoped to a sub-task and returns only a condensed result. This *multiplies* effective context (each sub-agent has a fresh 200K) and keeps each focused.
  - **Critical caveat (Cognition's "Don't Build Multi-Agents"):** parallel sub-agents with *independent* contexts make *conflicting* decisions because they don't see each other's reasoning. Isolation buys focus but costs coherence. Safe pattern: **read-heavy parallelism** (sub-agents gather in parallel) + **single-threaded action** (one agent decides/writes). Isolate for *retrieval breadth*, not for *coordinated action*.
- **Sandboxing** — run code in a sandbox; only the *result* returns to context (HuggingFace CodeAgent keeps heavy objects in the runtime).
- **State partitioning** — in LangGraph, the full state can be large but you expose only chosen fields per node; the rest stays out of context.

### 4.5 OFFLOAD — let the model fetch context itself, just-in-time

Rather than pre-loading everything possibly relevant, give the agent **lightweight identifiers** (paths, URLs, query handles) and **tools to fetch contents on demand.** The model decides at runtime what to pull — like a human navigating a codebase via filenames and grep instead of memorizing it.

- **Just-in-time retrieval** beats exhaustive pre-retrieval for large/unpredictable corpora.
- **Metadata is signal** — `2024-q3-incident-postmortem.md` tells the model *whether and when* to read without spending tokens on contents.
- **Hybrid** — pre-load the obvious core, offload the long tail. Claude Code pulls key files up front but uses `grep`/`glob` for the rest.

Trade-off: offloading adds round trips (latency, turns) for a leaner, more accurate context. For big/unpredictable corpora that trade usually pays.

---

## 5 — The End-to-End Workflow

Follows a design-doc → MVP0 → MVP1 → MVP2 rhythm.

### Phase A — Design doc: characterize the task first

These answers determine every later decision:

1. **Horizon** — single-turn, few-turn, or long (50+)? Long → invest early in WRITE + COMPRESS.
2. **Corpus size** — fits in context (maybe skip RAG) or not (SELECT/OFFLOAD)?
3. **Tool count** — few (<10, inline) or many (>20, retrieve)?
4. **State** — what must persist across turns/sessions? That's your memory/scratchpad schema.
5. **Failure cost** — high-stakes (favor selection, avoid lossy compression) or tolerant (compression fine)?
6. **Parallelizable?** — read-heavy + decomposable → consider ISOLATE; coupled decisions → single-threaded.

Output: a written spec of *what goes in context, from where, and when it's evicted.*

### Phase B — MVP0: smallest working loop, one context, no cleverness

One agent, one window. Tight system prompt at the right altitude. All tools inline (few). No RAG, no compression yet — run the loop and **watch the context grow.** Instrument token-count-per-turn and periodic full-context dumps. **You cannot engineer what you cannot see** — this is where most teams skip and then suffer.

### Phase C — MVP1: add management where MVP0 *observably* broke

- Overflowing on long runs → **COMPRESS** (summarize old history at a threshold) + **WRITE** (externalize plan/state).
- Wrong tool calls → **SELECT** for tools.
- Knowledge base too big to inline → **SELECT** (RAG) or **OFFLOAD** (fetch tools).
- Big noisy tool outputs → tool-boundary **distillation** (cheapest big win — do early).

### Phase D — MVP2: scale and harden

Introduce **ISOLATE** (sub-agents) only if a single context genuinely can't hold a focused view *and* the work is read-heavy + decomposable. Add cross-session memory if the product needs it. Make **eval + observability** first-class (Part 8) — at scale, regressions are invisible without it.

### The runtime loop (each turn, conceptually)

```
loop:
  1. ASSEMBLE:  system prompt
               + SELECTED tools (retrieve relevant subset)
               + SELECTED knowledge (RAG / memory fetch)
               + COMPRESSED history (summarize if over threshold)
               + working state (read relevant slice of scratchpad)
               + next instruction
  2. CALL model -> action (tool call or final answer)
  3. EXECUTE action
  4. DISTILL the tool result (drop noise at the boundary)
  5. WRITE durable bits to external store (plan updates, learned facts)
  6. EVICT: trim/summarize anything now stale
  7. repeat
```

Steps 1, 4, 6 are the heart. The model call is the easy part.

---

## 6 — The Must-Haves (non-negotiable checklist)

1. **Token-budget accounting** — per turn, per layer; set a budget per layer.
2. **System prompt at the right altitude** — clear sections (role, constraints, tool guidance, output format), minimal but complete; not brittle if-thens, not vague platitudes.
3. **Tool hygiene** — few, well-named, non-overlapping tools with crisp descriptions; retrieve a subset if many.
4. **Tool-output distillation at the boundary** — never let raw dumps flow in. Highest-ROI habit in the discipline.
5. **Eviction/compaction strategy** — a threshold (e.g., 70% of window) that triggers summarize-or-trim. Without it, every long task eventually dies.
6. **Externalized state (WRITE)** — scratchpad/plan/memory so the agent isn't relying on the window to remember the goal 80 turns later.
7. **Position discipline** — stable rules top, live instruction bottom, nothing critical in the middle.
8. **Observability** — trace every assembled context, every tool I/O, token counts. You debug agents by reading their contexts.

---

## 7 — The Trade-offs (what separates seniors from juniors)

| Decision | One way | Other way | The judgment |
|---|---|---|---|
| **Pre-load vs. offload** | Pre-load: fast, simple; risks bloat & rot | Offload: lean & accurate; more latency/turns/complexity | Big/unpredictable corpus → offload. Small/known → pre-load. |
| **Compress vs. select** | Compress: continuity, but lossy — may drop the key fact | Select: precise, but may miss needed context | High-stakes facts → select. Long chatty history → compress. |
| **Isolate vs. single** | Isolate: multiplies context, focus per agent | Single: coherent decisions, no conflicts | Read/research → isolate. Coupled writes → single-threaded. |
| **RAG recall vs. precision** | High recall (big k): nothing missed, noisy | High precision (small k): clean, may omit | Re-rank; measure both, don't guess. |
| **Rich vs. lean context** | Rich: better single-shot quality | Lean: cheaper, faster, less rot | The whole game: smallest context that's still complete. |
| **Static prompt vs. dynamic** | Static: simple, cacheable | Dynamic: adaptive, breaks caching, more code | Keep a stable cacheable prefix; vary only the tail. |
| **Summarize vs. keep raw** | Summarize: fits more, loses detail, adds a model call | Raw: lossless, grows unbounded | Summarize old turns, keep recent turns raw (sliding fidelity). |

Two bite hardest:

- **Compression is lossy and fails silently.** The summary looks fine; the dropped constraint causes a wrong action three turns later and you can't trace why. Mitigate: summarize-then-verify for critical state, or prefer selection.
- **Multi-agent coherence.** Isolation is seductive (fresh windows everywhere) but independent contexts contradict each other. Cognition's lesson: most apparent multi-agent needs are better served by one agent with good context management plus read-only parallel sub-tasks. Reach for true multi-agent last, not first.

---

## 8 — Evaluation & Observability (you cannot engineer blind)

Context engineering is empirical: you change a compaction threshold and *measure* whether task success moved. Instrument:

- **Per-turn token counts** by layer (system/tools/history/results/state).
- **Full context snapshots** per step — your primary debugging artifact. Most agent bugs are "the context was wrong," found by reading the context the model actually saw.
- **Tool I/O** — every call, args, raw vs. distilled result size.
- **Task metrics** — success rate, turns-to-completion, cost/task, latency.
- **Context-health** — did it re-ask for known info? pick a wrong tool? lose the goal?

Keep a small **eval set** of representative tasks; every strategy change runs against it, so you don't "fix the long-task bug, silently break the short path." Treat tracing (Langfuse/LangSmith) as load-bearing, not nice-to-have.

---

## 9 — Where It Sits in the Map

- **Prompt engineering** = crafting one instruction string. A *subset* — it's how you write the system-prompt and tool-description layers well.
- **RAG** = one *technique* inside SELECT. Context engineering decides *whether* RAG is even the right tool vs. offloading vs. long-context-plus-compression.
- **Context engineering** = the whole discipline of managing the information environment across a stateful, long-running system.

Vocabulary shifted from "prompt" to "context" because agents made the *string* the wrong unit. The right unit is *the dynamic system that assembles strings*.

---

## 10 — Concrete Walkthrough: a coding agent over a large repo

1. **Design doc:** long horizon, corpus ≫ window, many tools, high failure cost, partly parallelizable (reading).
2. **System prompt (right altitude):** role = senior engineer; rules = read-before-edit, run tests after; output = unified diffs. Stable → cacheable prefix.
3. **Tools:** `read_file`, `grep`, `glob`, `edit`, `run_tests` — few and sharp, inline all. (80 tools → retrieve.)
4. **OFFLOAD the repo:** no full index/pre-load; give `grep`/`glob`, fetch files by name just in time; paths are the navigation signal.
5. **WRITE the plan:** agent writes `plan.md`; each turn reads back only the current step. Survives long runs and truncation.
6. **DISTILL results:** a read returns the relevant function or line-range, not 3,000 lines; test output trimmed to failures.
7. **COMPRESS history:** at 70% window, summarize older turns ("explored auth, found token-refresh bug, wrote fix to X") while keeping the last few raw.
8. **ISOLATE — carefully:** read-only sub-agents search modules in parallel and return condensed findings; all *edits* stay single-threaded to avoid conflicts.
9. **EVAL/OBSERVE:** trace every context, measure success on a fixed task set, watch tokens-per-turn stay flat.

Each of the five/six strategies appears because a property of the *task* demanded it. That is context engineering.

---

## 11 — Design Checklist (pin above your desk)

- [ ] What is the **minimum** this step needs to decide correctly?
- [ ] What's in context that this step does **not** need? (evict)
- [ ] Anything **critical** buried in the middle? (move to top/bottom)
- [ ] Can large content be **offloaded** to a pointer + fetch tool?
- [ ] Can the **tool result be distilled** before it lands?
- [ ] Should old history be **compressed** now (over threshold)?
- [ ] Is durable state **written** outside the window?
- [ ] Are the **tools** for this step the right, minimal, non-overlapping set?
- [ ] Is my **stable prefix** intact so prompt caching still works?
- [ ] Am I **tracing** this so I can debug by reading the context later?

---

## 12 — Anti-Patterns

1. **"Just use a bigger model/window."** Doesn't fix rot; big windows degrade too. Curation still wins.
2. **Dumping raw tool output.** #1 token leak and noise source.
3. **Hoarding history.** No compaction → guaranteed eventual long-task failure.
4. **40 tools, all inline.** Confusion, wrong-tool calls. Retrieve a subset.
5. **Premature multi-agent.** Conflicting actions, coordination overhead. Single agent + good context first.
6. **Over-summarizing high-stakes state.** Silent loss of the one fact that mattered.
7. **No observability.** Flying blind; every bug a mystery.
8. **Brittle, overfit prompts.** Hardcoded edge-case logic that breaks on the next case.
9. **Breaking the cacheable prefix.** Reshuffling stable context every turn kills prompt caching and inflates cost/latency.

---

# 13 — Interview Questions: L4 (mid) and L5 (senior)

Framing: **L4 tests whether you understand the mechanisms and can implement them.** **L5 tests whether you can reason about trade-offs, design under constraints, and know when *not* to do the obvious thing.** Each has a model answer and the signal an interviewer listens for.

## L4 — Understanding & Implementation

**L4.1 — What is context engineering, and how is it different from prompt engineering?**
*Answer:* Prompt engineering crafts a single instruction string; context engineering manages the entire information environment (system prompt, tools, retrieved knowledge, history, tool results, state) across a multi-step task. The unit shifts from a string to a system that assembles strings on each stateless `f(context)` call. Prompt engineering is a *subset*.
*Signal:* Sees the LLM as stateless and context as the sole determinant of output. Red flag: treating it as "just better prompting."

**L4.2 — Why does adding more relevant context sometimes make an agent perform worse?**
*Answer:* Context rot — recall/usage of any token degrades non-linearly as the window fills. Plus lost-in-the-middle (poor attention to mid-context), distraction, and confusion. More tokens = more noise competing for attention, even when each token is individually relevant.
*Signal:* Names ≥1 specific failure mode; understands it's a *quality* gradient, not just a hard length limit.

**L4.3 — Name the core context-management strategies and give a technique for each.**
*Answer:* Write (scratchpad/memory/files), Select (RAG, tool-retrieval), Compress (summarize, trim, tool-result distillation), Isolate (sub-agents, sandboxing), Offload (pointers + fetch-on-demand).
*Signal:* Fluent with the taxonomy; gives a *concrete* technique per verb, not just labels.

**L4.4 — A tool returns a 15K-token JSON blob. What do you do?**
*Answer:* Distill at the tool boundary before it enters the window — parse and keep only the fields the model needs, or return a summary + a handle to fetch detail on demand. Never pass raw dumps through.
*Signal:* Instinct to filter at the boundary, not after. Highest-ROI habit; strong candidates reach for it immediately.

**L4.5 — Your agent's context overflows on long tasks. Two mechanisms to prevent it?**
*Answer:* (1) Compaction — at a threshold (e.g., 70% of window) summarize or trim older history, keeping recent turns raw. (2) Externalize state (Write) — persist plan/notes to a store and read back only the relevant slice each turn.
*Signal:* Knows compaction needs a *threshold*, keeping recent turns raw preserves fidelity, and externalization is the durable fix.

**L4.6 — When would you *not* use RAG?**
*Answer:* When the relevant corpus fits comfortably in context (just include it), or when the relevant slice is large/unpredictable — then offloading (search tools, fetch just-in-time) beats pre-retrieval. RAG is one technique within Select, not a default.
*Signal:* Doesn't treat RAG as automatic; can name the fits-in-context and offload alternatives.

**L4.7 — Why does information order in the window matter, and how do you use it?**
*Answer:* Lost-in-the-middle: models attend to start and end far better than the middle. Put stable high-priority rules near the top, the live instruction near the bottom, never bury critical info mid-context.
*Signal:* Actionable position discipline, not just awareness of the phenomenon.

**L4.8 — What are the three memory types and when do you use each?**
*Answer:* Episodic (past interactions/examples), semantic (facts about user/world), procedural (learned how-to). Fetch only what's relevant to the current task (memory selection).
*Signal:* Distinguishes the three; pairs memory with *selective retrieval*, not dumping all memory in.

**L4.9 — What's tool-result distillation and why is it high-ROI?**
*Answer:* Filtering/summarizing a tool's output at the boundary so only the needed signal enters context. High-ROI because tool results are usually the biggest, noisiest layer; trimming them at the source prevents both overflow and rot at once, and it's cheap (deterministic parsing, no model call).
*Signal:* Identifies tool results as the dominant token sink and treats the boundary as the right place to act.

**L4.10 — In RAG, what do chunk size and chunk overlap control, and what breaks at each extreme?**
*Answer:* Chunk size = how much text each embedding represents. Too large → the embedding is a blurry average of many topics, retrieval precision drops, and you inject lots of irrelevant tokens. Too small → each chunk lacks surrounding context, so a retrieved fragment is uninterpretable ("it increases 20%" — what does?). Overlap carries a few sentences across chunk boundaries so a fact split across a boundary isn't lost by either chunk. Typical starting point: a few hundred tokens per chunk with ~10–20% overlap, then tune against an eval set.
*Signal:* Understands both knobs affect retrieval *quality*, not just count; names the precision-vs-interpretability trade and treats the values as empirical, not fixed.

**L4.11 — What is a re-ranker and why add one after vector retrieval?**
*Answer:* Vector search retrieves a candidate set fast but coarsely (bi-encoder: query and docs embedded separately, compared by cosine — cheap but approximate). A re-ranker (cross-encoder) then scores each candidate *jointly with the query*, which is far more accurate but too slow to run over the whole corpus. Pattern: retrieve top-50 cheaply, re-rank to top-5 accurately, inject only those 5. It's how you get precision without sacrificing recall — cast a wide net, then filter hard.
*Signal:* Knows the two-stage retrieve-then-rerank pattern and *why* (bi- vs cross-encoder cost/accuracy trade). Strong candidates connect it directly to the recall-vs-precision tension.

**L4.12 — Semantic (vector) search vs. keyword (BM25) search — when does each win, and what's hybrid?**
*Answer:* Vector search matches *meaning* — good for paraphrase, synonyms, fuzzy intent. Keyword search matches *exact tokens* — better for rare terms, IDs, error codes, product names, acronyms where the exact string matters and embeddings blur it. Hybrid runs both and fuses the scores (e.g., reciprocal rank fusion), covering each other's blind spots. Default to hybrid for anything with a mix of prose and identifiers (codebases, docs with API names).
*Signal:* Doesn't treat vector search as strictly superior; knows exact-match cases where it fails; knows hybrid is usually the pragmatic default.

**L4.13 — Distinguish short-term (working) memory from long-term memory in an agent. Give an example of each.**
*Answer:* Short-term/working memory is the current task's scratchpad — this run's plan, intermediate results, recent turns; it lives in or near the window and is discarded when the task ends. Long-term memory persists across sessions — user preferences, learned facts, past-interaction summaries; it lives in an external store and is *selectively retrieved* into context when relevant. Example short-term: "step 3 of 5 done, output saved to /tmp/x." Example long-term: "this user always wants Terraform, not CloudFormation."
*Signal:* Separates within-task vs cross-session; pairs long-term memory with selective retrieval rather than always-loaded.

**L4.14 — How should you write tool descriptions, and why does it matter for context?**
*Answer:* Crisp, unambiguous, non-overlapping. Each description states exactly what the tool does, when to use it, and what it returns — because the schema *is* context the model reads to decide. Two tools with fuzzy or overlapping descriptions cause context confusion and wrong-tool calls. Prefer few sharp tools over many similar ones; if two tools are easily confused, merge or rename them. Bad: `search` and `query` and `find` that all do similar things. Good: `search_code_by_name`, `grep_file_contents` — distinct, self-explaining.
*Signal:* Treats tool schemas as context, not just plumbing; ties description quality to the confusion failure mode.

**L4.15 — What is "right altitude" for a system prompt? Give a too-low and too-high example.**
*Answer:* The Goldilocks level: specific enough to steer behavior, general enough not to overfit or bloat. Too low (over-specified): a brittle wall of hardcoded if-thens for every edge case — breaks on the next unseen case and wastes tokens. Too high (under-specified): "be a helpful engineer" — gives no real guidance. Right altitude: clear role, a handful of firm principles/constraints, output format, and tool-use guidance — enough that the model generalizes correctly without a rulebook.
*Signal:* Can articulate both failure directions, not just "be clear"; connects over-specification to brittleness and token cost.

## L5 — Trade-offs, Design & Judgment

**L5.1 — Choosing between summarizing history and selectively retrieving from it — how do you decide?**
*Answer:* Depends on failure cost and information shape. Summarization preserves continuity but is lossy and fails *silently* — it can drop the one constraint that matters, causing an untraceable wrong action later. Selection is precise but risks missing needed context (recall). High-stakes state (API contracts, decisions, constraints) → selection, or summarize-then-verify with a tuned prompt. Long, chatty, low-stakes history → summarization. In practice: sliding fidelity — raw recent turns, summarized older ones, durable facts pinned in state.
*Signal:* Names compression's silent-failure risk; ties the choice to failure cost; proposes a hybrid rather than dogmatically picking one.

**L5.2 — A teammate wants 5 parallel agents to speed up a complex task. Push back or endorse?**
*Answer:* Depends on coupling. Isolation gives each agent a fresh, focused window (multiplies effective context) — great for *read-heavy, decomposable* work like parallel research. But agents with independent contexts make *conflicting decisions* because they don't see each other's reasoning; reconciliation costs more than it saves for tightly-coupled *action*. Default: single-threaded agent with good context management + read-only parallel sub-tasks for breadth. Reach for true multi-agent last (Cognition's "Don't Build Multi-Agents").
*Signal:* Not seduced by parallelism; distinguishes read-parallelism from action-parallelism; knows the coherence cost. Bonus: cites the failure mode specifically.

**L5.3 — Design the context strategy for a coding agent over a 500K-file monorepo. Walk me through it.**
*Answer:* Characterize first: long horizon, corpus ≫ window, high failure cost, read-parallelizable. Then: (1) right-altitude system prompt (read-before-edit, run-tests-after, diff output) in a stable cacheable prefix; (2) few sharp tools inlined (`grep`/`glob`/`read`/`edit`/`run_tests`); (3) **offload** the repo — no full index, fetch by name just-in-time, paths as navigation signal; (4) **write** the plan to `plan.md`, read back only the current step; (5) **distill** file reads to relevant functions/line-ranges, test output to failures; (6) **compress** history at ~70% window keeping recent turns raw; (7) **isolate** read-only search sub-agents for breadth but keep all edits single-threaded; (8) trace contexts, hold tokens-per-turn flat under eval.
*Signal:* Starts from task characterization, not techniques. Chooses offload over indexing for a huge unpredictable corpus. Keeps edits single-threaded. Mentions caching and eval. Every choice justified by a task property.

**L5.4 — How do you know your context engineering is actually working? What do you measure?**
*Answer:* Tokens-per-turn staying roughly flat over long runs; task success rate and turns-to-completion on a fixed eval set; predictable cost/latency; context-health signals (re-asking for known info, wrong-tool rate, goal drift). Primary debugging artifact is the full context snapshot per step — most agent bugs are "the context was wrong," found by reading what the model actually saw. Every strategy change is validated against the eval set to avoid fixing long-task behavior while regressing the short path.
*Signal:* Treats it as empirical; has outcome *and* context-health metrics; debugs by reading raw contexts; guards against regressions.

**L5.5 — Prompt caching cuts cost/latency significantly. How does dynamic context assembly threaten it, and how do you keep both?**
*Answer:* Caching keys on a stable prefix; reshuffling the system prompt / tool defs / early context each turn invalidates the cache and you pay full price + latency every call. Keep stable high-value content (system prompt, tool schemas, durable instructions) as an unchanging prefix, and confine dynamic assembly (retrieved chunks, current instruction, fresh tool results) to the *tail*. Adaptivity where it matters, caching where it pays.
*Signal:* Understands caching interacts with context design; deliberately structures the window as stable-prefix + dynamic-tail. Few juniors reach this.

**L5.6 — When is aggressive compression dangerous, and how do you mitigate it?**
*Answer:* When compressed context carries load-bearing constraints or decisions — an API contract, a "must not do X" rule, a chosen approach. Summarization drops these silently; the wrong action surfaces turns later with no traceable cause. Mitigations: prefer *selection* for high-stakes facts; use a summarizer tuned to preserve decisions/constraints; summarize-then-verify against the original; pin critical facts in durable state (Write) so they're never subject to summarization.
*Signal:* Sees compression as a *risk surface*; separates "narrative you can lossily summarize" from "constraints you must preserve losslessly."

**L5.7 — Your agent nails demos but degrades on real long-running tasks. Diagnose systematically.**
*Answer:* First, look — pull full context snapshots at the point of degradation; the bug is almost always visible there. Then map symptom → fix: window filling (rot/overflow) → compaction + externalization; goal lost mid-run → it's buried mid-context or was summarized away, so pin it in state and keep it at the window tail; wrong tools late → tool-def bloat/confusion, retrieve a subset; acting on stale info → context clash from un-evicted old plans, add eviction. Validate each fix against a long-task eval set so you don't regress short ones.
*Signal:* Debugs by reading the context *first*, then maps observed symptom to a specific strategy. "Look before theorizing" is the L5 tell.

**L5.8 — Long-context models now offer 1M-token windows. Does that make context engineering obsolete?**
*Answer:* No. A bigger window raises the ceiling but doesn't fix rot, lost-in-the-middle, distraction, or clash — quality still degrades with length, and cost/latency scale with tokens. Bigger windows change *where* you spend effort (less on hard overflow, more on curation and ordering) but the core discipline — minimal, high-signal, coherent context per step — is unchanged. If anything, more room to fill makes disciplined curation *more* valuable, not less.
*Signal:* Rejects the "bigger window solves it" framing with specific mechanisms; understands cost/latency and quality both still favor curation.

**L5.9 — Retrieved documents and tool outputs can carry prompt-injection attacks. How does context engineering both create and mitigate this risk?**
*Answer:* Every byte you inject — a retrieved web page, a tool's JSON, a file's contents — is untrusted text the model may treat as instructions. Selection and offload *expand* the attack surface: you're pulling in third-party content at runtime. Mitigations are context-design decisions: (1) structurally separate untrusted content from instructions (clear delimiters/roles so the model knows retrieved text is *data*, not commands); (2) never let retrieved content silently redefine the system prompt — keep the trusted instruction layer stable and privileged; (3) distill/sanitize tool output at the boundary, which also strips injected instructions; (4) constrain what tools the agent can *act* with, so even a successful injection has limited blast radius; (5) for high-stakes actions, require confirmation rather than letting retrieved text trigger them. Treat it as a trust-boundary problem, not just a phrasing problem.
*Signal:* Recognizes retrieved/tool content as untrusted input, connects it to the Select/Offload strategies, and proposes structural (not just prompt-wording) defenses plus blast-radius limiting. This is a security-minded L5 answer.

**L5.10 — Design a long-term memory system for an assistant used daily over months. What's the architecture and the hard part?**
*Answer:* Architecture: (1) a *write path* that extracts durable facts from conversations (preferences, decisions, recurring context) and stores them — typed by episodic/semantic/procedural — in a store with embeddings + metadata; (2) a *read path* that, per turn, selectively retrieves only memories relevant to the current task and injects a small slice; (3) a *maintenance path* that dedupes, resolves contradictions (new fact supersedes old), decays/evicts stale memories, and consolidates many episodic entries into semantic summaries. The hard part is *what to write and what to forget* — write too much and retrieval gets noisy and memories contradict each other; write too little and the assistant feels amnesiac. Contradiction resolution (the user changed their mind) and staleness (a fact that was true in March) are where naive systems break. Retention needs a policy — recency, frequency of use, and explicit importance — not "keep everything."
*Signal:* Separates write/read/maintenance paths; identifies forgetting and contradiction-resolution as the real problems, not storage; treats retention as a designed policy. Weak answers just say "store embeddings and retrieve."

**L5.11 — A sub-agent returns a summary that later turns out to have omitted a critical detail the lead agent needed. How do you design around lossy hand-offs?**
*Answer:* This is the isolation-coherence tax in concrete form. Options, in rough order: (1) have sub-agents return *structured* results (findings + source pointers) rather than free-text summaries, so the lead can fetch detail on demand rather than trusting a lossy digest; (2) make the summarization contract explicit — tell the sub-agent exactly what fields the lead needs preserved (a tuned summarizer, as Cognition does at hand-off boundaries); (3) for critical paths, pass source handles alongside the summary so nothing is unrecoverable; (4) if omissions keep biting, that's a signal the task wasn't safely decomposable — collapse to a single context. The meta-point: hand-off is where multi-agent systems lose information, so design the hand-off payload as carefully as an API contract.
*Signal:* Frames hand-off loss as the core multi-agent risk; reaches for structured returns + source pointers over free-text; knows when the right answer is "don't decompose."

**L5.12 — Your agent is correct but too slow and expensive per task. Walk through optimizing without hurting quality.**
*Answer:* Profile first — token counts per layer per turn tell you where the spend is. Then, roughly: (1) protect the cacheable prefix so the stable system prompt + tool schemas are cached, not re-billed each turn (often the biggest easy win on both cost and latency); (2) distill tool outputs harder — they're usually the largest layer; (3) compress/trim history sooner so per-turn tokens stay flat; (4) retrieve fewer, better chunks (re-ranking lets you drop k without losing recall); (5) route — use a smaller/faster model for easy sub-steps (classification, summarization) and reserve the big model for reasoning; (6) reduce round-trips where offload added latency, by pre-loading the reliably-needed core. Each change gets validated against the eval set so a cost cut doesn't silently drop success rate.
*Signal:* Measures before cutting; knows prompt caching and tool-distillation are the high-leverage levers; considers model routing; guards quality with evals. Distinguishes token-cost from round-trip latency.

**L5.13 — When do you stop context-engineering and reach for fine-tuning instead?**
*Answer:* Context engineering is the default — it's faster to iterate, cheaper, and doesn't freeze behavior. You consider fine-tuning when: (1) you need a *behavior or format* that's stable across all inputs and expensive to re-specify in every prompt (fine-tune it in, reclaim the tokens); (2) you're spending huge context on few-shot examples that a tuned model could internalize; (3) latency/cost from a bloated prompt is the bottleneck and the behavior is stable enough to bake in; (4) you need a specialized capability (e.g., Cognition's fine-tuned summarizer for hand-offs). You *don't* fine-tune for knowledge that changes (use retrieval — fine-tuning bakes in a stale snapshot) or when you're still iterating on behavior. Rule of thumb: retrieval for knowledge, context engineering for behavior you're still shaping, fine-tuning for behavior that's settled and token-expensive to keep re-specifying.
*Signal:* Treats fine-tuning as a later, narrower tool; correctly assigns *changing knowledge* to retrieval and *stable behavior* to fine-tuning; doesn't reach for it prematurely.

**L5.14 — How do you evaluate RAG quality specifically, separate from overall task success?**
*Answer:* Decompose it into retrieval and generation. Retrieval metrics: does the retrieved set *contain* the needed evidence (recall/hit-rate) and how much noise came with it (precision), measured against a labeled set of query→relevant-doc pairs. Generation metrics: given good context, is the answer faithful (grounded in the retrieved text, not hallucinated) and relevant to the question. The reason to separate them: if end-to-end accuracy is low, you need to know *which stage* failed — bad retrieval (fix chunking/re-ranking/hybrid) vs. bad generation despite good context (fix the prompt or model). Measuring only end-to-end tells you it's broken but not where.
*Signal:* Splits retrieval from generation; names faithfulness/groundedness; frames it as *localizing* the failure. Weak answers only mention final accuracy.

**L5.15 — Two sources in context disagree (a stale cached fact vs. a fresh tool result). How do you prevent and resolve context clash?**
*Answer:* Prevent: aggressive eviction — when a fresh result supersedes an old one, *remove* the stale version rather than letting both sit in context; version/timestamp facts so freshness is explicit. Resolve when it happens: make precedence a rule the model can apply (e.g., "tool results outrank cached context; newer outranks older") and surface the timestamp/source in the injected text so the model has the basis to choose. Structurally, prefer a single source of truth for any given fact — pin it in state and read from there — rather than letting the same fact enter context from multiple paths. Clash is usually a symptom of missing eviction, so fix the eviction step.
*Signal:* Treats clash as primarily an eviction/single-source-of-truth problem, not just a prompt instruction; makes precedence explicit and machine-applicable.

**L5.16 — You're multi-tenant: many users share one agent service. What context-isolation risks appear and how do you handle them?**
*Answer:* The core risk is context bleed — one tenant's data (memory, cached retrieval, scratchpad) leaking into another's context, which is both a correctness and a privacy/security failure. Handle it by scoping every context source per-tenant: retrieval and memory stores partitioned and filtered by tenant ID on every query; no shared scratchpad/state across tenants; cache keys namespaced by tenant so prompt caching never serves one tenant's prefix to another. Be especially careful with "global" memory or shared example stores — they must contain only non-tenant-specific content. Test it explicitly: an eval that checks tenant A's identifiers never appear in tenant B's assembled context.
*Signal:* Sees isolation as a data-boundary/privacy problem across every context layer (retrieval, memory, cache, state); proposes per-tenant scoping and an explicit leak test. This is a systems-and-security L5 answer.

---

## References

Priority order: primary engineering writeups and runnable code first.

**Primary essays (read these):**
- Anthropic — *Effective context engineering for AI agents*: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- LangChain — *Context Engineering for Agents* (Write/Select/Compress/Isolate): https://blog.langchain.com/context-engineering-for-agents/
- Cognition — *Don't Build Multi-Agents* (isolation vs. coherence): https://cognition.ai/blog/dont-build-multi-agents
- Anthropic — *How we built our multi-agent research system*: https://www.anthropic.com/engineering/built-multi-agent-research-system
- Drew Breunig — *How Long Contexts Fail* / *How to Fix Your Context*: https://www.dbreunig.com/2025/06/22/how-contexts-fail-and-how-to-fix-them.html

**Code to pull, run, modify:**
- LangGraph (state = context-management substrate): https://github.com/langchain-ai/langgraph
- LlamaIndex (RAG/retrieval = SELECT in code): https://github.com/run-llama/llama_index
- Pydantic AI (typed agents, clean tool/state separation): https://github.com/pydantic/pydantic-ai
- HuggingFace `smolagents` (CodeAgent = ISOLATE via sandbox): https://github.com/huggingface/smolagents
- Anthropic Cookbook (agent + tool-use + memory patterns): https://github.com/anthropics/anthropic-cookbook

**Observability / eval:**
- Langfuse (open-source LLM tracing + eval): https://github.com/langfuse/langfuse

**Background (skim, optional):**
- *Lost in the Middle* (Liu et al.): https://arxiv.org/abs/2307.03172
- Chip Huyen — *AI Engineering* (book; RAG, agents, context chapters).
