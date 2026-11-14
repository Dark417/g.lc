# 03db.04mongodb.00index MongoDB

> Document database: store what you read together in one Binary JavaScript Object Notation (BSON) document, scale reads with replica sets and writes with shards.

## Index

- [1. One-Minute Version](#1-one-minute-version)
- [2. Files](#2-files)
  - [2.1 Model And Storage](#21-model-and-storage)
  - [2.2 Reads And Writes](#22-reads-and-writes)
  - [2.3 Cluster](#23-cluster)
  - [2.4 Review](#24-review)
- [3. Code Map](#3-code-map)
- [4. Run Locally And Terraform](#4-run-locally-and-terraform)
- [References](#references)

## 1. One-Minute Version

MongoDB stores JavaScript Object Notation (JSON)-like documents and updates them atomically one document at a time.

- **What**: collections of BSON documents, flexible schema, rich queries, secondary indexes
- **Why**: the aggregate (order + items) is one document ⇒ one read, one atomic write, no joins
- **How**
  - WiredTiger storage: B+ trees, document-level concurrency, compression
  - Replica set: primary takes writes, the oplog feeds secondaries, automatic failover
  - Sharding: chunks by shard key behind `mongos`
- **Catch**
  - A bad schema (unbounded arrays) or a bad shard key is expensive to undo
  - Multi-document transactions work but cost more than in a relational database
- 🗣 "I embed what is read together, reference what grows without bound, and pick the shard key from the hottest query."

## 2. Files

Read top to bottom; each file explains first, then shows Java and Python.

### 2.1 Model And Storage

- [01 Document model and BSON](04mongodb.01document-model-bson.md)
- [02 WiredTiger storage](04mongodb.02wiredtiger-storage.md)
- [03 Schema design](04mongodb.03schema-design.md)

### 2.2 Reads And Writes

- [04 Create, Read, Update, Delete (CRUD) and update operators](04mongodb.04crud-update-operators.md)
- [05 Bulk writes and errors](04mongodb.05bulk-write.md)
- [06 Indexes](04mongodb.06indexes.md)
- [07 Query planner and explain](04mongodb.07query-planner-explain.md)
- [08 Pagination](04mongodb.08pagination.md)
- [09 Aggregation pipeline](04mongodb.09aggregation.md)

### 2.3 Cluster

- [10 Replica sets and oplog](04mongodb.10replica-sets-oplog.md)
- [11 Read and write concern](04mongodb.11read-write-concern.md)
- [12 Transactions](04mongodb.12transactions.md)
- [13 Sharding](04mongodb.13sharding.md)
- [14 Change streams](04mongodb.14change-streams.md)

### 2.4 Review

- [98 Tradeoffs](04mongodb.98tradeoffs.md)
- [99 Interview questions](04mongodb.99interview.md)

## 3. Code Map

Java lives in `com.lc.x.<layer>._03db_04mongodb`; Python in `app/<layer>/_03db_04mongodb.py`.

| File | Java (`infra/_03db_04mongodb/`) | Python (`app/infra/_03db_04mongodb.py`) |
| --- | --- | --- |
| 03 schema | `MongoShowcase.applyOrderValidator`, `renameCustomerEverywhere`, `appendOrderEvent` | same names, snake_case |
| 04 CRUD | `MongoShowcase.insertOrder` … `deleteCancelledBefore` | `insert_order` … `delete_cancelled_before` |
| 05 bulk | `MongoShowcase.upsertStock`, `MongoErrors.classify` | `upsert_stock`, `classify_error` |
| 06 indexes | `MongoShowcase.ensureIndexes`, `searchNotes` | `ensure_indexes`, `search_notes` |
| 07 explain | `MongoShowcase.explainCustomerOrders`, `MongoAdmin` | `explain_customer_orders`, `MongoAdmin` |

| File | Java (`infra/_03db_04mongodb/`) | Python (`app/infra/_03db_04mongodb.py`) |
| --- | --- | --- |
| 08 pagination | `MongoShowcase.listCustomerOrders`, `OrderCursor` | `list_customer_orders`, `encode_cursor` |
| 09 aggregation | `revenueByCustomer`, `statusFacets`, `runningTotals`, `materializeDailyRevenue` | same, snake_case |
| 10–11 replica, concern | `ConsistencyProfiles`, `MongoAdmin.replicaSetSummary`, `insertThenReadFromSecondary` | `*_collection`, `replica_set_summary` |
| 12 transactions | `MongoTransactions.placeOrder`, `placeOrderHandRolled`, `goOffCall`, `reserveStock` | `MongoTransactions` |
| 13–14 shard, streams | `MongoAdmin.shardOrdersCollection`, `MongoChangeStreams` | `shard_orders_collection`, `MongoChangeStreams` |

- Thin layers: `config/_03db_04mongodb/MongoConfig`, `domain/_03db_04mongodb/*` (records + `OrderStore` port), `service/…/MongoOrderService`, `api/…/MongoController`
- Switch: `x.mongodb.enabled=true` (Java) · `X_ENABLED=mongodb` (Python)

## 4. Run Locally And Terraform

- Local replica set: `1x/local/mongodb/` (`docker-compose.yml`, `init-replica.js`, `sample-queries.js`)
  - Default Uniform Resource Identifier (URI) `mongodb://localhost:27017/?replicaSet=rs0`
- Amazon Web Services (AWS): `terraform/modules/03db_04mongodb/` declares Amazon DocumentDB (Mongo-compatible)
  - Gaps vs MongoDB: no change-stream `fullDocumentBeforeChange`, limited `$lookup` and text search, different index internals

## References

- MongoDB Manual — Data Modeling, Indexes, Aggregation, Replication, Sharding, Transactions (mongodb.com/docs/manual)
- MongoDB Java Driver 5.x and PyMongo 4.x documentation
- Amazon DocumentDB — functional differences with MongoDB (docs.aws.amazon.com/documentdb)
