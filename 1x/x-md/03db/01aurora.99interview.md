# 03db.01aurora.99interview Interview Questions

> Aurora PostgreSQL interview questions with L4 answers, L5 extras, and L5-only design questions.

## Index

- [1. Storage And Replicas](#1-storage-and-replicas)
  - [Q1 Aurora vs Relational Database Service (RDS) Storage](#q1-aurora-vs-relational-database-service-rds-storage)
  - [Q2 Missing Own Write](#q2-missing-own-write)
  - [Q3 Failover From The App](#q3-failover-from-the-app)
  - [Q4 Identity and Access Management (IAM) Auth Pitfalls](#q4-identity-and-access-management-iam-auth-pitfalls)
- [2. Engine And Concurrency](#2-engine-and-concurrency)
  - [Q5 Isolation Levels](#q5-isolation-levels)
  - [Q6 Job Queue On Postgres](#q6-job-queue-on-postgres)
  - [Q7 OFFSET vs Keyset](#q7-offset-vs-keyset)
  - [Q8 Optimistic vs Pessimistic](#q8-optimistic-vs-pessimistic)
- [3. L5-Only Questions](#3-l5-only-questions)
  - [Q9 Checkout Without Double Charging](#q9-checkout-without-double-charging)
  - [Q10 Writer At 90 Percent CPU](#q10-writer-at-90-percent-cpu)
  - [Q11 When SERIALIZABLE Hurts](#q11-when-serializable-hurts)
- [Related](#related)

## 1. Storage And Replicas

Questions on the storage layer, endpoints, failover and authentication.

### Q1 Aurora vs Relational Database Service (RDS) Storage

**Q:** How does Aurora store data differently from RDS PostgreSQL?

- Concept file: [01architecture](01aurora.01architecture.md)

**L4 answer**

- RDS writes pages and Write-Ahead Log (WAL) to its own Elastic Block Store (EBS) volume; replicas keep full copies
- Aurora's writer sends only redo log records to a shared storage volume
- Each 10 gigabytes (GB) segment has 6 copies in 3 Availability Zones (AZs); commit needs 4 acks
- Replicas read the same volume, so they don't copy data

**L5 extra**

- Quorum overlap: 4 + 3 > 6 and 2·4 > 6
  - Reads see the latest write, no split writes
- Survives AZ + 1 node for reads, a full AZ for writes
- Normal reads hit one known-current segment, not a quorum
- Small segments repair in seconds, shrinking the double-failure window
- Cost: a network hop per page miss, and pricing per I/O or Aurora Capacity Unit (ACU)
- 🗣 "Aurora moves replication from the database to the storage layer: the writer ships redo log records, and storage turns them into pages."

### Q2 Missing Own Write

**Q:** A user creates an order and immediately can't see it. Why, and how do you fix it?

- Concept file: [02endpoints-replica-lag](01aurora.02endpoints-replica-lag.md)

**L4 answer**

- The read went to the reader endpoint; the replica had not applied the commit yet
- Lag is usually under 100 milliseconds (ms) but not zero
- Read from the writer for flows that must see their own writes

**L5 extra**

- Version or Log Sequence Number (LSN) token
  - Client sends the version it wrote
  - Read the reader, fall back to the writer if behind
- Sticky-to-writer window per session after a write
- Trade-off: every fallback adds writer load; measure the fallback rate
- Monitor `AuroraReplicaLag`; a Central Processing Unit (CPU)-starved reader lags more

### Q3 Failover From The App

**Q:** Walk through an Aurora failover from the application's point of view.

- Concept files: [03failover-dns](01aurora.03failover-dns.md), [10retries-idempotency](01aurora.10retries-idempotency.md)

**L4 answer**

- Writer dies; Aurora promotes a reader and repoints the cluster endpoint Domain Name System (DNS)
- Open connections break; the app must reconnect and retry
- Takes tens of seconds (Amazon Web Services (AWS): typically under 60 s)

**L5 extra**

- Cached DNS sends new connections to the demoted node ⇒ `25006`; evict on it
- Retry the whole transaction
  - A lost COMMIT ack is ambiguous ⇒ idempotency key
- Retry budget must span the failover window, but stay under the request deadline
- AWS Java Database Connectivity (JDBC) Wrapper or RDS Proxy cut failover time by not depending on DNS

### Q4 Identity and Access Management (IAM) Auth Pitfalls

**Q:** Why use IAM auth, and what breaks if you implement it naively?

- Concept file: [05iam-auth-tls](01aurora.05iam-auth-tls.md)

**L4 answer**

- No password in config; access follows the IAM role
- Token is valid 15 minutes and needs Transport Layer Security (TLS)

**L5 extra**

- Token is checked only at login ⇒ open connections outlive it
- Naive: generate once at startup ⇒ every new connection after 15 min fails
- Fix: password supplier per physical connection
  - Wrapper DataSource (Java) / callable kwargs (Python)
- Verified on HikariCP 6.3.3: the pool reads credentials via `getCredentials()`
  - So overriding `getPassword()` in a subclass does nothing
- AWS recommends under about 200 new IAM connections per second ⇒ jitter reconnects

## 2. Engine And Concurrency

Questions on PostgreSQL isolation, locking, queues and pagination.

### Q5 Isolation Levels

**Q:** Explain PostgreSQL's isolation levels and when you'd pick each.

- Concept file: [08isolation-levels](01aurora.08isolation-levels.md)

**L4 answer**

- READ COMMITTED default: each statement sees committed data as of its start
- REPEATABLE READ: one snapshot for the transaction
- SERIALIZABLE: behaves as if transactions ran one at a time

**L5 extra**

- Repeatable Read (RR) is snapshot isolation
  - Stronger than American National Standards Institute (ANSI) RR (no phantoms) but allows write skew
- RR raises `40001` when updating a row changed after the snapshot (first updater wins)
- SERIALIZABLE is Serializable Snapshot Isolation (SSI)
  - Predicate SIREAD locks
  - Aborts on dangerous dependency cycles
  - False positives
- Both need whole-transaction retries
- SERIALIZABLE unavailable on read replicas

### Q6 Job Queue On Postgres

**Q:** How would you build a job queue on Postgres?

- Concept file: [13skip-locked-queue](01aurora.13skip-locked-queue.md)

**L4 answer**

- Table of jobs; workers claim with `SELECT … FOR UPDATE SKIP LOCKED LIMIT n`
- Mark them running, process, mark done

**L5 extra**

- Claim and process in separate transactions; claim sets a lease (`locked_until`)
- Complete only if still the lease owner; reaper requeues expired leases
- At-least-once ⇒ idempotent handlers
- Partial index on `READY` rows
- Limit is polling and index churn ⇒ Simple Queue Service (SQS)/Kafka at high rates

### Q7 OFFSET vs Keyset

**Q:** Why does OFFSET pagination get slow, and what replaces it?

- Concept file: [14pagination](01aurora.14pagination.md)

**L4 answer**

- The database reads and throws away all skipped rows
- Keyset: `WHERE (created_at, id) < cursor ORDER BY … LIMIT n`

**L5 extra**

- Needs a unique tie-breaker and a matching composite index
- Stable under concurrent inserts; cannot jump to page k
- Opaque cursor lets you change the sort key later

### Q8 Optimistic vs Pessimistic

**Q:** Optimistic vs pessimistic locking: when each?

- Concept file: [12locking](01aurora.12locking.md)

**L4 answer**

- Optimistic: version column, fail on 0 rows updated, client retries
- Pessimistic: `SELECT … FOR UPDATE` blocks others until commit

**L5 extra**

- Optimistic wins with low contention and long think time (human edits)
- Pessimistic wins with high contention on short critical sections
- Often best: one atomic conditional UPDATE, no read at all
- Pessimistic needs key-ordered locking and `lock_timeout`

## 3. L5-Only Questions

Design ownership, scale, and ambiguity.

### Q9 Checkout Without Double Charging

**Q:** Design the data layer for a checkout service on Aurora that must survive failover without double charging.

- Concept files: [10retries-idempotency](01aurora.10retries-idempotency.md), [09transactions-propagation](01aurora.09transactions-propagation.md), [06pools-rds-proxy](01aurora.06pools-rds-proxy.md)
- Writer pool for writes, reader pool for catalog reads
  - Read-your-writes via writer
- Idempotency key per checkout
  - Unique column, `ON CONFLICT DO NOTHING` + fetch
- One transaction
  - Order insert
  - Stock decrement (conditional UPDATE)
  - Outbox row
- Payment call outside the transaction
  - Outbox relay drives it with its own idempotency key
- Retry whole transaction on `40001`/`40P01`/`08xxx`/`25006`
  - Jittered backoff spanning ~30–60 s
- Pool sizing from `max_connections`, not from request concurrency

### Q10 Writer At 90 Percent CPU

**Q:** Your Aurora writer is at 90% CPU from writes. What are your options, in order?

- Concept file: [98tradeoffs](01aurora.98tradeoffs.md)

1. Find waste first
   - Performance Insights top Structured Query Language (SQL)
   - Missing indexes, N+1 queries, chatty transactions
2. Batch writes, drop unused indexes (each index = extra write)
3. Move reads off the writer to replicas or a cache
4. Scale up the writer (max ACU / larger class)
5. Then partition the write path
   - Limitless sharding
   - Split by domain
   - Move a key-value hot path to DynamoDB

- Trade-off: each step adds operational cost; sharding changes the data model

### Q11 When SERIALIZABLE Hurts

**Q:** When does SERIALIZABLE hurt more than it helps, and what do you use instead?

- Concept file: [08isolation-levels](01aurora.08isolation-levels.md)
- Hurts when
  - High contention on the same predicate ⇒ abort-retry storms, wasted work
  - Sequential scans widen predicate locks to the table ⇒ false positives
- Alternatives
  - Lock a parent row (`SELECT … FOR UPDATE` on the customer)
    - Serializes only that customer
  - Materialize the invariant in a row (running total) and update it atomically
  - Constraint or exclusion constraint where the invariant fits one

## Related

- [00index](01aurora.00index.md)
- [98tradeoffs](01aurora.98tradeoffs.md)
