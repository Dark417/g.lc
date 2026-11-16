# 4data-rds-ds — Relational Schema Design

- **In plain words:** relational schema design decides which tables exist, what columns and keys they have, and how they link, so the data stays correct and the queries you need stay fast.
- `-ds` = design file; engine internals (MVCC, locking, isolation) live in [03db Aurora docs](../03db/01aurora.00index.md) and [4persistence.md](4persistence.md)
- Siblings: [4data-nosql-ds.md](4data-nosql-ds.md) (MongoDB, DynamoDB, S3), [4data-redis-ds.md](4data-redis-ds.md) (cache keys)

## Index

- [0. One-Minute Version](#0-one-minute-version)
- [1. The Method](#1-the-method)
- [2. Entities And Relationships](#2-entities-and-relationships)
- [3. Keys And IDs](#3-keys-and-ids)
- [4. Normalization And When To Break It](#4-normalization-and-when-to-break-it)
- [5. Constraints As Business Rules](#5-constraints-as-business-rules)
- [6. Indexes From Queries](#6-indexes-from-queries)
- [7. Common Modeling Problems](#7-common-modeling-problems)
- [8. Scale: Partitioning And Sharding The Schema](#8-scale-partitioning-and-sharding-the-schema)
- [9. Schema Evolution](#9-schema-evolution)
- [10. Worked Example: Orders](#10-worked-example-orders)
- [11. Failure Modes](#11-failure-modes)
- [12. Interview Questions](#12-interview-questions)
- [References](#references)

---

## 0. One-Minute Version

- **What:** tables, columns, keys, constraints and indexes for one domain
- **Why:** the schema is the last line of defense for correctness and the main driver of query speed
- **How:** list entities and access patterns → normalize to 3NF → add constraints for every invariant → index for the real queries → denormalize only where a measured read needs it
- **Catch:** a schema is expensive to change once data and callers depend on it
- 🗣 "I put invariants in the database as constraints, design indexes from the query list, and denormalize only for a read path I can name."

## 1. The Method

1. List the entities and their relationships from the requirements (nouns and verbs)
2. List the queries with frequency: "orders for a customer, newest first, 20 per page"
3. List the invariants: "an order's total equals its items' sum", "a seat sells once"
4. Draft tables in 3NF; pick primary keys
5. Add constraints: `NOT NULL`, `UNIQUE`, `CHECK`, foreign keys
6. Add indexes that serve each query; check with `EXPLAIN`
7. Estimate size and growth; decide partitioning only if numbers demand it

## 2. Entities And Relationships

- **In plain words:** each kind of thing gets a table; links between things become foreign keys or a join table.

| Relationship | How to model | Example |
|---|---|---|
| 1:1 | FK with `UNIQUE`, or merge into one table | `user` ↔ `user_profile` |
| 1:N | FK on the "many" side | `order_item.order_id → order.id` |
| N:M | Join table with a composite key | `student_course(student_id, course_id)` |
| Self-reference | FK to the same table | `employee.manager_id → employee.id` |
| Hierarchy | Adjacency list, closure table, or materialized path | Categories, org charts |

- Put attributes on the join table when the relationship has data (`enrollment.grade`, `order_item.quantity`)

## 3. Keys And IDs

| Option | Good at | Bad at |
|---|---|---|
| Natural key (email, ISBN) | Meaningful, no extra column | Values change; PII in every FK |
| Sequence / identity (`BIGINT`) | Small, fast, ordered B-tree inserts | Guessable; needs coordination across shards |
| UUID v4 | Generated anywhere | Random inserts fragment B-tree indexes; 16 bytes |
| UUID v7 / Snowflake | Generated anywhere and time-ordered | Leaks creation time; Snowflake needs worker ids |

- Default: surrogate `BIGINT` identity internally (or UUID v7 when ids are created across services), plus a `UNIQUE` constraint on the natural key
- Expose opaque ids in APIs, never sequential ids that reveal volume or invite enumeration

## 4. Normalization And When To Break It

- **In plain words:** normalization means storing each fact once; denormalization means copying a fact on purpose so reads get faster.
- 1NF: atomic columns, no repeating groups; 2NF: no partial dependency on a composite key; 3NF: no column depends on another non-key column
- Denormalize when a hot read needs it, and own the cost of keeping copies in sync
  - Counters (`post.like_count`), snapshots (`order_item.unit_price` at purchase time), read models built from events
- Snapshot vs reference: an order must keep the price paid, not join to today's price

## 5. Constraints As Business Rules

- `NOT NULL` for required facts; `CHECK (amount_cents >= 0)`; `UNIQUE (tenant_id, email)`
- Foreign keys prevent orphans; in sharded systems they often go, so the app must enforce them
- Partial unique index for "one active row": `CREATE UNIQUE INDEX ON subscription(user_id) WHERE status = 'ACTIVE'`
- Exclusion constraints (Postgres) for non-overlapping ranges, like room bookings
- A `UNIQUE` constraint is also the cheapest idempotency guard: insert the request id and let duplicates fail

## 6. Indexes From Queries

- Each query in the list gets an index plan
  - Equality columns first, then the range or sort column: `(customer_id, created_at DESC)`
  - Covering index (`INCLUDE (status, total)`) avoids table lookups
- Keyset pagination needs an index matching the sort: `WHERE (created_at, id) < (?, ?) ORDER BY created_at DESC, id DESC`
- Every index slows writes and takes space; drop unused ones (`pg_stat_user_indexes`)

## 7. Common Modeling Problems

| Problem | Pattern | Catch |
|---|---|---|
| Money | `BIGINT` minor units + `currency CHAR(3)`, or `NUMERIC(19,4)` | Never `FLOAT` |
| Time | `TIMESTAMPTZ` stored in UTC | Business dates (birthdays) are `DATE`, not timestamps |
| Soft delete | `deleted_at` column + partial indexes | Every query must filter; unique constraints need `WHERE deleted_at IS NULL` |
| Audit history | History table filled by trigger or app, or event log | Grows fast; partition by time |
| Status / state machine | `status` column + `CHECK`, transitions guarded by `UPDATE … WHERE status = 'PENDING'` | Concurrent transitions without the guard |
| Flexible attributes | `JSONB` column with a GIN index | Loses type checks; don't hide core fields there |
| Multi-tenancy | `tenant_id` in every table and every index; row-level security | One missing filter leaks data |
| Optimistic locking | `version INT` incremented on update | Clients must send the version back |

## 8. Scale: Partitioning And Sharding The Schema

- Partition big tables by time or tenant (Postgres declarative partitioning) to prune scans and drop old data cheaply
- Sharding needs a shard key that every hot query includes (`tenant_id`, `customer_id`)
- Keep data that is joined or updated together on the same shard (co-location)
- Cross-shard: no foreign keys, no cheap joins, globally unique ids (UUID v7 / Snowflake)

## 9. Schema Evolution

- Expand and contract
  → Add the new column (nullable) and deploy code that writes both  
  → Backfill in batches  
  → Switch reads to the new column  
  → Stop writing the old one, then drop it in a later release
- Avoid long locks: create indexes concurrently (`CREATE INDEX CONCURRENTLY`), add `NOT NULL` via a validated `CHECK` first
- Migrations are versioned code (Flyway, Liquibase) and run before the app version that needs them

## 10. Worked Example: Orders

```sql
CREATE TABLE customer (
  id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  email       TEXT NOT NULL UNIQUE,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE "order" (
  id            BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  customer_id   BIGINT NOT NULL REFERENCES customer(id),
  status        TEXT NOT NULL CHECK (status IN ('PENDING','PAID','SHIPPED','CANCELLED')),
  total_cents   BIGINT NOT NULL CHECK (total_cents >= 0),
  currency      CHAR(3) NOT NULL,
  request_id    TEXT NOT NULL UNIQUE,              -- idempotency key from the client
  version       INT NOT NULL DEFAULT 0,             -- optimistic locking
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE order_item (
  order_id          BIGINT NOT NULL REFERENCES "order"(id),
  line_no           INT NOT NULL,
  sku               TEXT NOT NULL,
  quantity          INT NOT NULL CHECK (quantity > 0),
  unit_price_cents  BIGINT NOT NULL,                -- snapshot at purchase time
  PRIMARY KEY (order_id, line_no)
);
CREATE INDEX order_by_customer ON "order"(customer_id, created_at DESC) INCLUDE (status, total_cents);
```

- Query "my orders, newest first" → served by `order_by_customer` with keyset pagination
- Duplicate submit → `request_id` unique violation → return the existing order
- Concurrent status change → `UPDATE … SET status='PAID', version=version+1 WHERE id=? AND version=?`

## 11. Failure Modes

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Duplicate rows | No unique constraint on a natural key or request id | Data audits, double charges | `UNIQUE` constraint, upsert |
| Orphans | No foreign keys | Joins return nulls | FKs, or app-level checks in sharded systems |
| Slow queries as data grows | Missing or wrong index; offset paging | p99 climbs; `EXPLAIN` shows seq scans | Index per query; keyset pagination |
| Write slowdown | Too many indexes; random UUID v4 keys | Insert latency, index bloat | Drop unused indexes; time-ordered ids |
| Outage during migration | Locking `ALTER TABLE` on a big table | Blocked queries | Expand and contract; concurrent index builds |
| Money errors | `FLOAT` columns | Rounding complaints | Integer minor units or `NUMERIC` |

## 12. Interview Questions

**Q1. How do you design the schema for a new feature?**
- L4: entities and relationships, 3NF tables, keys, constraints, indexes for the main queries
- L5 extra: start from access patterns and invariants with numbers; say which reads you'll denormalize and how the copies stay in sync

**Q2. UUID or auto-increment primary key?**
- L4: auto-increment is compact and index-friendly; UUIDs can be generated anywhere
- L5 extra: random UUID v4 fragments B-trees; UUID v7 or Snowflake keeps time order while allowing distributed generation; never expose sequential ids publicly

**Q3. How do you change a column on a large live table?**
- L4: a migration tool, run in a low-traffic window
- L5 extra: expand and contract across several releases, backfill in batches, concurrent index builds, no long table locks

## References

- [PostgreSQL docs — Constraints](https://www.postgresql.org/docs/current/ddl-constraints.html) and [Indexes](https://www.postgresql.org/docs/current/indexes.html)
- [Use The Index, Luke](https://use-the-index-luke.com/) — index design from queries
- Martin Kleppmann, *Designing Data-Intensive Applications*, ch. 2–3
