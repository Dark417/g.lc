# 03db.02dynamodb.05single-table-design Single-Table Design

> Model the table from access patterns, with prefixed keys and fixed-width sort keys, as `x-orders` does.

## Index

- [1. Access-Pattern-First Modeling](#1-access-pattern-first-modeling)
- [2. The x-orders Key Design](#2-the-x-orders-key-design)
- [3. Why One Table](#3-why-one-table)
- [4. Sort Keys Compare As Strings](#4-sort-keys-compare-as-strings)
- [5. Key Helpers In Code](#5-key-helpers-in-code)
- [6. Limits](#6-limits)
- [Related](#related)

## 1. Access-Pattern-First Modeling

You design keys from the queries, not from the entities.

→ List every access pattern with its rate and latency target  
→ Pick Partition Key (PK)/Sort Key (SK) so each pattern is one `GetItem` or one `Query`  
→ Add a Global Secondary Index (GSI) only for patterns the base keys cannot serve  
→ Write the key design down (here: the header of [`modules/03db_02dynamodb/main.tf`](../../terraform/modules/03db_02dynamodb/main.tf))

## 2. The x-orders Key Design

Every pattern maps to one call on one key.

| Access pattern | Operation | Key |
|---|---|---|
| Get customer profile | GetItem | `PK=CUSTOMER#c`, `SK=PROFILE` |
| Get one order | GetItem | `PK=CUSTOMER#c`, `SK=ORDER#<iso>#<orderId>` |
| Customer's orders, newest first | Query | `PK=CUSTOMER#c`, `begins_with(SK, "ORDER#")`, `ScanIndexForward=false` |
| Customer's orders in a time range | Query | `PK=CUSTOMER#c`, `SK BETWEEN ORDER#<from> AND ORDER#<to>` |
| All PENDING orders, oldest first | Query GSI1 | `GSI1PK=STATUS#PENDING`, sort by `GSI1SK=<iso>` |
| Idempotency check | GetItem / condition | `x-idempotency.idempotencyKey` |

- Terraform also declares Time To Live (TTL), streams, and Point-In-Time Recovery (PITR) on `x-orders`, plus the `x-idempotency` table
- Key design best practices
  - High-cardinality PK spread evenly
    - Prevents: hot partitions
  - Prefix keys with the entity type (`CUSTOMER#`, `ORDER#`)
    - Prevents: collisions between entity types in one table
  - Fixed-width timestamps and zero-padded numbers in SK
    - Prevents: wrong sort order
- Trick: composite SK for hierarchy (`COUNTRY#STATE#CITY`) + `begins_with`

## 3. Why One Table

Related items that share a PK come back together in one request.

- Profile + orders share a PK
  - Result: one Query returns both (pre-joined)
- Fewer tables to monitor, back up, and scale

## 4. Sort Keys Compare As Strings

Sort keys compare byte by byte, so formatting decides order.

- Timestamps must be fixed width
  - `2026-01-01T00:00:00Z` sorts after `2026-01-01T00:00:00.123Z` (`Z` > `.`)
  - Result: always format with milliseconds: `yyyy-MM-ddTHH:mm:ss.SSSZ`
- Numbers inside keys must be zero-padded

→ Variable-width timestamps or numbers in SK  
⇒ Out-of-order pages (wrong sort order)  
→ Fixed-width International Organization for Standardization (ISO), zero-padded numbers

## 5. Key Helpers In Code

All key strings are built in one place per stack, so Java and Python writers agree.

**Java**

```java
// domain/_03db_02dynamodb/OrderKeys.java
public static final String CUSTOMER_PREFIX = "CUSTOMER#";
public static final String ORDER_PREFIX = "ORDER#";
public static final String PROFILE_SK = "PROFILE";
public static final String STATUS_PREFIX = "STATUS#";

// Fixed width with millis. Instant.toString() drops zero fractions ("...00Z" vs "...00.123Z"),
// and 'Z' (0x5A) > '.' (0x2E) would sort the earlier timestamp AFTER the later one.
private static final DateTimeFormatter ISO_MILLIS =
        DateTimeFormatter.ofPattern("uuuu-MM-dd'T'HH:mm:ss.SSS'Z'").withZone(ZoneOffset.UTC);

public static String customerPk(String customerId) {
    return CUSTOMER_PREFIX + customerId;
}

public static String orderSk(Instant createdAt, String orderId) {
    return ORDER_PREFIX + iso(createdAt) + "#" + orderId;
}

/** Lower/upper bound for BETWEEN: "ORDER#<iso>" sorts before every "ORDER#<iso>#<id>". */
public static String orderSkBound(Instant t) {
    return ORDER_PREFIX + iso(t);
}

public static String gsi1Pk(OrderStatus status) {
    return STATUS_PREFIX + status.name();
}
```

**Python**

```python
# app/domain/_03db_02dynamodb.py
def iso(t: datetime) -> str:
    """Fixed-width UTC timestamp with millis.

    datetime.isoformat() drops zero microseconds, which breaks string ordering of sort keys.
    """
    t = t.astimezone(timezone.utc)
    return t.strftime("%Y-%m-%dT%H:%M:%S.") + f"{t.microsecond // 1000:03d}Z"

def pk_customer(customer_id: str) -> str:
    return CUSTOMER_PREFIX + customer_id

def sk_order(created_at: datetime, order_id: str) -> str:
    return f"{ORDER_PREFIX}{iso(created_at)}#{order_id}"

def sk_order_bound(t: datetime) -> str:
    """BETWEEN bound: 'ORDER#<iso>' sorts before every 'ORDER#<iso>#<id>' -> BETWEEN acts as [from, to)."""
    return ORDER_PREFIX + iso(t)
```

**Catch**

- Both default formatters (`Instant.toString()`, `datetime.isoformat()`) drop zero fractions
  - Result: never use them for sort keys

## 6. Limits

Single-table pays off for known, stable patterns.

- For analytics or ad-hoc queries
  - Result: export to Simple Storage Service (S3) and use Athena
- When to refuse single-table: see [99interview Q11](02dynamodb.99interview.md#q11-when-would-you-refuse-single-table-design)
- Adding a pattern on a live table: see [99interview Q10](02dynamodb.99interview.md#q10-new-access-pattern-on-a-live-single-table-design)

## Related

- [00index](02dynamodb.00index.md)
- [04indexes-gsi-lsi](02dynamodb.04indexes-gsi-lsi.md)
- [07query-pagination-scan](02dynamodb.07query-pagination-scan.md)
