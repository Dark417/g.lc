# Messaging Systems — Google L4 / L5 Interview Review Guide

**How to use this document**

- **Part 1 — Index.** Questions only, layered by system → subsection. Use it as a self-test: read a line, answer out loud, then check Part 2.
- **Part 2 — Answers.** Every question from Part 1, answered twice: `L4` = the answer that passes a Google L4 bar (correct, concrete, mechanism-aware). `L5` = the answer that passes an L5 bar (tradeoffs, operational reality, failure analysis, org/ownership boundaries).
- **Part 3 — Code.** Java/Spring Boot + AWS reference implementations of the patterns.

**Interviewer's framing (why the L4/L5 split looks the way it does):** L4 is expected to *use* the system correctly and know what happens when it breaks. L5 is expected to *own* the system — pick the technology, define the delivery contract, design the failure envelope, and explain what the on-call engineer sees at 3am. If your answer never mentions a config knob, a metric, or a tradeoff, it's an L4 answer no matter how long it is.

---

# PART 1 — INDEX (questions only)

## System 1 — Apache Kafka

### 1.1 Architecture & core concepts
- `KA-1` What are the components of a Kafka cluster, and what does each one own?
- `KA-2` What is a topic, a partition, and a segment? How is a partition stored on disk?
- `KA-3` What is an offset? Where are consumer offsets stored?
- `KA-4` What does the controller do? What changed with KRaft vs ZooKeeper?
- `KA-5` What is a consumer group and a group coordinator?
- `KA-6` How does a producer decide which partition a record goes to?
- `KA-7` What is the ISR (in-sync replica set)? How does a replica enter and leave it?
- `KA-8` Walk through the full lifecycle of one record: `producer.send()` → consumer business logic.
- `KA-9` Why is Kafka fast? What does it do that a traditional broker doesn't?
- `KA-10` What is a Kafka record actually made of (key, value, headers, timestamp)?

### 1.2 Producer semantics
- `KP-1` What do `acks=0`, `acks=1`, `acks=all` mean, and what can be lost with each?
- `KP-2` What is the idempotent producer and what problem does it solve?
- `KP-3` What are `linger.ms`, `batch.size`, and `compression.type` trading off?
- `KP-4` What is `max.in.flight.requests.per.connection` and how can it reorder records?
- `KP-5` What is the difference between `retries`, `request.timeout.ms`, and `delivery.timeout.ms`?
- `KP-6` What are Kafka transactions? What does `transactional.id` protect against?
- `KP-7` What happens when the producer buffer fills up?
- `KP-8` How do you handle a send failure in application code?

### 1.3 Consumer semantics & consumer groups
- `KC-1` How are partitions assigned to consumers? What assignment strategies exist?
- `KC-2` What triggers a rebalance? What is a rebalance storm?
- `KC-3` Eager vs cooperative (incremental) rebalancing — what's the difference?
- `KC-4` What is static group membership and when do you use it?
- `KC-5` `session.timeout.ms` vs `heartbeat.interval.ms` vs `max.poll.interval.ms` — what does each protect?
- `KC-6` What is the consequence of the number of consumers exceeding the number of partitions?
- `KC-7` Auto-commit vs manual commit — what breaks with each?
- `KC-8` What does `auto.offset.reset` do, and when does it actually fire?
- `KC-9` How do you reprocess history (replay) for one consumer group?
- `KC-10` What is `isolation.level=read_committed` and what is the LSO?

### 1.4 Delivery guarantees & idempotency
- `KD-1` Define at-most-once, at-least-once, exactly-once — in terms of what step fails.
- `KD-2` The classic: consumer crashes after processing but before committing the offset. What happens?
- `KD-3` Does Kafka give you exactly-once? Where does it stop?
- `KD-4` How do you build an idempotent consumer?
- `KD-5` What is the outbox pattern and what problem does it solve?
- `KD-6` What is the inbox pattern / dedup table? What are its operational costs?
- `KD-7` How do you make a non-idempotent downstream call (payment, email) safe under retry?

### 1.5 Ordering & partitioning
- `KO-1` What ordering guarantee does Kafka actually give?
- `KO-2` How do you choose a partition key?
- `KO-3` What is a hot partition / key skew, and how do you fix it without breaking ordering?
- `KO-4` You need global ordering across the whole topic. What do you tell the requester?
- `KO-5` How do you change the partition count of a live topic, and what breaks?
- `KO-6` How do you handle out-of-order or late events at the consumer?

### 1.6 Replication, durability & consistency
- `KR-1` How does replication work? What is a leader vs follower?
- `KR-2` What is `min.insync.replicas` and how does it interact with `acks=all`?
- `KR-3` What is unclean leader election and what is the tradeoff?
- `KR-4` What happens to producers and consumers when a broker dies?
- `KR-5` Where does Kafka sit on CAP, and is it linearizable?
- `KR-6` How do you deploy Kafka across AZs / regions? What is MirrorMaker 2 for?

### 1.7 Retention, storage & compaction
- `KT-1` What are the retention policies and how does retention actually delete data?
- `KT-2` What is log compaction and when do you use it instead of time retention?
- `KT-3` What is a tombstone, and what is `delete.retention.ms` protecting?
- `KT-4` How do you handle large messages / payloads over `message.max.bytes`?
- `KT-5` What is tiered storage and what does it change about capacity planning?

### 1.8 Design patterns & best practices
- `KB-1` When do you use Kafka instead of an HTTP call?
- `KB-2` When do you use Kafka instead of SQS?
- `KB-3` Event notification vs event-carried state transfer vs event sourcing — how do you pick?
- `KB-4` How do you version and evolve an event schema without breaking consumers?
- `KB-5` How do you structure retries: blocking retry, retry topics, or DLQ?
- `KB-6` How do you design a DLQ that is actually usable in production?
- `KB-7` How do you apply backpressure to a Kafka consumer?
- `KB-8` How do you decide topic count, partition count, and replication factor for a new service?
- `KB-9` What belongs in a message payload and what doesn't?
- `KB-10` How do you propagate trace context and tenant context through messaging?

### 1.9 Failure models & operations
- `KF-1` Consumer lag is growing. Walk through your diagnosis.
- `KF-2` A poison message is blocking a partition. What happens and what do you do?
- `KF-3` Rebalances are happening every few minutes. Root causes?
- `KF-4` Broker OOM vs consumer OOM — how do you tell them apart and fix each?
- `KF-5` Under-replicated partitions are alerting. What's going on?
- `KF-6` Duplicates appeared downstream after a deploy. How do you investigate?
- `KF-7` A consumer group's offsets were reset/lost. What are your options?
- `KF-8` The producer is timing out but brokers look healthy. What do you check?
- `KF-9` What are the top metrics and alerts you'd put on a Kafka-backed pipeline?
- `KF-10` What happens if a topic's disk fills up?

### 1.10 Ownership boundary — infra vs application engineer
- `KI-1` What does the platform/infra team own for Kafka?
- `KI-2` What does the application engineer own?
- `KI-3` Which configs are the most common source of production incidents when defaults are left alone?
- `KI-4` Self-managed Kafka vs MSK vs Confluent Cloud — how do you choose?

---

## System 2 — AWS SQS (with SNS / EventBridge)

### 2.1 Architecture & model
- `SA-1` What is SQS architecturally, and how does it differ from Kafka's model?
- `SA-2` What is the message lifecycle in SQS?
- `SA-3` Short polling vs long polling — what problem does long polling solve?
- `SA-4` What are the key SQS limits you design around?
- `SA-5` Is SQS a log? Can you replay from it?

### 2.2 Standard vs FIFO
- `SF-1` Standard vs FIFO — guarantees, throughput, and cost of each.
- `SF-2` What are `MessageGroupId` and `MessageDeduplicationId`?
- `SF-3` What does FIFO "exactly-once processing" actually mean, and what's the window?
- `SF-4` What is high-throughput FIFO and what do you give up?
- `SF-5` A single slow message group is blocking a FIFO queue. What happens?

### 2.3 Visibility timeout & consumption
- `SL-1` What is the visibility timeout and what is the correct way to size it?
- `SL-2` What happens if processing takes longer than the visibility timeout?
- `SL-3` What is a visibility heartbeat and when do you need it?
- `SL-4` What are delay queues and per-message delay used for?
- `SL-5` How do batch receive and batch delete change your failure handling?
- `SL-6` How does Lambda's SQS event source mapping differ from a self-managed poller?

### 2.4 DLQ, retries & redrive
- `SD-1` How does the SQS redrive policy work?
- `SD-2` How do you size `maxReceiveCount`?
- `SD-3` How do you retry with backoff in SQS (there is no native backoff)?
- `SD-4` How do you redrive messages out of a DLQ safely?
- `SD-5` What do you alert on for a DLQ?

### 2.5 SNS, fanout & EventBridge
- `SN-1` SQS vs SNS — when do you use each?
- `SN-2` Why is SNS → SQS the standard fanout pattern instead of SNS → service directly?
- `SN-3` What are SNS message filter policies and why do they matter for cost?
- `SN-4` What is raw message delivery and why does it trip people up?
- `SN-5` SNS vs EventBridge vs Kinesis vs SQS — decision framework.
- `SN-6` What are the delivery guarantees and failure modes of SNS itself?

### 2.6 Scaling, cost & operations
- `SS-1` How does SQS scale, and what does the consumer side need to do?
- `SS-2` How do you autoscale consumers on queue depth?
- `SS-3` What drives SQS cost and how do you reduce it?
- `SS-4` What are the main SQS failure modes in production?
- `SS-5` What do you monitor on an SQS-backed pipeline?

### 2.7 Ownership boundary
- `SI-1` What does the infra/platform team own for SQS/SNS?
- `SI-2` What does the application engineer own?
- `SI-3` Which SQS defaults most often cause incidents?

---

## System 3 — Other systems (breadth)

### 3.1 Google Cloud Pub/Sub
- `OP-1` What is the Pub/Sub model and how does it differ from Kafka?
- `OP-2` Push vs pull subscriptions — when do you use each?
- `OP-3` How does Pub/Sub do ordering, and what's the cost?
- `OP-4` What is Pub/Sub exactly-once delivery and how does it work?
- `OP-5` What are seek, snapshots, and dead-letter topics used for?

### 3.2 RabbitMQ
- `OR-1` What is the AMQP model (exchange, binding, queue) and how does routing work?
- `OR-2` How does RabbitMQ differ from Kafka in consumption model?
- `OR-3` What are publisher confirms, consumer acks, and prefetch?
- `OR-4` How do you do delayed retry in RabbitMQ?
- `OR-5` When is RabbitMQ the right choice over Kafka?

### 3.3 Kinesis Data Streams
- `OK-1` What is the Kinesis model and how does it map to Kafka concepts?
- `OK-2` What is enhanced fan-out and what problem does it solve?
- `OK-3` How does KCL checkpointing work and what's the DynamoDB table for?
- `OK-4` Kinesis vs Kafka vs SQS — when do you pick Kinesis?

### 3.4 Selection
- `OC-1` Give a decision framework for picking a messaging technology.
- `OC-2` Queue vs log vs stream processor — what's the actual distinction?

---

## System 4 — Cross-cutting patterns (technology-independent)

- `PT-1` Transactional outbox — mechanics, CDC vs polling, failure modes.
- `PT-2` Inbox / idempotent receiver — schema, TTL, contention.
- `PT-3` Idempotency at the business-effect level — natural keys, conditional updates, state machines.
- `PT-4` Claim check for large payloads.
- `PT-5` Saga — orchestration vs choreography, compensating actions.
- `PT-6` Competing consumers vs partitioned consumers.
- `PT-7` Retry taxonomy: transient vs permanent, backoff + jitter, budget.
- `PT-8` Circuit breaker and bulkhead in a consumer.
- `PT-9` Schema registry and compatibility modes.
- `PT-10` Backpressure and flow control end-to-end.
- `PT-11` Poison message quarantine and replay tooling.
- `PT-12` Observability contract for async systems.
- `PT-13` Testing async systems.
- `PT-14` Migration: HTTP → async, or SQS → Kafka.

---

# PART 2 — ANSWERS

> Format: `L4` = sufficient answer. `L5` = the layer that gets the senior signal. If you remember one thing per question, remember the L5 bullet that names a **config, metric, or tradeoff**.

---

## System 1 — Apache Kafka

### 1.1 Architecture & core concepts

**`KA-1` Components of a Kafka cluster**
- **L4**
  - **Broker** — server holding partition data, serving produce/fetch.
  - **Topic** — named logical stream; **partition** — unit of parallelism and ordering.
  - **Producer / Consumer** — clients; consumers organized into **consumer groups**.
  - **Controller** — one broker elected to manage cluster metadata and leader assignment.
- **L5**
  - Broker responsibilities: append-only log storage per partition, replication (leader + follower fetch), request handling (network threads → request queue → IO threads), group coordination, transaction coordination.
  - Two internal topics matter operationally: `__consumer_offsets` (50 partitions by default, compacted) and `__transaction_state`.
  - Controller owns the metadata log, partition leader election, ISR changes, broker registration. In KRaft it is a Raft quorum of controller nodes; metadata itself is a replicated log (`__cluster_metadata`).
  - Clients are thick: partitioning, batching, retry, offset tracking and group membership all live client-side. That is why most "Kafka problems" are client-config problems.
  - Boundary answer: brokers store and replicate; **they do not track per-message consumption state**. That single design choice is why Kafka replays cheaply and why it cannot do per-message ack/nack like SQS or RabbitMQ.

**`KA-2` Topic / partition / segment; on-disk layout**
- **L4**
  - A topic is split into N partitions; each partition is an ordered, immutable, append-only log.
  - Each partition has one leader broker, replicated to followers.
  - Partitions are split into **segment** files; old segments are deleted or compacted.
- **L5**
  - Directory `topic-partition/` holds `.log` (records), `.index` (offset → byte position, sparse), `.timeindex` (timestamp → offset), plus producer-state snapshots.
  - Segment roll driven by `segment.bytes` (default 1 GB) and `segment.ms`. **Retention operates at segment granularity** — a topic can exceed `retention.ms` until the active segment rolls. Small retention + 1 GB segments deletes nothing.
  - Reads are sequential with `sendfile` zero-copy from page cache; writes are sequential appends. Kafka deliberately relies on the OS page cache instead of a JVM cache — hence "small heap, lots of RAM."
  - Partition count is the parallelism ceiling per consumer group and the unit of rebalance/replication/file handles. Over-partitioning costs open files, longer leader election, slower failover, larger metadata.

**`KA-3` Offsets**
- **L4**
  - Offset = monotonically increasing position of a record within a partition.
  - Consumers track the next offset to read; committed offsets live in the internal compacted topic `__consumer_offsets`, keyed by `(group, topic, partition)`.
- **L5**
  - Three distinct offsets: **current position** (in-memory), **committed offset** (durable, drives recovery), **high watermark / log-end offset** (broker side). Lag = HW − committed.
  - Because `__consumer_offsets` is compacted, group state survives a full consumer fleet restart.
  - Offsets can be stored externally, in the same DB transaction as the side effect, using `ConsumerRebalanceListener` + `seek()` on assignment — a legitimate exactly-once-ish design and the best answer to "EOS without Kafka transactions."

**`KA-4` Controller / KRaft vs ZooKeeper**
- **L4**
  - ZooKeeper historically stored cluster metadata and elected the controller. Modern Kafka uses **KRaft**: a built-in Raft quorum, no ZooKeeper.
- **L5**
  - ZK problem: metadata propagation was O(partitions); controller failover on a large cluster could take minutes; two consensus systems to operate.
  - KRaft: metadata is an event log that brokers replay and cache, so a new controller already has state in memory — near-instant failover, scales to millions of partitions.
  - Practical impact: faster failover, one system to run, changed tooling (`kafka-metadata-quorum`). ZooKeeper mode is removed in Kafka 4.x.

