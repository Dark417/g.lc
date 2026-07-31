# Building Blocks — Numbers, Choices, Traps

## Contents

- [Estimation arithmetic](#estimation-arithmetic)
- [Order-of-magnitude anchors](#order-of-magnitude-anchors)
- [Storage decision table](#storage-decision-table)
- [Canonical tradeoffs](#canonical-tradeoffs)
- [Trap statements](#trap-statements)
- [Sourcing discipline](#sourcing-discipline)

## Estimation arithmetic

Round hard. Precision is not the point; the decision the number forces is the point.

```text
seconds/day          ≈ 10^5          (86,400 — round up)
1M DAU × 10 req/day  = 10^7/day     ≈ 100 QPS average
peak                 = 3–5× average (state the multiplier and why)
1 KB × 10^7/day      = 10 GB/day    ≈ 3.6 TB/year
```

Use this sequence:

1. DAU → requests/day → average QPS → peak QPS.
2. Record size × records/day × retention → storage, then × replication factor.
3. State the read:write ratio because it decides cache strategy and replica topology.
4. State the consequence. Every number must kill an option or unlock one.

## Order-of-magnitude anchors

These are approximate and machine-dependent. Use them for reasoning, not as precise facts.

| Operation | Order of magnitude |
|---|---|
| L1 cache reference | ~1 ns |
| Main memory reference | ~100 ns |
| SSD random read | ~100 µs |
| Round trip within a datacenter | ~0.5 ms |
| Disk seek (spinning) | ~10 ms |
| Cross-continent round trip | ~100–150 ms |
| Single Postgres primary, simple writes | Low thousands of writes/sec before tuning |
| Redis single instance | ~10^5 ops/sec order |
| Kafka partition | ~10 MB/s order; scale with partitions |

Service limits change. Verify Lambda execution ceilings, DynamoDB item size, SQS message size and visibility timeout, and S3 request behavior before relying on a hard limit. Say “I’d check the current limit” rather than reciting from memory.

## Storage decision table

| Need | Reach for | Because | Cost accepted |
|---|---|---|---|
| Transactions, joins, ad-hoc queries | Relational (Postgres/Aurora) | ACID, flexible query, mature ops | Vertical ceiling; sharding is a project |
| Known key, huge scale, predictable access | DynamoDB/Cassandra | Horizontal scale, predictable p99 | Access patterns fixed early; secondary indexes cost and lag |
| Full-text or faceted search | OpenSearch/Elasticsearch | Inverted index, relevance scoring | Not a source of truth; reindexing and cluster ops |
| Hot low-latency reads | Redis | In-memory, rich structures | Invalidation, memory cost, limited default durability |
| Blobs and large objects | S3/object store | Cheap, durable, effectively unbounded | Latency and no general query surface |
| Ordered event log, replay, fan-out | Kafka | Durable partitioned log, independent consumers | Operational weight; ordering only within a partition |
| Simple decoupling, one consumer group | SQS | Managed, low operational burden | No general replay; FIFO reduces throughput |
| Time-series metrics | Timescale/Prometheus | Time partitioning and downsampling | Not general purpose |

Naming a product is worth nothing without the key design and consequence. Prefer: “DynamoDB, partition key `tenantId#date`, which spreads the hot tenant but makes cross-tenant queries a GSI read.”

## Canonical tradeoffs

| Tradeoff | Take this side when | Take the other side when |
|---|---|---|
| Sync vs async write path | Caller needs the result to proceed | Work is durable-then-deferred; caller needs only an acknowledgement |
| Read-through vs write-through cache | Reads dominate and staleness is tolerable | Freshness matters more than write latency |
| Push vs pull fan-out | Read-heavy with bounded fan-out | Huge fan-out makes writes explode |
| Strong vs eventual consistency | Money, inventory, authorization | Feeds, counters, presence, analytics |
| Optimistic vs pessimistic locking | Conflicts are rare | Conflicts are common or concentrated on hot keys |
| Single-region vs multi-region | Latency/compliance permit and ops budget is small | Residency or regional-failure SLA requires it |
| Monolith vs services | Team is small and domain unstable | Independent scaling or deployment is the constraint |
| Idempotency key vs dedupe store | Client can generate a stable key | Client cannot; server owns TTL-window dedupe |

For a hybrid answer, state the split rule. Example: push for normal accounts and pull above a follower threshold justified by fan-out arithmetic.

## Trap statements

| Trap | Correct framing |
|---|---|
| “Kafka guarantees exactly-once.” | Kafka offers exactly-once semantics within a transactional read-process-write scope. External side effects still require idempotency. |
| “Add a cache to make it fast.” | A cache trades latency for invalidation, stampede, and memory problems. Name the strategy. |
| “NoSQL scales; SQL does not.” | Both scale differently and surrender different properties. Size the actual load first. |
| “Shard by user ID.” | State what becomes expensive: cross-user queries, rebalancing, and hot users. |
| “Eventually consistent, so it is fine.” | State the staleness window and visible user behavior. |
| “Use a load balancer for high availability.” | Name health checks, draining, partial failure, and the load balancer’s own failure mode. |
| “Microservices for scalability.” | Services buy independent deploy/scale and cost distributed transactions, network failure, and operational surface. |
| “Retry on failure.” | Use bounded backoff, jitter, and a retry budget to prevent storms. |
| “ZooKeeper/etcd for coordination.” | Name what is coordinated and whether a lease, compare-and-swap, or single writer is sufficient. |

## Sourcing discipline

- Show arithmetic or cite precise numbers with a date/version anchor.
- Verify or hedge service limits.
- Cite public postmortems, status pages, or talks for incidents; otherwise label `Canonical failure pattern (not a specific incident)`.
- Mark uncertainty explicitly with `> ⚠️ Low confidence:`.
