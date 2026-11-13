"""Evaluations showcase (boto3), in the order of docs/04.03.evaluations.md.

- client("s3"): write JSONL datasets to evals/datasets/, read results from evals/results/
- client("bedrock"): create_evaluation_job (automated, LLM-as-a-judge, RAG), get/list/stop
- client("bedrock-runtime"): apply_guardrail for the local guardrail eval harness
- Request shapes follow the botocore 1.44 CreateEvaluationJob model; uncertain bits are flagged inline.
- No AWS call at import time.
"""

import json
import threading
import time
import uuid
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any

from app.a04_03_evaluations.config import get_evals_settings
from app.a04_03_evaluations.domain import (
    AUTOMATED_METRICS,
    JUDGE_QUALITY_METRICS,
    RAG_GENERATE_METRICS,
    RAG_RETRIEVE_METRICS,
    ConfusionMatrix,
    EvalJob,
    GuardrailCase,
    GuardrailEvalReport,
    JobKind,
)
from app.shared import aws
from app.shared.config import get_settings
from app.shared.retry import backoff

Json = dict[str, Any]

MAX_DATASET_LINES = 1000  # custom prompt datasets are capped per job (order of magnitude; check the quota page)
TERMINAL = {"Completed", "Failed", "Stopped"}
GEO_PREFIXES = ("us.", "eu.", "apac.", "global.", "jp.", "au.", "ca.", "us-gov.")


def _bedrock() -> Any:
    return aws.client("bedrock")


def _s3() -> Any:
    return aws.client("s3")


def _runtime() -> Any:
    return aws.client("bedrock-runtime")


def _job_name(kind: JobKind) -> str:
    # jobName pattern: [a-z0-9](-*[a-z0-9]){0,62} -> lowercase, digits, hyphens, max 63.
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"a-{kind.value.replace('_', '-')}-{stamp}"[:63]


def _generator() -> str:
    return get_evals_settings().generator_model_id or get_settings().fast_model_id


@lru_cache
def _account_id() -> str:
    return str(aws.client("sts").get_caller_identity()["Account"])


def model_arn(model_id: str) -> str:
    """RAG retrieveAndGenerate needs an ARN: inference profile (geo-prefixed id) or foundation model."""
    if model_id.startswith("arn:"):
        return model_id
    region = get_settings().aws_region
    if model_id.startswith(GEO_PREFIXES):
        return f"arn:aws:bedrock:{region}:{_account_id()}:inference-profile/{model_id}"
    return f"arn:aws:bedrock:{region}::foundation-model/{model_id}"


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


# ================================================================ 1. datasets


def validate_records(records: list[Json], rag: bool) -> None:
    """Cheap local checks before upload: a bad line otherwise fails the whole job minutes later."""
    if not records:
        raise ValueError("empty dataset")
    if len(records) > MAX_DATASET_LINES:
        raise ValueError(f"{len(records)} lines > {MAX_DATASET_LINES} per job; split the dataset")
    key = "conversationTurns" if rag else "prompt"
    bad = [i for i, r in enumerate(records) if key not in r]
    if bad:
        raise ValueError(f"lines missing {key!r}: {bad[:10]}")


def write_dataset(records: list[Json], name: str, rag: bool = False) -> str:
    """Write JSONL (one object per line) to s3://<bucket>/evals/datasets/<name>.jsonl; returns the S3 URI.

    Bucket default encryption (SSE-KMS, 00.05) applies. Never overwrite a dataset a past job used: version names.
    """
    validate_records(records, rag)
    bucket = get_settings().data_bucket
    key = f"{get_evals_settings().datasets_prefix}{name}.jsonl"
    body = "\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n"
    _s3().put_object(Bucket=bucket, Key=key, Body=body.encode(), ContentType="application/jsonl")
    return f"s3://{bucket}/{key}"


# ================================================================ 2. model evaluation jobs


def create_automated_model_eval(
    dataset_uri: str,
    task_type: str = "QuestionAndAnswer",
    metrics: tuple[str, ...] = AUTOMATED_METRICS,
    model_id: str | None = None,
    client_token: str | None = None,
) -> str:
    """Automatic (programmatic) model eval: built-in Accuracy / Robustness / Toxicity, no judge.

    task_type: Summarization | Classification | QuestionAndAnswer | Generation (decides how Accuracy is computed,
    e.g. BERTScore for summaries). Catch: overlap-style scores, needs referenceResponse for Accuracy.
    """
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