**`KA-5` Consumer group & group coordinator**
- **L4**
  - A consumer group is a set of consumers sharing `group.id`; each partition is assigned to exactly one member. Scaling stops at partition count.
  - The **group coordinator** is a broker (chosen by hashing `group.id` onto an `__consumer_offsets` partition) tracking membership, heartbeats and commits.
- **L5**
  - Protocol: `FindCoordinator` → `JoinGroup` (coordinator elects a leader *client*) → leader client computes the assignment → `SyncGroup` distributes it → `Heartbeat` maintains membership.
  - **Assignment is computed client-side** — which is why custom assignors exist and why a version-mismatched client can break a whole group.
  - Two groups on one topic get independent copies; that is Kafka's fanout mechanism (no AMQP-style exchange).
  - KIP-848 moves assignment server-side and makes rebalances incremental by default — worth naming for currency.

**`KA-6` Producer partitioning**
- **L4**
  - Explicit partition if provided → else `murmur2(key) % numPartitions` → else spread across partitions.
- **L5**
  - Null-key behavior is the **sticky partitioner** (2.4+): fill one partition's batch, then switch. Better batching than round-robin, but bursty short-window distribution — surprising in tests.
  - Hashing is over *serialized key bytes*, so changing serializer or key type silently reshuffles ordering.
  - A custom `Partitioner` is the escape hatch for tenant isolation or skew, but it must be deployed to **every** producer or ordering breaks nondeterministically.

**`KA-7` ISR**
- **L4**
  - ISR = replicas (including leader) sufficiently caught up. `acks=all` is acknowledged when all ISR members have the record.
  - A follower leaves ISR if it has not fetched to the leader's log-end offset within `replica.lag.time.max.ms` (default 30 s), and rejoins when caught up.
- **L5**
  - The **high watermark** is the minimum log-end offset across the ISR, and consumers can only read up to HW — so a slow follower raises consumer-visible latency, not just replication lag.
  - ISR shrink is the leading indicator for most Kafka incidents: GC pause, disk saturation, network, heavy leader election.
  - Durability is `min.insync.replicas`, not `replication.factor`. RF=3 / minISR=2 / `acks=all` tolerates one broker loss with no data loss and no write outage; minISR=3 is more durable but any single broker loss stops writes.

**`KA-8` End-to-end record lifecycle**
- **L4**
  - `send()` → serialize → partition → accumulate into batch → sender thread ships to leader → broker appends → followers replicate → ack → consumer `poll()` → deserialize → business logic → commit offset.
- **L5**
  - `send()` returns a `Future` immediately; the callback runs on the **sender IO thread** — blocking there stalls the entire producer.
  - Broker side: append to leader log → followers `Fetch` → HW advances → ack for `acks=all`.
  - Consumer side: `poll()` returns from a prefetched buffer, not one network call per record; a fetcher thread pipelines fetches. Heartbeats run on a **background thread**, but `max.poll.interval.ms` is enforced by the poll loop — that split causes most "consumer keeps dropping out" incidents.
  - Ordering-relevant failure point: retry of a failed batch while a later batch is in flight, unless idempotence is on.

**`KA-9` Why Kafka is fast**
- **L4**
  - Sequential disk I/O, zero-copy reads, batching, compression, no per-message broker-side state.
- **L5**
  - Zero-copy (`sendfile`) sends page cache → socket with no JVM copy — **but it is disabled when the broker must recompress or down-convert message format**, a real perf cliff caused by old clients.
  - Compression is end-to-end (producer compresses the batch, broker stores it compressed, consumer decompresses), so broker CPU stays low. `zstd` for ratio, `lz4` when CPU-bound.
  - Cost side: p99 latency is governed by `linger.ms`, replication and page-cache misses on backfill reads. Kafka is a throughput system tunable for latency, not a low-latency system by default.

**`KA-10` Record anatomy**
- **L4**
  - Key, value, headers (byte k/v pairs), timestamp, plus broker-assigned partition and offset.
- **L5**
  - Key drives partitioning and compaction identity. **Null key ≠ tombstone** — a null *value* is the tombstone.
  - Headers are the right place for cross-cutting metadata: `traceparent`, `messageId`, `schemaVersion`, `tenantId`, `retryCount`, `originalTopic`. Keeps schema churn out of the payload.
  - Two timestamp types (`CreateTime` vs `LogAppendTime`, set by `message.timestamp.type`). Retention and time-based seek use it — a producer with a skewed clock can cause premature deletion under `CreateTime`.

### 1.2 Producer semantics

**`KP-1` acks**
- **L4**
  - `acks=0` fire-and-forget, loss on any failure. `acks=1` leader-only, loses data if the leader dies before replication. `acks=all` all ISR members have it.
- **L5**
  - `acks=all` alone is not durable — pair with `min.insync.replicas>=2`, otherwise an ISR shrunk to one makes `all` equal to `1`.
  - Cost: one extra replication round trip (single-digit ms in-AZ; cross-AZ it dominates latency).
  - Rule: telemetry/metrics can take `acks=1`; anything that is a system of record takes `acks=all` + minISR 2 + `unclean.leader.election.enable=false`.

**`KP-2` Idempotent producer**
- **L4**
  - `enable.idempotence=true` (default since 3.0). The broker dedups producer retries so a network retry does not create a duplicate record.
- **L5**
  - Mechanism: broker assigns a **PID** and producer **epoch**; the producer stamps a monotonic **sequence number per partition**; broker keeps the last 5 sequences per PID/partition and rejects duplicates or gaps (`OutOfOrderSequenceException`).
  - Requires `acks=all`, `retries>0`, `max.in.flight<=5`. It also **preserves ordering under retry** — the underrated half.
  - Scope limit: it dedups retries of one producer session for one partition. It does **not** dedup application-level double sends, and without `transactional.id` the PID state is lost across producer restarts. State this unprompted; it is the standard follow-up.

**`KP-3` linger.ms / batch.size / compression**
- **L4**
  - `batch.size` = max bytes per per-partition batch; `linger.ms` = how long to wait to fill it. Higher = better throughput and compression, worse latency.
- **L5**
  - Send fires when either the batch is full or linger expires; `linger.ms=0` still batches whatever accumulates while a request is in flight.
  - Typical production tuning: `linger.ms` 5–20 ms, `batch.size` 64–256 KB, `compression.type=zstd|lz4`. Compression ratio is per batch, so tiny batches compress badly — linger and compression are coupled decisions.
  - `buffer.memory` (default 32 MB) bounds the accumulator; buffer size ÷ throughput = how long you survive a broker slowdown before `send()` blocks.

**`KP-4` max.in.flight and reordering**
- **L4**
  - Number of unacked requests per connection. With retries and >1 in flight, a retried batch can land after a later batch → reordering.
- **L5**
  - With `enable.idempotence=true` the broker enforces sequence order, so up to 5 in flight is safe *and* ordered. Setting it to 1 without idempotence is the old, slow way.
  - Trap question "ordering *and* throughput?" → idempotent producer + `max.in.flight<=5` + keyed partitioning. Not `max.in.flight=1`.

**`KP-5` retries / request.timeout.ms / delivery.timeout.ms**
- **L4**
  - `request.timeout.ms` bounds one request; `retries` bounds attempts; `delivery.timeout.ms` is the total wall-clock budget from `send()` to success/failure.
- **L5**
  - `delivery.timeout.ms` (default 120 s) is the one that matters — it supersedes `retries` (default `MAX_INT`). Constraint: `delivery.timeout.ms >= linger.ms + request.timeout.ms`.
  - `retry.backoff.ms` avoids hammering a broker mid-election.
  - Design point: the producer budget must be shorter than the upstream HTTP timeout, otherwise you return 5xx while the record still lands — a phantom duplicate at the business level.

**`KP-6` Transactions & transactional.id**
- **L4**
  - Transactions atomically write to multiple partitions/topics and commit consumer offsets together — the basis of exactly-once read-process-write inside Kafka.
  - Consumers must set `isolation.level=read_committed` to hide aborted records.
- **L5**
  - Mechanism: transaction coordinator + `__transaction_state`; commit/abort markers written into data partitions; consumers filter by markers and stop at the **LSO** (last stable offset).
  - `transactional.id` provides **zombie fencing**: `initTransactions()` bumps the epoch and the old instance's writes are rejected. It must be **stable per logical producer instance** — random UUIDs defeat fencing and leak coordinator state.
  - Costs: throughput drop, added latency (read_committed consumers cannot advance past an open transaction), and a hung transaction blocks the LSO for everyone on that partition (`transaction.timeout.ms`).
  - Hard boundary: EOS holds **only when the side effect is Kafka**. Kafka → external DB/API is at-least-once + idempotency.

**`KP-7` Producer buffer full**
- **L4**
  - `send()` blocks up to `max.block.ms` (default 60 s), then throws `TimeoutException`.
- **L5**
  - This is Kafka's backpressure signal into your app. Blocking 60 s inside a web request is an outage — set `max.block.ms` near your SLA (1–2 s) and fail fast or spill to an outbox.
  - Causes: broker slow/unreachable, ISR shrink stalling `acks=all`, DNS/auth failure, or genuine over-production. Metrics: `buffer-available-bytes`, `record-queue-time-avg`, `waiting-threads`.

**`KP-8` Handling send failures in code**
- **L4**
  - Use the async callback / `Future`; on exception log with the key and either retry or write to a fallback store. Never swallow silently.
- **L5**
  - Classify: **retriable** (`NotLeaderOrFollower`, `NotEnoughReplicas`, timeouts — the client already retried) vs **non-retriable** (`RecordTooLarge`, serialization, auth, `InvalidTopic`) — the latter must alert, not retry.
  - If the record must not be lost and the DB write already happened, you have a dual-write problem; the answer is the **outbox pattern**, not a better retry loop.
  - Never block in the callback (sender thread) — hand off to an executor.

### 1.3 Consumer semantics & consumer groups

**`KC-1` Partition assignment strategies**
- **L4**
  - `Range` (per-topic contiguous ranges, skews with multiple topics), `RoundRobin` (even across topics), `Sticky` (even + minimal movement), `CooperativeSticky` (sticky + incremental rebalance).
- **L5**
  - `CooperativeSticky` is the modern default: keeps warm state (caches, connections, local aggregation) and avoids stop-the-world.
  - Migrating eager → cooperative needs a two-step rolling deploy (list both strategies, then drop the old) — a real operational gotcha.
  - Custom assignors answer rack-aware or workload-weighted assignment.

**`KC-2` Rebalance triggers / storms**
- **L4**
  - Triggers: member join/leave, failed heartbeat, `max.poll.interval.ms` exceeded, partition count change, subscription change, coordinator failover.
  - A storm is a loop where consumers keep timing out and never make progress.
- **L5**
  - Dominant real cause: **processing time > `max.poll.interval.ms`** — the consumer is heartbeating but not polling, gets evicted, triggers a rebalance, which slows everyone, which causes more evictions.
  - Fix order: reduce `max.poll.records`, move slow work off the poll thread with `pause()`/`resume()`, raise `max.poll.interval.ms`, add static membership, switch to cooperative.
  - Also check pod churn (k8s eviction, OOMKill), HPA thrash, GC pauses > `session.timeout.ms`.

**`KC-3` Eager vs cooperative rebalancing**
- **L4**
  - Eager: everyone revokes everything, then reassigns — full stop-the-world. Cooperative: only partitions that actually move are revoked, across two short rounds.
- **L5**
  - Eager: adding one pod to a 50-pod group pauses the whole group. Cooperative: ~1/50 of the work pauses.
  - Cost: one extra rebalance round, and `onPartitionsRevoked` now receives a **partial** set — revocation logic (commit, flush local state) must handle that. Common migration bug.

**`KC-4` Static membership**
- **L4**
  - Set `group.instance.id`; the member keeps identity across restarts, so a rolling restart does not trigger a rebalance (within `session.timeout.ms`).
- **L5**
  - Right tool for stateful consumers on StatefulSets — bind `group.instance.id` to the pod ordinal.
  - Tradeoff: you must raise `session.timeout.ms` to cover restart time, which delays detection of a genuinely dead consumer. You are trading rebalance churn for failure-detection latency. Combine with cooperative for both.

**`KC-5` session.timeout vs heartbeat.interval vs max.poll.interval**
- **L4**
  - `heartbeat.interval.ms` — how often the background thread heartbeats (~1/3 of session timeout).
  - `session.timeout.ms` — time without a heartbeat before the member is dead (process liveness).
  - `max.poll.interval.ms` — max time between `poll()` calls before eviction (processing-loop liveness).
- **L5**
  - Two independent failure detectors: heartbeat catches a dead JVM in seconds; poll interval catches a stuck handler in minutes (default 5 min).
  - Sizing rule: `max.poll.interval.ms > max.poll.records × p99 per-record processing time`, with headroom — then verify against a lag/poll-latency dashboard rather than guessing.
  - `session.timeout.ms` must fall inside the broker's `group.min/max.session.timeout.ms`.

**`KC-6` More consumers than partitions**
- **L4**
  - The extras idle. Partition count is the hard parallelism ceiling per group.
- **L5**
  - So partition count is a capacity decision made at topic creation, and raising it later breaks key→partition ordering (`KO-5`). Over-provision modestly (2–3× current consumer count).
  - Escape hatch when you cannot add partitions: decouple fetch from processing — one poll thread feeding a bounded worker pool keyed by record key (preserves per-key order), `pause()`/`resume()` for backpressure, and commit only up to the lowest incomplete offset.

**`KC-7` Auto-commit vs manual commit**
- **L4**
  - Auto-commit (`enable.auto.commit=true`, every `auto.commit.interval.ms`) commits during `poll()` regardless of processing success → possible loss or duplication.
  - Manual commit after successful processing → at-least-once, which is what you want.
- **L5**
  - Precisely: auto-commit commits the offsets returned by the *previous* poll, so a crash mid-batch loses the unprocessed remainder. It is effectively at-most-once and the most common cause of "we silently dropped events."
  - `commitSync` (blocking, retriable) vs `commitAsync` (fast, no retry — a failed commit later superseded is fine). Idiom: `commitAsync` in the loop, `commitSync` in `finally` and on revoke.
  - Spring: `AckMode.MANUAL_IMMEDIATE` for precision, `BATCH` for throughput. Always commit **after** the durable side effect.

**`KC-8` auto.offset.reset**
- **L4**
  - `earliest` / `latest` / `none`, applied **only when there is no valid committed offset** — new group, or the committed offset aged out.
- **L5**
  - The dangerous case is not a new group; it is an existing group whose committed offset fell **out of retention** (consumer down over a weekend). `earliest` → reprocess everything; `latest` → silent data loss; `none` → throw and force a human decision. For financial pipelines `none` + alerting is often correct.
  - It also fires on `OffsetOutOfRangeException` after truncation or unclean leader election.
  - Alert on `committed offset < log start offset` *before* the reset happens.

**`KC-9` Replay for a consumer group**
- **L4**
  - Stop consumers, `kafka-consumer-groups --reset-offsets --to-earliest|--to-datetime|--shift-by`, restart. Or start a new group with `auto.offset.reset=earliest`.
- **L5**
  - New group is safer: no risk to a working group and it can run side by side. Cost: downstream side effects fire again — replay is only safe if consumers are idempotent. Say that first.
  - Programmatic: `seek()` inside a `ConsumerRebalanceListener`, or `offsetsForTimes()` for point-in-time.
  - For selective replay (one tenant, one key range) you must filter on consume — Kafka has no query. If selective replay is frequent, that argues for an S3/event-store archive alongside the topic.

**`KC-10` read_committed and the LSO**
- **L4**
  - With `isolation.level=read_committed`, consumers skip aborted records and cannot read past the **last stable offset** — the offset before the earliest still-open transaction.
- **L5**
  - Consequence: an open or hung transaction **stalls consumers on that partition** even though committed data exists beyond it. Watch LSO lag and `transaction.timeout.ms` (bounded by broker `transaction.max.timeout.ms`).
  - `read_committed` also imposes a latency floor equal to transaction duration → keep transactions small and short.
  - Default is `read_uncommitted`, so a team can enable transactions on the producer and get none of the guarantee. Classic incident.

