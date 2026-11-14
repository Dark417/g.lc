# 03db.02dynamodb.99interview DynamoDB Interview Questions

> Eight core questions with L4 and L5 answers, plus three L5-only design questions.

## Index

- [1. Core Questions](#1-core-questions)
  - [Q1 Where An Item Lives And What Limits A Key](#q1-where-an-item-lives-and-what-limits-a-key)
  - [Q2 Strong Vs Eventual Reads](#q2-strong-vs-eventual-reads)
  - [Q3 Preventing A Lost Update](#q3-preventing-a-lost-update)
  - [Q4 Paginating A Query For API Clients](#q4-paginating-a-query-for-api-clients)
  - [Q5 Keys For Orders By Time And Pending Orders](#q5-keys-for-orders-by-time-and-pending-orders)
  - [Q6 BatchWriteItem Vs TransactWriteItems](#q6-batchwriteitem-vs-transactwriteitems)
  - [Q7 Idempotent Place Order](#q7-idempotent-place-order)
  - [Q8 Streams And TTL Together](#q8-streams-and-ttl-together)
- [2. L5-Only Questions](#2-l5-only-questions)
  - [Q9 Sale-Day Throttling On On-Demand](#q9-sale-day-throttling-on-on-demand)
  - [Q10 New Access Pattern On A Live Single-Table Design](#q10-new-access-pattern-on-a-live-single-table-design)
  - [Q11 When Would You Refuse Single-Table Design](#q11-when-would-you-refuse-single-table-design)
- [Related](#related)

## 1. Core Questions

Each question links to the concept file that holds the mechanism and code.

### Q1 Where An Item Lives And What Limits A Key

**Q:** How does DynamoDB decide where an item lives, and what limits a single key? ([02partitions-hot-keys](02dynamodb.02partitions-hot-keys.md))

**L4 answer**

- `hash(PK)` maps the item to a partition
- Items with the same Partition Key (PK) are stored together, sorted by Sort Key (SK)
- Each partition serves up to 3,000 Read Capacity Units (RCU) / 1,000 Write Capacity Units (WCU)
  - Result: a single hot key throttles, even with spare table capacity

**L5 extra**

- Partitions are three-way replicated
  - A leader handles writes and strong reads (Multi-Paxos)
- Adaptive capacity lends unused throughput to hot partitions
- Split for heat spreads hot SK ranges
- Neither can split one item ⇒ shard the key (suffix) or cache it
- Pick shard count N from peak WCU / 1,000, and accept N-way fan-out on read

### Q2 Strong Vs Eventual Reads

**Q:** Strong vs eventual reads: cost, where they are available, when to use each? ([03reads-consistency](02dynamodb.03reads-consistency.md))

**L4 answer**

- Eventual: half the cost, may miss the latest write
- Strong: 2x cost, latest acknowledged write
- Global Secondary Indexes (GSIs) only support eventual reads

**L5 extra**

- Strong reads go to the partition leader; eventual reads can use any replica
- Avoid strong reads by returning `ALL_NEW` from the write
- GSI lag is usually small but unbounded under GSI throttling
  - Result: never use a GSI read to check uniqueness; use a condition on a base item

### Q3 Preventing A Lost Update

**Q:** Two users edit the same order at once. How do you prevent a lost update? ([06conditions-updates](02dynamodb.06conditions-updates.md#3-optimistic-lock))

**L4 answer**

- Store a `version` number on the item
- Update with `ConditionExpression: version = :expected` and `SET version = version + 1`
- On `ConditionalCheckFailedException` → re-read, re-apply, retry or return 409

**L5 extra**

- `ReturnValuesOnConditionCheckFailure=ALL_OLD` returns the winner's item ⇒ no extra read
- Enhanced Client `@DynamoDbVersionAttribute` adds the condition automatically
- For commutative changes (counters), `ADD` avoids the lock entirely, but is not idempotent
- Expose version as an Entity Tag (ETag) + `If-Match` in the Application Programming Interface (API)

### Q4 Paginating A Query For API Clients

**Q:** How do you paginate a Query and expose it to API clients? ([07query-pagination-scan](02dynamodb.07query-pagination-scan.md#2-pagination))

**L4 answer**

- Each response returns at most 1 megabyte (MB) or `Limit` items
- If `LastEvaluatedKey` is present, pass it as `ExclusiveStartKey`
- Return it to the client as an opaque cursor

**L5 extra**

- `Limit` counts items evaluated before the filter
  - Result: pages can be short or empty, but not final
- Base64 the key map; validate the PK on decode so a client cannot jump partitions
- Cursors are stable under inserts (keyset), unlike OFFSET
- No total count: `Select=COUNT` still reads every item

### Q5 Keys For Orders By Time And Pending Orders

**Q:** Design keys for "a customer's orders by time" and "all pending orders". ([05single-table-design](02dynamodb.05single-table-design.md))

**L4 answer**

- `PK=CUSTOMER#<id>`, `SK=ORDER#<iso>#<orderId>`
  - Then: Query with `begins_with` or `BETWEEN`
- GSI1: `GSI1PK=STATUS#<status>`, `GSI1SK=<iso>`
  - Then: oldest pending first

**L5 extra**

- `STATUS#PENDING` is a hot GSI key
  - Result: shard it (`STATUS#PENDING#0..N-1`) and scatter-gather
- REMOVE `GSI1PK` on terminal states ⇒ sparse index stays small
- `INCLUDE` projection keeps GSI writes cheap; fetch details from the base table if needed
- Fixed-width timestamps, or the sort order breaks

### Q6 BatchWriteItem Vs TransactWriteItems

**Q:** BatchWriteItem vs TransactWriteItems? ([08batch-ops](02dynamodb.08batch-ops.md), [09transactions-idempotency](02dynamodb.09transactions-idempotency.md))

**L4 answer**

- Batch: up to 25 items, not atomic, no conditions, returns `UnprocessedItems`
- Transaction: up to 100 items, all-or-nothing, conditions allowed, 2x cost

**L5 extra**

- Batch partial failure is normal under throttling
  - Result: resend leftovers with full-jitter backoff
- Transactions fail as a whole with per-action reasons
  - `TransactionConflict` is retryable
  - `ConditionalCheckFailed` is not
- Use batch for bulk loads, transactions for invariants

### Q7 Idempotent Place Order

**Q:** Make "place order" idempotent. ([09transactions-idempotency](02dynamodb.09transactions-idempotency.md#3-idempotent-place-order-use-case))

**L4 answer**

- Client sends an `Idempotency-Key`
- One transaction
  - Put the order (`attribute_not_exists(PK)`)
  - Put the idempotency record (`attribute_not_exists`)
- Record exists → return the stored result

**L5 extra**

- Scope the key by caller (`customerId#key`) so two customers cannot collide
- Store a request hash; same key with a different body → 422
- `ALL_OLD` on the idempotency put returns the stored result inside the cancellation reason
- Time To Live (TTL) deletion is lazy ⇒ condition `attribute_not_exists(k) OR expiresAt < :now`
- `ClientRequestToken` only covers 10 minutes of identical calls; the record covers the client's horizon

### Q8 Streams And TTL Together

**Q:** How do Streams and TTL work together? ([10streams-ttl](02dynamodb.10streams-ttl.md))

**L4 answer**

- TTL deletes items whose `expiresAt` (epoch seconds) has passed, in the background
- Streams emit a `REMOVE` record with the old image for that delete

**L5 extra**

- Deletion is not exact (typically within days) ⇒ filter expired items on read
- TTL deletes carry `userIdentity.principalId = dynamodb.amazonaws.com`
  - Result: archive only those to Simple Storage Service (S3)
- Streams keep 24 h ⇒ a consumer down longer loses changes
  - Use Kinesis Data Streams for DynamoDB for longer retention

## 2. L5-Only Questions

These test diagnosis and design ownership rather than recall.

### Q9 Sale-Day Throttling On On-Demand

**Q:** On a sale day, order writes throttle although the table is on-demand. Diagnose and fix. ([02partitions-hot-keys](02dynamodb.02partitions-hot-keys.md), [11capacity-modes](02dynamodb.11capacity-modes.md))

**L5 answer**

- Check whether throttles are on the base table or on GSI1
  - All new orders write `GSI1PK=STATUS#PENDING` ⇒ one GSI partition takes every write
  - GSI throttling back-pressures base writes
- Check traffic vs previous peak
  - On-demand absorbs 2x previous peak instantly; more may throttle
- Fix

→ Shard the GSI key with a calculated suffix  
→ Readers scatter-gather N shards and merge by `GSI1SK`  
→ Pre-warm: raise warm throughput before the event (or switch to provisioned at peak)

- Prove it with Contributor Insights on the index

### Q10 New Access Pattern On A Live Single-Table Design

**Q:** Product asks for a new access pattern on a live single-table design. How do you ship it? ([05single-table-design](02dynamodb.05single-table-design.md))

**L5 answer**

- Can a new GSI serve it from existing attributes?
  - Yes → add the GSI online
  - DynamoDB backfills; reads must tolerate backfill lag
- New attribute needed?

→ Writers start writing it (dual write)  
→ Backfill old items with a parallel scan job, conditional updates, throttled  
→ Only then switch reads

- Ad-hoc or analytical → Export to S3 + Athena, not a GSI

### Q11 When Would You Refuse Single-Table Design

**Q:** When would you refuse single-table design? ([05single-table-design](02dynamodb.05single-table-design.md#6-limits))

**L5 answer**

- Entities have unrelated access patterns and different scale
  - Result: separate tables isolate capacity and blast radius
- Many teams own the entities
  - Result: one table couples their deployments
- Patterns are not known
  - Result: start relational, move hot paths later
- Trade-off
  - Single table pre-joins related items
  - Multi-table is simpler to evolve and reason about

## Related

- [00index](02dynamodb.00index.md)
- [98tradeoffs](02dynamodb.98tradeoffs.md)
