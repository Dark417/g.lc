# 01core.01principles.03lsp Liskov Substitution Principle (LSP)

> A subtype keeps every promise of its base type, so callers never need to know which one they hold.

## Index

- [1. Idea](#1-idea)
- [2. Mechanism](#2-mechanism)
- [3. Code](#3-code)
  - [3.1 Violation](#31-violation)
  - [3.2 Fix](#32-fix)
  - [3.3 Contract Test](#33-contract-test)
- [4. Catch](#4-catch)
- [References](#references)

Part A, SOLID (Java + Python). Back to [00index](00index.md).

## 1. Idea

Code written for a base type works with any subtype, without knowing which.

- **Behavioral subtyping** (Liskov 1987 keynote; Liskov & Wing 1994)
  - Preconditions not strengthened
  - Postconditions not weakened
  - Invariants preserved
  - No new exception types callers can't expect
- Running example (`Lsp`)
  - Violation: `Payment.refund()`; `GiftCardPayment.refund()` throws `UnsupportedOperationException`
  - Callers add `instanceof GiftCardPayment` checks
  - Fix: split capability
    - `Payment` for all
    - `Refundable` only for refundable types

## 2. Mechanism

Callers reason against the contract once, not per subtype.

- Violations surface as type checks in callers
  - The polymorphism stopped paying
- The capability split makes the wrong call a compile error, not a runtime throw

## 3. Code

The violation forces `instanceof` in callers; the fix makes gift cards unpassable where a refund is expected.

### 3.1 Violation

```java
// concept/_01core_01principles/solid/Lsp.java
/** Base promise: refund() returns a refund id for any captured payment. */
public static class Payment {                      // Lsp.Violation.Payment
    protected final BigDecimal amount;
    public String refund() { return "refund-" + amount; }
}

/** Breaks the promise: callers written against Payment now crash. */
public static class GiftCardPayment extends Payment {
    @Override
    public String refund() {
        throw new UnsupportedOperationException("gift cards are not refundable");
    }
}

/** Caller forced to know subtypes: the smell that tells you LSP is broken. */
public static List<String> refundAll(List<Payment> payments) {
    List<String> out = new ArrayList<>();
    for (Payment p : payments) {
        if (p instanceof GiftCardPayment) { out.add("skipped gift card"); continue; }
        out.add(p.refund());
    }
    return out;
}
```

```python
# app/concept/_01core_01principles/solid.py
class LspViolationGiftCard(LspViolationPayment):
    """Breaks the promise; callers written for LspViolationPayment crash."""

    def refund(self) -> str:
        raise NotImplementedError("gift cards are not refundable")


def lsp_violation_refund_all(payments: list[LspViolationPayment]) -> list[str]:
    """The smell: callers need isinstance checks to survive the subtype."""
    return ["skipped gift card" if isinstance(p, LspViolationGiftCard) else p.refund() for p in payments]
```

### 3.2 Fix

```java
// concept/_01core_01principles/solid/Lsp.java
public interface Payment { BigDecimal amount(); }  // Lsp.Fix.Payment

/** Only types that can honor refund() implement it; no throwing overrides. */
public interface Refundable extends Payment { String refund(); }

public record CardPayment(BigDecimal amount) implements Refundable {
    public String refund() { return "refund-card-" + amount; }
}

public record GiftCardPayment(BigDecimal amount) implements Payment { }   // not Refundable

public static List<String> refundAll(List<? extends Refundable> refundables) {
    List<String> out = new ArrayList<>();
    for (Refundable r : refundables) out.add(r.refund());   // no type checks needed
    return out;
}
```

```python
# app/concept/_01core_01principles/solid.py
class Refundable(ABC):
    """Capability: only types that can honor refund() implement it."""

    amount: Decimal

    @abstractmethod
    def refund(self) -> str: ...


@dataclass(frozen=True)
class CardPayment(Refundable):
    amount: Decimal

    def refund(self) -> str:
        return f"refund-card-{self.amount}"


@dataclass(frozen=True)
class GiftCardPayment:
    """Not Refundable, so it can't be passed where a refund is expected."""

    amount: Decimal
```

### 3.3 Contract Test

One behavioral check, run against every implementation.

```java
// concept/_01core_01principles/solid/Lsp.java
// Contract test in miniature: run the same behavioral checks against every implementation.
// Catch: it only checks what you wrote down; unstated promises (rounding, latency) still drift.
public static boolean contractHolds(Refundable r) {   // Lsp.Fix.contractHolds
    String id = r.refund();
    return id != null && id.startsWith("refund-") && id.endsWith(r.amount().toPlainString());
}
```

```python
# app/concept/_01core_01principles/solid.py
def contract_holds(r: Refundable) -> bool:
    """Mini contract test: run the same behavioral checks against every implementation."""
    rid = r.refund()
    return rid.startswith("refund-") and rid.endswith(str(r.amount))
```

- Demo: `Lsp.demo()` / `lsp_demo()` shows the `instanceof` smell, the split, and the contract check
- Java demo also prints `List.of(1).add(2)` → `UnsupportedOperationException`
- Python demo prints `isinstance((1, 2), MutableSequence)` → `False`
- Use when a subtype "can't" do something the base promises

## 4. Catch

Compilers and type checkers check signatures, never behavior.

→ Compilers check signatures, never behavior.  
⇒ A subtype can compile and still break callers (stricter validation, different rounding).  
→ Write one contract test suite and run it against every implementation.

→ The Java Development Kit (JDK) itself trades Liskov Substitution Principle (LSP) for fewer interfaces: `List.of(...).add(x)` throws.  
⇒ "Optional operations" in `java.util.Collection` docs; callers must know the concrete source.  
→ Python's `collections.abc` splits `Sequence` from `MutableSequence` instead; do the same in your types.

→ Inheritance used only for code reuse, never substituted.  
⇒ LSP looks irrelevant, but the subtype is still assignable to the base type.  
→ If it can't keep the promises, don't inherit — compose.

- 🗣 "Signatures compile; behavior substitutes — LSP is about the second."

## References

- [Liskov & Wing, "A Behavioral Notion of Subtyping", Association for Computing Machinery (ACM) Transactions on Programming Languages and Systems (TOPLAS) 1994](https://doi.org/10.1145/197320.197383) — formal LSP
