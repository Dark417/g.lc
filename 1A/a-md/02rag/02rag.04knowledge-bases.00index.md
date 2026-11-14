# 02rag.04knowledge-bases Bedrock Knowledge Bases

> Entry point for managed Retrieval-Augmented Generation (RAG) on Bedrock: ingestion jobs, Retrieve, RetrieveAndGenerate, filters, and freshness.

## Index

- [1. Source And Scope](#1-source-and-scope)
- [2. One-Minute Version](#2-one-minute-version)
- [3. File Index](#3-file-index)
- [4. Code Map](#4-code-map)
- [References](#references)

## 1. Source And Scope

This component wires embeddings, chunking, and the vector store into one managed pipeline.

- Lectures: AIP-C01 #15, #16, #21 (retrieval side), #38 (structured data, doc only)
  - Slides p.36–38, 49–51, 76–81
- Scope: Python + Terraform
- Terraform: [modules/02rag_04knowledge_bases](../../terraform/modules/02rag_04knowledge_bases/main.tf)
  - `aws_bedrockagent_knowledge_base.main`
    - `a-kb`, Titan V2 1024 dims
    - OpenSearch Serverless `a-vectors` / `a-kb-index`
  - `aws_bedrockagent_data_source.s3`
    - `kb-docs/`, hierarchical chunking, `DELETE` policy
  - Uses `aws_iam_role.kb` and the collection from [02rag.02opensearch](02rag.02opensearch.00index.md)
- Code
  - `app/infra/_02rag_04knowledge_bases.py`: ingestion jobs, Retrieve, RetrieveAndGenerate, citations, sidecars
  - `app/service/_02rag_04knowledge_bases.py`: freshness
- Apply order

  → collection ([02rag.02opensearch](02rag.02opensearch.03serverless.md))  
  → index (`create_kb_index` in `app/infra/_02rag_02opensearch.py`)  
  → Knowledge Base (KB) (this component)

- Numbers: Bedrock User Guide (Knowledge Bases) and the bedrock-agent / bedrock-agent-runtime Application Programming Interface (API) models, read 2026-11, unless marked "order of magnitude"

## 2. One-Minute Version

A Knowledge Base is a managed RAG pipeline plus retrieval and generation APIs.

- **What**: data source → parse → chunk → embed → vector store, plus retrieval and generation APIs
- **Why**
  - Removes the ingestion plumbing
    - Crawling, change detection, chunking, embedding, upserts, deletes
  - One API call returns a grounded answer with citations
- **How**
  - Ingestion job ("sync") per data source
    - Only new, changed, or deleted files are processed
  - `Retrieve` = search only (you build the prompt)
  - `RetrieveAndGenerate` = search + prompt + model + citations
    - `sessionId` for follow-ups
  - Knobs per query
    - `numberOfResults`, `overrideSearchType` (HYBRID / SEMANTIC), metadata `filter`
    - Reranking, guardrail, prompt template
- **Catch**
  - The vector index must exist with the right fields and dims before the KB (bring-your-own store)
  - Chunking is fixed per data source ⇒ change = new data source + re-ingest
  - Sync is not automatic for Simple Storage Service (S3) ⇒ you trigger it (schedule or event)
  - One running ingestion job per data source
    - ⇒ concurrent triggers get `ConflictException`
  - `RetrieveAndGenerate` is convenient but less controllable than `Retrieve` + Converse
- 🗣 "A Knowledge Base is ingestion-as-a-service plus two APIs: Retrieve if you own the prompt, RetrieveAndGenerate if you don't."
- 🗣 "Sync is incremental, but nothing syncs until you start a job."
- 🗣 "Metadata filters are your authorization boundary inside a shared index; enforce them server-side."

## 3. File Index

Read in pipeline order: why, ingestion, retrieval, generation, stores, freshness.

- **Foundations**
  - [01 Managed RAG](02rag.04knowledge-bases.01managed-rag.md): the pain, the picture, use cases
- **Ingestion**
  - [02 Ingestion](02rag.04knowledge-bases.02ingestion.md): data sources, jobs, statistics, deletion policy
- **Query**
  - [03 Retrieve](02rag.04knowledge-bases.03retrieve.md): Retrieve vs RetrieveAndGenerate, search type, filters, reranking
  - [04 Generation](02rag.04knowledge-bases.04generation.md): prompt template, citations, sessions, guardrails
- **Stores and operations**
  - [05 Stores and Structured Query Language (SQL) KBs](02rag.04knowledge-bases.05stores-sql.md): supported stores, KB types, text-to-SQL
  - [06 Freshness](02rag.04knowledge-bases.06freshness.md): scheduled, event-driven, direct ingestion
- **Decisions and practice**
  - [98 Tradeoffs](02rag.04knowledge-bases.98tradeoffs.md): when to use, knobs, comparison, failure modes
  - [99 Interview](02rag.04knowledge-bases.99interview.md): Level 4 (L4) + Level 5 (L5) questions

## 4. Code Map

Python lives in the infra and service layers; the KB itself is Terraform.

**Python**

| Concept file | Python path | Function / class |
|---|---|---|
| 02 S3 data source + chunking + deletion policy | `app/infra/_02rag_04knowledge_bases.py` | `create_data_source`, `CHUNKING_CONFIGS` |
| 02 Start sync (idempotent clientToken) | `app/infra/_02rag_04knowledge_bases.py` | `start_ingestion_job`, `client_token` |
| 02 Poll job + statistics | `app/infra/_02rag_04knowledge_bases.py` | `wait_for_ingestion`, `get_ingestion_job` |
| 02 Job history (paginator, status filter) | `app/infra/_02rag_04knowledge_bases.py` | `list_ingestion_jobs` |
| 03 Retrieve (numberOfResults, HYBRID/SEMANTIC, filter, rerank) | `app/infra/_02rag_04knowledge_bases.py` | `retrieve` |
| 03 Filter builders | `app/domain/_02rag_04knowledge_bases.py` | `eq`, `in_`, `gte`, `and_all`, `or_all` |

| Concept file | Python path | Function / class |
|---|---|---|
| 03 Metadata sidecar | `app/infra/_02rag_04knowledge_bases.py` | `write_metadata_sidecar` |
| 04 RetrieveAndGenerate (prompt, guardrail, session, decomposition) | `app/infra/_02rag_04knowledge_bases.py` | `retrieve_and_generate`, `DEFAULT_PROMPT_TEMPLATE` |
| 04 Citation extraction | `app/infra/_02rag_04knowledge_bases.py` | `extract_citations` |
| 06 Keep fresh: S3 event → idempotent sync | `app/service/_02rag_04knowledge_bases.py` | `handle_s3_event`, `changed_keys` |
| Settings (`A_KB_`) | `app/config/_02rag_04knowledge_bases.py` | `KbSettings` |
| Representational State Transfer (REST) | `app/api/_02rag_04knowledge_bases.py` | `router` (`/kb/sync`, `/retrieve`, `/ask`, `/metadata`, `/data-sources`, `/s3-event`) |

**Terraform** (modules/02rag_04knowledge_bases)

| Concept file | Terraform resource |
|---|---|
| 05 KB (VECTOR, Titan V2 dims, Amazon OpenSearch Serverless (AOSS) field mapping) | `aws_bedrockagent_knowledge_base.main` |
| 01 KB service role permissions | `aws_iam_role_policy.kb` (role `aws_iam_role.kb` in 02rag_02opensearch) |
| 02 S3 data source + chunking + deletion policy | `aws_bedrockagent_data_source.s3` |
| 02 App permission to start sync | `aws_iam_role_policy.app_kb` |

- Gaps (doc only)
  - SQL (Redshift) KB, Kendra-type KB, GraphRAG with Neptune Analytics
  - `RetrieveAndGenerateStream`, `IngestKnowledgeBaseDocuments`, implicit filtering
  - EventBridge Scheduler / Lambda wiring for freshness (only the handler logic)
  - KB evaluation jobs ([04safety.03evaluations](../04safety/04safety.03evaluations.00index.md))

## References

- [aws-samples/amazon-bedrock-samples: rag/knowledge-bases](https://github.com/aws-samples/amazon-bedrock-samples/tree/main/rag)
- [Bedrock User Guide: Knowledge Bases](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)
- [Bedrock User Guide: Query configurations (filters, search type, reranking)](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-config.html)
- [Bedrock User Guide: Sync your data with your knowledge base](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-data-source-sync-ingest.html)
- [Bedrock User Guide: Build a knowledge base with a structured data store](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-build-structured.html)
