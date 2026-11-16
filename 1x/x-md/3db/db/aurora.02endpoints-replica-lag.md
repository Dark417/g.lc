# 03db.01aurora.02endpoints-replica-lag Endpoints, Replicas, Replica Lag

> Writer endpoint for the latest commit, reader endpoint for lag-tolerant reads, and a fallback when the replica is behind.

## Index

- [1. Endpoints](#1-endpoints)
  - [1.1 Cluster Endpoint](#11-cluster-endpoint)
  - [1.2 Reader Endpoint](#12-reader-endpoint)
  - [1.3 Instance And Custom Endpoints](#13-instance-and-custom-endpoints)
- [2. How A Reader Stays Current](#2-how-a-reader-stays-current)
- [3. Replica Lag](#3-replica-lag)
  - [3.1 Size And Measurement](#31-size-and-measurement)
  - [3.2 Lag Probe In Code](#32-lag-probe-in-code)
- [4. Read-After-Write Routing](#4-read-after-write-routing)
  - [4.1 The Caveat](#41-the-caveat)
  - [4.2 Routing In Code](#42-routing-in-code)
- [Related](#related)

## 1. Endpoints

Aurora gives Domain Name System (DNS) names, not Internet Protocol addresses (IPs); which instance a name points at changes over time.

### 1.1 Cluster Endpoint

- Also called the writer endpoint
- DNS Canonical Name (CNAME) to whichever instance is the writer now
- Use for every write
- Use for every read that must see the latest commit

### 1.2 Reader Endpoint

- DNS round-robin over reader instances
- Balances **connections**, not queries
  - A pool that opened 10 connections at one moment may land them all on one reader
  - Bounded `maxLifetime` re-resolves DNS and spreads them again
  - See [06pools-rds-proxy](01aurora.06pools-rds-proxy.md)

### 1.3 Instance And Custom Endpoints

- Instance endpoints and custom endpoints exist
- Use: pinning analytics to specific readers

## 2. How A Reader Stays Current

The writer streams the same redo records to readers that it sends to storage.

- Reader applies them to pages already in its buffer cache
- Other pages are read from shared storage on a miss
- No data copy ⇒ replica creation does not copy the dataset
- 🗣 "A replica is just another compute node on the same volume, so adding one doesn't copy data, but it still lags by milliseconds."

## 3. Replica Lag

Lag is small but never zero, and it spikes exactly when the writer is busiest.

### 3.1 Size And Measurement

- Amazon Web Services (AWS) docs: usually well under 100 milliseconds (ms)
  - Order of magnitude: tens of ms
- Spikes
  - Under heavy write load
  - When a reader is Central Processing Unit (CPU)-starved
- Measure
  - CloudWatch `AuroraReplicaLag`
  - `aurora_replica_status()` on the cluster

### 3.2 Lag Probe In Code

The repo samples `aurora_replica_status()` on the writer, one row per reader.

**Java**

```java
// infra/_03db_01aurora/AuroraJdbcRepository.java
// Aurora-only function, queried on the writer. Catch: point-in-time sample;
// may need extra privileges for x_app.
@Override
public Map<String, Long> replicaLagMillis() {
    Map<String, Long> lag = new LinkedHashMap<>();
    writer.query("SELECT server_id, replica_lag_in_msec FROM aurora_replica_status() "
                    + "WHERE session_id <> 'MASTER_SESSION_ID'", // skip the writer's own row
            rs -> {
                lag.put(rs.getString("server_id"), Math.round(rs.getDouble("replica_lag_in_msec")));
            });
    return lag;
}
```

**Python**

```python
# app/infra/_03db_01aurora.py
def replica_lag_ms(self) -> dict[str, int]:
    """Per-reader lag from aurora_replica_status() (Aurora-only), sampled on the writer.

    Catch: a point-in-time sample; CloudWatch AuroraReplicaLag is the alarm source.
    """
    with self._connection(self._pools.writer(), evict_on_read_only=True) as conn:
        rows = conn.execute(
            "SELECT server_id, replica_lag_in_msec FROM aurora_replica_status() "
            "WHERE session_id <> 'MASTER_SESSION_ID'"
        ).fetchall()
    return {str(r["server_id"]): round(float(r["replica_lag_in_msec"] or 0)) for r in rows}
```

**Catch**

- A sample is not a guarantee: lag spikes under write bursts
- Alarm on CloudWatch `AuroraReplicaLag`, not on this endpoint

## 4. Read-After-Write Routing

The reader endpoint gives no read-your-writes guarantee.

### 4.1 The Caveat

→ Client commits an order on the writer  
→ Next request reads it through the reader endpoint 20 ms later  
⇒ Reader may not have applied the commit yet  
⇒ "Order not found" or the old status  
→ Route reads that must see own writes to the writer, or pass a version and fall back to the writer when the reader is behind

- Fix options
  - Writer for read-your-writes flows
  - **Version token**: client sends the version it last wrote
    - Read the reader; fall back to the writer if `version < token`
  - Sticky-to-writer window per session after a write
- Trade-off: every fallback adds writer load
  - Measure the fallback rate

### 4.2 Routing In Code

`strong=true` goes to the writer; otherwise reader first, writer on a miss or a stale version.

**Java**

```java
// infra/_03db_01aurora/AuroraJdbcRepository.java
// Offloads the writer. Catch: read-after-write NOT guaranteed (replica lag).
@Override
public Optional<Order> findByIdOnReader(long id) {
    String sql = "SELECT " + ORDER_COLUMNS + " FROM x_order WHERE id = :id";
    return reader.query(sql, Map.of("id", id), this::mapOrder).stream().findFirst();
}
```

```java
// service/_03db_01aurora/AuroraOrderService.java
// minVersion = the version the client last wrote (read-your-writes token).
public Order getOrder(long id, boolean strong, Integer minVersion) {
    return withRetry("getOrder", () -> {
        if (!strong) {
            var fromReader = orders.findByIdOnReader(id);
            if (fromReader.isPresent() && (minVersion == null || fromReader.get().version() >= minVersion)) {
                return fromReader.get();
            }
            // miss or stale on the replica: replica lag, not necessarily absence
        }
        return orders.findById(id).orElseThrow(() -> new OrderNotFoundException(id));
    });
}
```

**Python**

```python
# app/service/_03db_01aurora.py
def get_order(self, order_id: int, strong: bool = False, min_version: int | None = None) -> Order:
    """Reader first; writer when strong, when the reader misses, or when its version < min_version."""

    def attempt() -> Order:
        if not strong:
            with self._repo.reader_tx(Isolation.READ_COMMITTED) as replica:
                found = replica.find_by_id(order_id)
            if found is not None and (min_version is None or found.version >= min_version):
                return found
            # miss or stale: replica lag, not necessarily absence
        with self._repo.writer_tx() as store:
            order = store.find_by_id(order_id)
        if order is None:
            raise OrderNotFound(f"order {order_id} not found")
        return order

    return self._with_retry(attempt)
```

**Catch**

- Every fallback is writer load
- Without `minVersion`, a stale-but-present row (old status) is returned
- A CPU-starved reader lags more ⇒ more fallbacks

## Related

- [00index](01aurora.00index.md)
- [01architecture](01aurora.01architecture.md)
- [08isolation-levels](01aurora.08isolation-levels.md): REPEATABLE READ reports on the reader
