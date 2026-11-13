"""Use case: keep the KB fresh (lecture 80). S3 event → one idempotent ingestion job.

Flow: S3 ObjectCreated / ObjectRemoved (via EventBridge or S3 notification → Lambda) → handle_s3_event
  → keep only keys under kb-docs/ → clientToken from (key, sequencer) pairs → StartIngestionJob
  → ConflictException (a job is already running) ⇒ "deferred": the change is picked up by the next sync
Catch: a running job may have scanned the prefix before this change landed ⇒ always pair events with a scheduled
sweep (EventBridge Scheduler, e.g. hourly) or retry deferred events from a queue. For per-document,
low-latency updates, the IngestKnowledgeBaseDocuments API (direct ingestion) is the alternative.
"""

from typing import Any

from app.a02_04_knowledge_bases import infra
from app.a02_04_knowledge_bases.config import get_kb_settings


def changed_keys(event: dict[str, Any]) -> list[tuple[str, str]]:
    """(key, sequencer) for each S3 record under the KB prefix. Sidecar changes count: metadata needs a sync too."""
    prefix = get_kb_settings().kb_docs_prefix
    out: list[tuple[str, str]] = []
    for record in event.get("Records", []):
        obj = record.get("s3", {}).get("object", {})
        key = obj.get("key", "")
        if key.startswith(prefix):
            out.append((key, obj.get("sequencer", "")))
    return out


def handle_s3_event(event: dict[str, Any]) -> dict[str, Any]:
    """Idempotent: S3 delivers at least once, so a redelivered event yields the same clientToken ⇒ no second job."""
    keys = changed_keys(event)
    if not keys:
        return {"status": "ignored", "reason": "no keys under the KB prefix"}
    token = infra.client_token(*sorted(f"{k}@{seq}" for k, seq in keys))
    try:
        job = infra.start_ingestion_job(token=token, description=f"s3 event: {len(keys)} object(s)")
    except Exception as e:  # noqa: BLE001 - only ConflictException is expected and handled
        if infra.is_conflict(e):
            return {"status": "deferred", "reason": "an ingestion job is already running", "keys": len(keys)}
        raise
    return {"status": "started", "job_id": job.job_id, "keys": len(keys)}
