# 03db.01aurora.06pools-rds-proxy Connection Pooling And Relational Database Service (RDS) Proxy

> Two bounded pools per process (writer, reader), sized from `max_connections`, recycled often enough to follow Domain Name System (DNS).

## Index

- [1. Why Pool](#1-why-pool)
- [2. Pool Knobs](#2-pool-knobs)
  - [2.1 Why maxLifetime Under 15 Minutes](#21-why-maxlifetime-under-15-minutes)
  - [2.2 Sizing](#22-sizing)
- [3. Two Pools In Code](#3-two-pools-in-code)
- [4. RDS Proxy](#4-rds-proxy)
- [Related](#related)

## 1. Why Pool

A Postgres connection = one backend Operating System (OS) process on the server.

- Memory per backend: order of magnitude several megabytes (MB)
- Login with Transport Layer Security (TLS) + Identity and Access Management (IAM): order of magnitude tens of milliseconds (ms)
- Rule: pool and reuse connections; never connect per request
- Separate writer and reader pools
  - Prevents writes landing on replicas
  - Prevents reads missing own writes by accident

## 2. Pool Knobs

Hikari names; psycopg_pool equivalents are in [98tradeoffs](01aurora.98tradeoffs.md).

- `maximumPoolSize`: hard cap per process
- `connectionTimeout`: max wait for a free connection before failing
- `maxLifetime`: retire a connection after this age (Hikari adds jitter)
- `idleTimeout`: retire idle connections above `minimumIdle`

### 2.1 Why maxLifetime Under 15 Minutes

- Not because the token kills open connections; it does not
- Real reasons
  - Re-resolve DNS regularly
    - Rebalance across readers
    - Leave a demoted writer
  - Bound how long a connection keeps state from an old instance
  - Exercise the token path regularly, so broken IAM config surfaces early
- Convention here: 14 min, just under token life

### 2.2 Sizing

- Hikari wiki rule of thumb: `cores × 2 + spindles` per database, not per pod
- Constraint: `pods × pools × maxSize` < `max_connections` minus admin headroom
  - `max_connections` derives from instance memory / max Aurora Capacity Unit (ACU)
- `REQUIRES_NEW` and separate audit connections double per-request demand
  - See [09transactions-propagation](01aurora.09transactions-propagation.md)

## 3. Two Pools In Code

One pool per endpoint and role; both start lazily, so startup opens no connection.

**Java**

```java
// config/_03db_01aurora/AuroraConfig.java
static HikariDataSource pool(AuroraProperties p, String name, String host, RdsUtilities rds, boolean readOnly) {
    HikariDataSource ds = new HikariDataSource(); // no-arg: pool starts on first getConnection()
    ds.setPoolName(name);
    DataSource physical = new IamAuthDataSource(pgDataSource(p, host), p.username(), tokenSupplier(p, host, rds));
    ds.setDataSource(physical);
    ds.setMaximumPoolSize(p.pool().maxSize());
    // Below max so idleTimeout can shrink the pool, and fewer connections reconnect at once after failover.
    ds.setMinimumIdle(Math.max(1, p.pool().maxSize() / 2));
    ds.setConnectionTimeout(p.pool().connectionTimeoutMs()); // wait for a free connection, then fail fast
    ds.setMaxLifetime(p.pool().maxLifetimeMs());             // Hikari subtracts up to 2.5% jitter
    ds.setIdleTimeout(p.pool().idleTimeoutMs());
    ds.setKeepaliveTime(120_000);                            // ping idle connections; finds dead ones
    ds.setValidationTimeout(1_000);                          // isValid() budget on checkout
    ds.setInitializationFailTimeout(-1);                     // don't fail startup if Aurora is mid-failover
    ds.setLeakDetectionThreshold(30_000);                    // log a stack when held > 30 s
    ds.setReadOnly(readOnly);                                // reader: driver marks transactions READ ONLY
    return ds;
}

@Bean(name = READER_DS, destroyMethod = "close")
public HikariDataSource auroraReaderDataSource(AuroraProperties p, RdsUtilities rds) {
    return pool(p, "x-aurora-reader", p.readerEndpoint(), rds, true);
}
```

```java
// config/_03db_01aurora/AuroraProperties.java
// maxLifetimeMs (14 min) < 15 min token life by convention; the real reason is DNS re-resolution.
public record Pool(
        @DefaultValue("10") int maxSize,
        @DefaultValue("3000") long connectionTimeoutMs,
        @DefaultValue("840000") long maxLifetimeMs,
        @DefaultValue("300000") long idleTimeoutMs) {
}
```

**Python**

```python
# app/infra/_03db_01aurora.py
class AuroraPools:
    """Writer + reader ConnectionPool, created on first use (thread-safe), so importing makes no connection."""

    def writer(self) -> ConnectionPool[psycopg.Connection[DictRow]]:
        with self._lock:
            if self._writer is None:
                self._writer = self._make_pool("x-aurora-writer", self._settings.aurora_writer_endpoint, False)
            return self._writer

    def _make_pool(self, name: str, host: str, read_only: bool) -> ConnectionPool[psycopg.Connection[DictRow]]:
        s = self._settings
        pool = ConnectionPool(
            kwargs=self._kwargs_supplier(host, read_only),     # fresh IAM token per new connection
            min_size=max(1, s.aurora_pool_max_size // 2),
            max_size=s.aurora_pool_max_size,                   # pods x pools x max_size < max_connections
            timeout=POOL_TIMEOUT_S,                            # 3 s, like Hikari connectionTimeout
            max_lifetime=float(s.aurora_pool_max_lifetime_s),  # 840 s; psycopg_pool adds jitter
            max_idle=POOL_MAX_IDLE_S,                          # 300 s, like Hikari idleTimeout
            reconnect_timeout=60.0,
            check=ConnectionPool.check_connection,             # validate on checkout (one round trip)
            name=name,
            open=False,
        )
        pool.open(wait=False)  # connect in the background; first request waits at most `timeout`
        return pool
```

**Catch**

- Total connections = `pods × pools × maxSize`; must stay under `max_connections` with headroom
  - Headroom for admin and failover reconnects
- A pool-wait timeout (no SQLSTATE) is overload
  - Shed load; do not retry it ([10retries-idempotency](01aurora.10retries-idempotency.md))
- Reconnect storm after failover
  - Jittered lifetimes, small min idle, or Relational Database Service (RDS) Proxy

## 4. RDS Proxy

A managed connection pooler in front of the cluster.

- Multiplexes many client connections onto fewer database (DB) connections
- Keeps client connections across failover
  - Amazon Web Services (AWS) says failover gets faster
- **Pinning**: session state pins a client to one DB connection
  - Triggers: `SET`, temp tables, some prepared statements
  - Result: multiplexing lost
- Costs
  - Per virtual Central Processing Unit (vCPU)/ACU-hour
  - Adds a hop (order of magnitude: about a millisecond)
- Choose when
  - Many short-lived clients (Lambda)
  - Or connection count, not query load, is the limit
- Gap: Terraform does not declare one; described only

## Related

- [00index](01aurora.00index.md)
- [05iam-auth-tls](01aurora.05iam-auth-tls.md)
- [03failover-dns](01aurora.03failover-dns.md)
