# 02rag.04knowledge-bases.01managed-rag Why Managed Retrieval-Augmented Generation (RAG)

> Most Retrieval-Augmented Generation (RAG) bugs live in ingestion; a Knowledge Base takes the ingestion pipeline off your hands.

## Index

- [1. The Pain And Prior Art](#1-the-pain-and-prior-art)
- [2. How A Knowledge Base (KB) Helps](#2-how-a-knowledge-base-kb-helps)
- [3. Picture](#3-picture)
  - [3.1 Ingestion](#31-ingestion)
  - [3.2 Query](#32-query)
- [4. Use Cases And Limits](#4-use-cases-and-limits)

## 1. The Pain And Prior Art

Do It Yourself (DIY) RAG means running every pipeline stage yourself.

- **The pain**
  - DIY RAG = crawler + parser + chunker + embedder + upsert + delete detection + retries + monitoring
  - Most bugs live in ingestion
    - Stale vectors
    - Orphans after deletes
    - Duplicates after retries
- **Prior art**
  - LangChain / LlamaIndex pipelines on your compute
  - Kendra: managed enterprise search, connectors, no generation step

## 2. How A Knowledge Base (KB) Helps

The KB detects changes, runs the stages declaratively, and exposes two query Application Programming Interfaces (APIs).

- Change detection per document ⇒ incremental sync
- Parsing, chunking, embedding configured declaratively ([02rag.03chunking](02rag.03chunking.00index.md))
- Retrieval API with hybrid search, filters, reranking
- Generation API with citations

```python
# app/infra/_02rag_04knowledge_bases.py
def _agent() -> Any:
    return aws.client("bedrock-agent")  # control plane: data sources, ingestion jobs (= "sync")


def _runtime() -> Any:
    return aws.client("bedrock-agent-runtime")  # data plane: Retrieve, RetrieveAndGenerate
```

## 3. Picture

Ingestion runs asynchronously; queries go through one of two APIs.

### 3.1 Ingestion

`StartIngestionJob` drives every stage, under the KB service role.

```text
S3 kb-docs/ + <file>.metadata.json
  │
  ▼
scan + change detection ─► parse ─► chunk ─► [Lambda]   (02rag.03)
  │
  ▼
embed (Titan V2, 02rag.01) ─► OpenSearch a-kb-index (02rag.02)

KB role a-kb: s3:GetObject, bedrock:InvokeModel, aoss:APIAccessAll, kms
```

Notice that the KB role, not the app, needs Simple Storage Service (S3), model, Amazon OpenSearch Serverless (AOSS), and Key Management Service (KMS) access.

### 3.2 Query

Retrieve stops at chunks; RetrieveAndGenerate continues to an answer.

```text
Retrieve:
  embed query ─► kNN / hybrid + filter ─► [rerank]
              ─► chunks + scores + locations

RetrieveAndGenerate:
  [query decomposition] ─► Retrieve ─► prompt ($search_results$)
              ─► LLM ─► [guardrail] ─► answer + citations + sessionId
```

Notice that RetrieveAndGenerate wraps Retrieve; the retrieval knobs are shared.

## 4. Use Cases And Limits

A KB fits standard document Question and Answer (Q&A) and agent retrieval tools.

- **Common use cases**
  - Internal Q&A over S3 / Confluence / SharePoint
  - The retrieval tool behind a Bedrock Agent (`06agents` (planned))
  - Customer-support assistants with source links
- **Limits**
  - Fixed pipeline stages
    - Custom logic only via parsing prompts and a post-chunking Lambda
  - Quotas on file size, documents per job, and metadata size (check the quotas page)
