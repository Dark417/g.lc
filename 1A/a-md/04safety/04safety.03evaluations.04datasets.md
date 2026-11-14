# 04safety.03evaluations.04datasets Evaluation Datasets

> The JavaScript Object Notation Lines (JSONL) shapes for model and Retrieval-Augmented Generation (RAG) eval, built-in datasets, and what makes a dataset worth trusting.

## Index

- [1. Model Eval JSONL](#1-model-eval-jsonl)
- [2. RAG Eval JSONL](#2-rag-eval-jsonl)
- [3. Size and Upload](#3-size-and-upload)
- [4. Built-In Datasets](#4-built-in-datasets)
- [5. What Makes a Good Set](#5-what-makes-a-good-set)

Back to [00index](04safety.03evaluations.00index.md).

## 1. Model Eval JSONL

One object per line.

- `{"prompt": "...", "referenceResponse": "...", "category": "billing"}`
- `referenceResponse`
  - optional for some metrics
  - required for Correctness-style comparisons and Accuracy
- `category` groups scores in the report (per-slice analysis)
- Bring Your Own Inference (BYOI) adds `"modelResponses": [{"response": "...", "modelIdentifier": "my-model"}]`

```python
# app/domain/_04safety_03evaluations.py
@dataclass(frozen=True)
class EvalCase:
    """Model-eval line: {"prompt", "referenceResponse", "category"} (+ "modelResponses" for BYOI)."""

    prompt: str
    reference: str = ""
    category: str = ""

    def to_record(self) -> Json:
        rec: Json = {"prompt": self.prompt}
        if self.reference:
            rec["referenceResponse"] = self.reference  # needed by Accuracy / Correctness-style metrics
        if self.category:
            rec["category"] = self.category  # groups scores in the report
        return rec
```

## 2. RAG Eval JSONL

A conversation-turn shape.

- `{"conversationTurns": [{"prompt": {"content": [{"text": "..."}]}, "referenceResponses": [{"content": [{"text": "..."}]}]}]}`
- One turn per line today
  - multi-turn: check the docs

```python
# app/domain/_04safety_03evaluations.py
@dataclass(frozen=True)
class RagCase:
    prompt: str
    references: tuple[str, ...] = ()  # ContextCoverage and Correctness need at least one

    def to_record(self) -> Json:
        turn: Json = {"prompt": {"content": [{"text": self.prompt}]}}
        if self.references:
            turn["referenceResponses"] = [{"content": [{"text": r}]} for r in self.references]
        return {"conversationTurns": [turn]}
```

## 3. Size and Upload

- Custom datasets are capped per job
  - order of magnitude: 1,000 prompts; check the quota page
- Validate locally before upload
  - a bad line otherwise fails the whole job minutes later

```python
# app/infra/_04safety_03evaluations.py
MAX_DATASET_LINES = 1000  # order of magnitude; check the quota page


def validate_records(records: list[Json], rag: bool) -> None:
    if not records:
        raise ValueError("empty dataset")
    if len(records) > MAX_DATASET_LINES:
        raise ValueError(f"{len(records)} lines > {MAX_DATASET_LINES} per job; split the dataset")
    key = "conversationTurns" if rag else "prompt"
    bad = [i for i, r in enumerate(records) if key not in r]
    if bad:
        raise ValueError(f"lines missing {key!r}: {bad[:10]}")


def write_dataset(records: list[Json], name: str, rag: bool = False) -> str:
    """Never overwrite a dataset a past job used: version names. Bucket SSE-KMS (base_data_bucket) applies."""
    validate_records(records, rag)
    bucket = get_settings().data_bucket
    key = f"{get_evals_settings().datasets_prefix}{name}.jsonl"
    body = "\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n"
    _s3().put_object(Bucket=bucket, Key=key, Body=body.encode(), ContentType="application/jsonl")
    return f"s3://{bucket}/{key}"
```

## 4. Built-In Datasets

Available for automatic eval.

- `Builtin.Bold`
- `Builtin.BoolQ`
- `Builtin.NaturalQuestions`
- `Builtin.Gigaword`
- `Builtin.RealToxicityPrompts`
- `Builtin.TriviaQA`
- `Builtin.T-Rex`
- `Builtin.WomensEcommerceClothingReviews`
- `Builtin.Wikitext2`

## 5. What Makes a Good Set

- Real user questions, not invented ones
  - sampled from logs, Personally Identifiable Information (PII) scrubbed per [04safety.02pii-redaction](04safety.02pii-redaction.00index.md)
- Hard cases and known failures, not only happy paths
- Answerable and unanswerable questions
  - tests refusal and faithfulness
- Versioned in Simple Storage Service (S3) with the results that used it
- Separate dev and test sets
  - evaluating on the examples used to write the prompt overfits