def create_judge_model_eval(
    dataset_uri: str,
    metrics: tuple[str, ...] = ("Builtin.Correctness", "Builtin.Completeness", "Builtin.Faithfulness"),
    model_id: str | None = None,
    judge_model_id: str | None = None,
    with_custom_metric: bool = True,
    client_token: str | None = None,
) -> str:
    """LLM-as-a-judge model eval: evaluatorModelConfig names the judge; optional custom rubric metric.

    Allowed built-ins: JUDGE_QUALITY_METRICS + RESPONSIBLE_AI_METRICS. Catch: judge bias (self-preference,
    verbosity) and judge-token cost per metric per item. taskType "General" follows AWS judge examples (verify).
    """
    s = get_evals_settings()
    unknown = [m for m in metrics if m.startswith("Builtin.") and m not in JUDGE_QUALITY_METRICS
               and m not in ("Builtin.Harmfulness", "Builtin.Stereotyping", "Builtin.Refusal")]
    if unknown:
        raise ValueError(f"not judge metrics: {unknown}")
    judge = judge_model_id or s.judge_model_id
    names = list(metrics)
    automated: Json = {
        "evaluatorModelConfig": {"bedrockEvaluatorModels": [{"modelIdentifier": judge}]},
    }
    if with_custom_metric:
        # Custom metric = your rubric. Template variables for model-as-a-judge: {{prompt}}, {{prediction}},
        # {{ground_truth}} (per the custom-metric docs; verify). Always give a rating scale, or the console
        # can't average scores.
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
            "taskType": "General",
            "dataset": {"name": "support-golden", "datasetLocation": {"s3Uri": dataset_uri}},
            "metricNames": names,  # max 25
        }
    ]
    req = _common(JobKind.JUDGE, client_token) | {
        "applicationType": "ModelEvaluation",
        "evaluationConfig": {"automated": automated},
        "inferenceConfig": {"models": [_bedrock_model(model_id or _generator())]},
    }
    return str(_bedrock().create_evaluation_job(**req)["jobArn"])


# ================================================================ 3. RAG evaluation jobs


def create_rag_eval(
    dataset_uri: str,
    retrieve_only: bool = False,
    metrics: tuple[str, ...] | None = None,
    knowledge_base_id: str | None = None,
    generator_model_id: str | None = None,
    judge_model_id: str | None = None,
    client_token: str | None = None,
) -> str:
    """RAG eval against a knowledge base (applicationType RagEvaluation), always judged by an evaluator model.

    retrieve_only=True: retrieveConfig + ContextRelevance/ContextCoverage (cheap, isolates the vector store).
    False: retrieveAndGenerateConfig + Correctness/Faithfulness/... (end to end). taskType is ignored for RAG.
    """
    s = get_evals_settings()
    kb = knowledge_base_id or s.knowledge_base_id
    search = {"vectorSearchConfiguration": {"numberOfResults": s.rag_number_of_results}}  # 1..100
    if retrieve_only:
        kind = JobKind.RAG_RETRIEVE
        names = list(metrics or RAG_RETRIEVE_METRICS)
        kb_config: Json = {"retrieveConfig": {"knowledgeBaseId": kb, "knowledgeBaseRetrievalConfiguration": search}}
    else:
        kind = JobKind.RAG_RETRIEVE_GENERATE
        names = list(metrics or ("Builtin.Correctness", "Builtin.Completeness", "Builtin.Faithfulness",
                                 "Builtin.Helpfulness"))
        unknown = [m for m in names if m not in RAG_GENERATE_METRICS]
        if unknown:
            raise ValueError(f"not documented RAG generate metrics: {unknown}")
        kb_config = {
            "retrieveAndGenerateConfig": {
                "type": "KNOWLEDGE_BASE",  # or EXTERNAL_SOURCES (documents passed inline)
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": kb,
                    "modelArn": model_arn(generator_model_id or _generator()),
                    "retrievalConfiguration": search,
                    "generationConfiguration": {
                        "kbInferenceConfig": {"textInferenceConfig": {"maxTokens": 512, "temperature": 0.0}}
                    },
                },
            }
        }
    req = _common(kind, client_token) | {
        "applicationType": "RagEvaluation",
        "evaluationConfig": {
            "automated": {
                "datasetMetricConfigs": [
                    {
                        "taskType": "QuestionAndAnswer",
                        "dataset": {"name": "rag-golden", "datasetLocation": {"s3Uri": dataset_uri}},
                        "metricNames": names,
                    }
                ],
                "evaluatorModelConfig": {
                    "bedrockEvaluatorModels": [{"modelIdentifier": judge_model_id or s.judge_model_id}]
                },
            }
        },
        "inferenceConfig": {"ragConfigs": [{"knowledgeBaseConfig": kb_config}]},
    }
    return str(_bedrock().create_evaluation_job(**req)["jobArn"])


