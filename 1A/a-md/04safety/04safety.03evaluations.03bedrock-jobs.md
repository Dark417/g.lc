# 04safety.03evaluations.03bedrock-jobs Bedrock Evaluation Jobs

> Job types and metric names, the `CreateEvaluationJob` request, lifecycle, results, and cost.

## Index

- [1. Job Types](#1-job-types)
- [2. Custom Metrics and Bring Your Own Inference (BYOI)](#2-custom-metrics-and-bring-your-own-inference-byoi)
- [3. Request Skeleton](#3-request-skeleton)
  - [3.1 Code: Common Fields](#31-code-common-fields)
  - [3.2 Code: Automatic Model Eval](#32-code-automatic-model-eval)
  - [3.3 Code: Judge Model Eval With Custom Metric](#33-code-judge-model-eval-with-custom-metric)
- [4. Lifecycle](#4-lifecycle)
- [5. Results](#5-results)
- [6. Orchestration Service](#6-orchestration-service)
- [7. Cost](#7-cost)

Back to [00index](04safety.03evaluations.00index.md).
Retrieval-Augmented Generation (RAG) job code: [06rag-eval](04safety.03evaluations.06rag-eval.md).

## 1. Job Types

`applicationType` picks model vs RAG; the scoring method picks the metric set.

| Job | `applicationType` | Scoring | Metric names (`metricNames`) | Needs |
|---|---|---|---|---|
| Automatic model eval | `ModelEvaluation` | built-in algorithms | `Builtin.Accuracy`, `Builtin.Robustness`, `Builtin.Toxicity` | `taskType`: Summarization, Classification, QuestionAndAnswer, Generation |
| Large Language Model (LLM)-as-a-judge model eval | `ModelEvaluation` | judge model | quality: `Builtin.Correctness`, `Completeness`, `Faithfulness`, `Helpfulness`, `Coherence`, `Relevance`, `FollowingInstructions`, `ProfessionalStyleAndTone`; responsible Artificial Intelligence (AI): `Harmfulness`, `Stereotyping`, `Refusal` | `evaluatorModelConfig.bedrockEvaluatorModels` |
| Human model eval | `ModelEvaluation` | your work team (SageMaker Ground Truth flow) | your custom metric names | `human.humanWorkflowConfig.flowDefinitionArn` |
| RAG eval, retrieve only | `RagEvaluation` | judge model | `Builtin.ContextRelevance`, `Builtin.ContextCoverage` (coverage needs references) | `ragConfigs[].knowledgeBaseConfig.retrieveConfig` |
| RAG eval, retrieve + generate | `RagEvaluation` | judge model | `Builtin.Correctness`, `Completeness`, `Helpfulness`, `LogicalCoherence`, `Faithfulness`, `Harmfulness`, `Stereotyping`, `Refusal`; citation metrics `CitationPrecision`, `CitationCoverage` (verify) | `ragConfigs[].knowledgeBaseConfig.retrieveAndGenerateConfig` |

```python
# app/domain/_04safety_03evaluations.py
# Metric names as listed in the CreateEvaluationJob API reference (botocore 1.44 doc text).
AUTOMATED_METRICS = ("Builtin.Accuracy", "Builtin.Robustness", "Builtin.Toxicity")
JUDGE_QUALITY_METRICS = (
    "Builtin.Correctness", "Builtin.Completeness", "Builtin.Faithfulness", "Builtin.Helpfulness",
    "Builtin.Coherence", "Builtin.Relevance", "Builtin.FollowingInstructions", "Builtin.ProfessionalStyleAndTone",
)
RESPONSIBLE_AI_METRICS = ("Builtin.Harmfulness", "Builtin.Stereotyping", "Builtin.Refusal")
RAG_RETRIEVE_METRICS = ("Builtin.ContextRelevance", "Builtin.ContextCoverage")
# Announced later; not in the API doc text checked: verify before relying on them.
RAG_CITATION_METRICS = ("Builtin.CitationPrecision", "Builtin.CitationCoverage")
```

## 2. Custom Metrics and Bring Your Own Inference (BYOI)

Custom metrics add your rubric; BYOI lets Bedrock judge outputs it did not generate.

- Custom metrics (judge and RAG)
  - `customMetricConfig.customMetrics[].customMetricDefinition`
  - `name`
  - `instructions`: rubric prompt with input variables
  - `ratingScale[]`: `definition` + `value.floatValue` or `stringValue`
- Bring your own inference (BYOI)
  - Model eval
    - `inferenceConfig.models[].precomputedInferenceSource.inferenceSourceIdentifier`
    - + `modelResponses` in the dataset
  - RAG eval
    - `precomputedRagSourceConfig`
    - + retrieved passages / output in the dataset
  - Use: evaluate a non-Bedrock model or your own RAG pipeline with Bedrock's judges
  - Shape only; not coded in the repo

## 3. Request Skeleton

`bedrock.create_evaluation_job` takes these top-level parts.

- `jobName`
  - lowercase, digits, hyphens; ≤ 63
- `roleArn`, `applicationType`
- `evaluationConfig.automated.datasetMetricConfigs[]`
  - `taskType`
  - `dataset{name, datasetLocation.s3Uri}`
  - `metricNames[]` (≤ 25)
- `inferenceConfig`
  - `models[].bedrockModel{modelIdentifier, inferenceParams (JSON string)}`
  - or `ragConfigs[]`
- `outputDataConfig.s3Uri`
- optional `customerEncryptionKeyId`, `clientRequestToken`

### 3.1 Code: Common Fields

```python
# app/infra/_04safety_03evaluations.py
def _job_name(kind: JobKind) -> str:
    # jobName pattern: [a-z0-9](-*[a-z0-9]){0,62} -> lowercase, digits, hyphens, max 63.
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"a-{kind.value.replace('_', '-')}-{stamp}"[:63]


def _common(kind: JobKind, client_token: str | None) -> Json:
    s = get_evals_settings()
    return {
        "jobName": _job_name(kind),
        "roleArn": s.role_arn,  # a-bedrock-eval; caller needs iam:PassRole
        "customerEncryptionKeyId": s.kms_key_id,  # encrypts job data + results
        "clientRequestToken": client_token or str(uuid.uuid4()),  # idempotent create on retry
        "outputDataConfig": {"s3Uri": f"s3://{get_settings().data_bucket}/{s.results_prefix}"},
        "jobTags": [{"key": "Component", "value": "04.03"}],
    }


def _bedrock_model(model_id: str) -> Json:
    # inferenceParams is a JSON STRING, not an object. Use production settings; temperature 0 for regression.
    params = {"inferenceConfig": {"maxTokens": 512, "temperature": 0.0}}
    return {"bedrockModel": {"modelIdentifier": model_id, "inferenceParams": json.dumps(params)}}
```

### 3.2 Code: Automatic Model Eval

- Built-in Accuracy / Robustness / Toxicity, no judge
- `task_type` decides how Accuracy is computed (e.g. BERTScore for summaries)

```python
# app/infra/_04safety_03evaluations.py
def create_automated_model_eval(
    dataset_uri: str,
    task_type: str = "QuestionAndAnswer",  # Summarization | Classification | QuestionAndAnswer | Generation
    metrics: tuple[str, ...] = AUTOMATED_METRICS,
    model_id: str | None = None,
    client_token: str | None = None,
) -> str:
    req = _common(JobKind.AUTOMATED, client_token) | {
        "applicationType": "ModelEvaluation",
        "evaluationConfig": {
            "automated": {
                "datasetMetricConfigs": [
                    {
                        "taskType": task_type,
                        "dataset": {"name": "custom-qa", "datasetLocation": {"s3Uri": dataset_uri}},
                        "metricNames": list(metrics),
                    }
                ]
            }
        },
        "inferenceConfig": {"models": [_bedrock_model(model_id or _generator())]},  # 1 model for automated
    }
    return str(_bedrock().create_evaluation_job(**req)["jobArn"])
```

- Catch
  - Overlap-style scores
  - needs `referenceResponse` for Accuracy

### 3.3 Code: Judge Model Eval With Custom Metric

- `evaluatorModelConfig` names the judge
- Custom metric `BankingTone` = your rubric
  - template variables for model-as-a-judge: `{{prompt}}`, `{{prediction}}`, `{{ground_truth}}` (verify)
  - always give a rating scale, or the console can't average scores

```python
# app/infra/_04safety_03evaluations.py  (create_judge_model_eval, trimmed)
automated: Json = {
    "evaluatorModelConfig": {"bedrockEvaluatorModels": [{"modelIdentifier": judge}]},
}
if with_custom_metric:
    names.append("BankingTone")
    automated["customMetricConfig"] = {
        "customMetrics": [
            {
                "customMetricDefinition": {
                    "name": "BankingTone",
                    "instructions": (
                        "You are grading a bank support answer.\n"
                        "Question: {{prompt}}\nAnswer: {{prediction}}\n"
                        "Rate whether the answer is polite, avoids investment advice, and tells the customer "
                        "the next step."
                    ),
                    "ratingScale": [
                        {"definition": "Fails one or more criteria", "value": {"floatValue": 0.0}},
                        {"definition": "Meets all criteria", "value": {"floatValue": 1.0}},
                    ],
                }
            }
        ],
        "evaluatorModelConfig": {"bedrockEvaluatorModels": [{"modelIdentifier": judge}]},
    }
automated["datasetMetricConfigs"] = [
    {
        "taskType": "General",  # follows AWS judge examples (verify)
        "dataset": {"name": "support-golden", "datasetLocation": {"s3Uri": dataset_uri}},
        "metricNames": names,  # max 25
    }
]
```

- Catch
  - The function rejects `Builtin.*` names outside the judge + responsible-AI lists
  - Judge bias and judge-token cost per metric per item: [05llm-judge](04safety.03evaluations.05llm-judge.md)

## 4. Lifecycle

→ `InProgress`  
→ `Completed` | `Failed` (`failureMessages`) | `Stopping` → `Stopped`

- `StopEvaluationJob` to cancel
  - inference already done is still billed
- Jobs take minutes to hours (size × metrics × judge)

```python
# app/infra/_04safety_03evaluations.py
def wait_for_job(job_arn: str, timeout_s: float = 6 * 3600) -> Json:
    """Poll with capped exponential backoff + jitter."""
    deadline = time.monotonic() + timeout_s
    attempt = 0
    while True:
        job = get_job(job_arn)  # status, output_uri, failure_messages
        if job["status"] in TERMINAL:  # Completed | Failed | Stopped
            return job
        if time.monotonic() > deadline:
            raise TimeoutError(f"{job_arn} still {job['status']}")
        time.sleep(max(15.0, backoff(attempt, base=15.0, cap=300.0)))
        attempt += 1


def list_jobs(status: str | None = None, application_type: str | None = None) -> list[Json]:
    kwargs: Json = {"maxResults": 100, "sortBy": "CreationTime", "sortOrder": "Descending"}
    if status:
        kwargs["statusEquals"] = status
    if application_type:
        kwargs["applicationTypeEquals"] = application_type  # ModelEvaluation | RagEvaluation
    out: list[Json] = []
    while True:  # nextToken pagination, newest first
        resp = _bedrock().list_evaluation_jobs(**kwargs)
        out += [
            {"job_arn": j["jobArn"], "name": j["jobName"], "status": j["status"], "type": j.get("applicationType")}
            for j in resp.get("jobSummaries", [])
        ]
        token = resp.get("nextToken")
        if not token:
            return out
        kwargs["nextToken"] = token
```

## 5. Results

Results land in Simple Storage Service (S3) under the output Uniform Resource Identifier (URI); the parser averages scores per metric.

- Layout `<output>/<jobName>/<jobId>/...` is not in the Application Programming Interface (API) model
  - keys are filtered by job id; verify on a real job
- Parser finds every `{"metricName": ..., "result": number}` anywhere in a line
- Paginated listing: a big job writes many files

```python
# app/infra/_04safety_03evaluations.py
def read_results(output_uri: str, job_arn: str) -> dict[str, float]:
    bucket, _, prefix = output_uri.removeprefix("s3://").partition("/")
    job_id = job_arn.rsplit("/", 1)[-1]
    sink: dict[str, list[float]] = {}
    paginator = _s3().get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if job_id not in key or not key.endswith(".jsonl"):
                continue
            body = _s3().get_object(Bucket=bucket, Key=key)["Body"].read().decode()
            for line in body.splitlines():
                if line.strip():
                    _collect_scores(json.loads(line), sink)  # layout-tolerant walk
    return {m: sum(v) / len(v) for m, v in sorted(sink.items()) if v}
```

## 6. Orchestration Service

Dataset → job → stored scores.

- The dataset name doubles as the idempotency token
  - retrying the same request does not start a second job
- `refresh` reads and stores mean scores once the job is Completed

```python
# app/service/_04safety_03evaluations/__init__.py
class EvalService:
    def __init__(self, store: EvalResultStore) -> None:
        self._store = store

    def start_model_eval(self, cases: list[EvalCase], dataset_name: str, judge: bool = True) -> EvalJob:
        uri = infra.write_dataset([c.to_record() for c in cases], dataset_name)
        if judge:
            arn, kind = infra.create_judge_model_eval(uri, client_token=f"judge-{dataset_name}"), JobKind.JUDGE
        else:
            arn, kind = infra.create_automated_model_eval(uri, client_token=f"auto-{dataset_name}"), JobKind.AUTOMATED
        job = EvalJob(arn, kind, uri, infra.get_job(arn)["output_uri"])
        self._store.save_job(job)
        return job

    def refresh(self, job_arn: str) -> EvalJob:
        info = infra.get_job(job_arn)
        job = self._store.get_job(job_arn) or EvalJob(job_arn, JobKind.JUDGE, "", info["output_uri"])
        scores = infra.read_results(info["output_uri"], job_arn) if info["status"] == "Completed" else {}
        job = replace(job, status=info["status"], failure_messages=tuple(info["failure_messages"]), scores=scores)
        self._store.save_job(job)
        return job
```

## 7. Cost

- You pay model inference for the generator and the judge at on-demand rates
  - no separate eval fee per the pricing page, 2026-11; verify
- Judge tokens ≈ (prompt + response + reference + rubric) × metrics × items
  - metrics multiply cost
