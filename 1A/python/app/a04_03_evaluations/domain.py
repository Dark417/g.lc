"""Domain for evaluations: dataset records, job records, confusion matrix, result-store port. No boto3 here.

- EvalCase / RagCase know their exact Bedrock dataset JSONL shape (to_record).
- ConfusionMatrix + GuardrailEvalReport = how a guardrail is scored as a set of binary classifiers.
- EvalResultStore is a port: evaluation results are data you keep and compare over time.
"""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Protocol

Json = dict[str, Any]

# ================================================================ dataset records


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


@dataclass(frozen=True)
class RagCase:
    """RAG-eval line: {"conversationTurns": [{"prompt": {...}, "referenceResponses": [...]}]}."""

    prompt: str
    references: tuple[str, ...] = ()  # ContextCoverage and Correctness need at least one

    def to_record(self) -> Json:
        turn: Json = {"prompt": {"content": [{"text": self.prompt}]}}
        if self.references:
            turn["referenceResponses"] = [{"content": [{"text": r}]} for r in self.references]
        return {"conversationTurns": [turn]}


# ================================================================ jobs


class JobKind(StrEnum):
    AUTOMATED = "automated"  # built-in algorithms: Accuracy, Robustness, Toxicity
    JUDGE = "judge"  # LLM-as-a-judge model evaluation
    RAG_RETRIEVE = "rag_retrieve"  # retrieve-only: ContextRelevance, ContextCoverage
    RAG_RETRIEVE_GENERATE = "rag_retrieve_generate"  # Correctness, Faithfulness, ...


# Metric names as listed in the CreateEvaluationJob API reference (botocore 1.44 doc text).
AUTOMATED_METRICS = ("Builtin.Accuracy", "Builtin.Robustness", "Builtin.Toxicity")
JUDGE_QUALITY_METRICS = (
    "Builtin.Correctness",
    "Builtin.Completeness",
    "Builtin.Faithfulness",
    "Builtin.Helpfulness",
    "Builtin.Coherence",
    "Builtin.Relevance",
    "Builtin.FollowingInstructions",
    "Builtin.ProfessionalStyleAndTone",
)
RESPONSIBLE_AI_METRICS = ("Builtin.Harmfulness", "Builtin.Stereotyping", "Builtin.Refusal")
RAG_RETRIEVE_METRICS = ("Builtin.ContextRelevance", "Builtin.ContextCoverage")
RAG_GENERATE_METRICS = (
    "Builtin.Correctness",
    "Builtin.Completeness",
    "Builtin.Helpfulness",
    "Builtin.LogicalCoherence",
    "Builtin.Faithfulness",
    "Builtin.Harmfulness",
    "Builtin.Stereotyping",
    "Builtin.Refusal",
)
# Announced later; not in the API doc text checked: verify before relying on them.
RAG_CITATION_METRICS = ("Builtin.CitationPrecision", "Builtin.CitationCoverage")


@dataclass(frozen=True)
class EvalJob:
    job_arn: str
    kind: JobKind
    dataset_uri: str
    output_uri: str
    status: str = "InProgress"  # InProgress | Completed | Failed | Stopping | Stopped | Deleting
    failure_messages: tuple[str, ...] = ()
    scores: dict[str, float] = field(default_factory=dict)  # metric -> mean score (0..1 for built-ins)


# ================================================================ guardrail evaluation


@dataclass(frozen=True)
class GuardrailCase:
    text: str
    source: str  # INPUT | OUTPUT
    expected_blocked: bool
    policy: str = "benign"  # label: topic:InvestmentAdvice | content:PROMPT_ATTACK | pii | word | benign


@dataclass
class ConfusionMatrix:
    tp: int = 0  # should block, blocked
    fp: int = 0  # should pass, blocked   (legitimate traffic broken)
    fn: int = 0  # should block, passed   (miss)
    tn: int = 0  # should pass, passed

    def add(self, expected: bool, predicted: bool) -> None:
        if expected and predicted:
            self.tp += 1
        elif predicted:
            self.fp += 1
        elif expected:
            self.fn += 1
        else:
            self.tn += 1

    @property
    def precision(self) -> float:
        return self.tp / (self.tp + self.fp) if self.tp + self.fp else 0.0

    @property
    def recall(self) -> float:
        return self.tp / (self.tp + self.fn) if self.tp + self.fn else 0.0

    @property
    def false_positive_rate(self) -> float:
        return self.fp / (self.fp + self.tn) if self.fp + self.tn else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if p + r else 0.0

    def as_dict(self) -> dict[str, float]:
        return {
            "tp": self.tp,
            "fp": self.fp,
            "fn": self.fn,
            "tn": self.tn,
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "fpr": round(self.false_positive_rate, 4),
            "f1": round(self.f1, 4),
        }


@dataclass
class GuardrailEvalReport:
    guardrail_version: str
    overall: ConfusionMatrix = field(default_factory=ConfusionMatrix)
    per_policy: dict[str, ConfusionMatrix] = field(default_factory=dict)
    misclassified: list[Json] = field(default_factory=list)  # case index + expected/predicted + fired policies
    total_units: int = 0  # text units billed across policies
    latencies_ms: list[int] = field(default_factory=list)

    def p95_latency_ms(self) -> int:
        if not self.latencies_ms:
            return 0
        s = sorted(self.latencies_ms)
        return s[min(len(s) - 1, int(0.95 * len(s)))]

    def passes(self, min_recall: float, max_fpr: float) -> bool:
        """Release gate: every labeled policy meets recall, and overall FPR stays within budget."""
        policies_ok = all(m.recall >= min_recall for p, m in self.per_policy.items() if p != "benign" and m.tp + m.fn)
        return policies_ok and self.overall.false_positive_rate <= max_fpr


# ================================================================ port


class EvalResultStore(Protocol):
    def save_job(self, job: EvalJob) -> None: ...

    def get_job(self, job_arn: str) -> EvalJob | None: ...

    def list_jobs(self) -> list[EvalJob]: ...

    def save_guardrail_report(self, run_id: str, report: GuardrailEvalReport) -> None: ...

    def get_guardrail_report(self, run_id: str) -> GuardrailEvalReport | None: ...
