# opensearch OpenSearch as a Vector Store

> Entry point for OpenSearch domains, Serverless collections, the k-Nearest Neighbors (k-NN) plugin, and the index a Bedrock Knowledge Base (KB) expects.

## Index

- [1. Source And Scope](#1-source-and-scope)
- [2. One-Minute Version](#2-one-minute-version)
- [3. File Index](#3-file-index)
- [4. Code Map](#4-code-map)
- [References](#references)

## 1. Source And Scope

This component is the vector store behind the Bedrock Knowledge Base.

- Lectures: AIP-C01 #17, #53–#59 (slides p.120–144)
- Scope: Python + Terraform
- Terraform: [modules/02rag_02opensearch](../../terraform/modules/02rag_02opensearch/main.tf)
  - Collection `a-vectors` (VECTORSEARCH)
  - Customer Managed Key (CMK) encryption policy, Virtual Private Cloud (VPC) + Bedrock network policy, data-access policy
  - `aws_iam_role.kb`: Knowledge Base service role, used by [knowledge-bases](knowledge-bases.00index.md)
- Code: `app/infra/_02rag_02opensearch.py`
  - Signature Version 4 (SigV4) client, KB index, bulk, k-NN, filtered k-NN, hybrid
- Shared contract with knowledge-bases
  - Index `a-kb-index`
  - Vector field `embedding` (1024 dims)
  - Text field `text`
  - Metadata field `metadata`
- Numbers: Amazon OpenSearch Service Developer Guide and OpenSearch k-NN docs, read 2026-11, unless marked "order of magnitude"

## 2. One-Minute Version

OpenSearch is a distributed search engine (Lucene inverted index) plus a k-NN plugin for vectors.

- **What**
  - Two Amazon Web Services (AWS) forms
    - **Managed domain**: you pick nodes, shards, versions
    - **Serverless collection**: AWS scales compute in OpenSearch Compute Units (OCUs); you pick a collection type
- **Why**
  - One engine does Best Matching 25 (BM25), vectors, filters, and aggregations
    - ⇒ hybrid search without glue code
  - Default vector store for Bedrock Knowledge Bases (quick-create uses Serverless)
- **How**
  - Vectors live in `knn_vector` fields
    - Indexed with Hierarchical Navigable Small World (HNSW) (faiss / lucene) or Inverted File Index (IVF) (faiss)
  - Query = `knn` clause
    - Optional filter inside it
    - Optional `hybrid` with a normalization pipeline
  - Access on AWS = SigV4 (`aoss` or `es`) + Identity and Access Management (IAM) + (Serverless) a data-access policy
- **Catch**
  - Serverless bills OCU-hours even when idle (lecture 17)
    - ⇒ delete dev collections; check the pricing page for the floor
  - Domains need shard sizing, Java Virtual Machine (JVM) watching, and 3 dedicated masters to stay stable
  - k-NN graphs live in native memory outside the JVM heap
    - ⇒ memory, not disk, sizes the cluster
  - The vector index must exist (right fields, dims) before the Bedrock KB is created
- 🗣 "Serverless trades knobs for no-ops, but not for zero cost: OCUs bill while idle."
- 🗣 "On Amazon OpenSearch Serverless (AOSS), IAM gets you to the door; the data-access policy opens the index."
- 🗣 "Put the filter inside the knn clause, or you post-filter and lose results."

## 3. File Index

Read from the engine outward: architecture, deployment forms, then index and queries.

- **Engine**
  - [01 Why OpenSearch](opensearch.01why-opensearch.md): pain, mechanism, write and read paths
- **Deployment forms**
  - [02 Managed domains](opensearch.02managed-domains.md): nodes, shards, tiers, stability, Index State Management (ISM)
  - [03 Serverless collections](opensearch.03serverless.md): OCUs, types, the three policies, SigV4
- **Vectors**
  - [04 k-NN plugin](opensearch.04knn-plugin.md): engines, methods, knobs, on_disk
  - [05 KB index and bulk](opensearch.05kb-index-bulk.md): the mapping a KB expects, bulk writes
  - [06 Filtering and hybrid](opensearch.06filtering-hybrid.md): efficient filtering, hybrid pipeline
- **Decisions and practice**
  - [98 Tradeoffs](opensearch.98tradeoffs.md): when to use, knobs, comparison, failure modes
  - [99 Interview](opensearch.99interview.md): Level 4 (L4) + Level 5 (L5) questions

## 4. Code Map

Python lives in `app/infra/_02rag_02opensearch.py` unless noted; Terraform in `modules/02rag_02opensearch/`.

**Python**

| Concept file | Python path | Function / class |
|---|---|---|
| 03 SigV4 client (aoss / es) | `app/infra/_02rag_02opensearch.py` | `opensearch_client` |
| 04 Disk-based vector field | `app/infra/_02rag_02opensearch.py` | `on_disk_vector_field` |
| 05 KB index mapping (faiss hnsw, text, metadata) | `app/infra/_02rag_02opensearch.py` | `kb_index_body`, `create_kb_index` |
| 05 Bulk with per-item errors + retry | `app/infra/_02rag_02opensearch.py` | `bulk_index`, `to_document` |
| 05 Delete | `app/infra/_02rag_02opensearch.py` | `bulk_delete`, `delete_index` |
| 05 Index contract | `app/domain/_02rag_02opensearch.py`, `app/config/_02rag_02opensearch.py` | `KbIndexContract`, `OpenSearchSettings` |

| Concept file | Python path | Function / class |
|---|---|---|
| 06 k-NN (+ per-query ef_search) | `app/infra/_02rag_02opensearch.py` | `knn_query` |
| 06 Efficient filtered k-NN | `app/infra/_02rag_02opensearch.py` | `filtered_knn_query`, `metadata_filter_clause` |
| 06 Hybrid pipeline + query | `app/infra/_02rag_02opensearch.py` | `create_hybrid_pipeline`, `hybrid_query` |
| 06 VectorStore port + adapter | `app/domain/_02rag_02opensearch.py`, infra | `VectorStore`, `OpenSearchVectorStore` |
| Representational State Transfer (REST) | `app/api/_02rag_02opensearch.py` | `router` (`/opensearch/index`, `/documents`, `/knn`, `/pipeline`, `/hybrid`) |

**Terraform** (no Python counterpart)

| Concept file | Terraform resource |
|---|---|
| 03 SigV4 app permissions | `aws_iam_role_policy.app_opensearch` |
| 03 Encryption / network / data-access policies | `aws_opensearchserverless_security_policy.encryption`, `.network`, `aws_opensearchserverless_access_policy.data` |
| 03 Collection VECTORSEARCH, standby replicas | `aws_opensearchserverless_collection.vectors` |
| 03 VPC endpoint | `aws_opensearchserverless_vpc_endpoint.main` |
| 05 KB service role | `aws_iam_role.kb` (+ policy in 02rag_04knowledge_bases) |
| 05 KB index mapping | none: the provider can't create indexes ⇒ Python |

- Gaps (doc only)
  - Managed domain Terraform (`aws_opensearch_domain`), UltraWarm, cold storage, ISM policies
  - IVF training Application Programming Interface (API), warmup API, force_merge
  - Reciprocal Rank Fusion (RRF) score-ranker pipeline (comment only)
  - Serverless lifecycle policies (TIMESERIES retention)

## References

- [aws-samples/amazon-bedrock-samples: knowledge bases with OpenSearch Serverless](https://github.com/aws-samples/amazon-bedrock-samples/tree/main/rag)
- [OpenSearch Service Developer Guide: Amazon OpenSearch Serverless](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless.html)
- [OpenSearch Service Developer Guide: Sizing domains (shard size guidance)](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/sizing-domains.html)
- [OpenSearch docs: k-NN vector search, methods and engines](https://opensearch.org/docs/latest/field-types/supported-field-types/knn-methods-engines/)
- [OpenSearch docs: hybrid search and the normalization processor](https://opensearch.org/docs/latest/vector-search/ai-search/hybrid-search/)
