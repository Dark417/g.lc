# evaluations.08offline-online Offline vs Online Evaluation

> Offline sets catch regressions; online sampling catches distribution shift; the loop connects them.

## Index

- [1. Offline](#1-offline)
- [2. Online](#2-online)
- [3. The Loop](#3-the-loop)
- [4. Code: Result Store](#4-code-result-store)

Back to [00index](evaluations.00index.md).

## 1. Offline

- Fixed dataset
- Run on every change (Continuous Integration (CI))
- Comparable over time
- Keep a fixed "golden" set and a growing "failures" set

## 2. Online

Production traffic, judged and measured after the fact.

- Sampled requests judged asynchronously (same judge prompts)
- User signals: thumbs, retries, escalations
- Guardrail intervention rate, grounding scores, refusal rate
- AgentCore online evaluation configs exist for agents
  - `aws_bedrockagentcore_online_evaluation_config`
  - out of scope here
- Doc only; not coded in the repo

## 3. The Loop

→ Online failures.  
→ New offline cases.  
→ The next change must fix them without regressions.

## 4. Code: Result Store

- Evaluation results are data you keep and compare over time
- Port + in-memory adapter
  - prod: DynamoDB (job index) + Simple Storage Service (S3) (raw results), keyed by dataset version

```python
# app/domain/_04safety_03evaluations.py
class EvalResultStore(Protocol):
    def save_job(self, job: EvalJob) -> None: ...

    def get_job(self, job_arn: str) -> EvalJob | None: ...

    def list_jobs(self) -> list[EvalJob]: ...

    def save_guardrail_report(self, run_id: str, report: GuardrailEvalReport) -> None: ...

    def get_guardrail_report(self, run_id: str) -> GuardrailEvalReport | None: ...
```

- Catch
  - Version dataset + config + results together
  - otherwise scores from different sets get compared
