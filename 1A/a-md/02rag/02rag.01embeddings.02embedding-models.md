# 02rag.01embeddings.02embedding-models Embedding Models

> How an encoder turns text into a vector, and the Titan V2, Cohere, and caching knobs on Bedrock.

## Index

- [1. Embedding Mechanism](#1-embedding-mechanism)
- [2. Titan Text Embeddings V2](#2-titan-text-embeddings-v2)
- [3. Cohere Embed](#3-cohere-embed)
- [4. Multimodal Embeddings](#4-multimodal-embeddings)
- [5. Embedding Cache](#5-embedding-cache)
- [6. Limits](#6-limits)

## 1. Embedding Mechanism

An encoder model maps text to a vector so that similar meanings land close.

- **Training**: contrastive, so similar meanings land close together
- **Fixed length**: vector length is fixed per model setting, whatever the input length
- **Averaging**: long input is averaged into one point
  - ⇒ one vector per chunk, not per book

```python
# app/domain/_02rag_01embeddings.py
Vector = list[float]


@dataclass(frozen=True)
class Embedding:
    vector: Vector
    model_id: str
    dimensions: int
    input_tokens: int = 0
    binary: list[int] | None = None  # Titan V2 embeddingTypes=["binary"]: one 0/1 per dimension


class Embedder(Protocol):
    def embed(self, text: str, input_type: InputType = InputType.SEARCH_DOCUMENT) -> Vector: ...
```

## 2. Titan Text Embeddings V2

Titan V2 (`amazon.titan-embed-text-v2:0`) is the Amazon Web Services (AWS) default: symmetric, one text per call.

- **`dimensions`**: 256 | 512 | 1024 (default 1024)
  - AWS reports ~99% (512) and ~97% (256) of 1024-dim retrieval accuracy
    - Source: Titan V2 launch blog, 2024
  - 4x fewer dims = 4x less storage and faster distance math
- **`normalize`**: default true
  - ⇒ unit vectors, so dot = cosine
- **`embeddingTypes`**: `["float"]` (default), `["binary"]`, or both
  - Binary = one bit per dim
  - Used for Hamming pre-search + float rescoring
- **Input limit**: 8,192 tokens / 50,000 characters (Bedrock model parameters page)
- **Symmetric**: one text per call, same embedding for query and document

```python
# app/infra/_02rag_01embeddings.py
TITAN_DIMENSIONS = (256, 512, 1024)


def titan_body(text: str, dimensions: int = 1024, normalize: bool = True, binary: bool = False) -> dict[str, Any]:
    if dimensions not in TITAN_DIMENSIONS:
        raise ValueError(f"Titan V2 dimensions must be one of {TITAN_DIMENSIONS}")
    return {
        "inputText": text,  # longer than 8,192 tokens is rejected: chunk first
        "dimensions": dimensions,
        "normalize": normalize,  # keep true so dot == cosine and L2 ranks the same
        "embeddingTypes": ["float", "binary"] if binary else ["float"],
    }
```

```python
# app/infra/_02rag_01embeddings.py
RETRYABLE_CODES = {"ThrottlingException", "ModelNotReadyException", "ServiceUnavailableException"}


def _invoke(model_id: str, body: dict[str, Any]) -> dict[str, Any]:
    # adaptive retries in the client handle most throttling;
    # the outer retry covers bursts in batch jobs.
    def call() -> dict[str, Any]:
        resp = aws.client("bedrock-runtime").invoke_model(
            modelId=model_id, body=json.dumps(body),
            contentType="application/json", accept="application/json",
        )
        return json.loads(resp["body"].read())

    return call_with_retry(call, _retryable, max_attempts=4)
```

- **Catch on bulk embedding**
  - `embed_batch` parallelism is bounded by the account's InvokeModel quota
  - For millions of chunks, use Bedrock batch inference (`CreateModelInvocationJob`)
    - Asynchronous; priced below on-demand for supported models
  - Or let a Knowledge Base ingestion job do it ([02rag.04knowledge-bases.02ingestion](02rag.04knowledge-bases.02ingestion.md))

## 3. Cohere Embed

Cohere (`cohere.embed-english-v3`, `cohere.embed-multilingual-v3`, Embed v4 where available) is asymmetric.

- **Asymmetric `input_type`**
  - `search_document` at index time
  - `search_query` at query time
  - Wrong type ⇒ lower recall, no error
- **Batch**: up to 96 texts per call
- **Truncation**: v3 truncates at ~512 tokens (check the model page)
  - `truncate`: `NONE` (error on long input) | `START` | `END` (default)
  - `NONE` surfaces chunking bugs
- **Server-side `embedding_types`**: float, int8, uint8, binary, ubinary

```python
# app/domain/_02rag_01embeddings.py
class InputType(StrEnum):
    # Asymmetric models (Cohere v3+) embed documents and queries differently;
    # Titan V2 has no such flag.
    SEARCH_DOCUMENT = "search_document"
    SEARCH_QUERY = "search_query"
```

```python
# app/infra/_02rag_01embeddings.py
COHERE_MAX_TEXTS = 96  # Cohere Embed v3 on Bedrock: texts per request


def cohere_body(texts: list[str], input_type: InputType) -> dict[str, Any]:
    if len(texts) > COHERE_MAX_TEXTS:
        raise ValueError(f"Cohere accepts at most {COHERE_MAX_TEXTS} texts per call")
    return {"texts": texts, "input_type": input_type.value,
            "truncate": "NONE", "embedding_types": ["float"]}  # NONE: fail loudly on long input


def embed_cohere(texts: list[str], input_type: InputType) -> list[Vector]:
    out = _invoke(get_embeddings_settings().cohere_model_id, cohere_body(texts, input_type))
    emb = out["embeddings"]
    return emb["float"] if isinstance(emb, dict) else emb  # dict shape when embedding_types is set
```

## 4. Multimodal Embeddings

Images and text can share one vector space.

- Titan Multimodal Embeddings and Nova multimodal embeddings put images and text in one space
  - Lecture 22, see [01bedrock](../01bedrock/01bedrock.01converse.00index.md)
- No repo code (gap)

## 5. Embedding Cache

Cache vectors by a hash of everything that changes the vector.

- **Key** = `sha256(model | dims | normalize | text)`
  - Re-ingest only re-embeds changed chunks
  - A model or dims change yields new keys ⇒ re-embed
- **Pays off on re-ingest**: cost is per input token
  - It does not help with first-time ingestion
- **Production store**: DynamoDB / ElastiCache with a Time To Live (TTL) (the repo uses an in-memory adapter for tests)

```python
# app/infra/_02rag_01embeddings.py
def cache_key(text: str, model_id: str, dimensions: int, normalize: bool) -> str:
    # A cache keyed by text alone serves vectors from the old model after an upgrade
    raw = f"{model_id}|{dimensions}|{int(normalize)}|{text}".encode()
    return hashlib.sha256(raw).hexdigest()


class CachedTitanEmbedder:
    def __init__(self, cache: EmbeddingCache) -> None:
        self.cache = cache

    def embed(self, text: str, input_type: InputType = InputType.SEARCH_DOCUMENT) -> Vector:
        # input_type is ignored: Titan V2 is symmetric.
        s = get_embeddings_settings()
        key = cache_key(text, get_settings().embed_model_id, s.dimensions, s.normalize)
        cached = self.cache.get(key)
        if cached is not None:
            return cached
        vector = embed_text(text).vector
        self.cache.put(key, vector)
        return vector
```

```python
# app/config/_02rag_01embeddings.py
class EmbeddingsSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="A_EMBEDDINGS_", env_file=".env", extra="ignore")

    dimensions: int = 1024  # 256 | 512 | 1024: smaller = less storage, faster search, lower recall
    normalize: bool = True  # unit-length output; required for dot product == cosine
    cohere_model_id: str = "cohere.embed-english-v3"  # contrast: asymmetric input_type
    batch_workers: int = 8  # parallel InvokeModel calls; bounded by the account's TPM/RPM quota
```

## 6. Limits

Embeddings are not a universal representation.

- Embeddings from different models (or dims) are not comparable

  ⇒ changing the model = re-embed the whole corpus

- Embeddings blur exact tokens (Identifiers (IDs), numbers, negation)
  - ⇒ hybrid search ([07 Hybrid search](02rag.01embeddings.07hybrid-rerank.md))
- Domain jargon the encoder never saw clusters poorly
  - ⇒ test on your data before choosing
