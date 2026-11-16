# guardrails.99interview Guardrails Interview Questions

> Level 4 (L4) + Level 5 (L5) answers on guardrail structure, call styles, prompt attacks, grounding, Personally Identifiable Information (PII), streaming, and rollout.

## Index

- [1. Core Questions](#1-core-questions)
  - [1.1 Guardrail Anatomy](#11-guardrail-anatomy)
  - [1.2 ApplyGuardrail vs guardrailConfig](#12-applyguardrail-vs-guardrailconfig)
  - [1.3 Prompt-Attack Filter](#13-prompt-attack-filter)
  - [1.4 Contextual Grounding](#14-contextual-grounding)
  - [1.5 BLOCK vs ANONYMIZE](#15-block-vs-anonymize)
  - [1.6 Sync vs Async Streaming](#16-sync-vs-async-streaming)
  - [1.7 Safe Rollout](#17-safe-rollout)
- [2. L5-Only Questions](#2-l5-only-questions)
  - [2.1 Multi-Tenant Agent Platform](#21-multi-tenant-agent-platform)
  - [2.2 Over-Blocking After Launch](#22-over-blocking-after-launch)
  - [2.3 Automated Reasoning vs Grounding](#23-automated-reasoning-vs-grounding)

Back to [00index](guardrails.00index.md).

## 1. Core Questions

Each question has a bounded L4 answer and an L5 extension.

### 1.1 Guardrail Anatomy

**Q:** What does a Bedrock guardrail consist of, and how is it applied?

**L4 answer**

- Up to six policies
  - content filters (incl. prompt attack)
  - denied topics, words, sensitive info
  - contextual grounding, Automated Reasoning
- Blocked-input and blocked-output messages
- Applied by id + version
  - on Converse/InvokeModel, Knowledge Base (KB), Agents
  - or standalone via `ApplyGuardrail`
- Input check → model → output check
  - any BLOCK hit returns the canned message

**L5 extra**

- Each check is a parallel set of classifiers
  - result is an assessment per policy
  - that is your audit and eval data
- Input block saves model tokens; output block wastes them
  - put cheap, high-recall checks on input
- Version pinning is the deployment contract; DRAFT is a dev artifact

See [02policies](guardrails.02policies.md).

### 1.2 ApplyGuardrail vs guardrailConfig

**Q:** When would you use ApplyGuardrail instead of guardrailConfig on Converse?

**L4 answer**

- Model is not on Bedrock (SageMaker, OpenAI, on-prem)
- Checking text that is not a model call
  - retrieved docs before indexing
  - tool results, user uploads
- You need custom flow between checks
  - e.g. log, route to human, retry with a different prompt

**L5 extra**

- Two extra round trips per turn vs one integrated call ⇒ latency budget
- Lets one central "safety service" own policy for many model providers
- With streaming from a non-Bedrock model, you must build your own buffering window
  - same trade-off as sync mode

See [05call-styles](guardrails.05call-styles.md).

### 1.3 Prompt-Attack Filter

**Q:** How does the prompt-attack filter work, and what goes wrong with it?

**L4 answer**

- Classifier on input for jailbreak, injection
  - and leakage on Standard tier
- Output strength must be NONE
- Common False Positive (FP): your own system prompt looks like instructions

**L5 extra**

- Fix with input tagging so only untrusted text is scanned
  - `guardContent` in Converse
  - tag suffix in InvokeModel
- Indirect injection (Retrieval-Augmented Generation (RAG) docs, tool output) needs `ApplyGuardrail` on that content too
- It is one layer
  - least-privilege tools and output checks limit the blast radius when it misses

See [04prompt-attacks](guardrails.04prompt-attacks.md).

### 1.4 Contextual Grounding

**Q:** Explain contextual grounding. What does it guarantee?

**L4 answer**

- Scores the answer against a grounding source (GROUNDING)
- Scores it against the query (RELEVANCE)
- Blocks if a score is under its threshold
- Needs the three qualifiers: `grounding_source`, `query`, `guard_content`

**L5 extra**

- Guarantee is relative to the source passed
  - wrong retrieval + faithful answer still passes
- Threshold is a precision/recall knob
  - set it from a labeled set of grounded vs hallucinated answers
- Source length limits
  - pass the top-k passages actually cited, not the whole KB result

See [03sensitive-grounding](guardrails.03sensitive-grounding.md).

### 1.5 BLOCK vs ANONYMIZE

**Q:** BLOCK vs ANONYMIZE for PII — how do you choose?

**L4 answer**

- BLOCK refuses the whole call
  - for identifiers that must never flow (Social Security Number (SSN), card numbers)
- ANONYMIZE masks with `{TYPE}` and continues
  - for contact info the task does not need

**L5 extra**

- Input ANONYMIZE removes PII before it reaches model logs and providers
- Masking breaks tasks that need the value
  - reversible pseudonymization outside the guardrail ([pii-redaction](pii-redaction.00index.md))
- ANONYMIZE is not applied in async streaming
  - PII policies force sync mode

### 1.6 Sync vs Async Streaming

**Q:** Sync vs async stream processing?

**L4 answer**

- Sync buffers and checks before sending
  - safe, slower first token
- Async streams immediately and checks in the background
  - fast, may show text that later gets blocked

**L5 extra**

- Async skips masking ⇒ PII exposure
- User Interface (UI) must handle a mid-stream stop (retract or replace)
- Choose per route
  - async for low-risk internal tools
  - sync for customer-facing

See [06streaming](guardrails.06streaming.md).

### 1.7 Safe Rollout

**Q:** How do you roll out a guardrail change safely?

**L4 answer**

→ Edit DRAFT.  
→ Run the eval set against DRAFT with `ApplyGuardrail`.  
→ Create a numbered version.  
→ Switch the app config.

**L5 extra**

- Detect mode on live traffic first (`inputAction=NONE`)
  - compare intervention rates
- Canary: route a percentage of traffic to the new version id
  - alarm on intervention rate and complaint rate
- Rollback = point to the previous number
  - versions are immutable

See [07versions-tiers](guardrails.07versions-tiers.md).

## 2. L5-Only Questions

Depth, scale, and design ownership.

### 2.1 Multi-Tenant Agent Platform

**Q:** Design guardrails for a multi-tenant agent platform that serves Bedrock and third-party models.

- Central safety service exposing `check(input|output, tenant)` built on `ApplyGuardrail`
- Per-tenant guardrail (or version) chosen from tenant config
  - shared baseline enforced at account/org level
- Untrusted content (tool results, retrieved pages) checked before entering the agent context
- Streaming
  - own sliding buffer for non-Bedrock models
  - sync mode for Bedrock
- Metrics per tenant and policy
  - labeled eval sets per tenant for tuning
- Cost
  - guard only untrusted spans
  - cache verdicts for identical retrieved chunks

### 2.2 Over-Blocking After Launch

**Q:** Your guardrail blocks 8% of legitimate traffic after launch. What do you do?

→ Pull assessments for blocked requests: which policy, which category, which confidence.  
→ Most often: untagged system prompt (prompt attack) or broad denied topic.  
→ Reproduce with `ApplyGuardrail` `outputScope=FULL` on a sample; add cases to the eval set.  
→ Fix: tagging, lower strength on that one category, sharpen topic definition.  
→ Re-run eval, create a new version, canary.

- Prevent
  - detect-mode shadowing
  - an FP-rate gate in Continuous Integration (CI) before version promotion

### 2.3 Automated Reasoning vs Grounding

**Q:** When is Automated Reasoning worth it over contextual grounding?

- Grounding = statistical "is this supported by the passage"
- Automated Reasoning (AR) = logical "does this follow from the rules"
  - returns contradicting rules
- Worth it for crisp rule sets with high cost of a wrong yes/no
  - eligibility, policy compliance
- Cost
  - rule extraction and test-case curation
  - findings only, so you build the decision logic

See [08automated-reasoning](guardrails.08automated-reasoning.md).
