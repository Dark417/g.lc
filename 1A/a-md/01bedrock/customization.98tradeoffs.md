# customization Trade-Offs

> When to customize, which knobs matter, how it compares, and how it fails.

## Index

- [1. When To Use / Not](#1-when-to-use--not)
- [2. Knobs And Best Practices](#2-knobs-and-best-practices)
- [3. Comparison](#3-comparison)
- [4. Failure Modes](#4-failure-modes)

Back to [00index](customization.00index.md).

---

## 1. When To Use / Not

Customize only for a measured behavior gap at volume.

- Fine-tune when
  - A narrow, repeated task with a stable target output (format, tone, labels)
  - Prompt + few-shot is close but too long, too slow, or too inconsistent
  - Volume is high enough to pay for serving
- Continued pre-training when
  - Heavy domain vocabulary the base model handles poorly
  - With lots of unlabeled text
- Distillation when
  - A large model already works
  - You need its quality cheaper and faster
- Do NOT fine-tune when
  - The problem is missing or changing knowledge ⇒ Retrieval-Augmented Generation (RAG)
  - You have fewer than ~hundreds of good examples (order of magnitude)
  - Prompting was not tried seriously first
  - Traffic is low
    - Provisioned throughput will cost more than the larger model on demand

## 2. Knobs And Best Practices

Each rule prevents a wasted training run or an idle bill.

- Prove the need first
  - Baseline with prompt engineering ([prompt-engineering](prompt-engineering.00index.md))
  - And RAG on a golden set ([evaluations](../04safety/evaluations.00index.md))
- Data
  - Clean, deduplicated, representative
  - Hold out a validation and a test set
  - Strip Personally Identifiable Information (PII)
  - Encrypt with the Customer Managed Key (CMK)
  - Keep the dataset versioned in Simple Storage Service (S3)
- Job
  - `clientRequestToken` for idempotent job creation
  - Service role scoped
    - `customization/train/` read
    - `customization/output/` write
  - `vpcConfig` when data must not leave the Virtual Private Cloud (VPC) path
  - Tags on job and custom model for cost tracking
- Evaluate
  - Compare the custom model against the prompt baseline
    - On the same test set, before serving
- Serving
  - No-commitment provisioned throughput for tests
    - Delete immediately after
  - Commit only after measuring utilization
- Lifecycle
  - Base models get deprecated ⇒ plan re-training on a newer base

## 3. Comparison

| Option | What it is | Strength | Weakness | Choose when |
|---|---|---|---|---|
| Prompt engineering | Instructions + examples at request time | Minutes to iterate; no training; any model | Tokens per call; consistency limits | Always first |
| RAG | Retrieve documents at request time (02rag) | Fresh, citable knowledge; per-document access control | Retrieval quality limits answers; more moving parts | Knowledge is large, private, or changing |
| Fine-tuning | Train weights on labeled pairs | Consistent behavior; shorter prompts; smaller model possible | Data prep; training time; provisioned serving cost; stale knowledge | Stable task/format at high volume |
| Continued pre-training | Train on unlabeled domain text | Domain vocabulary and familiarity | Lots of data; few models; still no fresh facts | Specialized domain language |
| Distillation | Teacher outputs train a student | Large-model quality at small-model cost | Needs a working teacher; per-task | Cost/latency reduction of a working pipeline |

- Deciding variable: is the gap knowledge or behavior?
  - Knowledge → RAG
  - Behavior at high volume → fine-tune or distill
- Pick: prompt engineering, then RAG for knowledge, unless a measured behavior gap remains at volume → fine-tune.

## 4. Failure Modes

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Job fails at validation | Wrong JavaScript Object Notation (JSON) Lines (JSONL) schema for the base model, record too long | Job `Failed`, `failureMessage` | Validate locally against the model's format and limits |
| Access denied | Role cannot read train/ or write output/, or Key Management Service (KMS) | `Failed` with S3/KMS error | Fix role policy, KMS grant, trust conditions |
| Overfitting | Too many epochs, small data | Validation loss rises | Fewer epochs, more data, early stop |
| No improvement | Bad or inconsistent labels | Eval equals baseline | Clean data; more examples of hard cases |

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Knowledge goes stale | Facts baked into weights | Wrong answers after changes | Move facts to RAG |
| Idle provisioned throughput | Forgot to delete | Bill; `InService` with no invocations | Delete; tag; alarm; no-commitment for tests |
| Base model deprecated | Lifecycle `LEGACY` | Lifecycle alarm | Re-train on a newer base |