### 1.4 Delivery guarantees & idempotency

**`KD-1` The three semantics**
- **L4**
  - At-most-once: commit before processing → loss possible, no duplicates. At-least-once: process then commit → duplicates possible, no loss. Exactly-once: neither, under constraints.
- **L5**
  - Frame it by *where the crash window is*: the gap between the side effect and the offset commit. Effect-then-commit → duplicates. Commit-then-effect → loss. No third option without a shared transaction or dedup.
  - Practical stance: **at-least-once delivery + idempotent processing = effectively-once**. Reserve Kafka transactions for Kafka-to-Kafka.

**`KD-2` Crash after processing, before commit**
- **L4**
  - After rebalance/restart the partition is reread from the last committed offset, so the record is delivered and processed again — at-least-once.
- **L5**
  - Blast radius is the whole uncommitted batch, not one record — `max.poll.records=500` can replay 500 records.
  - Mitigations in preference order: make the effect idempotent (natural key + conditional write); commit more frequently (smaller batches, throughput cost); store offset and effect in one DB transaction (external offset storage).
  - If the effect is a non-idempotent third-party call, you need a dedup/inbox row written **in the same transaction as the call's recorded result**, plus reconciliation for the window where the call succeeded but the row did not commit.

**`KD-3` Does Kafka give exactly-once?**
- **L4**
  - Yes within Kafka: idempotent producer + transactions + `read_committed` gives exactly-once read-process-write (what Kafka Streams uses).
- **L5**
  - Precisely: exactly-once **processing semantics** for Kafka-resident state, not exactly-once *delivery* over a network (two-generals — impossible).
  - It breaks the moment the effect leaves Kafka: DB, HTTP, email, S3 → back to at-least-once + idempotency.
  - Kafka Streams: `processing.guarantee=exactly_once_v2` (v2 uses one producer per instance rather than per task — far cheaper than v1).

**`KD-4` Building an idempotent consumer**
- **L4**
  - Give each message a stable id (business key, or a producer-generated UUID in a header). On consume, check/insert into a dedup store; skip if present.
- **L5**
  - Prefer **natural business keys** (`paymentId`, `orderId + version`) over UUIDs — they dedup across *republishes* by a different producer, not just client retries.
  - Cheapest correct mechanism: a DB **unique constraint** on the natural key with `INSERT ... ON CONFLICT DO NOTHING`, so dedup and effect are one atomic write. "Check then write" is a race.
  - Better: make the effect naturally idempotent — `UPDATE ... WHERE version < :incoming` (conditional / LWW), or a state machine where `PAID → PAID` is a no-op.
  - Operational: dedup table needs TTL or partition-drop, an index matching the lookup, and awareness that hot keys become hot rows.

**`KD-5` Outbox pattern**
- **L4**
  - Problem: DB write and Kafka publish are two systems, so a crash between them loses or fabricates an event.
  - Solution: insert the event into an `outbox` table **inside the same DB transaction**; a relay reads the outbox and publishes, marking rows sent.
- **L5**
  - Two relay implementations: **polling publisher** (simple, adds latency and DB load, needs `SKIP LOCKED` for multiple instances) vs **CDC** (Debezium on the WAL — low latency, no polling, but you now operate Kafka Connect and care about replication slots and WAL retention).
  - Delivery stays at-least-once (relay can crash after publish, before marking sent) → consumers still need idempotency. Never claim outbox = exactly-once.
  - Ordering: key by aggregate id, add an outbox sequence column, publish per-aggregate in order.
  - Housekeeping: delete-after-publish or partition-by-day-and-drop. An unbounded outbox table is a genuine outage source.

**`KD-6` Inbox / dedup table**
- **L4**
  - A table of processed message ids; the consumer checks it before processing and inserts after (ideally in the same transaction).
- **L5**
  - Schema `(message_id, consumer_group)` as the key — include consumer identity so different consumers do not dedup each other's work.
  - Insert-first-then-process gives at-most-once on crash; the correct form is a **single transaction** containing both the effect and the inbox row.
  - Costs: one extra write per message, TTL cleanup, contention on hot keys. If the effect is already idempotent, skip the inbox — it is pure overhead.

**`KD-7` Non-idempotent downstream (payment / email)**
- **L4**
  - Use the provider's idempotency key (e.g. Stripe `Idempotency-Key`) derived deterministically from the message id, so a retry is deduped by the provider.
- **L5**
  - No idempotency key available: record intent first (`status=PENDING` with the message id) → call → record outcome. On replay, a PENDING row means "unknown" → reconcile by querying the provider with your correlation id; do not blindly retry.
  - Add a reconciliation job for that unknown window — this is the part interviewers listen for, because it is what actually happens in payments.
  - For notifications, dedup on `(recipient, templateId, businessEventId)` with a TTL — tune the window rather than chasing perfection.

### 1.5 Ordering & partitioning

**`KO-1` Ordering guarantee**
- **L4**
  - Total order within a partition; **no** order across partitions.
- **L5**
  - It is per-partition ordering *as observed by a single consumer thread* — a multi-threaded handler breaks it in application code even though Kafka preserved it.
  - Producer retries also break it without `enable.idempotence` (`KP-4`).
  - So the real guarantee: same key → same partition → ordered, given idempotent producer + single-threaded per-partition processing + no partition-count change.

**`KO-2` Choosing a partition key**
- **L4**
  - Pick the entity whose events must stay ordered: `accountId`, `orderId`, `userId` — gives per-entity ordering and even spread at high cardinality.
- **L5**
  - Three criteria in tension: ordering scope; cardinality ≫ partition count; uniform distribution of **traffic**, not of keys. High key cardinality with power-law traffic (one whale tenant) still creates a hot partition.
  - Consider consumer-side locality too — keying by tenant lets you cache tenant config per partition.
  - Anti-pattern: keying on a low-cardinality enum (`region`, `eventType`) — 4 keys, 32 partitions, 28 idle.

**`KO-3` Hot partition / key skew**
- **L4**
  - Symptom: one partition's lag grows while others are flat. Causes: low-cardinality key or a dominant key.
  - Fixes: composite key (`tenantId#bucket`), more partitions, or a separate topic for the whale.
- **L5**
  - Salting (`key + "#" + n % N`) sacrifices strict per-key ordering — acceptable only if the effect is commutative or version-stamped. Be explicit about what you give up.
  - Order-preserving alternatives: a dedicated partition/topic for the hot key with its own consumer (isolation, not sharding); or application-level version stamping so out-of-order writes are dropped.
  - Detection: per-partition lag and bytes-in, plus a top-K key sampler on the producer. "We saw it in lag-per-partition" is the answer they want.

**`KO-4` Global ordering across a topic**
- **L4**
  - Only with a single partition — capping throughput at one consumer and one broker write path.
- **L5**
  - Challenge the requirement first: what is almost always needed is per-entity ordering, a monotonic version so consumers can order themselves, or an event-time watermark with a bounded reorder buffer.
  - If truly global: single partition + single consumer (fine to tens of MB/s, zero horizontal headroom), or a dedicated sequencer service and consumer-side sorting.
  - This is a scoping test as much as a technical one — an L5 answer starts by pushing back.

**`KO-5` Changing partition count live**
- **L4**
  - You can only increase, never decrease. Increasing changes `hash(key) % N`, so existing keys move → **ordering breaks across the change boundary**, and compaction/keyed-state assumptions break.
- **L5**
  - Safe procedure when ordering matters: create a new topic at the target count → dual-write or mirror → drain the old topic → cut consumers over → decommission. It is a topic migration, not a config change.
  - If expanding in place: quiesce producers for affected keys, let consumers drain to zero lag, then expand. The window where both mappings are in flight is the danger zone.
  - This is why partition count is a design decision and modest over-provisioning is cheap insurance.

**`KO-6` Out-of-order / late events**
- **L4**
  - Carry a version or event timestamp; the consumer ignores updates older than current state (`WHERE version < :incoming`).
- **L5**
  - Distinguish **event time** from **processing time**; use a bounded reorder buffer / watermark for windowed aggregation (Kafka Streams grace period, Flink watermarks).
  - Late-arrival policy is a product decision — drop, side-output to a late topic, or recompute the window. Make it explicit and observable (`late_events_total`).
  - Best answer: design state updates as LWW-with-version or CRDT-ish so ordering is not required for correctness at all.

### 1.6 Replication, durability & consistency

**`KR-1` Replication mechanics**
- **L4**
  - Each partition has one leader and N−1 followers; all reads and writes go to the leader; followers pull via `Fetch`. On leader failure a new leader is elected from the ISR.
- **L5**
  - Followers pull rather than the leader pushing — simpler flow control, reuses the consumer fetch path.
  - Leadership is spread across brokers (preferred leader election, `auto.leader.rebalance.enable`); after restarts you often run `kafka-leader-election` to rebalance.
  - Rack awareness (`broker.rack`) places replicas across AZs; `client.rack` + `RackAwareReplicaSelector` enables **follower fetching** for local reads — a large cross-AZ cost saver on AWS.

**`KR-2` min.insync.replicas**
- **L4**
  - Minimum in-sync replicas required for an `acks=all` write; below it, producers get `NotEnoughReplicasException` and writes fail.
- **L5**
  - It is a **topic-level durability/availability dial**: RF=3 + minISR=2 survives one broker loss with writes continuing; minISR=3 is more durable but any single loss halts writes. Availability is deliberately traded for durability.
  - Only meaningful with `acks=all`; with `acks=1` it is ignored — a common misconfiguration.
  - Broker default is overridable per topic; audit per topic rather than assuming.

**`KR-3` Unclean leader election**
- **L4**
  - If enabled, an out-of-sync replica can become leader when no ISR member is available — the partition stays available but records missing from that replica are lost.
- **L5**
  - Disabled by default in modern versions; keep it off for anything transactional. Enabling it makes silent data loss a config choice.
  - Consumer-visible effect: log truncation → `OffsetOutOfRangeException` → `auto.offset.reset` fires → gaps or duplicates depending on the setting.
  - Correct response to "partition offline, cannot write" is to restore the broker or accept the outage — unless the data is genuinely disposable (metrics).

**`KR-4` Broker death — client behavior**
- **L4**
  - Metadata refresh → clients discover new leaders → traffic resumes. Producers see retriable `NotLeaderOrFollower`; consumers refetch from the new leader.
- **L5**
  - Expected impact: seconds of elevated latency and retries; with `acks=all` + minISR, no loss.
  - Turns into an incident when: unclean election is on (loss), minISR too high (write outage), RF=1 (partition offline), or client `delivery.timeout.ms` shorter than failover time (spurious upstream failures).
  - Consumers may see duplicates around failover if commits were in flight — another reason for idempotency.

**`KR-5` CAP position / linearizability**
- **L4**
  - With `acks=all` + minISR, Kafka favors consistency and durability over availability — writes fail rather than diverge. CP-leaning per partition.
- **L5**
  - Per partition it is a single-leader replicated log with a quorum-ish ack rule; reads are bounded by the high watermark, so consumers never see a record that could be lost — close to linearizable per partition for committed data.
  - No cross-partition atomicity except inside a Kafka transaction; no cross-topic consistency at all.
  - With `acks=1` or unclean election it becomes AP-ish with real loss windows. The point: **the CAP position is a configuration, not a property**.

**`KR-6` Multi-AZ / multi-region**
- **L4**
  - Multi-AZ in-region with rack awareness is standard. Multi-region uses **MirrorMaker 2** (or Cluster Linking) to asynchronously replicate topics between clusters.
- **L5**
  - Stretch clusters across regions are usually wrong — replication latency enters every `acks=all` write. Prefer independent regional clusters plus async mirroring.
  - MM2 replicates with a prefix (`us-east.orders`) and offers offset translation, but offsets are **not identical**, so DR failover involves translation and accepted duplicates. Active-active needs cycle prevention and a conflict story.
  - RPO is nonzero by construction. Stating explicit RPO/RTO numbers is the L5 framing.

### 1.7 Retention, storage & compaction

**`KT-1` Retention**
- **L4**
  - `cleanup.policy=delete` with `retention.ms` (default 7 days) and/or `retention.bytes`; whichever hits first deletes eligible segments.
- **L5**
  - Deletion is per **segment** and the active segment is never deleted — effective retention ≥ configured retention, and low-traffic topics can hold data far longer.
  - `retention.bytes` is **per partition**, not per topic — multiply by partitions and replication factor for real disk. Very common capacity error.
  - Retention is a **durability contract with consumers**: it must exceed the maximum tolerable consumer downtime, or you get the `KC-8` reset scenario.

**`KT-2` Log compaction**
- **L4**
  - `cleanup.policy=compact` retains at least the latest value per key indefinitely. Used for changelogs/state; reading from the beginning reconstructs current state.
- **L5**
  - Compaction is asynchronous, so duplicates per key exist until the cleaner runs, and the active segment (log head) is never compacted — consumers must tolerate both.
  - Knobs: `min.cleanable.dirty.ratio` (default 0.5), `min.compaction.lag.ms`, `max.compaction.lag.ms`, cleaner threads. A lagging cleaner is a real disk-fill risk.
  - `compact,delete` is valid and useful — latest per key *and* bounded age.
  - Requires non-null keys; null-key records on a compacted topic are a config bug.

**`KT-3` Tombstones and delete.retention.ms**
- **L4**
  - A null-value record is a tombstone marking a key deleted; compaction eventually removes it and all prior values for that key.
- **L5**
  - `delete.retention.ms` (default 24 h) is how long the tombstone survives compaction so lagging consumers still observe the delete. A consumer lagging beyond it misses the delete and keeps stale state forever — the classic "ghost record" bug.
  - It is also the GDPR-delete mechanism for compacted topics. On `delete`-policy topics you cannot remove a single record — which is why PII usually should not be in the payload (claim check or crypto-shredding with per-subject keys).

**`KT-4` Large messages**
- **L4**
  - Defaults cap around 1 MB (`message.max.bytes` broker, `max.request.size` producer, `max.partition.fetch.bytes` consumer, `replica.fetch.max.bytes`). All must agree or you get stuck replication or `RecordTooLargeException`.
  - Preferred fix: **claim check** — blob in S3, pointer on the topic.
- **L5**
  - Why not raise the limits: large records inflate producer/consumer memory (`max.partition.fetch.bytes × assigned partitions`), cause GC pressure and rebalance timeouts, hurt batching/compression, and slow replication.
  - Claim check adds a lifecycle problem: object retention must exceed topic retention plus max replay window, and you must handle "pointer exists, object gone."
  - Chunking with sequence headers is possible but rarely worth it.

**`KT-5` Tiered storage**
- **L4**
  - KIP-405: brokers keep recent segments locally and offload older ones to object storage, so retention can be months without local disk.
- **L5**
  - Changes capacity planning from "disk sized for retention" to "disk sized for the hot set" — a big win for replay/backfill-heavy topics.
  - Tradeoffs: cold reads hit object storage (higher, more variable latency) and full-history replay can be slow and costly; broker recovery is faster because less local data must re-replicate.
  - Position it as a lever for long-retention event stores, not a default.

### 1.8 Design patterns & best practices

**`KB-1` Kafka vs HTTP**
- **L4**
  - HTTP for synchronous request/response where the caller needs the answer now. Messaging for decoupling, spike absorption, retries, fanout, and workflows tolerant of eventual consistency.
- **L5**
  - Decide on four axes: does the caller need the result to proceed? can the callee's downtime be absorbed? is fanout to unknown consumers likely? is replay/audit valuable?
  - Async is not free — you inherit eventual consistency, duplicates, ordering questions, DLQ ops, and much harder debugging. Do not event-ify simple CRUD.
  - Hybrid is common and correct: synchronous validate + persist, then emit an event for downstream effects — exactly the outbox shape.

