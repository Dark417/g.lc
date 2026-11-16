# 03db.01aurora.11crud-batch-upsert Create, Read, Update, Delete (CRUD), Batch Insert, Upsert, Schema

> Single-round-trip writes with `RETURNING`, batched inserts, atomic upserts, and chunked imports with partial failure.

## Index

- [1. Schema](#1-schema)
- [2. Create, Read, Update, Delete (CRUD) With RETURNING](#2-create-read-update-delete-crud-with-returning)
- [3. Batch Insert](#3-batch-insert)
- [4. Chunked Import With Partial Failure](#4-chunked-import-with-partial-failure)
- [5. Upsert ON CONFLICT DO UPDATE](#5-upsert-on-conflict-do-update)
- [Related](#related)

## 1. Schema

The slice uses four tables; every index serves one named query.

- `x_order`: orders with version, idempotency key, Binary JavaScript Object Notation (JSONB) attrs
- `x_inventory`: stock per Stock Keeping Unit (SKU), `CHECK (on_hand >= 0)` = last defence against oversell
- `x_job`: job queue ([13skip-locked-queue](01aurora.13skip-locked-queue.md))
- `x_audit`: audit rows, `clock_timestamp()` (wall clock, not transaction start)

```sql
-- resources/_03db_01aurora/schema.sql
-- One-time admin step (master user): CREATE USER x_app, GRANT rds_iam TO x_app,
-- GRANT CREATE ON SCHEMA public TO x_app (PostgreSQL 15+ no longer grants CREATE on public to everyone)
CREATE TABLE IF NOT EXISTS x_order (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_id     TEXT        NOT NULL,
    sku             TEXT        NOT NULL,
    quantity        INT         NOT NULL CHECK (quantity > 0),
    amount_cents    BIGINT      NOT NULL CHECK (amount_cents >= 0),
    status          TEXT        NOT NULL DEFAULT 'NEW',
    version         INT         NOT NULL DEFAULT 0,          -- optimistic lock counter
    idempotency_key TEXT        UNIQUE,                      -- one row per request
    attrs           JSONB       NOT NULL DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),      -- now() = transaction start: ties are common
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS x_inventory (
    sku        TEXT        PRIMARY KEY,
    on_hand    INT         NOT NULL CHECK (on_hand >= 0),    -- last line of defence against oversell
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

**Java**

```java
// infra/_03db_01aurora/AuroraJdbcRepository.java
// Idempotent (IF NOT EXISTS everywhere). Catch: N pods racing DDL at startup;
// real projects run Flyway/Liquibase once.
public void applySchema() {
    DataSource ds = Objects.requireNonNull(writer.getJdbcTemplate().getDataSource(), "writer DataSource");
    new ResourceDatabasePopulator(new ClassPathResource("_03db_01aurora/schema.sql")).execute(ds);
}
```

**Python**

```python
# app/infra/_03db_01aurora.py
def apply_schema(self) -> None:
    """Run SCHEMA_SQL in one transaction (PostgreSQL DDL is transactional). Real projects use migrations."""
    statements = [stmt.strip() for stmt in SCHEMA_SQL.split(";") if stmt.strip()]
    with (
        self._connection(self._pools.writer(), evict_on_read_only=True) as conn,
        conn.transaction(),
    ):
        for stmt in statements:
            conn.execute(stmt)
```

**Catch**

- `applySchema` is a demo
- Migrations via Flyway/Liquibase, not app startup
  - Prevents N pods racing Data Definition Language (DDL)
- `CREATE INDEX CONCURRENTLY` on live tables
  - Prevents a write-blocking lock during index builds

## 2. Create, Read, Update, Delete (CRUD) With RETURNING

`INSERT … RETURNING` returns the generated id, defaults and timestamps in one round trip.

**Java**

```java
// infra/_03db_01aurora/AuroraJdbcRepository.java
// When to use: creates that are never retried.
// Catch: without an idempotency key a lost commit ack is unrecoverable.
@Override
public Order insert(NewOrder o) {
    String sql = "INSERT INTO x_order (customer_id, sku, quantity, amount_cents, idempotency_key, attrs) "
            + "VALUES (:customerId, :sku, :quantity, :amountCents, :idempotencyKey, CAST(:attrs AS jsonb)) "
            + "RETURNING " + ORDER_COLUMNS;
    return writer.queryForObject(sql, orderParams(o), this::mapOrder);
}

// Read by primary key on the writer: always sees the latest commit. Catch: every such read is writer load.
@Override
public Optional<Order> findById(long id) {
    String sql = "SELECT " + ORDER_COLUMNS + " FROM x_order WHERE id = :id";
    return writer.query(sql, Map.of("id", id), this::mapOrder).stream().findFirst();
}
```

**Python**

```python
# app/infra/_03db_01aurora.py
def insert(self, order: NewOrder) -> Order:
    """Plain INSERT ... RETURNING. Catch: no idempotency key => never retry."""
    row = self._conn.execute(
        "INSERT INTO x_order (customer_id, sku, quantity, amount_cents, idempotency_key, attrs) "
        "VALUES (%(customer_id)s, %(sku)s, %(quantity)s, %(amount_cents)s, %(key)s, %(attrs)s) "
        f"RETURNING {ORDER_COLUMNS}",
        _order_params(order),
    ).fetchone()
    return _order(row)

def find_by_id(self, order_id: int) -> Order | None:
    """On a writer store it sees the latest commit, on a reader store it may lag."""
    row = self._conn.execute(f"SELECT {ORDER_COLUMNS} FROM x_order WHERE id = %s", (order_id,)).fetchone()
    return _order(row) if row else None
```

**Catch**

- Idempotent variant: [10retries-idempotency](01aurora.10retries-idempotency.md)
- Delete and dead tuples: [07mvcc-vacuum](01aurora.07mvcc-vacuum.md)

## 3. Batch Insert

Fewer round trips per row: the deciding variable is rows per round trip.

- Java: Java Database Connectivity (JDBC) batch + `reWriteBatchedInserts=true`
  - pgjdbc rewrites the batch into multi-row `VALUES`
- Python: `executemany`
  - psycopg 3 pipelines the statements (no round trip per row)

**Java**

```java
// infra/_03db_01aurora/AuroraJdbcRepository.java
@Override
public int batchInsert(List<NewOrder> orders) {
    String sql = "INSERT INTO x_order (customer_id, sku, quantity, amount_cents, idempotency_key, attrs) "
            + "VALUES (?, ?, ?, ?, ?, CAST(? AS jsonb)) ON CONFLICT (idempotency_key) DO NOTHING";
    int[][] counts = writer.getJdbcTemplate().batchUpdate(sql, orders, JDBC_BATCH_SIZE, (ps, o) -> { // 500
        ps.setString(1, o.customerId());
        // ... remaining parameters
        ps.setString(6, toJson(o.attrs()));
    });
    int known = 0;
    for (int[] group : counts) {
        for (int c : group) {
            if (c == Statement.SUCCESS_NO_INFO) {
                return orders.size(); // rewritten batch does not report per-row outcome
            }
            known += Math.max(c, 0);
        }
    }
    return known;
}
```

**Python**

```python
# app/infra/_03db_01aurora.py
def batch_insert(self, orders: list[NewOrder]) -> int:
    """executemany: pipelined; rowcount = rows inserted. Catch: for millions of rows COPY is faster."""
    with self._conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO x_order (customer_id, sku, quantity, amount_cents, idempotency_key, attrs) "
            "VALUES (%(customer_id)s, %(sku)s, %(quantity)s, %(amount_cents)s, %(key)s, %(attrs)s) "
            "ON CONFLICT (idempotency_key) DO NOTHING",
            [_order_params(o) for o in orders],
        )
        return max(cur.rowcount, 0)
```

**Catch**

- With the rewrite the driver reports `SUCCESS_NO_INFO` (-2) per row
  - Exact inserted count (ON CONFLICT skips) is unknown
- For millions of rows, `COPY` is faster still
- Use inside one transaction: all-or-nothing

## 4. Chunked Import With Partial Failure

Each chunk = one transaction, retried on transient errors; a chunk that still fails is reported.

**Java**

```java
// service/_03db_01aurora/AuroraOrderService.java
public BatchResult importOrders(List<NewOrder> rows) {
    int inserted = 0;
    List<String> failures = new ArrayList<>();
    for (int from = 0; from < rows.size(); from += IMPORT_CHUNK_SIZE) { // 500
        int to = Math.min(from + IMPORT_CHUNK_SIZE, rows.size());
        List<NewOrder> chunk = List.copyOf(rows.subList(from, to));
        try {
            inserted += withRetry("importChunk", () -> tx.importChunk(chunk)); // keys make replays no-ops
        } catch (RuntimeException e) {
            String state = AuroraErrors.sqlState(e);
            failures.add("rows " + from + ".." + (to - 1) + ": " + (state == null ? "" : state + " ")
                    + e.getClass().getSimpleName());
        }
    }
    return new BatchResult(rows.size(), inserted, failures);
}
```

```java
// service/_03db_01aurora/AuroraOrderTx.java
// One chunk = one transaction: all rows or none (a constraint error aborts the chunk).
@Transactional(transactionManager = AuroraConfig.WRITER_TX)
public int importChunk(List<NewOrder> chunk) {
    return orders.batchInsert(chunk);
}
```

**Python**

```python
# app/service/_03db_01aurora.py
def import_orders(self, rows: list[NewOrder]) -> BatchResult:
    inserted = 0
    failures: list[str] = []
    for start in range(0, len(rows), IMPORT_CHUNK_SIZE):
        chunk = rows[start : start + IMPORT_CHUNK_SIZE]

        def attempt(chunk: list[NewOrder] = chunk) -> int:
            with self._repo.writer_tx() as store:
                return store.batch_insert(chunk)

        try:
            inserted += self._with_retry(attempt)
        except Exception as e:  # report per chunk, keep going
            state = getattr(e, "sqlstate", None)
            failures.append(f"rows {start}..{start + len(chunk) - 1}: {state or ''} {type(e).__name__}".strip())
    return BatchResult(requested=len(rows), inserted=inserted, failures=failures)
```

**Catch**

- Big chunks hold locks and Write-Ahead Log (WAL) longer
- Rows without an idempotency key are not deduplicated on replay
  - Require keys for retried imports

## 5. Upsert ON CONFLICT DO UPDATE

Atomic insert-or-update, no SELECT-then-INSERT race.

**Java**

```java
// infra/_03db_01aurora/AuroraJdbcRepository.java
// When to use: "set to this value" writes keyed by a natural key.
@Override
public StockLevel upsertStock(String sku, int onHand) {
    String sql = "INSERT INTO x_inventory (sku, on_hand) VALUES (:sku, :onHand) "
            + "ON CONFLICT (sku) DO UPDATE SET on_hand = EXCLUDED.on_hand, updated_at = now() "
            + "RETURNING sku, on_hand, updated_at";
    return writer.queryForObject(sql, Map.of("sku", sku, "onHand", onHand),
            (rs, n) -> new StockLevel(rs.getString("sku"), rs.getInt("on_hand"), instant(rs, "updated_at")));
}
```

**Python**

```python
# app/infra/_03db_01aurora.py
def upsert_stock(self, sku: str, on_hand: int) -> StockLevel:
    row = self._conn.execute(
        "INSERT INTO x_inventory (sku, on_hand) VALUES (%s, %s) "
        "ON CONFLICT (sku) DO UPDATE SET on_hand = EXCLUDED.on_hand, updated_at = now() "
        "RETURNING sku, on_hand, updated_at",
        (sku, on_hand),
    ).fetchone()
    return StockLevel(sku=row["sku"], on_hand=row["on_hand"], updated_at=row["updated_at"])
```

**Catch**

- `SET on_hand = EXCLUDED.on_hand` is idempotent ⇒ retried (`restock`)
- An additive `SET on_hand = x_inventory.on_hand + EXCLUDED.on_hand` is **not** safe to retry

## Related

- [00index](01aurora.00index.md)
- [10retries-idempotency](01aurora.10retries-idempotency.md)
- [06pools-rds-proxy](01aurora.06pools-rds-proxy.md): `reWriteBatchedInserts` lives on the driver
