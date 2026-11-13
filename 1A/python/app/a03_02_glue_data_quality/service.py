"""Use case: quality gate before ingestion."""

from dataclasses import dataclass

from app.a03_02_glue_data_quality.config import get_glue_dq_settings
from app.a03_02_glue_data_quality.domain import QualityReport, RunStatus
from app.a03_02_glue_data_quality.infra import get_rule_outcomes, start_evaluation, wait_for_evaluation


@dataclass
class GateDecision:
    passed: bool
    run_id: str
    status: str
    report: QualityReport | None = None
    reason: str = ""


def evaluate_gate(run_token: str) -> GateDecision:
    """Run the ruleset and decide: score >= gate_min_score and no ERROR rule => ingestion may continue.

    Catch: a FAILED/TIMEOUT run is not a pass; run_token keeps retries idempotent.
    """
    run_id = start_evaluation(run_token)
    run = wait_for_evaluation(run_id)
    status = run["Status"]
    if status != RunStatus.SUCCEEDED or not run.get("ResultIds"):
        return GateDecision(False, run_id, status, reason=run.get("ErrorString", "no result"))
    report = get_rule_outcomes(run["ResultIds"][0])
    ok = report.score >= get_glue_dq_settings().gate_min_score and not any(o.result == "ERROR" for o in report.outcomes)
    return GateDecision(ok, run_id, status, report, reason="" if ok else f"{len(report.failed)} rule(s) not passing")
