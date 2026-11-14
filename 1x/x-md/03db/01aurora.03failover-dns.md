# 03db.01aurora.03failover-dns Failover And Domain Name System (DNS)

> Failover flips a Domain Name System (DNS) name in tens of seconds; the client must evict stale connections and retry whole transactions.

## Index

- [1. Failover Flow](#1-failover-flow)
- [2. Time](#2-time)
- [3. What The Client Does](#3-what-the-client-does)
  - [3.1 Evict On Stale DNS In Code](#31-evict-on-stale-dns-in-code)
- [4. Faster Options](#4-faster-options)
- [Related](#related)

## 1. Failover Flow

Trigger: writer instance failure, Availability Zone (AZ) problem, or a manual failover.

→ Aurora picks a reader by promotion tier (Terraform: `promotion_tier = count.index`), then size  
→ Promotes it to writer; storage needs no copy because the volume is shared  
→ Updates the cluster endpoint Canonical Name (CNAME) to the new writer  
→ Old writer restarts and rejoins as a reader  
⇒ Every open connection to the old writer breaks (SQLSTATE `08006` or `57P01`)  
⇒ Clients that cached the old Internet Protocol (IP) connect to an instance that is now a reader  
⇒ Writes on it fail with `25006 read_only_sql_transaction`

- Terraform: [`modules/03db_01aurora/main.tf`](../../terraform/modules/03db_01aurora/main.tf)

## 2. Time

- Amazon Web Services (AWS) docs: service typically restored in under 60 s, often under 30 s
  - Order of magnitude
- Aurora endpoint DNS Time To Live (TTL) is short (AWS docs: 5 s)
- Limit: Java Virtual Machines (JVMs) and Operating System (OS) resolvers may cache longer
  - Java: set `networkaddress.cache.ttl` low
  - It is a security property; set it before the first lookup

## 3. What The Client Does

Four moves, each closing one failure path.

- Evict broken connections
  - Hikari already evicts `08xxx` and `57P0x`
- Also evict on `25006` from the writer pool
  - Stale DNS put the connection on a reader
- Retry the whole transaction with backoff that spans the failover window
  - See [10retries-idempotency](01aurora.10retries-idempotency.md)
- Bound `maxLifetime` so the pool reconnects through fresh DNS
  - See [06pools-rds-proxy](01aurora.06pools-rds-proxy.md)

### 3.1 Evict On Stale DNS In Code

Java installs a Hikari `SQLExceptionOverride` on the writer pool; Python closes the connection so the pool drops it.

**Java**

```java
// infra/_03db_01aurora/AuroraEvictionOverride.java
// Hikari already evicts 08xxx and 57P01/57P02/57P03.
// Added: 25006 on the WRITER pool = connection reached a demoted writer (cached DNS).
public final class AuroraEvictionOverride implements SQLExceptionOverride {

    @java.lang.Override // spelled out: inside this class "Override" means SQLExceptionOverride.Override
    public SQLExceptionOverride.Override adjudicate(SQLException e) {
        return AuroraErrors.READ_ONLY_TRANSACTION.equals(e.getSQLState())
                ? SQLExceptionOverride.Override.MUST_EVICT
                : SQLExceptionOverride.Override.CONTINUE_EVICT;
    }
}
```

```java
// config/_03db_01aurora/AuroraConfig.java
@Bean(name = WRITER_DS, destroyMethod = "close")
public HikariDataSource auroraWriterDataSource(AuroraProperties p, RdsUtilities rds) {
    HikariDataSource ds = pool(p, "x-aurora-writer", p.writerEndpoint(), rds, false);
    ds.setExceptionOverride(new AuroraEvictionOverride()); // evict on 25006: stale DNS reached a demoted writer
    return ds;
}
```

**Python**

```python
# app/infra/_03db_01aurora.py
@contextmanager
def _connection(self, pool, evict_on_read_only: bool) -> Iterator[psycopg.Connection[DictRow]]:
    """Borrow a connection; on 25006 from the writer pool close it so the pool discards it."""
    with pool.connection() as conn:
        try:
            yield conn
        except errors.ReadOnlySqlTransaction:
            if evict_on_read_only:
                conn.close()  # closed connections are dropped and replaced when returned to the pool
            raise
```

**Catch**

- Only install on the writer pool
  - On the reader pool, `25006` is a bug in the caller, not a stale node
- Eviction alone does not save the request: the caller still retries the whole transaction
- Also needed: `socketTimeout` / Transmission Control Protocol (TCP) keepalives
  - A half-open TCP socket after failover can otherwise hang forever

## 4. Faster Options

Both stop depending on DNS.

- **AWS Advanced Java Database Connectivity (JDBC) Wrapper / Python Wrapper**
  - Reads cluster topology
  - Reconnects to the new writer without waiting for DNS
  - Not a dependency in this repo (gap)
- **Relational Database Service (RDS) Proxy**
  - Keeps client connections open
  - Re-points them to the new writer
  - See [06pools-rds-proxy](01aurora.06pools-rds-proxy.md)

## Related

- [00index](01aurora.00index.md)
- [05iam-auth-tls](01aurora.05iam-auth-tls.md): reconnect storms vs Identity and Access Management (IAM) auth rate
- [98tradeoffs](01aurora.98tradeoffs.md): failure modes table