# ================================================================ 4. lifecycle: get / wait / list / stop


def get_job(job_arn: str) -> Json:
    j = _bedrock().get_evaluation_job(jobIdentifier=job_arn)
    return {
        "job_arn": j["jobArn"],
        "name": j["jobName"],
        "status": j["status"],  # InProgress | Completed | Failed | Stopping | Stopped | Deleting
        "application_type": j.get("applicationType"),
        "job_type": j.get("jobType"),  # Automated | Human
        "output_uri": j["outputDataConfig"]["s3Uri"],
        "failure_messages": j.get("failureMessages", []),
    }


def wait_for_job(job_arn: str, timeout_s: float = 6 * 3600) -> Json:
    """Poll with capped exponential backoff + jitter. Jobs take minutes to hours (size x metrics x judge)."""
    deadline = time.monotonic() + timeout_s
    attempt = 0
    while True:
        job = get_job(job_arn)
        if job["status"] in TERMINAL:
            return job
        if time.monotonic() > deadline:
            raise TimeoutError(f"{job_arn} still {job['status']}")
        time.sleep(max(15.0, backoff(attempt, base=15.0, cap=300.0)))
        attempt += 1


def list_jobs(status: str | None = None, application_type: str | None = None) -> list[Json]:
    """ListEvaluationJobs with nextToken pagination, newest first."""
    kwargs: Json = {"maxResults": 100, "sortBy": "CreationTime", "sortOrder": "Descending"}
    if status:
        kwargs["statusEquals"] = status
    if application_type:
        kwargs["applicationTypeEquals"] = application_type  # ModelEvaluation | RagEvaluation
    out: list[Json] = []
    while True:
        resp = _bedrock().list_evaluation_jobs(**kwargs)
        out += [
            {"job_arn": j["jobArn"], "name": j["jobName"], "status": j["status"], "type": j.get("applicationType")}
            for j in resp.get("jobSummaries", [])
        ]
        token = resp.get("nextToken")
        if not token:
            return out
        kwargs["nextToken"] = token


def stop_job(job_arn: str) -> None:
    """StopEvaluationJob: InProgress -> Stopping -> Stopped. Inference already done is still billed."""
    _bedrock().stop_evaluation_job(jobIdentifier=job_arn)


# ================================================================ 5. results


def _collect_scores(node: Any, sink: dict[str, list[float]]) -> None:
    """Find every {"metricName": ..., "result": number} anywhere in a result line (layout-tolerant)."""
    if isinstance(node, dict):
        name, value = node.get("metricName"), node.get("result")
        if isinstance(name, str) and isinstance(value, (int, float)) and not isinstance(value, bool):
            sink.setdefault(name, []).append(float(value))
        for v in node.values():
            _collect_scores(v, sink)
    elif isinstance(node, list):
        for v in node:
            _collect_scores(v, sink)


def read_results(output_uri: str, job_arn: str) -> dict[str, float]:
    """Read the job's *.jsonl outputs under the output URI and return metric -> mean score.

    Results land under <output>/<jobName>/<jobId>/... (layout not in the API model: verify on a real job), so
    keys are filtered by the job id. Paginated listing: a big job writes many files.
    """
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
                    _collect_scores(json.loads(line), sink)
    return {m: sum(v) / len(v) for m, v in sorted(sink.items()) if v}


