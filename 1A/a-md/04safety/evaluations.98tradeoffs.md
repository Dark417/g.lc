# evaluations.98tradeoffs Evaluations Trade-offs

> When to use managed jobs vs a local harness, the knobs, best practices, comparison, and failure modes.

## Index

- [1. When to Use / Not](#1-when-to-use--not)
- [2. Knobs](#2-knobs)
- [3. Best Practices](#3-best-practices)
- [4. Comparison](#4-comparison)
- [5. Failure Modes](#5-failure-modes)

Back to [00index](evaluations.00index.md).

## 1. When to Use / Not

Managed jobs for Bedrock models and Knowledge Bases (KBs); a local harness for guardrails and fast Continuous Integration (CI) loops.

- Use Bedrock evaluation jobs when
  - Models and KBs are on Bedrock, and you want managed judges, reports, and an audit trail
  - Comparing several models or KB configs on the same dataset
- Use a local harness when
  - Evaluating guardrails (no managed job type for it)
  - Fast inner-loop checks in CI where a job's minutes of startup are too slow
  - Metrics Bedrock does not offer (exact JavaScript Object Notation (JSON) schema validity, tool-call accuracy)
- Do not
  - Use Recall-Oriented Understudy for Gisting Evaluation (ROUGE)/Bilingual Evaluation Understudy (BLEU) alone for open-ended answers
  - Trust a judge you have never compared with humans
  - Evaluate on the same examples you used to write the prompt (overfitting)

## 2. Knobs

| Knob | Values | Trade-off | Change when |
|---|---|---|---|
| Job type | automatic / judge / human / Retrieval-Augmented Generation (RAG) | cost and speed vs nuance | new task → judge; calibration → human |
| Judge model | supported evaluator list | quality vs cost; family bias | generator family changes |
| Metric list | ≤ 25 per dataset config | each metric = judge calls | focus on 3–5 that map to failures |
| Dataset size | up to the per-job cap | confidence vs cost | wide confidence intervals → more items |
| `category` | free text | per-slice insight | quality differs by segment |

| Knob | Values | Trade-off | Change when |
|---|---|---|---|
| `inferenceParams` | JSON string (temperature, maxTokens) | determinism vs realism | use prod settings; temperature 0 for regression |
| `numberOfResults` (RAG) | 1–100 | coverage vs noise | coverage low → raise |
| Guardrail strengths | NONE…HIGH per category | recall vs False Positive Rate (FPR) | per confusion matrix |
| `outputScope` (guardrail eval) | FULL | bigger responses | always FULL for eval |

```python
# app/config/_04safety_03evaluations.py
class EvalsSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="A_EVALS_", env_file=".env", extra="ignore")

    role_arn: str = "arn:aws:iam::ACCOUNT_ID:role/a-bedrock-eval"  # terraform output bedrock_eval_role_arn
    datasets_prefix: str = "evals/datasets/"
    results_prefix: str = "evals/results/"
    kms_key_id: str = "alias/a-data"  # customerEncryptionKeyId for results
    judge_model_id: str = "us.amazon.nova-pro-v1:0"
    knowledge_base_id: str = "KB_ID"  # terraform output of knowledge-bases
    rag_number_of_results: int = 5  # top-k for the RAG eval (1..100)
    guardrail_version: str = "DRAFT"  # evaluate the candidate (DRAFT) before creating a version
```

## 3. Best Practices

Each rule names the failure it prevents.

- Version dataset + config + results together
  - prevents comparing scores from different sets
- Report per-category scores, not only the mean
  - prevents a regression hiding in a small segment
- Keep a fixed "golden" set and a growing "failures" set
  - prevents overfitting to old cases
- Calibrate judges on human labels
  - prevents optimizing for judge bias
- Use the same inference params as production
  - prevents eval/prod drift
- Encrypt datasets and results with the Customer Managed Key (CMK), scrub Personally Identifiable Information (PII) first
  - eval buckets hold real user text
- Gate releases on thresholds in CI
  - prevents "we'll look at the eval later"

## 4. Comparison

| Option | What it is | Strength | Weakness | Choose when |
|---|---|---|---|---|
| Bedrock Evaluations | Managed model + RAG eval jobs (auto, judge, human) | No infra; KB-native RAG metrics; reports; Identity and Access Management (IAM)/Key Management Service (KMS) | Minutes per job; fixed metric set + custom metrics; Bedrock-centric (Bring Your Own Inference (BYOI) helps) | Amazon Web Services (AWS) stack, model/KB selection, audit |
| Retrieval-Augmented Generation Assessment (RAGAS) | Open-source RAG metrics library (faithfulness, context precision/recall, answer relevancy) | Popular RAG metrics, any Large Language Model (LLM) as judge | You run it; metric definitions change between versions | Custom RAG pipelines, notebook iteration |
| DeepEval | Open-source pytest-style LLM test framework | Unit-test ergonomics, many metrics, CI-friendly | You host judge calls; metric quality varies | Developer CI gates |
| promptfoo | Open-source Command Line Interface (CLI) for prompt/model matrix tests + red teaming | Fast config-driven comparisons; red-team plugins | Less RAG-specific depth | Prompt A/B and jailbreak testing |
| Custom harness | Your code: dataset → system → scorers | Exactly your metrics (guardrail confusion matrix, schema checks) | You maintain it | Guardrails, tool calls, domain checks |
| Human eval (Ground Truth) | Managed rating workflows | Ground truth | Slow, costly | Calibration, launch reviews |

- Default
  - Bedrock Evaluations for model and RAG quality
  - plus a custom harness for guardrails and schema/tool checks
  - unless the pipeline is not on Bedrock and BYOI is awkward
    - RAGAS or DeepEval in CI
- Deciding variable
  - where inference runs
  - whether you need managed reports + audit or fast developer loops

Pick: Bedrock Evaluations + a custom guardrail harness, unless the pipeline runs off Bedrock.

## 5. Failure Modes

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Good answers score low | ROUGE/BLEU on paraphrases | judge vs metric disagreement | judge or BERTScore; multiple references |
| Judge inflates scores | same family as generator; verbosity | human sample disagrees | different-family judge; rubric anchors |
| Scores jump with no change | judge model or dataset changed | config diff | pin judge version; version datasets |
| Job fails AccessDenied | role trust / Simple Storage Service (S3) / KMS / model access | `failureMessages` | trust bedrock.amazonaws.com + SourceAccount; grants |
| Job fails on dataset | wrong JavaScript Object Notation Lines (JSONL) keys, too many prompts | `failureMessages` | validate locally before upload |

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| RAG eval looks fine, prod poor | dataset not like real questions | online sampling | build sets from scrubbed logs |
| Guardrail tuned to a tiny set | 20 cases, no near misses | False Positive (FP) complaints after launch | 100s of cases per policy, benign look-alikes |
| Overfit prompt | eval set used while writing the prompt | holdout set drops | separate dev and test sets |
| Cost blow-up | many metrics × many items × big judge | bill | sample, fewer metrics, cheaper judge for smoke |
