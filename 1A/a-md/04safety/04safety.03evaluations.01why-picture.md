# 04safety.03evaluations.01why-picture Why Evaluations and the Picture

> Why Large Language Model (LLM) evaluation tooling exists, where it is used, and how a job and the guardrail harness flow.

## Index

- [1. Why It Was Created](#1-why-it-was-created)
  - [1.1 The Pain Before It](#11-the-pain-before-it)
  - [1.2 What Changed](#12-what-changed)
  - [1.3 Common Use Cases](#13-common-use-cases)
- [2. Picture](#2-picture)
  - [2.1 Code: Job Record](#21-code-job-record)

Back to [00index](04safety.03evaluations.00index.md).

## 1. Why It Was Created

Classic Natural Language Processing (NLP) metrics assumed one right answer; generative answers have many.

### 1.1 The Pain Before It

- Classic NLP had task metrics tied to one reference
  - Bilingual Evaluation Understudy (BLEU) for translation
  - Recall-Oriented Understudy for Gisting Evaluation (ROUGE) for summaries
- Generative answers have many correct forms
  - overlap metrics under-score good answers
- Human evaluation is the gold standard
  - but takes days and costs per item

### 1.2 What Changed

- LLM-as-a-judge (2023+)
  - strong models grade with rubrics, at scale, in minutes
- Managed jobs (Bedrock Evaluations, 2023–2025)
  - bundle datasets, judges, metrics, reports

### 1.3 Common Use Cases

- Pick a model for a task (quality vs cost vs latency)
- Regression-test a prompt or Retrieval-Augmented Generation (RAG) change in Continuous Integration (CI)
- Tune a guardrail's strengths against a false-positive budget
- Measure bias and harmful-output rates for responsible-Artificial Intelligence (AI) reviews

## 2. Picture

A managed job does inference then scoring; guardrails use a local harness.

```text
 dataset.jsonl (S3 evals/datasets/)
   prompt, referenceResponse, category
        │
        ▼
 ┌──────────────── Bedrock evaluation job ────────────────┐
 │ inference:  model  |  KB retrieve  |  KB retrieve+gen  │  (or precomputed responses: BYOI)
 │      │                                                 │
 │      ▼                                                 │
 │ scoring:    built-in metrics | judge model | humans    │
 └────────────────────────────┬───────────────────────────┘
                              ▼
               results (S3 evals/results/<job>/...)  → report, per-prompt scores + judge explanations

 guardrail eval (local harness):
   labeled cases ─► ApplyGuardrail(outputScope=FULL) ─► predicted block? + which policy
                 ─► confusion matrix per policy ─► precision / recall / FPR ─► adjust strengths ─► repeat
```

Notice that guardrails have no managed job type, so they are scored by a local loop.

### 2.1 Code: Job Record

- Each job is kept as data: kind, dataset, output, status, scores

```python
# app/domain/_04safety_03evaluations.py
class JobKind(StrEnum):
    AUTOMATED = "automated"  # built-in algorithms: Accuracy, Robustness, Toxicity
    JUDGE = "judge"  # LLM-as-a-judge model evaluation
    RAG_RETRIEVE = "rag_retrieve"  # retrieve-only: ContextRelevance, ContextCoverage
    RAG_RETRIEVE_GENERATE = "rag_retrieve_generate"  # Correctness, Faithfulness, ...


@dataclass(frozen=True)
class EvalJob:
    job_arn: str
    kind: JobKind
    dataset_uri: str
    output_uri: str
    status: str = "InProgress"  # InProgress | Completed | Failed | Stopping | Stopped | Deleting
    failure_messages: tuple[str, ...] = ()
    scores: dict[str, float] = field(default_factory=dict)  # metric -> mean score (0..1 for built-ins)
```

- Catch
  - A score is only comparable with the dataset version and judge that produced it
