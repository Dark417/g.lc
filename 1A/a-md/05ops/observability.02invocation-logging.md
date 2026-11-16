# observability.02invocation-logging Model Invocation Logging

> Per-request payload logs from Bedrock, what belongs in them, and how to query them.

## Index

- [1. How It Works](#1-how-it-works)
  - [1.1 Configuration](#11-configuration)
  - [1.2 Record Fields](#12-record-fields)
  - [1.3 Tenant Attribution](#13-tenant-attribution)
- [2. What to Log and Not](#2-what-to-log-and-not)
- [3. Logs Insights](#3-logs-insights)

Back to [00index](observability.00index.md).

## 1. How It Works

Bedrock writes each request and response to CloudWatch Logs and/or Simple Storage Service (S3).

### 1.1 Configuration

- Off by default
- One configuration per account and Region
  - a single owner; another stack can silently replace it
- Destinations: CloudWatch Logs, S3, or both
- Delivery flags per data type
  - text (Converse, InvokeModel text)
  - embedding
  - image
  - video
  - each flag = payloads of that type logged; off = metadata only
- Large payloads
  - bodies over the CloudWatch event size limit are written to S3 (`large_data_delivery_s3_config`)
  - the log keeps a pointer
- Owned by the Terraform module; not coded in Python

```python
# illustrative: the same config through boto3 (the repo sets it in Terraform)
bedrock.put_model_invocation_logging_configuration(
    loggingConfig={
        "cloudWatchConfig": {
            "logGroupName": "/aws/bedrock/a-invocations",
            "roleArn": logging_role_arn,  # Bedrock assumes it; trust with aws:SourceAccount
            "largeDataDeliveryS3Config": {"bucketName": bucket, "keyPrefix": "bedrock-large/"},
        },
        "textDataDeliveryEnabled": True,  # payloads logged; False = metadata only
        "embeddingDataDeliveryEnabled": False,
        "imageDataDeliveryEnabled": False,
    }
)
```

### 1.2 Record Fields

Verify on a real record.

- `timestamp`, `requestId`, `modelId`, `operation`, `identity.arn`
- `input.inputTokenCount`, `output.outputTokenCount`
- `input.inputBodyJson`, `output.outputBodyJson`
- Use
  - debugging
  - audit
  - offline evaluation datasets
  - cost attribution by caller

### 1.3 Tenant Attribution

- It records caller identity, not your tenant id
- pass tenant in `requestMetadata` of Converse (verify in the Converse reference)
  - so it shows up in the log

```python
# illustrative: tenant and feature in requestMetadata for attributable logs
runtime.converse(
    modelId=model_id,
    messages=messages,
    requestMetadata={"tenant": "acme", "feature": "support-chat"},  # low-cardinality strings
)
```

## 2. What to Log and Not

Never log a prompt you would not want read in an audit.

- Log
  - model id
  - token counts
  - latency
  - `stopReason`
  - guardrail action
  - prompt template id and version
  - tenant tier
- Don't log by default
  - raw user prompts
  - retrieved documents
  - tool outputs with secrets
- If you must (debug, audit)
  - redact first ([pii-redaction](../04safety/pii-redaction.00index.md))
  - encrypt with a Customer Managed Key (CMK), short retention, narrow read access
  - sample instead of 100 %

## 3. Logs Insights

High-cardinality questions (per caller, per model) belong in logs, not metrics.

- Queries are asynchronous
  - `StartQuery`, then poll `GetQueryResults`
  - statuses: Scheduled, Running, Complete, Failed, Cancelled, Timeout
- Billed per Gigabyte (GB) scanned
  - always bound the time range
- Results of a Running query are partial

```python
# app/infra/_05ops_01observability.py
TOKENS_BY_MODEL_QUERY = (
    "fields @timestamp, modelId, input.inputTokenCount as inTok, output.outputTokenCount as outTok "
    "| stats count(*) as calls, sum(inTok) as inputTokens, sum(outTok) as outputTokens by modelId "
    "| sort outputTokens desc"
)  # field names follow the invocation log schema: verify against one real record


def logs_insights(query: str = TOKENS_BY_MODEL_QUERY, hours: int = 24) -> list[dict[str, str]]:
    cfg = get_observability_settings()
    logs = client("logs")
    end = int(time.time())
    qid = logs.start_query(
        logGroupName=cfg.log_group,
        startTime=end - hours * 3600,  # bound the scan: billed per GB
        endTime=end,
        queryString=query,
        limit=100,
    )["queryId"]
    deadline = time.monotonic() + cfg.query_deadline_s
    attempt = 0
    while True:
        resp = logs.get_query_results(queryId=qid)
        status = resp["status"]
        if status == "Complete":
            return [{c["field"]: c["value"] for c in row if c["field"] != "@ptr"} for row in resp["results"]]
        if status in ("Failed", "Cancelled", "Timeout"):
            raise RuntimeError(f"Logs Insights query {qid} ended {status}")
        if time.monotonic() >= deadline:
            logs.stop_query(queryId=qid)  # stop paying for a query nobody waits for
            raise TimeoutError(f"query {qid} still {status}")
        time.sleep(backoff(attempt, base=0.5, cap=5.0))
        attempt += 1
```
