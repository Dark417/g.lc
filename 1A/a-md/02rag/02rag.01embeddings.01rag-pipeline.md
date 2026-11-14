# 02rag.01embeddings.01rag-pipeline Retrieval-Augmented Generation (RAG) Pipeline

> Why retrieval-augmented generation exists and how index time differs from query time.

## Index

- [1. Why Retrieval-Augmented Generation (RAG) Exists](#1-why-retrieval-augmented-generation-rag-exists)
  - [1.1 The Pain And Prior Art](#11-the-pain-and-prior-art)
  - [1.2 RAG Mechanism And Use Cases](#12-rag-mechanism-and-use-cases)
- [2. Index Time vs Query Time](#2-index-time-vs-query-time)
  - [2.1 Picture](#21-picture)
  - [2.2 Budgets](#22-budgets)

## 1. Why Retrieval-Augmented Generation (RAG) Exists

RAG moves knowledge out of model weights and into a searchable index.

### 1.1 The Pain And Prior Art

A Large Language Model (LLM) alone cannot answer from private, recent, or citable data.

- **The pain**
  - An LLM's knowledge is frozen at training time and excludes private data
  - Long prompts with "all the documents" exceed the context window
    - They also cost per token
  - Fine-tuning teaches style and format better than facts
    - It cannot cite ([01bedrock.02customization](../01bedrock/01bedrock.02customization.00index.md))
- **Prior art**
  - Keyword search (Best Matching 25 (BM25), inverted index)
    - Exact terms
    - No synonyms or paraphrase
  - Enterprise search (Kendra)
    - Good connectors
    - Rank-only, no generation

### 1.2 RAG Mechanism And Use Cases

RAG (Lewis et al., 2020) conditions generation on retrieved passages.

- **Mechanism**
  - Retrieve passages with a dense retriever
  - Condition generation on them
  - Knowledge lives in the index ⇒ update = re-embed changed chunks
- **Common use cases**
  - Internal docs Question and Answer (Q&A), support assistants, policy lookups
  - Code and runbook search for agents
  - Semantic cache ("similar question already answered")

```python
# app/infra/_02rag_01embeddings.py
def embed_text(text: str, dimensions: int | None = None, normalize: bool | None = None, binary: bool = False) -> Embedding:
    """One text -> one Titan V2 embedding.

    Catch: the SAME model id + dimensions + normalize must be used at index time
    and query time, or similarity scores are meaningless.
    """
    s = get_embeddings_settings()
    model_id = get_settings().embed_model_id
    dims = dimensions or s.dimensions
    body = titan_body(text, dims, s.normalize if normalize is None else normalize, binary)
    out = _invoke(model_id, body)
    ...
```

- **Limit**
  - Retrieval fails silently: a wrong chunk produces a fluent wrong answer

    ⇒ evaluate retrieval separately from generation ([04safety.03evaluations](../04safety/04safety.03evaluations.00index.md))

## 2. Index Time vs Query Time

The same embedding model sits on both paths; everything else differs.

### 2.1 Picture

Index time runs as a batch; query time runs per request.

```text
INDEX TIME (batch, async)          QUERY TIME (online, per request)
docs in S3                         user question
  │                                  │
  ▼                                  ▼
parse (text, tables, OCR)          [opt] rewrite / decompose / HyDE
  │                                  │
  ▼                                  ▼
chunk (02rag.03chunking)           embed(question)  same model+dims+norm
  │                                  │
  ▼                                  ▼
embed(chunk) Titan V2 / Cohere     kNN (ANN) + filter  [hybrid: + BM25]
  │                                  │
  ▼                                  ▼
store {vector, text, metadata} ◄── top-k ─► [rerank] ─► prompt ─► LLM
                                                  ─► answer + citations
```

Notice that both paths call the same `embed`; the store is the only shared state.

- Pre-retrieval steps (rewrite, decompose, Hypothetical Document Embeddings (HyDE)): [02rag.03chunking.06pre-retrieval-metadata](02rag.03chunking.06pre-retrieval-metadata.md)
- Chunking: [02rag.03chunking](02rag.03chunking.00index.md)

```python
# app/infra/_02rag_01embeddings.py
def embed_batch(texts: list[str], workers: int | None = None) -> list[Embedding]:
    """Index time: many texts via parallel single-text calls (Titan V2 has no
    multi-text body). Order is preserved."""
    n = workers or get_embeddings_settings().batch_workers
    with ThreadPoolExecutor(max_workers=n) as pool:
        return list(pool.map(embed_text, texts))  # query time calls embed_text directly
```

### 2.2 Budgets

Each path is bound by a different resource.

- **Index time is throughput-bound**
  - Cost = input tokens embedded, once per chunk version
- **Query time is latency-bound**
  - Budget, order of magnitude
    - Embed: ~tens of ms
    - Approximate Nearest Neighbor (ANN): ~ms to tens of ms
    - LLM: ~seconds

⇒ the LLM dominates latency  
⇒ retrieval quality dominates correctness
