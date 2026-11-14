# 01core.01principles.06dry-kiss-yagni Don't Repeat Yourself (DRY), Keep It Simple (KISS), You Aren't Gonna Need It (YAGNI)

> The three brakes on over-design: one home per piece of knowledge, the simplest real design, nothing built before it is needed.

## Index

- [1. Don't Repeat Yourself (DRY)](#1-dont-repeat-yourself-dry)
  - [1.1 Idea](#11-idea) · [1.2 Code](#12-code) · [1.3 Catch](#13-catch)
- [2. Keep It Simple (KISS)](#2-keep-it-simple-kiss)
  - [2.1 Idea](#21-idea) · [2.2 Code](#22-code) · [2.3 Catch](#23-catch)
- [3. You Aren't Gonna Need It (YAGNI)](#3-you-arent-gonna-need-it-yagni)
  - [3.1 Idea](#31-idea) · [3.2 Code](#32-code) · [3.3 Catch](#33-catch)

Part B, general principles (Java + Python). Back to [00index](00index.md).

## 1. Don't Repeat Yourself (DRY)

Every business rule should have exactly one place where it is defined.

### 1.1 Idea

- "Every piece of knowledge must have a single, unambiguous, authoritative representation"
  - Hunt & Thomas, *The Pragmatic Programmer* (1999)
- About knowledge (rules, schemas), not about similar-looking text
- Running example (`Dry`)
  - Violation: tax rate `0.08` hard-coded in checkout, invoice and refund
  - Fix: one `TaxPolicy` used by all three
- **Mechanism**
  - One change site per business rule ⇒ no drift between copies

### 1.2 Code

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

### 1.3 Catch

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

## 2. Keep It Simple (KISS)

Pick the simplest design that still meets the real requirements.

### 2.1 Idea

- The simplest design that meets the *real* requirements
- Running example (`Kiss`)
  - Violation: a generic reflection-based rule engine to compute a shipping fee
  - Fix: a five-line function with two `if`s
- **Mechanism**
  - Fewer moving parts ⇒ less to read, fewer failure modes, faster onboarding

### 2.2 Code

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

### 2.3 Catch

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

## 3. You Aren't Gonna Need It (YAGNI)

Do not build a feature or abstraction until a real requirement needs it.

### 3.1 Idea

- Don't build a feature or abstraction until a requirement needs it (Extreme Programming)
- Running example (`Yagni`)
  - Violation: a `PaymentProviderPlugin` Service Provider Interface (SPI) with config-driven class loading, for one provider
  - Fix: a concrete `CardGateway`; extract an interface when provider two appears
- **Mechanism**
  - Saves build cost, carrying cost, and the cost of guessing wrong (Fowler, "Yagni", 2015)

### 3.2 Code

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

### 3.3 Catch

Retrofit-expensive properties are NOT covered by YAGNI — keep them now.

→ YAGNI applied to things that are expensive to retrofit.  
⇒ Missing idempotency keys, tenant identifiers (IDs), schema versioning, auth, observability — each costs a migration later.  
→ YAGNI assumes refactoring is cheap; it is not across public APIs, persisted data, or other teams.

- Tension with [Open-Closed Principle (OCP)](02ocp.md#4-catch): see [98tradeoffs](98tradeoffs.md#5-tensions-between-principles)
- 🗣 "YAGNI covers features, not things that are expensive to retrofit."
