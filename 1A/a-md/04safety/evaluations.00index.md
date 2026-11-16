# evaluations Evaluations

> Measure a Large Language Model (LLM) system on a fixed dataset so every change ships with a before/after score.

## Index

- [1. Source and Scope](#1-source-and-scope)
- [2. One-Minute Version](#2-one-minute-version)
- [3. File Index](#3-file-index)
  - [3.1 Concept](#31-concept)
  - [3.2 Bedrock Jobs](#32-bedrock-jobs)
  - [3.3 Targets](#33-targets)
  - [3.4 Decisions and Interview](#34-decisions-and-interview)
- [4. Code Map](#4-code-map)
- [5. Gaps](#5-gaps)
- [References](#references)

## 1. Source and Scope

Lectures: AIP-C01 #21 (slides p.49–51) + guardrail evaluation.

- Preview of #190–#192
  - model evaluation
  - Recall-Oriented Understudy for Gisting Evaluation (ROUGE)/Bilingual Evaluation Understudy (BLEU)/BERTScore
  - Bedrock Model Evaluations
- Scope: Python + Terraform
- Terraform: `terraform/` module `04safety_03evaluations`
  - evaluation service role `a-bedrock-eval`
  - app policy
  - optional example job
- Code: Python `app/*/_04safety_03evaluations*` (slice `evals`)
- Field and metric names
  - checked against the botocore 1.44 `bedrock` model (`CreateEvaluationJob` shape + `metricNames` doc text) and provider 6.73, 2026-11
  - not in that doc text, so marked "verify"
    - `Builtin.CitationPrecision`, `Builtin.CitationCoverage`
    - judge `taskType: "General"`
    - the Simple Storage Service (S3) result layout
- Numbers
  - Bedrock User Guide "Evaluate the performance of Amazon Bedrock resources", read 2026-11
  - unless marked "order of magnitude"

## 2. One-Minute Version

No eval set, no change.

- What
  - Measuring an LLM system on a fixed dataset so changes can be compared with numbers
  - Targets: a model, a prompt, a Retrieval-Augmented Generation (RAG) pipeline (retrieval + generation), a guardrail
- Why
  - LLM output is open-ended
    - "looks good" on five examples does not survive a model or prompt change
  - Every change (model version, chunk size, guardrail strength) needs a before/after score
- How
  - Dataset: prompts + reference answers (+ category, + expected labels)
  - Score with one of three methods
    - Automatic metrics: string overlap (ROUGE, BLEU), embedding similarity (BERTScore), exact match
    - LLM-as-a-judge: a second model rates correctness, faithfulness, … with a rubric
    - Humans: rating work teams, slow and costly, the ground truth for the other two
  - Bedrock evaluation jobs run all three
    - RAG eval scores retrieval only or retrieval + generation
  - Guardrails: labeled allow/block set → ApplyGuardrail → confusion matrix → tune strengths
- Catch
  - Overlap metrics punish correct paraphrases
  - Judges are biased (self-preference, verbosity, position)
    - calibrate against human labels
  - A small or stale dataset gives confident wrong answers
  - Offline scores do not guarantee online quality
    - sample production traffic too
- 🗣 "No eval set, no change: every prompt, model, or guardrail edit ships with a before/after score."
- 🗣 "Retrieval metrics tell you if the right context arrived; generation metrics tell you if the model used it."
- 🗣 "A guardrail is a classifier: report precision, recall, and false-positive rate per policy."

## 3. File Index

Read top to bottom: scoring methods, then Bedrock jobs, then each target.

### 3.1 Concept

- [01why-picture](evaluations.01why-picture.md)
  - Why evaluation tooling was created, use cases, picture
- [02scoring-methods](evaluations.02scoring-methods.md)
  - Automatic vs judge vs human
  - ROUGE, BLEU, BERTScore mechanics

### 3.2 Bedrock Jobs

- [03bedrock-jobs](evaluations.03bedrock-jobs.md)
  - Job types, metric names, custom metrics, Bring Your Own Inference (BYOI)
  - Request skeleton, lifecycle, results, cost
- [04datasets](evaluations.04datasets.md)
  - Model and RAG JavaScript Object Notation Lines (JSONL), built-in datasets, what makes a good set
- [05llm-judge](evaluations.05llm-judge.md)
  - Judge mechanism, biases, mitigations, model choice

### 3.3 Targets

- [06rag-eval](evaluations.06rag-eval.md)
  - Retrieval vs generation metrics, diagnosis grid (lecture 21)
- [07guardrail-eval](evaluations.07guardrail-eval.md)
  - Labeled cases, confusion matrix per policy, release gate
- [08offline-online](evaluations.08offline-online.md)
  - Offline Continuous Integration (CI) sets vs online sampling, the feedback loop

### 3.4 Decisions and Interview

- [98tradeoffs](evaluations.98tradeoffs.md)
  - When to use / not, knobs, best practices, comparison, failure modes
- [99interview](evaluations.99interview.md)
  - Level 4 (L4) + Level 5 (L5) questions, L5-only design questions

## 4. Code Map

Python only; the layer-first paths below replace the old slice package.

| Scenario | Concept file | Python |
|---|---|---|
| Dataset records (model, RAG) | 04 | `app/domain/_04safety_03evaluations.py` `EvalCase.to_record`, `RagCase.to_record` |
| Write JSONL to S3 `evals/datasets/` | 04 | `app/infra/_04safety_03evaluations.py` `write_dataset` |
| Automatic model eval (built-in metrics) | 03 | `infra` `create_automated_model_eval` |
| LLM-as-a-judge model eval (+ custom metric) | 03 | `infra` `create_judge_model_eval` |
| RAG eval: retrieve-and-generate / retrieve-only | 06 | `infra` `create_rag_eval` |
| Poll with backoff, list with pagination, stop | 03 | `infra` `wait_for_job`, `list_jobs`, `stop_job` |

| Scenario | Concept file | Python |
|---|---|---|
| Read results from S3, aggregate per metric | 03 | `infra` `read_results` |
| Guardrail eval harness → confusion matrix per policy | 07 | `infra` `run_guardrail_eval` → `domain` `GuardrailEvalReport` |
| Confusion matrix math | 07 | `domain` `ConfusionMatrix` |
| ROUGE-1 / ROUGE-L mechanics | 02 | `app/service/_04safety_03evaluations/metrics.py` `rouge_n`, `rouge_l` |
| Result store port + adapter | 08 | `domain` `EvalResultStore`, `infra` `InMemoryEvalResultStore` |
| Orchestration (dataset → job → store) | 03 | `app/service/_04safety_03evaluations/__init__.py` `EvalService` |
| Representational State Transfer (REST) | — | `app/api/_04safety_03evaluations.py` (`/evals/...`) |

## 5. Gaps

Known gaps between this doc and the code.

- Human evaluation jobs
  - needs a SageMaker Ground Truth flow definition
  - request shape in [03bedrock-jobs](evaluations.03bedrock-jobs.md) only
- BYOI (precomputed inference / RAG sources): shape in 03bedrock-jobs only
- BLEU and BERTScore: described, not implemented
- Online evaluation (sampled production judging, AgentCore online evals): doc only
- S3 result layout
  - parser is tolerant (finds `metricName` + `result` anywhere)
  - the exact layout is not in the Application Programming Interface (API) model; verify on a real job

## References

- [aws-samples/amazon-bedrock-samples (evaluation and RAG notebooks)](https://github.com/aws-samples/amazon-bedrock-samples)
- [Bedrock User Guide — Evaluate performance (model + RAG evaluation)](https://docs.aws.amazon.com/bedrock/latest/userguide/evaluation.html)
- [Bedrock API — CreateEvaluationJob](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_CreateEvaluationJob.html)
- [Retrieval-Augmented Generation Assessment (RAGAS) documentation](https://docs.ragas.io/)
- [Zheng et al. 2023, "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena"](https://arxiv.org/abs/2306.05685)