**`KB-2` Kafka vs SQS**
- **L4**
  - Kafka: durable ordered log, replay, multiple independent consumer groups, high throughput, per-key ordering. SQS: managed work queue, no ordering (standard), no replay, trivial ops, per-message ack/retry/DLQ built in.
- **L5**
  - Choose SQS when the semantics are "distribute work to a pool" — per-message failure isolation, variable per-message latency, no consumer/partition coupling, scale-to-zero, no cluster to run.
  - Choose Kafka when the data is an **event stream with multiple consumers** needing ordering, replay, retention, or stream processing/joins.
  - Cost shape: SQS is per-request (expensive at very high volume, near-free at low); Kafka is fixed infra + ops headcount (cheap at high volume, absurd at low). Honest default for most teams: SQS unless you need replay or ordering.

**`KB-3` Notification vs state transfer vs event sourcing**
- **L4**
  - Notification: thin event (`OrderPlaced{orderId}`), consumer calls back for details. State transfer: event carries the full payload. Event sourcing: the log *is* the system of record; state is a fold over events.
- **L5**
  - Notification keeps schema coupling low but re-couples at runtime via callback and creates read amplification on the producer.
  - State transfer removes runtime coupling but adds schema coupling and staleness questions; needs versioning discipline and often compaction.
  - Event sourcing is a large commitment: snapshots, replay cost, historical schema migration, a different debugging model. Do not propose it casually in a design round — propose outbox/CDC plus state-transfer events instead.

**`KB-4` Schema evolution**
- **L4**
  - Schema registry with Avro/Protobuf and a compatibility mode; add optional fields with defaults; never rename, repurpose, or remove a required field.
- **L5**
  - Modes: `BACKWARD` (new consumer reads old data — upgrade consumers first, the common case), `FORWARD` (old consumer reads new data — upgrade producers first), `FULL`, and `*_TRANSITIVE` (checked against all versions, usually what you actually want).
  - Protobuf field-number reuse is the killer bug — reserve removed numbers and names.
  - Breaking changes require a new topic or a version field with parallel publish, then drain and retire. There is no in-place breaking change on a topic with retention.
  - Note that JSON-without-registry is the default failure mode in most orgs; adding CI schema-compatibility checks is a concrete L5 proposal.

**`KB-5` Retry strategy**
- **L4**
  - Blocking retry (in place with backoff) is simple but stalls the partition. Non-blocking retry publishes to `topic.retry.5s`, `topic.retry.1m`, … then DLQ after max attempts.
- **L5**
  - Rule: transient and short (a few hundred ms) → blocking retry, ≤3 attempts. Dependent on a downstream outage → non-blocking, because blocking through a 10-minute outage means 10 minutes of partition stall and then a rebalance.
  - Non-blocking retry **breaks ordering for retried keys** — must be explicitly acceptable. Spring implements this with `@RetryableTopic`; the delay works by not advancing the retry-topic consumer until the record's timestamp is due.
  - Classify errors first: deserialization/validation are permanent → DLQ immediately. Retrying a poison record five times is pure added latency.
  - Add a retry budget / circuit breaker so a full downstream outage does not become a DLQ flood.

**`KB-6` A usable DLQ**
- **L4**
  - Separate topic/queue for messages that exhausted retries, preserving the original payload plus error metadata; alert on depth; provide replay after a fix.
- **L5**
  - Required headers: original topic/partition/offset, exception class and message, first/last failure time, attempt count, consumer group, schema version, trace id. Without these it is a graveyard, not a DLQ.
  - Requirements: retention ≥ notice + fix + replay time; a replay tool that filters by error class and republishes with a `replayed=true` header so metrics stay honest; a named owner and a runbook.
  - Ordering caveat: replaying a DLQ record after later records reorders that key — the effect must be order-insensitive or version-checked.
  - Alert on **rate and error-class diversity**, not just depth: one new error class at low rate is often more urgent than a large spike of a known one.

**`KB-7` Backpressure on a consumer**
- **L4**
  - Kafka's pull model is inherently backpressured — poll slower. Control with `max.poll.records`, `fetch.max.bytes`, and `pause()`/`resume()` when internal queues fill.
- **L5**
  - The hazard is that "polling slower" collides with `max.poll.interval.ms`. Correct pattern: poll → hand to a bounded queue → `pause()` when full → **keep calling `poll()`** (returns nothing but keeps membership) → `resume()` when drained.
  - Scale-out backpressure: KEDA/HPA on consumer lag rather than CPU, capped at partition count.
  - Downstream-driven: rate limiter + circuit breaker in the handler, and pause the listener container when the breaker opens.

**`KB-8` Sizing topics, partitions, replication**
- **L4**
  - RF=3, minISR=2 for anything important. Partitions = max(target throughput ÷ per-partition throughput, expected consumer parallelism), plus headroom.
- **L5**
  - Method: measure per-consumer throughput (records/s given p99 handler latency), then `partitions = peak_rate ÷ per_consumer_rate × safety`. Also bounded by broker count (prefer even multiples) and by retention/disk.
  - Guardrails: keep partitions per broker in the low thousands; more partitions means more memory, file handles and slower failover.
  - Topic granularity: one topic per event type per bounded context is usually right. A shared topic with a type header is acceptable when consumers share the ordering scope and accept filtering waste. Avoid one topic per tenant (metadata explosion).

**`KB-9` What goes in the payload**
- **L4**
  - Stable event id, event type and version, occurred-at timestamp, aggregate id, and the minimum data consumers need. Not mutable internal state, secrets, or large blobs.
- **L5**
  - Model events as **facts about the past** with immutable names (`OrderPlaced`, not `OrderUpdate`) — that is what makes them reusable by consumers you have not met.
  - Do not leak internal DB shape; publish a deliberate public contract that survives a refactor.
  - PII: minimize, or hold the payload behind a claim check with its own access control and deletion path. Topic retention is not a deletion mechanism.

**`KB-10` Trace and tenant context**
- **L4**
  - Propagate `traceparent` (W3C) and correlation/tenant ids in **headers**, and restore them into MDC/context in the consumer so logs stitch across the async hop.
- **L5**
  - Async breaks parent-child spans: the consumer span should **link** to the producer span (follows-from), not be a child of a long-finished request span. OTel's Kafka instrumentation does this.
  - The metric that matters is **end-to-end latency** (producer timestamp → processing complete) — invisible on either service's own latency dashboard.
  - Tenant id in headers also enables per-tenant lag metrics, filtering, and selective replay.

### 1.9 Failure models & operations

**`KF-1` Growing consumer lag**
- **L4**
  - Check: all partitions or one (skew)? Input rate spike? Slower processing (downstream latency)? Consumers healthy? All partitions assigned?
  - Fixes: scale consumers (≤ partition count), reduce per-record work, increase batching, fix downstream.
- **L5**
  - Triage order: (1) lag per partition — one partition ⇒ skew or a stuck consumer; all ⇒ capacity or downstream. (2) Is the group rebalancing (`rebalance-rate`)? Lag with churn is a rebalance problem, not a throughput problem. (3) Compare `records-consumed-rate` with the derivative of lag — falling behind vs draining a backlog.
  - Distinguish **lag** from **latency**: a burst leaves lag but fine latency; a slow handler raises both. Alert on lag in **time units** (lag ÷ consumption rate), not record count.
  - Name the ceiling: you cannot scale past partition count, so the fix may be intra-consumer parallelism, not more pods.

**`KF-2` Poison message blocking a partition**
- **L4**
  - The handler throws every attempt; with blocking retry the consumer never advances past that offset, so the partition stalls and lag grows.
  - Fix: catch non-retriable exceptions, route to DLQ, commit past it.
- **L5**
  - Distinguish causes: deserialization failure (fails before your code — needs `ErrorHandlingDeserializer` or a container error handler, otherwise it is an uncatchable loop), business validation failure (DLQ immediately), and downstream 5xx (retry — *not* a poison message).
  - Emergency lever: `kafka-consumer-groups --reset-offsets --shift-by 1` for the stuck partition, after capturing the record and understanding you are intentionally skipping data.
  - Prevention: schema registry + contract tests, defensive deserialization, and a max-attempts policy that always terminates in DLQ. "It can never block forever" should be a design invariant.

**`KF-3` Rebalance storm root causes**
- **L4**
  - Processing exceeding `max.poll.interval.ms`; consumer crashes/restarts; GC pauses exceeding `session.timeout.ms`; pod churn or aggressive autoscaling; coordinator network issues.
- **L5**
  - Diagnostic order: consumer logs for the "leaving group" reason string (Kafka states poll-timeout vs heartbeat vs leave request) → GC logs → pod restart counts → `max.poll.records` × p99 handler latency.
  - Structural fixes: cooperative sticky, static membership with matched `session.timeout.ms`, smaller `max.poll.records`, slow work off the poll thread, HPA stabilization windows.
  - Name the vicious cycle: each rebalance reprocesses uncommitted records, increasing per-poll work, causing the next timeout. Break it by reducing batch size first, then re-tune.

**`KF-4` Broker OOM vs consumer OOM**
- **L4**
  - Consumer OOM: `max.poll.records` × record size × partitions too large, or unbounded internal queues. Lower `max.poll.records`, `max.partition.fetch.bytes`, `fetch.max.bytes`, and bound the work queue.
  - Broker OOM: heap too small for the workload, too many partitions/connections, large messages forcing decompression.
- **L5**
  - Brokers want a **small heap (6–12 GB) and lots of page cache** — a large broker heap is usually a misdiagnosis. Broker heap pressure typically comes from partition count, connection count, or message-format down-conversion (which also disables zero-copy).
  - Consumer fetch buffers alone are roughly `max.partition.fetch.bytes × assigned partitions` — a consumer fine with 4 partitions can OOM after a rebalance hands it 40.
  - Say how you would confirm: GC logs and heap dump, and which side the OOM is on. That distinction is the real question.

**`KF-5` Under-replicated partitions**
- **L4**
  - A follower fell behind beyond `replica.lag.time.max.ms`. Causes: broker down, disk/network saturation, GC pause, unbalanced leadership.
  - Risk: durability drops; crossing `min.insync.replicas` starts failing `acks=all` writes.
- **L5**
  - Three-alert set: `UnderReplicatedPartitions` (should be 0), `UnderMinIsrPartitionCount` (writes failing), `OfflinePartitionsCount` (no leader — hard outage).
  - Investigate which broker is the lagging follower (usually one) → its disk I/O, network, GC. Often a single degraded volume or a broker catching up after restart.
  - Mitigation: throttle reassignment traffic (`--throttle`) so recovery does not starve production traffic; move leadership off the sick broker.

**`KF-6` Duplicates after a deploy**
- **L4**
  - Likely: rebalance on rolling restart reprocessing uncommitted records; commit strategy changed; retries newly enabled. Trace a duplicated business id back to the offsets consumed.
- **L5**
  - Determine whether it is **redelivery** (same partition/offset processed twice — expected at-least-once behavior; the bug is missing idempotency) or **double-produce** (two distinct offsets carrying the same business id — a producer/outbox bug). That distinction decides the fix and is the differentiator on this question.
  - Preventive framing: every deploy is a rebalance, so deploy-time duplicates are *normal*. If users can see them, the design is wrong, not the deploy.

**`KF-7` Offsets reset or lost**
- **L4**
  - Options: reset to earliest (full reprocess — needs idempotency), reset to a timestamp near the incident, or reset to latest (accept the gap).
- **L5**
  - Establish blast radius first: which partitions, what time range, and is there a natural key downstream to reconcile against? Often the right move is targeted replay into a side topic plus a reconciliation job, not a blind full reset.
  - Prevention: `offsets.retention.minutes` (default 7 days) is the usual culprit for an idle group — raise it, or use external offset storage for critical consumers.
  - Always `--dry-run` before `--execute`, and snapshot current offsets first.

**`KF-8` Producer timeouts with healthy brokers**
- **L4**
  - Check `delivery.timeout.ms`/`request.timeout.ms`, buffer exhaustion, ISR below minISR (writes rejected), DNS/advertised-listener issues, TLS/SASL handshake cost, client network path.
- **L5**
  - "Brokers look healthy" usually means broker-level dashboards are fine while one **partition** is not — check per-partition ISR and leadership, not cluster averages.
  - Client metrics tell the story: `record-queue-time-avg` (backpressure), `request-latency-avg` (network/broker), `buffer-available-bytes` (accumulator full), `record-error-rate`.
  - Environmental favorites: advertised listeners resolving to an unreachable address (works from one subnet, not another), and security-group/NAT changes.

**`KF-9` Metrics and alerts**
- **L4**
  - Consumer lag per group/partition, produce/consume rates, error and DLQ rates, under-replicated partitions, broker disk, request latency.
- **L5**
  - Page on: `OfflinePartitionsCount > 0`, `UnderMinIsrPartitionCount > 0`, DLQ rate spike, lag-in-seconds beyond SLO, and **a consumer group with zero members on a live topic** (silent death — the most-missed alert).
  - Ticket on: sustained `UnderReplicatedPartitions`, rebalance rate, disk trending to 80%, schema-registry rejects.
  - Track **end-to-end event latency** (produce timestamp → effect committed) as the user-facing SLI; lag alone misses a slow producer or a stalled downstream.

**`KF-10` Disk full**
- **L4**
  - The log directory goes offline; partitions led by that broker become under-replicated or offline; producers to them fail. Kafka may shut the broker down rather than corrupt data.
- **L5**
  - Immediate levers: reduce `retention.ms`/`retention.bytes` on the largest topics (segment-granular, so not instant), delete or move non-critical topics, add a log dir/volume, expand the volume.
  - Root causes: a compacted topic whose cleaner is behind, `retention.bytes` planned per topic but applied per partition, a runaway producer. Explicitly correct the common misconception: **a lagging consumer does not hold data** — Kafka retention is time/size based, not consumption based.
  - Prevention: disk alerts at 70/80/90% with growth projection, producer quotas (`producer_byte_rate`), tiered storage for long retention.

### 1.10 Ownership boundary

**`KI-1` Platform/infra team owns**
- **L4**
  - Cluster provisioning and sizing, broker configs, replication defaults, KRaft quorum, upgrades/patching, TLS/SASL and ACLs, monitoring and alerting, capacity, DR, MirrorMaker.
- **L5**
  - Also topic-creation policy and naming standards (usually `auto.create.topics.enable=false` plus Terraform or a self-service path), per-client quotas, schema registry operation and compatibility policy, and the **defaults application teams inherit**.
  - The L5 point is the **contract**: infra publishes an SLO (availability, p99 produce latency, retention guarantee) and guardrails; app teams choose within them. A platform that owns everything becomes a bottleneck; one that owns nothing yields twelve incompatible retry strategies.

**`KI-2` Application engineer owns**
- **L4**
  - Topic design (partitions, key, retention request), schema and its evolution, producer/consumer configs (acks, idempotence, commit strategy, `max.poll.*`), error handling, retry/DLQ policy, idempotency, consumer scaling, business-level monitoring.
- **L5**
  - Own the **delivery contract** end to end: what guarantee consumers get, the ordering scope, what happens on failure, the replay procedure, the schema compatibility promise — written down in the service design doc.
  - Own the consumer-lag SLO and the DLQ runbook. Infra can alert; only the owning team can decide whether a DLQ record is safe to replay.

**`KI-3` Dangerous defaults**
- **L4**
  - `enable.auto.commit=true`, `acks=1` on older clients, `min.insync.replicas=1`, `auto.offset.reset=latest`, `max.poll.records=500` with slow processing, `read_uncommitted` while using transactions, 7-day retention when consumers can be down longer.
- **L5**
  - Add: `unclean.leader.election.enable` left on in older clusters, `auto.create.topics.enable=true` (topics born with 1 partition, RF=1), `offsets.retention.minutes` too short for low-traffic groups, and `delivery.timeout.ms=120s` inside a 5-second HTTP handler.
  - The L5 move: ship an internal starter/config library with correct defaults so no team makes these choices independently.

