# chunking.01why-chunk Why Chunk

> One vector per document matches nothing well; chunks give each vector one topic.

## Index

- [1. The Pain](#1-the-pain)
- [2. How Chunking Helps](#2-how-chunking-helps)
- [3. Picture](#3-picture)
- [4. Use Cases](#4-use-cases)
- [5. Token Approximation In Code](#5-token-approximation-in-code)

## 1. The Pain

Embedding models and generators both punish whole-document inputs.

- Embedding models have input limits (Titan V2: 8,192 tokens)
- They average everything into one vector
  - A 50-page manual as one vector matches every query weakly and none strongly
- Generation models pay per input token
- Accuracy drops for facts buried mid-context
  - "Lost in the middle", Liu et al., 2023

## 2. How Chunking Helps

Each chunk carries one topic, so its vector sits near queries about that topic.

- **Mechanism**
  - Each chunk carries one topic ⇒ its vector sits near queries about that topic
  - Retrieval returns only the passages needed ⇒ fewer tokens, sharper answers
- **What it costs**
  - More chunks = more vectors to store and search
  - Boundaries cut facts in half unless overlap or structure-aware splits are used

```python
# app/domain/_02rag_03chunking.py
@dataclass(frozen=True)
class Chunk:
    id: str
    text: str
    start_word: int  # offsets into the source: cite and re-chunk deterministically
    end_word: int
    level: str = "leaf"  # "parent" | "child" | "leaf"
    parent_id: str | None = None  # hierarchical: child -> parent link
    metadata: dict[str, object] = field(default_factory=dict)
```

## 3. Picture

Chunking sits between parsing and embedding; strategies differ in where they cut.

```text
doc ─► parse (text/FM/BDA) ─► chunk ─► [Lambda POST_CHUNKING]
    ─► embed ─► vector store

FIXED_SIZE    |──300──|
                   |──300──|            (20% overlap)
HIERARCHICAL  |─────────── parent 1500 ───────────|
              |c 300|c 300|c 300|c 300|c 300|     children embedded
SEMANTIC      |s1 s2 s3 ‖ s4 s5 ‖ s6 s7 s8|       ‖ = distance > p95
NONE          |──────────── whole file ───────────|
```

Notice that only hierarchical embeds one unit but returns another.

## 4. Use Cases

Content shape picks the strategy.

- Manuals and policies: hierarchical
- Frequently Asked Questions (FAQs): none (one entry per chunk)
- Transcripts and emails: semantic
- Code: recursive on syntax boundaries
- Full mapping: [98 Tradeoffs](chunking.98tradeoffs.md)

## 5. Token Approximation In Code

The local chunkers count words, not tokens.

- Tokens ≈ words × tokens_per_word (~1.3 for English, order of magnitude)
- Real tokenizers differ per model (Titan, Claude, Cohere)
  - Exact budgets need that model's tokenizer
- Bedrock Knowledge Base (KB) counts tokens itself
  - Local functions exist to show the mechanism and unit-test chunk shapes

```python
# app/service/_02rag_03chunking/chunkers.py
def tokens_to_words(tokens: int) -> int:
    return max(1, int(tokens / get_chunking_settings().tokens_per_word))


def approx_tokens(text: str) -> int:
    return math.ceil(len(_words(text)) * get_chunking_settings().tokens_per_word)


def _chunk_id(prefix: str, start: int, end: int, text: str) -> str:
    # Deterministic id: same content + position => same id => idempotent re-ingest (upsert, not duplicate).
    digest = hashlib.sha256(f"{start}:{end}:{text}".encode()).hexdigest()[:12]
    return f"{prefix}-{start}-{digest}"
```

```python
# app/config/_02rag_03chunking.py
# English averages ~0.75 words per token, i.e. ~1.3 tokens per word (order of magnitude).
tokens_per_word: float = 1.3
```
