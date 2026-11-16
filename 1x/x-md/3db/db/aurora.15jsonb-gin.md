# 03db.01aurora.15jsonb-gin Binary JavaScript Object Notation (JSONB) And Generalized Inverted Index (GIN)

> Binary JavaScript Object Notation (JSONB) stores parsed JavaScript Object Notation (JSON); a Generalized Inverted Index (GIN) inverted index makes containment queries on schema-less attributes fast.

## Index

- [1. JSONB](#1-jsonb)
- [2. GIN Index](#2-gin-index)
- [3. Containment Query In Code](#3-containment-query-in-code)
- [4. Limits](#4-limits)
- [Related](#related)

## 1. JSONB

- **JSONB**: parsed binary JSON
  - Keys deduplicated
  - Not order-preserving
- Operators
  - `@>` containment
  - `?` key exists
  - `->` / `->>` access
  - jsonpath `@?`

## 2. GIN Index

A GIN index is an inverted index from keys/values to rows.

| Operator class | Supports | Size / speed |
|---|---|---|
| `jsonb_ops` (default) | `@>`, `?`, `?\|`, `?&` | Larger |
| `jsonb_path_ops` | `@>` and jsonpath only | Smaller, faster for containment |

- Write cost: one row insert touches many index entries
  - `fastupdate` buffers them in a pending list

```sql
-- resources/_03db_01aurora/schema.sql
-- jsonb_path_ops: smaller and faster than jsonb_ops, but only @> and jsonpath.
CREATE INDEX IF NOT EXISTS x_order_attrs_gin
    ON x_order USING GIN (attrs jsonb_path_ops);
```

## 3. Containment Query In Code

`attrs @> '{"channel":"web"}'` is served by the GIN index and runs on the reader.

**Java**

```java
// infra/_03db_01aurora/AuroraJdbcRepository.java
// Insert side: insert() binds attrs as CAST(:attrs AS jsonb).
@Override
public List<Order> findByAttrs(Map<String, Object> containment, int limit) {
    String sql = "SELECT " + ORDER_COLUMNS + " FROM x_order WHERE attrs @> CAST(:filter AS jsonb) "
            + "ORDER BY id DESC LIMIT :limit";
    MapSqlParameterSource params = new MapSqlParameterSource()
            .addValue("filter", toJson(containment))   // Jackson -> JSON text
            .addValue("limit", limit);
    return reader.query(sql, params, this::mapOrder);
}
```

**Python**

```python
# app/infra/_03db_01aurora.py
def find_by_attrs(self, containment: dict[str, Any], limit: int) -> list[Order]:
    """attrs @> %s served by the GIN (jsonb_path_ops) index. Jsonb() adapts the dict to a jsonb parameter."""
    rows = self._conn.execute(
        f"SELECT {ORDER_COLUMNS} FROM x_order WHERE attrs @> %s ORDER BY id DESC LIMIT %s",
        (Jsonb(containment), limit),
    ).fetchall()
    return [_order(r) for r in rows]
```

**Catch**

- ⚠️ Java Database Connectivity (JDBC): `?` is a bind placeholder
  - Use `@>` or `jsonb_exists()` instead of the `?` operator

## 4. Limits

- When to use: filtering on sparse, schema-less attributes
- A column you filter on every query belongs in a real typed column with a B-tree index

## Related

- [00index](01aurora.00index.md)
- [11crud-batch-upsert](01aurora.11crud-batch-upsert.md): `attrs` in the schema