**`KI-4` Self-managed vs MSK vs Confluent Cloud**
- **L4**
  - Self-managed: max control, lowest unit cost at scale, highest ops burden. MSK: AWS-managed brokers, you still own topics/clients/tuning; MSK Serverless removes capacity planning. Confluent Cloud: fully managed with registry and connectors, highest price, lowest ops.
- **L5**
  - Decide on: do you have a platform team with Kafka expertise and on-call? What throughput (unit economics flip at scale)? Do you need registry/connectors/ksqlDB? Compliance and VPC constraints?
  - Default recommendation for a mid-size team: MSK provisioned for steady high throughput, MSK Serverless for spiky/low volume — and honestly SQS/SNS if you do not need log semantics at all. Saying "we do not need Kafka" when true is a strong L5 signal.

---

## System 2 — AWS SQS (with SNS / EventBridge)

### 2.1 Architecture & model

**`SA-1` What SQS is, vs Kafka**
- **L4**
  - A fully managed, distributed **queue**: producers `SendMessage`, consumers `ReceiveMessage`, process, then `DeleteMessage`. Messages are removed once deleted; there is no log to re-read.
  - No partitions, no consumer groups, no offsets. Scaling consumers is just running more pollers.
- **L5**
  - Messages are stored redundantly across multiple AZs; the service is effectively infinitely scalable and there is no capacity to provision. That is the whole value proposition.
  - Consequence of the distributed store: **standard queues are at-least-once with best-effort ordering** — a `ReceiveMessage` hits a subset of servers, so a message can be returned more than once and out of order.
  - Model difference that matters in design rounds: SQS tracks **per-message state** (in-flight, visibility, receive count) which Kafka deliberately does not. That gives per-message retry/DLQ/isolation for free, and costs you replay and multi-consumer fanout.
  - Consumption is destructive → fanout requires SNS or EventBridge in front, one queue per consumer.

**`SA-2` Message lifecycle**
- **L4**
  - `SendMessage` → message stored (optionally delayed) → `ReceiveMessage` returns it and starts the **visibility timeout** → consumer processes → `DeleteMessage` removes it. If not deleted before the timeout expires, it becomes visible again and is redelivered, incrementing `ApproximateReceiveCount`.
- **L5**
  - "In flight" is a real state with a limit (≈120k messages for standard queues, ~20k for FIFO) — exceeding it makes `ReceiveMessage` fail, which is a genuine failure mode for very wide fan-outs of slow consumers.
  - Delete is what acknowledges; there is no negative ack. The way to nack is `ChangeMessageVisibility(0)`, making it immediately redeliverable — worth naming, most candidates do not.
  - Retention (`MessageRetentionPeriod`, default 4 days, max 14) is a hard TTL — a message that never succeeds silently disappears unless a DLQ catches it first. That is why `maxReceiveCount` × visibility timeout must be well under retention.

**`SA-3` Short vs long polling**
- **L4**
  - Short polling samples a subset of servers and often returns empty even when messages exist. Long polling (`ReceiveMessageWaitTimeSeconds` up to 20 s) waits for a message to arrive, returning fewer empty responses.
- **L5**
  - Long polling should be on essentially always: fewer empty receives → lower cost (you pay per API request) and lower latency (the response fires as soon as a message lands, rather than on your next poll).
  - Set it at the queue level (`ReceiveMessageWaitTimeSeconds`) so every client inherits it, rather than relying on each client passing `WaitTimeSeconds`.
  - Short polling's only real use is a latency-sensitive fast drain across many queues.

**`SA-4` Limits you design around**
- **L4**
  - Max message size 256 KB (larger payloads → S3 + Extended Client / claim check); retention 1 min – 14 days; visibility timeout max 12 h; delay max 15 min; batch of 10 for send/receive/delete; long-poll wait max 20 s.
  - Standard: unlimited throughput. FIFO: 300 TPS (3,000 with batching), or much higher in high-throughput mode.
- **L5**
  - The in-flight cap and the retention TTL are the two limits that actually cause incidents; batch size 10 is the one that shapes your code.
  - Note that quotas move — the right interview answer is "here are the ones I design around, and I verify current values in the service quotas page before committing to a design."
  - Design implication of the 12 h visibility max: any job longer than that must be broken into steps (Step Functions) rather than held in a single message.

**`SA-5` Is SQS a log? Replay?**
- **L4**
  - No. Consumption is destructive and there is no offset — once deleted, a message is gone. Replay requires you to have archived the payload elsewhere (S3, a DB, or a DLQ you can redrive).
- **L5**
  - This is the single biggest architectural difference from Kafka and the usual reason a design switches to Kafka/Kinesis: audit, reprocessing after a bug fix, or adding a new consumer that needs history.
  - Workarounds: EventBridge archive + replay; SNS → an S3-archiving SQS consumer; or Kinesis (24 h – 365 d retention) when you need a short replay window with AWS-managed semantics.

### 2.2 Standard vs FIFO

**`SF-1` Standard vs FIFO**
- **L4**
  - Standard: at-least-once, best-effort ordering, effectively unlimited throughput. FIFO: strict ordering within a message group, exactly-once *processing* within the dedup window, limited throughput, and the queue name must end in `.fifo`.
- **L5**
  - Choose standard by default and add idempotency; choose FIFO only when ordering is a real business requirement (financial sequencing, per-account state machines, command streams).
  - FIFO costs: lower throughput, head-of-line blocking within a group, higher per-request price, and no Lambda concurrency beyond the number of active message groups.
  - You cannot convert a queue between types — it is a create-new-and-migrate operation.

**`SF-2` MessageGroupId and MessageDeduplicationId**
- **L4**
  - `MessageGroupId` is FIFO's ordering/parallelism unit — ordering is guaranteed *within* a group, and different groups are processed in parallel. It is the direct analogue of a Kafka partition key.
  - `MessageDeduplicationId` identifies a message for dedup; either supply it or enable content-based dedup (SHA-256 of the body).
- **L5**
  - Group id choice mirrors Kafka key choice: high cardinality for parallelism, aligned to the ordering scope (`accountId`), never a constant (a single group serializes the whole queue).
  - Content-based dedup is dangerous when two legitimately identical messages can occur within the window (e.g. "heartbeat for account X") — supply an explicit dedup id derived from a business key instead.
  - A message group with an in-flight message will not deliver the next message in that group until the first is deleted or times out — that is the ordering mechanism, and also the head-of-line blocking risk.

**`SF-3` FIFO "exactly-once" and the window**
- **L4**
  - Within a **5-minute deduplication interval**, a message with the same `MessageDeduplicationId` sent again is accepted but not delivered. Combined with in-order delivery per group, AWS calls this exactly-once processing.
- **L5**
  - The 5-minute window is fixed and not configurable — so a producer retry 6 minutes later produces a duplicate. FIFO does **not** relieve you of application-level idempotency for anything with a long retry horizon.
  - It also does not dedup a redelivery caused by a consumer failing to delete before the visibility timeout — that is at-least-once *consumption*, orthogonal to the dedup window. Making that distinction is a strong L5 signal.

**`SF-4` High-throughput FIFO**
- **L4**
  - Setting `DeduplicationScope=messageGroup` and `FifoThroughputLimit=perMessageGroupId` raises throughput dramatically by scoping dedup and throughput per group rather than per queue.
- **L5**
  - What you give up: dedup is no longer queue-wide, so the same dedup id in two different groups is not deduped. Fine when your group id is the natural entity key, wrong if you relied on queue-wide dedup.
  - Throughput then scales with group cardinality — so the design lever is the same one as Kafka's: pick a high-cardinality ordering key.

**`SF-5` Slow message group blocking a FIFO queue**
- **L4**
  - Messages within that group queue up behind the slow one (head-of-line blocking), but other groups keep flowing. If the message keeps failing, the group is stuck until `maxReceiveCount` sends it to the DLQ.
- **L5**
  - This is the FIFO equivalent of the Kafka poison-message partition stall, and the mitigation is the same: a strict max receive count so the group always drains, and per-group lag/age monitoring (`ApproximateAgeOfOldestMessage`).
  - Because DLQ-ing a message breaks that group's ordering, the consumer must be able to tolerate a gap — or you need a "quarantine the whole group" policy where subsequent messages for that entity are also parked. Naming that tradeoff is the L5 answer.

### 2.3 Visibility timeout & consumption

**`SL-1` Visibility timeout sizing**
- **L4**
  - Time a received message is hidden from other consumers (default 30 s, max 12 h). Set it to comfortably exceed p99 processing time — typically p99 × 2–3.
- **L5**
  - Too short → duplicate processing while the first consumer is still working (the most common SQS bug). Too long → slow recovery from a crashed consumer, because the message stays hidden for the full timeout.
  - Set it per queue, and override per message with `ChangeMessageVisibility` when the work is variable — prefer a short default plus a heartbeat over a long default.
  - Interaction: `maxReceiveCount × visibilityTimeout` must be far below `MessageRetentionPeriod`, or messages expire before they can reach the DLQ.

**`SL-2` Processing exceeds the visibility timeout**
- **L4**
  - The message becomes visible again and another consumer picks it up → concurrent duplicate processing. The original consumer's eventual `DeleteMessage` may also fail or delete the wrong receipt handle.
- **L5**
  - Note the compounding failure: the duplicate is not just wasted work, it is *concurrent* work on the same entity — so your idempotency has to be concurrency-safe (conditional update / unique constraint / lock), not just replay-safe.
  - Receipt handles are per-receive, so a stale handle's delete is rejected. Never cache receipt handles across receives.
  - Detection: `ApproximateReceiveCount > 1` at scale, and duplicate business effects. Emit receive count as a metric.

**`SL-3` Visibility heartbeat**
- **L4**
  - For long or variable jobs, periodically call `ChangeMessageVisibility` to extend the timeout while work is in progress.
- **L5**
  - This is a lease-renewal pattern: short initial lease (fast failover if the worker dies) plus renewal (no premature redelivery for slow-but-alive work). It is strictly better than a long static timeout.
  - Implementation detail interviewers probe: the heartbeat must run on a **separate scheduler**, and it must stop immediately on completion or failure, or you extend the lease on a dead task. Spring Cloud AWS does this automatically with `Visibility`/`@SqsListener` acknowledgement modes.
  - Cap the total extension so a hung worker cannot hold a message indefinitely — otherwise you have reinvented an unbounded lock.

**`SL-4` Delay queues and per-message delay**
- **L4**
  - Queue-level `DelaySeconds` delays every message; `SendMessage` can also set a per-message delay (both up to 15 min). Used for deferred work and simple backoff.
- **L5**
  - Per-message delay is **not supported on FIFO queues** — only queue-level delay. That single fact kills naive FIFO retry designs.
  - Because the cap is 15 minutes, longer backoff needs either a chain of delay queues, Step Functions `Wait`, or EventBridge Scheduler. Say that instead of hand-waving "we'd add backoff."

**`SL-5` Batch receive / batch delete**
- **L4**
  - Up to 10 messages per `ReceiveMessage`, and `DeleteMessageBatch` deletes up to 10. Batching cuts API cost and latency substantially.
- **L5**
  - The failure-handling subtlety: batch delete has **partial failures** — the response has `Successful` and `Failed` lists, and ignoring `Failed` silently causes redelivery. Same for `SendMessageBatch`.
  - With Lambda, a batch failure by default retries the **whole batch** — enable `ReportBatchItemFailures` and return the failed message ids, or one poison message causes the entire batch to reprocess repeatedly.
  - Batch size is a latency/throughput tradeoff and it also multiplies the visibility timeout requirement (you now need to process 10 messages inside one lease).

**`SL-6` Lambda event source mapping vs self-managed poller**
- **L4**
  - Lambda's event source mapping polls for you, scales concurrency with queue depth, and deletes messages automatically on a successful return. A self-managed poller (ECS/EC2) gives you full control of concurrency, batching, visibility extension, and long-running work.
- **L5**
  - Lambda's rules matter: it scales up in steps, it requires the function timeout to be less than the queue visibility timeout (AWS recommends ≥6×), failures return the whole batch unless `ReportBatchItemFailures`, and there are `MaximumConcurrency` controls to protect a downstream DB from being hammered by scale-out.
  - Choose Lambda for spiky, short, stateless work with no connection-pool concerns; choose ECS pollers for steady throughput, long jobs, warm caches/connection pools, or when you need visibility heartbeats.
  - Cost inversion: Lambda is cheap at low/spiky volume and expensive at sustained high volume, where an always-on ECS poller wins.

### 2.4 DLQ, retries & redrive

**`SD-1` Redrive policy**
- **L4**
  - Attach a `RedrivePolicy` with a `deadLetterTargetArn` and `maxReceiveCount`. When a message's receive count exceeds the limit, SQS moves it to the DLQ instead of making it visible again.
- **L5**
  - The DLQ must be the **same type** as the source queue (FIFO → FIFO) and in the same account/region.
  - The DLQ's retention is independent and should be much longer than the source's (typically 14 days) — a common bug is a DLQ that expires messages before anyone triages them. Note that the enqueue timestamp is preserved from the original send, so retention counts from the original send time.
  - Use `RedriveAllowPolicy` on the DLQ to control which source queues may redrive from it.

**`SD-2` Sizing maxReceiveCount**
- **L4**
  - Enough to absorb transient failures, low enough to fail fast: typically 3–5. `maxReceiveCount = 1` sends everything to DLQ on first failure; very high values delay detection and burn retries.
- **L5**
  - Constraint to state: `maxReceiveCount × visibilityTimeout` must be well under `MessageRetentionPeriod`, or messages die before reaching the DLQ.
  - Also note that a *consumer crash* (not a bad message) increments receive count, so an unstable deployment can DLQ perfectly good messages. That argues for a slightly higher count plus alerting on DLQ arrivals with a "crash-loop" error signature.

**`SD-3` Backoff in SQS**
- **L4**
  - SQS has no native exponential backoff. Options: `ChangeMessageVisibility` with an increasing timeout based on `ApproximateReceiveCount` (the standard trick); a chain of delay queues; or Step Functions with `Retry` and `BackoffRate`.
- **L5**
  - The `ChangeMessageVisibility(receiveCount²·base)` approach is the cheapest and keeps everything in one queue — worth being able to write on a whiteboard.
  - Add jitter or your retries synchronize into thundering herds against a recovering downstream.
  - For Lambda, `ReportBatchItemFailures` plus a maximum retry attempt in the event source mapping is cleaner than hand-rolled backoff for short work.

**`SD-4` Redriving out of a DLQ**
- **L4**
  - Use the DLQ redrive API / console ("Start DLQ redrive") to move messages back to the source queue, or write a script that receives from the DLQ and sends to the source.
- **L5**
  - Redrive is only safe after the root cause is fixed and consumers are idempotent — otherwise you replay the same failure and burn retries again.
  - Do it in **controlled batches with a rate limit** so you do not stampede a just-recovered downstream, and tag replayed messages (message attribute) so metrics and dashboards distinguish replay from live traffic.
  - Always triage first: group DLQ messages by error class; some should be replayed, some fixed and re-sent with corrected payloads, some discarded with a record of the decision.

**`SD-5` DLQ alerting**
- **L4**
  - Alarm on `ApproximateNumberOfMessagesVisible > 0` for the DLQ, and on `ApproximateAgeOfOldestMessage` to catch messages sitting untriaged.
- **L5**
  - Page on the **rate of arrival** and on the appearance of a **new error class**, not merely on depth — a steady trickle of a known error is a ticket, a sudden new class is an incident.
  - Also alarm on `NumberOfMessagesSent` to the DLQ being zero for a queue that historically has some — a silent DLQ can mean a broken redrive policy.
  - Every DLQ needs a named owner and a runbook link in the alarm description. That operational detail is exactly what separates the L5 answer.

### 2.5 SNS, fanout & EventBridge

**`SN-1` SQS vs SNS**
- **L4**
  - SQS is a **pull** queue that buffers work for consumers; SNS is a **push** pub/sub topic that fans a message out to all subscribers. SNS does not store messages for later consumption — if a subscriber is down, delivery is retried and then dropped (or sent to a subscription DLQ).
