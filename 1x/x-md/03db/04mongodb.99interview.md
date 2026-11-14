# 03db.04mongodb.99interview Interview Questions

> L4 baseline answers with L5 extras; each points to the file that explains it.

## Index

- [1. Model And Queries](#1-model-and-queries)
- [2. Cluster And Consistency](#2-cluster-and-consistency)
- [3. L5 Only](#3-l5-only)
- [Related](#related)

## 1. Model And Queries

Questions about documents, schema, indexes, and queries.

- **Q1. Embed or reference: how do you decide?**
  - L4: embed what is read together and bounded; reference shared or unbounded data ([03](04mongodb.03schema-design.md))
  - L5 extra: extended reference copies display fields; name the rename fan-out cost
- **Q2. Why is a document update atomic but a two-document change not?**
  - L4: the document lock covers one document; operators like `$inc` run inside it ([04](04mongodb.04crud-update-operators.md))
  - L5 extra: redesign so the invariant lives in one document before reaching for a transaction
- **Q3. How do you design a compound index?**
  - L4: Equality, Sort, Range order (ESR) ([06](04mongodb.06indexes.md))
  - L5 extra: check `totalKeysExamined / nReturned` in explain; aim near 1
- **Q4. Why not paginate with skip?**
  - L4: skip walks n entries per page ⇒ linear cost, shifting pages ([08](04mongodb.08pagination.md))
  - L5 extra: keyset on `(createdAt, _id)` with an opaque cursor
- **Q5. Where should `$match` go in a pipeline?**
  - L4: first, so it uses an index and shrinks input ([09](04mongodb.09aggregation.md))
  - L5 extra: `$merge` into a materialized collection for dashboards

## 2. Cluster And Consistency

Questions about replica sets, concerns, transactions, and sharding.

- **Q6. What happens when the primary dies?**
  - L4: secondaries elect a new primary in seconds; drivers retry writes once ([10](04mongodb.10replica-sets-oplog.md))
  - L5 extra: `w:1` writes not yet replicated are rolled back
- **Q7. Explain write concern and read concern.**
  - L4: `w:majority` = acked by most members; `readConcern majority` = no rollback reads ([11](04mongodb.11read-write-concern.md))
  - L5 extra: causal consistency sessions give read-your-writes on secondaries
- **Q8. How do you retry a transaction correctly?**
  - L4: rerun on `TransientTransactionError`, retry commit on `UnknownTransactionCommitResult` ([12](04mongodb.12transactions.md))
  - L5 extra: write skew under snapshot isolation; force a conflict on a shared document
- **Q9. How do you pick a shard key?**
  - L4: high cardinality, even frequency, present in the common query ([13](04mongodb.13sharding.md))
  - L5 extra: monotonic keys create a hot shard; reshard cost
- **Q10. How do you build a reliable change-stream consumer?**
  - L4: save the resume token after processing; idempotent handler ([14](04mongodb.14change-streams.md))
  - L5 extra: alert when lag approaches the oplog window

## 3. L5 Only

Design ownership questions.

- **Q11.** MongoDB, DynamoDB, or Postgres for an order service with flexible attributes? Defend with access patterns ([98](04mongodb.98tradeoffs.md))
- **Q12.** A collection hit 2 terabytes (TB) and writes are hot on one shard. Walk through diagnosis and fix
- **Q13.** Atlas vs DocumentDB on Amazon Web Services (AWS): which features would block you?

## Related

- [Index](04mongodb.00index.md)
- [98 Tradeoffs](04mongodb.98tradeoffs.md)
