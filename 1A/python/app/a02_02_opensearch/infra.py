"""OpenSearch vector-store showcase (opensearch-py), in the order of docs/02.02.opensearch-vector-store.md.

- Client: SigV4 (AWSV4SignerAuth, service "aoss" for Serverless, "es" for a managed domain).
- Index: the exact mapping a Bedrock Knowledge Base expects (vector + text + metadata fields).
- Writes: _bulk with per-item error handling and retry of 429 / 5xx items only.
- Reads: k-NN, efficient-filtered k-NN, hybrid (BM25 + k-NN) through a normalization search pipeline.
- Serverless catches (verify against the "supported operations" page for your collection):
  - no index settings for shards / replicas (AOSS manages them) and no ?refresh: writes become searchable after a
    short delay (seconds, order of magnitude)
  - early VECTORSEARCH collections rejected client-supplied _id on index/bulk; if yours does, drop "_id" and
    delete by query on the stored doc_id field instead
- No network call at import time: the client is built on first use.
"""

import json
import time
from functools import lru_cache
from typing import Any

from opensearchpy import AWSV4SignerAuth, OpenSearch, RequestsHttpConnection
from opensearchpy.exceptions import NotFoundError, RequestError

from app.a02_02_opensearch.config import get_opensearch_settings
from app.a02_02_opensearch.domain import (
    BulkItemError,
    BulkResult,
    KbIndexContract,
    MetadataFilter,
    SearchHit,
    Vector,
    VectorRecord,
)
from app.shared import aws
from app.shared.retry import backoff

RETRYABLE_STATUS = {429, 502, 503, 504}  # 429 = too many requests / OCU scaling; 5xx = transient


def contract() -> KbIndexContract:
    s = get_opensearch_settings()
    return KbIndexContract(s.index_name, s.vector_field, s.text_field, s.metadata_field, s.dimensions)


# ================================================================ client (SigV4)


@lru_cache
def opensearch_client() -> OpenSearch:
    """SigV4-signed client. When to use: every AOSS / managed-domain call from AWS credentials.

    Catch: AWSV4SignerAuth takes a credentials object that refreshes itself (role / SSO); never freeze keys.
    IAM aoss:APIAccessAll is necessary but not sufficient: the data-access policy (02.02 .tf) must name the role.
    """
    s = get_opensearch_settings()
    credentials = aws.session().get_credentials()
    auth = AWSV4SignerAuth(credentials, aws.session().region_name, s.service)
    return OpenSearch(
        hosts=[{"host": s.collection_endpoint, "port": s.port}],
        http_auth=auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,  # required for AWSV4SignerAuth (signs the requests call)
        pool_maxsize=20,
        timeout=s.timeout_s,
    )


# ================================================================ index for Bedrock KB


def kb_index_body(ef_search: int = 512, m: int = 16, ef_construction: int = 512) -> dict[str, Any]:
    """Mapping a Bedrock KB can write to. Field names must equal the KB field_mapping (02.04).

    Knobs on the vector field:
    - engine: faiss (KB requirement for AOSS; supports efficient filtering, fp16/PQ encoders) | lucene
      (smaller indexes, efficient filtering) | nmslib (deprecated; blocked for new indexes in OpenSearch 3.0)
    - name: hnsw (no training) | ivf (faiss only, needs a train step + model; managed domains)
    - space_type: l2 | innerproduct | cosinesimil | l1 | linf | hamming (binary vectors). Titan V2 output is
      normalized, so l2 and innerproduct rank identically.
    - m (default 16): links per node; ef_construction (default 100): build beam. Higher = recall, memory, build time.
    - index.knn.algo_param.ef_search (default 100): query beam; higher = recall + latency.
    For binary embeddings (KB embedding_data_type BINARY) use "data_type": "binary" + space_type "hamming".
    """
    c = contract()
    return {
        "settings": {
            "index": {
                "knn": True,  # turns on native k-NN structures for knn_vector fields
                "knn.algo_param.ef_search": ef_search,
                # AOSS: no number_of_shards / number_of_replicas. Managed domain: set them (shard sizing in the doc).
            }
        },
        "mappings": {
            "properties": {
                c.vector_field: {
                    "type": "knn_vector",
                    "dimension": c.dimensions,
                    "method": {
                        "name": "hnsw",
                        "engine": "faiss",
                        "space_type": "l2",
                        "parameters": {"m": m, "ef_construction": ef_construction},
                    },
                },
                c.text_field: {"type": "text"},  # BM25-searchable chunk text (hybrid search needs this)
                # KB stores a JSON string of system metadata here; not searched, so not indexed.
                c.metadata_field: {"type": "text", "index": False},
                "doc_id": {"type": "keyword"},  # our own id, for delete-by-query when _id is not allowed
            }
        },
    }