- **L5**
  - The framing that lands: SQS decouples in **time** (buffering, backpressure, retry), SNS decouples in **topology** (one producer, N unknown consumers). You usually need both.
  - SNS retry behavior differs by protocol: SQS/Lambda targets get near-guaranteed delivery with retries; HTTP endpoints follow a configurable retry policy and then drop.

**`SN-2` Why SNS → SQS instead of SNS → service**
- **L4**
  - The queue gives each consumer independent buffering, retries, DLQ, and backpressure. If a consumer is down, messages wait in its queue instead of being lost.
- **L5**
  - It also decouples consumer scaling from producer rate, isolates a slow consumer from the others (one queue backing up does not affect siblings), and gives per-consumer replay-ish behavior via its own DLQ.
  - Cost note: enable **raw message delivery** so the SQS body is the SNS message rather than a JSON envelope, and apply **filter policies** so you do not pay to deliver messages a consumer will discard.
  - Modern alternative worth naming: EventBridge for content-based routing and archive/replay when the routing rules are complex.

**`SN-3` Filter policies**
- **L4**
  - A JSON policy on the subscription matching against message attributes (or the message body with `MessageBody` scope); non-matching messages are not delivered to that subscriber.
- **L5**
  - It moves filtering from consumer code to the broker — less consumer compute, fewer SQS requests, lower cost, and one less place for a filtering bug.
  - Supports prefix, anything-but, numeric ranges, exists, and OR semantics across values. Filter on **attributes** where possible; body filtering is newer and slightly more limited.
  - Failure mode to watch: a wrong policy silently drops everything, with no error anywhere. Alert on "subscription delivered zero messages" as a canary.

**`SN-4` Raw message delivery**
- **L4**
  - Without it, SNS wraps the payload in a JSON envelope (`Type`, `MessageId`, `TopicArn`, `Message`, …) and the consumer must unwrap `Message`. With `RawMessageDelivery=true` the SQS body is the original payload.
- **L5**
  - The trap: enabling raw delivery **removes the envelope and the message attributes for some protocols**, so consumers reading `MessageAttributes` from the envelope break. Changing it on a live subscription is a breaking change for consumers — version it like an API change.
  - Practical guidance: pick one convention org-wide (raw + attributes carried as SQS message attributes) and enforce it in the Terraform module.

**`SN-5` SNS vs EventBridge vs Kinesis vs SQS**
- **L4**
  - SQS: point-to-point work queue. SNS: high-throughput, low-latency fanout to subscribers. EventBridge: event bus with rich content-based routing, schema registry, archive/replay, many AWS targets. Kinesis: ordered, replayable stream with retention and per-shard consumers.
- **L5**
  - Decide on: routing complexity (EventBridge), latency and throughput (SNS is faster and cheaper per message at volume), replay/audit needs (EventBridge archive or Kinesis), ordering (FIFO SQS or Kinesis), and consumer count (SNS/EventBridge for fanout).
  - EventBridge tradeoffs: higher latency (tens to hundreds of ms), lower throughput ceilings, higher cost per event — but it replaces glue code with declarative rules and gives replay.
  - The senior answer names one and says why *not* the others, rather than listing all four.

**`SN-6` SNS delivery guarantees and failure modes**
- **L4**
  - At-least-once delivery per subscriber, no ordering on standard topics (FIFO topics exist for ordered fanout to FIFO queues). Failures are retried per protocol, then optionally routed to a subscription DLQ.
- **L5**
  - Configure a **subscription-level DLQ** on every important subscription — without it, exhausted retries are silently dropped, which is the most common way teams lose events in AWS.
  - HTTP subscribers need the retry policy tuned (immediate, pre-backoff, backoff, post-backoff phases) and must handle duplicates.
  - Message size and throughput quotas apply per topic; very high fanout to many SQS queues multiplies cost linearly, which is where filter policies pay for themselves.

### 2.6 Scaling, cost & operations

**`SS-1` How SQS scales**
- **L4**
  - The queue itself scales automatically with no configuration for standard queues. The consumer side is your problem: run more pollers/threads, use batching, and use long polling.
- **L5**
  - Constraints to name: the in-flight message cap, per-API-action request rates, and downstream capacity — SQS will happily hand you more work than your database can take, so the queue is not the bottleneck, the consumer's downstream is.
  - Because there is no partition ceiling, consumer parallelism is unbounded — which makes **downstream protection** (connection pool limits, `MaximumConcurrency`, rate limiting) a required part of the design rather than optional.

**`SS-2` Autoscaling consumers on depth**
- **L4**
  - Scale on `ApproximateNumberOfMessagesVisible` or, better, a **backlog-per-instance** target metric (messages ÷ running tasks) with an ECS/Kubernetes target-tracking policy.
- **L5**
  - Depth alone causes thrash; backlog-per-task is the AWS-recommended target-tracking metric and behaves much better.
  - Better still: scale on `ApproximateAgeOfOldestMessage` when your SLO is latency-based — that is what users actually experience, and it captures a stuck consumer that depth misses.
  - Add scale-in stabilization and a floor of 1–2 tasks so you always have a poller to discover a backlog; KEDA's SQS scaler does this cleanly in Kubernetes.

**`SS-3` SQS cost**
- **L4**
  - Priced per API request (plus data transfer). Cost drivers: empty receives from short polling, one-message-per-request patterns, and high-frequency polling on idle queues.
  - Reduce with long polling, batching (10 per request), and fewer pollers on idle queues.
- **L5**
  - A frequent surprise: many idle pollers doing 20-second long polls still generate constant requests × pollers × queues. Consolidate or scale to a small floor.
  - Also count downstream costs: SNS→SQS fanout multiplies request count by subscriber count, which is where filter policies produce real savings.
  - At sustained very high throughput (hundreds of thousands of messages/s) the per-request model is where Kafka/Kinesis becomes cheaper — that is a legitimate build-vs-buy input, not just a preference.

**`SS-4` Main failure modes**
- **L4**
  - Duplicate processing (visibility too short, or at-least-once by design), poison messages looping to the DLQ, DLQ filling silently, message expiry via retention, throttling on API limits, and a consumer overwhelming its downstream.
- **L5**
  - Add the subtle ones: in-flight limit reached (receives start failing); FIFO group head-of-line blocking; a batch delete whose partial failures are ignored, causing silent redelivery; a Lambda batch failing wholesale without `ReportBatchItemFailures`; and messages lost because an SNS subscription had no DLQ.
  - Note the asymmetry vs Kafka: SQS failures are usually **per-message and isolated**, which is a real operational advantage — one bad message does not stall a partition.

**`SS-5` Monitoring**
- **L4**
  - `ApproximateNumberOfMessagesVisible` (backlog), `ApproximateAgeOfOldestMessage` (latency), `ApproximateNumberOfMessagesNotVisible` (in flight), `NumberOfMessagesDeleted` (throughput), DLQ depth, and consumer error rate.
- **L5**
  - Alert on **age of oldest message** as the primary SLI — depth is a capacity signal, age is a user-facing one.
  - Watch `ApproximateReceiveCount` distribution to catch visibility-timeout misconfiguration before it becomes duplicate-processing bugs.
  - Track empty-receive ratio for cost, and in-flight count against the service limit. Every queue should have a DLQ and both should have alarms — no exceptions.

### 2.7 Ownership boundary

**`SI-1` Infra/platform owns**
- **L4**
  - Queue and topic provisioning via Terraform, IAM policies, KMS encryption, DLQ wiring, default settings (long polling, retention, visibility), alarms and dashboards, cost monitoring, and account/region layout.
- **L5**
  - The real deliverable is a **Terraform module** that makes the right thing the default: queue + DLQ + redrive policy + alarms + encryption in one resource, so no team ships a queue without a DLQ.
  - Also: cross-account access patterns, VPC endpoints for SQS, and quota monitoring.

**`SI-2` Application engineer owns**
- **L4**
  - Message schema and versioning, idempotency, visibility timeout sizing to match actual processing time, `maxReceiveCount`, batch handling and partial failures, consumer concurrency, DLQ triage and redrive, business metrics.
- **L5**
  - Own the same **delivery contract** as in Kafka: guarantee, ordering scope, failure behavior, replay procedure. In SQS the replay story must be designed deliberately because the platform gives you none.
  - Own downstream protection: the queue removes backpressure, so the consumer is the only place that can protect the database.

**`SI-3` Dangerous defaults**
- **L4**
  - Visibility timeout left at 30 s while processing takes longer; no DLQ; short polling (`ReceiveMessageWaitTimeSeconds=0`); retention left at 4 days; no `ReportBatchItemFailures` on Lambda; ignoring partial batch failures.
- **L5**
  - Add: content-based dedup enabled on a FIFO queue whose messages are legitimately identical; a constant `MessageGroupId` serializing the whole queue; a DLQ with a shorter retention than the source; and an SNS subscription with no DLQ.

---

## System 3 — Other systems (breadth)

### 3.1 Google Cloud Pub/Sub

**`OP-1` Model vs Kafka**
- **L4**
  - Publishers send to a **topic**; each **subscription** is an independent, durable stream of that topic's messages. Subscribers ack messages individually; unacked messages are redelivered after the ack deadline. Fully managed, no partitions or capacity to provision.
- **L5**
  - It is a hybrid of the two models: SQS-like per-message ack/redelivery, Kafka-like durable multi-consumer fanout (each subscription is effectively a consumer group with its own retention).
  - No partitions means no partition-count ceiling on parallelism — but also no free per-key ordering unless you opt into ordering keys.
  - Retention is per subscription (default 7 days ack deadline extension window; message retention configurable up to 31 days), and `seek` lets you rewind — replay without an offset concept.

**`OP-2` Push vs pull**
- **L4**
  - Pull: the subscriber calls (or streams) to fetch and acks explicitly — best for high throughput and controlled concurrency. Push: Pub/Sub POSTs to an HTTPS endpoint and treats a 2xx as an ack — best for serverless (Cloud Run/Functions) and cross-network delivery.
- **L5**
  - Push flow control is via the endpoint's response latency and Pub/Sub's own backoff — you have much less control, so a slow endpoint causes retries and duplicates.
  - StreamingPull (the default in the client libraries) gives the lowest latency and built-in flow control (`max outstanding messages/bytes`) — name it, because it is the practical default in production.

**`OP-3` Ordering**
- **L4**
  - Set an **ordering key** on publish and enable message ordering on the subscription; messages with the same key are delivered in order to the same subscriber, provided they are published to the same region.
- **L5**
  - Cost: ordering serializes per key and a failed ack blocks that key's stream until resolved — the same head-of-line tradeoff as FIFO SQS and Kafka partitions.
  - Publisher-side ordering also disables some batching optimizations and requires the publisher to handle `resumePublish` after an error for that key.
  - Default (no ordering key) gives best-effort ordering only — never rely on it.

**`OP-4` Exactly-once delivery**
- **L4**
  - A subscription setting: within the ack deadline, Pub/Sub guarantees a successfully acked message is not redelivered, and redelivery of an outstanding message is prevented while the lease is valid.
- **L5**
  - Same honest caveat as everywhere: it is exactly-once *delivery to the subscriber within the service*, not exactly-once *side effects*. If your handler writes to a database and crashes after the write but before the ack, you still reprocess. Idempotency remains required.
  - It reduces throughput and adds latency, so enable it where duplicates are expensive, not by default.

**`OP-5` Seek, snapshots, dead-letter topics**
- **L4**
  - **Seek** rewinds (or fast-forwards) a subscription to a timestamp or snapshot, replaying retained messages. **Snapshots** capture a subscription's ack state for later restore. **Dead-letter topics** capture messages exceeding max delivery attempts.
- **L5**
  - Seek-to-timestamp is the "oh no, we deployed a bug" button — it is the operational feature Kafka gives via offset reset and SQS does not give at all. Worth naming as a differentiator in a design round.
  - Snapshot before a risky deploy, then seek back on failure — a genuinely good pattern.
  - DLT requires granting Pub/Sub publish rights on the dead-letter topic and subscribe rights on the source; a missing IAM binding silently disables dead-lettering.

### 3.2 RabbitMQ

**`OR-1` AMQP model**
- **L4**
  - Publishers send to an **exchange**, which routes to **queues** via **bindings** and a routing key. Exchange types: direct (exact key), topic (wildcard patterns), fanout (all bound queues), headers.
- **L5**
  - The routing intelligence lives in the **broker**, which is the philosophical opposite of Kafka (dumb broker, smart clients). That buys expressive routing and per-message flexibility, and costs you throughput and replayability.
  - Queues are the unit of storage and consumption; a message routed to three queues is stored three times.

**`OR-2` vs Kafka consumption model**
- **L4**
  - Rabbit pushes messages to consumers and removes them on ack — a work queue, not a log. No replay, no offsets, no consumer groups. Competing consumers on one queue is the standard scaling pattern.
- **L5**
  - Rabbit gives per-message ack/nack/requeue, priorities, TTLs, and per-message routing — capabilities Kafka simply does not have. Kafka gives retention, replay, ordered partitions and much higher throughput.
  - Rule of thumb: **task distribution with complex routing → Rabbit; event streaming with replay → Kafka.** Streams in RabbitMQ 3.9+ add a Kafka-like append-only log, worth naming for currency.

**`OR-3` Publisher confirms, acks, prefetch**
- **L4**
  - **Publisher confirms** are the broker's ack that a message was accepted (the durability handshake — without them, publishes are fire-and-forget). **Consumer acks** (`basic.ack`/`nack`/`reject`) control redelivery. **Prefetch** (`basic.qos`) bounds unacked messages per consumer.
- **L5**
  - Prefetch is the backpressure and fairness knob: too high and one consumer hoards the queue while others idle (and memory grows); too low and you add a round trip per message. Typical starting point: a small multiple of concurrency.
  - Durability requires all three: durable exchange + durable queue + persistent messages + publisher confirms. Missing any one silently loses messages on broker restart — a very common interview trap.
  - `nack` with `requeue=true` can create an infinite hot loop; pair with a retry count header and a dead-letter exchange.

**`OR-4` Delayed retry**
- **L4**
  - Use a **dead-letter exchange** plus a queue with a message TTL: the message expires from the "wait" queue and is dead-lettered back to the work exchange after the delay. Or use the delayed-message exchange plugin.
- **L5**
  - The TTL+DLX trick has a gotcha: TTL expiry is evaluated at the **head** of the queue, so a long-TTL message at the head blocks shorter-TTL messages behind it. Use one wait queue **per delay tier**, not per-message TTL on a shared queue.
  - Carry an attempt counter in headers and dead-letter to a terminal DLQ after N attempts, exactly as in Kafka/SQS.

**`OR-5` When Rabbit over Kafka**
- **L4**
  - Complex routing, per-message priority or TTL, request/reply (RPC over messaging), moderate throughput, a task-queue workload, or an existing AMQP ecosystem.
- **L5**
  - Also when you need consumers to scale beyond a fixed partition count with per-message isolation, and you do not need replay or long retention.
  - Be honest about the operational shape: clustering and mirrored/quorum queues are more subtle to run correctly than people expect, and a queue that grows unboundedly can take down a node — Rabbit is not a buffer for infinite backlogs the way Kafka is.

### 3.3 Kinesis Data Streams

**`OK-1` Model mapped to Kafka**
- **L4**
  - Stream ≈ topic, **shard** ≈ partition, **partition key** hashes to a shard, **sequence number** ≈ offset, and consumers checkpoint their position. Retention 24 h (default) up to 365 days.
  - Capacity: provisioned mode (1 MB/s or 1,000 records/s in, 2 MB/s out per shard) or on-demand.
- **L5**
  - The per-shard read quota is the key constraint: shared throughput means multiple consumers of the same shard split the 2 MB/s and are limited to 5 `GetRecords`/s — which is exactly what enhanced fan-out fixes.
  - Resharding (split/merge) is the analogue of changing partition count, with the same key-mapping consequences, but AWS supports both directions.

