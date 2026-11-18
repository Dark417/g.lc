# 9itv-bank — Agentic AI Interview Question Bank

> 30 common agentic AI interview questions, each with a plain line, an L4 answer, and an L5 extra.
> Starred questions (★) are ones I missed before: Q12 (guarding an LLM), Q18–Q19 (evals and false positives for the email reconciliation agent).
> Group 9 (interview). Concept docs: [1harness](1harness.md), [4guardrails](4guardrails.md), [4evals](4evals.md), [1architecture](1architecture.md). Last updated: 2026-11-16.

## Index
- [A. Agent basics (Q1–Q6)](#a-agent-basics)
- [B. Context, memory, RAG (Q7–Q11)](#b-context-memory-rag)
- [C. Guardrails and security (Q12–Q16)](#c-guardrails-and-security)
- [D. Evals (Q17–Q22)](#d-evals)
- [E. Production (Q23–Q28)](#e-production)
- [F. Experience and judgment (Q29–Q30)](#f-experience-and-judgment)
- [Where this fits](#where-this-fits)
- [References](#references)

---

## A. Agent basics
Docs: [1harness](1harness.md), [1loop](1loop.md), [1orchestration](1orchestration.md), [1aa-msg](1aa-msg.md).

### Q1 What's the difference between an agent and a workflow?

**Intuitive:** in a workflow, my code picks the next step; in an agent, the model picks it.

**L4 answer**
- A workflow is fixed steps in code, with LLM calls inside some of them.
- An agent is a model in a loop with tools; it decides which tool to call next based on results.
- Workflows are cheaper, predictable and testable; agents handle cases you can't script.
- I default to a workflow and add an agent loop only where the path truly can't be known.

**L5 extra**
- Real systems mix them: a graph of fixed stages with a small agent loop inside one fuzzy node.
- Name the ladder: single call, workflow, single agent, graph with loops, multi-agent; justify each step up.
- Agents trade predictability for coverage: variable steps, cost and latency per run.
- The deciding variable: can I write the steps down in advance?
- Evidence: Anthropic's guidance says to start with the simplest pattern that works.

### Q2 When should you not use an agent?

**Intuitive:** when plain code or one model call already does the job.

**L4 answer**
- When the steps are known: write a workflow.
- When it's high-volume, simple and latency-sensitive: classification or extraction with one call.
- When a wrong action can't be undone and there's no human checkpoint.
- When you can't measure quality yet: no evals, no agent.

**L5 extra**
- Cost of an agent = tokens × steps, and steps vary per run; budget forecasts get hard.
- Regulated flows need audit trails of why each step happened; fixed code explains itself better.
- A deterministic rule engine beats an agent where rules are known (e.g. reconciliation tolerances).
- Use the model where the input is messy (free text, emails, PDFs), and code where the decision is a rule.

### Q3 What stops an agent loop from running forever?

**Intuitive:** every loop needs a done signal and a ceiling.

**L4 answer**
- Done signal: the model gives a final answer or calls a finish tool.
- Ceilings in code: max steps, max tokens or spend, a wall-clock deadline.
- Repeated-failure detection: same tool with the same arguments N times means stop.
- I log the stop reason on every run.

**L5 extra**
- The model's "done" is a prompt-level request; the limits are code-level guarantees.
- On a ceiling hit, return a partial result with the reason, or escalate to a human.
- Set step budgets from eval runs, not guesses.
- Alert on the stop-reason mix: a rise in "hit step limit" signals drift after a prompt change.
- A verifier (a grader inside the loop) can also end the run when output passes.

### Q4 Single agent or multi-agent?

**Intuitive:** one agent until its context or toolset can't hold the job.

**L4 answer**
- Split for context isolation, parallel independent work, or different permissions per part.
- Don't split coupled tasks: agents with separate contexts make conflicting choices.
- Multi-agent costs more: Anthropic reported about 15× the tokens of a chat for its research system.
- Common patterns: supervisor with workers, handoff, agent as a tool.

**L5 extra**
- Handoff gives control away; agent-as-tool lends it and gets the result back.
- Sub-agents should return compressed summaries or structured records, not transcripts.
- Consistency is a distributed-systems problem: idempotent actions, a ledger of steps, leases and retries.
- Anthropic's multi-agent research setup beat a single agent on an internal eval; coding tasks often go the other way (Cognition's argument).
- Across teams or vendors, use A2A; inside one runtime, share state.

### Q5 How does tool calling work?

**Intuitive:** the model asks, the harness acts.

**L4 answer**
- The harness sends tool definitions (name, description, argument schema) with every model request.
- The model replies with a structured tool call: a name and arguments. It executes nothing.
- The harness validates arguments, checks permission, runs the tool, and returns the result.
- The loop continues until a final answer.

**L5 extra**
- Tool descriptions are prompts; vague or overlapping tools cause wrong choices.
- Enums and strict schemas stop invented values; validation errors go back to the model so it can fix them.
- Write tools take an idempotency key; retries must not double-charge.
- Every tool call needs a matching result before the next request, or providers reject it.
- With many tools, send a relevant subset or use tool search to save tokens.

### Q6 MCP vs function calling vs A2A?

**Intuitive:** function calling is how the model asks; MCP is how tools are packaged; A2A is how agents talk to agents.

**L4 answer**
- Function calling: tool schemas in the model request; the model returns a structured call.
- MCP: a standard protocol (JSON-RPC) so one tool server works with any agent.
- A2A: tasks between agents with a lifecycle (working, input-required, completed).
- I use in-process tools when I own both sides, MCP for shared tools, A2A for someone else's agent.

**L5 extra**
- MCP covers tools, resources and prompts; transports are stdio for local and streamable HTTP for remote.
- MCP authorization uses OAuth with audience-bound tokens; never pass the user's token through.
- MCP tool lists cost tokens; filter per agent.
- A2A agents publish an agent card (skills, endpoint, auth) for discovery.
- Between my own services I'd still use gRPC; A2A earns its cost at ownership boundaries.

---

## B. Context, memory, RAG
Docs: [2context](2context-engineering-handbook.md), [1architecture §5](1architecture.md), [3rag](3rag-reference-handbook.md), [2prompt](2prompt.md).

### Q7 What is context engineering?

**Intuitive:** deciding what the model sees on each call, since it sees nothing else.

**L4 answer**
- The model is stateless; each request carries instructions, tools, history, retrieved text and the new message.
- Context engineering picks, orders and trims that content.
- Too little: the model lacks facts. Too much: cost rises and quality drops ("context rot").
- Stable content goes first for prompt caching; volatile content last.

**L5 extra**
- Techniques: summarize old turns, prune tool results to pointers, retrieve just in time, sub-agents for isolation.
- Long windows aren't usable windows; test quality at real lengths.
- Measure tokens per turn and quality late in long runs.
- Context is also an attack surface: untrusted text in context can carry injected instructions.

### Q8 What kinds of memory does an agent have?

**Intuitive:** short-term is this conversation; long-term is what survives across conversations.

**L4 answer**
- Run state: where one execution is now.
- Session: one conversation's history, loaded by session ID.
- Long-term memory: facts across sessions, like preferences, stored per user.
- All of it lives in external stores, so the harness stays stateless.

**L5 extra**
- Checkpoints snapshot run state per step so runs resume after crashes or approvals.
- Long-term memory needs extraction rules, namespaces per user, TTLs and a delete path.
- Memory can be poisoned; control what gets written.
- One writer per session (lock or queue) prevents corrupted history.
- Frameworks: ADK session and memory services, LangGraph checkpointer and store.

### Q9 Walk me through a RAG pipeline and where it fails.

**Intuitive:** find the right passages, then answer only from them.

**L4 answer**
- Ingest: parse, chunk, embed, index with metadata.
- Query: rewrite, retrieve (vector plus keyword), rerank, put top chunks in context.
- Generate with citations; check that claims are supported.
- Failures: bad chunking, retrieval misses, stale index, the model ignoring the context.

**L5 extra**
- Evaluate retrieval separately (recall at k) from generation (groundedness); a bad retriever caps everything.
- Hybrid search fixes exact terms (IDs, product codes) that embeddings miss.
- Permission filters go in the query, not the prompt.
- Freshness: incremental re-indexing and deletes.
- Agentic RAG: retrieval as a tool the agent calls when needed.

### Q10 How do you reduce hallucination?

**Intuitive:** give it the facts, and check its claims against them.

**L4 answer**
- Ground answers in retrieved or tool data; require citations.
- Tell it to say "I don't know"; give it an escalation path.
- Check outputs: every number or ID must match a tool result.
- Use structured output for fields that downstream code reads.

**L5 extra**
- Grounding checks can be code (match values) or a judge model (claim support).
- Lower-temperature settings don't fix missing knowledge.
- Measure hallucination rate on an eval set with known answers.
- In regulated domains, never let the model invent amounts; compute them in code.

### Q11 How do you get reliable structured output?

**Intuitive:** don't just ask for JSON; enforce the schema and validate.

**L4 answer**
- Four levels: ask nicely, JSON mode, schema-enforced decoding, schema plus validation plus retry.
- Providers support strict schemas for outputs and tool arguments.
- Validate with a schema library; on failure, send the error back once and retry.
- Keep schemas flat and use enums.

**L5 extra**
- Schema-enforced decoding has limits (some constraints and recursive schemas unsupported); check provider docs.
- Validity isn't correctness: a valid JSON can hold a wrong amount.
- Version schemas; downstream consumers break on changes.

---

## C. Guardrails and security
Docs: [4guardrails](4guardrails.md), [4access](4access.md), [4security](4security.md).

### Q12 ★ How do you guard an LLM?

**Intuitive:** checks at every door the model touches, in code, plus limits on what it's allowed to do at all.

**30-second spoken answer**
- "I guard it in layers, and I don't rely on the system prompt."
- "First, limit what it can do: least-privilege tools, user-scoped credentials, approval for irreversible actions."
- "Second, check at five points: user input, untrusted content entering context, every tool call, tool results, and the final output."
- "Third, measure it: a red-team eval set in CI and monitoring of block rates in production."

**L4 answer**
- Input: PII masking, injection and jailbreak detection, topic limits, rate limits.
- Tool calls: allowlist per agent, argument limits (amounts), permission as the user, approval when risky.
- Output: grounding check, PII and secret scan, policy and schema checks.
- Rules live in code or a policy engine; the prompt only asks.

**L5 extra**
- Checkpoints 3 and 4 (tool calls and tool results) are the agent-specific ones; chatbot guardrails stop at input and output.
- Indirect injection is the big risk: instructions planted in emails, web pages or documents the agent reads. Tag untrusted content and tighten writes after reading it.
- Prompt injection has no complete fix, so limit blast radius: an agent with private data, untrusted input and an outbound channel can leak (Simon Willison's "lethal trifecta").
- Cost and latency: deterministic checks everywhere (milliseconds); model-based classifiers at the edges; LLM judges only for high-stakes outputs.
- High-risk paths fail closed if a checker is down.
- Banking specifics: PII redaction before logs, provider zero-retention terms, data residency, append-only audit with who approved what.
- Tools: Bedrock Guardrails, Google Model Armor, NeMo Guardrails, Guardrails AI, framework hooks. Check each framework's gaps (e.g. some run input guardrails only on the first agent).

### Q13 What's prompt injection, and how do you defend against indirect injection?

**Intuitive:** text the model reads that tries to give it orders.

**L4 answer**
- Direct: the user types "ignore your instructions".
- Indirect: the instruction hides in content the agent reads, like an email or web page.
- Defenses: tag sources, treat tool results as data, scan for instructions, restrict follow-up actions.
- Approval for outbound or irreversible actions.

**L5 extra**
- Classifiers miss new phrasing; detection is one layer only.
- Break the trifecta: separate private data from untrusted content, or remove outbound channels.
- Test with an injection case set in evals.
- Watch for "untrusted read followed by write" patterns in traces.

### Q14 How do you handle PII in an LLM system at a bank?

**Intuitive:** send the model only what it needs, and keep sensitive data out of logs.

**L4 answer**
- Mask or tokenize PII before the model call where the task allows.
- Use providers or cloud hubs with zero-retention and residency terms.
- Redact traces and logs; restrict who can read them.
- Retention per store and a delete path.

**L5 extra**
- Hidden copies: traces, eval sets, caches, long-term memory, vector indexes.
- Detokenize only in the tool layer when an action needs the real value.
- Per-tenant encryption keys for strict cases.
- Audit who viewed transcripts.

### Q15 How do you design human-in-the-loop approval?

**Intuitive:** pause the run, ask a structured question, resume on the answer.

**L4 answer**
- Decide by blast radius and reversibility: reads auto, reversible writes logged, irreversible writes approved.
- The harness saves state, emits an approval request with options, and holds no thread.
- The answer comes back with the run ID; the run resumes down that branch.
- Requests have an expiry and an owner.

**L5 extra**
- Check the approver's rights when the answer arrives; the requester can't approve their own action.
- Store paused state server side; state round-tripped through the client can be tampered with.
- Re-validate on resume: an approval for $200 doesn't cover $900.
- Approval fatigue: too many prompts train people to click yes; gate only the risky tail.

### Q16 What is the confused-deputy problem with agents?

**Intuitive:** the agent uses its own broad rights to do something the user isn't allowed to do.

**L4 answer**
- Happens when tools run under a shared service account.
- Fix: on-behalf-of tokens, scoped to this user and this tool.
- The tenant ID comes from the token, never from model-written arguments.
- Least privilege per agent.

**L5 extra**
- For MCP: audience-bound tokens; no token passthrough.
- Data-level filters in queries enforce tenancy.
- Audit tool calls with the acting identity.
- Test cross-tenant cases in evals.

---

## D. Evals
Docs: [4evals](4evals.md), [4observability](4observability.md).

### Q17 How do you evaluate an agent?

**Intuitive:** run it on realistic cases, score the results and key steps, and repeat on every change.

**L4 answer**
- Build a set of real cases with expected outcomes.
- Grade the outcome (final state and answer) and key steps (right tool, right arguments).
- Use code checks first, an LLM judge for nuance, humans to calibrate.
- Run it as a gate in CI and sample production.

**L5 extra**
- End to end decides whether to ship; step-level evals find why it failed.
- Several trials per case: passing once (capability) differs from passing every time (reliability).
- Track cost, steps and latency beside quality.
- Every production failure becomes a new case.

### Q18 ★ How would you evaluate your email reconciliation agent?

**Intuitive:** it's a classifier with money on the line, so measure it with labeled cases and a confusion matrix, not vibes.

**30-second spoken answer**
- "I treat it as matching emails to ledger entries: matched, partial, or exception."
- "I build a labeled set from historical cases that ops already resolved, so I have ground truth."
- "I measure each stage separately: field extraction, candidate retrieval, the match decision."
- "I report precision and recall per case type, with false positives weighted higher because a wrong auto-match hides a real break."

**L4 answer**
- Define labels and costs first: a false positive (auto-matched but wrong) is worse than a false negative (sent to a human but actually fine).
- Golden set from history: emails plus the final human resolution as the label.
- Stratify cases: exact match, partial payments, currency, date offsets, duplicates, missing references, attachments.
- Metrics: confusion matrix, precision and recall per stratum, auto-match rate, human review rate.

**L5 extra**
- Stage evals
  - Extraction: field-level accuracy for amount, date, counterparty, reference.
  - Retrieval: did the true ledger entry appear in the candidate list (recall at k)?
  - Decision: was the match correct given the candidates?
- This locates errors: most "wrong matches" are often extraction or retrieval misses, not reasoning.
- Ground truth exists here, so use exact checks, not an LLM judge.
- Repeat each case a few times to catch non-determinism; reliability matters more than one lucky pass.
- Online: sample auto-matched items for human review to estimate the live false-positive rate; every human-corrected exception becomes a labeled false negative.
- Gate: no release if precision on auto-matches drops below the target, whatever recall does.

### Q19 ★ How do you reduce false positives and false negatives?

**Intuitive:** let code verify what the model claims, and send unsure cases to a human instead of guessing.

**L4 answer**
- Split the job: the model extracts fields from messy emails; code applies the matching rules and tolerances.
- Add a confidence band: auto-match only above a threshold, auto-reject below one, humans in between.
- Tune the threshold on a precision-recall curve using the cost of each error.
- Fix the biggest error bucket first, found from the confusion matrix by stratum.

**L5 extra**
- Cutting false positives (wrong auto-matches)
  - Deterministic re-check: recompute amounts and dates against the ledger in code.
  - Require evidence: the model must quote the email text that supports each field.
  - Two independent signals must agree (e.g. reference number and amount) before auto-matching.
  - Schema and range validation on every extracted field.
- Cutting false negatives (good matches sent to humans)
  - Better candidate retrieval: wider date windows, fuzzy reference matching, normalized counterparty names.
  - Handle formats: attachments, tables, forwarded threads, multiple payments in one email.
  - Few-shot examples of hard cases in the prompt; a stronger model only for low-confidence items.
- The trade-off is real: you can't drive both to zero; pick the operating point by cost, e.g. "precision 99%+ on auto-matches, accept more human review."
- Monitor drift: new counterparties or email formats show up as a rising exception rate.

### Q20 What are the pitfalls of LLM-as-judge?

**Intuitive:** the judge is also a model, so it can be wrong in predictable ways.

**L4 answer**
- Biases: position, length, self-preference.
- Drift when the judge model changes.
- Calibrate against human labels; write a clear rubric.
- Prefer code checks whenever ground truth exists.

**L5 extra**
- Measure judge agreement with humans (e.g. Cohen's kappa) before trusting it.
- Pin the judge model version.
- Use a different, stronger model than the one being judged.
- Judges can be fooled by the same injections as the agent.

### Q21 How do you stop a prompt change from breaking production?

**Intuitive:** treat prompts like code: version, review, gate, roll out slowly.

**L4 answer**
- Prompts, models, tool schemas and policies are versioned and released as a bundle.
- Every change runs the eval gate in CI.
- Canary to a small share of traffic; compare quality, cost and latency.
- Roll back by switching to the previous bundle.

**L5 extra**
- Stamp the bundle version on every trace.
- Shadow runs for risky changes, with write tools in dry-run mode.
- Pin model versions; an alias that moves silently is an unreviewed deploy.
- Kill switches per agent and per tool.

### Q22 How is an eval different from a termination condition or a guardrail?

**Intuitive:** termination stops one run, a guardrail blocks live traffic, an eval measures many runs afterwards.

**L4 answer**
- Termination: a runtime decision for the current run (limits, done signal).
- Guardrail: a real-time check that blocks or redacts live inputs, actions and outputs.
- Eval: offline or sampled measurement deciding whether the system is good enough to ship.
- They meet at the verifier: a small eval inside the loop that can end a run.

**L5 extra**
- A guardrail's block rate and false positives are themselves evaluated.
- Online scoring feeds the eval set; it doesn't stop runs.

---

## E. Production
Docs: [4observability](4observability.md), [6cost-latency](6cost-latency.md), [1architecture §6–7](1architecture.md), [6durable](6durable.md), [6llmops](6llmops.md).

### Q23 An agent gave a wrong answer in production. How do you debug it?

**Intuitive:** open the trace, find the first wrong step, read what the model saw.

**L4 answer**
- Find the run by session or run ID; open the trace.
- Find the first wrong span; later steps are usually fallout.
- Check the context at that step: instructions, retrieved text, tool results.
- Fix the cause, then add the case to the eval set.

**L5 extra**
- Common causes: unclear tool description, retrieval miss, context bloat, rule only in the prompt, tool error ignored.
- Replay with recorded tool outputs so side effects don't repeat.
- Compare version stamps when "it worked yesterday".
- One trace ID across queues and approval pauses.

### Q24 How do you cut an agent's cost?

**Intuitive:** fewer steps, smaller models where they pass, and cache the stable prompt.

**L4 answer**
- Move known paths into workflows to cut steps.
- Order prompts so the stable prefix is cached.
- Route easy steps to smaller models after evals confirm quality.
- Trim history and cap tool results.

**L5 extra**
- Loop cost grows faster than linearly because each step resends history.
- Batch APIs (about half price) for offline work like evals.
- Per-run budgets and per-tenant quotas; cost attribution on every call.
- Gate every cost change on the eval set.

### Q25 How do you reduce latency?

**Intuitive:** stream for perceived speed, parallelize for real speed, cut steps for both.

**L4 answer**
- Stream tokens and progress events.
- Run independent tool calls in parallel.
- Use faster models for easy steps.
- Cache tool and retrieval results.

**L5 extra**
- Prompt caching also lowers time to first token.
- Long work becomes a job with a run ID and notifications.
- Watch tail latency per span to find slow tools.

### Q26 How do you scale an agent service to many users?

**Intuitive:** stateless harness, external state, and quotas on tokens, which run out before servers do.

**L4 answer**
- Stateless harness instances behind a load balancer; state loaded by session ID.
- Autoscale on active runs, not CPU.
- One run per session at a time; many sessions in parallel.
- A model gateway with fallback providers and per-tenant quotas.

**L5 extra**
- Back-of-envelope: users to runs per second to concurrent runs to tokens per minute.
- In typical numbers, connections are cheap and tokens per minute are the bottleneck.
- Queue with backpressure; shed low-priority work.
- Dedicated harness service behind the BFF, so agent and API scale separately.

### Q27 How do you handle long-running or interrupted runs?

**Intuitive:** make it a job: queued, checkpointed, resumable, idempotent.

**L4 answer**
- Return a run ID; workers execute from a queue.
- Save state after each step (checkpoints).
- Waits for humans or events are stored, not sleeping threads.
- Side effects carry idempotency keys.

**L5 extra**
- A resumed graph node restarts from its start; it must be safe to repeat.
- Workflow engines (Temporal, Step Functions) record step results and replay.
- Model calls are recorded activities so a crash doesn't re-bill or re-act.
- Timeouts and escalation on every wait.

### Q28 How do you handle model upgrades?

**Intuitive:** a model version is a dependency; upgrade it through the same gate as code.

**L4 answer**
- Pin exact versions.
- Run the eval gate on the new model; compare cost and latency.
- Canary before full rollout.
- Track provider deprecation dates.

**L5 extra**
- Prompts are model-specific; expect to adjust them.
- Keep the old version deployable for rollback.

---

## F. Experience and judgment
Docs: [5frameworks](5frameworks.md), [5adk](5adk.md).

### Q29 Tell me about an agent you built and one trade-off you made.

**Intuitive:** one system, one hard decision, one number.

**L4 answer (shape, fill with my reconciliation agent)**
- Problem: matching payment emails to ledger entries took ops hours a day.
- Design: the model extracts fields; code matches with tolerances; low-confidence items go to a human queue.
- Trade-off: chose precision over automation rate, because a wrong auto-match hides a real break.
- Result: state measured numbers only (auto-match rate, precision on the golden set).

**L5 extra**
- Show the eval set and how the threshold was chosen.
- Say what failed first and how traces found it.
- Say what I'd change next (retrieval of candidates, drift monitoring).
- Don't claim numbers I can't defend in a follow-up.

### Q30 Why that framework? Would you build your own loop?

**Intuitive:** pick by control flow and hosting; make sure you could rewrite the loop yourself.

**L4 answer**
- Graph runtime (LangGraph, ADK workflows) for known stages with approvals and resumable runs.
- Model-driven SDK (Claude Agent SDK, OpenAI Agents SDK, Strands) for open-ended tasks.
- Cloud fit: ADK with Google's Agent Runtime; Strands with AWS AgentCore.
- A plain loop is fine to start; adopt a framework for checkpoints, streaming and tracing.

**L5 extra**
- Every "has sessions" claim needs checking: where is it stored, who locks it, what happens at scale.
- Frameworks change fast; pin versions and keep a thin interface around them.
- What I always own: edge, auth, tenant isolation, evals, cost budgets.

---

## Where this fits
- **Place:** L9 of [1a-bp.md](../1a-bp.md); the interview layer over groups 1–7.
- **Time it deserves:** tonight, 20 minutes on Q12, Q18, Q19 and the A group; the rest as a skim.
- **I should be able to…**
  - Say the Q12 and Q18 spoken answers from memory.
  - Explain false positive vs false negative for my own agent, and which one I'd trade.
  - Answer any A-group question in under a minute.

## References
1. [Anthropic — Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) — workflows vs agents.
2. [Anthropic — Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) — graders, trials, outcome vs transcript.
3. [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/) — injection, excessive agency.
4. [Simon Willison — the lethal trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/) — why agents leak.
