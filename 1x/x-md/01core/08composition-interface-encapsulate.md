# 01core.01principles.08composition-interface-encapsulate Composition Interfaces And Variation

> Assemble behavior from parts, depend on the narrowest contract, and wall off the axis of change.

## Index

- [1. Composition Over Inheritance](#1-composition-over-inheritance)
  - [1.1 Idea](#11-idea) · [1.2 Code](#12-code) · [1.3 Catch](#13-catch)
- [2. Program To An Interface](#2-program-to-an-interface)
  - [2.1 Idea](#21-idea) · [2.2 Code](#22-code) · [2.3 Catch](#23-catch)
- [3. Encapsulate What Varies](#3-encapsulate-what-varies)
  - [3.1 Idea](#31-idea) · [3.2 Code](#32-code) · [3.3 Catch](#33-catch)

Part B, general principles (Java + Python). Back to [00index](00index.md).

## 1. Composition Over Inheritance

Build behavior by wrapping small parts instead of growing a class tree.

### 1.1 Idea

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

### 1.2 Code

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

### 1.3 Catch

Decorator order is a contract; inheritance is still right for designed bases.

→ Composition everywhere.  
⇒ Long delegation chains and forwarding boilerplate in Java.  
→ Inheritance is right for a true is-a with a base *designed and documented for extension*.  
→ Examples: framework abstract classes, sealed data hierarchies.

→ Decorators wrapped in an unplanned order.  
⇒ Logging outside retry logs requests; inside it logs attempts.  
→ Treat the wiring order as part of the contract.

- 🗣 "Inheritance is the tightest coupling Java offers; I use it only for real is-a."

## 2. Program To An Interface

Accept the widest type you can handle; return the most useful specific one.

### 2.1 Idea

- Depend on a supertype contract, not a concrete class (GoF)
- "Interface" = the contract, not necessarily the `interface` keyword
- Running example (`ProgramToInterface`)
  - Violation: `totalOf(ArrayList<Order>)` returns `HashMap`
  - Fix: `totalOf(Collection<Order>)` returns `Map`
  - Python takes `Iterable[Order]`, returns `Mapping`
- **Mechanism**
  - Callers bind to the narrowest contract ⇒ implementation swaps are invisible

### 2.2 Code

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

### 2.3 Catch

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

## 3. Encapsulate What Varies

Find the part that changes and put a stable interface in front of it.

### 3.1 Idea

- Find the axis of change, put a stable interface in front of it
- The engine behind Open-Closed Principle (OCP; [02ocp](02ocp.md)) and the Strategy pattern
- Running example (`EncapsulateWhatVaries`)
  - Violation: region fee rules inline in checkout, edited every quarter
  - Fix: `FeePolicy` per region, selected by a map
- **Mechanism**
  - Volatile code is isolated
  - Stable code stops changing

### 3.2 Code

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

### 3.3 Catch

You must have observed the variation; abstracting a part that never changes is pure overhead.

→ Guessing the axis.  
⇒ Abstractions around stable parts, while the real change hits elsewhere.  
→ Encapsulate after observing change, not before.

→ Encapsulating as code what is really data.  
⇒ A deploy for every rate change.  
→ Rates and thresholds that business users edit belong in config or tables, not classes.

- 🗣 "Find the part that changes, put a stable interface in front of it."
