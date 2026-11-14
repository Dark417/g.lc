# 05ops.01observability.04alarms-tracing Alarms and Tracing

> Which alarms catch quiet Large Language Model (LLM) failures, and how traces locate the slow step.

## Index

- [1. Alarms](#1-alarms)
  - [1.1 Alarm Set](#11-alarm-set)
  - [1.2 Code: Throttle Alarm](#12-code-throttle-alarm)
- [2. Tracing](#2-tracing)

Back to [00index](05ops.01observability.00index.md).

## 1. Alarms

Alarm on percentiles and throttles, not on averages.

### 1.1 Alarm Set

- Throttles
  - `Sum(InvocationThrottles) > 0` over 5 min
  - quota or burst problem
- Latency
  - `p90(InvocationLatency)` over threshold, 2 of 3 windows
  - ignore one long generation
- Cost proxy
  - `Sum(OutputTokenCount)` per hour above budget
  - or an anomaly-detection alarm
- Errors: `InvocationServerErrors > 0`
- `treat_missing_data = notBreaching` for sparse traffic
- Send to Simple Notification Service (SNS) (`a-alerts`)
  - a human or a runbook acts
- The repo defines two alarms (throttles, p90 latency) in Terraform

### 1.2 Code: Throttle Alarm

```python
# illustrative: the Terraform throttle alarm expressed with boto3
cloudwatch.put_metric_alarm(
    AlarmName="a-bedrock-throttles",
    Namespace="AWS/Bedrock",
    MetricName="InvocationThrottles",
    Dimensions=[{"Name": "ModelId", "Value": model_id}],  # check ListMetrics for profile vs model id
    Statistic="Sum",
    Period=300,
    EvaluationPeriods=1,
    Threshold=0,
    ComparisonOperator="GreaterThanThreshold",
    TreatMissingData="notBreaching",  # sparse traffic is not an outage
    AlarmActions=[alerts_topic_arn],  # SNS a-alerts
)
```

- Catch
  - Wrong `ModelId` dimension ⇒ alarm sits in `INSUFFICIENT_DATA` and never fires
  - Mean latency hides slowness ⇒ use p90 / p99 (`ExtendedStatistic`)

## 2. Tracing

Trace answers "which step is slow"; metrics answer "how often".

- One user request = many spans
  - retrieval
  - rerank
  - model call
  - tool call
  - guardrail
- Options
  - Amazon Web Services (AWS) X-Ray / AWS Distro for OpenTelemetry (ADOT)
  - OpenTelemetry with the Generative Artificial Intelligence (GenAI) semantic conventions
    - `gen_ai.request.model`, `gen_ai.usage.input_tokens`, …
    - still evolving
- Agent frameworks and AgentCore emit spans
  - see the agents group (06agents) later
- Not coded in the repo (gap)