def on_disk_vector_field(dimensions: int, compression: str = "32x") -> dict[str, Any]:
    """Disk-based vector field (managed domains, OpenSearch 2.17+): quantized vectors in memory, full ones on disk.

    compression_level: 1x | 2x (fp16) | 4x (byte) | 8x | 16x | 32x (binary). on_disk defaults to 32x and rescores
    with full precision. Trade: ~32x less RAM for extra disk reads and latency. Check AOSS support before using.
    """
    return {
        "type": "knn_vector",
        "dimension": dimensions,
        "space_type": "innerproduct",
        "mode": "on_disk",
        "compression_level": compression,
    }


def create_kb_index(recreate: bool = False) -> dict[str, Any]:
    """Create the KB vector index before creating the Knowledge Base (apply order: collection → index → KB).

    Idempotent: an existing index is left alone unless recreate=True. Catch: mapping of an existing field can't
    change in place (dimension, engine, space_type) ⇒ new index + reindex / re-ingest.
    """
    client = opensearch_client()
    name = contract().index_name
    if client.indices.exists(index=name):
        if not recreate:
            return {"index": name, "created": False}
        client.indices.delete(index=name)
    try:
        resp = client.indices.create(index=name, body=kb_index_body())
    except RequestError as e:
        if e.error == "resource_already_exists_exception":  # raced with another creator
            return {"index": name, "created": False}
        raise
    return {"index": name, "created": True, "acknowledged": resp.get("acknowledged", False)}


def delete_index() -> bool:
    """Drop the index (and every vector). Catch: a KB pointing at it fails ingestion until it is recreated."""
    try:
        opensearch_client().indices.delete(index=contract().index_name)
        return True
    except NotFoundError:
        return False


# ================================================================ bulk indexing (partial failures + retry)


def to_document(record: VectorRecord) -> dict[str, Any]:
    """Document shape compatible with KB-written docs: vector + text + metadata JSON + flat filterable attributes."""
    c = contract()
    if len(record.vector) != c.dimensions:
        raise ValueError(f"vector has {len(record.vector)} dims, index expects {c.dimensions}")
    return {
        c.vector_field: record.vector,
        c.text_field: record.text,
        c.metadata_field: json.dumps(record.metadata),
        "doc_id": record.id,
        **record.metadata,  # top-level fields are what filters match (dynamic mapping: strings get .keyword)
    }


def bulk_index(records: list[VectorRecord]) -> BulkResult:
    """Bulk load with per-item results. _bulk returns 200 even when items fail: inspect every item.

    - 429 / 5xx items are retried with full-jitter backoff (OCU scale-up, throttling)
    - 400-class items (mapping errors, wrong dimension) are reported, never retried
    When to use: self-managed ingestion (not via KB). Catch: retries make "index" an upsert; keep ids stable.
    """
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
            for r, item in zip(batch, resp["items"]):
                op = item["index"]
                status = op.get("status", 500)
                if status < 300:
                    result.succeeded += 1
                elif status in RETRYABLE_STATUS and attempt < s.bulk_max_attempts - 1:
                    retry.append(r)
                else:
                    err = op.get("error", {})
                    result.failed.append(
                        BulkItemError(r.id, status, err.get("type", "unknown"), err.get("reason", ""))
                    )
        if not retry:
            break
        pending = retry
        time.sleep(backoff(attempt, base=0.5, cap=10.0))
    return result


def bulk_delete(ids: list[str]) -> int:
    """Delete by _id through _bulk; a 404 item means already gone (idempotent)."""
    if not ids:
        return 0
    index = contract().index_name
    resp = opensearch_client().bulk(body=[{"delete": {"_index": index, "_id": i}} for i in ids])
    return sum(1 for item in resp["items"] if item["delete"].get("status") in (200, 404))


# ================================================================ k-NN queries


def _hits(resp: dict[str, Any]) -> list[SearchHit]:
    c = contract()
    out: list[SearchHit] = []
    for h in resp["hits"]["hits"]:
        src = h.get("_source", {})
        meta_raw = src.get(c.metadata_field) or "{}"
        try:
            meta = json.loads(meta_raw) if isinstance(meta_raw, str) else dict(meta_raw)
        except json.JSONDecodeError:
            meta = {"raw": meta_raw}
        out.append(SearchHit(id=src.get("doc_id", h["_id"]), score=h["_score"], text=src.get(c.text_field, ""), metadata=meta))
    return out


def knn_query(vector: Vector, k: int = 5, ef_search: int | None = None) -> list[SearchHit]:
    """Plain approximate k-NN. k = neighbours per segment/shard; size = hits returned.

    ef_search per query (method_parameters, OpenSearch 2.16+) overrides the index default: raise it for recall.
    Catch: never return the vector in _source (4 KB per hit at 1024 dims) — excluded below.
    """
    c = contract()
    knn: dict[str, Any] = {"vector": vector, "k": k}
    if ef_search:
        knn["method_parameters"] = {"ef_search": ef_search}
    body = {"size": k, "query": {"knn": {c.vector_field: knn}}, "_source": {"excludes": [c.vector_field]}}
    return _hits(opensearch_client().search(index=c.index_name, body=body))


