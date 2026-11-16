# knowledge-bases.99interview Interview Questions

> Level 4 (L4) baseline and Level 5 (L5) extensions for Bedrock Knowledge Bases.

## Index

- [1. Core Questions](#1-core-questions)
  - [Q1 What A Sync Does](#q1-what-a-sync-does)
  - [Q2 Retrieve Or RetrieveAndGenerate](#q2-retrieve-or-retrieveandgenerate)
  - [Q3 Metadata Filters](#q3-metadata-filters)
  - [Q4 When To Rerank](#q4-when-to-rerank)
  - [Q5 Keeping A Knowledge Base (KB) Fresh](#q5-keeping-a-knowledge-base-kb-fresh)
  - [Q6 Guardrail And Custom Prompt](#q6-guardrail-and-custom-prompt)
  - [Q7 Structured Query Language (SQL) Knowledge Base](#q7-structured-query-language-sql-knowledge-base)
- [2. L5-Only Questions](#2-l5-only-questions)
  - [Q8 Multi-Tenant RAG](#q8-multi-tenant-rag)
  - [Q9 Wrong Answers After An Update](#q9-wrong-answers-after-an-update)
  - [Q10 KB vs LangChain](#q10-kb-vs-langchain)

## 1. Core Questions

Each question has an L4 answer and an L5 extension.

### Q1 What A Sync Does

**Q:** Walk through what happens when you sync a Knowledge Base.

**L4 answer**

- `StartIngestionJob` scans the data source
- New/changed files are parsed, chunked, embedded, and upserted
- Deleted files' vectors are removed

**L5 extra**

- Change detection makes it incremental
  - ⇒ cost scales with changes, not corpus size
- One job per data source at a time
  - ⇒ design triggers for `ConflictException`
- `COMPLETE` ≠ all succeeded
  - Check `numberOfDocumentsFailed` and `failureReasons`

### Q2 Retrieve Or RetrieveAndGenerate

**Q:** Retrieve or RetrieveAndGenerate?

**L4 answer**

- Retrieve returns chunks; you build the prompt and call the model
- RetrieveAndGenerate does all of it and returns citations and a session

**L5 extra**

- Retrieve for agents, custom prompts, streaming with Converse, multi-source fusion, and evaluation
- RetrieveAndGenerate for fast delivery with built-in citations and session handling
- Both accept the same retrieval knobs (filters, hybrid, reranking)

### Q3 Metadata Filters

**Q:** How do metadata filters work, and what are they good for?

**L4 answer**

- Sidecar `<file>.metadata.json` attributes are indexed with each chunk
- Retrieve passes a `filter` (equals, in, andAll, …)

**L5 extra**

- Filters run inside the store query ⇒ no post-filter shortfall
- Use for tenant isolation and recency
  - Enforce server-side, never from client input
- Sidecar changes need a sync; size limits apply (check quotas)

### Q4 When To Rerank

**Q:** When do you add reranking?

**L4 answer**

- When top results are relevant-ish but not the best
- Retrieve more candidates, rerank, keep the top few

**L5 extra**

- Cross-encoder scores query and chunk jointly
  - ⇒ better precision than embedding similarity
- Costs a reranker call and latency per query
- Pair with hybrid search
  - Hybrid widens recall, reranker sharpens precision

### Q5 Keeping A Knowledge Base (KB) Fresh

**Q:** How do you keep a KB up to date?

**L4 answer**

- Trigger `StartIngestionJob` on a schedule or on Simple Storage Service (S3) events

**L5 extra**

- Event path: S3 → Lambda → StartIngestionJob with clientToken from (key, sequencer)
- Conflicts while a job runs ⇒ defer and retry
  - Plus a scheduled sweep for completeness
- `IngestKnowledgeBaseDocuments` for seconds-level updates of specific documents

### Q6 Guardrail And Custom Prompt

**Q:** How do you attach a guardrail and a custom prompt to RetrieveAndGenerate?

**L4 answer**

- `generationConfiguration.guardrailConfiguration` with id + version
- `promptTemplate.textPromptTemplate` with `$search_results$`

**L5 extra**

- Keep `$output_format_instructions$` or citations break
- Use a published guardrail version, not DRAFT, in production
- Check `guardrailAction` and log interventions for tuning

### Q7 Structured Query Language (SQL) Knowledge Base

**Q:** When is a SQL Knowledge Base the right choice?

**L4 answer**

- Questions over tables (counts, sums, filters)
- The KB generates SQL against Redshift and returns rows

**L5 extra**

- Accuracy depends on table/column descriptions and curated example queries
- Run under a read-only, least-privilege Database (DB) user; set an execution timeout
- Vector Retrieval-Augmented Generation (RAG) cannot aggregate reliably ⇒ route by question type

## 2. L5-Only Questions

Depth, scale, and design ownership.

### Q8 Multi-Tenant RAG

**Q:** Design a multi-tenant RAG service on Bedrock KB.

**L5 answer**

- Option A: shared KB + index
  - `tenant` attribute in sidecars
  - Server-side `equals(tenant)` filter on every call
- Option B: KB (or data source + index) per large tenant
  - ⇒ isolation, separate deletion, separate cost
- Ingestion: tenant prefix per data source; sync per tenant
- Audit: log every retrieval with tenant and citations
  - Test for leakage in Continuous Integration (CI)

### Q9 Wrong Answers After An Update

**Q:** Answers became wrong after a document update. Debug it.

**L5 answer**

- Was the job run?
  - Check `list_ingestion_jobs` for a job after the upload
- Did it process the file?
  - Statistics: modified indexed vs skipped vs failed
- Do old and new chunks both exist?
  - Possible if the file was renamed (new id) without deleting the old
- Do citations point to the old version?
  - Then sync or delete/re-add
  - Consider direct ingestion for hot docs

### Q10 KB vs LangChain

**Q:** Bedrock KB vs Do It Yourself (DIY): the team wants LangChain. Decide.

**L5 answer**

- List required capabilities
  - Sources, parsing, chunking, filters, hybrid, rerank, citations, freshness Service Level Agreement (SLA)
- If the KB covers them ⇒ KB
  - Less code, fewer ingestion bugs, Identity and Access Management (IAM), managed sync
- If not (custom fusion, Access Control List (ACL) joins, unsupported sources) ⇒ DIY with OpenSearch
  - Own ingestion Service Level Objectives (SLOs)
- Hybrid path: KB for ingestion + Retrieve, LangChain/agents for orchestration on top
