# chunking.03hierarchical Hierarchical Chunking

> Match small child chunks for precision, return their large parents for context.

## Index

- [1. Mechanism](#1-mechanism)
- [2. Bedrock Config](#2-bedrock-config)
- [3. Strength, Costs, And Limits](#3-strength-costs-and-limits)

## 1. Mechanism

Two levels: parents for context, children for matching.

→ split into large parent chunks (e.g. 1,500 tokens)  
→ split each parent into children (e.g. 300 tokens), with `overlapTokens` between neighbours  
→ embed children only  
→ at query time, match children, then replace each with its parent

```python
# app/service/_02rag_03chunking/chunkers.py
def hierarchical_chunks(text, parent_max_tokens=1500, child_max_tokens=300, overlap_tokens=60, doc_id="doc"):
    words = _words(text)
    p_size, c_size, ov = tokens_to_words(parent_max_tokens), tokens_to_words(child_max_tokens), tokens_to_words(overlap_tokens)
    if ov >= c_size:
        raise ValueError("overlap must be smaller than the child size")
    parents: list[Chunk] = []
    children: list[Chunk] = []
    p_start = 0
    while p_start < len(words):
        p_end = min(p_start + p_size, len(words))
        p_text = " ".join(words[p_start:p_end])
        parent = Chunk(_chunk_id(doc_id, p_start, p_end, p_text), p_text, p_start, p_end, level="parent")
        parents.append(parent)
        c_start = p_start
        while c_start < p_end:
            c_end = min(c_start + c_size, p_end)
            c_text = " ".join(words[c_start:c_end])
            # child links to its parent: the only thing the retriever needs to expand
            children.append(Chunk(_chunk_id(doc_id, c_start, c_end, c_text), c_text, c_start, c_end, "child", parent.id))
            if c_end == p_end:
                break
            c_start = c_end - ov  # overlap between neighbouring children
        if p_end == len(words):
            break
        p_start = p_end - ov
    return parents, children


def expand_to_parents(child_hits: list[Chunk], parents: list[Chunk]) -> list[Chunk]:
    """Retrieve child, return parent: dedupe by parent id, keep the best-ranked child's order."""
    by_id = {p.id: p for p in parents}
    seen: set[str] = set()
    out: list[Chunk] = []
    for c in child_hits:
        if c.parent_id and c.parent_id not in seen and c.parent_id in by_id:
            seen.add(c.parent_id)
            out.append(by_id[c.parent_id])
    return out
```

## 2. Bedrock Config

Bedrock `HIERARCHICAL` takes two level configurations and one overlap.

- `hierarchicalChunkingConfiguration { levelConfigurations: [parent, child], overlapTokens }`
- Each `maxTokens` 1–8192; `overlapTokens` ≥ 1
- Console defaults: 1500 / 300 / 60

```python
# app/infra/_02rag_03chunking/bedrock_config.py
def hierarchical_config(parent_max_tokens: int = 1500, child_max_tokens: int = 300, overlap_tokens: int = 60) -> Config:
    _check("parent maxTokens", parent_max_tokens, 1, 8192)
    _check("child maxTokens", child_max_tokens, 1, 8192)
    _check("overlapTokens", overlap_tokens, 1)
    if child_max_tokens >= parent_max_tokens:
        raise ValueError("child chunks must be smaller than parent chunks")
    return {
        "chunkingConfiguration": {
            "chunkingStrategy": ChunkingStrategy.HIERARCHICAL.value,
            "hierarchicalChunkingConfiguration": {
                "levelConfigurations": [{"maxTokens": parent_max_tokens}, {"maxTokens": child_max_tokens}],  # parent first
                "overlapTokens": overlap_tokens,
            },
        }
    }
```

## 3. Strength, Costs, And Limits

Precision and context, paid for in result count and tokens.

- **Strength**: precise matching (small vectors) and rich context (large passages)
- **Costs and limits**
  - Several matching children of one parent collapse to one result
    - ⇒ fewer results than `numberOfResults`
  - Each result is a full parent ⇒ more prompt tokens per result
  - Parent size must stay within the generator's budget × k
