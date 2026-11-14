# 02rag.04knowledge-bases.02ingestion Ingestion

> Data sources, incremental ingestion jobs, job statistics, and the data deletion policy.

## Index

- [1. Data Sources](#1-data-sources)
- [2. Ingestion Job](#2-ingestion-job)
  - [2.1 Mechanism](#21-mechanism)
  - [2.2 Start With A Client Token](#22-start-with-a-client-token)
  - [2.3 Poll And Read Statistics](#23-poll-and-read-statistics)
  - [2.4 Job History](#24-job-history)
- [3. Data Deletion Policy And Encryption](#3-data-deletion-policy-and-encryption)

## 1. Data Sources

A data source = where documents come from + how they are processed.

- **Types**: Simple Storage Service (S3), web crawler, Confluence, SharePoint, Salesforce, custom (direct ingestion Application Programming Interface (API))
- One Knowledge Base (KB) can have several data sources
  - e.g. one per chunking strategy or per prefix
- Chunking is immutable after create ([02rag.03chunking.05none-lambda-parsing](02rag.03chunking.05none-lambda-parsing.md))

```python
# app/infra/_02rag_04knowledge_bases.py
def create_data_source(name: str, strategy: str, prefix: str | None = None) -> dict[str, Any]:
    """The KB console's data-source screen as code: one data source per strategy and prefix."""
    s = get_kb_settings()
    resp = _agent().create_data_source(
        knowledgeBaseId=s.knowledge_base_id,
        clientToken=client_token("data-source", name, strategy),  # a retry returns the same data source
        name=name,
        description=f"{strategy} chunking over {prefix or s.kb_docs_prefix}",
        dataSourceConfiguration={
            "type": "S3",
            "s3Configuration": {
                "bucketArn": f"arn:aws:s3:::{get_settings().data_bucket}",
                "inclusionPrefixes": [prefix or s.kb_docs_prefix],
            },
        },
        dataDeletionPolicy="DELETE",  # vectors removed with the data source
        vectorIngestionConfiguration={"chunkingConfiguration": CHUNKING_CONFIGS[strategy]},  # immutable
    )
    ds = resp["dataSource"]
    return {"data_source_id": ds["dataSourceId"], "status": ds["status"], "name": ds["name"]}
```

## 2. Ingestion Job

An ingestion job ("sync") processes only what changed since the last sync.

### 2.1 Mechanism

Change detection makes ingestion cost scale with changes, not corpus size.

→ scan the source  
→ compare with the last sync (new / modified / deleted)  
→ parse, chunk, embed only what changed  
→ upsert vectors; delete vectors of removed files

### 2.2 Start With A Client Token

The same inputs yield the same token, so a retried call does not start a second job.

```python
# app/infra/_02rag_04knowledge_bases.py
def client_token(*parts: str) -> str:
    """Idempotency token (API: 33–256 chars)."""
    return hashlib.sha256("|".join(parts).encode()).hexdigest()  # 64 hex chars


def start_ingestion_job(token: str | None = None, description: str = "") -> IngestionJob:
    s = get_kb_settings()
    resp = _agent().start_ingestion_job(
        knowledgeBaseId=s.knowledge_base_id,
        dataSourceId=s.data_source_id,
        clientToken=token or client_token(str(uuid.uuid4()), str(uuid.uuid4())),
        description=description or "1A sync",
    )
    return _to_job(resp["ingestionJob"])
```

- **Catch**: one running job per data source
  - ⇒ `ConflictException` while another runs (check the quotas page)
  - Handling: [06 Freshness](02rag.04knowledge-bases.06freshness.md)

### 2.3 Poll And Read Statistics

`COMPLETE` can still contain failed documents.

- **Statistics**: scanned, new indexed, modified indexed, deleted, failed, skipped (unchanged)
- Read `numberOfDocumentsFailed` + `failureReasons`
  - Typical causes: bad metadata JavaScript Object Notation (JSON), file too large, unsupported type

```python
# app/domain/_02rag_04knowledge_bases.py
TERMINAL_STATUSES = {"COMPLETE", "FAILED", "STOPPED"}


@dataclass(frozen=True)
class IngestionStats:
    scanned: int = 0
    metadata_scanned: int = 0
    new_indexed: int = 0
    modified_indexed: int = 0
    deleted: int = 0
    failed: int = 0
    skipped: int = 0  # unchanged since last sync (incremental change detection)
```

```python
# app/infra/_02rag_04knowledge_bases.py
def wait_for_ingestion(job_id: str) -> IngestionJob:
    s = get_kb_settings()
    deadline = time.monotonic() + s.poll_deadline_s
    while True:
        job = get_ingestion_job(job_id)
        if job.status in TERMINAL_STATUSES:
            return job  # caller must still check job.stats.failed and failure_reasons
        if time.monotonic() > deadline:
            raise TimeoutError(f"ingestion job {job_id} still {job.status} after {s.poll_deadline_s}s")
        time.sleep(s.poll_interval_s)
```

### 2.4 Job History

List jobs newest first to check whether a sync ran after an upload.

```python
# app/infra/_02rag_04knowledge_bases.py
def list_ingestion_jobs(status: str | None = None) -> list[IngestionJob]:
    s = get_kb_settings()
    kwargs: dict[str, Any] = {
        "knowledgeBaseId": s.knowledge_base_id,
        "dataSourceId": s.data_source_id,
        "sortBy": {"attribute": "STARTED_AT", "order": "DESCENDING"},
        "PaginationConfig": {"PageSize": 100},  # paginator follows nextToken; maxResults ≤ 1000
    }
    if status:
        kwargs["filters"] = [{"attribute": "STATUS", "operator": "EQ", "values": [status]}]
    jobs: list[IngestionJob] = []
    for page in _agent().get_paginator("list_ingestion_jobs").paginate(**kwargs):
        for summary in page["ingestionJobSummaries"]:
            jobs.append(_to_job(summary))
    return jobs
```

## 3. Data Deletion Policy And Encryption

The deletion policy decides whether vectors outlive their data source.

- **`DELETE`**: removing the data source removes its vectors
- **`RETAIN`** (default): vectors stay
  - ⇒ orphans that still answer queries
- **Encryption**: data source `serverSideEncryptionConfiguration` (transient data) with the Customer Managed Key (CMK)