def metadata_filter_clause(flt: MetadataFilter) -> dict[str, Any]:
    """{"dept": "hr", "year": 2025, "tags": ["a", "b"]} → bool filter. Strings match the .keyword sub-field."""
    terms: list[dict[str, Any]] = []
    for k, v in flt.items():
        if isinstance(v, list):
            field = f"{k}.keyword" if v and isinstance(v[0], str) else k
            terms.append({"terms": {field: v}})
        else:
            terms.append({"term": {f"{k}.keyword" if isinstance(v, str) else k: v}})
    return {"bool": {"filter": terms}}


def filtered_knn_query(vector: Vector, flt: MetadataFilter, k: int = 5) -> list[SearchHit]:
    """Efficient filtering: the filter sits INSIDE the knn clause (faiss 2.9+, lucene 2.4+).

    The engine decides per query: very selective filter ⇒ exact search over matches; loose ⇒ filtered HNSW.
    Catch: a bool { must: knn, filter: ... } is POST-filtering ⇒ can return fewer than k hits.
    """
    c = contract()
    body = {
        "size": k,
        "query": {"knn": {c.vector_field: {"vector": vector, "k": k, "filter": metadata_filter_clause(flt)}}},
        "_source": {"excludes": [c.vector_field]},
    }
    return _hits(opensearch_client().search(index=c.index_name, body=body))


# ================================================================ hybrid search (BM25 + k-NN)


def create_hybrid_pipeline(lexical_weight: float = 0.3, vector_weight: float = 0.7) -> dict[str, Any]:
    """Search pipeline with the normalization processor (OpenSearch 2.10+).

    - normalization.technique: min_max (default) | l2 — puts BM25 (unbounded) and k-NN scores on one scale
    - combination.technique: arithmetic_mean (default) | geometric_mean | harmonic_mean; weights follow the
      ORDER of sub-queries in the hybrid clause
    - Alternative (2.19+): "score-ranker-processor" with {"combination": {"technique": "rrf", "rank_constant": 60}}
    Catch: verify search-pipeline support on your AOSS collection; managed domains support it.
    """
    body = {
        "description": "BM25 + k-NN hybrid for the KB index",
        "phase_results_processors": [
            {
                "normalization-processor": {
                    "normalization": {"technique": "min_max"},
                    "combination": {
                        "technique": "arithmetic_mean",
                        "parameters": {"weights": [lexical_weight, vector_weight]},
                    },
                }
            }
        ],
    }
    return opensearch_client().search_pipeline.put(id=get_opensearch_settings().search_pipeline, body=body)


def hybrid_query(text: str, vector: Vector, k: int = 5, flt: MetadataFilter | None = None) -> list[SearchHit]:
    """Hybrid = lexical match + k-NN in one request, fused by the pipeline. Sub-query order = weight order.

    When to use: queries mixing identifiers (SKUs, error codes) and natural language.
    Catch: without ?search_pipeline the hybrid query errors or returns un-normalized scores.
    """
    c = contract()
    knn: dict[str, Any] = {"vector": vector, "k": k}
    lexical: dict[str, Any] = {"match": {c.text_field: {"query": text}}}
    if flt:
        knn["filter"] = metadata_filter_clause(flt)
        lexical = {"bool": {"must": [lexical], "filter": metadata_filter_clause(flt)["bool"]["filter"]}}
    body = {
        "size": k,
        "query": {"hybrid": {"queries": [lexical, {"knn": {c.vector_field: knn}}]}},
        "_source": {"excludes": [c.vector_field]},
    }
    resp = opensearch_client().search(
        index=c.index_name, body=body, params={"search_pipeline": get_opensearch_settings().search_pipeline}
    )
    return _hits(resp)


# ================================================================ VectorStore adapter


class OpenSearchVectorStore:
    """VectorStore port over the KB index. Same port as 02.01's ExactVectorStore, so callers can swap stores."""

    def upsert(self, records: list[VectorRecord]) -> int:
        result = bulk_index(records)
        if result.failed:
            # Surface partial failure instead of hiding it; the caller decides to retry or dead-letter.
            raise RuntimeError(f"{len(result.failed)} documents failed, first: {result.failed[0]}")
        return result.succeeded

    def query(self, vector: Vector, k: int, filter: MetadataFilter | None = None) -> list[SearchHit]:
        return filtered_knn_query(vector, filter, k) if filter else knn_query(vector, k)

    def delete(self, ids: list[str]) -> int:
        return bulk_delete(ids)
