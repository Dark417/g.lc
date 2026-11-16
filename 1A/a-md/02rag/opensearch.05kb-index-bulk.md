# opensearch.05kb-index-bulk Knowledge Base (KB) Index and Bulk Writes

> The index a Bedrock Knowledge Base (KB) expects, the shared field contract, and bulk writes that surface partial failures.

## Index

- [1. The Index A Bedrock KB Expects](#1-the-index-a-bedrock-kb-expects)
  - [1.1 Fields](#11-fields)
  - [1.2 Apply Order And Creation](#12-apply-order-and-creation)
- [2. Bulk Writes](#2-bulk-writes)
  - [2.1 Document Shape](#21-document-shape)
  - [2.2 Partial Failures And Retry](#22-partial-failures-and-retry)
  - [2.3 Delete](#23-delete)

## 1. The Index A Bedrock KB Expects

Bedrock does not create the index on a bring-your-own collection, so create it first.

### 1.1 Fields

Field names are yours; they must match the KB `field_mapping`.

- **Vector**: `embedding`, `knn_vector`, `dimension = 1024` (Titan V2), `faiss` + `hnsw`, `l2`
- **Text**: `text`, type `text`
  - ⇒ the chunk; also what Best Matching 25 (BM25) hybrid search reads
- **Metadata**: `metadata`, type `text`, `index: false`
  - ⇒ Bedrock's JavaScript Object Notation (JSON) of system metadata
- Bedrock also writes your sidecar metadata attributes as top-level fields
  - ⇒ those are filterable
- Dimension mismatch between index and embedding model
  - ⇒ KB ingestion fails per document

```python
# app/config/_02rag_02opensearch.py
# Index contract shared with the Bedrock KB (02rag_04 storage_configuration.field_mapping):
# change one, change both.
index_name: str = "a-kb-index"
vector_field: str = "embedding"
text_field: str = "text"
metadata_field: str = "metadata"
dimensions: int = 1024  # must equal the KB embedding model dimensions (Titan V2 1024)
```

```python
# app/infra/_02rag_02opensearch.py  (kb_index_body, non-vector fields)
c.text_field: {"type": "text"},  # BM25-searchable chunk text (hybrid search needs this)
# KB stores a JSON string of system metadata here; not searched, so not indexed.
c.metadata_field: {"type": "text", "index": False},
"doc_id": {"type": "keyword"},  # our own id, for delete-by-query when _id is not allowed
```

### 1.2 Apply Order And Creation

The index sits between the collection and the KB.

→ collection  
→ data-access policy  
→ index (Python, `create_kb_index`)  
→ KB ([knowledge-bases](knowledge-bases.00index.md))

```python
# app/infra/_02rag_02opensearch.py
def create_kb_index(recreate: bool = False) -> dict[str, Any]:
    client = opensearch_client()
    name = contract().index_name
    if client.indices.exists(index=name):
        if not recreate:
            return {"index": name, "created": False}  # idempotent
        client.indices.delete(index=name)
    try:
        resp = client.indices.create(index=name, body=kb_index_body())
    except RequestError as e:
        if e.error == "resource_already_exists_exception":  # raced with another creator
            return {"index": name, "created": False}
        raise
    return {"index": name, "created": True, "acknowledged": resp.get("acknowledged", False)}
```

- **Catch**: mapping of an existing field can't change in place (dimension, engine, space_type)
  - ⇒ new index + reindex / re-ingest
- **Catch**: `delete_index` drops every vector
  - A KB pointing at it fails ingestion until it is recreated

## 2. Bulk Writes

Self-managed ingestion (not via KB) uses `_bulk`.

### 2.1 Document Shape

Documents match KB-written docs, so both can share the index.

```python
# app/infra/_02rag_02opensearch.py
def to_document(record: VectorRecord) -> dict[str, Any]:
    c = contract()
    if len(record.vector) != c.dimensions:
        raise ValueError(f"vector has {len(record.vector)} dims, index expects {c.dimensions}")
    return {
        c.vector_field: record.vector,
        c.text_field: record.text,
        c.metadata_field: json.dumps(record.metadata),
        "doc_id": record.id,
        **record.metadata,  # top-level fields are what filters match (strings get .keyword)
    }
```

### 2.2 Partial Failures And Retry

`_bulk` returns Hypertext Transfer Protocol (HTTP) 200 even when items fail, so inspect every item.

- 429 / 5xx items are retried with full-jitter backoff (OpenSearch Compute Unit (OCU) scale-up, throttling)
- 400-class items (mapping errors, wrong dimension) are reported, never retried
- Retries make "index" an upsert ⇒ keep ids stable

```python
# app/infra/_02rag_02opensearch.py
RETRYABLE_STATUS = {429, 502, 503, 504}  # 429 = too many requests / OCU scaling; 5xx = transient


def bulk_index(records: list[VectorRecord]) -> BulkResult:
    s = get_opensearch_settings()
    client = opensearch_client()
    result = BulkResult()
    pending = list(records)
    for attempt in range(s.bulk_max_attempts):
        result.attempts = attempt + 1
        retry: list[VectorRecord] = []
        for start in range(0, len(pending), s.bulk_chunk):
            batch = pending[start : start + s.bulk_chunk]
            lines: list[dict[str, Any]] = []
            for r in batch:
                lines.append({"index": {"_index": s.index_name, "_id": r.id}})
                lines.append(to_document(r))
            resp = client.bulk(body=lines)
            for r, item in zip(batch, resp["items"]):  # per-item status, not HTTP status
                status = item["index"].get("status", 500)
                if status < 300:
                    result.succeeded += 1
                elif status in RETRYABLE_STATUS and attempt < s.bulk_max_attempts - 1:
                    retry.append(r)
                else:
                    err = item["index"].get("error", {})
                    result.failed.append(BulkItemError(r.id, status, err.get("type", "unknown"), err.get("reason", "")))
        if not retry:
            break
        pending = retry
        time.sleep(backoff(attempt, base=0.5, cap=10.0))
    return result
```

```python
# app/infra/_02rag_02opensearch.py
class OpenSearchVectorStore:
    def upsert(self, records: list[VectorRecord]) -> int:
        result = bulk_index(records)
        if result.failed:
            # Surface partial failure; the caller decides to retry or dead-letter.
            raise RuntimeError(f"{len(result.failed)} documents failed, first: {result.failed[0]}")
        return result.succeeded
```

### 2.3 Delete

Delete by `_id` through `_bulk`; a 404 means already gone.

```python
# app/infra/_02rag_02opensearch.py
def bulk_delete(ids: list[str]) -> int:
    if not ids:
        return 0
    index = contract().index_name
    resp = opensearch_client().bulk(body=[{"delete": {"_index": index, "_id": i}} for i in ids])
    return sum(1 for item in resp["items"] if item["delete"].get("status") in (200, 404))  # idempotent
```

- **Catch**: on Serverless, writes are not instantly searchable
  - ⇒ do not "read your write" right after bulk
