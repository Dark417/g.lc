"""Embedding calls through Bedrock InvokeModel, in the order of docs/02.01.embeddings-vector-search.md.

- Titan Text Embeddings V2 (amazon.titan-embed-text-v2:0): one text per call, dimensions 256/512/1024,
  normalize flag, embeddingTypes float/binary. Input limit: 8,192 tokens (Bedrock model parameters page).
- Cohere Embed v3 on Bedrock: up to 96 texts per call, asymmetric input_type (document vs query).
- IAM: bedrock:InvokeModel on the embedding model ARNs belongs in terraform/01.01.bedrock-converse.tf (not here).
- Clients come from app.shared.aws (adaptive retries); nothing runs at import time.
"""

import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from botocore.exceptions import ClientError

from app.a02_01_embeddings.config import get_embeddings_settings
from app.a02_01_embeddings.domain import Embedding, EmbeddingCache, InputType, Vector
from app.shared import aws
from app.shared.config import get_settings
from app.shared.retry import call_with_retry

TITAN_DIMENSIONS = (256, 512, 1024)
COHERE_MAX_TEXTS = 96  # Cohere Embed v3 on Bedrock: texts per request (model parameters page)
RETRYABLE_CODES = {"ThrottlingException", "ModelNotReadyException", "ServiceUnavailableException"}


def _retryable(e: Exception) -> bool:
    return isinstance(e, ClientError) and e.response["Error"]["Code"] in RETRYABLE_CODES


def _invoke(model_id: str, body: dict[str, Any]) -> dict[str, Any]:
    # adaptive retries in the client handle most throttling; the outer retry covers bursts in batch jobs.
    def call() -> dict[str, Any]:
        resp = aws.client("bedrock-runtime").invoke_model(
            modelId=model_id,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )
        return json.loads(resp["body"].read())

    return call_with_retry(call, _retryable, max_attempts=4)


# ================================================================ Titan Text Embeddings V2


def titan_body(text: str, dimensions: int = 1024, normalize: bool = True, binary: bool = False) -> dict[str, Any]:
    """Request body for Titan V2. Every field is a knob:

    - inputText: required; up to 8,192 tokens / 50,000 characters, longer input is rejected (chunk first, 02.03)
    - dimensions: 256 | 512 | 1024 (default 1024). AWS reports ~99% (512) and ~97% (256) of 1024-dim
      retrieval accuracy (Titan V2 launch blog, 2024) for 2x / 4x less storage.
    - normalize: default true. Keep it true so dot product == cosine and L2 ranks the same way.
    - embeddingTypes: ["float"] (default) and/or ["binary"] (1 bit per dim, for Hamming pre-filtering).
    """
    if dimensions not in TITAN_DIMENSIONS:
        raise ValueError(f"Titan V2 dimensions must be one of {TITAN_DIMENSIONS}")
    return {
        "inputText": text,
        "dimensions": dimensions,
        "normalize": normalize,
        "embeddingTypes": ["float", "binary"] if binary else ["float"],
    }


def embed_text(text: str, dimensions: int | None = None, normalize: bool | None = None, binary: bool = False) -> Embedding:
    """One text -> one Titan V2 embedding.

    When to use: query-time embedding and small ingestion. Catch: the SAME model id + dimensions + normalize
    must be used at index time and query time, or similarity scores are meaningless.
    """
    s = get_embeddings_settings()
    model_id = get_settings().embed_model_id
    dims = dimensions or s.dimensions
    body = titan_body(text, dims, s.normalize if normalize is None else normalize, binary)
    out = _invoke(model_id, body)
    by_type = out.get("embeddingsByType", {})
    return Embedding(
        vector=by_type.get("float", out.get("embedding", [])),
        model_id=model_id,
        dimensions=dims,
        input_tokens=out.get("inputTextTokenCount", 0),
        binary=by_type.get("binary"),
    )


def embed_batch(texts: list[str], workers: int | None = None) -> list[Embedding]:
    """Many texts via parallel single-text calls (Titan V2 has no multi-text body). Order is preserved.

    When to use: ingestion of up to thousands of chunks. Catch: parallelism is bounded by the account's
    InvokeModel quota; for millions of chunks use Bedrock batch inference (CreateModelInvocationJob, priced below on-demand for supported models,
    asynchronous) or let a Knowledge Base ingestion job do it (02.04).
    """
    n = workers or get_embeddings_settings().batch_workers
    with ThreadPoolExecutor(max_workers=n) as pool:
        return list(pool.map(embed_text, texts))


# ================================================================ Cohere Embed (contrast: asymmetric input_type)


def cohere_body(texts: list[str], input_type: InputType) -> dict[str, Any]:
    """Request body for Cohere Embed v3 on Bedrock.

    - input_type: search_document at index time, search_query at query time (also classification, clustering).
      Mixing them up lowers recall without any error.
    - truncate: NONE (error on long input) | START | END. Default END; NONE surfaces chunking bugs.
    - embedding_types: float | int8 | uint8 | binary | ubinary (server-side quantization).
    - Limits: up to 96 texts per call, ~512 tokens per text for v3 (check the model parameters page).
    """
    if len(texts) > COHERE_MAX_TEXTS:
        raise ValueError(f"Cohere accepts at most {COHERE_MAX_TEXTS} texts per call")
    return {"texts": texts, "input_type": input_type.value, "truncate": "NONE", "embedding_types": ["float"]}


def embed_cohere(texts: list[str], input_type: InputType) -> list[Vector]:
    """Batch embed with Cohere. Response shape: {"embeddings": {"float": [[...], ...]}} when embedding_types is set."""
    out = _invoke(get_embeddings_settings().cohere_model_id, cohere_body(texts, input_type))
    emb = out["embeddings"]
    return emb["float"] if isinstance(emb, dict) else emb


# ================================================================ embedding cache (content hash + model id)


def cache_key(text: str, model_id: str, dimensions: int, normalize: bool) -> str:
    """Key = sha256(model | dims | normalize | text). A model or dims change yields new keys => re-embed.

    Catch: a cache keyed by text alone serves vectors from the old model after an upgrade (silent recall drop).
    """
    raw = f"{model_id}|{dimensions}|{int(normalize)}|{text}".encode()
    return hashlib.sha256(raw).hexdigest()


class InMemoryEmbeddingCache:
    """EmbeddingCache adapter for tests; production would use DynamoDB / ElastiCache with a TTL."""

    def __init__(self) -> None:
        self._data: dict[str, Vector] = {}
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Vector | None:
        v = self._data.get(key)
        if v is None:
            self.misses += 1
        else:
            self.hits += 1
        return v

    def put(self, key: str, vector: Vector) -> None:
        self._data[key] = vector


class CachedTitanEmbedder:
    """Embedder port backed by Titan V2 plus a cache. Re-embedding only happens for new text or a new model.

    When to use: re-ingesting mostly unchanged corpora; repeated queries. Catch: cost is per input token,
    so the cache pays off on re-ingest; it does not help with first-time ingestion.
    """

    def __init__(self, cache: EmbeddingCache) -> None:
        self.cache = cache

    def embed(self, text: str, input_type: InputType = InputType.SEARCH_DOCUMENT) -> Vector:
        # input_type is ignored: Titan V2 is symmetric (same embedding for query and document).
        s = get_embeddings_settings()
        key = cache_key(text, get_settings().embed_model_id, s.dimensions, s.normalize)
        cached = self.cache.get(key)
        if cached is not None:
            return cached
        vector = embed_text(text).vector
        self.cache.put(key, vector)
        return vector
