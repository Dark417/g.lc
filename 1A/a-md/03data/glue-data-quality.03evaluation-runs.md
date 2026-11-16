# glue-data-quality Evaluation Runs

> Where rules run, how to start and poll an evaluation run, and how the score becomes an ingestion gate.

## Index

- [1. Where Rules Run](#1-where-rules-run)
- [2. Starting A Run](#2-starting-a-run)
- [3. Polling](#3-polling)
- [4. Quality Gate](#4-quality-gate)

## 1. Where Rules Run

Rules run either standalone against a catalog table or inside an Extract, Transform, Load (ETL) job.

| Mode | How | Strength | Choose for |
|---|---|---|---|
| Catalog-attached ruleset | `StartDataQualityRulesetEvaluationRun` or a schedule | No ETL code | Audit and gates |
| In an ETL job | `EvaluateDataQuality` transform in the Glue script | Routes failing rows out before writing | Row routing |

- Both emit the same result object
- Row-level outcomes only come from the ETL transform
- Rule of thumb: standalone for audit and gates, in-job for row routing

```python
# illustrative (no repo code): EvaluateDataQuality inside a Glue ETL script
from awsgluedq.transforms import EvaluateDataQuality

outcomes = EvaluateDataQuality().process_rows(
    frame=docs_frame,
    ruleset=dqdl,
    publishing_options={"dataQualityEvaluationContext": "docs", "enableDataQualityCloudWatchMetrics": True},
)  # returns rowLevelOutcomes / ruleOutcomes frames to split good and bad rows
```

- **Catch**: choose on whether you must stop or route rows before writing

## 2. Starting A Run

Workers and timeout are the only cost caps, and `ClientToken` keeps retries to one run.

- `Role` is passed to Glue
  - The caller needs `iam:PassRole` on that role only
- `NumberOfWorkers`: default 5 (G.1X)
- `Timeout`: minutes, default 2,880 (48 h)
- `CloudWatchMetricsEnabled` ⇒ metrics per run for alarms
- `ResultsS3Prefix` ⇒ optional Simple Storage Service (S3) copy of results

```python
# app/infra/_03data_02glue_data_quality.py
def start_evaluation(run_token: str, ruleset_names: list[str] | None = None) -> str:
    cfg = get_glue_dq_settings()
    options: dict[str, Any] = {"CloudWatchMetricsEnabled": True}  # metrics per run
    if cfg.results_s3_prefix:
        options["ResultsS3Prefix"] = cfg.results_s3_prefix
    resp = _glue().start_data_quality_ruleset_evaluation_run(
        DataSource=_data_source(),
        Role=cfg.role_arn,  # needs iam:PassRole
        NumberOfWorkers=cfg.number_of_workers,  # default 5, G.1X workers
        Timeout=cfg.timeout_minutes,  # minutes; default 2880
        ClientToken=run_token,  # a retried call returns the same run
        RulesetNames=ruleset_names or [cfg.ruleset_name],
        AdditionalRunOptions=options,
    )
    return resp["RunId"]
```

- **Catch**: the role must read the S3 prefix and decrypt with the Customer Managed Key (CMK)
  - Else the run fails immediately with an `ErrorString`
- **Catch**: scope the service role to the data prefix and CMK only

## 3. Polling

Spark startup takes about a minute, so the poll starts slow and stays slow.

- Terminal states: `STOPPED`, `SUCCEEDED`, `FAILED`, `TIMEOUT`
- The same `_wait` serves evaluation and recommendation runs

```python
# app/infra/_03data_02glue_data_quality.py
def _wait(get_run: Any, run_id: str) -> dict[str, Any]:
    end = time.monotonic() + get_glue_dq_settings().poll_deadline_s
    attempt = 0
    while True:
        run = get_run(RunId=run_id)
        if RunStatus(run["Status"]) in TERMINAL:
            return run
        if time.monotonic() >= end:
            raise TimeoutError(f"run {run_id} still {run['Status']} after deadline")
        time.sleep(backoff(attempt, base=2.0, cap=30.0))  # Spark startup ~1 min: poll slowly
        attempt += 1


def wait_for_evaluation(run_id: str) -> dict[str, Any]:
    """The dict has Status, ErrorString and ResultIds."""
    return _wait(_glue().get_data_quality_ruleset_evaluation_run, run_id)
```

- **Catch**: Spark startup + Data Processing Unit (DPU)-hour billing ⇒ never a per-record or request-time check

## 4. Quality Gate

The gate passes only when the run succeeded, the score clears the threshold, and no rule errored.

→ Start the run with the caller's idempotency key  
→ Wait to a terminal state  
→ Read the first result  
→ `score >= gate_min_score` and no `ERROR` rule ⇒ ingestion may continue

```python
# app/service/_03data_02glue_data_quality.py
def evaluate_gate(run_token: str) -> GateDecision:
    run_id = start_evaluation(run_token)
    run = wait_for_evaluation(run_id)
    status = run["Status"]
    if status != RunStatus.SUCCEEDED or not run.get("ResultIds"):
        # a FAILED/TIMEOUT run is not a pass
        return GateDecision(False, run_id, status, reason=run.get("ErrorString", "no result"))
    report = get_rule_outcomes(run["ResultIds"][0])
    ok = report.score >= get_glue_dq_settings().gate_min_score and not any(o.result == "ERROR" for o in report.outcomes)
    return GateDecision(ok, run_id, status, report, reason="" if ok else f"{len(report.failed)} rule(s) not passing")
```

```python
# app/api/_03data_02glue_data_quality.py
@router.post("/gate")
def gate(idempotency_key: str = Header(alias="Idempotency-Key", min_length=1)) -> dict[str, Any]:
    return asdict(service.evaluate_gate(idempotency_key))
```

- **Catch**: an `ERROR` rule fails the gate even at a high score
  - Errors usually mean a missing column, not bad data
