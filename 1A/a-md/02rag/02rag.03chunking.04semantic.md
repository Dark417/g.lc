# 02rag.03chunking.04semantic Semantic Chunking

> Cut where the embedding distance between consecutive sentences jumps.

## Index

- [1. Mechanism](#1-mechanism)
- [2. Bedrock Config](#2-bedrock-config)
- [3. Strength And Limits](#3-strength-and-limits)
- [4. Test Embedder](#4-test-embedder)

## 1. Mechanism

Breakpoints follow topic shifts measured by embeddings.

→ split into sentences  
→ embed each sentence, with `bufferSize` neighbours on each side for stability  
→ distance between consecutive embeddings  
→ cut where the distance exceeds the `breakpointPercentileThreshold` percentile of all distances  
→ enforce `maxTokens` as a hard cap

```python
# app/service/_02rag_03chunking/chunkers.py
def percentile(values: list[float], p: float) -> float:
    """Nearest-rank percentile (p in 0–100)."""
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = max(0, min(len(ordered) - 1, math.ceil(p / 100 * len(ordered)) - 1))
    return ordered[rank]


def semantic_chunks(text, embedder: Embedder, buffer_size=0, breakpoint_percentile_threshold=95, max_tokens=300, doc_id="doc"):
    sentences = split_sentences(text)
    if len(sentences) <= 1:
        return no_chunking(text, doc_id)
    windows = [  # each sentence plus buffer_size neighbours per side
        " ".join(sentences[max(0, i - buffer_size) : i + buffer_size + 1]) for i in range(len(sentences))
    ]
    vectors = [embedder.embed(w) for w in windows]  # one embedding call per sentence window
    distances = [_cosine_distance(vectors[i], vectors[i + 1]) for i in range(len(vectors) - 1)]
    threshold = percentile(distances, breakpoint_percentile_threshold)  # relative to this doc

    chunks: list[Chunk] = []
    group: list[str] = []
    word_pos = 0
    group_start = 0
    for i, sentence in enumerate(sentences):
        candidate = group + [sentence]
        if group and approx_tokens(" ".join(candidate)) > max_tokens:
            body = " ".join(group)  # size cap reached before a semantic break
            chunks.append(Chunk(_chunk_id(doc_id, group_start, word_pos, body), body, group_start, word_pos))
            group, group_start = [sentence], word_pos
        else:
            group = candidate
        word_pos += len(_words(sentence))
        if i < len(distances) and distances[i] > threshold:  # semantic break
            body = " ".join(group)
            chunks.append(Chunk(_chunk_id(doc_id, group_start, word_pos, body), body, group_start, word_pos))
            group, group_start = [], word_pos
    if group:
        body = " ".join(group)
        chunks.append(Chunk(_chunk_id(doc_id, group_start, word_pos, body), body, group_start, word_pos))
    return chunks
```

## 2. Bedrock Config

Bedrock `SEMANTIC` exposes the same three knobs.

- `semanticChunkingConfiguration { maxTokens 1–8192, bufferSize 0–1, breakpointPercentileThreshold 50–99 }`
- Console defaults: 300 / 0 / 95
- Higher threshold ⇒ fewer breaks ⇒ larger chunks

```python
# app/infra/_02rag_03chunking/bedrock_config.py
def semantic_config(max_tokens: int = 300, buffer_size: int = 0, breakpoint_percentile_threshold: int = 95) -> Config:
    _check("maxTokens", max_tokens, 1, 8192)
    _check("bufferSize", buffer_size, 0, 1)  # neighbour sentences per side
    _check("breakpointPercentileThreshold", breakpoint_percentile_threshold, 50, 99)
    return {
        "chunkingConfiguration": {
            "chunkingStrategy": ChunkingStrategy.SEMANTIC.value,
            "semanticChunkingConfiguration": {
                "maxTokens": max_tokens,
                "bufferSize": buffer_size,
                "breakpointPercentileThreshold": breakpoint_percentile_threshold,
            },
        }
    }
```

## 3. Strength And Limits

Topic-coherent chunks at an ingestion cost.

- **Strength**: boundaries follow topic shifts, even without headings
- **Limits**
  - One embedding call per sentence (window) during ingestion ⇒ cost and time
    - Bedrock uses a foundation model during ingestion
  - Short, list-like text produces noisy distances ⇒ erratic chunks

## 4. Test Embedder

Semantic chunking needs an `Embedder`; tests inject a deterministic fake.

```python
# app/domain/_02rag_03chunking.py
class Embedder(Protocol):
    def embed(self, text: str) -> Vector: ...
```

```python
# app/service/_02rag_03chunking/chunkers.py
class HashingEmbedder:
    """Hashed bag of words, normalized. Deterministic, no AWS.

    Captures word overlap, not meaning: enough to see breakpoints between unrelated topics.
    """

    def __init__(self, dims: int = 256) -> None:
        self.dims = dims

    def embed(self, text: str) -> Vector:
        v = [0.0] * self.dims
        for w in re.findall(r"[a-z0-9]+", text.lower()):
            v[int(hashlib.md5(w.encode()).hexdigest(), 16) % self.dims] += 1.0
        n = math.sqrt(sum(x * x for x in v)) or 1.0
        return [x / n for x in v]
```
