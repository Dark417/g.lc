"""Glue Data Quality SDK calls: ruleset CRUD, evaluation run, results, recommendations."""

import time
import uuid
from typing import Any

from botocore.exceptions import ClientError

from app.a03_02_glue_data_quality.config import get_glue_dq_settings
from app.a03_02_glue_data_quality.domain import (
    TERMINAL,
    QualityReport,
    Rule,
    RuleOutcome,
    RunStatus,
    build_ruleset,
)
from app.shared.aws import client
from app.shared.retry import backoff


def _glue() -> Any:
    return client("glue")


def _data_source() -> dict[str, Any]:
    cfg = get_glue_dq_settings()
    return {"GlueTable": {"DatabaseName": cfg.database, "TableName": cfg.table}}


# ---------------------------------------------------------------- 1.4 ruleset (config as code)


def upsert_ruleset(rules: list[Rule], name: str | None = None) -> str:
    """Create the ruleset, or update it when it exists. Returns the DQDL that was stored.

    Catch: names are unique; CreateDataQualityRuleset raises AlreadyExistsException, so we fall back to update.
    TargetTable attaches the ruleset to a catalog table (needed for catalog-based evaluation runs).
    """
    cfg = get_glue_dq_settings()
    name = name or cfg.ruleset_name
    dqdl = build_ruleset(rules)
    try:
        _glue().create_data_quality_ruleset(
            Name=name,
            Description="Corpus metadata checks",
            Ruleset=dqdl,
            TargetTable={"DatabaseName": cfg.database, "TableName": cfg.table},
            ClientToken=str(uuid.uuid5(uuid.NAMESPACE_URL, f"dq/{name}/{dqdl}")),
        )
    except ClientError as e:
        if e.response["Error"]["Code"] != "AlreadyExistsException":
            raise
        _glue().update_data_quality_ruleset(Name=name, Description="Corpus metadata checks", Ruleset=dqdl)
    return dqdl


# ---------------------------------------------------------------- 1.5 evaluation run


def start_evaluation(run_token: str, ruleset_names: list[str] | None = None) -> str:
    """Start a ruleset evaluation run on the catalog table; returns the run id.

    ClientToken makes a retried call return the same run. Catch: the Role is passed to Glue (iam:PassRole),
    and workers/timeout are the only cost caps.
    """
    cfg = get_glue_dq_settings()
    options: dict[str, Any] = {"CloudWatchMetricsEnabled": True}  # metrics per run
    if cfg.results_s3_prefix:
        options["ResultsS3Prefix"] = cfg.results_s3_prefix
    resp = _glue().start_data_quality_ruleset_evaluation_run(
        DataSource=_data_source(),
        Role=cfg.role_arn,
        NumberOfWorkers=cfg.number_of_workers,  # default 5, G.1X workers
        Timeout=cfg.timeout_minutes,  # minutes; default 2880
        ClientToken=run_token,
        RulesetNames=ruleset_names or [cfg.ruleset_name],
        AdditionalRunOptions=options,
    )
    return resp["RunId"]


def _wait(get_run: Any, run_id: str) -> dict[str, Any]:
    end = time.monotonic() + get_glue_dq_settings().poll_deadline_s
    attempt = 0
    while True:
        run = get_run(RunId=run_id)
        if RunStatus(run["Status"]) in TERMINAL:
            return run
        if time.monotonic() >= end:
            raise TimeoutError(f"run {run_id} still {run['Status']} after deadline")
        time.sleep(backoff(attempt, base=2.0, cap=30.0))  # Spark startup takes about a minute: poll slowly
        attempt += 1


def wait_for_evaluation(run_id: str) -> dict[str, Any]:
    """Poll the evaluation run to a terminal state; the dict has Status, ErrorString and ResultIds."""
    return _wait(_glue().get_data_quality_ruleset_evaluation_run, run_id)


# ---------------------------------------------------------------- 1.6 results


def get_rule_outcomes(result_id: str) -> QualityReport:
    """Read one result: per-rule PASS/FAIL/ERROR plus the score Glue computed.

    Catch: Score is a fraction of passing rules, not of rows.
    """
    res = _glue().get_data_quality_result(ResultId=result_id)
    outcomes = [
        RuleOutcome(name=r["Name"], result=r["Result"], message=r.get("EvaluationMessage", ""))
        for r in res.get("RuleResults", [])
    ]
    return QualityReport(result_id=result_id, score=float(res.get("Score", 0.0)), outcomes=outcomes)


def list_results(limit: int = 20) -> list[dict[str, Any]]:
    """List recent results for the table (manual NextToken pagination: list_data_quality_results has no paginator).

    Use for dashboards / trend. Catch: a page may be short; stop only when NextToken is absent.
    """
    out: list[dict[str, Any]] = []
    token: str | None = None
    while len(out) < limit:
        kwargs: dict[str, Any] = {
            "Filter": {"DataSource": _data_source()},
            "MaxResults": min(100, limit - len(out)),
        }
        if token:
            kwargs["NextToken"] = token
        page = _glue().list_data_quality_results(**kwargs)
        out.extend(page.get("Results", []))
        token = page.get("NextToken")
        if not token:
            break
    return out


# ---------------------------------------------------------------- recommendations


def start_recommendation(run_token: str) -> str:
    """Ask Glue to profile the table and propose DQDL rules; returns the run id.

    Catch: it scans the data (cost); treat the output as a draft and review thresholds.
    """
    cfg = get_glue_dq_settings()
    resp = _glue().start_data_quality_rule_recommendation_run(
        DataSource=_data_source(),
        Role=cfg.role_arn,
        NumberOfWorkers=cfg.number_of_workers,
        Timeout=cfg.timeout_minutes,
        ClientToken=run_token,
        # CreatedRulesetName="a-docs-recommended",  # optionally save the proposal as a ruleset
    )
    return resp["RunId"]


def wait_for_recommendation(run_id: str) -> str:
    """Poll the recommendation run; return the recommended DQDL (empty if the run failed)."""
    run = _wait(_glue().get_data_quality_rule_recommendation_run, run_id)
    return run.get("RecommendedRuleset", "") if run["Status"] == RunStatus.SUCCEEDED else ""