**`OK-2` Enhanced fan-out**
- **L4**
  - Each registered consumer gets its own dedicated 2 MB/s per shard, pushed over HTTP/2, instead of sharing the standard read throughput — lower latency (~70 ms) and no contention between consumers.
- **L5**
  - Cost: priced per consumer-shard-hour plus data retrieved, so it is expensive at high shard counts. Use it when you have several independent consumers or a strict latency SLO; stay with shared throughput for one or two consumers.

**`OK-3` KCL checkpointing**
- **L4**
  - The Kinesis Client Library assigns shards to workers (leases), tracks progress, and stores lease ownership and checkpoints in a **DynamoDB table** it creates per application.
- **L5**
  - That table is a real operational surface: it needs adequate capacity, it is a cost line item, and lease contention or throttling there shows up as stalled or thrashing consumers — a classic "the stream is fine but nothing is processing" incident.
  - Checkpoint after the durable side effect, exactly as with Kafka offsets — and expect at-least-once with duplicates on lease handoff.

**`OK-4` Kinesis vs Kafka vs SQS**
- **L4**
  - Kinesis when you want Kafka-like ordered, replayable streaming without operating a cluster, and you are already all-in on AWS with moderate throughput.
  - Kafka when you need higher throughput, richer ecosystem (Connect, Streams, registry), longer retention economics, or portability.
  - SQS when you need a work queue and none of the log semantics.
- **L5**
  - Kinesis's real advantages are managed simplicity and tight AWS integration (Firehose to S3/Redshift, Lambda triggers, KDA/Flink). Its disadvantages are per-shard quotas, resharding friction, weaker tooling, and cost at scale.
  - MSK versus Kinesis is often the actual decision on AWS: MSK if you want the Kafka API and ecosystem, Kinesis if you want fewer moving parts and native integrations.

### 3.4 Selection

**`OC-1` Decision framework**
- **L4**
  - Ask in order: (1) Does the caller need a synchronous answer? → HTTP/gRPC. (2) One consumer doing work, or many consumers reacting to an event? → queue vs pub/sub. (3) Is ordering required, and at what scope? (4) Is replay/audit required? (5) What throughput and latency? (6) What ops capacity do you have?
- **L5**
  - Add the non-technical axes that actually decide it: existing platform investment, team on-call capability, compliance/data residency, and cost curve at projected volume.
  - Present it as a recommendation with a named tradeoff, not a matrix. e.g. "SNS→SQS fanout: we get per-consumer retry and DLQ for free, we give up replay, and we accept that adding a consumer that needs history requires an archive — which we will build in S3 from day one."

**`OC-2` Queue vs log vs stream processor**
- **L4**
  - **Queue** (SQS, Rabbit): per-message state, destructive read, work distribution. **Log** (Kafka, Kinesis, Pub/Sub-ish): retained ordered records, non-destructive reads, multiple independent consumers, replay. **Stream processor** (Kafka Streams, Flink): stateful computation over a log — joins, windows, aggregations, with its own state stores and checkpointing.
- **L5**
  - The log is a *shared source of truth*, the queue is a *unit of work transfer*. That framing drives everything: replay, fanout, ordering, retention, and who owns the schema.
  - Stream processors add exactly-once state via changelog topics and checkpointing; the operational cost is state store size, rebalance/restore time, and reprocessing strategy. Do not bolt a stream processor onto a design unless windows/joins are genuinely required.

---

## System 4 — Cross-cutting patterns

**`PT-1` Transactional outbox**
- **L4**
  - Insert the event into an `outbox` table in the same DB transaction as the state change; a relay publishes it and marks it sent. Solves the dual-write problem.
- **L5**
  - Polling relay vs CDC (Debezium): polling is simpler and self-contained but adds latency and DB load and needs `FOR UPDATE SKIP LOCKED` for multiple instances; CDC is lower-latency and zero-polling but adds Kafka Connect, replication slots, and WAL retention concerns to your ops surface.
  - Still at-least-once — consumers must be idempotent. Ordering per aggregate via key + sequence column. Purge or partition the table or it becomes an outage.
  - Failure modes to name: relay lag (add an outbox-age metric and alert), slot bloat with CDC if the connector stalls, and schema drift between the DB row and the published event (use a mapper with a contract test).

**`PT-2` Inbox / idempotent receiver**
- **L4**
  - Persist processed message ids and skip repeats; ideally in the same transaction as the effect.
- **L5**
  - Key on `(message_id, consumer)`; add a TTL or time-partition and drop old partitions. Watch for hot-key contention.
  - Prefer it only when the effect cannot be made naturally idempotent — otherwise it is a per-message write you do not need.

**`PT-3` Business-level idempotency**
- **L4**
  - Natural keys with unique constraints, conditional updates (`WHERE version < :v`), state machines that make repeat transitions no-ops, and upserts.
- **L5**
  - The hierarchy, best first: (1) naturally idempotent effect, (2) conditional/compare-and-set write, (3) unique constraint + `ON CONFLICT DO NOTHING`, (4) explicit dedup table, (5) distributed lock (last resort — it is a liveness risk).
  - Must be **concurrency-safe**, not just replay-safe, because duplicate delivery can be simultaneous (see `SL-2`).
  - Non-idempotent external calls need intent-recording plus reconciliation (`KD-7`).

**`PT-4` Claim check**
- **L4**
  - Store the large payload in S3/GCS; publish a message containing the pointer plus enough metadata to route and filter.
- **L5**
  - Design the lifecycle: object retention ≥ topic/queue retention + replay window; handle "pointer valid, object missing" as a first-class error; and put access control on the object, not just the topic.
  - Bonus: it also enables **crypto-shredding** for GDPR — encrypt per subject and delete the key rather than the events.

**`PT-5` Saga**
- **L4**
  - A sequence of local transactions across services, each with a **compensating action**, coordinated either by **choreography** (each service reacts to events) or **orchestration** (a central coordinator drives steps).
- **L5**
  - Choreography: no central component, but the workflow is implicit and hard to observe or change — fine for 2–3 steps, painful beyond.
  - Orchestration (Step Functions, Temporal, a saga service): explicit state, easier timeouts/retries/observability, at the cost of a coordinator to own. Default to orchestration past three steps.
  - Compensations are not rollbacks — they are new business facts (`PaymentRefunded`, not "un-charge"), and some steps cannot be compensated (an email sent), which must be sequenced last or made reversible by design.
  - Every saga needs timeouts, idempotent steps, and a stuck-saga alert.

**`PT-6` Competing consumers vs partitioned consumers**
- **L4**
  - Competing consumers (SQS/Rabbit): any consumer takes any message, scale freely, no ordering. Partitioned consumers (Kafka/Kinesis): each partition has one owner, ordering per key, parallelism capped by partition count.
- **L5**
  - Choose by whether ordering is required. If it is not, competing consumers are operationally simpler in every way — no rebalance, no ceiling, per-message isolation.
  - Hybrid: partitioned transport plus in-consumer keyed worker pool to keep ordering per key while exceeding one-thread-per-partition throughput (`KC-6`).

**`PT-7` Retry taxonomy**
- **L4**
  - Classify errors as transient (timeouts, 429, 5xx, connection resets → retry with exponential backoff + jitter) or permanent (validation, deserialization, 4xx → straight to DLQ). Cap attempts.
- **L5**
  - Add a **retry budget** (e.g. retries ≤10% of requests) so a downstream outage does not amplify load — retries are the classic cause of metastable failure and cascading collapse.
  - Jitter is mandatory; without it, retries synchronize and re-kill a recovering service.
  - Distinguish **in-process retry** (fast, transient), **delayed retry via queue/topic** (outage-scale), and **DLQ + manual replay** (bugs). Three different tools, three different failure classes.

**`PT-8` Circuit breaker and bulkhead**
- **L4**
  - Circuit breaker opens after a failure threshold and fails fast, then half-opens to probe recovery. Bulkhead isolates resources (separate thread/connection pools) so one slow dependency cannot exhaust everything.
- **L5**
  - In a consumer, the breaker should **pause the listener** rather than fail messages into the DLQ — otherwise a downstream outage turns into thousands of DLQ entries that all need manual replay. This is the point most candidates miss.
  - Bulkhead by dependency and by tenant; a whale tenant should not be able to starve everyone else's messages.

**`PT-9` Schema registry and compatibility**
- **L4**
  - A central store of versioned schemas (Avro/Protobuf/JSON Schema) enforcing a compatibility rule on registration; producers serialize with a schema id, consumers resolve it.
- **L5**
  - Use `BACKWARD_TRANSITIVE` or `FULL_TRANSITIVE` for long-lived topics; the non-transitive modes only check the immediately previous version and let you drift across several releases.
  - Enforce compatibility in **CI**, not only at runtime — catching it at deploy time is far cheaper than a consumer crash loop.
  - Registry availability becomes a hard dependency of producers and consumers; cache schemas locally and plan for registry downtime.

**`PT-10` Backpressure end-to-end**
- **L4**
  - Pull-based transports (Kafka, SQS, Pub/Sub pull) give natural backpressure — consume slower. Push-based (SNS push, Rabbit without prefetch) needs explicit flow control: prefetch limits, concurrency caps, rate limiters.
- **L5**
  - Backpressure must reach the **producer** or the queue just becomes an unbounded buffer that converts an outage into a much longer outage. Levers: producer quotas, `max.block.ms`, load shedding at the edge, and admission control.
  - Decide deliberately whether to buffer or shed: for user-facing latency-sensitive work, shedding with a clear error beats a 40-minute backlog. Say that explicitly — it is a senior judgment call.

**`PT-11` Poison quarantine and replay tooling**
- **L4**
  - Max-attempt policy that always terminates in a DLQ; preserve payload plus error metadata; a tool to inspect, filter, fix and replay.
- **L5**
  - Quarantine granularity matters: for ordered streams, DLQ-ing one record breaks that key's order, so you may need to park the whole key/group. State that tradeoff.
  - Replay tooling requirements: filter by error class and time range, rate-limited republish, replay marker header, dry-run mode, and an audit record of who replayed what.

**`PT-12` Observability contract for async**
- **L4**
  - Metrics: lag/backlog, age of oldest message, processing latency, error rate by class, DLQ rate, retry count distribution. Traces: propagate `traceparent` in headers. Logs: message id, key, attempt, correlation id.
- **L5**
  - The SLI that matters is **end-to-end event latency** (produced → effect durable), not per-service latency. Neither the producer's nor the consumer's own dashboards show it.
  - Consumer spans should **link** to producer spans, not be children of them.
  - Add a "silent failure" alert set: zero consumers on a live queue/topic, zero messages processed in N minutes on a queue that normally has traffic, and a subscription filter delivering nothing.

**`PT-13` Testing async systems**
- **L4**
  - Unit-test the handler directly. Integration-test with Testcontainers (Kafka, LocalStack for SQS/SNS) or embedded Kafka. Explicitly test duplicate delivery, out-of-order delivery, and poison messages.
- **L5**
  - Contract tests on the schema (producer and consumer both compile against the registry) catch more real bugs than end-to-end tests.
  - Test the failure paths deliberately: kill the consumer mid-batch and assert no loss and no double effect; force a DLQ and assert headers are complete; replay from the DLQ and assert idempotency holds.
  - In staging, run a **chaos drill**: pause the downstream, watch backlog and alerts fire, then recover and verify drain time matches the runbook's estimate.

**`PT-14` Migration: HTTP → async, or SQS → Kafka**
- **L4**
  - Strangler approach: dual-write (call the old path and publish the event), run the new consumer in shadow mode comparing results, then cut over per traffic slice, then remove the old path.
- **L5**
  - Sequence: (1) publish events alongside the existing synchronous path (outbox), (2) build the consumer writing to a shadow table, (3) reconcile continuously and alert on divergence, (4) flip reads, (5) remove the sync path.
  - Have an explicit rollback: keep the old path deployable, keep dual-write until the reconciliation error rate is at zero for a defined window.
  - For SQS → Kafka specifically, the hard part is not the transport, it is that you now inherit ordering, partition sizing, rebalance behavior and replay semantics you did not have before. Call out that the migration cost is mostly in the consumer's failure handling, not the client swap.

---

# PART 3 — CODE

Reference implementations in Java 17 / Spring Boot 3 / Spring Kafka / Spring Cloud AWS. These are the snippets worth being able to write on a whiteboard or in CoderPad.

## 3.1 Producer configuration (durable + ordered + idempotent)

```java
@Configuration
public class KafkaProducerConfig {

    @Bean
    public ProducerFactory<String, byte[]> producerFactory(KafkaProperties props) {
        Map<String, Object> cfg = new HashMap<>(props.buildProducerProperties());

        // durability
        cfg.put(ProducerConfig.ACKS_CONFIG, "all");                    // + min.insync.replicas=2 on the topic
        cfg.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);       // PID + per-partition sequence
        cfg.put(ProducerConfig.MAX_IN_FLIGHT_REQUESTS_PER_CONNECTION, 5); // safe & ordered WITH idempotence

        // latency / throughput
        cfg.put(ProducerConfig.LINGER_MS_CONFIG, 10);
        cfg.put(ProducerConfig.BATCH_SIZE_CONFIG, 128 * 1024);
        cfg.put(ProducerConfig.COMPRESSION_TYPE_CONFIG, "zstd");

        // timeouts: total budget must fit inside the upstream request SLA
        cfg.put(ProducerConfig.DELIVERY_TIMEOUT_MS_CONFIG, 30_000);
        cfg.put(ProducerConfig.REQUEST_TIMEOUT_MS_CONFIG, 10_000);
        cfg.put(ProducerConfig.MAX_BLOCK_MS_CONFIG, 2_000);            // fail fast instead of blocking 60s

        return new DefaultKafkaProducerFactory<>(cfg);
    }
}
```

Sending with a key (ordering scope) and headers (context), never blocking in the callback:

```java
public void publish(OrderEvent event) {
    ProducerRecord<String, byte[]> record = new ProducerRecord<>(
            "orders.v1",
            event.getOrderId(),                       // partition key == ordering scope
            serializer.serialize(event));

    record.headers()
          .add("messageId", event.getEventId().getBytes(UTF_8))
          .add("schemaVersion", "1".getBytes(UTF_8))
          .add("traceparent", currentTraceParent().getBytes(UTF_8));

    kafkaTemplate.send(record).whenComplete((result, ex) -> {
        if (ex == null) {
            meter.counter("kafka.publish.success").increment();
            return;
        }
        // classify: retriable exceptions were already retried by the client
        if (ex instanceof RetriableException) {
            meter.counter("kafka.publish.retriable_exhausted").increment();
        } else {
            meter.counter("kafka.publish.fatal").increment();
        }
        // hand off; do NOT do blocking work here (this runs on the sender thread)
        failureHandoff.submit(() -> deadLetterStore.save(record, ex));
    });
}
```

## 3.2 Consumer: manual ack, error classification, DLT

```java
@Configuration
public class KafkaConsumerConfig {

    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, byte[]> factory(
            ConsumerFactory<String, byte[]> cf, KafkaTemplate<String, byte[]> template) {

        var factory = new ConcurrentKafkaListenerContainerFactory<String, byte[]>();
        factory.setConsumerFactory(cf);
        factory.setConcurrency(3);                                   // <= partition count
        factory.getContainerProperties().setAckMode(AckMode.MANUAL_IMMEDIATE);

        // publish to <topic>-dlt with original topic/partition/offset/exception headers
        var recoverer = new DeadLetterPublishingRecoverer(template,
                (record, ex) -> new TopicPartition(record.topic() + "-dlt", -1));

        // 3 fast retries, 500ms apart, then DLT
        var errorHandler = new DefaultErrorHandler(recoverer, new FixedBackOff(500L, 3L));
        // permanent errors: no retry at all
        errorHandler.addNotRetryableExceptions(
                ValidationException.class, DeserializationException.class, JsonProcessingException.class);
        factory.setCommonErrorHandler(errorHandler);
        return factory;
    }
}

@Component
class OrderListener {

    @KafkaListener(topics = "orders.v1", groupId = "billing-service")
    public void onMessage(ConsumerRecord<String, byte[]> record, Acknowledgment ack) {
        String messageId = header(record, "messageId");
        try {
            service.handle(deserialize(record.value()), messageId);  // idempotent, see 3.3
            ack.acknowledge();                                       // commit AFTER the durable effect
        } catch (RuntimeException ex) {
            // do NOT ack; DefaultErrorHandler decides retry vs DLT
            throw ex;
        }
    }
}
```

