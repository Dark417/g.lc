# chunking.99interview Interview Questions

> Level 4 (L4) baseline and Level 5 (L5) extensions for chunking, parsing, and pre-retrieval.

## Index

- [1. Core Questions](#1-core-questions)
  - [Q1 Choosing A Chunk Size](#q1-choosing-a-chunk-size)
  - [Q2 Hierarchical Chunking](#q2-hierarchical-chunking)
  - [Q3 Semantic Breakpoints](#q3-semantic-breakpoints)
  - [Q4 Changing Chunking On A Live Knowledge Base (KB)](#q4-changing-chunking-on-a-live-knowledge-base-kb)
  - [Q5 Custom Parser](#q5-custom-parser)
  - [Q6 Rewriting vs Decomposition vs Hypothetical Document Embeddings (HyDE)](#q6-rewriting-vs-decomposition-vs-hypothetical-document-embeddings-hyde)
- [2. L5-Only Questions](#2-l5-only-questions)
  - [Q7 Spec Tables Fail](#q7-spec-tables-fail)
  - [Q8 Evaluating Strategies](#q8-evaluating-strategies)
  - [Q9 Chunks Lack Context](#q9-chunks-lack-context)

## 1. Core Questions

Each question has an L4 answer and an L5 extension.

### Q1 Choosing A Chunk Size

**Q:** How do you choose a chunk size?

**L4 answer**

- Start at ~300 tokens with ~20% overlap
- Smaller = precise matches, less context
- Larger = more context, vaguer matches

**L5 extra**

- Decide with a golden set: recall@k and answer faithfulness per configuration
- Budget the prompt: k × chunk size must fit with instructions and answer
- If answers need surrounding context, switch to hierarchical
  - Rather than just growing chunks

### Q2 Hierarchical Chunking

**Q:** Explain hierarchical chunking and its catch.

**L4 answer**

- Parents (large) contain children (small)
- Children are embedded and matched
- Parents are returned to the model

**L5 extra**

- Several children of one parent dedupe to one parent
  - ⇒ fewer results than `numberOfResults`
- Each result costs more tokens ⇒ fewer results fit
- Overlap applies between neighbours to soften boundary cuts

### Q3 Semantic Breakpoints

**Q:** How does semantic chunking decide where to cut?

**L4 answer**

- Embed sentences
- Measure distance between neighbours
- Cut where it jumps

**L5 extra**

- Cut where distance exceeds the Nth percentile (default 95) of all distances in the doc
  - ⇒ relative, not absolute
- `bufferSize` smooths distances with neighbour sentences
- Costs embedding calls at ingestion; `maxTokens` still caps size

### Q4 Changing Chunking On A Live Knowledge Base (KB)

**Q:** You want to change chunking on a live Knowledge Base. What happens?

**L4 answer**

- Chunking is set per data source and can't be changed after creation
- Create a new data source with the new strategy and re-ingest

**L5 extra**

- Run old and new data sources side by side
  - Evaluate on the golden set, then delete the old one
- `dataDeletionPolicy = DELETE` cleans vectors of the removed data source
- Budget a full re-embed: corpus tokens × embedding price

### Q5 Custom Parser

**Q:** When do you need a custom parser?

**L4 answer**

- Portable Document Format files (PDFs) with tables, scans, slides, or images
- Use the Foundation Model (FM) parser or Bedrock Data Automation (BDA) parser

**L5 extra**

- Parsing errors cannot be fixed downstream by chunking or retrieval
- FM parsing costs per page
  - ⇒ apply to the subset of documents that need it (separate data source)
- A custom parsing prompt can force Markdown tables
  - Preserves structure for chunking

### Q6 Rewriting vs Decomposition vs Hypothetical Document Embeddings (HyDE)

**Q:** Query rewriting vs decomposition vs HyDE?

**L4 answer**

- Rewriting: make the query standalone and search-friendly
- Decomposition: split compound questions into sub-queries
- HyDE: embed a hypothetical answer instead of the question

**L5 extra**

- Each adds a Large Language Model (LLM) call ⇒ latency
  - Apply conditionally (multi-turn, long questions)
- HyDE helps when questions and documents use different vocabulary
  - Risky for factual edge cases
- Bedrock KB exposes decomposition natively (`QUERY_DECOMPOSITION`)

## 2. L5-Only Questions

Depth, scale, and design ownership.

### Q7 Spec Tables Fail

**Q:** Retrieval works for prose but fails on product spec tables. Fix it.

**L5 answer**

- Diagnose: inspect retrieved chunks
  - Flattened tables lose row/column relations
- Parse with FM/BDA into Markdown tables
  - Keep each table within one chunk (custom Lambda or NONE per table)
- Add metadata (product, version) for filtering
- Consider hybrid search for model numbers
- If questions are aggregations over rows
  - ⇒ structured store + text-to-Structured Query Language (SQL) instead of Retrieval-Augmented Generation (RAG)

### Q8 Evaluating Strategies

**Q:** Design an evaluation to pick a chunking strategy.

**L5 answer**

- Golden set: 100–300 real questions with labeled source passages (order of magnitude)
- Index the corpus once per strategy
  - Separate data sources, or a local pipeline
- Metrics
  - recall@k / context precision
  - Answer faithfulness and correctness ([evaluations](../04safety/evaluations.00index.md))
  - Tokens per answer
  - Ingestion cost
- Pick the cheapest strategy within the quality target
  - Record the decision, since it is costly to change

### Q9 Chunks Lack Context

**Q:** Chunks lack context ("it", "the above section"). What do you do?

**L5 answer**

- Contextual headers: prepend title and section path at chunking time
- Contextual retrieval: an LLM writes a 1–2 sentence context per chunk before embedding
  - Ingestion cost up
- Hierarchical chunking returns the surrounding section anyway
- Measure the gain
  - Enrichment multiplies ingestion cost by roughly one LLM call per chunk
