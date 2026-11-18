# 6llmops — Shipping Changes: Versioning, Rollout, Rollback

> How prompts, models, tools and policies are versioned, tested, rolled out and rolled back, like code.
> Group 6 (production). Related: [4evals.md](4evals.md), [2models.md](2models.md) §7, [4observability.md](4observability.md).
> Concept level, no code (AGENTS.md §8b). Last updated: 2026-11-16.

## Index
- [0. One-minute version](#0-one-minute-version)
- [1. Concept](#1-concept)
- [2. What gets versioned](#2-what-gets-versioned)
- [3. The pipeline](#3-the-pipeline)
- [4. Rollout strategies](#4-rollout-strategies)
- [5. Rollback and incidents](#5-rollback-and-incidents)
- [6. Config at runtime](#6-config-at-runtime)
- [7. System design view: choosing](#7-system-design-view-choosing)
- [8. Failure modes](#8-failure-modes)
- [Where this fits](#where-this-fits)
- [References](#references)

---

## 0. One-minute version
- **What:** LLMOps is release engineering for agents: every prompt, model, tool and policy change is a versioned artifact that passes a gate and rolls out gradually.
- **Why:** a one-word prompt edit can change behavior as much as a code change, and it often ships without review.
- **How:** version artifacts together, gate them with evals, roll out by shadow or canary, watch quality and cost, roll back fast.
- **Catch:** if prompts live in a console that anyone can edit, none of this works.
- 🗣 "A prompt is code. It gets a version, a review, an eval gate and a rollback."

---

## 1. Concept
`software` ★★★

- **Plain idea:** the same CI/CD discipline you'd use for a Spring service, applied to the parts that aren't code.
- **Picture it:** a teammate edits the support agent's prompt to be "more concise".
  - Without LLMOps: it ships at once; refund explanations get vague; complaints rise a week later.
  - With LLMOps: the edit is a pull request; the eval gate shows a drop on "explain the policy" cases; it's fixed before release.
- **How it works**
  1. Change an artifact in version control or a prompt registry.
  2. Run unit tests, then the eval gate.
  3. Deploy to shadow or a small canary.
  4. Compare quality, cost and latency against the current version.
  5. Promote or roll back.
- **The catch:** behavior depends on the combination of versions; test them together.

---

## 2. What gets versioned
`software` ★★★

| Artifact | Example change | Breaks if unversioned |
|---|---|---|
| Harness code | new loop limit | normal code risk |
| Prompts and instructions | wording, examples | silent behavior change |
| Model version | snapshot upgrade | quality and cost shift |
| Tool definitions | renamed argument, new description | wrong tool calls |
| Retrieval config and index | chunk size, re-index | answers change, citations break |
| Guardrail and access policies | thresholds, rules | over-blocking or leaks |

- **Bundle them:** a release is a named set of versions ("support-agent v42 = prompt v17 + model X + tools v9 + policy v5").
- **Stamp the bundle on every trace,** so any behavior can be traced to a release ([4observability.md](4observability.md)).

---

## 3. The pipeline
`software` ★★★

```
 change -> lint and unit tests -> smoke eval (minutes) -> full eval gate -> build -> shadow or canary -> promote
```

| Stage | Checks | Blocks on |
|---|---|---|
| Lint and unit tests | schemas, tool contracts, prompt templates render | errors |
| Smoke eval | a small set of critical cases | any critical failure |
| Full eval gate | the full set; cost and latency budgets | score drops beyond noise; policy failures |
| Review | a human reads prompt and policy diffs | reviewer sign-off |
| Shadow or canary | live traffic comparison | quality, cost or error alarms |

- **Prompt review is a real review.** Diff the text, read the eval delta, check cost.

---

## 4. Rollout strategies
`boundary` ★★★

| Strategy | How | Good at | Weak at | Choose when |
|---|---|---|---|---|
| Shadow | new version runs on copies of live traffic; output not shown | zero user risk | double cost; no side effects allowed | risky changes; read-only paths |
| Canary | a small share of users get the new version | real feedback, limited blast radius | needs metrics per version | default |
| A/B test | split traffic to compare outcomes | business-metric comparison | slow to reach significance | product decisions |
| Feature flag | switch per user, tenant or region | instant on and off | flag debt | tenant-by-tenant rollouts |
| Blue / green | two full stacks; switch traffic | instant rollback | cost of two stacks | harness code changes |

- **Shadow and side effects:** a shadow run must not call write tools for real. Use dry-run modes or recorded tool outputs.
- **Managed help:** AWS AgentCore Optimization supports versioned config bundles and A/B tests by splitting Gateway traffic.

---

## 5. Rollback and incidents
`software` ★★

- **Rollback = switch the bundle pointer** back to the last good release. Keep old versions deployable.
- **Triggers:** task success drop, safety violation, cost per task spike, error rate, user complaints.
- **Kill switch:** disable an agent or one tool instantly without a deploy ([4access.md](4access.md)).
- **Incident loop:** find runs in traces, roll back, label failures, add them to the eval set, fix, re-run the gate.
- **Model deprecations** are planned incidents: qualify the replacement through the same pipeline before the retirement date.

---

## 6. Config at runtime
`software` ★★

- **Where configs live:** Git (reviewed, slow), a prompt registry (versioned, UI), a config service (fast to change).
- **Load and cache:** load at start or session start with a refresh interval; never mid-run, so one run sees one version.
- **Who may change what:** prompt edits need review; emergency flags can be flipped by on-call.
- **Tools at hand**

| Tool | Role |
|---|---|
| Git plus CI (GitHub Actions, GitLab CI) | source of truth and pipeline |
| Prompt registries (LangSmith, Langfuse, MLflow) | versioned prompts with UI and history |
| Feature flags (LaunchDarkly, Unleash, cloud config services) | per-tenant rollout, kill switches |
| Eval tools ([4evals.md](4evals.md)) | the gate |
| AgentCore Optimization | config bundles and A/B on AWS |

---

## 7. System design view: choosing
`boundary` ★★★

| Decision | Options | How to decide |
|---|---|---|
| Prompt home | code, registry, console | code or registry with review; never unreviewed console edits in prod |
| Release unit | each artifact alone vs bundle | bundle |
| Gate | manual vs eval gate | eval gate plus human review for prompts and policies |
| Rollout | shadow, canary, A/B, flags | canary by default; shadow for risky reads |
| Rollback | redeploy vs pointer switch | pointer switch |

- **Default:** prompts and policies in Git or a registry, bundled releases stamped on traces, smoke and full eval gates in CI, canary rollout with per-version metrics, instant pointer rollback and kill switches.

---

## 8. Failure modes
`boundary`

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Unreviewed prompt edit | console editing in prod | behavior shift with no deploy | review and registry with audit |
| Version mismatch | prompt updated, tools not | wrong tool calls | bundles |
| Shadow causes side effects | write tools run in shadow | duplicate actions | dry-run tools in shadow |
| Canary without metrics | no per-version split | can't compare | tag traces with release |
| Mid-run config change | hot reload during a run | inconsistent steps | load per run |
| Old version not deployable | artifacts deleted | rollback fails | keep N releases |

---

## Where this fits
- **Place:** L8.4 of [1a-bp.md](../1a-bp.md).
- **Time it deserves:** 15 minutes; §2, §3 and §4.
- **I should be able to…**
  - List the six artifacts and why each is versioned.
  - Describe the pipeline and what the eval gate blocks.
  - Choose between shadow, canary, A/B and flags.
  - Explain rollback as a pointer switch.

## References
1. [Google — Rules of ML / MLOps practices](https://developers.google.com/machine-learning/guides/rules-of-ml) — release discipline for ML systems.
2. [AgentCore release notes](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/release-notes.md) — Optimization, A/B testing.
3. [Langfuse — prompt management](https://langfuse.com/docs/prompts) — versioned prompts.
