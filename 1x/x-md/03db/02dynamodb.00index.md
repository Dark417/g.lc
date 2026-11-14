# 03db.02dynamodb.00index DynamoDB

> Managed key-value store: design keys for the queries, guard writes with conditions, and know where a single key tops out.

- Scope: Java + Python + Terraform
- Terraform: [`modules/03db_02dynamodb/main.tf`](../../terraform/modules/03db_02dynamodb/main.tf)
  - `x-orders`: Partition Key (PK)/Sort Key (SK) + `GSI1`, Time To Live (TTL), streams, Point-In-Time Recovery (PITR)
  - `x-idempotency`
- Code: Java `infra|domain|service|api/_03db_02dynamodb`, `config/_03db_02dynamodb`; Python `app/<layer>/_03db_02dynamodb.py`
- Numbers: DynamoDB Developer Guide, read 2026-11, unless marked "order of magnitude"

## Index

- [1. One-Minute Version](#1-one-minute-version)
- [2. File Map](#2-file-map)
- [3. Code Map](#3-code-map)
  - [3.1 Wiring And Keys](#31-wiring-and-keys)
  - [3.2 Reads, Writes, Conditions](#32-reads-writes-conditions)
  - [3.3 Query, Pagination, Scan, Batch](#33-query-pagination-scan-batch)
  - [3.4 Transactions, TTL, Streams, Sharding](#34-transactions-ttl-streams-sharding)
- [4. Gaps](#4-gaps)
- [References](#references)

## 1. One-Minute Version

DynamoDB is a distributed hash map of sorted lists.

- What
  - A managed key-value and document store
  - Every item is addressed by a partition key, plus an optional sort key
- Why
  - Single-digit-millisecond reads and writes that stay flat as the table grows
  - No servers, no connection pools, no vacuum, no failover to run
- How
  - `hash(PK)` picks a partition
  - Items with the same PK sit together, sorted by SK (an "item collection")
  - Each partition is replicated three ways across Availability Zones (AZs)
  - You model the table from the access patterns, not from entities
- Catch
  - One partition caps at 3,000 Read Capacity Units (RCU) / 1,000 Write Capacity Units (WCU)
    - Result: a hot key throttles even when the table has spare capacity
  - Queries only work on keys you designed
    - Result: a new access pattern means a new Global Secondary Index (GSI) or a backfill
  - GSIs are async ⇒ always eventually consistent
  - Item size caps at 400 kilobytes (KB)
- Concurrency primitive = the condition expression
  - Create-only, optimistic lock, and idempotency are all "write only if …"
- Transactions exist (up to 100 items) but cost 2x and conflict under contention
- 🗣 "DynamoDB is a distributed hash map of sorted lists: design the keys for the queries, and the scale is free."
- 🗣 "Every correctness guarantee in DynamoDB is a condition expression."
- 🗣 "A short page is not the last page; only a missing LastEvaluatedKey is."

## 2. File Map

Read top to bottom: storage model, then data modeling, then operations, then decisions.

- Storage model
  - [01architecture](02dynamodb.01architecture.md): why it exists, partitions + replicas picture, write/read path
  - [02partitions-hot-keys](02dynamodb.02partitions-hot-keys.md): capacity units, splits, adaptive capacity, write sharding
  - [03reads-consistency](02dynamodb.03reads-consistency.md): strong vs eventual, `ReturnValues`
- Data modeling
  - [04indexes-gsi-lsi](02dynamodb.04indexes-gsi-lsi.md): GSI vs Local Secondary Index (LSI), sparse index, back-pressure
  - [05single-table-design](02dynamodb.05single-table-design.md): access-pattern-first keys, fixed-width SK
- Operations
  - Writes
    - [06conditions-updates](02dynamodb.06conditions-updates.md): create-only, SET/ADD/REMOVE, optimistic lock
    - [08batch-ops](02dynamodb.08batch-ops.md): batch write/get, unprocessed retry
    - [09transactions-idempotency](02dynamodb.09transactions-idempotency.md): `TransactWriteItems`, idempotent place order
  - Reads
    - [07query-pagination-scan](02dynamodb.07query-pagination-scan.md): Query, cursor pagination, Scan
  - Lifecycle and capacity
    - [10streams-ttl](02dynamodb.10streams-ttl.md): Streams, TTL, PITR
    - [11capacity-modes](02dynamodb.11capacity-modes.md): on-demand vs provisioned, retries
- Decisions
  - [98tradeoffs](02dynamodb.98tradeoffs.md): when to use, knobs, comparison, failure modes
  - [99interview](02dynamodb.99interview.md): Q1–Q8 L4 + L5, Q9–Q11 L5-only

## 3. Code Map

Java paths are under `1x/java/src/main/java/com/lc/x/`; Python paths are under `1x/python/`.

### 3.1 Wiring And Keys

| Concept file | Java | Python |
|---|---|---|
| [01architecture](02dynamodb.01architecture.md) client config | `config/_03db_02dynamodb/DynamoDbConfig.dynamoDbClient`, `.dynamoDbEnhancedClient` | `app/infra/_03db_02dynamodb.py` `DynamoDbShowcase.client`, `.table` (lazy `app.shared.aws`) |
| [05single-table-design](02dynamodb.05single-table-design.md) keys | `domain/_03db_02dynamodb/OrderKeys` | `app/domain/_03db_02dynamodb.py` `pk_customer`, `sk_order`, `iso` |
| Item mapping | `infra/_03db_02dynamodb/OrderItemMapper` (low-level), `OrderItem` (`@DynamoDbBean`) | `app/infra/_03db_02dynamodb.py` `to_item` / `from_item`, `to_av` / `from_av` |
| Representational State Transfer (REST) Application Programming Interface (API) | `api/_03db_02dynamodb/DynamoDbController` (`/dynamodb`) | `app/api/_03db_02dynamodb.py` `router` (`/dynamodb`) |

### 3.2 Reads, Writes, Conditions

Java class `DynamoDbShowcase` / `EnhancedClientShowcase` live in `infra/_03db_02dynamodb/`; Python methods are on `DynamoDbShowcase` in `app/infra/_03db_02dynamodb.py`.

| Concept file | Java | Python |
|---|---|---|
| [06conditions-updates](02dynamodb.06conditions-updates.md#13-create-only-put-in-code) create-only put | `DynamoDbShowcase.putOrderCreateOnly`; `EnhancedClientShowcase.putCreateOnly` | `put_order_create_only`, `put_order_create_only_resource` |
| [03reads-consistency](02dynamodb.03reads-consistency.md) strong vs eventual | `DynamoDbShowcase.getOrder(.., consistent)`; `EnhancedClientShowcase.getOrder` | `get_order`, `get_order_resource` |
| [06conditions-updates](02dynamodb.06conditions-updates.md#2-update-expressions) SET/ADD/REMOVE | `DynamoDbShowcase.recordOrderOnProfile` | `record_order_on_profile`, `record_order_on_profile_resource` |
| [06conditions-updates](02dynamodb.06conditions-updates.md#3-optimistic-lock) optimistic lock | `DynamoDbShowcase.changeStatusWithVersion`; `EnhancedClientShowcase.updateWithVersionAttribute` | `change_status_with_version`, `change_status_with_version_resource` |

### 3.3 Query, Pagination, Scan, Batch

| Concept file | Java | Python |
|---|---|---|
| [07query-pagination-scan](02dynamodb.07query-pagination-scan.md#1-query-on-keys) Query prefix / between | `DynamoDbShowcase.queryOrdersByPrefix`, `.queryOrdersBetween`; `EnhancedClientShowcase.queryOrders` | `query_orders_by_prefix`, `query_orders_between`, `query_orders_resource` |
| [04indexes-gsi-lsi](02dynamodb.04indexes-gsi-lsi.md#4-gsi-query-in-code) GSI query | `DynamoDbShowcase.queryByStatus`; `EnhancedClientShowcase.queryByStatus` | `query_by_status`, `query_by_status_resource` |
| [07query-pagination-scan](02dynamodb.07query-pagination-scan.md#2-pagination) cursor | `DynamoDbShowcase.queryOrdersPage` + `CursorCodec`; `.queryAllOrders` | `query_orders_page` + `encode_cursor` / `decode_cursor`; `query_all_orders` |
| [07query-pagination-scan](02dynamodb.07query-pagination-scan.md#3-scan-and-parallel-scan) Scan | `DynamoDbShowcase.scanAllOrders`, `.parallelScan` | `scan_all_orders`, `parallel_scan` |
| [08batch-ops](02dynamodb.08batch-ops.md) batch + unprocessed | `DynamoDbShowcase.batchPutOrders`, `.batchGetOrders`; `EnhancedClientShowcase.batchPut`, `.batchGet` | `batch_put_orders`, `batch_put_orders_resource` (`batch_writer`), `batch_get_orders` |

### 3.4 Transactions, TTL, Streams, Sharding

| Concept file | Java | Python |
|---|---|---|
| [09transactions-idempotency](02dynamodb.09transactions-idempotency.md#2-the-place-order-transaction-in-code) transaction | `infra/_03db_02dynamodb/DynamoDbShowcase.placeOrderTransaction`, `.parseCancellation`; `EnhancedClientShowcase.placeOrderTransaction` | `app/infra/_03db_02dynamodb.py` `place_order_transaction`, `parse_cancellation` |
| [09transactions-idempotency](02dynamodb.09transactions-idempotency.md#3-idempotent-place-order-use-case) use case | `service/_03db_02dynamodb/OrderService.placeOrder` | `app/service/_03db_02dynamodb.py` `PlaceOrderService.place_order` |
| [10streams-ttl](02dynamodb.10streams-ttl.md#2-ttl) TTL | `DynamoDbShowcase.expireOrderAfter`, `.queryLiveOrders` | `expire_order_after`, `query_live_orders` |
| [10streams-ttl](02dynamodb.10streams-ttl.md#1-streams) Streams | `infra/_03db_02dynamodb/StreamRecordHandler.handle`, `.sampleModifyRecord` | `app/infra/_03db_02dynamodb.py` `handle_stream_record`, `sample_modify_record` |
| [02partitions-hot-keys](02dynamodb.02partitions-hot-keys.md#4-write-sharding-and-scatter-gather) sharding | `DynamoDbShowcase.putOrderShardedStatus`, `.scatterGatherByStatus` | `put_order_sharded_status`, `scatter_gather_by_status` |

## 4. Gaps

Described in the docs, not coded.

- Global tables (multi-Region, last-writer-wins)
- DynamoDB Accelerator (DAX) cache
- Export to Simple Storage Service (S3) / import from S3
- `TransactGetItems`, PartiQL
- Real stream consumption (Lambda / Kinesis Client Library (KCL)); only the record shape is parsed

## References

- [aws-samples/aws-dynamodb-examples](https://github.com/aws-samples/aws-dynamodb-examples) — Software Development Kit (SDK) examples and data-modeling schemas
- [DynamoDB Developer Guide: Service, account, and table quotas](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/ServiceQuotas.html)
- [DynamoDB Developer Guide: Best practices for designing partition keys](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-partition-key-design.html)
- [DynamoDB Developer Guide: Transactions](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/transaction-apis.html)
- [Elhemali et al., "Amazon DynamoDB: A Scalable, Predictably Performant, and Fully Managed NoSQL Database Service", USENIX Annual Technical Conference (ATC) 2022](https://www.usenix.org/conference/atc22/presentation/elhemali)
