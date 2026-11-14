# 02rag.04knowledge-bases.98tradeoffs Tradeoffs

> When a Bedrock Knowledge Base (KB) fits, which knobs matter, how it compares, and how it fails.

## Index

- [1. When To Use Or Not](#1-when-to-use-or-not)
- [2. Knobs](#2-knobs)
- [3. Best Practices](#3-best-practices)
- [4. Comparison](#4-comparison)
- [5. Failure Modes](#5-failure-modes)

## 1. When To Use Or Not

The deciding question is how much of the pipeline must be custom.

- **Use a Bedrock KB when**
  - Documents live in supported sources and standard chunking/parsing fits
  - You want citations and incremental sync without running pipelines
  - Agents need a retrieval tool with IAM-governed access
- **Use Do It Yourself (DIY) Retrieval-Augmented Generation (RAG) when**
  - Custom retrieval logic
    - Multi-index fusion, custom rerankers, graph traversal, per-chunk Access Control List (ACL) joins
  - Exotic sources or formats the KB can't parse even with a Lambda
  - You need full control of ingestion latency and batching
- **Use Q Business / Kendra when**
  - The goal is an employee assistant with many Software as a Service (SaaS) connectors and per-user ACLs out of the box
- **Don't use RAG when** the answer is an aggregation over tables
  - ⇒ Structured Query Language (SQL) KB or text-to-SQL ([05 Stores and SQL](02rag.04knowledge-bases.05stores-sql.md))

## 2. Knobs

Ingestion knobs are mostly immutable; query knobs change per call.

**Ingestion**

| Knob | Values | Trades | Change when |
|---|---|---|---|
| Embedding model + dims | Titan V2 256 / 512 / 1024; Cohere | recall vs storage | memory or recall issues (requires a new KB) |
| Chunking | FIXED / HIERARCHICAL / SEMANTIC / NONE | precision vs context ([02rag.03](02rag.03chunking.98tradeoffs.md)) | golden-set results; immutable per data source |
| Parsing | default / Foundation Model (FM) / Bedrock Data Automation (BDA) | fidelity vs ingestion cost | tables, scans, images |
| `dataDeletionPolicy` | DELETE / RETAIN | clean index vs keeping vectors | almost always DELETE |

**Query**

| Knob | Values | Trades | Change when |
|---|---|---|---|
| `numberOfResults` | 1–100, default 5 | recall vs prompt tokens | answers miss facts |
| `overrideSearchType` | HYBRID / SEMANTIC | exact-term recall vs simplicity | identifier-heavy ⇒ HYBRID |
| Metadata filter | operators in [03 Retrieve](02rag.04knowledge-bases.03retrieve.md) | precision + isolation vs sidecar upkeep | multi-tenant, time-bounded queries |
| Reranking | model + numberOfRerankedResults | precision vs latency + cost | top-k precision low |
| Prompt template | custom text | grounding, tone vs citation format | hallucinations, style |
| Guardrail | id + version | safety vs latency | user-facing apps |

## 3. Best Practices

Each rule prevents a specific failure.

- Create the index from code with a shared contract (name, fields, dims)
  - ⇒ prevents KB create failures and per-document ingestion errors
- Pass `clientToken` on `StartIngestionJob` and `CreateDataSource`
  - ⇒ retries and event redeliveries don't start duplicates
- Check job statistics, not just status
  - ⇒ `COMPLETE` with failed documents is common (bad sidecars, size limits)
- Put tenant / ACL attributes in sidecars and add the filter server-side on every query
  - ⇒ prevents cross-tenant leakage in a shared index
- Evaluate with Bedrock KB evaluations or Retrieval-Augmented Generation Assessment (RAGAS) on a golden set before changing knobs
  - See [04safety.03evaluations](../04safety/04safety.03evaluations.00index.md)
  - ⇒ prevents tuning by anecdote

## 4. Comparison

The deciding variable is how much of the pipeline must be custom.

| Option | What it is | Strength | Weakness | Choose when |
|---|---|---|---|---|
| Bedrock Knowledge Bases | Managed ingestion + Retrieve / RetrieveAndGenerate | No pipeline code; incremental sync; citations; Identity and Access Management (IAM); many stores | Fixed stages; chunking immutable; you trigger sync | Default for RAG on Amazon Web Services (AWS) |
| DIY RAG (LangChain / LlamaIndex + OpenSearch) | Your pipeline on your compute | Total control: splitters, fusion, rerankers, ACL joins | You own ingestion bugs, scaling, monitoring | Custom retrieval logic or sources |
| Amazon Q Business | Managed enterprise assistant | 40+ connectors, per-user ACLs, ready User Interface (UI) | Less control of prompts and models; per-user pricing | Employee assistant over SaaS data |
| Amazon Kendra (Generative Artificial Intelligence (GenAI) index) | Managed enterprise search | Connectors, ACL-aware ranking; usable as a KB type | Search-only; index pricing | Existing Kendra estate; search UI |

- **Default**: Bedrock KB with `Retrieve` + Converse, unless
  - you need retrieval logic the KB can't express ⇒ DIY
  - the product is an internal assistant with SaaS connectors and per-user ACLs ⇒ Q Business

Pick: Bedrock KB, unless the retrieval logic must be custom.

## 5. Failure Modes

Ingestion failures are often silent; access failures are loud.

**Setup and ingestion**

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| KB create fails | Index missing / wrong fields / dims mismatch / role lacks data access | Create error | Apply order; shared contract; data-access policy |
| Stale answers | No sync after document changes | Citations show old content | Event + scheduled sync; direct ingestion |
| Duplicate / missed sync | Concurrent triggers ⇒ ConflictException | Deferred events; job history | Queue + retry; scheduled sweep; clientToken |
| Silent document failures | Bad sidecar JavaScript Object Notation (JSON), oversized files, unsupported types | `numberOfDocumentsFailed` > 0 | Read failureReasons; fix and resync |
| Orphan vectors | Data source deleted with RETAIN | Answers cite deleted docs | DELETE policy; clean the index |

**Query and generation**

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Cross-tenant leak | Shared index, filter not enforced | Audit retrieval logs | Server-side mandatory filters; index per tenant |
| Fewer results than asked | Hierarchical chunking parent dedupe | Result count < numberOfResults | Expected; raise numberOfResults |
| Citations missing | Custom template dropped `$output_format_instructions$` | Empty `citations` | Restore the placeholder |
| Guardrail blocks valid answers | Over-strict policy | `guardrailAction = INTERVENED` rate | Tune guardrail ([04safety.01](../04safety/04safety.01guardrails.00index.md)) |
