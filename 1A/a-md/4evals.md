# 4evals — Evaluating Agents

> How to measure whether a harness does its job: end to end and step by step, offline and in production, and where evals sit next to tests, guardrails and stop conditions.
> Group 4 (quality and safety). Related: [4observability.md](4observability.md), [4guardrails.md](4guardrails.md), [1loop.md](1loop.md) §3.1.
> Concept level, no code (AGENTS.md §8b). Last updated: 2026-11-16.

## Index
- [0. One-minute version](#0-one-minute-version)
- [1. Concept: how is an eval different from a test?](#1-concept-how-is-an-eval-different-from-a-test)
- [2. Four levels: component, step, end to end, online](#2-four-levels-component-step-end-to-end-online)
- [3. End to end or each step?](#3-end-to-end-or-each-step)
- [4. The eval set](#4-the-eval-set)
- [5. Graders and metrics](#5-graders-and-metrics)
- [6. Where evals run: gate, canary, production](#6-where-evals-run-gate-canary-production)
- [7. System design view: choosing and building](#7-system-design-view-choosing-and-building)
- [8. Failure modes](#8-failure-modes)
- [Where this fits](#where-this-fits)
- [References](#references)

---

## 0. One-minute version
- **What:** an eval runs the agent on a set of realistic cases and scores the results.
- **Why:** outputs vary run to run, so a few manual tries prove nothing. A prompt or model change can quietly break things.
- **How:** build a set of cases, grade end results and key steps, run it on every change, and sample production.
- **Catch:** scores are statistical. A judge model is itself imperfect, and a stale set gives false comfort.
- 🗣 "Tests check that code does what I wrote. Evals check that the system does what users need, on average, across cases."

---

## 1. Concept: how is an eval different from a test?
`boundary` ★★★

- **Plain idea:** an eval is a test suite for something that gives different answers each time.
- **Your analogy, checked**
  - Evaluating the whole result is like an **integration or end-to-end test**: did the system achieve the goal?
  - Evaluating each step is like a **unit test**: did this one decision (tool choice, arguments, retrieval) go right?
  - The analogy holds for *scope*. It breaks in three places:

| | Classic test | Eval |
|---|---|---|
| Result | pass or fail, same every run | a score; varies across runs, so repeat and average |
| Expected value | exact output | often a rubric; many answers can be right |
| Grader | an assertion | code, a judge model, or a human |
| Failure meaning | a bug | maybe a bug, maybe noise, maybe a changed model |
| Run on | each commit, in seconds | each change, in minutes, costs tokens |

- **Picture it:** a refund agent.
  - Unit-style: given "refund order 42", did it call `get_order` before `refund`, with the right order ID?
  - End-to-end: after the run, is the refund in the database exactly once, and did the reply say so?
- **How it works**
  1. Collect cases: input, context, and what good looks like.
  2. Run the agent on each case, several times if outcomes vary.
  3. Grade with code checks, then a judge, then humans for calibration.
  4. Compare scores to the last version and to a threshold.
  5. Block the change, or ship it.
- **The catch:** evals can't prove correctness; they estimate quality on cases you thought of.
- 🗣 "Step evals tell me where it broke. End-to-end evals tell me whether it works. I need both."

---

## 2. Four levels: component, step, end to end, online
`boundary` ★★★

| Level | What's graded | Analogy | Catches | Speed and cost |
|---|---|---|---|---|
| Component | one prompt, retriever or tool in isolation | unit test | a bad retriever, a vague tool description | fast, cheap |
| Step (trajectory) | each decision in a run: tool choice, arguments, order, efficiency | unit and contract test | wrong tool, bad arguments, wasted calls | medium |
| End to end | final outcome and final state | integration test | wrong answers, missed goals, side-effect errors | slower, pricier |
| Online | real production runs, scored after the fact | monitoring | drift, unseen inputs, real failure mix | continuous |

- **Final state beats final text.** Check that the database, ticket or file changed as expected, not only that the reply sounds right.
- **Component evals** matter most for retrieval ([3rag](3rag-reference-handbook.md)) because a bad retriever caps everything after it.
- 🗣 "Four levels: component, step, end to end, online. Each catches what the one above can't see."

---

## 3. End to end or each step?
`boundary` ★★★

- **Plain idea:** use end to end to decide *whether* to ship, and steps to find *why* it failed.
- **Why end to end alone isn't enough**
  - A lucky correct answer can hide a wrong route or a bad tool call.
  - A wrong early step can cascade and the final score shows only "fail", with no diagnosis.
  - It can't tell you which part to fix.
- **Why steps alone aren't enough**
  - Grading against one reference trace punishes valid alternative paths.
  - All steps can look fine while the result is wrong.
- **How to combine**
  - Grade the outcome first (did it achieve the goal and respect policy?).
  - Add step checks that are hard rules: right tool for the case, required arguments present, no forbidden calls, step count within budget.
  - Grade checkpoints, not exact traces: "looked up the order before refunding" rather than "step 3 must be X".
  - Run several trials per case. Capability (pass at least once in k tries) and reliability (pass all k tries) are different numbers. Production needs the second.
- **Weights:** high-stakes tasks weight the outcome and policy violations most; exploratory tasks weight outcome over route.
- 🗣 "I ship on end-to-end results and debug with step results. Reliability means passing every trial, not one."

---

## 4. The eval set
`software` ★★★

- **Sources, best first**
  1. Real production cases and failures (from traces, support tickets, thumbs-down).
  2. Cases written by domain experts, including tricky ones.
  3. Synthetic cases generated by a model and then reviewed by a person.
- **Size (order of magnitude):** start with 20–50 real cases; grow to hundreds. A small set that is realistic beats a big one that is generic.
- **What to include**
  - Common cases, edge cases, and "should refuse or escalate" cases.
  - Safety and injection cases from [4guardrails.md](4guardrails.md).
  - Cost and step-count targets.
  - Multi-turn cases for chat agents, and cases that need tool failures.
- **Hygiene**
  - Version the set; record which model, prompt and tool versions ran each time.
  - Keep a held-out slice you don't tune against.
  - Add every production failure as a new case. This is the improvement loop in [1loop.md](1loop.md) §5.
  - Retire cases that no longer reflect the product.
- 🗣 "Every production failure becomes a test case. That's how the set stays real."

---

## 5. Graders and metrics
`AI` ★★

| Grader | Good at | Weak at | Use for |
|---|---|---|---|
| Code check | exact facts, state changes, schema, tool arguments | nuance | first line for everything checkable |
| LLM as judge | tone, helpfulness, grounding, rubric items | bias, drift, cost | quality that code can't see |
| Human review | calibration and ambiguous cases | slow, costly | sampling and judge calibration |

- **Judge hygiene:** write a rubric with clear levels; ask for reasoning and a score; calibrate against human labels; watch for position and length bias; pin the judge model version.
- **Metrics that matter for agents**
  - Task success and policy compliance.
  - Tool selection accuracy and argument correctness.
  - Groundedness (answers supported by retrieved text).
  - Steps, tokens, cost and latency per task.
  - Safety violations and escalation rate.
  - Reliability across repeated trials.
- 🗣 "Code checks first, judge for nuance, humans to calibrate the judge."

---

## 6. Where evals run: gate, canary, production
`boundary` ★★★

- **Plain idea:** the same cases serve three jobs at three moments.

| Moment | Name | What it does | Blocks what |
|---|---|---|---|
| Before merge or release | eval gate (offline) | runs the set on the changed prompt, model, tool or flow; compares to baseline | the change, if scores drop or a policy case fails |
| Gradual rollout | canary or A/B | a share of live traffic uses the new version; compare outcomes | the rollout |
| In production | online scoring | samples real runs, scores them by judge and feedback | nothing directly; raises alerts and feeds the set |

- **What counts as a change that needs the gate:** prompt, model version, tool descriptions or schemas, retrieval settings, harness logic, guardrail rules.
- **Gate rules:** a minimum score, no regression beyond noise, zero critical policy failures, cost and latency budgets.
- **Evals vs termination:** a stop condition ends *one run*. An eval judges *many runs afterwards*. The in-loop verifier sits between them ([1loop.md](1loop.md) §3.1).
- **Evals vs guardrails:** guardrails act on live traffic in real time. Evals measure quality offline or after the fact. A guardrail's block rate is itself something to evaluate.
- **Closing the loop:** online scores and thumbs-down point to traces ([4observability.md](4observability.md)); label them; add them to the set; fix; re-run the gate.
- 🗣 "The gate stops regressions before release. Online scoring finds what the set didn't predict."

---

## 7. System design view: choosing and building
`boundary` ★★★

| Decision | Options | How to decide |
|---|---|---|
| Build the set from | production logs, experts, synthetic | start with real; add synthetic for gaps |
| What to grade | outcome only, steps only, both | both; outcome decides, steps diagnose |
| Judge model | same as agent, stronger, small tuned | a different and stronger model reduces self-bias |
| Gate strictness | block on any drop vs threshold | block policy failures always; use thresholds for quality |
| Online sampling | all, a percent, only flagged | all errors and low feedback; a few percent of the rest |
| Cost control | full set per commit vs a smoke subset | a small smoke set per commit; the full set before release |

| Tool | Type | Strength | Choose when |
|---|---|---|---|
| Braintrust | commercial, eval-first | datasets, scorers, experiment comparison | evals are the main workflow |
| LangSmith | commercial | evals tied to LangChain and LangGraph traces | you use that stack |
| Langfuse | open source | evals and datasets beside tracing | self-hosted, one tool for traces and evals |
| Arize Phoenix | source-available | strong trajectory and agent evals | agent-heavy, self-host |
| Promptfoo | open source | CLI test runs, red-teaming, CI friendly | quick CI gate |
| Inspect (UK AISI) | open source | research-grade eval framework | complex, agentic task evals |
| DeepEval, Ragas | open source libraries | ready metrics (RAG, agent) | want metrics out of the box |
| AgentCore Evaluations | managed (AWS) | scores sessions, traces and spans; custom evaluators | AWS runtime |
| ADK eval | built into ADK | test cases for ADK agents | ADK stack |

- **Default:** a versioned set of 50–200 real cases in the repo, code checks plus one calibrated judge, run in CI on every harness change, a smoke subset per commit, sampled online scoring through the trace backend, and every failure fed back as a case.

---

## 8. Failure modes
`boundary`

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Lucky passes | outcome-only grading | step audit shows wrong routes | add step and state checks |
| Penalizing valid paths | exact-trace matching | good runs fail the gate | grade checkpoints, not traces |
| Judge bias or drift | judge model changed or biased to length | judge disagrees with human sample | calibrate; pin the version; spot-check |
| Overfitting to the set | prompts tuned to the cases | held-out score lags | held-out slice; refresh from production |
| Flaky gate | single run per case | score swings between runs | several trials; compare with noise bands |
| Stale set | product changed | online score far from offline | continuous additions and retirements |
| Eval cost creep | full set on every commit | CI bills and time grow | smoke subset plus nightly full |

---

## Where this fits
- **Place:** L6 of [1a-bp.md](../1a-bp.md). The quality half of the control plane; its inputs come from traces.
- **Time it deserves:** 25 minutes; §1, §3 and §6.
- **I should be able to…**
  - Map unit, integration and end-to-end tests to step, outcome and online evals, and say where the analogy breaks.
  - Explain why I need both end-to-end and step-level evals.
  - Describe the eval gate and what counts as a change that triggers it.
  - Say how an eval differs from a termination condition and from a guardrail.

## References
1. [Anthropic — Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) — graders, trials, outcome vs transcript.
2. [Evaluating AI agents: trajectories, not just outcomes](https://tianpan.co/blog/2026/02/07/evaluating-ai-agents-trajectories-not-just-outcomes) — step-level metrics, offline vs online.
3. [Inspect AI](https://inspect.aisi.org.uk/) — open eval framework.
4. [Promptfoo](https://www.promptfoo.dev/docs/intro/) — CI-friendly evals and red-teaming.
5. [Amazon Bedrock AgentCore — release notes](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/release-notes.md) — Evaluations features.
