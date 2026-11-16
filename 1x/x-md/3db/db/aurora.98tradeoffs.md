# 03db.01aurora.98tradeoffs Trade-offs, Knobs, Failure Modes

> When Aurora PostgreSQL fits, the knobs that matter, how it compares with its siblings, and how it fails.

## Index

- [1. When To Use / Not](#1-when-to-use--not)
- [2. Knobs](#2-knobs)
  - [2.1 Pool Knobs](#21-pool-knobs)
  - [2.2 Driver Knobs](#22-driver-knobs)
- [3. Best Practices](#3-best-practices)
- [4. Tricks](#4-tricks)
- [5. Comparison](#5-comparison)
- [6. Failure Modes](#6-failure-modes)
  - [6.1 Failover And Connections](#61-failover-and-connections)
  - [6.2 Retries And Transactions](#62-retries-and-transactions)
  - [6.3 Concurrency And Locking](#63-concurrency-and-locking)
  - [6.4 Performance And Storage](#64-performance-and-storage)
- [Related](#related)

## 1. When To Use / Not

Aurora is single-writer Postgres with cheap replicas and fast failover; decide on write throughput first.

- Use Aurora PostgreSQL when
  - Relational model: joins, constraints, transactions across rows and tables
  - Read-heavy with replicas, and you want replicas without data copies
  - Fast in-Region failover with no committed-data loss matters
  - Storage grows unpredictably (auto-grows; no volume sizing)
- Avoid when
  - Write throughput beyond one large instance
    - Shard (Limitless), DynamoDB, or a distributed Structured Query Language (SQL) engine
  - Key-value access at very high scale with single-digit-millisecond (ms) tail latency
    - DynamoDB
  - Small, steady, cost-sensitive workload
    - Relational Database Service (RDS) PostgreSQL is cheaper and simpler
  - Heavy analytics scans
    - Redshift or Athena; keep Online Transaction Processing (OLTP) and Online Analytical Processing (OLAP) apart
  - You need Postgres extensions or settings Aurora does not support
    - Self-managed or RDS

## 2. Knobs

Each knob lists the Java (Hikari / pgjdbc) and Python (psycopg_pool) name and its deciding variable.

### 2.1 Pool Knobs

| Knob | Java | Python | Deciding variable |
|---|---|---|---|
| Pool max | `maximumPoolSize` (`x.aurora.pool.max-size`) | `max_size` | database (DB) `max_connections` ÷ pods; not request concurrency |
| Wait for connection | `connectionTimeout` 3 s | `timeout` | Fail fast under overload vs ride out blips |
| Max lifetime | `maxLifetime` 14 min | `max_lifetime` 840 s | Domain Name System (DNS) rebalance cadence; under token life by convention |
| Idle retire | `idleTimeout` 5 min | `max_idle` | Cost of idle backends vs cold reconnect |
| Validate on checkout | Java Database Connectivity 4 (JDBC4) `isValid()` when idle > 500 ms (built in) | `check=ConnectionPool.check_connection` | One round trip vs serving a dead connection |

- Code: [06pools-rds-proxy](01aurora.06pools-rds-proxy.md)

### 2.2 Driver Knobs

| Knob | Java | Python | Deciding variable |
|---|---|---|---|
| Batch inserts | `reWriteBatchedInserts=true` | `executemany` (pipeline mode) | Rows per round trip |
| Statement timeout | `options=-c statement_timeout=…` | `options` in kwargs | Longest legitimate query |
| Transport Layer Security (TLS) | `sslmode=verify-full` + `sslrootcert` | same libpq keys | Never lower in prod |
| Read-only pool | `setReadOnly(true)` on reader | `SET default_transaction_read_only` | Catch accidental writes to readers |

- Code: [05iam-auth-tls](01aurora.05iam-auth-tls.md), [11crud-batch-upsert](01aurora.11crud-batch-upsert.md)

## 3. Best Practices

Each rule names the failure it prevents.

- Separate writer and reader pools
  - Prevents writes landing on replicas and reads missing own writes by accident
- Fresh Identity and Access Management (IAM) token per physical connection
  - Prevents login failures 15 min after startup
- Retry outside the transaction with idempotency keys
  - Prevents duplicate writes on ambiguous commit
- Keep transactions short, no network calls inside
  - Prevents lock pile-ups and vacuum blocking
- Name the transaction manager
  - Prevents a silent no-op `@Transactional` when several exist
- Keyset pagination
  - Prevents deep-page latency growth
- `CREATE INDEX CONCURRENTLY` on live tables
  - Prevents a write-blocking lock during index builds
- Migrations via Flyway/Liquibase, not app startup
  - Prevents N pods racing Data Definition Language (DDL)

## 4. Tricks

- `INSERT … ON CONFLICT DO NOTHING RETURNING` + fallback SELECT
  - Idempotent create in one round trip ([10retries-idempotency](01aurora.10retries-idempotency.md))
- `UPDATE … WHERE n >= k`
  - Replaces SELECT FOR UPDATE for simple counters ([12locking](01aurora.12locking.md))
- `SERIALIZABLE READ ONLY DEFERRABLE`
  - Runs a consistent report with no abort risk (writer only)
- Version number as a read-your-writes token
  - Read the reader, fall back to the writer if `version < token` ([02endpoints-replica-lag](01aurora.02endpoints-replica-lag.md))

## 5. Comparison

| Option | What it is | Strength | Weakness | Choose when |
|---|---|---|---|---|
| Aurora PostgreSQL | Postgres engine on shared 6-way quorum storage | Replicas without copies, fast failover, storage auto-grows | Single writer, higher per-I/O or per-Aurora Capacity Unit (ACU) cost, Amazon Web Services (AWS)-only | Read-heavy OLTP that needs High Availability (HA) and replicas |
| RDS PostgreSQL | Community Postgres on Elastic Block Store (EBS), managed by AWS | Cheaper, closest to upstream, more extensions/versions | Replica = full copy, slower failover (standby promotion) | Small or steady workload, cost first |
| Self-managed PostgreSQL (Elastic Compute Cloud (EC2) / Kubernetes (k8s)) | You run Postgres, Patroni, backups | Full control of versions, extensions, tuning | You own HA, backups, patching, on-call | Unusual extensions or settings, or non-AWS portability |
| DynamoDB | Managed key-value / document store, partitioned | Horizontal write scale, predictable latency at any size | No joins, access patterns fixed up front, limited transactions | Known key-based access at very high scale |
| Aurora DSQL | Serverless distributed SQL, PostgreSQL-compatible (General Availability (GA) 2025) | Active-active multi-Region, no instances to size | Optimistic concurrency (commit-time `40001`), Postgres feature subset (check docs) | Multi-Region writes and you can accept Optimistic Concurrency Control (OCC) retries |
| Aurora Limitless Database | Aurora PostgreSQL (PG) sharded across many writers via routers (GA 2024) | Write scale-out while staying in Aurora PG | Shard key design, cross-shard queries cost more | One cluster's writer is the bottleneck |

Pick: Aurora PostgreSQL, unless the workload is small and steady (RDS PostgreSQL) or access is pure key-value at very high write scale (DynamoDB).

- Deciding variable: write throughput vs one instance's ceiling, then cost per steady I/O
- DynamoDB side of the comparison: [02dynamodb.98tradeoffs](02dynamodb.98tradeoffs.md)

## 6. Failure Modes

Grouped so each table stays small; every row links to the file with the fix in code.

### 6.1 Failover And Connections

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Writes fail after failover | Cached DNS points the writer pool at the demoted node | `25006 read_only_sql_transaction` | Evict on `25006`, low DNS Time To Live (TTL), bounded `maxLifetime`, retry |
| Broken connections | Failover or reboot | `08006`, `57P01` | Pool eviction + transaction retry with idempotency key |
| Login fails after 15 min | Token generated once at startup | `PAM authentication failed` | Generate token per new physical connection |
| Reconnect storm | Every pod reconnects at once after failover | IAM auth throttling, Central Processing Unit (CPU) spike | Jittered lifetimes, small min idle, RDS Proxy |
| Missing own write | Read through reader endpoint right after commit | Not-found right after create | Writer for read-your-writes, version token fallback |

- Files: [03failover-dns](01aurora.03failover-dns.md), [05iam-auth-tls](01aurora.05iam-auth-tls.md), [02endpoints-replica-lag](01aurora.02endpoints-replica-lag.md)

### 6.2 Retries And Transactions

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Duplicate order | Retry after a lost COMMIT ack | Two rows for one request | Unique idempotency key + `ON CONFLICT DO NOTHING` |
| Retry never succeeds | Retry inside the failed transaction | `25P02 current transaction is aborted` | Retry the whole transaction from outside |
| Pool starvation | `REQUIRES_NEW` or nested pool use with pool ≤ concurrency | Connection timeout, threads blocked | Bigger pool, fewer nested connections |

- Files: [10retries-idempotency](01aurora.10retries-idempotency.md), [09transactions-propagation](01aurora.09transactions-propagation.md)

### 6.3 Concurrency And Locking

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Write skew | Invariant across rows under Read Committed (RC)/Repeatable Read (RR) | Business rule broken, no error | SERIALIZABLE + retry, or lock a parent row |
| Lost update | Read-modify-write under RC | Overwritten changes | Version column, or atomic `UPDATE … SET n = n - k` |
| Deadlock | Two transactions lock rows in opposite order | `40P01` | Lock in key order; retry |
| Lock pile-up | Long transaction holds `FOR UPDATE` | `pg_locks` waits, `55P03` | Short transactions, `lock_timeout` |
| Stuck job | Worker crashed after claiming | `RUNNING` with past `locked_until` | Lease + reaper; idempotent handler |

- Files: [08isolation-levels](01aurora.08isolation-levels.md), [12locking](01aurora.12locking.md), [13skip-locked-queue](01aurora.13skip-locked-queue.md)

### 6.4 Performance And Storage

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Deep pages slow | OFFSET pagination | Latency grows with page number | Keyset pagination |
| Table bloat | Long or idle transactions block vacuum | Dead tuples rise, `n_dead_tup` | `idle_in_transaction_session_timeout`, autovacuum tuning |

- Files: [14pagination](01aurora.14pagination.md), [07mvcc-vacuum](01aurora.07mvcc-vacuum.md)

## Related

- [00index](01aurora.00index.md)
- [99interview](01aurora.99interview.md)
