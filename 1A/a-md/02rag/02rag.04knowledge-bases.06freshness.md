# 02rag.04knowledge-bases.06freshness Keeping It Fresh

> Nothing syncs until you start a job: schedule it, trigger it from events, or ingest documents directly.

## Index

- [1. Options](#1-options)
- [2. The Concurrency Catch](#2-the-concurrency-catch)
- [3. Event Handler](#3-event-handler)

## 1. Options

Lecture 80: four ways to keep the index current.

- **Scheduled sync**: EventBridge Scheduler → `StartIngestionJob` (hourly / daily)
- **Event-driven**: Simple Storage Service (S3) event → Lambda → `StartIngestionJob` with a `clientToken`
  - Idempotent on redelivery
- **Direct ingestion**: `IngestKnowledgeBaseDocuments` for specific documents
  - Seconds-level freshness
  - Custom and S3 data sources
- **Managed connectors** expose a sync schedule in newer Application Programming Interface (API) versions (check the docs)

## 2. The Concurrency Catch

An event during a running job may be missed by that job.

→ an event arrives while a job runs  
⇒ `ConflictException`  
⇒ the running job may have scanned before the change landed  
→ defer: queue the event and retry, or rely on the next scheduled sweep

- Always pair events with a scheduled sweep (EventBridge Scheduler, e.g. hourly)
- Or retry deferred events from a queue

## 3. Event Handler

S3 delivers at least once, so the handler derives the token from the event itself.

→ S3 ObjectCreated / ObjectRemoved (EventBridge or S3 notification → Lambda)  
→ keep only keys under `kb-docs/`  
→ `clientToken` from (key, sequencer) pairs  
→ `StartIngestionJob`  
⇒ `ConflictException` ⇒ "deferred": the next sync picks it up

```python
# app/service/_02rag_04knowledge_bases.py
def changed_keys(event: dict[str, Any]) -> list[tuple[str, str]]:
    """(key, sequencer) per S3 record under the KB prefix. Sidecar changes count: metadata needs a sync too."""
    prefix = get_kb_settings().kb_docs_prefix
    out: list[tuple[str, str]] = []
    for record in event.get("Records", []):
        obj = record.get("s3", {}).get("object", {})
        key = obj.get("key", "")
        if key.startswith(prefix):
            out.append((key, obj.get("sequencer", "")))
    return out


def handle_s3_event(event: dict[str, Any]) -> dict[str, Any]:
    keys = changed_keys(event)
    if not keys:
        return {"status": "ignored", "reason": "no keys under the KB prefix"}
    # redelivered event => same (key, sequencer) set => same token => no second job
    token = infra.client_token(*sorted(f"{k}@{seq}" for k, seq in keys))
    try:
        job = infra.start_ingestion_job(token=token, description=f"s3 event: {len(keys)} object(s)")
    except Exception as e:  # noqa: BLE001 - only ConflictException is expected and handled
        if infra.is_conflict(e):
            return {"status": "deferred", "reason": "an ingestion job is already running", "keys": len(keys)}
        raise
    return {"status": "started", "job_id": job.job_id, "keys": len(keys)}
```

```python
# app/infra/_02rag_04knowledge_bases.py
def is_conflict(e: Exception) -> bool:
    return isinstance(e, ClientError) and e.response["Error"]["Code"] == "ConflictException"
```

- **Gap**: the EventBridge Scheduler and Lambda wiring are doc only (handler logic only)
- **Alternative** for per-document, low-latency updates: `IngestKnowledgeBaseDocuments`
