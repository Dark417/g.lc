# 01core.01principles.15template Template-Style Boilerplate Removal

> The framework owns a resource's fixed lifecycle steps; you pass only the variable part as a callback.

## Index

- [1. Idea](#1-idea)
- [2. Mechanism](#2-mechanism)
- [3. Code](#3-code)
  - [3.1 Violation](#31-violation)
  - [3.2 Fix](#32-fix)
  - [3.3 The Real JdbcTemplate](#33-the-real-jdbctemplate)
- [4. Catch](#4-catch)

Part C, Spring principles (Java only). Back to [00index](00index.md).

## 1. Idea

Inversion of control for a connection's lifecycle.

- The framework owns the fixed steps of a resource's lifecycle
- You pass only the variable part as a callback
- Examples
  - `JdbcTemplate`
  - `TransactionTemplate`
  - `RestClient`
  - `KafkaTemplate`
- Don't Repeat Yourself (DRY) for resource handling ([06](06dry-kiss-yagni.md#1-dont-repeat-yourself-dry))
- Example (`TemplateMethod`)
  - Violation: every call copies open/retry/close/translate
  - Fix: `MiniTemplate.execute(callback)` owns retry, close and error translation once

## 2. Mechanism

`JdbcTemplate.query(sql, rowMapper)` runs the same skeleton around your callback.

→ Get connection (bound to the current transaction if any)  
→ Prepare statement, execute, iterate rows → your `RowMapper`  
→ Translate `SQLException` into the `DataAccessException` hierarchy  
→ Close everything in `finally`

- Template method + callbacks (lambdas), not Gang of Four (GoF) inheritance

## 3. Code

A fake resource (`FakeDataSource`, `FakeConnection`, `TransientDbError`) lets the demo run without a `DataSource`.

### 3.1 Violation

```java
// concept/_01core_01principles/spring/TemplateMethod.java
/** Skeleton copy #1; copy #2 (loadCustomer) would repeat it, and one copy will forget close(). */
public static String loadOrder(FakeDataSource ds, String id) {   // TemplateMethod.Violation.loadOrder
    for (int attempt = 1; ; attempt++) {
        FakeConnection c = ds.getConnection();
        try {
            return c.query("SELECT * FROM orders WHERE id = ?", id);
        } catch (TransientDbError e) {             // like SQLState 40001 serialization failure
            if (attempt == 3) {
                throw new DataAccessFailure("loadOrder failed", e);
            }
        } finally {
            c.close();
        }
    }
}
```

### 3.2 Fix

```java
// concept/_01core_01principles/spring/TemplateMethod.java
@FunctionalInterface
public interface ConnectionCallback<T> { T doInConnection(FakeConnection c); }

/** Owns the fixed steps once; reuses the shared full-jitter Retry for transient errors only. */
public static final class MiniTemplate {           // TemplateMethod.Fix.MiniTemplate
    private final FakeDataSource ds;
    private final Retry retry;

    // The template method: open -> callback -> close always -> translate driver errors.
    // Catch: retry is only safe because the callback here is a read; writes need idempotency.
    public <T> T execute(ConnectionCallback<T> callback) {
        try {
            return retry.call(() -> {
                try (FakeConnection c = ds.getConnection()) {
                    return callback.doInConnection(c);
                }
            }, e -> e instanceof TransientDbError);
        } catch (TransientDbError e) {
            throw new DataAccessFailure("query failed after retries", e);   // callers never see driver types
        }
    }

    public String loadOrder(String id) {
        return execute(c -> c.query("SELECT * FROM orders WHERE id = ?", id));
    }
    public String loadCustomer(String id) {
        return execute(c -> c.query("SELECT * FROM customers WHERE id = ?", id));
    }
}
```

- Demo: `TemplateMethod.demo(maxAttempts)` via `SpringPrinciplesDemo.template()`
  - A transient failure is retried by the template
  - Every connection is closed (`open=0`)
  - Attempts come from typed config ([14external-config](14external-config.md))

### 3.3 The Real JdbcTemplate

```java
// concept/_01core_01principles/spring/TemplateMethod.java
// JdbcTemplate does the same steps around a RowMapper callback.
// Use when a DataSource exists (the Aurora slice); not called here, so no DataSource bean is needed.
public static List<String> findOrderIds(JdbcTemplate jdbc, String customerId) {
    return jdbc.query("SELECT id FROM orders WHERE customer_id = ?", (rs, rowNum) -> rs.getString("id"), customerId);
}
```

## 4. Catch

One-line template calls hide cost and vendor detail.

→ The template hides cost.  
⇒ `jdbc.query` inside a loop is N+1 queries that look like one line each.  
→ Batch (`batchUpdate`, `IN` lists) and watch query counts.

→ Exception translation hides vendor detail.  
⇒ Retry logic can't see the Structured Query Language (SQL) state it needs.  
→ Inspect `getCause()` / `SQLException.getSQLState()` where retry depends on it.

- 🗣 "`JdbcTemplate` is inversion of control for a connection's lifecycle."