# ================================================================ 6. guardrail evaluation harness (local)


def _fired_policies(resp: Json) -> tuple[bool, set[str]]:
    """Predicted block + which policy labels BLOCKED. ANONYMIZE alone intervenes but is not a block."""
    fired: set[str] = set()
    for a in resp.get("assessments", []):
        for t in a.get("topicPolicy", {}).get("topics", []):
            if t["action"] == "BLOCKED":
                fired.add(f"topic:{t['name']}")
        for f in a.get("contentPolicy", {}).get("filters", []):
            if f["action"] == "BLOCKED":
                fired.add(f"content:{f['type']}")
        word = a.get("wordPolicy", {})
        if any(w["action"] == "BLOCKED" for w in word.get("customWords", []) + word.get("managedWordLists", [])):
            fired.add("word")
        sens = a.get("sensitiveInformationPolicy", {})
        if any(p["action"] == "BLOCKED" for p in sens.get("piiEntities", []) + sens.get("regexes", [])):
            fired.add("pii")
        if any(g["action"] == "BLOCKED" for g in a.get("contextualGroundingPolicy", {}).get("filters", [])):
            fired.add("grounding")
    return bool(fired), fired


def run_guardrail_eval(cases: list[GuardrailCase], version: str | None = None) -> GuardrailEvalReport:
    """Labeled cases -> ApplyGuardrail(outputScope=FULL) -> confusion matrix overall + per policy.

    Per policy P: positive = case labeled P and expected blocked; predicted positive = P fired. So a case
    blocked by the WRONG policy counts as FP for that policy and FN for the right one.
    Catch: sequential calls for clarity; add a thread pool + rate limit for big sets.
    """
    s = get_evals_settings()
    ver = version or s.guardrail_version
    report = GuardrailEvalReport(guardrail_version=ver)
    labels = {c.policy for c in cases if c.policy != "benign"}
    results: list[tuple[GuardrailCase, bool, set[str]]] = []
    for c in cases:
        resp = _runtime().apply_guardrail(
            guardrailIdentifier=s.guardrail_id,
            guardrailVersion=ver,
            source=c.source,
            content=[{"text": {"text": c.text}}],
            outputScope="FULL",  # every assessment, incl. non-hits: needed to explain misses
        )
        predicted, fired = _fired_policies(resp)
        report.overall.add(c.expected_blocked, predicted)
        report.total_units += sum(int(v) for v in resp.get("usage", {}).values())
        report.latencies_ms.append(
            sum(int(a.get("invocationMetrics", {}).get("guardrailProcessingLatency", 0)) for a in resp.get("assessments", []))
        )
        labels |= fired
        results.append((c, predicted, fired))
    for label in sorted(labels):
        m = ConfusionMatrix()
        for c, _pred, fired in results:
            m.add(c.policy == label and c.expected_blocked, label in fired)
        report.per_policy[label] = m
    for i, (c, predicted, fired) in enumerate(results):
        if predicted != c.expected_blocked:
            report.misclassified.append(
                {"case": i, "policy": c.policy, "expected": c.expected_blocked, "predicted": predicted,
                 "fired": sorted(fired)}  # no text: eval sets may hold sensitive examples
            )
    return report


# ================================================================ 7. result store adapter


class InMemoryEvalResultStore:
    """EvalResultStore adapter. Prod: DynamoDB (job index) + S3 (raw results), keyed by dataset version."""

    def __init__(self) -> None:
        self._jobs: dict[str, EvalJob] = {}
        self._reports: dict[str, GuardrailEvalReport] = {}
        self._lock = threading.Lock()

    def save_job(self, job: EvalJob) -> None:
        with self._lock:
            self._jobs[job.job_arn] = job

    def get_job(self, job_arn: str) -> EvalJob | None:
        with self._lock:
            return self._jobs.get(job_arn)

    def list_jobs(self) -> list[EvalJob]:
        with self._lock:
            return list(self._jobs.values())

    def save_guardrail_report(self, run_id: str, report: GuardrailEvalReport) -> None:
        with self._lock:
            self._reports[run_id] = report

    def get_guardrail_report(self, run_id: str) -> GuardrailEvalReport | None:
        with self._lock:
            return self._reports.get(run_id)