Consumer properties worth setting explicitly:

```yaml
spring:
  kafka:
    consumer:
      enable-auto-commit: false
      auto-offset-reset: earliest        # or 'none' for financial pipelines
      isolation-level: read_committed    # only if producers use transactions
      max-poll-records: 100              # max-poll-records x p99 handler latency < max.poll.interval.ms
      properties:
        partition.assignment.strategy: org.apache.kafka.clients.consumer.CooperativeStickyAssignor
        max.poll.interval.ms: 300000
        session.timeout.ms: 45000
        heartbeat.interval.ms: 15000
        spring.deserializer.value.delegate.class: org.apache.kafka.common.serialization.ByteArrayDeserializer
```

## 3.3 Idempotent handler (single transaction: effect + dedup)

```java
@Service
class PaymentService {

    @Transactional
    public void handle(OrderEvent event, String messageId) {
        // (1) dedup and effect in ONE transaction — never check-then-write in two steps
        int inserted = inbox.insertIfAbsent(messageId, "billing-service");
        if (inserted == 0) {
            meter.counter("consumer.duplicate").increment();
            return;                                  // already processed
        }
        // (2) effect is ALSO conditional, so it is safe even if the inbox row is lost
        payments.upsertIfNewer(event.getOrderId(), event.getVersion(), event.getAmount());
    }
}
```

```sql
-- inbox: dedup keyed by message + consumer, time-partitioned for cheap cleanup
CREATE TABLE inbox (
    message_id     TEXT        NOT NULL,
    consumer       TEXT        NOT NULL,
    processed_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (message_id, consumer)
) PARTITION BY RANGE (processed_at);

-- insertIfAbsent
INSERT INTO inbox (message_id, consumer) VALUES (:id, :consumer)
ON CONFLICT DO NOTHING;

-- upsertIfNewer: conditional update makes the effect itself idempotent AND concurrency-safe
INSERT INTO payments (order_id, version, amount)
VALUES (:orderId, :version, :amount)
ON CONFLICT (order_id) DO UPDATE
SET version = EXCLUDED.version,
    amount  = EXCLUDED.amount
WHERE payments.version < EXCLUDED.version;
```

## 3.4 Transactional outbox + polling relay

```java
@Transactional
public Order placeOrder(PlaceOrderCommand cmd) {
    Order order = orders.save(Order.from(cmd));                    // state change
    outbox.save(new OutboxRecord(                                  // event, SAME transaction
            UUID.randomUUID(),
            "Order", order.getId(),                                // aggregate type + id (Kafka key)
            "OrderPlaced",
            json.write(OrderPlacedEvent.from(order))));
    return order;                                                  // no Kafka call here at all
}
```

```java
@Scheduled(fixedDelay = 500)
@Transactional
public void relay() {
    List<OutboxRecord> batch = outbox.lockNextBatch(100);          // FOR UPDATE SKIP LOCKED
    for (OutboxRecord r : batch) {
        var record = new ProducerRecord<>("orders.v1", r.getAggregateId(), r.getPayload());
        record.headers().add("messageId", r.getId().toString().getBytes(UTF_8));
        kafkaTemplate.send(record).join();                          // at-least-once: may publish twice
        outbox.markSent(r.getId());
    }
}
```

```sql
-- relay claim query: SKIP LOCKED lets multiple relay instances run safely
SELECT * FROM outbox
WHERE sent_at IS NULL
ORDER BY seq                    -- per-aggregate ordering preserved by monotonic seq
LIMIT :n
FOR UPDATE SKIP LOCKED;

-- alert on this: outbox lag
SELECT EXTRACT(EPOCH FROM now() - MIN(created_at)) AS oldest_unsent_seconds
FROM outbox WHERE sent_at IS NULL;
```

## 3.5 Non-blocking retry topics + DLT (Spring)

```java
@RetryableTopic(
        attempts = "4",
        backoff = @Backoff(delay = 5_000, multiplier = 4.0),   // 5s -> 20s -> 80s
        autoCreateTopics = "false",
        topicSuffixingStrategy = TopicSuffixingStrategy.SUFFIX_WITH_INDEX_VALUE,
        exclude = {ValidationException.class, DeserializationException.class}, // straight to DLT
        dltStrategy = DltStrategy.FAIL_ON_ERROR)
@KafkaListener(topics = "orders.v1", groupId = "billing-service")
public void listen(OrderEvent event) {
    service.handle(event);
}

@DltHandler
public void dlt(ConsumerRecord<String, byte[]> record,
                @Header(KafkaHeaders.EXCEPTION_FQCN) String exceptionClass) {
    log.error("DLT: topic={} partition={} offset={} cause={}",
            record.topic(), record.partition(), record.offset(), exceptionClass);
    meter.counter("dlt.messages", "exception", exceptionClass).increment();
}
```

> Trade-off to state aloud: retry topics keep the main partition flowing, but a retried record is now **out of order** relative to its key.

## 3.6 Kafka transactions (read-process-write, Kafka → Kafka only)

```java
@Bean
public KafkaTransactionManager<String, byte[]> ktm(ProducerFactory<String, byte[]> pf) {
    ((DefaultKafkaProducerFactory<String, byte[]>) pf)
            .setTransactionIdPrefix("billing-tx-");   // STABLE per instance -> zombie fencing works
    return new KafkaTransactionManager<>(pf);
}

@Transactional("ktm")
@KafkaListener(topics = "orders.v1", groupId = "billing-service")
public void process(OrderEvent event) {
    kafkaTemplate.send("invoices.v1", event.getOrderId(), toInvoice(event));
    // offsets for orders.v1 are committed inside the same transaction
}
```
Consumers of `invoices.v1` must set `isolation.level=read_committed`, or the guarantee is worth nothing.

## 3.7 Backpressure: pause/resume with a bounded worker pool

```java
// Use when processing is slow and you must exceed one-thread-per-partition,
// while keeping per-key ordering.
private final Map<Integer, Semaphore> permits = new ConcurrentHashMap<>();

public void pollLoop(KafkaConsumer<String, byte[]> consumer) {
    while (running) {
        ConsumerRecords<String, byte[]> records = consumer.poll(Duration.ofMillis(500));
        for (ConsumerRecord<String, byte[]> r : records) {
            // route by key hash so one key always lands on the same worker -> order preserved
            workers[Math.abs(r.key().hashCode()) % workers.length].submit(() -> handle(r));
        }
        if (queueDepth() > HIGH_WATERMARK) {
            consumer.pause(consumer.assignment());     // stop fetching...
        } else if (consumer.paused().size() > 0 && queueDepth() < LOW_WATERMARK) {
            consumer.resume(consumer.paused());
        }
        // keep calling poll() even while paused, or max.poll.interval.ms evicts us
        commitCompletedOffsets(consumer);              // only up to the lowest incomplete offset
    }
}
```

## 3.8 SQS consumer: visibility heartbeat, batch delete with partial failures

```java
@Component
class SqsWorker {

    @SqsListener(value = "orders-queue", maxConcurrentMessages = "10")
    public void onMessage(Message<OrderEvent> message,
                          @Header("ApproximateReceiveCount") String receiveCount,
                          Acknowledgement ack,
                          Visibility visibility) {

        if (Integer.parseInt(receiveCount) > 1) {
            meter.counter("sqs.redelivery").increment();   // visibility timeout may be too short
        }

        // extend the lease while working (lease renewal, not a long static timeout)
        ScheduledFuture<?> hb = scheduler.scheduleAtFixedRate(
                () -> visibility.changeToAsync(60), 30, 30, SECONDS);
        try {
            service.handle(message.getPayload(), messageId(message));  // idempotent
            ack.acknowledge();                                          // == DeleteMessage
        } finally {
            hb.cancel(true);                                            // MUST stop on completion
        }
    }
}
```

Raw SDK batch delete — the partial-failure handling most code gets wrong:

```java
DeleteMessageBatchResponse resp = sqs.deleteMessageBatch(b -> b.queueUrl(url).entries(entries));
if (!resp.failed().isEmpty()) {
    // these messages will be REDELIVERED. Log, count, and retry the failed subset.
    resp.failed().forEach(f ->
        log.warn("delete failed id={} senderFault={} code={}", f.id(), f.senderFault(), f.code()));
    meter.counter("sqs.delete.partial_failure").increment(resp.failed().size());
}
```

Exponential backoff without native support (`ChangeMessageVisibility` keyed on receive count):

```java
int attempt = Integer.parseInt(receiveCount);
int backoff = (int) Math.min(900, Math.pow(2, attempt) * 5 + ThreadLocalRandom.current().nextInt(5));
sqs.changeMessageVisibility(r -> r.queueUrl(url).receiptHandle(handle).visibilityTimeout(backoff));
```

Lambda partial batch failure (the single most important SQS+Lambda setting):

```java
public SQSBatchResponse handleRequest(SQSEvent event, Context ctx) {
    List<SQSBatchResponse.BatchItemFailure> failures = new ArrayList<>();
    for (SQSEvent.SQSMessage msg : event.getRecords()) {
        try {
            service.handle(msg);
        } catch (Exception e) {
            failures.add(new SQSBatchResponse.BatchItemFailure(msg.getMessageId()));
        }
    }
    return new SQSBatchResponse(failures);   // requires ReportBatchItemFailures on the event source
}
```

## 3.9 Terraform: queue + DLQ + alarms + SNS fanout with filtering

```hcl
resource "aws_sqs_queue" "orders_dlq" {
  name                      = "orders-dlq"
  message_retention_seconds = 1209600            # 14 days: longer than the source, always
  sqs_managed_sse_enabled   = true
}

resource "aws_sqs_queue" "orders" {
  name                       = "orders-queue"
  visibility_timeout_seconds = 180               # ~3x p99 processing time
  message_retention_seconds  = 345600            # 4 days
  receive_wait_time_seconds  = 20                # long polling ON at the queue level
  sqs_managed_sse_enabled    = true

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.orders_dlq.arn
    maxReceiveCount     = 5                      # 5 x 180s = 900s << 4 day retention
  })
}

# the alarm that actually maps to user experience
resource "aws_cloudwatch_metric_alarm" "orders_age" {
  alarm_name          = "orders-queue-age-of-oldest"
  namespace           = "AWS/SQS"
  metric_name         = "ApproximateAgeOfOldestMessage"
  dimensions          = { QueueName = aws_sqs_queue.orders.name }
  statistic           = "Maximum"
  period              = 60
  evaluation_periods  = 3
  threshold           = 300                      # SLO: nothing older than 5 minutes
  comparison_operator = "GreaterThanThreshold"
}

resource "aws_cloudwatch_metric_alarm" "orders_dlq" {
  alarm_name          = "orders-dlq-not-empty"
  namespace           = "AWS/SQS"
  metric_name         = "ApproximateNumberOfMessagesVisible"
  dimensions          = { QueueName = aws_sqs_queue.orders_dlq.name }
  statistic           = "Maximum"
  period              = 300
  evaluation_periods  = 1
  threshold           = 0
  comparison_operator = "GreaterThanThreshold"
  alarm_description   = "Runbook: <link>. Owner: billing-team."
}

# SNS -> SQS fanout: raw delivery + filter policy + subscription DLQ
resource "aws_sns_topic_subscription" "orders_to_billing" {
  topic_arn            = aws_sns_topic.orders.arn
  protocol             = "sqs"
  endpoint             = aws_sqs_queue.orders.arn
  raw_message_delivery = true

  filter_policy = jsonencode({
    eventType = ["OrderPlaced", "OrderCancelled"]
    amount    = [{ numeric = [">=", 100] }]
  })

  redrive_policy = jsonencode({           # subscription DLQ: without this, drops are silent
    deadLetterTargetArn = aws_sqs_queue.sns_dlq.arn
  })
}
```

## 3.10 Tests worth writing (Testcontainers)

```java
@Testcontainers
class OrderConsumerIT {

    @Container static KafkaContainer kafka =
            new KafkaContainer(DockerImageName.parse("confluentinc/cp-kafka:7.6.0"));

    @Test
    void duplicateDeliveryProducesOneEffect() {
        producer.send(record("msg-1", orderPlaced("o-1", 1)));
        producer.send(record("msg-1", orderPlaced("o-1", 1)));   // exact duplicate
        await().untilAsserted(() ->
            assertThat(payments.countByOrderId("o-1")).isEqualTo(1));
    }

    @Test
    void staleVersionIsIgnored() {
        consume(orderPlaced("o-2", 5));
        consume(orderPlaced("o-2", 3));                          // out of order, older version
        assertThat(payments.findVersion("o-2")).isEqualTo(5);
    }

    @Test
    void poisonMessageGoesToDltAndPartitionKeepsFlowing() {
        producer.send(record("bad", malformedBytes()));
        producer.send(record("good", orderPlaced("o-3", 1)));
        await().untilAsserted(() -> {
            assertThat(dltRecords()).hasSize(1);
            assertThat(payments.countByOrderId("o-3")).isEqualTo(1);   // not blocked
        });
    }
}
```
For SQS/SNS use **LocalStack** (`LocalStackContainer` with `SQS, SNS`) and assert the same three properties: duplicate safety, DLQ routing after `maxReceiveCount`, and redrive idempotency.

---

## Final checklist — say these unprompted and you sound senior

- "At-least-once + idempotent processing = effectively-once. Exactly-once only holds inside Kafka."
- "`acks=all` is meaningless without `min.insync.replicas >= 2`."
- "Ordering is per partition, per key, and only if a single thread processes that partition."
- "Every retry policy must terminate in a DLQ — nothing can block forever."
- "I alert on age-of-oldest-message / lag-in-seconds, not on queue depth."
- "Changing partition count breaks key→partition mapping; it's a migration, not a config change."
- "The queue removes backpressure, so the consumer is the only thing protecting the database."
- "Every DLQ needs an owner, a runbook, and a rate-limited replay tool."

---

## References

1. **`apache/kafka`** — `clients/src/main/java/org/apache/kafka/clients/producer/internals/` (`RecordAccumulator`, `Sender`) and `consumer/internals/ConsumerCoordinator.java`. Reading the coordinator is the fastest way to actually understand rebalance behavior. https://github.com/apache/kafka
2. **`spring-projects/spring-kafka`** — `DefaultErrorHandler`, `DeadLetterPublishingRecoverer`, `RetryTopicConfigurer`. Real, runnable reference for everything in §3.2–3.5. https://github.com/spring-projects/spring-kafka
3. **`debezium/debezium-examples`** — `outbox` module: the canonical transactional-outbox + CDC implementation. https://github.com/debezium/debezium-examples/tree/main/outbox
4. **Kafka documentation — Design & Configuration** (delivery semantics, replication, all producer/consumer configs in one place). https://kafka.apache.org/documentation/
5. **AWS SQS Developer Guide** — visibility timeout, DLQ/redrive, FIFO throughput, and the current service quotas page. https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/
6. **Confluent — "Transactions in Apache Kafka"** and **"Exactly-Once Semantics Are Possible"**: the two posts that explain `transactional.id`, fencing, and LSO properly. https://www.confluent.io/blog/transactions-apache-kafka/
7. **Microservices.io patterns** — Outbox, Saga, Idempotent Receiver, CQRS, with tradeoffs stated per pattern. https://microservices.io/patterns/data/transactional-outbox.html
