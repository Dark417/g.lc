# 03db.01aurora.00index Aurora PostgreSQL

> PostgreSQL on shared 6-way quorum storage: cheap replicas and fast failover, but a single writer and a client that must handle lag, Domain Name System (DNS) flips, and retries.

- Scope: Java + Python + Terraform
- Terraform: [`modules/03db_01aurora/main.tf`](../../terraform/modules/03db_01aurora/main.tf)
- Code: Java `config|api|domain|infra|service/_03db_01aurora`; Python `app/<layer>/_03db_01aurora.py`
- Schema: `resources/_03db_01aurora/schema.sql` (Java), `SCHEMA_SQL` in `app/infra/_03db_01aurora.py` (Python)
- Engine assumed: Aurora PostgreSQL 16, Serverless v2 instances, 1 writer + 1 reader (per Terraform)

## Index

- [1. One-Minute Version](#1-one-minute-version)
- [2. File Map](#2-file-map)
- [3. Code Map](#3-code-map)
  - [3.1 Wiring And Connections](#31-wiring-and-connections)
  - [3.2 Transactions And Retries](#32-transactions-and-retries)
  - [3.3 Writes And Locking](#33-writes-and-locking)
  - [3.4 Reads And Queue](#34-reads-and-queue)
- [4. Gaps](#4-gaps)
- [References](#references)

## 1. One-Minute Version

Aurora keeps the Postgres engine but replaces its storage and replication.

- What
  - PostgreSQL-compatible engine on a purpose-built distributed storage volume
  - Compute (writer + up to 15 readers) is separate from storage
- Why
  - Classic Postgres High Availability (HA) ships full pages and Write-Ahead Log (WAL) to a standby with its own disk
    - Every replica = another full copy, another I/O path, minutes to rebuild
  - Aurora ships only redo log records to a shared, 6-way replicated volume
- How
  - Each 10 gigabytes (GB) segment lives as 6 copies across 3 Availability Zones (AZs)
  - Write is durable at 4/6 acks; recovery read quorum is 3/6
  - Readers attach to the same volume, so a replica costs compute, not storage
  - Cluster endpoint → current writer
  - Reader endpoint → DNS round-robin over readers
- The catch
  - Readers lag the writer (Amazon Web Services (AWS): usually under 100 milliseconds (ms))
    - Result: no read-your-writes on the reader endpoint
  - Failover flips a DNS name
    - Result: clients with cached DNS or long-lived connections hit the old node
  - It is still single-writer Postgres: write throughput is bounded by one instance
- What the app must do
  - Two pools (writer, reader)
  - Bounded `maxLifetime`
  - Fresh Identity and Access Management (IAM) token per new physical connection
  - Transport Layer Security (TLS) `verify-full`
  - Retry SQLSTATE `40001` / `40P01` / `08xxx` at the transaction boundary, with idempotency keys
  - Pick isolation on purpose
    - READ COMMITTED default
    - REPEATABLE READ for snapshots
    - SERIALIZABLE for invariants
- 🗣 "Aurora moves replication from the database to the storage layer: the writer ships redo log records, and storage turns them into pages."
- 🗣 "A replica is just another compute node on the same volume, so adding one doesn't copy data, but it still lags by milliseconds."
- 🗣 "Retries belong outside the transaction, and only work when the write is idempotent."

## 2. File Map

Read top to bottom: the cluster, then the connection layer, then the engine, then app patterns, then decisions.

- Cluster (AWS layer)
  - [01architecture](01aurora.01architecture.md): why Aurora exists, log-is-the-database storage, quorum math
  - [02endpoints-replica-lag](01aurora.02endpoints-replica-lag.md): writer/reader endpoints, replica lag, read-after-write routing
  - [03failover-dns](01aurora.03failover-dns.md): failover flow, DNS Time To Live (TTL), evict on `25006`
  - [04serverless-v2](01aurora.04serverless-v2.md): Aurora Capacity Unit (ACU), in-place scaling, cold cache
- Connection layer
  - [05iam-auth-tls](01aurora.05iam-auth-tls.md): token per physical connection, `verify-full`
  - [06pools-rds-proxy](01aurora.06pools-rds-proxy.md): two pools, lifetime, sizing, Relational Database Service (RDS) Proxy
- PostgreSQL engine
  - [07mvcc-vacuum](01aurora.07mvcc-vacuum.md): row versions, xmin horizon, wraparound
  - [08isolation-levels](01aurora.08isolation-levels.md): Read Committed (RC) / Repeatable Read (RR) / SERIALIZABLE (Serializable Snapshot Isolation, SSI), write skew, reader snapshots
- Application patterns
  - Transactions
    - [09transactions-propagation](01aurora.09transactions-propagation.md): `@Transactional`, REQUIRED vs REQUIRES_NEW, psycopg blocks
    - [10retries-idempotency](01aurora.10retries-idempotency.md): retry boundary, SQLSTATEs, idempotent create
  - Writes
    - [11crud-batch-upsert](01aurora.11crud-batch-upsert.md): schema, RETURNING, batch insert, chunked import, upsert
    - [12locking](01aurora.12locking.md): FOR UPDATE, conditional UPDATE, version column
    - [13skip-locked-queue](01aurora.13skip-locked-queue.md): SKIP LOCKED claim, lease, reaper
  - Reads
    - [14pagination](01aurora.14pagination.md): OFFSET vs keyset, opaque cursor
    - [15jsonb-gin](01aurora.15jsonb-gin.md): Binary JavaScript Object Notation (JSONB) operators, Generalized Inverted Index (GIN) operator classes
- Decisions
  - [98tradeoffs](01aurora.98tradeoffs.md): when to use, knobs, best practices, comparison, failure modes
  - [99interview](01aurora.99interview.md): Q1–Q8 (L4 + L5 extra), Q9–Q11 (L5-only)

## 3. Code Map

Java paths are under `java/src/main/java/com/lc/x/`; Python paths under `python/`.

### 3.1 Wiring And Connections

| Concept file | Java | Python |
|---|---|---|
| Config keys | `config/_03db_01aurora/AuroraProperties` | `app/shared/config.py` `Settings.aurora_*` + `app/infra/_03db_01aurora.py` constants |
| [06pools-rds-proxy](01aurora.06pools-rds-proxy.md) | `config/_03db_01aurora/AuroraConfig.auroraWriterDataSource`, `auroraReaderDataSource`, `pool` | `app/infra/_03db_01aurora.py` `AuroraPools.writer`, `reader`, `_make_pool` |
| [05iam-auth-tls](01aurora.05iam-auth-tls.md) token | `infra/_03db_01aurora/IamAuthDataSource.getConnection` + `AuroraConfig.tokenSupplier` | `iam_token` + `AuroraPools._kwargs_supplier` (callable kwargs) |
| [05iam-auth-tls](01aurora.05iam-auth-tls.md) TLS | `config/_03db_01aurora/AuroraConfig.pgDataSource` | `AuroraPools._base_kwargs` |
| [03failover-dns](01aurora.03failover-dns.md) | `infra/_03db_01aurora/AuroraEvictionOverride.adjudicate` | `AuroraRepository._connection` |
| [04serverless-v2](01aurora.04serverless-v2.md) | Terraform only | Terraform only |

### 3.2 Transactions And Retries

| Concept file | Java | Python |
|---|---|---|
| [10retries-idempotency](01aurora.10retries-idempotency.md) classify | `infra/_03db_01aurora/AuroraErrors.isRetryable` | `app/infra/_03db_01aurora.py` `is_retryable` |
| [10retries-idempotency](01aurora.10retries-idempotency.md) retry | `service/_03db_01aurora/AuroraOrderService.withRetry`, `changeStatus` | `app/service/_03db_01aurora.py` `AuroraOrderService._with_retry`, `change_status` |
| [09transactions-propagation](01aurora.09transactions-propagation.md) managers | `config/_03db_01aurora/AuroraConfig.auroraWriterTxManager`, `auroraReaderTxManager` | `AuroraRepository.writer_tx`, `reader_tx`, `independent_tx` |
| [09transactions-propagation](01aurora.09transactions-propagation.md) REQUIRED vs REQUIRES_NEW | `service/_03db_01aurora/AuroraAuditService.recordJoined`, `recordIndependent`; used by `AuroraOrderTx.placeOrder` | `AuroraOrderService._place_once` (`independent_tx` for the attempt row) |
| [08isolation-levels](01aurora.08isolation-levels.md) SERIALIZABLE | `service/_03db_01aurora/AuroraOrderTx.placeOrderWithinCreditLimit` | `AuroraOrderService._place_within_limit_once` |
| [08isolation-levels](01aurora.08isolation-levels.md) RR on reader | `AuroraOrderTx.customerSummary` | `AuroraOrderService.customer_summary` |

### 3.3 Writes And Locking

| Concept file | Java (`infra/_03db_01aurora/AuroraJdbcRepository`) | Python (`app/infra/_03db_01aurora.py`) |
|---|---|---|
| [11crud-batch-upsert](01aurora.11crud-batch-upsert.md) schema + Create, Read, Update, Delete (CRUD) | `applySchema`, `insert`, `findById`, `delete` | `AuroraRepository.apply_schema`, `PgOrderStore.insert`, `find_by_id`, `delete` |
| [11crud-batch-upsert](01aurora.11crud-batch-upsert.md) batch + upsert | `batchInsert`, `upsertStock`; `AuroraOrderService.importOrders` | `PgOrderStore.batch_insert`, `upsert_stock`; `AuroraOrderService.import_orders` |
| [10retries-idempotency](01aurora.10retries-idempotency.md) idempotent create | `insertIdempotent`, `findByIdempotencyKey` | `PgOrderStore.insert_idempotent`, `find_by_idempotency_key` |
| [12locking](01aurora.12locking.md) optimistic | `updateStatusIfVersion` | `PgOrderStore.update_status_if_version` |
| [12locking](01aurora.12locking.md) pessimistic + atomic | `lockStockForUpdate`, `decrementStock`, `decrementStockIfAvailable` | `PgOrderStore.lock_stock_for_update`, `decrement_stock`, `decrement_stock_if_available` |
| [09transactions-propagation](01aurora.09transactions-propagation.md) order + stock | `service/_03db_01aurora/AuroraOrderTx.placeOrder` | `app/service/_03db_01aurora.py` `AuroraOrderService._place_once` |

### 3.4 Reads And Queue

| Concept file | Java | Python |
|---|---|---|
| [14pagination](01aurora.14pagination.md) | `AuroraJdbcRepository.pageByOffset`, `pageByKeyset`, `Cursor` | `PgOrderStore.page_by_offset`, `page_by_keyset`, `_encode_cursor`, `decode_cursor` |
| [15jsonb-gin](01aurora.15jsonb-gin.md) | `AuroraJdbcRepository.insert` (attrs), `findByAttrs` | `PgOrderStore.insert`, `find_by_attrs` |
| [02endpoints-replica-lag](01aurora.02endpoints-replica-lag.md) routing | `AuroraJdbcRepository.findByIdOnReader`; `AuroraOrderService.getOrder` | `AuroraOrderService.get_order` (reader store) |
| [02endpoints-replica-lag](01aurora.02endpoints-replica-lag.md) lag probe | `AuroraJdbcRepository.replicaLagMillis` | `AuroraRepository.replica_lag_ms` |
| [13skip-locked-queue](01aurora.13skip-locked-queue.md) | `AuroraJdbcRepository.enqueue`, `claim`, `complete`, `fail`, `requeueExpired` | `PgOrderStore.enqueue`, `claim`, `complete`, `fail`, `requeue_expired` |
| Representational State Transfer (REST) endpoints | `api/_03db_01aurora/AuroraController` | `app/api/_03db_01aurora.py` `router` |

- [07mvcc-vacuum](01aurora.07mvcc-vacuum.md): no dedicated code; `delete` shows the dead-tuple catch

## 4. Gaps

Described in the docs, not coded here.

- AWS Advanced Java Database Connectivity (JDBC) / Python Wrapper failover plugin
  - Described in [03failover-dns](01aurora.03failover-dns.md); not a dependency here
- RDS Proxy
  - Described in [06pools-rds-proxy](01aurora.06pools-rds-proxy.md); Terraform does not declare one
- Outbox relay and LISTEN/NOTIFY: out of scope for this slice
- Schema migrations: `applySchema` is a demo; real projects use Flyway/Liquibase

## References

- [awslabs/aws-advanced-jdbc-wrapper](https://github.com/awslabs/aws-advanced-jdbc-wrapper): topology-aware failover and IAM plugins for JDBC
- [Amazon Aurora User Guide: Aurora storage, replication, and endpoints](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.Overview.html)
- [Amazon Aurora User Guide: IAM database authentication](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/UsingWithRDS.IAMDBAuth.html)
- [PostgreSQL 16 docs: Transaction Isolation](https://www.postgresql.org/docs/16/transaction-iso.html)
- [Verbitski et al., "Amazon Aurora: Design Considerations for High Throughput Cloud-Native Relational Databases", Special Interest Group on Management of Data (SIGMOD) 2017](https://www.amazon.science/publications/amazon-aurora-design-considerations-for-high-throughput-cloud-native-relational-databases)
