# 01core.01principles.10cqs-failfast-pola Command-Query Separation (CQS), Fail Fast And Least Astonishment

> Correctness guards: queries without side effects, errors caught at the first boundary, and behavior that matches the name.

## Index

- [1. Command Query Separation](#1-command-query-separation)
  - [1.1 Idea](#11-idea) · [1.2 Code](#12-code) · [1.3 Catch](#13-catch)
- [2. Fail Fast](#2-fail-fast)
  - [2.1 Idea](#21-idea) · [2.2 Code](#22-code) · [2.3 Catch](#23-catch)
- [3. Principle Of Least Astonishment](#3-principle-of-least-astonishment)
  - [3.1 Idea](#31-idea) · [3.2 Code](#32-code) · [3.3 Catch](#33-catch)

Part B, general principles (Java + Python). Back to [00index](00index.md).

## 1. Command Query Separation

A method either changes state or returns data, not both.

### 1.1 Idea

- A method is one of (Meyer, 1988):
  - **command**: changes state, returns nothing
  - **query**: returns data, no side effects
- Running example (`Cqs`)
  - Violation: `nextOrderNumber()` that also increments the counter
  - Fix: `reserveNumber()` command + `peekNext()` query
- **Mechanism**
  - Queries are safe to repeat, cache, reorder, log, retry, call from a debugger

### 1.2 Code

A "getter" burns numbers; the fix offers a safe query, and an explicit atomic exception.

```java
// concept/_01core_01principles/general/Cqs.java
/** Violation: reads like a getter; every call (debugger, log line, retry) consumes a number. */
public long nextOrderNumber() { return next++; }   // Cqs.Violation.OrderNumbers

// Fix
public static final class OrderNumbers {           // Cqs.Fix.OrderNumbers
    private final AtomicLong next = new AtomicLong(1);

    /** Query: safe to call any number of times. */
    public long peekNext() { return next.get(); }

    /** Command: changes state, returns nothing. */
    public void advance() { next.incrementAndGet(); }

    /** Justified CQS exception: atomic reserve-and-return, like INSERT ... RETURNING id. */
    public long reserveNumber() { return next.getAndIncrement(); }
}
```

```python
# app/concept/_01core_01principles/general.py
class CqsOrderNumbers:
    def peek_next(self) -> int:
        """Query: safe to repeat."""
        return self._next

    def advance(self) -> None:
        """Command: changes state, returns nothing."""
        with self._lock:
            self._next += 1

    def reserve_number(self) -> int:
        """Justified exception: atomic reserve-and-return (like INSERT ... RETURNING id)."""
        with self._lock:
            n = self._next
            self._next += 1
            return n
```

- Python violation: `CqsViolationNumbers.next_order_number`
- Demo: `Cqs.demo()` / `cqs_demo()`; the second "read" of the violation returns 2 (number 1 lost)
- Use for any Application Programming Interface (API) where callers might retry, log or cache calls

### 1.3 Catch

Splitting an atomic read-modify-write creates a check-then-act race.

→ Splitting an atomic read-modify-write into query + command.  
⇒ Check-then-act race: two callers peek the same number.  
→ Keep atomic ops combined: `AtomicLong.incrementAndGet`, `stack.pop`, `INSERT ... RETURNING id`, DynamoDB `UpdateItem` with `ReturnValues`.

→ Command-Query Separation (CQS) confused with Command Query Responsibility Segregation (CQRS).  
⇒ Teams split databases when they only needed cleaner methods.  
→ CQS = method level; CQRS = separate read and write models (Greg Young).

- 🗣 "Queries must be safe to call twice — except atomic ops where splitting causes races."

## 2. Fail Fast

Detect and report an error at the point closest to its cause.

### 2.1 Idea

- Detect and report an error at the point closest to its cause (Shore, Institute of Electrical and Electronics Engineers (IEEE) Software, 2004)
- Running example (`FailFast`)
  - Violation: `Order` accepts a negative amount; a downstream job crashes hours later
  - Fix: validate in the record's compact constructor / dataclass `__post_init__`
  - Config validated at startup ([14external-config](14external-config.md))
- **Mechanism**
  - Short distance between cause and symptom ⇒ cheap diagnosis
  - No corrupted state propagated

### 2.2 Code

Invalid objects cannot exist; batches validate per record and quarantine bad rows.

```java
// concept/_01core_01principles/general/FailFast.java
/** Violation: accepts anything; a downstream job divides by currency rate and throws hours later. */
public record Order(String id, BigDecimal amount, String currency) { }   // FailFast.Violation.Order

/** Fix: the error names the field at the point of creation. */
public record Order(String id, BigDecimal amount, String currency) {     // FailFast.Fix.Order
    public Order {                                 // compact constructor
        Objects.requireNonNull(id, "id");
        Objects.requireNonNull(amount, "amount");
        if (amount.signum() <= 0) {
            throw new IllegalArgumentException("amount must be > 0, got " + amount);
        }
        if (currency == null || currency.length() != 3) {
            throw new IllegalArgumentException("currency must be ISO-4217, got " + currency);
        }
    }
}

// Per-record fail fast: each bad row is rejected with a reason; the batch continues.
// Catch: alert on the quarantine rate, or silent data loss replaces loud failure.
public static BatchResult validateBatch(List<String[]> rows) {   // FailFast.Fix.validateBatch
    List<Order> ok = new ArrayList<>();
    List<String> bad = new ArrayList<>();
    for (String[] r : rows) {
        try {
            ok.add(new Order(r[0], new BigDecimal(r[1]), r[2]));
        } catch (RuntimeException e) {
            bad.add(String.join(",", r) + " -> " + e.getMessage());
        }
    }
    return new BatchResult(ok, bad);
}
```

```python
# app/concept/_01core_01principles/general.py
@dataclass(frozen=True)
class FailFastOrder:
    id: str
    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        """Invalid objects cannot exist; explicit raises survive `python -O` (asserts don't)."""
        if self.amount <= 0:
            raise ValueError(f"amount must be > 0, got {self.amount}")
        if not isinstance(self.currency, str) or len(self.currency) != 3:
            raise ValueError(f"currency must be ISO-4217, got {self.currency!r}")


def validate_batch(rows: Iterable[tuple[str, str, str]]) -> BatchResult:
    """Per-record fail fast: reject with a reason, continue the batch (Databricks job, Kafka consumer)."""
    result = BatchResult([], [])
    for row in rows:
        try:
            result.accepted.append(FailFastOrder(row[0], Decimal(row[1]), row[2]))
        except (ValueError, ArithmeticError) as e:
            result.quarantined.append(f"{','.join(row)} -> {e}")
    return result
```

- Python violation: `FailFastViolationOrder` (accepts `-5` and `None`)
- Demo: `FailFast.demo()` / `failfast_demo()`; batch of 3 → 1 accepted, 2 quarantined
- Use at every trust boundary (Hypertext Transfer Protocol (HTTP) input, files, config)

### 2.3 Catch

Fail fast per record, not per system — one bad row must not kill a million-row job.

→ Fail fast read as "crash everything".  
⇒ One bad row kills a 1M-row batch.  
→ Fail fast per record (reject, quarantine, Dead-Letter Queue (DLQ)); degrade gracefully per system.

→ Startup fails when an *optional* dependency is briefly down.  
⇒ Crash loops across a fleet during a dependency blip.  
→ Fail startup on invalid config; tolerate unavailable optional dependencies with retries and health checks.

→ Using `assert` as the guard.  
⇒ Java disables asserts by default; `python -O` strips them.  
→ Use explicit checks that raise.

- 🗣 "Fail fast per record, degrade gracefully per system."

## 3. Principle Of Least Astonishment

A component behaves the way its name, signature, and ecosystem lead readers to expect.

### 3.1 Idea

- Behavior matches what name and context suggest
- Running example (`LeastAstonishment`)
  - Violation: `getDiscount()` that writes an audit row
  - Python violation: `def add(item, items=[])` shares one list
  - Real Java Development Kit (JDK) trap: `List<Integer>.remove(1)` removes index 1, not value 1
  - Fix: names that reveal side effects; `None` defaults; explicit `remove(Integer.valueOf(1))`
- **Mechanism**
  - Readers predict behavior from the call site ⇒ fewer wrong assumptions

### 3.2 Code

The Java demo shows a getter with hidden writes; the Python demo shows the mutable-default trap.

```java
// concept/_01core_01principles/general/LeastAstonishment.java
/** Violation: a getter with a hidden side effect; calling it twice writes twice. */
public static BigDecimal getDiscount(String customerId, List<String> audit) {   // LeastAstonishment.Violation
    audit.add("discount looked up for " + customerId);
    return customerId.startsWith("vip") ? new BigDecimal("0.10") : BigDecimal.ZERO;
}

/** Fix: pure — the name promises a value and nothing else. */
public static BigDecimal discountFor(String customerId) {
    return customerId.startsWith("vip") ? new BigDecimal("0.10") : BigDecimal.ZERO;
}
/** The side effect is in the name. */
public static void recordDiscountAudit(String customerId, List<String> audit) {
    audit.add("discount applied for " + customerId);
}

// JDK trap
ids.remove(1);                       // removes index 1 (value 2), not value 1
ids2.remove(Integer.valueOf(1));     // removes value 1
```

```python
# app/concept/_01core_01principles/general.py
def pola_violation_add(item: str, items: list[str] = []) -> list[str]:  # noqa: B006 - the point of the demo
    """Mutable default is created once, so every call without `items` shares one list."""
    items.append(item)
    return items


def pola_add(item: str, items: list[str] | None = None) -> list[str]:
    """None default: a fresh list per call, as readers expect."""
    result = [] if items is None else items
    result.append(item)
    return result
```

- Demo: `LeastAstonishment.demo()` / `pola_demo()`
- Use when naming any method with side effects and choosing defaults

### 3.3 Catch

Astonishment is audience-relative.

→ Astonishment is audience-relative.  
⇒ Python properties surprise Java readers; Java getters look odd in Python.  
→ Follow the ecosystem's and the codebase's conventions over personal taste.

- 🗣 "If a reader must open the method to know what it does, the name failed."
