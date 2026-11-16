# opensearch.02managed-domains Managed Domains

> Node-based OpenSearch clusters: building blocks, storage tiers, stability rules, and index management.

## Index

- [1. Building Blocks](#1-building-blocks)
- [2. Storage Tiers And Changes](#2-storage-tiers-and-changes)
- [3. Shard Sizing](#3-shard-sizing)
- [4. Java Virtual Machine (JVM) And k-NN Memory](#4-java-virtual-machine-jvm-and-k-nn-memory)
- [5. Index State Management](#5-index-state-management)
- [6. Performance Knobs](#6-performance-knobs)

## 1. Building Blocks

A domain is data nodes holding shards, coordinated by dedicated masters.

- **Data nodes**: hold shards
  - Memory-optimized types suit k-Nearest Neighbors (k-NN) (graphs need Random-Access Memory (RAM))
- **Dedicated master (cluster manager) nodes**: cluster state only, no data
  - Use 3: quorum survives one loss
  - 2 cannot elect after a failure
  - 1 is a single point of failure
- **Shards**: primary + replicas
  - Primary count is fixed at index creation (reindex or split to change)
- **Multi-AZ with standby**: 3 Availability Zones (AZs), one held as standby for failover
  - Amazon Web Services (AWS) recommended for production

```python
# app/infra/_02rag_02opensearch.py
"settings": {
    "index": {
        "knn": True,
        "knn.algo_param.ef_search": ef_search,
        # AOSS: no number_of_shards / number_of_replicas.
        # Managed domain: set them (shard sizing below).
    }
},
```

## 2. Storage Tiers And Changes

Tiers trade cost per gigabyte (GB) against access speed.

- **Hot**: Elastic Block Store (EBS) / instance storage, read-write
- **UltraWarm**: Simple Storage Service (S3)-backed with a cache, read-only, cheaper per GB
  - Needs dedicated masters
- **Cold**: detached from compute, attach before querying
  - ⇒ lowest cost, minutes to access
- **Vector Retrieval-Augmented Generation (RAG) data is hot**: k-NN needs graphs in memory
- **Changes**: most config changes run a blue/green deployment
  - ⇒ hours on big domains, double nodes meanwhile

## 3. Shard Sizing

AWS sizing guidance sets the target shard size by workload.

- 10–30 gibibytes (GiB) per shard when search latency matters
- 30–50 GiB for write-heavy (logs)
- Too many small shards ⇒ cluster-state and heap overhead per shard
- Too few large shards ⇒ slow recovery, hot nodes
- Keep shards per node within the heap guidance
  - AWS: up to 25 per GiB of heap; check current docs

## 4. Java Virtual Machine (JVM) And k-NN Memory

The JVM heap and the native k-NN memory fail differently.

- **JVM memory pressure**
  - Heap ≈ half of RAM, capped near 32 GiB (compressed pointers)
  - AWS recommended alarms (recommended-alarms page)
    - `JVMMemoryPressure` max ≥ 95%
    - `OldGenJVMMemoryPressure` ≥ 80%

→ high pressure  
⇒ Garbage Collection (GC) pauses  
⇒ timeouts  
⇒ node drops

- **k-NN memory is native (off-heap)**
  - Circuit breaker caps graph memory (`knn.memory.circuit_breaker.limit`)
    - ⇒ when tripped, new graphs are rejected
  - Watch `KNNGraphMemoryUsage` and circuit-breaker metrics

## 5. Index State Management

Index State Management (ISM) automates index lifecycle by policy.

- **Policy** = states + transitions + actions
  - Transitions: age, size, doc count
  - Actions: rollover, replica count, force_merge, warm, delete
- **Typical logs policy**: hot → warm after 7 d → delete after 90 d
- **For vectors**: force_merge after bulk load
  - ⇒ fewer segments ⇒ fewer graphs to search

```python
# illustrative: ISM policy body for a logs index (not in the repo)
ism_policy = {
    "policy": {
        "states": [
            {"name": "hot", "actions": [], "transitions": [{"state_name": "warm", "conditions": {"min_index_age": "7d"}}]},
            {"name": "warm", "actions": [{"warm_migration": {}}], "transitions": [{"state_name": "delete", "conditions": {"min_index_age": "90d"}}]},
            {"name": "delete", "actions": [{"delete": {}}], "transitions": []},
        ]
    }
}
```

## 6. Performance Knobs

Lecture 57 bulk-load tuning.

- Bulk requests of ~5–15 megabytes (MB) (order of magnitude); parallel clients
- `refresh_interval: -1` during bulk load, restore after
- Replicas 0 during initial load, add after (managed domain only)
- Warm up graphs (`GET /_plugins/_knn/warmup/<index>`) before traffic

```python
# app/config/_02rag_02opensearch.py
bulk_chunk: int = 500  # docs per _bulk request; keep requests ~5–15 MB (order of magnitude)
bulk_max_attempts: int = 4  # retries for 429 / 5xx items only
```

- **Catch**: warmup, force_merge, and ISM are doc only in this repo
