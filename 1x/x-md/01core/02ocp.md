# 01core.01principles.02ocp Open-Closed Principle (OCP)

> Add behavior by adding code, not by editing tested code.

## Index

- [1. Idea](#1-idea)
- [2. Mechanism](#2-mechanism)
- [3. Code](#3-code)
  - [3.1 Violation](#31-violation)
  - [3.2 Fix](#32-fix)
  - [3.3 Closed Set Exception](#33-closed-set-exception)
- [4. Catch](#4-catch)

Part A, SOLID (Java + Python). Back to [00index](00index.md).

## 1. Idea

A module should accept new variants without its tested code being reopened.

- **Open for extension, closed for modification** (Meyer, 1988)
- Martin's version: extend through polymorphism behind a stable interface
- Running example (`Ocp`)
  - Violation: `PaymentProcessor.pay` switches on `"CARD" | "PAYPAL"`
  - A new method edits and retests it
  - Fix: `PaymentMethod` interface + registry keyed by name
  - A new method is a new class

## 2. Mechanism

Registration replaces the branch, so new behavior is additive.

- Tested code stays untouched
- Registration (map, Spring `List<PaymentMethod>` injection) replaces the `switch`
- Duplicate names fail fast at registry construction

## 3. Code

The violation must be edited for every new method; the fix adds `ApplePay` with zero edits.

### 3.1 Violation

```java
// concept/_01core_01principles/solid/Ocp.java
/** Closed for extension: adding "APPLE_PAY" means editing pay() and every other switch like it. */
public static final class PaymentProcessor {       // Ocp.Violation.PaymentProcessor
    public String pay(String method, BigDecimal amount) {
        switch (method) {
            case "CARD":   return "card charged " + amount;
            case "PAYPAL": return "paypal charged " + amount;
            default: throw new IllegalArgumentException("unsupported method " + method);
        }
    }
}
```

```python
# app/concept/_01core_01principles/solid.py
class OcpViolationProcessor:
    """Every new payment method edits and retests this if-chain."""

    def pay(self, method: str, amount: Decimal) -> str:
        if method == "CARD":
            return f"card charged {amount}"
        if method == "PAYPAL":
            return f"paypal charged {amount}"
        raise ValueError(f"unsupported method {method}")
```

### 3.2 Fix

```java
// concept/_01core_01principles/solid/Ocp.java
/** The stable abstraction; implementations are additive. */
public interface PaymentMethod {                   // Ocp.Fix.PaymentMethod
    String name();
    String charge(BigDecimal amount);
}

/** Added later without touching PaymentProcessor, Card or PayPal. */
public record ApplePay() implements PaymentMethod {
    public String name() { return "APPLE_PAY"; }
    public String charge(BigDecimal amount) { return "apple pay charged " + amount; }
}

/** Registry replaces the switch; duplicate names fail fast at construction. */
public static final class PaymentProcessor {       // Ocp.Fix.PaymentProcessor
    private final Map<String, PaymentMethod> methods = new LinkedHashMap<>();

    public PaymentProcessor(List<PaymentMethod> all) {   // Spring can inject List<PaymentMethod>
        for (PaymentMethod m : all) {
            if (methods.putIfAbsent(m.name(), m) != null) {
                throw new IllegalStateException("duplicate payment method " + m.name());
            }
        }
    }

    public String pay(String method, BigDecimal amount) {
        PaymentMethod m = methods.get(method);
        if (m == null) {
            throw new IllegalArgumentException("unsupported method " + method + "; known=" + methods.keySet());
        }
        return m.charge(amount);
    }
}
```

```python
# app/concept/_01core_01principles/solid.py
class PaymentMethod(Protocol):
    name: str

    def charge(self, amount: Decimal) -> str: ...


@dataclass(frozen=True)
class ApplePay:
    """Added later with zero edits to the processor."""

    name: str = "APPLE_PAY"

    def charge(self, amount: Decimal) -> str:
        return f"apple pay charged {amount}"


class OcpPaymentProcessor:
    """Registry replaces the if-chain; duplicate names fail fast at construction."""

    def __init__(self, methods: list[PaymentMethod]) -> None:
        self._methods: dict[str, PaymentMethod] = {}
        for m in methods:
            if m.name in self._methods:
                raise ValueError(f"duplicate payment method {m.name}")
            self._methods[m.name] = m

    def pay(self, method: str, amount: Decimal) -> str:
        if method not in self._methods:
            raise ValueError(f"unsupported method {method}; known={sorted(self._methods)}")
        return self._methods[method].charge(amount)
```

### 3.3 Closed Set Exception

For a set fixed by contract, an exhaustive `switch` beats an interface.

```java
// concept/_01core_01principles/solid/Ocp.java
// Java 17 checks exhaustiveness for enum switch expressions; a new constant breaks the build here.
public enum FeeKind { FLAT, PERCENT }              // Ocp.Fix.FeeKind

public static BigDecimal fee(FeeKind kind, BigDecimal amount) {
    return switch (kind) {
        case FLAT -> new BigDecimal("0.30");
        case PERCENT -> amount.multiply(new BigDecimal("0.029"));
    };
}
```

- Demo: `Ocp.demo()` / `ocp_demo()` pays with `APPLE_PAY` without touching the processor
- Use when variants arrive over time and each is independent

## 4. Catch

You only close against variation you have seen; if variants were speculative, the interface is You Aren't Gonna Need It (YAGNI) debt.

→ You can only close against a variation you predicted.  
⇒ Wrong axis: the abstraction resists the change that actually arrives.  
→ Wait for the second or third real variant (rule of three); then extract.

→ Plugin points added "in case" (direct conflict with [YAGNI](06dry-kiss-yagni.md#3-you-arent-gonna-need-it-yagni)).  
⇒ Interfaces with one implementation, factories, config-driven loading nobody uses.  
→ Keep a concrete class until a second variant exists.

→ The expression problem: polymorphism makes new *types* cheap but new *operations* expensive.  
⇒ Adding `refund()` to every `PaymentMethod` edits every class anyway.  
→ For a closed set, an exhaustive `switch` is fine; the compiler finds every site.  
→ Java 17: enum switch expressions; Java 21: sealed types + pattern `switch`.

- 🗣 "I close code against the variation I have seen twice, not the one I imagine."
