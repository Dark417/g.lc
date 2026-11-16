# knowledge-bases.05stores-sql Stores, Knowledge Base (KB) Types, and Structured Query Language (SQL) KBs

> Which vector stores a Knowledge Base (KB) can use, the three KB types, and text-to-SQL over structured data.

## Index

- [1. Supported Vector Stores](#1-supported-vector-stores)
- [2. Field Mapping And Embedding Config](#2-field-mapping-and-embedding-config)
- [3. KB Types](#3-kb-types)
- [4. Structured Data: Text-To-SQL KBs](#4-structured-data-text-to-sql-kbs)

## 1. Supported Vector Stores

`storage_configuration.type` selects the store.

- **OpenSearch**
  - OpenSearch Serverless (quick-create default)
  - OpenSearch managed cluster
- **Amazon Web Services (AWS) databases**
  - Aurora PostgreSQL (pgvector, `RDS`)
  - Neptune Analytics (GraphRAG)
  - Simple Storage Service (S3) Vectors
- **Third party** (secrets in Secrets Manager)
  - Pinecone
  - Redis Enterprise Cloud
  - MongoDB Atlas
- Store comparison: [embeddings.98tradeoffs](embeddings.98tradeoffs.md)

## 2. Field Mapping And Embedding Config

The KB must know which index fields hold vector, text, and metadata.

- **Field mapping**: vector field, text field, metadata field
  - Plus primary key for Relational Database Service (RDS)
- **Embedding config**: model Amazon Resource Name (ARN) + `dimensions` + `embedding_data_type` (`FLOAT32` / `BINARY`)
- The field mapping is the shared contract with the OpenSearch index ([opensearch.05kb-index-bulk](opensearch.05kb-index-bulk.md))

```python
# app/config/_02rag_02opensearch.py
# Shared with modules/02rag_04knowledge_bases field_mapping: change one, change both.
index_name: str = "a-kb-index"
vector_field: str = "embedding"
text_field: str = "text"
metadata_field: str = "metadata"
dimensions: int = 1024  # must equal the KB embedding model dimensions (Titan V2 1024)
```

## 3. KB Types

Three KB types cover vectors, enterprise search, and structured data.

- **`VECTOR`**: the Retrieval-Augmented Generation (RAG) pipeline in this component
- **`KENDRA`**: a Kendra Generative Artificial Intelligence (GenAI) index
- **`SQL`**: structured data (section 4)

## 4. Structured Data: Text-To-SQL KBs

Lecture 38; doc only here (no repo code).

**Mechanism**

→ KB type `SQL`, query engine = Amazon Redshift (provisioned or Serverless)  
→ storage = Redshift databases or AWS Glue Data Catalog tables  
→ the KB generates Structured Query Language (SQL) from the question, runs it, returns rows (`sqlLocation` in results)

- **Accuracy levers**
  - Table and column descriptions
  - Inclusion/exclusion of tables and columns
  - Curated queries: example question → SQL pairs
  - Query execution timeout
- **Use when** answers are aggregations or lookups over tables
- **Limit**: generated SQL can be wrong yet plausible
  - ⇒ least-privilege read-only Database (DB) user
  - ⇒ curated examples
  - ⇒ review logs
