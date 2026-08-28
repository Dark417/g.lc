# Apache Kafka — Implementation

> Implementation pair of [1.kafka.md](1.kafka.md); same section order. Rules: [.agents/rules.md](../../.agents/rules.md).
> Snippets are focused and compile in isolation; not a runnable project.
> Libraries named: Python → `confluent-kafka` (librdkafka binding; chosen over `kafka-python` for idempotence/transactions/perf). Java → `org.apache.kafka:kafka-clients`, Spring → `spring-kafka`.

## Index
- [0. Setup and admin](#0-setup-and-admin)
  - [0.1 Local cluster (KRaft)](#01-local-cluster-kraft)
  - [0.2 CLI ops cheat sheet](#02-cli-ops-cheat-sheet)
  - [0.3 AdminClient (create topics, alter config)](#03-adminclient-create-topics-alter-config)
- [1. Producer](#1-producer)
  - [1.1 Normal mode: durable, ordered, idempotent](#11-normal-mode-durable-ordered-idempotent)
  - [1.2 Keyed vs keyless, custom partitioner](#12-keyed-vs-keyless-custom-partitioner)
  - [1.3 Headers, serializers, Schema Registry](#13-headers-serializers-schema-registry)
  - [1.4 Producer config table](#14-producer-config-table)
- [2. Consumer and consumer groups](#2-consumer-and-consumer-groups)
  - [2.1 Poll loop with manual commit](#21-poll-loop-with-manual-commit)
  - [2.2 Pub/sub fan-out vs competing consumers](#22-pubsub-fan-out-vs-competing-consumers)
  - [2.3 Rebalance listener, static membership, cooperative](#23-rebalance-listener-static-membership-cooperative)
  - [2.4 Seek, replay, offset reset](#24-seek-replay-offset-reset)
  - [2.5 Parallel processing with pause/resume](#25-parallel-processing-with-pauseresume)
  - [2.6 Consumer config table](#26-consumer-config-table)
- [3. Delivery guarantees](#3-delivery-guarantees)
  - [3.1 Idempotent consumer (dedup table / upsert)](#31-idempotent-consumer-dedup-table--upsert)
  - [3.2 Offsets stored in the sink DB](#32-offsets-stored-in-the-sink-db)
  - [3.3 Transactions: read-process-write](#33-transactions-read-process-write)
  - [3.4 Transactional outbox](#34-transactional-outbox)
- [4. Retry, DLQ, error handling](#4-retry-dlq-error-handling)
  - [4.1 Blocking retry with backoff](#41-blocking-retry-with-backoff)
  - [4.2 Non-blocking retry topics + DLT](#42-non-blocking-retry-topics--dlt)
  - [4.3 Spring: error handlers and `@RetryableTopic`](#43-spring-error-handlers-and-retryabletopic)
- [5. Cache patterns](#5-cache-patterns)
  - [5.1 Compacted topic as a KV snapshot](#51-compacted-topic-as-a-kv-snapshot)
  - [5.2 Cache invalidation via CDC events](#52-cache-invalidation-via-cdc-events)
- [6. Streams: group, aggregate, join, merge](#6-streams-group-aggregate-join-merge)
  - [6.1 Kafka Streams (Java): filter, map, branch, merge](#61-kafka-streams-java-filter-map-branch-merge)
  - [6.2 groupBy, count, windowed aggregate](#62-groupby-count-windowed-aggregate)
  - [6.3 Joins: stream-table, stream-stream, GlobalKTable](#63-joins-stream-table-stream-stream-globalktable)
  - [6.4 Exactly-once, state stores, interactive queries](#64-exactly-once-state-stores-interactive-queries)
  - [6.5 Python streaming (Faust / plain consumer aggregate)](#65-python-streaming-faust--plain-consumer-aggregate)
  - [6.6 Streams config table](#66-streams-config-table)
- [7. Spring Boot wiring](#7-spring-boot-wiring)
- [8. Broker / topic config table](#8-broker--topic-config-table)
- [9. Observability and testing](#9-observability-and-testing)
- [References](#references)

---

## 0. Setup and admin

### 0.1 Local cluster (KRaft)
```yaml
# docker-compose.yml — single-node KRaft (Kafka 3.9 / 4.x image)
services:
  kafka:
    image: apache/kafka:3.9.0
    ports: ["9092:9092"]
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka:9093
      KAFKA_LISTENERS: PLAINTEXT://:9092,CONTROLLER://:9093
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
```
- deps
  - Python: `pip install confluent-kafka` (`confluent-kafka[avro,schemaregistry]` for registry)
  - Java: `org.apache.kafka:kafka-clients:3.9.x`, `org.apache.kafka:kafka-streams:3.9.x`
  - Spring Boot 3.x: `org.springframework.kafka:spring-kafka` (Spring Boot starter auto-configures)

### 0.2 CLI ops cheat sheet
```bash
# topics
kafka-topics.sh --bootstrap-server localhost:9092 --create --topic orders --partitions 6 --replication-factor 3 \
  --config min.insync.replicas=2 --config retention.ms=604800000
kafka-topics.sh --bootstrap-server localhost:9092 --describe --topic orders
kafka-topics.sh --bootstrap-server localhost:9092 --alter --topic orders --partitions 12     # grow only; breaks key mapping
kafka-configs.sh --bootstrap-server localhost:9092 --alter --entity-type topics --entity-name orders \
  --add-config cleanup.policy=compact,min.cleanable.dirty.ratio=0.1

# consumer groups / offsets
kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group billing            # lag per partition
kafka-consumer-groups.sh --bootstrap-server localhost:9092 --group billing --reset-offsets \
  --topic orders --to-datetime 2026-08-25T00:00:00.000 --execute                                  # group must be inactive
kafka-consumer-groups.sh --bootstrap-server localhost:9092 --group billing --reset-offsets --topic orders --shift-by -100 --execute

# produce / consume for debugging
kafka-console-producer.sh --bootstrap-server localhost:9092 --topic orders --property parse.key=true --property key.separator=:
kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic orders --from-beginning --property print.key=true --property print.headers=true

# cluster
kafka-leader-election.sh --bootstrap-server localhost:9092 --election-type PREFERRED --all-topic-partitions
kafka-reassign-partitions.sh --bootstrap-server localhost:9092 --reassignment-json-file plan.json --execute --throttle 50000000
kafka-metadata-quorum.sh --bootstrap-server localhost:9092 describe --status                    # KRaft quorum health
```

### 0.3 AdminClient (create topics, alter config)
```python
# Python
from confluent_kafka.admin import AdminClient, NewTopic, ConfigResource
admin = AdminClient({"bootstrap.servers": "localhost:9092"})
fs = admin.create_topics([NewTopic("orders", num_partitions=6, replication_factor=3,
                                   config={"min.insync.replicas": "2", "retention.ms": "604800000"})])
for topic, f in fs.items():
    f.result()  # raises on failure (e.g. TopicExistsException)
admin.alter_configs([ConfigResource(ConfigResource.Type.TOPIC, "orders", {"cleanup.policy": "compact"})])
```
```java
// Java
try (Admin admin = Admin.create(Map.of(AdminClientConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092"))) {
    NewTopic t = new NewTopic("orders", 6, (short) 3)
        .configs(Map.of("min.insync.replicas", "2", "retention.ms", "604800000"));
    admin.createTopics(List.of(t)).all().get();
    admin.incrementalAlterConfigs(Map.of(
        new ConfigResource(ConfigResource.Type.TOPIC, "orders"),
        List.of(new AlterConfigOp(new ConfigEntry("cleanup.policy", "compact"), AlterConfigOp.OpType.SET))
    )).all().get();
}
```
```java
// Spring Boot: topics declared as beans are created on startup (KafkaAdmin auto-configured)
@Bean NewTopic orders() { return TopicBuilder.name("orders").partitions(6).replicas(3)
        .config("min.insync.replicas", "2").build(); }
```

---

## 1. Producer

### 1.1 Normal mode: durable, ordered, idempotent
```python
# Python — confluent-kafka
from confluent_kafka import Producer
p = Producer({
    "bootstrap.servers": "localhost:9092",
    "acks": "all",
    "enable.idempotence": True,          # forces acks=all, retries>0, max.in.flight<=5
    "linger.ms": 10, "batch.size": 131072, "compression.type": "zstd",
    "delivery.timeout.ms": 120000,
})
def on_delivery(err, msg):
    if err is not None:                  # non-retriable or timed out → your responsibility (log/DLQ/alert)
        print(f"FAILED {msg.key()} {err}")
p.produce("orders", key="order-42", value=b'{"id":42}', on_delivery=on_delivery)
p.poll(0)                                # serves callbacks; call regularly in a loop
p.flush(10)                              # on shutdown: block until queue drained
```
```java
// Java — kafka-clients
Properties c = new Properties();
c.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
c.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
c.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
c.put(ProducerConfig.ACKS_CONFIG, "all");
c.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
c.put(ProducerConfig.LINGER_MS_CONFIG, 10);
c.put(ProducerConfig.BATCH_SIZE_CONFIG, 131072);
c.put(ProducerConfig.COMPRESSION_TYPE_CONFIG, "zstd");
c.put(ProducerConfig.DELIVERY_TIMEOUT_MS_CONFIG, 120000);
try (var producer = new KafkaProducer<String, String>(c)) {
    producer.send(new ProducerRecord<>("orders", "order-42", "{\"id\":42}"), (md, ex) -> {
        if (ex != null) log.error("send failed key=order-42", ex);   // handle: DLQ / alert / fail request
        else log.info("p={} o={}", md.partition(), md.offset());
    });
    // sync variant when the caller must know: producer.send(rec).get()
}   // close() flushes
```
```java
// Spring Boot — KafkaTemplate (application.yml in §7)
@Service @RequiredArgsConstructor
class OrderPublisher {
    private final KafkaTemplate<String, OrderEvent> kafka;
    CompletableFuture<SendResult<String, OrderEvent>> publish(OrderEvent e) {
        return kafka.send("orders", e.orderId(), e)
            .whenComplete((res, ex) -> { if (ex != null) log.error("publish failed {}", e.orderId(), ex); });
    }
}
```

### 1.2 Keyed vs keyless, custom partitioner
- keyed → `murmur2(key) % n` (Java); confluent-kafka default is `consistent_random` (crc32) → set `"partitioner": "murmur2_random"` when mixing with Java producers on the same topic
```python
p = Producer({..., "partitioner": "murmur2_random"})
p.produce("orders", key="tenant-7", value=b"...")                # key → same partition each time
p.produce("orders", value=b"...", partition=3)                  # explicit partition overrides partitioner
```
```java
// Custom partitioner: bucket indirection so partition count can grow later without breaking key affinity
public class BucketPartitioner implements Partitioner {
    static final int BUCKETS = 1024;
    public int partition(String topic, Object key, byte[] kb, Object v, byte[] vb, Cluster cluster) {
        int n = cluster.partitionCountForTopic(topic);
        int bucket = Math.abs(Utils.murmur2(kb)) % BUCKETS;
        return bucket * n / BUCKETS;                              // contiguous bucket ranges per partition
    }
    public void close() {} public void configure(Map<String, ?> cfg) {}
}
// c.put(ProducerConfig.PARTITIONER_CLASS_CONFIG, BucketPartitioner.class);
```

### 1.3 Headers, serializers, Schema Registry
```python
p.produce("orders", key="k", value=b"v", headers=[("trace-id", b"abc"), ("schema-ver", b"2")])
```
```python
# Avro + Schema Registry (confluent-kafka)
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer
from confluent_kafka.serialization import SerializationContext, MessageField
sr = SchemaRegistryClient({"url": "http://localhost:8081"})
ser = AvroSerializer(sr, open("order.avsc").read())          # registers under subject "orders-value" (TopicNameStrategy)
p.produce("orders", key="42", value=ser({"id": 42, "amount": 9.5}, SerializationContext("orders", MessageField.VALUE)))
```
```java
// Java JSON via Jackson (no registry)
public class JsonSerializer<T> implements Serializer<T> {
    private final ObjectMapper om = new ObjectMapper();
    public byte[] serialize(String topic, T data) { try { return om.writeValueAsBytes(data); }
        catch (JsonProcessingException e) { throw new SerializationException(e); } }
}
// Spring: spring.kafka.producer.value-serializer=org.springframework.kafka.support.serializer.JsonSerializer
// Confluent Avro: io.confluent.kafka.serializers.KafkaAvroSerializer + schema.registry.url
```

### 1.4 Producer config table
| Config | Default | What it trades | Change when |
| --- | --- | --- | --- |
| `acks` | `all` (3.0+) | latency ↔ durability | `1` for loss-tolerant telemetry |
| `enable.idempotence` | `true` | nothing material | never disable; needed for ordering with pipelining |
| `max.in.flight.requests.per.connection` | 5 | pipelining ↔ ordering (≤5 with idempotence) | leave |
| `retries` / `delivery.timeout.ms` | MAX / 120 s | how long a stuck partition can block | shorten for request-path producers (e.g. 30 s) |
| `linger.ms` / `batch.size` | 0 / 16 KiB | throughput ↔ p99 latency | 5–50 ms / 64–256 KiB for ingestion |
| `compression.type` | none | CPU ↔ bytes | `zstd` or `lz4` almost always |
| `buffer.memory` / `max.block.ms` | 32 MiB / 60 s | memory ↔ backpressure behaviour | raise buffer for bursty producers; lower block for request path |
| `max.request.size` | 1 MiB | big messages ↔ broker/consumer memory | prefer claim-check |
| `partitioner.class` | built-in sticky | balance ↔ affinity | bucket partitioner for growable keyed topics |
| `transactional.id` | none | enables tx + fencing ↔ coordinator RTT | Kafka→Kafka EOS pipelines |
| `request.timeout.ms` | 30 s | how long to wait for one broker | rarely |
| `client.id` | "" | metrics/quotas attribution | always set |

---

## 2. Consumer and consumer groups

### 2.1 Poll loop with manual commit
```python
from confluent_kafka import Consumer, KafkaError, KafkaException
c = Consumer({
    "bootstrap.servers": "localhost:9092",
    "group.id": "billing",
    "enable.auto.commit": False,
    "auto.offset.reset": "earliest",
    "max.poll.interval.ms": 300000,
    "session.timeout.ms": 45000,
    "partition.assignment.strategy": "cooperative-sticky",
    "isolation.level": "read_committed",
})
c.subscribe(["orders"])
try:
    while True:
        msgs = c.consume(num_messages=500, timeout=1.0)     # batch; poll() for single
        if not msgs: continue
        for m in msgs:
            if m.error():
                if m.error().code() == KafkaError._PARTITION_EOF: continue
                raise KafkaException(m.error())
            handle(m.key(), m.value(), m.headers())         # your idempotent handler (§3.1)
        c.commit(asynchronous=False)                         # after processing → at-least-once
except KeyboardInterrupt: pass
finally:
    c.close()                                                # leaves group cleanly → immediate rebalance, no session wait
```
```java
Properties c = new Properties();
c.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
c.put(ConsumerConfig.GROUP_ID_CONFIG, "billing");
c.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
c.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
c.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);
c.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
c.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG, 500);
c.put(ConsumerConfig.PARTITION_ASSIGNMENT_STRATEGY_CONFIG, CooperativeStickyAssignor.class.getName());
c.put(ConsumerConfig.ISOLATION_LEVEL_CONFIG, "read_committed");
try (var consumer = new KafkaConsumer<String, String>(c)) {
    consumer.subscribe(List.of("orders"));
    while (running) {
        ConsumerRecords<String, String> recs = consumer.poll(Duration.ofSeconds(1));
        for (ConsumerRecord<String, String> r : recs) handle(r);
        consumer.commitAsync((offs, ex) -> { if (ex != null) log.warn("commit failed", ex); });
    }
    consumer.commitSync();     // final sync commit on shutdown
}
// wakeup from another thread: consumer.wakeup() → poll throws WakeupException → exit loop
```
```java
// Spring Boot — listener; container commits after listener returns (AckMode.BATCH default) or MANUAL
@KafkaListener(topics = "orders", groupId = "billing", concurrency = "3")     // 3 threads ≤ partitions
void onOrder(ConsumerRecord<String, OrderEvent> r, Acknowledgment ack) {   // Acknowledgment only with MANUAL/MANUAL_IMMEDIATE
    handle(r.value());
    ack.acknowledge();
}
// batch listener: void onOrders(List<ConsumerRecord<String, OrderEvent>> recs, Acknowledgment ack)
```

### 2.2 Pub/sub fan-out vs competing consumers
```
topic orders (6 partitions)
  group "billing"   : c1 → p0,p1   c2 → p2,p3   c3 → p4,p5     ← competing consumers (work split)
  group "analytics" : a1 → p0..p5                              ← independent cursor (fan-out)
  group "search-idx": s1 → p0,p1,p2   s2 → p3,p4,p5
```
- fan-out = **different `group.id` per service**; competing = **same `group.id`, more instances**
```python
# manual assignment (no group protocol, no rebalance, no offset commit unless you do it) — e.g. one-off replay tool
from confluent_kafka import TopicPartition
c = Consumer({"bootstrap.servers": "localhost:9092", "group.id": "tool", "enable.auto.commit": False})
c.assign([TopicPartition("orders", 0, 0), TopicPartition("orders", 1, 0)])
```
```java
consumer.assign(List.of(new TopicPartition("orders", 0)));   // Java equivalent; subscribe() and assign() are exclusive
```

### 2.3 Rebalance listener, static membership, cooperative
```python
def on_assign(consumer, parts): print("assigned", parts)      # cooperative: incremental_assign is automatic in confluent-kafka ≥1.6
def on_revoke(consumer, parts):
    consumer.commit(asynchronous=False)                          # commit what you processed before losing partitions
c.subscribe(["orders"], on_assign=on_assign, on_revoke=on_revoke)
c = Consumer({..., "group.instance.id": f"billing-{pod_ordinal}"})   # static membership: restart < session.timeout → no rebalance
```
```java
consumer.subscribe(List.of("orders"), new ConsumerRebalanceListener() {
    public void onPartitionsRevoked(Collection<TopicPartition> parts) { consumer.commitSync(currentOffsets(parts)); }
    public void onPartitionsAssigned(Collection<TopicPartition> parts) { /* seek from external store if you own offsets */ }
});
c.put(ConsumerConfig.GROUP_INSTANCE_ID_CONFIG, "billing-" + System.getenv("POD_ORDINAL"));
// KIP-848 (3.7+): c.put(ConsumerConfig.GROUP_PROTOCOL_CONFIG, "consumer"); assignor becomes broker-side ("uniform"/"range")
```
```yaml
# Spring
spring.kafka.consumer.properties.partition.assignment.strategy: org.apache.kafka.clients.consumer.CooperativeStickyAssignor
spring.kafka.consumer.properties.group.instance.id: billing-${HOSTNAME}
```

### 2.4 Seek, replay, offset reset
```python
# replay from a timestamp
from confluent_kafka import TopicPartition, OFFSET_BEGINNING
ts_ms = 1756080000000
parts = [TopicPartition("orders", p, ts_ms) for p in range(6)]
for tp in c.offsets_for_times(parts): c.seek(tp)              # only after assignment (inside on_assign or after poll)
c.seek(TopicPartition("orders", 0, OFFSET_BEGINNING))
```
```java
Map<TopicPartition, Long> q = parts.stream().collect(toMap(tp -> tp, tp -> tsMs));
consumer.offsetsForTimes(q).forEach((tp, ot) -> consumer.seek(tp, ot == null ? consumer.endOffsets(List.of(tp)).get(tp) : ot.offset()));
consumer.seekToBeginning(parts); consumer.seekToEnd(parts);
// Spring: implement ConsumerSeekAware → onPartitionsAssigned(assignments, callback) { callback.seekToTimestamp(...) }
```
- CLI equivalent: `kafka-consumer-groups.sh --reset-offsets` (§0.2), group must be stopped

### 2.5 Parallel processing with pause/resume
```java
// Poll thread + bounded worker pool; commit only contiguous completed offsets per partition; preserve per-key order by sharding
ExecutorService pool = Executors.newFixedThreadPool(8);
Map<TopicPartition, OffsetTracker> trackers = new ConcurrentHashMap<>();  // tracks lowest uncompleted offset
Set<TopicPartition> paused = new HashSet<>();
while (running) {
    var recs = consumer.poll(Duration.ofMillis(200));
    for (var r : recs) {
        var tp = new TopicPartition(r.topic(), r.partition());
        trackers.computeIfAbsent(tp, k -> new OffsetTracker()).inFlight(r.offset());
        int shard = Math.floorMod(r.key().hashCode(), 8);          // same key → same worker → order kept
        workerFor(shard).submit(() -> { handle(r); trackers.get(tp).done(r.offset()); });
        if (trackers.get(tp).inFlightCount() > 1000 && paused.add(tp)) consumer.pause(Set.of(tp));   // backpressure
    }
    for (var tp : new ArrayList<>(paused)) if (trackers.get(tp).inFlightCount() < 200) { consumer.resume(Set.of(tp)); paused.remove(tp); }
    Map<TopicPartition, OffsetAndMetadata> commit = new HashMap<>();
    trackers.forEach((tp, t) -> t.committable().ifPresent(o -> commit.put(tp, new OffsetAndMetadata(o + 1))));
    if (!commit.isEmpty()) consumer.commitAsync(commit, null);
}
// poll() keeps running even while paused → heartbeats + max.poll.interval satisfied
```
```python
c.pause([TopicPartition("orders", 0)]); c.resume([TopicPartition("orders", 0)])   # same idea; keep calling consume/poll
```
- Off-the-shelf: Confluent Parallel Consumer (Java, key-ordered concurrency); Spring `concurrency` is partition-bound, not key-bound

### 2.6 Consumer config table
| Config | Default | What it trades | Change when |
| --- | --- | --- | --- |
| `group.id` | — | fan-out vs competing | one id per logical service |
| `enable.auto.commit` | true | simplicity ↔ loss/dup control | `false` for anything with side effects |
| `auto.offset.reset` | latest | skip backlog ↔ reprocess history | `earliest` for new pipelines; `none` for strict |
| `max.poll.records` | 500 | batch efficiency ↔ poll-interval risk | lower when per-record work is heavy |
| `max.poll.interval.ms` | 5 min | slow-processing tolerance ↔ dead-consumer detection | = real worst-case batch time |
| `session.timeout.ms` / `heartbeat.interval.ms` | 45 s / 3 s | crash detection speed ↔ false evictions | lower in stable networks |
| `partition.assignment.strategy` | range+coop-sticky list | stop-the-world ↔ incremental | `CooperativeStickyAssignor` |
| `group.instance.id` | none | rebalance-free restarts ↔ idle partition during outage | stateful / slow-boot consumers |
| `group.protocol` (3.7+) | classic | client ↔ broker-side assignment | `consumer` once brokers ≥ 3.7/4.0 |
| `fetch.min.bytes` / `fetch.max.wait.ms` | 1 / 500 ms | request rate ↔ latency | raise min bytes for high-volume topics |
| `max.partition.fetch.bytes` | 1 MiB | memory ↔ throughput; must ≥ `message.max.bytes` | big messages |
| `isolation.level` | read_uncommitted | see aborted data ↔ LSO latency | `read_committed` with tx producers |
| `client.rack` | none | cross-AZ cost ↔ replica staleness | multi-AZ with fetch-from-follower enabled |

---

## 3. Delivery guarantees

### 3.1 Idempotent consumer (dedup table / upsert)
```sql
CREATE TABLE processed_events (event_id TEXT PRIMARY KEY, processed_at TIMESTAMPTZ DEFAULT now());
-- effect table keyed by business id so replays are upserts
CREATE TABLE payments (payment_id TEXT PRIMARY KEY, amount NUMERIC, version BIGINT);
```
```python
def handle(msg, db):
    evt = json.loads(msg.value()); eid = evt["event_id"]
    with db.transaction():
        if db.execute("INSERT INTO processed_events(event_id) VALUES (%s) ON CONFLICT DO NOTHING", (eid,)).rowcount == 0:
            return                                              # duplicate → skip, still commit offset
        db.execute("""INSERT INTO payments(payment_id, amount, version) VALUES (%s,%s,%s)
                      ON CONFLICT (payment_id) DO UPDATE SET amount=EXCLUDED.amount, version=EXCLUDED.version
                      WHERE payments.version < EXCLUDED.version""", (evt["payment_id"], evt["amount"], evt["version"]))
```
```java
@Transactional
public void handle(PaymentEvent e) {
    if (jdbc.update("INSERT INTO processed_events(event_id) VALUES (?) ON CONFLICT DO NOTHING", e.eventId()) == 0) return;
    jdbc.update("""INSERT INTO payments(payment_id, amount, version) VALUES (?,?,?)
                   ON CONFLICT (payment_id) DO UPDATE SET amount=EXCLUDED.amount, version=EXCLUDED.version
                   WHERE payments.version < EXCLUDED.version""", e.paymentId(), e.amount(), e.version());
}
```
- for HTTP sinks: pass `Idempotency-Key: <event_id>` header; for Redis dedup: `SET event:<id> 1 NX EX <retention_s>`

### 3.2 Offsets stored in the sink DB
```java
// exactly-once to one DB without Kafka transactions: {effect, offset} in one DB tx, seek on assignment
consumer.subscribe(List.of("orders"), new ConsumerRebalanceListener() {
    public void onPartitionsAssigned(Collection<TopicPartition> parts) {
        for (var tp : parts) { Long off = offsetsDao.get(tp); consumer.seek(tp, off == null ? 0 : off); }
    }
    public void onPartitionsRevoked(Collection<TopicPartition> parts) {}
});
for (var r : consumer.poll(Duration.ofSeconds(1))) {
    tx.execute(() -> { apply(r); offsetsDao.put(new TopicPartition(r.topic(), r.partition()), r.offset() + 1); });
}
// never commit to Kafka; group is used only for assignment. Set enable.auto.commit=false.
```

### 3.3 Transactions: read-process-write
```python
from confluent_kafka import Producer, Consumer, KafkaException
p = Producer({"bootstrap.servers": "localhost:9092", "transactional.id": "enricher-0", "enable.idempotence": True})
c = Consumer({"bootstrap.servers": "localhost:9092", "group.id": "enricher", "enable.auto.commit": False, "isolation.level": "read_committed"})
p.init_transactions(); c.subscribe(["orders"])
while True:
    msgs = c.consume(100, timeout=1.0)
    if not msgs: continue
    p.begin_transaction()
    try:
        for m in msgs: p.produce("orders-enriched", key=m.key(), value=enrich(m.value()))
        p.send_offsets_to_transaction(c.position(c.assignment()), c.consumer_group_metadata())
        p.commit_transaction()
    except KafkaException as e:
        p.abort_transaction()
        if e.args[0].txn_requires_abort(): continue          # retry batch: consumer position not advanced
        raise                                                # fatal (fenced) → exit, let another instance take over
```
```java
Properties pc = new Properties(); /* … */ pc.put(ProducerConfig.TRANSACTIONAL_ID_CONFIG, "enricher-" + instanceId);
var producer = new KafkaProducer<String, String>(pc); producer.initTransactions();
while (running) {
    var recs = consumer.poll(Duration.ofSeconds(1)); if (recs.isEmpty()) continue;
    producer.beginTransaction();
    try {
        for (var r : recs) producer.send(new ProducerRecord<>("orders-enriched", r.key(), enrich(r.value())));
        Map<TopicPartition, OffsetAndMetadata> offs = new HashMap<>();
        for (var tp : recs.partitions()) { var l = recs.records(tp); offs.put(tp, new OffsetAndMetadata(l.get(l.size()-1).offset() + 1)); }
        producer.sendOffsetsToTransaction(offs, consumer.groupMetadata());   // KIP-447 fencing via group metadata
        producer.commitTransaction();
    } catch (ProducerFencedException | OutOfOrderSequenceException | AuthorizationException fatal) {
        producer.close(); throw fatal;
    } catch (KafkaException e) { producer.abortTransaction(); }               // batch will be re-polled
}
```
```java
// Spring: KafkaTransactionManager auto-configured when spring.kafka.producer.transaction-id-prefix is set
@KafkaListener(topics = "orders") @Transactional("kafkaTransactionManager")
void enrich(ConsumerRecord<String, String> r) { kafka.send("orders-enriched", r.key(), enrich(r.value())); }
// container commits consumer offsets inside the same Kafka tx; consumer isolation-level: read_committed
```

### 3.4 Transactional outbox
```sql
CREATE TABLE outbox (id BIGSERIAL PRIMARY KEY, aggregate_id TEXT, topic TEXT, key TEXT, payload JSONB,
                     created_at TIMESTAMPTZ DEFAULT now(), published_at TIMESTAMPTZ);
```
```java
@Transactional
public void placeOrder(Order o) {
    orders.save(o);
    outbox.save(new OutboxRow(o.id(), "orders", o.id(), toJson(new OrderPlaced(o))));   // same DB tx → no dual-write gap
}
// Relay option A: Debezium outbox event router (CDC on outbox table) → Kafka; no polling, preserves commit order
// Relay option B: poller
@Scheduled(fixedDelay = 200)
@Transactional
public void relay() {
    List<OutboxRow> rows = outbox.lockUnpublished(100);          // SELECT … WHERE published_at IS NULL ORDER BY id FOR UPDATE SKIP LOCKED
    for (var r : rows) kafka.send(r.topic(), r.key(), r.payload()).get();   // sync: at-least-once toward Kafka
    outbox.markPublished(rows);
}
// consumers dedup by outbox id (header "event-id") — §3.1
```
```python
# Python poller relay (SQLAlchemy-ish pseudocode kept short)
with db.begin():
    rows = db.execute("SELECT id, topic, key, payload FROM outbox WHERE published_at IS NULL ORDER BY id LIMIT 100 FOR UPDATE SKIP LOCKED").fetchall()
    for r in rows: p.produce(r.topic, key=r.key, value=r.payload, headers=[("event-id", str(r.id).encode())])
    p.flush()
    db.execute("UPDATE outbox SET published_at=now() WHERE id = ANY(%s)", ([r.id for r in rows],))
```

---

## 4. Retry, DLQ, error handling

### 4.1 Blocking retry with backoff
```python
import time
def process_with_retry(m, attempts=3, base=0.2):
    for i in range(attempts):
        try: return handle(m)
        except TransientError:
            time.sleep(base * 2 ** i)                          # keep total < max.poll.interval.ms
        except PermanentError as e:
            send_to_dlt(m, e); return
    send_to_dlt(m, "retries exhausted")

def send_to_dlt(m, err):
    p.produce("orders.DLT", key=m.key(), value=m.value(), headers=(m.headers() or []) + [
        ("dlt-origin-topic", m.topic().encode()), ("dlt-origin-partition", str(m.partition()).encode()),
        ("dlt-origin-offset", str(m.offset()).encode()), ("dlt-exception", str(err).encode()[:1000])])
```
- blocking retry stalls the partition; fine for short transient sink errors, wrong for anything > seconds

### 4.2 Non-blocking retry topics + DLT
```
orders ──fail──▶ orders-retry-1s ──fail──▶ orders-retry-30s ──fail──▶ orders-retry-5m ──fail──▶ orders.DLT
   ▲ each retry topic has its own consumer that sleeps until (header retry-at) then re-processes
```
```java
// Java (plain client) — retry consumer for one tier
void retryLoop(String topic, String nextTopic, Duration delay) {
    for (var r : consumer.poll(Duration.ofSeconds(1))) {
        long readyAt = r.timestamp() + delay.toMillis();
        long wait = readyAt - System.currentTimeMillis();
        if (wait > 0) { consumer.pause(Set.of(new TopicPartition(r.topic(), r.partition()))); sleepButKeepPolling(wait); }
        try { handle(r); }
        catch (Exception e) { producer.send(new ProducerRecord<>(nextTopic, r.key(), r.value())); }   // escalate tier
        consumer.commitSync();
    }
}
// per-key ordering is lost across tiers → for order-sensitive keys, park the whole key (write key to a "parked" set; skip newer events for it until drained)
```

### 4.3 Spring: error handlers and `@RetryableTopic`
```java
@Bean
DefaultErrorHandler errorHandler(KafkaTemplate<Object, Object> template) {
    var recoverer = new DeadLetterPublishingRecoverer(template,
        (rec, ex) -> new TopicPartition(rec.topic() + ".DLT", rec.partition()));   // same partition → ordering hint preserved
    var h = new DefaultErrorHandler(recoverer, new ExponentialBackOffWithMaxRetries(3) {{ setInitialInterval(200); setMultiplier(2); }});
    h.addNotRetryableExceptions(DeserializationException.class, IllegalArgumentException.class);   // poison → straight to DLT
    return h;
}
// Spring adds headers: kafka_dlt-original-topic/partition/offset, kafka_dlt-exception-fqcn/message/stacktrace

@RetryableTopic(attempts = "4", backoff = @Backoff(delay = 1000, multiplier = 10), // 1s, 10s, 100s → then DLT
        topicSuffixingStrategy = TopicSuffixingStrategy.SUFFIX_WITH_INDEX_VALUE,
        include = TransientException.class, dltTopicSuffix = ".DLT")
@KafkaListener(topics = "orders", groupId = "billing")
void onOrder(OrderEvent e) { handle(e); }

@DltHandler
void onDlt(OrderEvent e, @Header(KafkaHeaders.EXCEPTION_MESSAGE) String why) { alert(e, why); }
```
```yaml
# poison-pill safe deserialization (don't crash the container on bad bytes)
spring.kafka.consumer.value-deserializer: org.springframework.kafka.support.serializer.ErrorHandlingDeserializer
spring.kafka.consumer.properties.spring.deserializer.value.delegate.class: org.springframework.kafka.support.serializer.JsonDeserializer
spring.kafka.consumer.properties.spring.json.trusted.packages: com.example.events
```

---

## 5. Cache patterns

### 5.1 Compacted topic as a KV snapshot
```bash
kafka-topics.sh --create --topic product-prices --partitions 12 --replication-factor 3 \
  --config cleanup.policy=compact --config min.cleanable.dirty.ratio=0.1 --config delete.retention.ms=86400000
```
```python
# bootstrap an in-memory cache from offset 0, then keep tailing (no group needed → assign)
cache = {}
c = Consumer({"bootstrap.servers": "localhost:9092", "group.id": f"price-cache-{uuid4()}", "enable.auto.commit": False})
parts = [TopicPartition("product-prices", p, OFFSET_BEGINNING) for p in range(12)]
c.assign(parts)
end = {p.partition: c.get_watermark_offsets(p)[1] for p in parts}
caught_up = set()
while True:
    m = c.poll(0.5)
    if m is None: continue
    if m.value() is None: cache.pop(m.key(), None)          # tombstone
    else: cache[m.key()] = json.loads(m.value())
    if m.offset() + 1 >= end[m.partition()]: caught_up.add(m.partition())
    if len(caught_up) == 12: ready.set()                     # serve traffic once warm
```
```java
// Java: same with consumer.assign + seekToBeginning + endOffsets; or use Kafka Streams GlobalKTable (§6.3) which does this for you
// producer side: producer.send(new ProducerRecord<>("product-prices", productId, null)) → delete
```

### 5.2 Cache invalidation via CDC events
```
Postgres ──Debezium (Connect)──▶ topic db.public.products (key = PK, compacted) ──▶ each API pod (own group.id) evicts/refreshes Redis or local cache
```
```java
@KafkaListener(topics = "db.public.products", groupId = "api-cache-${HOSTNAME}")    // unique group per pod → every pod sees every change
void onProductChange(ConsumerRecord<String, DebeziumEnvelope> r) {
    String id = r.key();
    if (r.value() == null || "d".equals(r.value().op())) cache.evict(id);
    else cache.put(id, r.value().after());
}
// pitfall: unique group ids leak into __consumer_offsets (7-day expiry); or use assign() with no commits
```
```json
// Debezium connector (Kafka Connect REST) — minimal
{"name":"products-cdc","config":{"connector.class":"io.debezium.connector.postgresql.PostgresConnector",
 "database.hostname":"pg","database.dbname":"shop","table.include.list":"public.products",
 "topic.prefix":"db","plugin.name":"pgoutput","tombstones.on.delete":"true"}}
```

---

## 6. Streams: group, aggregate, join, merge

### 6.1 Kafka Streams (Java): filter, map, branch, merge
```java
Properties p = new Properties();
p.put(StreamsConfig.APPLICATION_ID_CONFIG, "order-metrics");          // = group.id + prefix for internal topics
p.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
p.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
p.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass());
p.put(StreamsConfig.PROCESSING_GUARANTEE_CONFIG, StreamsConfig.EXACTLY_ONCE_V2);
p.put(StreamsConfig.NUM_STANDBY_REPLICAS_CONFIG, 1);

StreamsBuilder b = new StreamsBuilder();
KStream<String, Order> orders = b.stream("orders", Consumed.with(Serdes.String(), orderSerde));

KStream<String, Order> big = orders.filter((k, o) -> o.amount() > 100);
KStream<String, String> summaries = orders.mapValues(o -> o.id() + ":" + o.amount());
KStream<String, Order> rekeyed = orders.selectKey((k, o) -> o.customerId());           // marks for repartition

Map<String, KStream<String, Order>> byRegion = orders.split(Named.as("region-"))
    .branch((k, o) -> o.region().equals("EU"), Branched.as("eu"))
    .branch((k, o) -> o.region().equals("US"), Branched.as("us"))
    .defaultBranch(Branched.as("other"));

KStream<String, Order> euAndUs = byRegion.get("region-eu").merge(byRegion.get("region-us"));   // merge = union, no ordering across inputs
euAndUs.to("orders-priority", Produced.with(Serdes.String(), orderSerde));

KafkaStreams app = new KafkaStreams(b.build(), p);
app.setUncaughtExceptionHandler(ex -> StreamThreadExceptionResponse.REPLACE_THREAD);
Runtime.getRuntime().addShutdownHook(new Thread(app::close));
app.start();
```

### 6.2 groupBy, count, windowed aggregate
```java
// count per customer (KTable, changelog-backed)
KTable<String, Long> ordersPerCustomer = orders
    .groupBy((k, o) -> o.customerId(), Grouped.with(Serdes.String(), orderSerde))   // repartition topic auto-created
    .count(Materialized.as("orders-per-customer"));                                  // queryable state store name

// revenue per customer per 5-minute tumbling window, 1-minute grace, emit final only
KTable<Windowed<String>, Double> revenue = orders
    .groupBy((k, o) -> o.customerId(), Grouped.with(Serdes.String(), orderSerde))
    .windowedBy(TimeWindows.ofSizeAndGrace(Duration.ofMinutes(5), Duration.ofMinutes(1)))
    .aggregate(() -> 0.0, (cust, o, sum) -> sum + o.amount(),
               Materialized.<String, Double, WindowStore<Bytes, byte[]>>as("revenue-5m").withValueSerde(Serdes.Double()))
    .suppress(Suppressed.untilWindowCloses(Suppressed.BufferConfig.unbounded()));

revenue.toStream().map((w, sum) -> KeyValue.pair(w.key() + "@" + w.window().start(), sum)).to("revenue-5m");

// reduce (same type), session windows, sliding windows:
// .reduce((a, b) -> b)  .windowedBy(SessionWindows.ofInactivityGapAndGrace(...))  .windowedBy(SlidingWindows.ofTimeDifferenceAndGrace(...))
```

### 6.3 Joins: stream-table, stream-stream, GlobalKTable
```java
KTable<String, Customer> customers = b.table("customers", Consumed.with(Serdes.String(), customerSerde));   // compacted topic
GlobalKTable<String, Product> products = b.globalTable("products", Consumed.with(Serdes.String(), productSerde));

// stream-table: enrich orders with customer; requires co-partitioning (same partition count, same key)
KStream<String, EnrichedOrder> enriched = orders
    .selectKey((k, o) -> o.customerId())
    .join(customers, (o, c) -> new EnrichedOrder(o, c), Joined.with(Serdes.String(), orderSerde, customerSerde));
// .leftJoin keeps orders with no customer (c == null)

// stream-globaltable: no co-partitioning needed; keyExtractor picks lookup key from the record
KStream<String, EnrichedOrder> withProduct = orders.join(products, (k, o) -> o.productId(), (o, prod) -> o.withProduct(prod));

// stream-stream: orders joined with payments within 10 minutes (windowed; both sides buffered in state stores)
KStream<String, Payment> payments = b.stream("payments", Consumed.with(Serdes.String(), paymentSerde));
KStream<String, Settled> settled = orders.join(payments, (o, pay) -> new Settled(o, pay),
    JoinWindows.ofTimeDifferenceAndGrace(Duration.ofMinutes(10), Duration.ofMinutes(1)),
    StreamJoined.with(Serdes.String(), orderSerde, paymentSerde));

// table-table: KTable.join(KTable) → KTable (foreign-key join: customers.join(regions, Customer::regionId, ...))
```

### 6.4 Exactly-once, state stores, interactive queries
```java
// EOS v2 set in §6.1: one transactional producer per stream thread; commit.interval.ms default 100 ms under EOS
// interactive query of a materialized store
ReadOnlyKeyValueStore<String, Long> store = app.store(
    StoreQueryParameters.fromNameAndType("orders-per-customer", QueryableStoreTypes.keyValueStore()));
Long n = store.get("cust-42");   // only keys hosted on THIS instance; use app.queryMetadataForKey(...) to route to the owning host

// Processor API with punctuation (custom state + timers)
b.addStateStore(Stores.keyValueStoreBuilder(Stores.persistentKeyValueStore("pending"), Serdes.String(), orderSerde));
orders.process(() -> new Processor<String, Order, String, String>() {
    KeyValueStore<String, Order> st; ProcessorContext<String, String> ctx;
    public void init(ProcessorContext<String, String> c) { ctx = c; st = c.getStateStore("pending");
        c.schedule(Duration.ofSeconds(30), PunctuationType.WALL_CLOCK_TIME, ts -> expireOld(ts)); }
    public void process(Record<String, Order> r) { st.put(r.key(), r.value()); }
}, "pending");
```

### 6.5 Python streaming (Faust / plain consumer aggregate)
- there is no official Kafka Streams for Python; options
  - `faust-streaming` (community fork): agents, tables (changelog-backed), tumbling windows
  - `quixstreams`: pandas-like stream ops with RocksDB state
  - plain `confluent-kafka` consumer + your own state (fine for stateless / small keyed aggregates)
```python
# faust-streaming
import faust
app = faust.App("order-metrics", broker="kafka://localhost:9092", processing_guarantee="exactly_once")
class Order(faust.Record): id: str; customer_id: str; amount: float
orders = app.topic("orders", key_type=str, value_type=Order)
revenue = app.Table("revenue", default=float).tumbling(300, expires=3600)   # changelog topic auto-created

@app.agent(orders)
async def aggregate(stream):
    async for o in stream.group_by(Order.customer_id):            # repartition topic
        revenue[o.customer_id] += o.amount
```
```python
# plain consumer keyed aggregate, state per partition, checkpoint = commit after flushing state to sink
counts = {}
for m in poll_batches(c):
    counts[m.key()] = counts.get(m.key(), 0) + 1
    if len(counts) >= 1000: flush_upsert(counts); counts.clear(); c.commit(asynchronous=False)
# on rebalance revoke: flush + commit; state must be rebuildable (idempotent upsert) since it is not changelog-backed
```

### 6.6 Streams config table
| Config | Default | What it trades | Change when |
| --- | --- | --- | --- |
| `application.id` | — | identity for group + internal topics | one per topology |
| `processing.guarantee` | at_least_once | latency/coordination ↔ EOS | `exactly_once_v2` for Kafka→Kafka pipelines |
| `commit.interval.ms` | 30 s (100 ms under EOS) | output latency ↔ overhead | lower for near-real-time |
| `num.stream.threads` | 1 | parallelism ↔ CPU (≤ total tasks) | = cores, spread across instances |
| `num.standby.replicas` | 0 | restore time ↔ storage/network | 1 for large state |
| `cache.max.bytes.buffering` / `statestore.cache.max.bytes` | 10 MiB | dedup of updates ↔ update latency | 0 to see every update |
| `state.dir` | /tmp/kafka-streams | restart restore ↔ disk | persistent volume in k8s |
| `default.deserialization.exception.handler` | LogAndFail | crash ↔ skip poison | `LogAndContinueExceptionHandler` + metric |
| `topology.optimization` | none | fewer repartition topics | `all` |
| `acceptable.recovery.lag` | 10000 | task move to warm standby ↔ staleness | tune with KIP-441 |

---

## 7. Spring Boot wiring
```yaml
spring:
  kafka:
    bootstrap-servers: localhost:9092
    producer:
      acks: all
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: org.springframework.kafka.support.serializer.JsonSerializer
      compression-type: zstd
      transaction-id-prefix: order-svc-tx-        # enables KafkaTransactionManager; omit for non-tx
      properties:
        enable.idempotence: true
        linger.ms: 10
        batch.size: 131072
        delivery.timeout.ms: 120000
    consumer:
      group-id: billing
      enable-auto-commit: false
      auto-offset-reset: earliest
      isolation-level: read_committed
      max-poll-records: 200
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: org.springframework.kafka.support.serializer.ErrorHandlingDeserializer
      properties:
        spring.deserializer.value.delegate.class: org.springframework.kafka.support.serializer.JsonDeserializer
        spring.json.trusted.packages: com.example.events
        partition.assignment.strategy: org.apache.kafka.clients.consumer.CooperativeStickyAssignor
        max.poll.interval.ms: 300000
        session.timeout.ms: 45000
    listener:
      ack-mode: manual            # RECORD | BATCH | MANUAL | MANUAL_IMMEDIATE
      concurrency: 3
      missing-topics-fatal: false
    streams:
      application-id: order-metrics
      properties:
        processing.guarantee: exactly_once_v2
```
```java
@Configuration @EnableKafka @EnableKafkaStreams
class KafkaConfig {
    @Bean ConcurrentKafkaListenerContainerFactory<String, Object> kafkaListenerContainerFactory(
            ConsumerFactory<String, Object> cf, DefaultErrorHandler eh) {
        var f = new ConcurrentKafkaListenerContainerFactory<String, Object>();
        f.setConsumerFactory(cf); f.setCommonErrorHandler(eh); f.setConcurrency(3);
        f.getContainerProperties().setAckMode(ContainerProperties.AckMode.MANUAL);
        return f;
    }
    @Bean KStream<String, Order> topology(StreamsBuilder b) { /* §6 */ return null; }
}
// Testing: @EmbeddedKafka(partitions = 3, topics = "orders") or Testcontainers KafkaContainer (§9)
```

---

## 8. Broker / topic config table
| Config (scope) | Default | What it trades | Change when |
| --- | --- | --- | --- |
| `num.partitions` (broker, for auto-create) | 1 | parallelism ↔ overhead | disable auto-create (`auto.create.topics.enable=false`), create explicitly |
| `default.replication.factor` / topic RF | 1 | durability ↔ storage ×RF | 3 in prod |
| `min.insync.replicas` (broker/topic) | 1 | write availability ↔ durability | 2 with RF 3 |
| `unclean.leader.election.enable` | false | availability ↔ data loss | true only for loss-tolerant topics |
| `retention.ms` / `retention.bytes` (topic) | 7 d / -1 | replay window ↔ disk | per topic, explicit |
| `cleanup.policy` (topic) | delete | history ↔ latest-state | `compact` for changelog/KV |
| `min.cleanable.dirty.ratio` / `min.compaction.lag.ms` | 0.5 / 0 | cleaner I/O ↔ dup residency | lower ratio for cache topics |
| `delete.retention.ms` (topic) | 24 h | tombstone visibility for slow consumers | ≥ slowest consumer lag |
| `segment.bytes` / `segment.ms` | 1 GiB / 7 d | retention granularity ↔ file count | smaller for compacted / short-retention topics |
| `message.max.bytes` (broker/topic) | 1 MiB | big messages ↔ memory, replication | with `replica.fetch.max.bytes`, `max.partition.fetch.bytes` |
| `log.retention.check.interval.ms` | 5 min | retention precision ↔ scan cost | rarely |
| `replica.lag.time.max.ms` | 30 s | ISR strictness ↔ flapping | lower with fast disks/network |
| `num.network.threads` / `num.io.threads` | 3 / 8 | request parallelism ↔ CPU | scale with cores; watch `RequestHandlerAvgIdlePercent` |
| `log.dirs` | /tmp/kafka-logs | I/O parallelism (JBOD) | multiple disks |
| `broker.rack` | none | AZ-aware placement | always in multi-AZ |
| `replica.selector.class` | leader | fetch-from-follower | `RackAwareReplicaSelector` |
| `transaction.max.timeout.ms` | 15 min | hung-tx blast radius on read_committed | lower (e.g. 1 min) |
| `offsets.retention.minutes` | 7 d | offset survival for idle groups | raise for batch consumers |
| `remote.log.storage.system.enable` + `remote.storage.enable` (topic) | false | long retention cost ↔ remote read latency | tiered storage (3.9+) |
| `group.coordinator.rebalance.protocols` (4.0) | classic,consumer | enable KIP-848 | on |
| `quota.*` (`producer_byte_rate`, `consumer_byte_rate`, `request_percentage`) per client/user | none | tenant isolation ↔ throttling | multi-tenant clusters |

---

## 9. Observability and testing
- Metrics to graph (JMX / Prometheus `kafka_exporter`, client `MetricsReporter`)
  | Signal | Meaning | Alert |
  | --- | --- | --- |
  | `UnderReplicatedPartitions`, `IsrShrinksPerSec` | durability degraded | > 0 for > 1 min |
  | `ActiveControllerCount` | must be 1 cluster-wide | ≠ 1 |
  | `RequestHandlerAvgIdlePercent`, `NetworkProcessorAvgIdlePercent` | broker saturation | < 0.3 |
  | consumer `records-lag-max`, group lag in seconds | consumer falling behind | derivative > 0 for N min |
  | producer `record-error-rate`, `buffer-available-bytes`, `request-latency-avg` | producer health / backpressure | errors > 0; buffer → 0 |
  | `LogEndOffset − LastStableOffset` | hung transactions | growing |
  | Streams `task-restore-remaining-records`, `rebalance-rate` | state restore / churn | restore > minutes |
- Testing
```java
// Testcontainers
static KafkaContainer kafka = new KafkaContainer(DockerImageName.parse("apache/kafka:3.9.0"));
@DynamicPropertySource static void props(DynamicPropertyRegistry r) { r.add("spring.kafka.bootstrap-servers", kafka::getBootstrapServers); }

// Streams topology test without a broker
TopologyTestDriver d = new TopologyTestDriver(b.build(), p);
TestInputTopic<String, Order> in = d.createInputTopic("orders", new StringSerializer(), orderSerde.serializer());
TestOutputTopic<String, Double> out = d.createOutputTopic("revenue-5m", new StringDeserializer(), new DoubleDeserializer());
in.pipeInput("k", new Order("1", "c1", 10.0), 0L);
d.advanceWallClockTime(Duration.ofMinutes(6));
assertEquals(10.0, out.readValue());
```
```python
# Python: testcontainers-python KafkaContainer, or pytest with a mocked Producer/Consumer; contract-test serializers against registry
from testcontainers.kafka import KafkaContainer
with KafkaContainer("apache/kafka:3.9.0") as k:
    bs = k.get_bootstrap_server()
```
- Tests worth writing: duplicate delivery → single effect (§3.1); crash after DB write before commit → replay is a no-op; rebalance mid-batch → no loss (`onPartitionsRevoked` commit); poison message → DLT with headers, partition keeps moving; transaction abort → consumer with `read_committed` never sees partial output

---

## References
- Apache Kafka docs: Producer/Consumer/Streams/Broker configs (kafka.apache.org/documentation, 3.9 / 4.0, accessed 2026-08)
- confluent-kafka-python docs and examples (github.com/confluentinc/confluent-kafka-python), librdkafka `CONFIGURATION.md`
- Spring for Apache Kafka reference (docs.spring.io/spring-kafka, 3.x): error handlers, `@RetryableTopic`, transactions
- Kafka Streams Developer Guide (kafka.apache.org/documentation/streams), `TopologyTestDriver`
- Debezium Outbox Event Router docs; Confluent Parallel Consumer README
- faust-streaming docs (faust-streaming.github.io/faust), quixstreams docs
- Testcontainers Kafka module (Java, Python)
