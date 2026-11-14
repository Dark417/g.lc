# 04safety.03evaluations.99interview Evaluations Interview Questions

> Level 4 (L4) + Level 5 (L5) answers on Retrieval-Augmented Generation (RAG) evaluation, overlap metrics, judges, guardrail evaluation, offline vs online, and Bedrock jobs.

## Index

- [1. Core Questions](#1-core-questions)
  - [1.1 Evaluating RAG](#11-evaluating-rag)
  - [1.2 Why Not Recall-Oriented Understudy for Gisting Evaluation (ROUGE) or Bilingual Evaluation Understudy (BLEU)](#12-why-not-recall-oriented-understudy-for-gisting-evaluation-rouge-or-bilingual-evaluation-understudy-bleu)
  - [1.3 Large Language Model (LLM)-as-a-Judge Risks](#13-large-language-model-llm-as-a-judge-risks)
  - [1.4 Evaluating a Guardrail](#14-evaluating-a-guardrail)
  - [1.5 Offline vs Online](#15-offline-vs-online)
  - [1.6 Bedrock Job Requirements](#16-bedrock-job-requirements)
- [2. L5-Only Questions](#2-l5-only-questions)
  - [2.1 Moving to a Cheaper Model](#21-moving-to-a-cheaper-model)
  - [2.2 Judge Up, Complaints Up](#22-judge-up-complaints-up)
  - [2.3 Bounding Eval Cost](#23-bounding-eval-cost)

Back to [00index](04safety.03evaluations.00index.md).

## 1. Core Questions

Each question has a bounded L4 answer and an L5 extension.

### 1.1 Evaluating RAG

**Q:** How would you evaluate a RAG system?

**L4 answer**

- Dataset of real questions with reference answers
- Retrieval metrics (context relevance/coverage, recall@k)
- Generation metrics (faithfulness, correctness)
- Bedrock RAG eval job: retrieve-only and retrieve-and-generate

**L5 extra**

- Separate the stages to localize faults
  - retrieval vs generation diagnosis grid
- Include unanswerable questions to test refusals and faithfulness
- Online: grounding scores and sampled judging
  - feed failures back into the offline set

See [06rag-eval](04safety.03evaluations.06rag-eval.md).

### 1.2 Why Not Recall-Oriented Understudy for Gisting Evaluation (ROUGE) or Bilingual Evaluation Understudy (BLEU)

**Q:** Why not just use ROUGE or BLEU?

**L4 answer**

- They count word overlap with one reference
- Correct paraphrases score low
- Wrong answers with shared words score high

**L5 extra**

- Fine for constrained outputs (extraction, short summaries) and as cheap regression signals
- BERTScore helps with synonyms but still doesn't check facts
- Judges add semantics at the price of bias and cost

See [02scoring-methods](04safety.03evaluations.02scoring-methods.md).

### 1.3 Large Language Model (LLM)-as-a-Judge Risks

**Q:** What are the risks of LLM-as-a-judge?

**L4 answer**

- Self-preference, verbosity, and position bias
- Cost
- Non-determinism

**L5 extra**

- Calibrate against human labels and report agreement
- Use a different family, explicit rubrics, pinned versions
- Pairwise comparisons: swap order and average

See [05llm-judge](04safety.03evaluations.05llm-judge.md).

### 1.4 Evaluating a Guardrail

**Q:** How do you evaluate a guardrail?

**L4 answer**

- Labeled allow/block cases per policy
- Run through `ApplyGuardrail`
- Compute precision/recall/False Positive Rate (FPR)

**L5 extra**

- Per-policy confusion matrices
  - near misses and benign look-alikes
- Threshold sweep from raw scores (`InvokeGuardrailChecks`) before picking strengths
- Gate version promotion on recall ≥ target and FPR ≤ budget
  - shadow in detect mode online

See [07guardrail-eval](04safety.03evaluations.07guardrail-eval.md).

### 1.5 Offline vs Online

**Q:** Offline vs online evaluation?

**L4 answer**

- Offline: fixed set, comparable, in Continuous Integration (CI)
- Online: real traffic, user signals, sampled judging

**L5 extra**

- Offline catches regressions; online catches distribution shift
- Close the loop: online failures become offline cases

See [08offline-online](04safety.03evaluations.08offline-online.md).

### 1.6 Bedrock Job Requirements

**Q:** What does a Bedrock evaluation job need?

**L4 answer**

- Service role
- Dataset JavaScript Object Notation Lines (JSONL) in Simple Storage Service (S3)
- Metric names
- Model or Knowledge Base (KB) config
- Output S3 Uniform Resource Identifier (URI)

**L5 extra**

- Judge model in `evaluatorModelConfig` for judge and RAG jobs
- Role trust with `aws:SourceAccount`
  - Key Management Service (KMS) grants for encrypted buckets
- Bring Your Own Inference (BYOI) for non-Bedrock systems

See [03bedrock-jobs](04safety.03evaluations.03bedrock-jobs.md).

## 2. L5-Only Questions

Depth, scale, and design ownership.

### 2.1 Moving to a Cheaper Model

**Q:** Design an evaluation program for a customer-support assistant moving from Claude to a cheaper model.

- Golden set (scrubbed real tickets) + failure set, categories per intent
- Judge job on both models
  - Correctness, Completeness, Faithfulness, Refusal
  - human sample for calibration
- Per-category diff and cost/latency per answer
  - decide per category (router) if the cheap model loses only some
- Guardrail re-eval
  - new model may produce different outputs ⇒ output-side FPR changes
- Online canary with sampled judging and escalation rate before full switch

### 2.2 Judge Up, Complaints Up

**Q:** Your judge says quality went up 8% after a prompt change, but complaints rose. What happened?

- Likely causes
  - judge bias (verbosity: new prompt is longer)
  - dataset not representative
  - category mix hides a regression
- Check
  - human agreement on the changed items
  - per-category scores
  - response length vs score
- Fix
  - fix the rubric
  - add complaint cases to the set
  - re-run before deciding

### 2.3 Bounding Eval Cost

**Q:** How do you keep eval cost bounded at scale?

- Stratified sampling instead of full sets
- Cheap judge for smoke, strong judge for release
- Few metrics mapped to known failures
- Cache responses (BYOI) and only re-judge
- Retrieve-only eval for retrieval changes (no generation cost)
