# 01core.01principles.07soc-cohesion Separation Of Concerns And Cohesion

> Keep each concern in its own part, strong inside a module and thin between modules.

## Index

- [1. Separation Of Concerns](#1-separation-of-concerns)
  - [1.1 Idea](#11-idea) · [1.2 Code](#12-code) · [1.3 Catch](#13-catch)
- [2. High Cohesion Low Coupling](#2-high-cohesion-low-coupling)
  - [2.1 Idea](#21-idea) · [2.2 Code](#22-code) · [2.3 Catch](#23-catch)

Part B, general principles (Java + Python). Back to [00index](00index.md).

## 1. Separation Of Concerns

Parsing, rules, persistence and logging live apart so each can change and be tested alone.

### 1.1 Idea

- Each part handles one concern (Dijkstra, 1974)
  - Hypertext Transfer Protocol (HTTP)
  - rules
  - persistence
  - logging
- Single Responsibility Principle (SRP) is Separation of Concerns (SoC) applied at class level, measured by actor ([01srp](01srp.md))
- Running example (`SeparationOfConcerns`)
  - Violation: a handler that parses input, applies discount, builds Structured Query Language (SQL), and logs
  - Fix: `parse` → `DiscountRule` → `OrderSink` port, each separately testable
- **Mechanism**
  - Reason about and change one concern at a time

### 1.2 Code

Identical results; only the fix lets you test the discount with two `BigDecimal`s.

```java
// concept/_01core_01principles/general/SeparationOfConcerns.java
/** Violation: input format, business rule, SQL and logging tangled; each change risks the others. */
public static String handle(String raw, List<String> sqlLog) {   // SeparationOfConcerns.Violation.handle
    String[] parts = raw.split(",");                                   // parsing
    BigDecimal amount = new BigDecimal(parts[1].trim());
    if (amount.compareTo(new BigDecimal("100")) >= 0) {                // business rule
        amount = amount.multiply(new BigDecimal("0.9"));
    }
    sqlLog.add("INSERT INTO orders VALUES ('" + parts[0] + "', " + amount + ")"); // persistence (and injectable)
    System.out.println("handled " + parts[0]);                         // logging
    return parts[0] + "=" + amount;
}

// Fix: one concern per piece
public static OrderRequest parse(String raw) { /* parsing only; rejects malformed input */ }

/** Business concern only: testable with plain values. */
public static final class DiscountRule {
    public BigDecimal apply(BigDecimal amount) {
        return amount.compareTo(new BigDecimal("100")) >= 0 ? amount.multiply(new BigDecimal("0.9")) : amount;
    }
}

/** Persistence concern behind a port; the adapter would use bound parameters. */
public interface OrderSink { void save(String id, BigDecimal amount); }

/** Coordinator: wires concerns, owns none of their rules. */
public String handle(String raw) {                 // SeparationOfConcerns.Fix.OrderHandler.handle
    OrderRequest req = parse(raw);
    BigDecimal amount = discount.apply(req.amount());
    sink.save(req.id(), amount);
    return req.id() + "=" + amount;
}
```

```python
# app/concept/_01core_01principles/general.py
def soc_violation_handle(raw: str, sql_log: list[str]) -> str:
    """Parsing, business rule, SQL and logging tangled together."""
    order_id, amount_s = raw.split(",")
    amount = Decimal(amount_s.strip())
    if amount >= 100:
        amount *= Decimal("0.9")
    sql_log.append(f"INSERT INTO orders VALUES ('{order_id}', {amount})")  # string SQL: injectable
    print(f"handled {order_id}")
    return f"{order_id}={amount}"


@dataclass
class SocOrderHandler:
    """Coordinator: wires concerns, owns none of their rules."""

    discount: DiscountRule
    sink: OrderSink  # Protocol port

    def handle(self, raw: str) -> str:
        req = parse_order(raw)
        amount = self.discount.apply(req.amount)
        self.sink.save(req.id, amount)
        return f"{req.id}={amount}"
```

- Demo: `SeparationOfConcerns.demo()` / `soc_demo()`
- Use whenever a unit mixes I/O format, rules and storage

### 1.3 Catch

Concerns are not only layers; package by feature first.

→ Concerns read as technical layers only.  
⇒ One feature is scattered across controller/service/repo/dto packages.  
→ Package by feature (vertical slice) first, layers inside it.

→ Cross-cutting concerns (tx, security, metrics) don't fit any layer.  
⇒ Copied into every method.  
→ Use Aspect-Oriented Programming (AOP), middleware, or decorators ([12aop-proxy](12aop-proxy.md)).

- 🗣 "Separate concerns so each can change and be tested alone."

## 2. High Cohesion Low Coupling

Elements that change together live together; modules know little about each other.

### 2.1 Idea

- **Cohesion**: how strongly elements inside a module belong together
- **Coupling**: how much a module knows about others
  - Constantine & Yourdon, *Structured Design* (1979)
- Running example (`CohesionCoupling`)
  - Violation: `OrderUtils` with `formatDate`, `calcTax`, `postToSlack`
    - Code version: `formatDate`, `shippingCost`, `slackMessage`
  - Callers reach into `Order` internals
  - Fix: `ShippingQuote` owns the zip-code rule and exposes `quoteFor(order)`
- **Mechanism**
  - Changes stay inside one module
  - Fewer cross-module edits per feature

### 2.2 Code

Same quote; in the fix an `Address` refactor touches `Order` only.

```java
// concept/_01core_01principles/general/CohesionCoupling.java
/** Violation: unrelated helpers; the shipping rule knows the full Order -> Customer -> Address shape. */
public static final class OrderUtils {             // CohesionCoupling.Violation.OrderUtils
    public static String formatDate(LocalDate d) { return d.toString(); }
    public static String slackMessage(String text) { return ":package: " + text; }
    public static BigDecimal shippingCost(Order order) {
        String zip = order.customer().address().zip();
        return zip.startsWith("9") ? new BigDecimal("15") : new BigDecimal("8");
    }
}

// Fix: Order hides how the zip is stored; callers ask for what they need.
public record Order(String id, Customer customer, BigDecimal weightKg) {   // CohesionCoupling.Fix.Order
    public String shippingZip() { return customer.address().zip(); }
}

/** Cohesive: every field and method is about quoting shipping. */
public static final class ShippingQuote {          // CohesionCoupling.Fix.ShippingQuote
    private final BigDecimal westCoast;
    private final BigDecimal standard;

    public BigDecimal quoteFor(Order order) {
        return order.shippingZip().startsWith("9") ? westCoast : standard;
    }
}
```

```python
# app/concept/_01core_01principles/general.py
@dataclass(frozen=True)
class ShipOrder:
    id: str
    customer: Customer

    def shipping_zip(self) -> str:
        """Hides where the zip lives; callers ask for what they need."""
        return self.customer.address.zip


@dataclass(frozen=True)
class ShippingQuote:
    """Cohesive: everything here is about quoting shipping."""

    west_coast: Decimal
    standard: Decimal

    def quote_for(self, order: ShipOrder) -> Decimal:
        return self.west_coast if order.shipping_zip().startswith("9") else self.standard
```

- Violation in Python: `CohesionViolationUtils` (`format_date`, `slack_message`, `shipping_cost`)
- Demo: `CohesionCoupling.demo()` / `cohesion_demo()`
- Use co-change history to decide what belongs together

### 2.3 Catch

Zero coupling is impossible; make the remaining coupling explicit and typed.

→ Coupling "removed" by switching from typed calls to events, maps, or strings.  
⇒ The coupling is still there, now invisible: a renamed field breaks a consumer at runtime.  
→ Coupling moves, it never vanishes; keep it explicit (schemas, contract tests).

→ Judging cohesion by naming instead of evidence.  
⇒ Modules that look tidy still change together.  
→ Use co-change data (`git log` files edited together) to find real seams.

- 🗣 "Cohesion is what changes together; coupling is what breaks together."
