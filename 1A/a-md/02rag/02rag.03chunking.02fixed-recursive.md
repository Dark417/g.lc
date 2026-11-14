# 02rag.03chunking.02fixed-recursive Fixed Size and Recursive

> The baseline sliding window, and the structure-aware splitter that keeps paragraphs whole.

## Index

- [1. Fixed Size With Overlap](#1-fixed-size-with-overlap)
  - [1.1 Mechanism](#11-mechanism)
  - [1.2 Bedrock Config](#12-bedrock-config)
  - [1.3 Strength And Limits](#13-strength-and-limits)
- [2. Recursive Structure-Aware](#2-recursive-structure-aware)

## 1. Fixed Size With Overlap

A window of `maxTokens` slides over the text with overlap.

### 1.1 Mechanism

Each window becomes one chunk.

→ slide a window of `maxTokens`  
→ advance by `maxTokens × (1 − overlap%)`  
→ each window = one chunk

- Code note: `fixed_size_chunks` approximates tokens by words
  - ~1.3 tokens per English word, order of magnitude

```python
# app/service/_02rag_03chunking/chunkers.py
def fixed_size_chunks(text: str, max_tokens: int = 300, overlap_percentage: int = 20, doc_id: str = "doc") -> list[Chunk]:
    if not 0 <= overlap_percentage < 100:
        raise ValueError("overlap_percentage must be in [0, 100)")
    words = _words(text)
    size = tokens_to_words(max_tokens)
    step = max(1, size - size * overlap_percentage // 100)  # advance by size x (1 - overlap%)
    chunks: list[Chunk] = []
    for start in range(0, len(words), step):
        end = min(start + size, len(words))
        body = " ".join(words[start:end])
        chunks.append(Chunk(id=_chunk_id(doc_id, start, end, body), text=body, start_word=start, end_word=end))
        if end == len(words):
            break
    return chunks
```

### 1.2 Bedrock Config

Bedrock `FIXED_SIZE` does the same with real tokens.

- `fixedSizeChunkingConfiguration { maxTokens 1–8192, overlapPercentage 1–99 }`
- Default chunking (no config) ≈ 300-token chunks that respect sentence boundaries (Knowledge Base (KB) user guide)

```python
# app/infra/_02rag_03chunking/bedrock_config.py
def fixed_size_config(max_tokens: int = 300, overlap_percentage: int = 20) -> Config:
    _check("maxTokens", max_tokens, 1, 8192)  # keep under the embedding model's limit
    _check("overlapPercentage", overlap_percentage, 1, 99)
    return {
        "chunkingConfiguration": {
            "chunkingStrategy": ChunkingStrategy.FIXED_SIZE.value,
            "fixedSizeChunkingConfiguration": {"maxTokens": max_tokens, "overlapPercentage": overlap_percentage},
        }
    }
```

### 1.3 Strength And Limits

Fixed size is the baseline every other strategy must beat.

- **Strength**: predictable size, cost, and latency
- **Limits**
  - Ignores structure: splits tables, lists, and sentences
  - Overlap stores ~overlap% more tokens
  - Overlap returns near-duplicate hits

## 2. Recursive Structure-Aware

Split on the coarsest separator that fits; recurse with finer ones.

- Not a Bedrock strategy
  - Common in LangChain / LlamaIndex, and inside custom Lambdas

→ try the coarsest separator (`\n\n` paragraphs)  
→ pieces under budget are merged greedily  
→ oversize pieces are split again with a finer separator (`\n`, `. `, space)

```python
# app/service/_02rag_03chunking/chunkers.py
DEFAULT_SEPARATORS = ["\n\n", "\n", ". ", " "]  # paragraph -> line -> sentence -> word


def recursive_split(text: str, max_tokens: int = 300, separators: list[str] | None = None) -> list[str]:
    seps = DEFAULT_SEPARATORS if separators is None else separators
    if approx_tokens(text) <= max_tokens:
        return [text] if text.strip() else []
    if not seps:
        return [c.text for c in fixed_size_chunks(text, max_tokens, 0)]  # no separator left: hard cut
    sep, finer = seps[0], seps[1:]
    pieces = [p for p in text.split(sep) if p.strip()]
    out: list[str] = []
    current = ""
    for piece in pieces:
        candidate = f"{current}{sep}{piece}" if current else piece
        if approx_tokens(candidate) <= max_tokens:
            current = candidate  # merge small pieces greedily
            continue
        if current:
            out.append(current)
        if approx_tokens(piece) > max_tokens:
            out.extend(recursive_split(piece, max_tokens, finer))  # recurse with finer separators
            current = ""
        else:
            current = piece
    if current:
        out.append(current)
    return out
```

- **Strength**: keeps paragraphs and sentences whole
- **Limits**
  - Chunk sizes vary widely
  - Headings may end up separated from their content
