# glue-data-quality Recommendations And Results

> Read per-rule outcomes and the score, list history for trends, and bootstrap rules with a recommendation run.

## Index

- [1. Results](#1-results)
  - [1.1 Rule Outcomes And Score](#11-rule-outcomes-and-score)
  - [1.2 Result History](#12-result-history)
- [2. Recommendations](#2-recommendations)
- [3. Metrics And Anomaly Detection](#3-metrics-and-anomaly-detection)

## 1. Results

Each run produces result ids; each result holds per-rule outcomes and an overall score.

### 1.1 Rule Outcomes And Score

- Per-rule result: `Pass | Fail | Error`
- Evaluated metrics per rule
- Overall score
  - A fraction of passing rules, not of rows

```python
# app/domain/_03data_02glue_data_quality.py
@dataclass
class QualityReport:
    result_id: str
    score: float  # 0..1, fraction of passing rules (as reported by Glue)
    outcomes: list[RuleOutcome] = field(default_factory=list)

    @property
    def failed(self) -> list[RuleOutcome]:
        return [o for o in self.outcomes if o.result != "PASS"]
```

```python
# app/infra/_03data_02glue_data_quality.py
def get_rule_outcomes(result_id: str) -> QualityReport:
    res = _glue().get_data_quality_result(ResultId=result_id)
    outcomes = [
        RuleOutcome(name=r["Name"], result=r["Result"], message=r.get("EvaluationMessage", ""))
        for r in res.get("RuleResults", [])
    ]
    return QualityReport(result_id=result_id, score=float(res.get("Score", 0.0)), outcomes=outcomes)
```

- **Catch**: one failing rule on 1% of rows and one on 90% weigh the same in the score

### 1.2 Result History

Listing past results feeds dashboards and trend alerts.

- `list_data_quality_results` has no paginator
  - Manual `NextToken` loop

```python
# app/infra/_03data_02glue_data_quality.py
def list_results(limit: int = 20) -> list[dict[str, Any]]:
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
        if not token:  # a page may be short; stop only when NextToken is absent
            break
    return out
```

- **Catch**: track score per run id with the Knowledge Base (KB) data-source version
  - Otherwise you cannot tie a retrieval drop to a data release

## 2. Recommendations

A recommendation run profiles the table and proposes a Data Quality Definition Language (DQDL) ruleset.

- `StartDataQualityRuleRecommendationRun` returns a DQDL ruleset
- Workflow
  - Start from recommendations
  - Prune noisy rules
  - Add business rules by hand
- Recommendations overfit the sample
  - Tune thresholds with domain knowledge

```python
# app/infra/_03data_02glue_data_quality.py
def start_recommendation(run_token: str) -> str:
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
    """Return the recommended DQDL (empty if the run failed)."""
    run = _wait(_glue().get_data_quality_rule_recommendation_run, run_id)
    return run.get("RecommendedRuleset", "") if run["Status"] == RunStatus.SUCCEEDED else ""
```

- **Catch**: it scans the data (cost)
  - Treat the output as a draft and review thresholds

## 3. Metrics And Anomaly Detection

CloudWatch metrics turn each run into an alarmable signal.

- Turn on `CloudWatchMetricsEnabled` (see [03 Evaluation Runs](glue-data-quality.03evaluation-runs.md#2-starting-a-run))
  - Metrics per run for dashboards and alarms
  - Alarm on a failing score
- Anomaly detection is a separate feature built on history
  - Not coded here

```python
# app/api/_03data_02glue_data_quality.py
@router.get("/results")
def results(limit: int = 20) -> list[dict[str, Any]]:
    return list_results(limit)
```

- **Catch**: page on trend, not single dips
