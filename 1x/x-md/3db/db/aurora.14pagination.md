# 03db.01aurora.14pagination Pagination: OFFSET vs Keyset

> OFFSET reads and discards every skipped row; keyset seeks to a cursor, so cost stays flat with depth.

## Index

- [1. OFFSET](#1-offset)
- [2. Keyset (Seek)](#2-keyset-seek)
- [3. Index](#3-index)
- [4. Code](#4-code)
  - [4.1 OFFSET Page](#41-offset-page)
  - [4.2 Keyset Page And Cursor](#42-keyset-page-and-cursor)
- [5. Choosing](#5-choosing)
- [Related](#related)

## 1. OFFSET

`LIMIT 20 OFFSET 100000`

- Server still reads and discards 100,000 rows
  - Result: cost grows with page number
- Rows inserted before the offset shift pages
  - Result: duplicates or skipped rows
- Only strength: jump to page k

## 2. Keyset (Seek)

`WHERE (created_at, id) < (:last_created_at, :last_id) ORDER BY created_at DESC, id DESC LIMIT 20`

- Index seek to the cursor, then read 20 rows
  - Result: cost independent of depth
- Stable under inserts
- Needs a unique tie-breaker (`id`)
  - Many rows share `created_at`
  - `now()` is transaction start time, so a batch insert gives every row the same timestamp
- Cursor returned to the client as an opaque token
  - Opaque lets you change the sort key later without breaking clients

## 3. Index

- Needs an index matching the ORDER BY: `(customer_id, created_at, id)`, scanned backward

```sql
-- resources/_03db_01aurora/schema.sql
-- ORDER BY created_at DESC, id DESC within one customer = this index scanned backward,
-- and the row comparison (created_at, id) < (?, ?) becomes an index condition.
-- Also narrows SERIALIZABLE predicate locks for the per-customer credit-limit check.
CREATE INDEX IF NOT EXISTS x_order_customer_created_id_idx
    ON x_order (customer_id, created_at, id);
```

## 4. Code

Both fetch `size + 1` rows: the extra row says whether a next page exists.

### 4.1 OFFSET Page

**Java**

```java
// infra/_03db_01aurora/AuroraJdbcRepository.java
// When to use: small sets or admin UIs that need "jump to page k".
@Override
public Page<Order> pageByOffset(String customerId, int page, int size) {
    String sql = "SELECT " + ORDER_COLUMNS + " FROM x_order WHERE customer_id = :customerId "
            + "ORDER BY created_at DESC, id DESC LIMIT :limit OFFSET :offset";
    MapSqlParameterSource params = new MapSqlParameterSource()
            .addValue("customerId", customerId)
            .addValue("limit", size + 1)                 // one extra row tells us whether a next page exists
            .addValue("offset", (long) page * size);
    List<Order> rows = reader.query(sql, params, this::mapOrder);
    boolean more = rows.size() > size;
    return new Page<>(more ? rows.subList(0, size) : rows, more ? Integer.toString(page + 1) : null);
}
```

**Python**

```python
# app/infra/_03db_01aurora.py
def page_by_offset(self, customer_id: str, page: int, size: int) -> Page[Order]:
    """Catch: the server reads and discards page*size rows; inserts shift rows between pages."""
    rows = self._conn.execute(
        f"SELECT {ORDER_COLUMNS} FROM x_order WHERE customer_id = %s "
        "ORDER BY created_at DESC, id DESC LIMIT %s OFFSET %s",
        (customer_id, size + 1, page * size),
    ).fetchall()
    more = len(rows) > size
    return Page(items=[_order(r) for r in rows[:size]], next=str(page + 1) if more else None)
```

### 4.2 Keyset Page And Cursor

**Java**

```java
// infra/_03db_01aurora/AuroraJdbcRepository.java
@Override
public Page<Order> pageByKeyset(String customerId, String cursor, int size) {
    MapSqlParameterSource params = new MapSqlParameterSource()
            .addValue("customerId", customerId)
            .addValue("limit", size + 1);
    String seek = "";
    if (cursor != null && !cursor.isBlank()) {
        Cursor c = Cursor.decode(cursor);
        seek = " AND (created_at, id) < (:createdAt, :id)"; // row comparison = index condition
        params.addValue("createdAt", OffsetDateTime.ofInstant(c.createdAt(), ZoneOffset.UTC)).addValue("id", c.id());
    }
    String sql = "SELECT " + ORDER_COLUMNS + " FROM x_order WHERE customer_id = :customerId" + seek
            + " ORDER BY created_at DESC, id DESC LIMIT :limit";
    List<Order> rows = reader.query(sql, params, this::mapOrder);
    if (rows.size() <= size) {
        return new Page<>(rows, null); // null next = last page
    }
    List<Order> pageRows = rows.subList(0, size);
    Order last = pageRows.get(size - 1);
    return new Page<>(pageRows, new Cursor(last.createdAt(), last.id()).encode());
}

/** Opaque keyset cursor: base64url("createdAt|id"). */
record Cursor(Instant createdAt, long id) {
    String encode() {
        String raw = createdAt + "|" + id;
        return Base64.getUrlEncoder().withoutPadding().encodeToString(raw.getBytes(StandardCharsets.UTF_8));
    }
    // decode(): split on the last '|'; any parse error -> IllegalArgumentException("invalid cursor")
}
```

**Python**

```python
# app/infra/_03db_01aurora.py
def page_by_keyset(self, customer_id: str, cursor: str | None, size: int) -> Page[Order]:
    """Catch: id is the tie-breaker (rows of one transaction share now()); no jump to page k."""
    if cursor:
        created_at, last_id = decode_cursor(cursor)
        rows = self._conn.execute(
            f"SELECT {ORDER_COLUMNS} FROM x_order WHERE customer_id = %s AND (created_at, id) < (%s, %s) "
            "ORDER BY created_at DESC, id DESC LIMIT %s",
            (customer_id, created_at, last_id, size + 1),
        ).fetchall()
    else:
        rows = self._conn.execute(
            f"SELECT {ORDER_COLUMNS} FROM x_order WHERE customer_id = %s "
            "ORDER BY created_at DESC, id DESC LIMIT %s",
            (customer_id, size + 1),
        ).fetchall()
    items = [_order(r) for r in rows[:size]]
    if len(rows) <= size:
        return Page(items=items, next=None)
    last = items[-1]
    return Page(items=items, next=_encode_cursor(last.created_at, last.id))

def _encode_cursor(created_at: datetime, last_id: int) -> str:
    """Opaque keyset cursor: base64url("iso-timestamp|id")."""
    raw = f"{created_at.isoformat()}|{last_id}".encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")
```

**Catch**

- Contract: pass `next` back verbatim; null / None = last page
- The Python service decodes the cursor before borrowing a connection
  - A malformed cursor becomes Hypertext Transfer Protocol (HTTP) 400 without touching the pool
- Page size is clamped to 1..100 in the service

## 5. Choosing

| Option | Cost at depth | Stable under inserts | Jump to page k | Choose when |
|---|---|---|---|---|
| OFFSET | Grows with page number | No | Yes | Small sets, admin User Interfaces (UIs) |
| Keyset | Flat | Yes | No | Application Programming Interfaces (APIs), infinite scroll |

Pick: keyset for APIs and infinite scroll, unless users need numbered page jumps over a small set.

## Related

- [00index](01aurora.00index.md)
- [02endpoints-replica-lag](01aurora.02endpoints-replica-lag.md): pages run on the reader
- [99interview](01aurora.99interview.md): Q7
