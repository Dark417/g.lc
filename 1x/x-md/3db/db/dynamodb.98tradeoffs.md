# 03db.02dynamodb.98tradeoffs DynamoDB Trade-Offs

> When to use DynamoDB, the knobs and best practices, how it compares to siblings, and how it fails.

## Index

- [1. When To Use Or Not](#1-when-to-use-or-not)
- [2. Knobs And Best Practices](#2-knobs-and-best-practices)
  - [2.1 Keys And Reads](#21-keys-and-reads)
  - [2.2 Pagination And Writes](#22-pagination-and-writes)
  - [2.3 Batch, Retries, Scan, Global Secondary Indexes (GSIs)](#23-batch-retries-scan-global-secondary-indexes-gsis)
  - [2.4 Tricks](#24-tricks)
- [3. Comparison](#3-comparison)
- [4. Failure Modes](#4-failure-modes)
- [Related](#related)

## 1. When To Use Or Not

DynamoDB fits when access patterns are known and key-addressable.

- Use when
  - Access patterns are known and key-addressable
  - You need flat latency from 10 to 10 million requests/s without re-architecting
  - Spiky or unpredictable load with no ops team (on-demand)
  - Idempotency, leases, counters, and session state for other services
- Avoid when
  - Queries are ad-hoc or analytical (aggregates, joins, `GROUP BY`)
    - Result: Aurora PostgreSQL, or export to Simple Storage Service (S3) + Athena
  - Access patterns are still changing every sprint
    - Result: each change risks a backfill
  - Items naturally exceed 400 kilobytes (KB)
    - Result: store the blob in S3, keep a pointer
  - Multi-item invariants are the core of the domain (ledgers with many rows per operation)
    - Result: possible with transactions, but relational is simpler
  - Full-text or geo search
    - Result: OpenSearch fed by Streams

## 2. Knobs And Best Practices

Each rule names the failure it prevents.

### 2.1 Keys And Reads

- Key design ([05single-table-design](02dynamodb.05single-table-design.md))
  - High-cardinality Partition Key (PK) spread evenly
    - Prevents: hot partitions
  - Prefix keys with the entity type (`CUSTOMER#`, `ORDER#`)
    - Prevents: collisions between entity types in one table
  - Fixed-width timestamps and zero-padded numbers in Sort Key (SK)
    - Prevents: wrong sort order
- Reads ([03reads-consistency](02dynamodb.03reads-consistency.md))
  - Default eventual reads; strong only where read-after-write matters
    - Prevents: paying 2x for nothing
  - `ProjectionExpression` to fetch only needed attributes
    - Limit: Read Capacity Unit (RCU) is charged on the full item size, not the projected size

### 2.2 Pagination And Writes

- Pagination ([07query-pagination-scan](02dynamodb.07query-pagination-scan.md#2-pagination))
  - Loop until `LastEvaluatedKey` is absent
    - Prevents: silent data loss when a page is short
  - `Limit` caps items evaluated before the filter
    - Result: a page can be empty yet have a next key
  - Each page is at most 1 megabyte (MB)
  - Expose `LastEvaluatedKey` as an opaque base64 cursor
    - Validate it on the way back in (PK matches the caller)
    - Sign or encrypt it if keys are sensitive
- Writes ([06conditions-updates](02dynamodb.06conditions-updates.md))
  - Every non-idempotent write carries a condition
    - Prevents: lost updates and duplicate creates
  - Use `ReturnValues` instead of read-after-write

### 2.3 Batch, Retries, Scan, Global Secondary Indexes (GSIs)

- Batch ([08batch-ops](02dynamodb.08batch-ops.md))
  - `BatchWriteItem`: up to 25 puts/deletes, 16 MB
  - `BatchGetItem`: up to 100 keys, 16 MB (Developer Guide, "Service quotas")
  - Not atomic, no conditions
  - Partial success returns `UnprocessedItems` / `UnprocessedKeys`
  - Duplicate keys inside one batch → `ValidationException`

→ Resend only the unprocessed items  
→ Sleep with exponential backoff + full jitter  
→ Give up after N attempts and surface the leftovers

- Retries ([11capacity-modes](02dynamodb.11capacity-modes.md#4-retries))
  - Software Development Kit (SDK) retries throttling and 5xx with backoff (adaptive mode in Python, standard in Java)
  - App-level retries only for idempotent or conditional writes
- Scan ([07query-pagination-scan](02dynamodb.07query-pagination-scan.md#3-scan-and-parallel-scan))
  - Reads the whole table, filter applied after read ⇒ full RCU cost
  - Parallel scan (`Segment` / `TotalSegments`) only for offline jobs
  - Prefer a GSI, or "Export to S3" for analytics
- GSIs ([04indexes-gsi-lsi](02dynamodb.04indexes-gsi-lsi.md))
  - Project only what the pattern needs (`INCLUDE`)
    - Prevents: write amplification on every base write
  - Shard low-cardinality GSI keys (status, date)
    - Prevents: GSI back-pressure throttling base writes

### 2.4 Tricks

- Sparse GSI as a work queue (only items with `GSI1PK` are indexed)
- Composite SK for hierarchy (`COUNTRY#STATE#CITY`) + `begins_with`
- Version attribute + `ALL_OLD` on failure = conflict resolution without a read
- Store counters on a parent item and update them inside the same transaction as the child

## 3. Comparison

| Option | What it is | Strength | Weakness | Choose when |
|---|---|---|---|---|
| DynamoDB | Managed key-value / document store, partitioned by hash(PK) | Flat latency at any scale; zero ops; conditions, transactions, streams, Time To Live (TTL) | Queries only on designed keys; 400 KB items; GSIs eventual; hot keys capped per partition | Known key-based patterns, spiky load, serverless on Amazon Web Services (AWS) |
| Aurora PostgreSQL | Managed relational database (DB), single writer + replicas, shared storage | Structured Query Language (SQL), joins, ad-hoc queries, multi-row Atomicity, Consistency, Isolation, Durability (ACID), constraints | One writer caps write scale; connections and failover to manage | Evolving queries, relational invariants, reporting |
| Cassandra / Amazon Keyspaces | Wide-column, leaderless (Cassandra) or managed Cassandra Query Language (CQL; Keyspaces) | High write throughput; tunable consistency; multi-data center (DC; Cassandra) | Lightweight Transactions (LWT; Paxos) is slow; tombstones; self-managed ops for Cassandra | Write-heavy time series, CQL portability, multi-cloud |
| MongoDB / DocumentDB | Document DB with secondary indexes and rich queries | Flexible queries on any field; aggregation pipeline | Sharding and index design still needed at scale; DocumentDB is Application Programming Interface (API)-compatible, not MongoDB | Document shape varies, queries on many fields, moderate scale |

- Deciding variable: how well you know the access patterns
  - Known, key-addressable, high or spiky scale → DynamoDB
  - Unknown or relational → Aurora PostgreSQL ([01aurora.00index](01aurora.00index.md))

Pick: DynamoDB for key-addressable access patterns on AWS, unless queries are ad-hoc, relational, or still changing → Aurora PostgreSQL.

## 4. Failure Modes

Split in two tables to stay scannable; each row links to the concept that fixes it.

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Hot partition | Low-cardinality PK or GSI PK (status, date) | `ThrottledRequests` while table capacity is unused; Contributor Insights top keys | Write sharding; cache reads; redesign key |
| GSI back-pressure | GSI capacity or key skew below base table | Base writes throttled; GSI throttle metrics | Shard GSI key; provision GSI ≥ base; on-demand |
| Lost update | Read-modify-write with no condition | Values silently overwritten | `version` condition; `ALL_OLD` on failure |
| Duplicate create on retry | Client retries after a timeout | Two orders for one request | Idempotency record + order in one transaction |
| Partial batch dropped | `UnprocessedItems` ignored | Missing items, no error | Loop with backoff; alert on leftovers |
| Pagination stops early | Short or empty page treated as the end | Missing results | Loop until `LastEvaluatedKey` is absent |

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Stale read | Eventual read or GSI read right after a write | Read misses the new value | `ConsistentRead` on base table; `ReturnValues` |
| Expired items returned | Relying on TTL deletion time | Expired items in results | Filter `expiresAt > :now`; treat expired as absent in conditions |
| Transaction conflicts | Concurrent writes to the same items | `TransactionConflict` reasons | Backoff retry; shrink transactions; avoid hot items |
| Item too large | Unbounded lists inside one item | `ValidationException` (400 KB) | Split into an item collection; S3 pointer |
| Scan in request path | Missing access pattern | RCU spikes, slow API | Add GSI; export to S3 for analytics |
| Wrong sort order | Variable-width timestamps or numbers in SK | Out-of-order pages | Fixed-width International Organization for Standardization (ISO), zero-padded numbers |

## Related

- [00index](02dynamodb.00index.md)
- [99interview](02dynamodb.99interview.md)
