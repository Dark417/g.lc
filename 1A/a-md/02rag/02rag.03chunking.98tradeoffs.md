# 02rag.03chunking.98tradeoffs Tradeoffs

> Which strategy fits which content, the knobs to turn, and how chunking fails.

## Index

- [1. When To Use Each Strategy](#1-when-to-use-each-strategy)
- [2. Knobs](#2-knobs)
- [3. Best Practices](#3-best-practices)
- [4. Comparison](#4-comparison)
- [5. Failure Modes](#5-failure-modes)

## 1. When To Use Each Strategy

Content shape decides the strategy.

| Content | Strategy | Why |
|---|---|---|
| Manuals, policies, specs with sections | Hierarchical | precise match + section context |
| Uniform prose, blogs, news | Fixed 300 / 20% | simple, predictable |
| Transcripts, emails, chats | Semantic | topic shifts without headings |
| Frequently Asked Questions (FAQs), tickets, product records | None | already one unit per file |
| Code, Markdown, special formats | Custom Lambda (recursive / syntax-aware) | boundaries need domain rules |
| Scanned Portable Document Format files (PDFs), tables, slides | Foundation Model (FM) or Bedrock Data Automation (BDA) parser + any of the above | parsing is the bottleneck |

- Don't chunk when the document is short enough to be one coherent unit
- Don't rely on chunking for structured data (tables in a Database (DB))
  - ⇒ text-to-Structured Query Language (SQL) ([02rag.04knowledge-bases.05stores-sql](02rag.04knowledge-bases.05stores-sql.md))

## 2. Knobs

Every knob trades precision, context, or cost.

**Chunk shape**

| Knob | Values | Trades | Change when |
|---|---|---|---|
| `maxTokens` (fixed) | 1–8192, default 300 | precision vs context per hit | misses nearby facts ⇒ larger; vague hits ⇒ smaller |
| `overlapPercentage` | 1–99, default 20 | boundary loss vs storage + duplicates | facts cut at boundaries |
| Parent / child `maxTokens` | default 1500 / 300 | context vs prompt tokens | parents overflow the prompt budget |
| `overlapTokens` | ≥ 1, default 60 | boundary loss vs duplication | same as overlap |

**Semantic, parsing, and query**

| Knob | Values | Trades | Change when |
|---|---|---|---|
| `breakpointPercentileThreshold` | 50–99, default 95 | chunk count vs coherence | chunks too big ⇒ lower it |
| `bufferSize` | 0–1, default 0 | distance stability vs sharpness | noisy breaks ⇒ 1 |
| Parsing strategy | default / FM / BDA | ingestion cost vs table + image fidelity | tables or scans in the corpus |
| Pre-retrieval | rewrite / decompose / Hypothetical Document Embeddings (HyDE) | latency + cost vs recall | multi-turn, compound, vague questions |

## 3. Best Practices

Each rule prevents a specific failure.

- Build a golden question set first, then compare strategies on recall@k and answer quality
  - ⇒ prevents choosing by intuition
- Keep `maxTokens` well under the embedding model limit
  - ⇒ prevents silent truncation
- Deterministic chunk ids from content + position
  - ⇒ re-ingest upserts instead of duplicating
- Plan the chunking choice before production ingest; test on a copy data source
  - ⇒ avoids a full re-ingest later
- Budget prompt tokens: k × chunk (or parent) size + instructions + answer
  - ⇒ prevents truncated context

## 4. Comparison

The deciding variable: does a matching passage need its surrounding section to be answerable?

| Option | What it is | Strength | Weakness | Choose when |
|---|---|---|---|---|
| Fixed size + overlap | Token window with overlap | Predictable, cheap, default-friendly | Cuts structure; duplicates | Baseline; uniform prose |
| Hierarchical | Child chunks matched, parents returned | Precision + context | Fewer results, more tokens per result | Long structured documents |
| Semantic | Breaks on embedding-distance jumps | Topic-coherent chunks | Ingestion cost; noisy on lists | Transcripts, long unstructured text |
| None | One chunk per file | No split errors | Blurry vectors for long files | Pre-chunked / short files |
| Custom Lambda | Your code after chunking | Any rule, any metadata | You operate it | Code, special formats, enrichment |
| LangChain / LlamaIndex splitters (Do It Yourself (DIY)) | Library splitters in your pipeline | Many splitters (recursive, Markdown, code) | You run the whole ingestion | DIY Retrieval-Augmented Generation (RAG) outside Bedrock Knowledge Base (KB) |

- **Default**: hierarchical (1500 / 300 / 60) for long structured docs, unless
  - documents are short or uniform ⇒ fixed 300 / 20%
  - topics drift without headings ⇒ semantic
- **Deciding variable**: does a matching passage need its surrounding section?
  - Yes ⇒ hierarchical
  - No ⇒ fixed

Pick: hierarchical, unless documents are short or uniform.

## 5. Failure Modes

Boundary and size failures hurt quality; immutability hurts change.

**Quality**

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Answer half-missing | Fact split across chunk boundary | Golden-set misses on boundary facts | Overlap; hierarchical; structure-aware split |
| Vague retrieval | Chunks too large / multi-topic | Low precision; many unrelated hits | Smaller chunks or hierarchical children |
| Context overflow | Parents × k exceed the prompt budget | Truncation, high token bills | Smaller parents; lower k; rerank |
| Fewer results than asked | Hierarchical children collapse into parents | Retrieve returns < numberOfResults | Expected; raise numberOfResults |

**Ingestion and change**

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Tables garbled | Default parser on complex PDFs | Retrieved text is word soup | FM or BDA parser |
| Stuck with a bad strategy | Chunking immutable per data source | Change request has no update path | New data source + re-ingest; test on a copy |
| Ingestion cost spike | Semantic chunking / FM parsing on a large corpus | Bedrock bill, slow ingestion jobs | Use only on the subsets that need it |
