# Design Principles

- **In plain words:** habits that keep code cheap to change: keep related things together, keep unrelated things apart, and don't build more than you need.
- 13 general principles beyond SOLID, in five groups, each with Java + Python code and its catch
- Siblings: [SOLID](solid.md) · [Design patterns](1design-patterns.md) · [Spring](spring.md) · [Spring Boot](spring-boot.md)

## Index

- [1. One-Minute Version](#1-one-minute-version)
- [2. Map](#2-map)
- [3. Cheat Sheet](#3-cheat-sheet)
- [4. Don't Repeat Yourself (DRY)](#4-dont-repeat-yourself-dry)
  - [4.1 Idea](#41-idea)
  - [4.2 Code](#42-code)
  - [4.3 Catch](#43-catch)
- [5. Keep It Simple (KISS)](#5-keep-it-simple-kiss)
  - [5.1 Idea](#51-idea)
  - [5.2 Code](#52-code)
  - [5.3 Catch](#53-catch)
- [6. You Aren't Gonna Need It (YAGNI)](#6-you-arent-gonna-need-it-yagni)
  - [6.1 Idea](#61-idea)
  - [6.2 Code](#62-code)
  - [6.3 Catch](#63-catch)
- [7. Separation Of Concerns](#7-separation-of-concerns)
  - [7.1 Idea](#71-idea)
  - [7.2 Code](#72-code)
  - [7.3 Catch](#73-catch)
- [8. High Cohesion Low Coupling](#8-high-cohesion-low-coupling)
  - [8.1 Idea](#81-idea)
  - [8.2 Code](#82-code)
  - [8.3 Catch](#83-catch)
- [9. Composition Over Inheritance](#9-composition-over-inheritance)
  - [9.1 Idea](#91-idea)
  - [9.2 Code](#92-code)
  - [9.3 Catch](#93-catch)
- [10. Program To An Interface](#10-program-to-an-interface)
  - [10.1 Idea](#101-idea)
  - [10.2 Code](#102-code)
  - [10.3 Catch](#103-catch)
- [11. Encapsulate What Varies](#11-encapsulate-what-varies)
  - [11.1 Idea](#111-idea)
  - [11.2 Code](#112-code)
  - [11.3 Catch](#113-catch)
- [12. Law Of Demeter](#12-law-of-demeter)
  - [12.1 Idea](#121-idea)
  - [12.2 Code](#122-code)
  - [12.3 Catch](#123-catch)
- [13. Tell Dont Ask](#13-tell-dont-ask)
  - [13.1 Idea](#131-idea)
  - [13.2 Code](#132-code)
  - [13.3 Catch](#133-catch)
- [14. Command Query Separation](#14-command-query-separation)
  - [14.1 Idea](#141-idea)
  - [14.2 Code](#142-code)
  - [14.3 Catch](#143-catch)
- [15. Fail Fast](#15-fail-fast)
  - [15.1 Idea](#151-idea)
  - [15.2 Code](#152-code)
  - [15.3 Catch](#153-catch)
- [16. Principle Of Least Astonishment](#16-principle-of-least-astonishment)
  - [16.1 Idea](#161-idea)
  - [16.2 Code](#162-code)
  - [16.3 Catch](#163-catch)
- [17. When To Use Or Not](#17-when-to-use-or-not)
- [18. Design Rules](#18-design-rules)
- [19. Tensions Between Principles](#19-tensions-between-principles)
- [20. Failure Modes](#20-failure-modes)
- [21. Interview Questions](#21-interview-questions)
- [22. Code Map](#22-code-map)

---

## 1. One-Minute Version

Principles are heuristics for one goal: lower the cost of the next change.

- **What**
  - Principles are heuristics for one goal: lower the cost of the next change
  - They are not laws; each one trades indirection for flexibility
- **Why**
  - Most cost of a long-lived service is change, not first delivery
  - Change is cheap when it touches one place and breaks nothing far away
- **How** (two forces + two brakes)
  - Raise cohesion: keep things that change together, together
    - Single Responsibility Principle (SRP), Separation of Concerns (SoC), Interface Segregation Principle (ISP), encapsulate what varies
  - Lower coupling: depend on stable contracts, not details
    - Dependency Inversion Principle (DIP), Open-Closed Principle (OCP), interfaces, Law of Demeter (LoD), composition
  - Brakes: Keep It Simple (KISS) and You Aren't Gonna Need It (YAGNI) stop you paying for change that never comes
  - Spring = these ideas built into a framework
    - Dependency Injection (DI) = DIP by container
    - Aspect-Oriented Programming (AOP) = SoC for cross-cutting code
- **Catch**
  - Every principle over-applied creates its own smell
  - SRP → class explosion
  - Don't Repeat Yourself (DRY) → wrong shared abstraction
  - OCP → speculative plugin points
- 🗣 "Principles are a cost model, not a checklist: I apply one when I can name the change it makes cheaper."

## 2. Map

What every principle is really for.

```text
                 cost of the next change
                           |
          +----------------+----------------+
          |                                 |
   raise COHESION                    lower COUPLING
   SRP, SoC, ISP,                    DIP, OCP, program-to-interface,
   encapsulate what varies           LoD, tell-don't-ask, composition
          |                                 |
          +----------------+----------------+
                           |
   correctness guards: LSP, CQS, fail fast, least astonishment
                           |
   brakes on over-design:  KISS, YAGNI  (and DRY used carefully)
                           |
   Spring = the same ideas in a framework:
     IoC/DI ................... DIP done by a container
     AOP ...................... SoC for cross-cutting concerns
     auto-config .............. convention over configuration
     @ConfigurationProperties . encapsulate what varies per env
     JdbcTemplate ............. template method + callbacks (DRY)
```

Two forces (cohesion up, coupling down) do the work; guards keep it correct and brakes keep it cheap.

## 3. Cheat Sheet

**Brakes and structure**

| Principle | One line | Smell when violated | 🗣 line to say aloud |
|---|---|---|---|
| [Don't Repeat Yourself (DRY)](#4-dont-repeat-yourself-dry) | One authoritative home per piece of knowledge | Same rule edited in 3 places, one forgotten | "DRY is about knowledge, not identical-looking text." |
| [Keep It Simple (KISS)](#5-keep-it-simple-kiss) | Simplest design that meets real requirements | Generic engine for a 5-line rule | "Simple means fewer moving parts, not fewer requirements handled." |
| [You Aren't Gonna Need It (YAGNI)](#6-you-arent-gonna-need-it-yagni) | Do not build what no requirement needs yet | Plugin system with one plugin | "YAGNI covers features, not things that are expensive to retrofit." |
| [Separation of Concerns (SoC)](#7-separation-of-concerns) | Each part handles one concern | Controller that parses, prices, writes Structured Query Language (SQL) and logs | "Separate concerns so each can change and be tested alone." |
| [High Cohesion, Low Coupling](#8-high-cohesion-low-coupling) | Strong inside, thin between | `Utils` grab-bag; edits ripple across modules | "Cohesion is what changes together; coupling is what breaks together." |

**Contracts and objects**

| Principle | One line | Smell when violated | 🗣 line to say aloud |
|---|---|---|---|
| [Composition Over Inheritance](#9-composition-over-inheritance) | Assemble behavior from parts, not deep subclassing | `LoggingRetryingEmailNotifier` class tree | "Inheritance is the tightest coupling Java offers; I use it only for real is-a." |
| [Program to an Interface](#10-program-to-an-interface) | Depend on the narrowest contract you need | Params typed `ArrayList`, `HashMap` | "Accept the widest type I can handle, return the most useful specific one." |
| [Encapsulate What Varies](#11-encapsulate-what-varies) | Wall off the axis of change | Region-specific fee logic inside checkout | "Find the part that changes, put a stable interface in front of it." |
| [Law of Demeter (LoD)](#12-law-of-demeter) | Talk only to your direct collaborators | `order.getCustomer().getWallet().getBalance()` | "Dots are fine on data and fluent Application Programming Interfaces (APIs); LoD is about behavior-rich objects." |
| [Tell, Don't Ask](#13-tell-dont-ask) | Tell an object to act; don't pull its state and decide | `if (a.getBalance() >= x) a.setBalance(...)` | "Put the decision next to the data that guards the invariant." |

**Correctness guards**

| Principle | One line | Smell when violated | 🗣 line to say aloud |
|---|---|---|---|
| [Command-Query Separation (CQS)](#14-command-query-separation) | A method changes state or returns data, not both | Getter that increments a counter | "Queries must be safe to call twice — except atomic ops where splitting causes races." |
| [Fail Fast](#15-fail-fast) | Reject bad input at the first boundary | Null blows up three services later | "Fail fast per record, degrade gracefully per system." |
| [Principle of Least Astonishment (POLA)](#16-principle-of-least-astonishment) | Behavior matches what name and context suggest | `get` that writes; mutable default args | "If a reader must open the method to know what it does, the name failed." |

## 4. Don't Repeat Yourself (DRY)

- **In plain words:** each business rule lives in one place, so changing it is one edit, not a hunt through three copies.

Every business rule should have exactly one place where it is defined.

### 4.1 Idea

- "Every piece of knowledge must have a single, unambiguous, authoritative representation"
  - Hunt & Thomas, *The Pragmatic Programmer* (1999)
- About knowledge (rules, schemas), not about similar-looking text
- Running example (`Dry`)
  - Violation: tax rate `0.08` hard-coded in checkout, invoice and refund
  - Fix: one `TaxPolicy` used by all three
- **Mechanism**
  - One change site per business rule ⇒ no drift between copies

### 4.2 Code

The violation's copies already drifted (`0.08` vs `0.0825`); the look-alike validators are kept apart on purpose.

```java
// concept/_01core_01principles/general/Dry.java
// Violation: the same business rule in two places
public static final class Checkout {               // Dry.Violation.Checkout
    public BigDecimal tax(BigDecimal subtotal) {
        return subtotal.multiply(new BigDecimal("0.08")).setScale(2, RoundingMode.HALF_UP);
    }
}
/** Someone updated the rate here only: invoice and checkout now disagree. */
public static final class Invoice {                // Dry.Violation.Invoice
    public BigDecimal tax(BigDecimal subtotal) {
        return subtotal.multiply(new BigDecimal("0.0825")).setScale(2, RoundingMode.HALF_UP);
    }
}

// Fix: the knowledge "how much tax" lives here only.
public record TaxPolicy(BigDecimal rate) {         // Dry.Fix.TaxPolicy
    public BigDecimal tax(BigDecimal subtotal) {
        return subtotal.multiply(rate).setScale(2, RoundingMode.HALF_UP);
    }
}

// Look alike today, different reasons to change: the API owner may tighten limits,
// the backfill owner must accept historical rows. Merging them would couple two teams.
public static boolean validApiAmount(BigDecimal amount) {
    return amount.signum() > 0 && amount.compareTo(new BigDecimal("10000")) <= 0;
}
public static boolean validBackfillAmount(BigDecimal amount) {
    return amount.signum() > 0 && amount.compareTo(new BigDecimal("10000")) <= 0;
}
```

```python
# app/concept/_01core_01principles/general.py
def dry_violation_invoice_tax(subtotal: Decimal) -> Decimal:
    """Copy that drifted: someone changed the rate here only."""
    return (subtotal * Decimal("0.0825")).quantize(CENT, ROUND_HALF_UP)

@dataclass(frozen=True)
class TaxPolicy:
    """Single source of truth for the tax rule."""

    rate: Decimal

    def tax(self, subtotal: Decimal) -> Decimal:
        return (subtotal * self.rate).quantize(CENT, ROUND_HALF_UP)

def valid_api_amount(amount: Decimal) -> bool:
    """Looks like valid_backfill_amount, but has a different owner and reason to change: keep separate."""
    return Decimal("0") < amount <= Decimal("10000")
```

- Demo: `Dry.demo()` / `dry_demo()` prints drifted copies vs one policy
- Use for business rules, schemas, constants with one owner

### 4.3 Catch

"Duplication is far cheaper than the wrong abstraction" when owners differ.

→ Two blocks look identical but encode different knowledge (Application Programming Interface (API) validation vs batch backfill validation).  
⇒ A shared helper grows boolean flags; a change for one caller breaks the other.  
→ Merge only when the *reason to change* is the same (Sandi Metz).

→ DRY across services via a shared Data Transfer Object (DTO) / utils library.  
⇒ Every service must redeploy in lockstep; the library becomes a distributed monolith.  
→ Share contracts (schemas, OpenAPI), not implementation; tolerate copies of small helpers.

→ DRY applied to tests.  
⇒ Clever shared fixtures hide what each test checks.  
→ Prefer readable, slightly repetitive tests (Descriptive And Meaningful Phrases, DAMP).

- 🗣 "DRY is about knowledge, not identical-looking text."

## 5. Keep It Simple (KISS)

- **In plain words:** pick the simplest design that solves the real problem today. Every extra moving part is one more thing to understand and debug.

Pick the simplest design that still meets the real requirements.

### 5.1 Idea

- The simplest design that meets the *real* requirements
- Running example (`Kiss`)
  - Violation: a generic reflection-based rule engine to compute a shipping fee
  - Fix: a five-line function with two `if`s
- **Mechanism**
  - Fewer moving parts ⇒ less to read, fewer failure modes, faster onboarding

### 5.2 Code

Both compute the same fee; one needs a mental interpreter.

```java
// concept/_01core_01principles/general/Kiss.java
// Violation: stringly-typed engine; typos fail at runtime, readers must simulate it to know the fee.
public record Rule(String field, String op, BigDecimal threshold, BigDecimal fee) { }

public BigDecimal evaluate(Map<String, Object> facts) {   // Kiss.Violation.RuleEngine.evaluate
    BigDecimal fee = BigDecimal.ZERO;
    for (Rule r : rules) {
        BigDecimal value = new BigDecimal(String.valueOf(facts.get(r.field())));
        boolean hit = switch (r.op()) {
            case "gt" -> value.compareTo(r.threshold()) > 0;
            case "eq" -> value.compareTo(r.threshold()) == 0;
            default -> throw new IllegalArgumentException("op " + r.op());
        };
        if (hit) fee = fee.add(r.fee());
    }
    return fee;
}

// Fix: readable in one glance; still validates input (simple, not simplistic).
public static BigDecimal shippingFee(BigDecimal weightKg, boolean express) {   // Kiss.Fix.shippingFee
    if (weightKg.signum() < 0) {
        throw new IllegalArgumentException("weight must be >= 0");
    }
    BigDecimal fee = weightKg.compareTo(new BigDecimal("5")) > 0 ? new BigDecimal("12") : new BigDecimal("5");
    return express ? fee.add(new BigDecimal("10")) : fee;
}
```

```python
# app/concept/_01core_01principles/general.py
@dataclass
class KissViolationRuleEngine:
    """Stringly-typed engine for a two-rule fee; readers must simulate it."""

    rules: list[KissRule]

    def evaluate(self, facts: dict[str, str]) -> Decimal:
        ops: dict[str, Callable[[Decimal, Decimal], bool]] = {"gt": lambda a, b: a > b, "eq": lambda a, b: a == b}
        return sum((r.fee for r in self.rules if ops[r.op](Decimal(facts[r.fact]), r.threshold)), Decimal("0"))

def shipping_fee(weight_kg: Decimal, express: bool) -> Decimal:
    """Direct code; still validates input (simple, not simplistic)."""
    if weight_kg < 0:
        raise ValueError("weight must be >= 0")
    fee = Decimal("12") if weight_kg > 5 else Decimal("5")
    return fee + Decimal("10") if express else fee
```

- Demo: `Kiss.demo()` / `kiss_demo()`
- Use when rules are few and owned by engineers

### 5.3 Catch

Simple is not simplistic; keep the essential requirements.

→ "Simple" code that drops real requirements (no retry, no idempotency, no timeout).  
⇒ Simplistic, not simple; complexity reappears as incidents.  
→ Keep the essential complexity, cut the accidental (Brooks, "No Silver Bullet", 1986).

→ One giant function called "simple".  
⇒ Easy to write, hard to change.  
→ Simple = few interleaved concerns, not few files.

→ Business users must edit hundreds of rules without deploys.  
⇒ Five lines of code would mean a deploy per rule change.  
→ There an engine may be essential complexity.

- 🗣 "Simple means fewer moving parts, not fewer requirements handled."

## 6. You Aren't Gonna Need It (YAGNI)

- **In plain words:** don't build features or hooks for needs nobody has yet. Build them when the need is real.

Do not build a feature or abstraction until a real requirement needs it.

### 6.1 Idea

- Don't build a feature or abstraction until a requirement needs it (Extreme Programming)
- Running example (`Yagni`)
  - Violation: a `PaymentProviderPlugin` Service Provider Interface (SPI) with config-driven class loading, for one provider
  - Fix: a concrete `CardGateway`; extract an interface when provider two appears
- **Mechanism**
  - Saves build cost, carrying cost, and the cost of guessing wrong (Fowler, "Yagni", 2015)

### 6.2 Code

The fix is concrete, but keeps the retrofit-expensive part: the idempotency key.

```java
// concept/_01core_01principles/general/Yagni.java
/** Violation: config-driven class loading; typos fail at runtime, IDE can't follow it, one plugin exists. */
public PaymentProviderPlugin load(String className) {   // Yagni.Violation.PluginLoader.load
    try {
        return (PaymentProviderPlugin) Class.forName(className).getDeclaredConstructor().newInstance();
    } catch (ReflectiveOperationException e) {
        throw new IllegalStateException("cannot load plugin " + className, e);
    }
}

/** Fix: concrete class; the idempotency key is kept because adding it later changes the public API. */
public static final class CardGateway {            // Yagni.Fix.CardGateway
    private final Map<String, String> processed = new ConcurrentHashMap<>();

    public String charge(String idempotencyKey, BigDecimal amount) {
        // a retry with the same key returns the first result: charged once
        return processed.computeIfAbsent(idempotencyKey, k -> "charge-" + k + "-" + amount);
    }
}
```

```python
# app/concept/_01core_01principles/general.py
class YagniViolationPluginLoader:
    """Dynamic loading for a single provider: typos fail at runtime, IDEs can't follow it."""

    def load(self, path: str) -> YagniOnlyProvider:
        module_name, _, cls_name = path.partition(":")
        cls = getattr(importlib.import_module(module_name), cls_name)
        return cls()

@dataclass
class CardGateway:
    """Concrete now; the idempotency key is kept because adding it later breaks the public API."""

    processed: dict[str, str] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def charge(self, idempotency_key: str, amount: Decimal) -> str:
        with self._lock:  # check + write as one step
            if idempotency_key not in self.processed:
                self.processed[idempotency_key] = f"charge-{idempotency_key}-{amount}"
            return self.processed[idempotency_key]
```

- Demo: `Yagni.demo()` / `yagni_demo()`; a retry with the same key charges once
- Use YAGNI for features and extension points

### 6.3 Catch

Retrofit-expensive properties are NOT covered by YAGNI — keep them now.

→ YAGNI applied to things that are expensive to retrofit.  
⇒ Missing idempotency keys, tenant identifiers (IDs), schema versioning, auth, observability — each costs a migration later.  
→ YAGNI assumes refactoring is cheap; it is not across public APIs, persisted data, or other teams.

- Tension with [Open-Closed Principle (OCP)](solid.md#44-catch): see [Tensions Between Principles](#19-tensions-between-principles)
- 🗣 "YAGNI covers features, not things that are expensive to retrofit."

## 7. Separation Of Concerns

- **In plain words:** each part of the code does one kind of job (web, rules, storage, logging), so you can change or test one without touching the others.

Parsing, rules, persistence and logging live apart so each can change and be tested alone.

### 7.1 Idea

- Each part handles one concern (Dijkstra, 1974)
  - Hypertext Transfer Protocol (HTTP)
  - rules
  - persistence
  - logging
- Single Responsibility Principle (SRP) is Separation of Concerns (SoC) applied at class level, measured by actor ([Single Responsibility Principle (SRP)](solid.md#3-single-responsibility-principle-srp))
- Running example (`SeparationOfConcerns`)
  - Violation: a handler that parses input, applies discount, builds Structured Query Language (SQL), and logs
  - Fix: `parse` → `DiscountRule` → `OrderSink` port, each separately testable
- **Mechanism**
  - Reason about and change one concern at a time

### 7.2 Code

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

### 7.3 Catch

Concerns are not only layers; package by feature first.

→ Concerns read as technical layers only.  
⇒ One feature is scattered across controller/service/repo/dto packages.  
→ Package by feature (vertical slice) first, layers inside it.

→ Cross-cutting concerns (tx, security, metrics) don't fit any layer.  
⇒ Copied into every method.  
→ Use Aspect-Oriented Programming (AOP), middleware, or decorators ([Aspect-Oriented Programming (AOP) And Proxies](spring.md#6-aspect-oriented-programming-aop-and-proxies)).

- 🗣 "Separate concerns so each can change and be tested alone."

## 8. High Cohesion Low Coupling

- **In plain words:** things that change together live together, and modules know as little as possible about each other's insides.

Elements that change together live together; modules know little about each other.

### 8.1 Idea

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

### 8.2 Code

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

### 8.3 Catch

Zero coupling is impossible; make the remaining coupling explicit and typed.

→ Coupling "removed" by switching from typed calls to events, maps, or strings.  
⇒ The coupling is still there, now invisible: a renamed field breaks a consumer at runtime.  
→ Coupling moves, it never vanishes; keep it explicit (schemas, contract tests).

→ Judging cohesion by naming instead of evidence.  
⇒ Modules that look tidy still change together.  
→ Use co-change data (`git log` files edited together) to find real seams.

- 🗣 "Cohesion is what changes together; coupling is what breaks together."

## 9. Composition Over Inheritance

- **In plain words:** build behavior by plugging small parts together, like Lego, instead of stacking deep class hierarchies.

Build behavior by wrapping small parts instead of growing a class tree.

### 9.1 Idea

- "Favor object composition over class inheritance" (Gang of Four (GoF), 1994)
- Running example (`CompositionOverInheritance`)
  - Violation: `EmailNotifier` → `RetryingEmailNotifier` → `LoggingRetryingEmailNotifier`
  - n optional features ⇒ up to 2ⁿ subclasses
  - Fix: decorators `Retrying(Logging(Email))` around a `Notifier` interface
- **Mechanism**
  - Behavior is assembled at runtime from small parts
  - No fragile base class
    - A subclass cannot depend on the base's self-calls
    - Bloch, *Effective Java*, `InstrumentedHashSet` example

### 9.2 Code

The same parts composed in two orders: log lines count requests vs attempts.

```java
// concept/_01core_01principles/general/CompositionOverInheritance.java
// Violation: retry is welded to email; SMS needs its own RetryingSmsNotifier.
public static class RetryingEmailNotifier extends EmailNotifier { /* loops super.send() up to 3 times */ }

/** Third level: depends on both parents' internals (fragile base class). */
public static class LoggingRetryingEmailNotifier extends RetryingEmailNotifier {
    public final List<String> log = new ArrayList<>();
    @Override
    public String send(String to, String msg) {
        log.add("send " + to);
        return super.send(to, msg);
    }
}

// Fix: small parts composed at runtime
public interface Notifier { String send(String to, String msg); }

/** Retry decorator reusing the shared full-jitter helper; only safe for idempotent sends. */
public static final class Retrying implements Notifier {   // CompositionOverInheritance.Fix.Retrying
    private final Notifier inner;
    private final Retry retry;   // shared/Retry

    public Retrying(Notifier inner, int maxAttempts) {
        this.inner = inner;
        this.retry = new Retry(maxAttempts, Duration.ofMillis(1), Duration.ofMillis(5));
    }
    public String send(String to, String msg) {
        return retry.call(() -> inner.send(to, msg), e -> e instanceof IllegalStateException);
    }
}

public static final class Logging implements Notifier {    // CompositionOverInheritance.Fix.Logging
    private final Notifier inner;
    private final List<String> log;
    public String send(String to, String msg) {
        log.add("send " + to);
        return inner.send(to, msg);
    }
}

// Order is chosen at wiring time:
new Logging(new Retrying(email, 3), log);   // log lines = requests
new Retrying(new Logging(email, log), 3);   // log lines = attempts
```

```python
# app/concept/_01core_01principles/general.py
class Notifier(Protocol):
    def send(self, to: str, msg: str) -> str: ...

@dataclass
class RetryingNotifier:
    """Retry decorator using the shared full-jitter helper; only for idempotent sends."""

    inner: Notifier
    max_attempts: int = 3

    def send(self, to: str, msg: str) -> str:
        return call_with_retry(lambda: self.inner.send(to, msg), lambda e: isinstance(e, TimeoutError),
                               max_attempts=self.max_attempts, base=0.001, cap=0.005)

@dataclass
class LoggingNotifier:
    inner: Notifier
    log: list[str] = field(default_factory=list)

    def send(self, to: str, msg: str) -> str:
        self.log.append(f"send {to}")
        return self.inner.send(to, msg)
```

- Python violation tree: `CompositionViolationEmail` → `...RetryingEmail` → `...LoggingRetryingEmail`
- `FlakyEmail(failures=2)` fails the first calls so retries are visible
- Demo: `CompositionOverInheritance.demo()` / `composition_demo()`
- Use when features combine freely (retry, logging, metrics, rate limit)

### 9.3 Catch

Decorator order is a contract; inheritance is still right for designed bases.

→ Composition everywhere.  
⇒ Long delegation chains and forwarding boilerplate in Java.  
→ Inheritance is right for a true is-a with a base *designed and documented for extension*.  
→ Examples: framework abstract classes, sealed data hierarchies.

→ Decorators wrapped in an unplanned order.  
⇒ Logging outside retry logs requests; inside it logs attempts.  
→ Treat the wiring order as part of the contract.

- 🗣 "Inheritance is the tightest coupling Java offers; I use it only for real is-a."

## 10. Program To An Interface

- **In plain words:** depend on what a thing can do (a `Collection`), not on exactly what it is (an `ArrayList`), so it can be swapped later.

Accept the widest type you can handle; return the most useful specific one.

### 10.1 Idea

- Depend on a supertype contract, not a concrete class (GoF)
- "Interface" = the contract, not necessarily the `interface` keyword
- Running example (`ProgramToInterface`)
  - Violation: `totalOf(ArrayList<Order>)` returns `HashMap`
  - Fix: `totalOf(Collection<Order>)` returns `Map`
  - Python takes `Iterable[Order]`, returns `Mapping`
- **Mechanism**
  - Callers bind to the narrowest contract ⇒ implementation swaps are invisible

### 10.2 Code

A caller holding an immutable `List` or `Set` must copy for the violation, not for the fix.

```java
// concept/_01core_01principles/general/ProgramToInterface.java
/** Violation: bound to concrete types on both sides. */
public static HashMap<String, BigDecimal> totalOf(ArrayList<Order> orders) { /* ... */ }

/** Fix: widest useful input, interface output; switching HashMap -> TreeMap breaks no caller. */
public static Map<String, BigDecimal> totalOf(Collection<Order> orders) {   // ProgramToInterface.Fix.totalOf
    Map<String, BigDecimal> totals = new TreeMap<>();
    for (Order o : orders) {
        totals.merge(o.customerId(), o.amount(), BigDecimal::add);
    }
    return totals;
}
```

```python
# app/concept/_01core_01principles/general.py
def total_of_violation(orders: list[AmountOrder]) -> dict[str, Decimal]:
    """Demands a list although it only iterates; tuples, sets and generators need a copy."""
    ...

def total_of(orders: Iterable[AmountOrder]) -> Mapping[str, Decimal]:
    """Widest input it can handle; read-only Mapping output leaves the implementation free."""
    totals: dict[str, Decimal] = {}
    for o in orders:
        totals[o.customer_id] = totals.get(o.customer_id, Decimal("0")) + o.amount
    return totals
```

- Demo: `ProgramToInterface.demo()` (from `List.of` and `Set.of`) / `interface_demo()` (from a generator)
- Use for parameters and return types of every public method

### 10.3 Catch

Interfaces don't state cost.

→ The interface does not express cost.  
⇒ `List.get(i)` is O(1) on `ArrayList`, O(n) on `LinkedList`; a loop becomes O(n²).  
→ The Java Development Kit (JDK) added the `RandomAccess` marker for this reason; document complexity in the contract.

→ A Python `Iterable` may be single-pass (a generator).  
⇒ Iterating twice silently yields nothing the second time.  
→ Iterate once, or accept `Collection` / `Sequence` when you need two passes.

→ Return types too narrow (`Iterable` when callers need size).  
⇒ Every caller copies into a list.  
→ Accept the widest type you can handle; return the most specific type that is useful.

- 🗣 "Accept the widest type I can handle, return the most useful specific one."

## 11. Encapsulate What Varies

- **In plain words:** find the part that keeps changing, put it behind a stable interface, and the rest of the code stops caring when it changes.

Find the part that changes and put a stable interface in front of it.

### 11.1 Idea

- Find the axis of change, put a stable interface in front of it
- The engine behind Open-Closed Principle (OCP; [Open-Closed Principle (OCP)](solid.md#4-open-closed-principle-ocp)) and the Strategy pattern
- Running example (`EncapsulateWhatVaries`)
  - Violation: region fee rules inline in checkout, edited every quarter
  - Fix: `FeePolicy` per region, selected by a map
- **Mechanism**
  - Volatile code is isolated
  - Stable code stops changing

### 11.2 Code

Same fees; the fix lets the rates come from config because `PercentFee` is data.

```java
// concept/_01core_01principles/general/EncapsulateWhatVaries.java
/** Violation: volatile rules mixed into stable checkout flow. */
public BigDecimal fee(String region, BigDecimal amount) {   // EncapsulateWhatVaries.Violation.Checkout.fee
    if (region.equals("US")) {
        return amount.multiply(new BigDecimal("0.03"));
    } else if (region.equals("EU")) {
        return amount.multiply(new BigDecimal("0.02")).add(new BigDecimal("0.25"));
    } else {
        return new BigDecimal("1.00");
    }
}

// Fix: the varying part, walled off.
public interface FeePolicy { BigDecimal fee(BigDecimal amount); }

public record PercentFee(BigDecimal rate, BigDecimal fixed) implements FeePolicy {
    public BigDecimal fee(BigDecimal amount) { return amount.multiply(rate).add(fixed); }
}

/** Stable part: checkout logic that does not change when fees do. */
public BigDecimal fee(String region, BigDecimal amount) {   // EncapsulateWhatVaries.Fix.Checkout.fee
    return policies.getOrDefault(region, fallback).fee(amount);
}
```

```python
# app/concept/_01core_01principles/general.py
class FeePolicy(Protocol):
    def fee(self, amount: Decimal) -> Decimal: ...

@dataclass(frozen=True)
class PercentFee:
    """Data, not code: rates can come from config."""

    rate: Decimal
    fixed: Decimal = Decimal("0")

    def fee(self, amount: Decimal) -> Decimal:
        return amount * self.rate + self.fixed

FEE_POLICIES: dict[str, FeePolicy] = {
    "US": PercentFee(Decimal("0.03")),
    "EU": PercentFee(Decimal("0.02"), Decimal("0.25")),
}

def checkout_fee(region: str, amount: Decimal, policies: Mapping[str, FeePolicy] = FEE_POLICIES) -> Decimal:
    """Stable part: unchanged when fees change."""
    return policies.get(region, FALLBACK_FEE).fee(amount)
```

- Python violation: `checkout_fee_violation`
- Demo: `EncapsulateWhatVaries.demo()` / `encapsulate_demo()`
- Use when one part changes on a different schedule than the rest

### 11.3 Catch

You must have observed the variation; abstracting a part that never changes is pure overhead.

→ Guessing the axis.  
⇒ Abstractions around stable parts, while the real change hits elsewhere.  
→ Encapsulate after observing change, not before.

→ Encapsulating as code what is really data.  
⇒ A deploy for every rate change.  
→ Rates and thresholds that business users edit belong in config or tables, not classes.

- 🗣 "Find the part that changes, put a stable interface in front of it."

## 12. Law Of Demeter

- **In plain words:** talk to your friends, not your friends' friends: `order.canPay()`, not `order.getCustomer().getWallet().getBalance()`.

A method should not depend on the structure of distant objects.

### 12.1 Idea

- A method talks only to (Lieberherr et al., 1988):
  - itself
  - its parameters
  - objects it creates
  - its fields
- "Only talk to your immediate friends"
- Running example (`LawOfDemeter`)
  - Violation: `order.customer().wallet().balance()` inside checkout
  - Fix: `order.canPay(amount)`; the order asks its own collaborators
- **Mechanism**
  - Callers don't depend on the structure of distant objects ⇒ internals can be restructured

### 12.2 Code

Same answer with and without reaching through objects.

```java
// concept/_01core_01principles/general/LawOfDemeter.java
/** Violation: knows the shape of three distant objects; moving wallet onto an Account breaks it. */
public boolean canPay(Order order, BigDecimal amount) {   // LawOfDemeter.Violation.Checkout.canPay
    return order.customer().wallet().balance().compareTo(amount) >= 0;
}

// Fix: each object asks only its own direct collaborator.
public static final class Wallet {
    public boolean covers(BigDecimal amount) { return balance.compareTo(amount) >= 0; }
}
public static final class Customer {
    public boolean canAfford(BigDecimal amount) { return wallet.covers(amount); }
}
public static final class Order {                  // LawOfDemeter.Fix.Order
    /** Checkout calls this only; the internal path can change freely. */
    public boolean canPay(BigDecimal amount) { return customer.canAfford(amount); }
}

// Allowed: a fluent chain over the same API is not a LoD violation.
long fluentOk = List.of(1, 2, 3).stream().filter(i -> i > 1).map(i -> i * 2).count();
```

```python
# app/concept/_01core_01principles/general.py
def lod_violation_can_pay(order: LodOrder, amount: Decimal) -> bool:
    """Reaches through three objects; a wallet refactor breaks every such caller."""
    return order.customer.wallet.balance >= amount

@dataclass(frozen=True)
class LodOrder:
    customer: LodCustomer

    def can_pay(self, amount: Decimal) -> bool:
        """Callers ask the order; the path to the wallet can change freely."""
        return self.customer.can_afford(amount)  # LodCustomer -> LodWallet.covers
```

- Demo: `LawOfDemeter.demo()` / `lod_demo()`
- Use for behavior-rich domain objects

### 12.3 Catch

Chains over plain data and fluent Application Programming Interfaces (APIs) are fine; Law of Demeter (LoD) targets behavior.

→ LoD read as "count the dots".  
⇒ Fluent builders, streams, and record navigation get wrapped for no gain.  
→ Chains that return the same type or plain data are fine; LoD targets behavior-rich objects.

→ Strict LoD on a middle object.  
⇒ It grows dozens of forwarding methods (wide interface).  
→ Pass the needed value in, or move the behavior to where the data is.

- 🗣 "Dots are fine on data and fluent APIs; LoD is about behavior-rich objects."

## 13. Tell Dont Ask

- **In plain words:** tell an object what to do instead of pulling its data out and deciding for it. The object that owns the data guards its rules.

Put the decision next to the data that guards the invariant.

### 13.1 Idea

- Tell an object what to do
- Don't pull its state and decide for it
- Running example (`TellDontAsk`)
  - Violation: service checks `wallet.balance() >= amount` then sets the new balance
  - Fix: `wallet.debit(amount)` enforces "no overdraft" inside
- **Mechanism**
  - The invariant lives in one place, next to the data that guards it

### 13.2 Code

The invariant moves into the wallet; the bypass via the setter is gone.

```java
// concept/_01core_01principles/general/TellDontAsk.java
/** Violation: the overdraft rule is here, and must be copied into every other caller. */
public boolean charge(Wallet wallet, BigDecimal amount) {   // TellDontAsk.Violation.PaymentService.charge
    if (wallet.getBalance().compareTo(amount) >= 0) {
        wallet.setBalance(wallet.getBalance().subtract(amount));   // anemic: any caller can set -100
        return true;
    }
    return false;
}

/** Fix: invariant guarded next to the data; synchronized so the check and the write are one step. */
public static final class Wallet {                 // TellDontAsk.Fix.Wallet
    private BigDecimal balance;

    public synchronized void debit(BigDecimal amount) {
        if (amount.signum() <= 0) {
            throw new IllegalArgumentException("amount must be > 0");
        }
        if (balance.compareTo(amount) < 0) {
            throw new InsufficientFunds("balance " + balance + " < " + amount);
        }
        balance = balance.subtract(amount);
    }

    /** A query for display is fine. */
    public synchronized BigDecimal balance() { return balance; }
}
```

```python
# app/concept/_01core_01principles/general.py
def tda_violation_charge(wallet: AnemicWallet, amount: Decimal) -> bool:
    """The overdraft rule lives in the caller and must be copied everywhere."""
    if wallet.balance >= amount:
        wallet.balance -= amount
        return True
    return False

class Wallet:
    """Invariant guarded next to the data; the lock makes check + write one step."""

    def debit(self, amount: Decimal) -> None:
        if amount <= 0:
            raise ValueError("amount must be > 0")
        with self._lock:
            if self._balance < amount:
                raise InsufficientFunds(f"balance {self._balance} < {amount}")
            self._balance -= amount

    @property
    def balance(self) -> Decimal:
        """A query for display is fine (CQS)."""
        return self._balance
```

- Demo: `TellDontAsk.demo()` / `tda_demo()`; overdraft of 100 is rejected
- Use for stateful domain objects with invariants

### 13.3 Catch

Queries for display are fine (Command-Query Separation, CQS); don't push I/O into entities.

→ Applied to reporting and display.  
⇒ Entities grow `printInvoice`, `toCsv`, `renderHtml`.  
→ Queries for display are fine (that is CQS's "query" side, [Command Query Separation](#14-command-query-separation)).

→ Everything pushed into entities.  
⇒ God entities that need mailers and repositories.  
→ Entities guard invariants; services orchestrate I/O.

→ Data pipelines (Spark, Databricks) are function-over-data, not objects.  
⇒ Tell-don't-ask does not apply to a DataFrame transform.  
→ Use it for stateful domain objects only.

- 🗣 "Put the decision next to the data that guards the invariant."

## 14. Command Query Separation

- **In plain words:** a method either changes something or answers a question, never both, so asking twice is always safe.

A method either changes state or returns data, not both.

### 14.1 Idea

- A method is one of (Meyer, 1988):
  - **command**: changes state, returns nothing
  - **query**: returns data, no side effects
- Running example (`Cqs`)
  - Violation: `nextOrderNumber()` that also increments the counter
  - Fix: `reserveNumber()` command + `peekNext()` query
- **Mechanism**
  - Queries are safe to repeat, cache, reorder, log, retry, call from a debugger

### 14.2 Code

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

### 14.3 Catch

Splitting an atomic read-modify-write creates a check-then-act race.

→ Splitting an atomic read-modify-write into query + command.  
⇒ Check-then-act race: two callers peek the same number.  
→ Keep atomic ops combined: `AtomicLong.incrementAndGet`, `stack.pop`, `INSERT ... RETURNING id`, DynamoDB `UpdateItem` with `ReturnValues`.

→ Command-Query Separation (CQS) confused with Command Query Responsibility Segregation (CQRS).  
⇒ Teams split databases when they only needed cleaner methods.  
→ CQS = method level; CQRS = separate read and write models (Greg Young).

- 🗣 "Queries must be safe to call twice — except atomic ops where splitting causes races."

## 15. Fail Fast

- **In plain words:** reject bad input loudly at the first door it reaches, instead of letting it travel and break something far away.

Detect and report an error at the point closest to its cause.

### 15.1 Idea

- Detect and report an error at the point closest to its cause (Shore, Institute of Electrical and Electronics Engineers (IEEE) Software, 2004)
- Running example (`FailFast`)
  - Violation: `Order` accepts a negative amount; a downstream job crashes hours later
  - Fix: validate in the record's compact constructor / dataclass `__post_init__`
  - Config validated at startup ([Externalized Configuration](spring-boot.md#4-externalized-configuration))
- **Mechanism**
  - Short distance between cause and symptom ⇒ cheap diagnosis
  - No corrupted state propagated

### 15.2 Code

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

### 15.3 Catch

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

## 16. Principle Of Least Astonishment

- **In plain words:** code does what its name suggests. A method called `get` never quietly writes to the database.

A component behaves the way its name, signature, and ecosystem lead readers to expect.

### 16.1 Idea

- Behavior matches what name and context suggest
- Running example (`LeastAstonishment`)
  - Violation: `getDiscount()` that writes an audit row
  - Python violation: `def add(item, items=[])` shares one list
  - Real Java Development Kit (JDK) trap: `List<Integer>.remove(1)` removes index 1, not value 1
  - Fix: names that reveal side effects; `None` defaults; explicit `remove(Integer.valueOf(1))`
- **Mechanism**
  - Readers predict behavior from the call site ⇒ fewer wrong assumptions

### 16.2 Code

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

### 16.3 Catch

Astonishment is audience-relative.

→ Astonishment is audience-relative.  
⇒ Python properties surprise Java readers; Java getters look odd in Python.  
→ Follow the ecosystem's and the codebase's conventions over personal taste.

- 🗣 "If a reader must open the method to know what it does, the name failed."

## 17. When To Use Or Not

Apply principles where change is frequent and boundaries are expensive; relax them where code is throwaway.

- **Apply firmly when**
  - Code is long-lived and changes often (core services, shared platform Application Programming Interfaces (APIs))
  - Several teams or many contributors touch it
  - The boundary is public or persisted (APIs, schemas, events) — retrofitting is expensive
  - Testing needs to run without real infrastructure (Dependency Inversion Principle (DIP), Dependency Injection (DI), ports)
- **Relax when**
  - Spikes, notebooks, one-off migrations, throwaway scripts
  - Stable code nobody has touched in a year
  - Only one variant exists and none is on the roadmap (You Aren't Gonna Need It (YAGNI) beats Open-Closed Principle (OCP))
  - Performance-critical inner loops where indirection costs
    - Order of magnitude: virtual calls are cheap on the Java Virtual Machine (JVM) after Just-In-Time compilation (JIT)
    - Allocations and remote calls are not
- **Never relax**
  - Liskov Substitution Principle (LSP) for types you expose to others
  - Fail fast on configuration and on input at trust boundaries
  - Idempotency and observability on networked commands (not covered by YAGNI)

## 18. Design Rules

Each rule names the failure it prevents.

- Rule of three before abstracting → prevents a wrong shared abstraction
- Invert dependencies at I/O and vendor boundaries first → prevents an untestable domain
- One contract test suite per interface with >1 implementation → prevents silent LSP breaks
- Let the consumer own small interfaces (Java role interfaces, Python `Protocol`) → prevents fat interfaces
- Closed set of variants → enum / sealed type + exhaustive `switch`; open set → interface + registry → prevents OCP misuse
- Validate in constructors (compact record constructor, `__post_init__`) → prevents invalid objects travelling far
- Use co-change history to choose seams → prevents cosmetic, not real, cohesion

## 19. Tensions Between Principles

Principles pull against each other; each row names how to resolve the pull.

**Abstraction tensions**

| Tension | Pulls toward | Pulls against | Resolve by |
|---|---|---|---|
| Don't Repeat Yourself (DRY) vs decoupling | One shared helper / library | Independent deploys and owners | Same reason to change → merge; different owners → duplicate |
| YAGNI vs OCP | Concrete code now | Extension point for future variants | Extract on the 2nd real variant; refactor is cheap inside one repo |
| Keep It Simple (KISS) vs Single Responsibility, Open-Closed, Liskov Substitution, Interface Segregation, Dependency Inversion (SOLID) | Fewer classes | Ports, adapters, role interfaces | SOLID at boundaries, KISS inside a module |
| Composition vs inheritance | Decorators, delegation | Reuse of a designed base class | Inherit only from bases designed for extension |

**Object and runtime tensions**

| Tension | Pulls toward | Pulls against | Resolve by |
|---|---|---|---|
| Law of Demeter (LoD) vs fluent APIs | Wrap every chain | Builders, streams, records | LoD only for behavior-rich objects |
| Tell-don't-ask vs Separation of Concerns (SoC) | Logic inside the entity | Entity free of I/O | Entity guards invariants; service does I/O |
| Command-Query Separation (CQS) vs atomicity | Split read and write | One atomic op | Keep atomic ops combined |
| Fail fast vs availability | Crash on bad state | Keep serving | Reject per request/record; never crash the fleet on optional deps |

Pick: concrete, simple code inside a module; SOLID-style abstractions at I/O, vendor and team boundaries, unless the variation has already appeared twice.

## 20. Failure Modes

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Wrong abstraction | DRY on look-alike code | Shared helper with boolean flags or `if (caller == X)` | Inline back into callers, re-extract later |
| Speculative generality | OCP / YAGNI ignored | Interfaces with one impl, unused config hooks | Delete; keep concrete until a 2nd variant |

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Hidden coupling | "Decoupled" via events/maps | Runtime break after a field rename | Schemas, contract tests, consumer-driven contracts |
| Fragile base class | Subclass relies on base self-calls | Base change breaks subclasses | Composition / decorators; `final` by default |
| Check-then-act race | CQS split of atomic op | Duplicate numbers/identifiers (IDs) under load | Atomic op (`incrementAndGet`, conditional write) |
| Batch killed by one row | Fail fast at system level | Job fails on a single bad record | Validate per record, quarantine / Dead-Letter Queue (DLQ) |

## 21. Interview Questions

### Q1 Duplication vs Don't Repeat Yourself (DRY)

**Q:** When is duplication better than DRY?

**L4 answer**

- When two pieces look alike but represent different knowledge with different reasons to change
- Merging them couples their callers

**L5 extra**

- Example: shared "common utils" across Databricks jobs and online services
  - One upgrade forces both to redeploy
- Share contracts (schemas), not implementation
- Rule of three before extracting

### Q2 You Aren't Gonna Need It (YAGNI) vs OCP

**Q:** YAGNI vs OCP — an agent tool registry has three tools today. Do you add a plugin interface?

**L4 answer**

- Three real tools with the same shape is already the "rule of three"
- A `Tool` interface + registry keyed by name is justified
- Dynamic class loading is not

**L5 extra**

- Close against the variation seen (new tools), not imagined ones (new protocols)
- Retrofit-expensive parts are not YAGNI
  - Tool input schemas
  - Idempotency of side-effecting tools
  - Per-tool timeouts and audit

### Q3 Composition Or Inheritance

**Q:** Composition or inheritance for notifiers with retry and logging?

**L4 answer**

- Composition: `Retrying(Logging(Email))` decorators over a `Notifier` interface
- Inheritance needs a class per combination

**L5 extra**

- Inheritance couples to the base's self-calls (fragile base class); decorators don't
- Decorator order is a contract
  - Metrics outside retry counts requests
  - Inside retry counts attempts

**L5-only: depth, scale, ambiguity, design ownership**

### Q1 Refactor A 5k-Line Class

**Q:** You inherit a 5k-line service class in a JPMorgan Chase (JPMC)-style data platform. Plan the refactor without stopping delivery.

- Characterization tests around current behavior first
- Find seams with co-change history and actors (pricing, persistence, notification)
- Strangle: extract one actor's code behind a port per release; keep the facade stable
- Stop when the remaining class is cohesive — not when it is "small"

### Q2 Agent Tool Registry

**Q:** Design an extensible agent tool registry that is not over-engineered.

- `Tool` interface: name, input schema, `invoke(input)`
  - Registry map
  - Startup validation of duplicate names (fail fast)
- LSP: every tool honors the same timeout, error, and idempotency contract
  - Contract tests per tool
- ISP: the planner sees `ToolCatalog` (describe), the executor sees `ToolInvoker`
- Not built yet: hot reloading, remote plugin loading — until a real need appears

### Q3 Principles In Distributed Systems

**Q:** Where do these principles hurt in distributed systems?

- Law of Demeter (LoD) and fine-grained interfaces → chatty remote calls
  - Remote Application Programming Interfaces (APIs) should be coarse-grained
- DRY across services → shared libraries force lockstep deploys
- Tell-don't-ask across a network → a command needs idempotency keys and retries
- Fail fast at startup on a remote dependency → fleet-wide crash loops

## 22. Code Map

- Java `1x/java/src/main/java/com/lc/x/concept/_01core_01principles/general/`; Python `1x/python/app/concept/_01core_01principles/general.py`
- Enable: Java `x.principles.enabled=true`; Python `X_ENABLED=principles`

| File | Java | Python |
|---|---|---|
| [Don't Repeat Yourself (DRY)](#4-dont-repeat-yourself-dry) | `Dry.Violation.{Checkout,Invoice}` vs `Dry.Fix.TaxPolicy`, `Dry.demo` | `TaxPolicy`, `dry_demo` |
| [Keep It Simple (KISS)](#5-keep-it-simple-kiss) | `Kiss.Violation.RuleEngine` vs `Kiss.Fix.shippingFee`, `Kiss.demo` | `KissViolationRuleEngine` vs `shipping_fee`, `kiss_demo` |
| [You Aren't Gonna Need It (YAGNI)](#6-you-arent-gonna-need-it-yagni) | `Yagni.Violation.PluginLoader` vs `Yagni.Fix.CardGateway`, `Yagni.demo` | `YagniViolationPluginLoader` vs `CardGateway`, `yagni_demo` |
| [Separation Of Concerns](#7-separation-of-concerns) | `SeparationOfConcerns.Violation.handle` vs `Fix.OrderHandler.handle`, `SeparationOfConcerns.demo` | `soc_violation_handle` vs `SocOrderHandler.handle`, `soc_demo` |
| [High Cohesion Low Coupling](#8-high-cohesion-low-coupling) | `CohesionCoupling.Violation.OrderUtils` vs `Fix.ShippingQuote.quoteFor`, `CohesionCoupling.demo` | `CohesionViolationUtils` vs `ShippingQuote.quote_for`, `cohesion_demo` |
| [Composition Over Inheritance](#9-composition-over-inheritance) | `CompositionOverInheritance.Violation.LoggingRetryingEmailNotifier` vs `Fix.{Retrying,Logging}`, `CompositionOverInheritance.demo` | `RetryingNotifier`, `LoggingNotifier`, `composition_demo` |
| [Program To An Interface](#10-program-to-an-interface) | `ProgramToInterface.Violation.totalOf(ArrayList)` vs `Fix.totalOf(Collection)`, `ProgramToInterface.demo` | `total_of_violation(list)` vs `total_of(Iterable)`, `interface_demo` |
| [Encapsulate What Varies](#11-encapsulate-what-varies) | `EncapsulateWhatVaries.Violation.Checkout.fee` vs `Fix.FeePolicy`, `EncapsulateWhatVaries.demo` | `FeePolicy`, `FEE_POLICIES`, `encapsulate_demo` |
| [Law Of Demeter](#12-law-of-demeter) | `LawOfDemeter.Violation.Checkout.canPay` vs `Fix.Order.canPay`, `LawOfDemeter.demo` | `lod_violation_can_pay` vs `LodOrder.can_pay`, `lod_demo` |
| [Tell Dont Ask](#13-tell-dont-ask) | `TellDontAsk.Violation.PaymentService.charge` vs `Fix.Wallet.debit`, `TellDontAsk.demo` | `tda_violation_charge` vs `Wallet.debit`, `tda_demo` |
| [Command Query Separation](#14-command-query-separation) | `Cqs.Violation.OrderNumbers.nextOrderNumber` vs `Fix.OrderNumbers.{reserveNumber,peekNext}`, `Cqs.demo` | `CqsOrderNumbers`, `cqs_demo` |
| [Fail Fast](#15-fail-fast) | `FailFast.Violation.Order` vs `Fix.Order` (compact constructor), `Fix.validateBatch` (per-record), `FailFast.demo` | `FailFastOrder.__post_init__`, `validate_batch`, `failfast_demo` |
| [Principle Of Least Astonishment](#16-principle-of-least-astonishment) | `LeastAstonishment.Violation.getDiscount` vs `Fix.recordDiscountAudit`, `LeastAstonishment.demo` (+ `List.remove` trap) | `pola_violation_add` vs `pola_add`, `pola_demo` |

## References

- [Andrew Hunt & David Thomas — The Pragmatic Programmer, 20th anniversary ed. (2019)](https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/) — DRY as "every piece of knowledge has one authoritative representation"
- [Martin Fowler — Yagni](https://martinfowler.com/bliki/Yagni.html) — the cost of building presumptive features
- [Martin Fowler — TellDontAsk](https://martinfowler.com/bliki/TellDontAsk.html) — and when not to apply it
- [Martin Fowler — CommandQuerySeparation](https://martinfowler.com/bliki/CommandQuerySeparation.html) — Bertrand Meyer's principle and its exceptions
- [Lieberherr & Holland, "Assuring Good Style for Object-Oriented Programs", IEEE Software 1989](https://doi.org/10.1109/52.35588) — origin of the Law of Demeter
