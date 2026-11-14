# 03db.04mongodb.98tradeoffs Tradeoffs

> When MongoDB fits, which knobs matter, and how it fails.

## Index

- [1. When To Use](#1-when-to-use)
- [2. Comparison](#2-comparison)
- [3. Knobs](#3-knobs)
- [4. Failure Modes](#4-failure-modes)
- [Related](#related)

## 1. When To Use

Pick MongoDB when the data is naturally an aggregate and the queries vary.

- ✅ Use
  - Aggregates read as a whole: orders, catalogs, user profiles, Content Management System (CMS) content
  - Evolving schema with many optional fields
  - Rich secondary queries and aggregation without a separate warehouse
- Avoid
  - Many-to-many relations queried from every side ⇒ relational joins win
  - Strong cross-entity invariants on every write ⇒ Postgres transactions are cheaper
  - Pure key-value at huge scale with fixed access patterns ⇒ DynamoDB is simpler to run

## 2. Comparison

Three stores, three cost models.

| Need | MongoDB | DynamoDB | Aurora Postgres (Binary JavaScript Object Notation, JSONB) |
| --- | --- | --- | --- |
| Data model | documents, nested | items by Partition Key (PK)/Sort Key (SK) | rows + JSONB column |
| Ad hoc queries | rich, secondary indexes | only on keys + Global Secondary Indexes (GSIs) | full Structured Query Language (SQL) |
| Multi-item transactions | yes, costlier | yes, 100 items | yes, cheapest |
| Scale-out writes | sharding (you pick the key) | automatic partitions | single writer |
| Ops burden | Atlas: low · self-run: high | none | low |

Pick: MongoDB for flexible aggregates with rich queries, unless access patterns are fixed (DynamoDB) or relations dominate (Postgres).

| Hosting | MongoDB Atlas | Amazon DocumentDB |
| --- | --- | --- |
| Engine | real MongoDB | Mongo Application Programming Interface (API) on Aurora-style storage |
| Feature parity | full | gaps (some operators, change-stream options) |
| Amazon Web Services (AWS) integration | PrivateLink | native Virtual Private Cloud (VPC), Identity and Access Management (IAM), Key Management Service (KMS) |

## 3. Knobs

Name the knob, its default, and what it trades.

- `w` (write concern): default `majority` since 5.0 ⇒ durable across failover; `w:1` is faster but can roll back
- `readConcern`: `local` default; `majority` for no rollback reads; `snapshot` inside transactions
- `readPreference`: `primary` default; `secondaryPreferred` offloads reads but returns stale data
- `retryWrites` / `retryReads`: on by default ⇒ one automatic retry on network or failover errors
- `maxPoolSize`: 100 per client by default; one `MongoClient` per process
- WiredTiger cache: 50% of (Random-Access Memory (RAM) − 1 gigabyte (GB)); the working set should fit

## 4. Failure Modes

What breaks, how you notice, and the fix.

| Failure | Trigger | Detect | Fix |
| --- | --- | --- | --- |
| Unbounded array | events pushed forever | document size, slow updates | cap array, outlier pattern |
| COLLSCAN | missing or wrong index | `explain`, profiler | Equality, Sort, Range (ESR) compound index |
| Hot shard | monotonic shard key | per-shard ops imbalance | hashed or compound key |
| Lost write | `w:1` + failover | rollback files | `w:majority` |

| Failure | Trigger | Detect | Fix |
| --- | --- | --- | --- |
| Stale read | secondary read after write | user sees old data | primary or causal session |
| Stream gap | consumer down longer than oplog window | `ChangeStreamHistoryLost` | bigger oplog, resync path |
| Txn abort storm | hot document in transactions | `TransientTransactionError` rate | redesign to single-doc update |

## Related

- [Index](04mongodb.00index.md)
- [99 Interview questions](04mongodb.99interview.md)
- [DynamoDB tradeoffs](02dynamodb.98tradeoffs.md)
- [Aurora tradeoffs](01aurora.98tradeoffs.md)
