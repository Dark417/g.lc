# opensearch.98tradeoffs Tradeoffs

> When to choose Serverless, a domain, or another store, which knobs matter, and how it fails.

## Index

- [1. When To Use Or Not](#1-when-to-use-or-not)
- [2. Knobs](#2-knobs)
- [3. Best Practices](#3-best-practices)
- [4. Comparison](#4-comparison)
- [5. Failure Modes](#5-failure-modes)

## 1. When To Use Or Not

The deployment form follows traffic shape and the need for knobs.

- **Use OpenSearch Serverless when**
  - Bedrock Knowledge Base (KB) with hybrid search and no cluster team
  - Traffic is steady enough that the OpenSearch Compute Unit (OCU) floor is small relative to value
- **Use a managed domain when**
  - You need Inverted File Index (IVF), on_disk, custom shard layout, Index State Management (ISM), or plugins
  - Very large corpora where per-node memory planning beats OCU pricing
  - You already run OpenSearch for logs/search
- **Don't use when**
  - Low, spiky traffic on a small corpus
    - ⇒ the idle floor dominates ⇒ Simple Storage Service (S3) Vectors or pgvector
  - Vectors must join with transactional rows ⇒ pgvector
  - You only need a cache of recent answers ⇒ MemoryDB / ElastiCache

## 2. Knobs

Collection-level knobs are mostly immutable; index knobs trade recall for cost.

**Collection (Serverless)**

| Knob | Values | Trades | Change when |
|---|---|---|---|
| Collection type | SEARCH / TIMESERIES / VECTORSEARCH | workload fit; immutable | never after create ⇒ VECTORSEARCH for KB |
| `standby_replicas` | ENABLED / DISABLED | Availability Zone (AZ) resilience vs ~half the OCU floor | DISABLED only for dev |
| Encryption key | AWS-owned / Customer Managed Key (CMK) | control + audit vs simplicity | regulated data ⇒ CMK |
| Network | public / Virtual Private Cloud (VPC) / Amazon Web Services (AWS) service | reachability vs exposure | private data ⇒ VPC + service access |

**Index**

| Knob | Values | Trades | Change when |
|---|---|---|---|
| Engine | faiss / lucene | scale + KB support vs index size | KB on Amazon OpenSearch Serverless (AOSS) ⇒ faiss |
| `m`, `ef_construction` | 16 / 100 default (KB samples: ef_construction 512) | recall vs memory + build time | recall plateau |
| `ef_search` | 100 default | recall vs latency | tune on a golden set |

**Domain**

| Knob | Values | Trades | Change when |
|---|---|---|---|
| Shards | 10–30 gibibytes (GiB) each for search | parallelism vs overhead | index growth |
| Dedicated masters | 3 | stability vs cost | always for production |
| `refresh_interval` | 1 s default | freshness vs indexing throughput | bulk loads ⇒ -1 temporarily |

## 3. Best Practices

Each rule prevents a specific failure.

- Exclude the vector from `_source` in responses
  - ⇒ a 1024-dim hit carries ~4 kilobytes (KB) of floats nobody reads
- Inspect every `_bulk` item; retry only 429 / 5xx
  - ⇒ `_bulk` returns Hypertext Transfer Protocol (HTTP) 200 with per-item failures
- Pin the index contract (name, fields, dims) in one config shared with the KB
  - ⇒ a renamed field breaks ingestion silently per document
- Delete idle Serverless collections; keep the billing alarm ([base_billing_alarm](../../terraform/modules/base_billing_alarm/main.tf))
  - ⇒ OCUs bill while idle
- Domain: 3 dedicated masters + Multi-AZ, alarms on Java Virtual Machine (JVM) pressure and k-Nearest Neighbors (k-NN) circuit breaker
  - ⇒ prevents split brain and Garbage Collection (GC)-induced node drops

## 4. Comparison

The deciding variable is idle cost vs operational control.

| Option | What it is | Strength | Weakness | Choose when |
|---|---|---|---|---|
| OpenSearch Serverless | OCU-billed collections, AWS-managed shards | No cluster ops; KB quick-create; hybrid; Identity and Access Management (IAM) + policies | Idle OCU floor; fewer knobs; delayed visibility | KB default; steady traffic; small team |
| OpenSearch managed domain | Node-based cluster with k-NN plugin | Every knob: IVF, on_disk, ISM, UltraWarm, plugins | Shard sizing, JVM, upgrades, blue/green | Large or tuned workloads; existing ops |
| Aurora PostgreSQL + pgvector | Postgres + Hierarchical Navigable Small World (HNSW) / IVFFlat | Joins business rows; Atomicity, Consistency, Isolation, Durability (ACID); Structured Query Language (SQL) filters; Serverless v2 auto-pause to 0 Aurora Capacity Unit (ACU) | Index Random-Access Memory (RAM) bound; weaker lexical relevance than Best Matching 25 (BM25) | Data already in Postgres; modest corpus |
| S3 Vectors | Vector buckets + indexes in S3 | Lowest storage cost; no compute; KB-supported | Higher latency; no BM25 hybrid; check quotas | Large, cold, cost-first corpora |

- **Default**: OpenSearch Serverless behind the KB, unless
  - traffic is low and spiky ⇒ S3 Vectors (no idle floor)
  - the data lives in Postgres ⇒ pgvector
  - you need IVF / on_disk / ISM or run at very large scale ⇒ managed domain
- **Deciding variable**: idle cost vs operational control
  - Serverless = pay a floor to skip ops
  - Domain = pay in engineer time to tune

Pick: Serverless, unless traffic is low and spiky or you need domain-only knobs.

## 5. Failure Modes

Access and contract failures are loud; ranking and bulk failures are quiet.

**Setup and access**

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Surprise bill | Dev collection left running (lecture 17) | Billing alarm; Cost Explorer by service | Destroy; standby DISABLED for dev; max OCU cap |
| 403 on every call | IAM allows `aoss:APIAccessAll` but data-access policy misses role (or vice versa) | 403 "no permissions" from AOSS | Add role to data-access policy; check both gates |
| KB creation fails | Index missing, wrong field names, or dims ≠ embedding dims | KB create error / per-doc ingestion failures | Create index first with the shared contract |

**Query and write**

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Fewer than k hits | Post-filtering with a selective filter | Result count < k | Filter inside `knn` |
| Partial bulk failure ignored | `_bulk` HTTP 200 treated as success | Doc counts lower than expected | Parse items; retry 429/5xx; dead-letter 4xx |
| Hybrid scores nonsense | Hybrid query without the pipeline | Erratic ranking, BM25 dominates | Pass `search_pipeline`; normalize scores |

**Cluster (domain)**

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Cluster red / node drops | Too many shards, JVM pressure, 2 masters | ClusterStatus.red, JVMMemoryPressure ≥ 95% | 3 dedicated masters; shard sizing; bigger heap |
| k-NN circuit breaker | Graphs exceed native memory | Breaker metric; indexing rejected | Quantize / on_disk; more RAM; fewer replicas of cold indexes |
