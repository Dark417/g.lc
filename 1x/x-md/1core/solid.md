# SOLID Principles

- **In plain words:** SOLID is five rules of thumb for arranging classes, so a change touches one place and swapping one part for another doesn't break its callers.
- Five principles (SRP, OCP, LSP, ISP, DIP), each with idea, mechanism, Java + Python code (violation, then fix), and the catch
- OOP mechanics behind them (overriding, polymorphism, the expression problem): [java-oop.md](java-oop.md)
- Siblings: [Design principles](design-principles.md) · [Design patterns](design-patterns.md) · [Spring](spring.md) · [Spring Boot](spring-boot.md)

## Index

- [1. One-Minute Version](#1-one-minute-version)
  - [1.1 What SOLID buys you (the goals)](#11-what-solid-buys-you-the-goals)
- [2. Cheat Sheet](#2-cheat-sheet)
- [3. Single Responsibility Principle (SRP)](#3-single-responsibility-principle-srp)
  - [3.1 Idea](#31-idea)
  - [3.2 Mechanism](#32-mechanism)
  - [3.3 Code](#33-code)
  - [3.4 Catch](#34-catch)
- [4. Open-Closed Principle (OCP)](#4-open-closed-principle-ocp)
  - [4.1 Idea](#41-idea)
  - [4.2 Mechanism](#42-mechanism)
  - [4.3 Code](#43-code)
  - [4.4 Catch](#44-catch)
- [5. Liskov Substitution Principle (LSP)](#5-liskov-substitution-principle-lsp)
  - [5.1 Idea](#51-idea)
  - [5.2 Mechanism](#52-mechanism)
  - [5.3 Code](#53-code)
  - [5.4 Catch](#54-catch)
- [6. Interface Segregation Principle (ISP)](#6-interface-segregation-principle-isp)
  - [6.1 Idea](#61-idea)
  - [6.2 Mechanism](#62-mechanism)
  - [6.3 Code](#63-code)
  - [6.4 Catch](#64-catch)
- [7. Dependency Inversion Principle (DIP)](#7-dependency-inversion-principle-dip)
  - [7.1 Idea](#71-idea)
  - [7.2 Mechanism](#72-mechanism)
  - [7.3 Code](#73-code)
  - [7.4 Catch](#74-catch)
- [8. Failure Modes](#8-failure-modes)
- [9. Interview Questions](#9-interview-questions)
  - [9.1 Overview (Q1–Q3)](#91-overview)
  - [9.2 SRP (Q4–Q6)](#92-srp)
  - [9.3 OCP (Q7–Q10)](#93-ocp)
  - [9.4 LSP (Q11–Q14)](#94-lsp)
  - [9.5 ISP (Q15–Q16)](#95-isp)
  - [9.6 DIP (Q17–Q18)](#96-dip)
  - [9.7 Putting it together (Q19–Q20)](#97-putting-it-together)
- [10. Code Map](#10-code-map)

---

## 1. One-Minute Version

- **What:** five rules of thumb with one goal: the next change should be cheap and safe
- **Why:** most of a long-lived service's cost is changing it later, not writing it the first time
- **How**
  - SRP: a class should only change for one group of people (finance, ops, marketing), not for all of them
  - OCP: a new kind of thing (new payment method) is a new class, not an edit to working code
  - LSP: a subclass must behave the way callers of the parent expect
  - ISP: give each caller a small interface with only what it uses
  - DIP: business code defines the interface; the database code implements it
- **Catch:** each one, overdone, causes its own mess
  - SRP overdone = **class explosion**: you split so eagerly that one feature is spread over 30 tiny classes and nobody can follow the flow
  - OCP overdone = **speculative plug-in points**: you add interfaces, factories and config "in case we need another one later", and that later never comes
- 🗣 "I don't apply SOLID everywhere. I apply a principle when I can name the future change it makes cheaper."

### 1.1 What SOLID buys you (the goals)

| Goal | What it means in practice | Main principles |
|---|---|---|
| Maintainable | A change touches one place, and you can predict which | SRP, OCP |
| Extensible | New variants are added, not hacked into old code | OCP, LSP |
| Testable | You can swap the database or mailer for a fake in a unit test | DIP, ISP |
| Readable | Each class has a clear owner and a small surface | SRP, ISP |
| Safe to substitute | Any implementation can be plugged in without surprises | LSP |

- "Scalable" here means the **codebase and team** scale (more people work without stepping on each other), not traffic
- "Easy to implement" is not a goal SOLID delivers: it adds interfaces and files up front; it pays back only when changes come

## 2. Cheat Sheet

- One line, the violation smell, and the line to say aloud

| Principle | One line | Smell when violated | 🗣 line to say aloud |
|---|---|---|---|
| [Single Responsibility Principle (SRP)](#3-single-responsibility-principle-srp) | One module answers to one actor | God class edited by finance, ops and marketing | "I split a class when different teams ask for changes to it, not when it has many methods." |
| [Open-Closed Principle (OCP)](#4-open-closed-principle-ocp) | Add behavior by adding code, not editing tested code | `switch` on type repeated in many places | "A new payment method should be a new class, not an edit to working code; I add that interface once a second variant really shows up." |
| [Liskov Substitution Principle (LSP)](#5-liskov-substitution-principle-lsp) | A subtype keeps the base type's promises | `instanceof` checks, overrides that throw `UnsupportedOperationException` | "A subclass compiling isn't enough; it has to behave the way callers of the parent expect." |
| [Interface Segregation Principle (ISP)](#6-interface-segregation-principle-isp) | Clients depend only on methods they use | Stub methods that throw; huge mocks in tests | "Interfaces belong to the client, sized to what it calls." |
| [Dependency Inversion Principle (DIP)](#7-dependency-inversion-principle-dip) | Policy owns the interface; details implement it | Domain imports the Amazon Web Services (AWS) Software Development Kit (SDK) or Java Database Connectivity (JDBC) | "The arrow of source dependency points at the policy, not the database." |

## 3. Single Responsibility Principle (SRP)

- **In plain words:** give each class one boss. If finance, ops and marketing all ask for changes to the same class, split it so each group's changes land in its own file.
- **One line:** One module answers to one actor, so each stakeholder's change lands in one file.

- Name and grouping: Robert C. Martin, "Design Principles and Design Patterns" (2000)
- Acronym: Michael Feathers
- Shared goal of SOLID: classes whose changes stay local and whose substitutes are safe

### 3.1 Idea

Single Responsibility Principle (SRP) is about who asks for changes, not how many methods a class has.

- **Actor** = a group of people who can ask for a change: finance, ops, marketing, compliance
- Ask "who would make me edit this class?"; if the answer is two or more groups, it has two or more responsibilities

- A module has **one reason to change**
  - "Reason" = one actor (stakeholder group)
  - Source: Martin, *Clean Architecture* (2017)
- Not "does one thing"
  - That rule is for functions
- Running example (`Srp`)
  - Violation: `OrderService.place` prices with tax, stores the order, formats the email
  - Finance, ops and marketing all edit the same class
  - Fix: `PriceCalculator`, `OrderRepository`, `OrderNotifier`
  - `OrderService` only coordinates

- **"One reason to change" vs "does one thing" — a tiny example**
  - Function rule ("do one thing"): `calculateTax()` only calculates tax; it doesn't also save or send email. This is about the code inside one function
  - Class rule (SRP): `PriceCalculator` may have five methods (`subtotal`, `tax`, `discount`, `round`, `total`), and that's fine: all five are finance rules, so only finance makes you change it
  - Violation: `OrderService` has only one method, `place()`, but finance (tax), ops (storage) and marketing (email wording) all edit it. One method, three reasons to change

### 3.2 Mechanism

Each actor's change request lands in a different file.

- **"Changes stay local"** means: when finance changes the tax rate, you edit `PriceCalculator` and nothing else. You don't open the email code, you don't retest storage, and marketing's pull request doesn't conflict with yours
- **Two classes, same database?** Fine. SRP is about who changes the *code*, not where data ends up
  - `MarketingReport` and `OpsCleanupJob` can both touch the `orders` table through a repository
  - Each still changes for its own team; the shared table belongs to the repository, whose owner is the data / ops side
  - The risk to watch: if both teams keep changing the table's meaning, the repository becomes the new shared hotspot

- Smaller diffs
- Fewer merge conflicts
- Tests target one reason
- Both versions produce the same output; only the cost per change request differs

### 3.3 Code

The violation mixes three actors' rules in one method; the fix gives each actor a class.

#### 3.3.1 Violation

```java
// concept/_01core_01principles/solid/Srp.java
/** God service: finance (tax), ops (storage) and marketing (email copy) all edit this class. */
public static final class OrderService {           // Srp.Violation.OrderService
    private final Map<String, BigDecimal> table = new LinkedHashMap<>();
    private final List<String> outbox = new ArrayList<>();

    public String place(Order order) {
        BigDecimal total = order.subtotal().multiply(new BigDecimal("1.08"))   // finance rule
                .setScale(2, RoundingMode.HALF_UP);
        table.put(order.id(), total);                                           // ops concern
        outbox.add("Hi! Your order " + order.id() + " costs " + total);         // marketing copy
        return "placed " + order.id() + " total=" + total + " mails=" + outbox.size();
    }
}
```

```python
# app/concept/_01core_01principles/solid.py
class SrpViolationOrderService:
    """God service: finance (tax), ops (storage) and marketing (email copy) all edit this class."""

    def place(self, order: SrpOrder) -> str:
        total = (order.subtotal * Decimal("1.08")).quantize(CENT, ROUND_HALF_UP)  # finance rule
        self._table[order.id] = total  # ops concern
        self._outbox.append(f"Hi! Your order {order.id} costs {total}")  # marketing copy
        return f"placed {order.id} total={total} mails={len(self._outbox)}"
```

#### 3.3.2 Fix

```java
// concept/_01core_01principles/solid/Srp.java
/** Finance owns this: tax and rounding rules change here only. */
public static final class PriceCalculator {        // Srp.Fix.PriceCalculator
    private final BigDecimal taxRate;
    public PriceCalculator(BigDecimal taxRate) { this.taxRate = taxRate; }

    public BigDecimal total(Order order) {
        return order.subtotal().multiply(BigDecimal.ONE.add(taxRate)).setScale(2, RoundingMode.HALF_UP);
    }
}
// OrderRepository (ops) and OrderNotifier (marketing) follow the same shape.

/** Coordinator: no rules of its own, so no actor needs to edit it for their change. */
public static final class OrderService {           // Srp.Fix.OrderService
    private final PriceCalculator prices;
    private final OrderRepository repo;
    private final OrderNotifier notifier;

    public String place(Order order) {
        BigDecimal total = prices.total(order);
        repo.save(order.id(), total);
        notifier.confirmed(order, total);
        return "placed " + order.id() + " total=" + total + " stored=" + repo.count() + " mails=" + notifier.sent();
    }
}
```

```python
# app/concept/_01core_01principles/solid.py
@dataclass
class SrpPriceCalculator:
    """Finance owns this: tax and rounding change here only."""

    tax_rate: Decimal

    def total(self, order: SrpOrder) -> Decimal:
        return (order.subtotal * (1 + self.tax_rate)).quantize(CENT, ROUND_HALF_UP)

@dataclass
class SrpOrderService:
    """Coordinator with no rules of its own."""

    prices: SrpPriceCalculator
    repo: SrpOrderRepository      # ops owns storage
    notifier: SrpOrderNotifier    # marketing owns wording and channel

    def place(self, order: SrpOrder) -> str:
        total = self.prices.total(order)
        self.repo.save(order.id, total)
        self.notifier.confirmed(order, total)
        return f"placed {order.id} total={total} stored={len(self.repo.rows)} mails={len(self.notifier.outbox)}"
```

- Demo: `Srp.demo()` / `srp_demo()` prints both; a tax change now edits `PriceCalculator` only
- Identical output proves nothing about design; the diff per change request does

### 3.4 Catch

The opposite of a god class is also a failure: there are two ways to split wrong.

- **Failure 1: splitting too much (the opposite of a god class)**
  → Someone reads "one reason to change" as "one method per class".  
  ⇒ 40 tiny classes; to understand one feature you open 12 files.  
  → Don't split just because a class is long. Split when you can name two different teams who actually ask for changes to it, and their changes land at different times.

- **Failure 2: splitting along the wrong line**
  → You split by technical layer (`OrderValidator`, `OrderMapper`, `OrderDao`, `OrderDto`) instead of by who changes it.  
  ⇒ Every new feature still edits all four classes at once. That's **shotgun surgery**: one change forces small edits scattered across many files, like pellets from a shotgun.  
  → Quick test: methods that use the same fields and always change in the same commits belong together. `git log` shows you which files change together.

- 🗣 "I split a class when different teams ask for changes to it, not when it has many methods. And if every feature still touches all the pieces, I split along the wrong line."

## 4. Open-Closed Principle (OCP)

- **In plain words:** a new kind of thing (say, a new payment method) is added by writing a new class, not by editing an `if/else` chain that already works.
- **One line:** Add behavior by adding code, not by editing tested code.

### 4.1 Idea

A module should accept new variants without its tested code being reopened.

- **Open for extension, closed for modification** (Meyer, 1988)
- Martin's version: extend through polymorphism behind a stable interface
- Running example (`Ocp`)
  - Violation: `PaymentProcessor.pay` switches on `"CARD" | "PAYPAL"`
  - A new method edits and retests it
  - Fix: `PaymentMethod` interface + registry keyed by name
  - A new method is a new class

- **What "closed" really means**
  - Closed = to add a **new variant** (a new payment method), you don't edit code that already works and is tested
  - It does **not** mean old code is frozen forever
    - Fixing a bug in `Card.charge()`: edit it, that's normal
    - The rule for card payments itself changes (say, add 3-D Secure): edit `Card`, because the requirement for that variant changed
    - Adding Apple Pay: don't edit `Card`, `PayPal` or the processor; write `ApplePay`
  - The interface (`PaymentMethod`) stays stable; if you truly need a new operation, see the expression problem in 4.4

### 4.2 Mechanism

Registration replaces the branch, so new behavior is additive.

- Tested code stays untouched
- Registration (map, Spring `List<PaymentMethod>` injection) replaces the `switch`
- Duplicate names fail fast at registry construction
  - This isn't OCP itself; it's a safety check that comes with the registry
  - Once new methods are just "dropped in", two classes could claim the same name (`"CARD"`) and one would silently win. The check makes that a startup error instead of a production surprise

### 4.3 Code

The violation must be edited for every new method; the fix adds `ApplePay` with zero edits.

#### 4.3.1 Violation

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

#### 4.3.2 Fix

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

#### 4.3.3 Closed Set Exception

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

### 4.4 Catch

An interface only helps against the kind of change you planned for; build it once real variants show up, not before.

- Vocabulary
  - **Variation** = the thing that keeps changing (which payment method)
  - **Closing against a variation** = shaping the code (an interface + registry) so that kind of change needs no edits to old code

- **Failure 1: you guessed the wrong kind of change ("wrong axis")**
  → You built `PaymentMethod` because you expected new payment methods.  
  ⇒ The change that actually arrives is "support EUR and JPY". Every payment class now needs currency logic, so your interface didn't help; worse, you now edit four classes instead of one.  
  → Wait until you have seen the change happen two or three times (rule of three), then build the abstraction along that line.

- **Failure 2: plug-in points "just in case"** (conflicts with [YAGNI](design-principles.md#6-you-arent-gonna-need-it-yagni))  
  ⇒ Interfaces with a single implementation, factories and config loading nobody uses.  
  → Keep one concrete class until a second variant really exists. Then extract the interface, so it has at least two implementations from day one.

- **Failure 3: the expression problem** (full explanation: [java-oop.md](java-oop.md#7-the-expression-problem))  
  → Interfaces make a new *type* cheap (Apple Pay = one new class) but a new *operation* expensive.  
  ⇒ Adding `refund()` to the `PaymentMethod` interface forces you to edit `Card`, `PayPal` and `ApplePay`. You edit every class anyway, so OCP gives you nothing for this kind of change.  
  → If the set of types is fixed and operations keep growing, an exhaustive `switch` is better: the compiler lists every place to update.  
  → Java 17: enum switch expressions; Java 21: sealed types + pattern `switch`.

- 🗣 "A new payment method should be a new class, not an edit to working code. But I add that interface only after a second variant really shows up, because an interface only helps against the kind of change you planned for."

## 5. Liskov Substitution Principle (LSP)

- **In plain words:** a replacement part must fit like the original. Code that accepts a base type keeps working, with no surprises, whatever subtype it is handed.
- **One line:** A subtype keeps every promise of its base type, so callers never need to know which one they hold.

### 5.1 Idea

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

- **Overriding vs LSP**
  - Overriding is the Java *mechanism*: a subclass replaces a parent method ([java-oop.md](java-oop.md#4-overriding))
  - LSP is the *rule* the override must follow: callers of the parent must not be surprised
  - The compiler checks only the signature (name, parameters, return type); it can't check that the new code still keeps the promise
- **`UnsupportedOperationException`** is Java's built-in "I have this method but I refuse to do it" exception
  - Example: `List.of(1, 2).add(3)` compiles (it's a `List`, and `List` has `add`), then throws at runtime because the list is immutable
  - An override that throws it is the classic LSP break: the type claims an ability it doesn't have

### 5.2 Mechanism

Callers reason against the contract once, not per subtype.

- Violations surface as type checks in callers
  - The polymorphism stopped paying
- The capability split makes the wrong call a compile error, not a runtime throw

### 5.3 Code

The violation forces `instanceof` in callers; the fix makes gift cards unpassable where a refund is expected.

#### 5.3.1 Violation

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

#### 5.3.2 Fix

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

#### 5.3.3 Contract Test

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

### 5.4 Catch

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

- 🗣 "A subclass compiling isn't enough; it has to behave the way callers of the parent expect. If it can't do something the parent promises, it shouldn't be that subtype."

## 6. Interface Segregation Principle (ISP)

- **In plain words:** don't hand a client a remote with 40 buttons when it presses 2. Give each client a small interface with only the methods it calls.
- **One line:** Clients depend only on the methods they call; interfaces belong to the client.

### 6.1 Idea

No client should depend on methods it does not use.

- Running example (`Isp`)
  - Violation: `OrderStore` with `find`, `save`, `purge`, `exportCsv`
  - The nightly report job only reads but must mock everything
  - Fix: role interfaces `OrderReader`, `OrderWriter`, `OrderAdmin`
  - One adapter implements all three

### 6.2 Mechanism

A smaller dependency surface limits how far a change ripples.

- Changes to unused methods don't ripple to the client
- Test fakes are one or two methods
- One adapter can still implement every role; clients just see less of it

### 6.3 Code

The violation's report fake stubs five methods to use one; the fix depends on the reader role only.

#### 6.3.1 Violation

```java
// concept/_01core_01principles/solid/Isp.java
/** Every client sees every method; a change to purge() touches the report's fakes. */
public interface OrderStore {                      // Isp.Violation.OrderStore
    Optional<Order> find(String id);
    List<Order> findAll();
    void save(Order order);
    int purgeOlderThanDays(int days);
    String exportCsv();
}

/** The report's test fake must stub four methods it never calls. */
public static final class ReportFake implements OrderStore {
    public List<Order> findAll() { return List.of(new Order("o-1", "PAID")); }
    public void save(Order order) { throw new UnsupportedOperationException(); }
    public int purgeOlderThanDays(int days) { throw new UnsupportedOperationException(); }
    public String exportCsv() { throw new UnsupportedOperationException(); }
    // ... find() stubbed too
}
```

```python
# app/concept/_01core_01principles/solid.py
class IspViolationOrderStore(ABC):
    """Fat interface: the read-only report must implement or fake every method."""

    @abstractmethod
    def find_all(self) -> list[IspOrder]: ...

    @abstractmethod
    def save(self, order: IspOrder) -> None: ...

    @abstractmethod
    def purge_older_than_days(self, days: int) -> int: ...

    @abstractmethod
    def export_csv(self) -> str: ...
```

#### 6.3.2 Fix

```java
// concept/_01core_01principles/solid/Isp.java
public interface OrderReader {                     // Isp.Fix.OrderReader
    Optional<Order> find(String id);
    List<Order> findAll();
}
public interface OrderWriter { void save(Order order); }
public interface OrderAdmin { int purgeOlderThanDays(int days); }

/** One adapter can still implement every role; clients just see less of it. */
public static final class InMemoryOrderStore implements OrderReader, OrderWriter, OrderAdmin { /* ... */ }

/** Client depends on the reader role only. */
public static final class NightlyReport {
    private final OrderReader reader;

    public String run() {
        long paid = reader.findAll().stream().filter(o -> o.status().equals("PAID")).count();
        return "paid=" + paid;
    }
}
```

```python
# app/concept/_01core_01principles/solid.py
@runtime_checkable
class OrderReader(Protocol):
    """Declared by the consumer; any object with find_all() fits, without inheriting."""

    def find_all(self) -> list[IspOrder]: ...

@dataclass
class InMemoryOrderStore:
    """Implements reader and writer roles structurally; no base class needed."""

    rows: dict[str, IspOrder] = field(default_factory=dict)

    def find_all(self) -> list[IspOrder]:
        return list(self.rows.values())

    def save(self, order: IspOrder) -> None:
        self.rows[order.id] = order

def nightly_report(reader: OrderReader) -> str:
    """Depends on the reader role only."""
    return f"paid={sum(1 for o in reader.find_all() if o.status == 'PAID')}"
```

- Demo: `Isp.demo()` / `isp_demo()`; Python also prints `isinstance(store, OrderReader)` → `True`
- Use when different clients use disjoint parts of an interface

### 6.4 Catch

Split by client role, not one interface per method.

→ One interface per method.  
⇒ Wiring noise; nobody can see the whole capability.  
→ Split by client role (reader, writer, admin), not by method.

→ Splitting by the provider's internals rather than the client's needs.  
⇒ Clients still need three interfaces for one use case.  
→ Let the consumer define the interface.  
→ In Python a `typing.Protocol` does this structurally, without the provider knowing.

- 🗣 "Interfaces belong to the client, sized to what it calls."

## 7. Dependency Inversion Principle (DIP)

- **In plain words:** business rules shouldn't depend on the database or a vendor SDK. The business code defines the plug shape, and the database adapter fits that plug.
- **One line:** Policy owns the interface; details implement it, so the source arrow points at the policy.

### 7.1 Idea

High-level policy and low-level details both depend on abstractions.

- The abstraction is owned by the policy side (the domain package)
- Running example (`Dip`)
  - Violation: `OrderService` does `new PostgresOrderTable()` and `new SmtpMailer()`
  - Fix: `OrderService(OrderRepository, Notifier)`
  - Ports live with the domain; adapters implement them
- This is the `domain` / `infra` split every 1x slice uses (hexagonal)

### 7.2 Mechanism

Source dependency points opposite to the flow of control.

```text
 control flow:  OrderService ──calls──▶ PostgresAdapter
 source deps:   OrderService ──owns──▶ OrderRepository ◀──implements── PostgresAdapter
```

The adapter imports the domain port; the domain imports nothing from infra.

- Domain compiles and tests without a database or Software Development Kit (SDK)
- Adapters swap without editing the policy

### 7.3 Code

The violation constructs its own details; the fix receives ports and runs with in-memory adapters.

#### 7.3.1 Violation

```java
// concept/_01core_01principles/solid/Dip.java
/** Untestable without Postgres and SMTP; swapping either means editing this class. */
public static final class OrderService {           // Dip.Violation.OrderService
    private final PostgresOrderTable table = new PostgresOrderTable();   // stand-in for a JDBC table class
    private final SmtpMailer mailer = new SmtpMailer();                  // stand-in for an SMTP client

    public String place(Order order) {
        table.insert(order.id());
        mailer.send(order.customerId(), "placed " + order.id());
        return "placed " + order.id() + " via hard-wired Postgres + SMTP";
    }
}
```

```python
# app/concept/_01core_01principles/solid.py
class DipViolationOrderService:
    """Constructs its own details: untestable without Postgres and SMTP."""

    def __init__(self) -> None:
        self._table = _PostgresOrderTable()
        self._mailer = _SmtpMailer()

    def place(self, order: DipOrder) -> str:
        self._table.insert(order.id)
        self._mailer.send(order.customer_id, f"placed {order.id}")
        return f"placed {order.id} via hard-wired Postgres + SMTP"
```

#### 7.3.2 Fix

```java
// concept/_01core_01principles/solid/Dip.java
/** Port shaped on domain needs (save an order), not on a vendor API (putItem, KeyCondition). */
public interface OrderRepository { void save(Order order); }   // Dip.Fix.OrderRepository
public interface Notifier { void notify(String customerId, String message); }

/** Policy: imports only its own ports. */
public static final class OrderService {           // Dip.Fix.OrderService
    private final OrderRepository repo;
    private final Notifier notifier;

    public OrderService(OrderRepository repo, Notifier notifier) {
        this.repo = repo;
        this.notifier = notifier;
    }

    public String place(Order order) {
        repo.save(order);
        notifier.notify(order.customerId(), "placed " + order.id());
        return "placed " + order.id();
    }
}
// InMemoryOrderRepository / RecordingNotifier: test adapters; a JDBC or DynamoDB adapter would sit in infra.
```

```python
# app/concept/_01core_01principles/solid.py
class OrderRepository(Protocol):
    """Port shaped on domain needs, not on a vendor API."""

    def save(self, order: DipOrder) -> None: ...

class Notifier(Protocol):
    def notify(self, customer_id: str, message: str) -> None: ...

@dataclass
class DipOrderService:
    """Policy: depends only on its own ports."""

    repo: OrderRepository
    notifier: Notifier

    def place(self, order: DipOrder) -> str:
        self.repo.save(order)
        self.notifier.notify(order.customer_id, f"placed {order.id}")
        return f"placed {order.id}"
```

- Demo: `Dip.demo()` / `dip_demo()` runs the policy with in-memory adapters: no database, no Simple Mail Transfer Protocol (SMTP)
- Use at architectural boundaries (I/O, vendors, other teams)

### 7.4 Catch

Invert at I/O and vendor boundaries only; shape ports on domain needs, not vendor Application Programming Interfaces (APIs).

→ Dependency Inversion Principle (DIP) is confused with Dependency Injection (DI) and Inversion of Control (IoC).  
⇒ Teams inject concrete classes and believe they "did DIP".  
→ DIP = who owns the interface; DI = how the object arrives; IoC = who controls the flow.

→ A "header interface" for every class, one implementation forever.  
⇒ Double the files, jump-to-definition lands on the interface, no swap ever happens.  
→ Invert at architectural boundaries (I/O, vendors, other teams), not between every pair of classes.

→ The port mirrors the vendor API (`putItem`, `KeyConditionExpression`).  
⇒ The abstraction leaks; swapping DynamoDB for Postgres is impossible anyway.  
→ Shape ports on domain needs: `save(order)`, `findByCustomer(id)`.

- See [IoC and DI](spring.md#3-inversion-of-control) for how Spring does the wiring
- 🗣 "The arrow of source dependency points at the policy, not the database."

## 8. Failure Modes

- What each principle looks like when over- or under-applied

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Class explosion | Single Responsibility Principle (SRP) read as "one method per class" | Feature needs 10 files to read; tiny classes with one caller | Merge by actor / co-change; SRP is per stakeholder |
| LSP break | Subtype throws or tightens checks | `instanceof` in callers; contract tests fail on one impl | Split capability interfaces; compose |
| Fat interface | One interface for all clients | Mocks stub many unused methods | Role interfaces per client |
| Leaky port | Port mirrors vendor API | Domain code mentions Software Development Kit (SDK) types/expressions | Reshape port around domain operations |

## 9. Interview Questions

- 20 classic questions, grouped by principle; each has an intuitive line, an L4 answer and an L5 extra
- Index: [9.1 Overview (Q1–Q3)](#91-overview) · [9.2 SRP (Q4–Q6)](#92-srp) · [9.3 OCP (Q7–Q10)](#93-ocp) · [9.4 LSP (Q11–Q14)](#94-lsp) · [9.5 ISP (Q15–Q16)](#95-isp) · [9.6 DIP (Q17–Q18)](#96-dip) · [9.7 Putting it together (Q19–Q20)](#97-putting-it-together)

### 9.1 Overview

#### Q1 What is SOLID and why does it matter?

**Intuitive:** SOLID is five habits for arranging classes so the next change is cheap and safe.

**L4 answer**

- Five principles: Single Responsibility, Open-Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- SRP: a class changes for one group of people only
- OCP: a new kind of thing is a new class, not an edit to working code
- LSP: a subclass behaves the way callers of the parent expect
- ISP: each caller gets a small interface with only what it uses
- DIP: business code owns the interface, and the database or vendor code implements it
- It matters because most of a service's cost is later changes, not the first version

**L5 extra**

- SOLID is a cost model for change; it does not speed up the first delivery, it adds files and indirection up front
- It pays back when many people work in the code, the service lives for years, and changes arrive along the axis you abstracted
- Two forces do the work: cohesion goes up (SRP, ISP), coupling goes down (DIP, OCP); LSP is the guard that keeps substitution safe
- It does not pay back in short scripts, prototypes and one-off jobs, where a plain function beats five interfaces
- Measure it: diff size per change request, merge conflicts, and how many methods a test fake must stub; if none improve, you added ceremony
- History: Martin collected the principles around 2000, Michael Feathers coined the acronym, and OCP (Meyer, 1988) and LSP (Liskov, 1987) are older
- In my own words: "I apply a principle when I can name the future change it makes cheaper."

#### Q2 Are the SOLID principles rules? When do you break them?

**Intuitive:** They are rules of thumb, like "warm up before you run"; sensible by default, silly for a 20-line script.

**L4 answer**

- They are guidelines, not laws
- I apply one when I can name a concrete change or test it makes easier
- I skip it when the abstraction costs more than it saves
- Example: a one-off job with a single implementation does not need an interface
- I keep a concrete class until a second variant really appears

**L5 extra**

- Every principle has a price: SRP adds classes, OCP adds indirection, DIP adds interfaces and wiring, ISP adds more interfaces
- Principles conflict: OCP wants extension points, YAGNI says don't build them yet; the tie-breaker is the rule of three (extract on the second or third real variant)
- Sandi Metz: duplication is far cheaper than the wrong abstraction
- Invert dependencies at I/O and vendor boundaries; don't put an interface between every pair of classes
- Evidence beats taste: `git log` shows which files change together
- A team's consistent conventions often matter more than local purity
- In review I flag a violation only when I can point at a change that hurts today

#### Q3 Explain SOLID with an example from your own systems

**Intuitive:** Pick one real service and show where each of the five shows up.

**L4 answer**

- SRP: a data-platform ingestion service split into parse, validate, persist, publish; each owned by a different concern
- OCP: new file formats are added as new `RecordParser` implementations in a registry
- LSP: every parser honors the same contract, with the same errors on bad input and no extra exceptions
- ISP: the reporting job depends on `OrderReader` only, not on writer or admin methods
- DIP: the service depends on a `LakeWriter` port; S3 and Delta adapters implement it

**L5 extra**

- I apply them at boundaries, not everywhere: DIP at I/O, OCP only where variants exist
- I name the cost: each interface is a file and an indirection, accepted only where a change or a test needs it
- I can show the payoff with a real change: a new format touched one new class and one registration line
- The failure I watch for is the opposite of SOLID: 30 tiny classes where one flow spans a dozen files
- If asked what I would not do again: an interface with one implementation that never gained a second

### 9.2 SRP

#### Q4 What is SRP? Does it mean a class should have one method?

**Intuitive:** A class should have one boss; if three different teams can force you to edit it, it has three jobs.

**L4 answer**

- SRP: a class has one reason to change, and a "reason" is one group of people who ask for changes (an actor)
- It is not "does one thing"; that rule is for functions
- `PriceCalculator` can have five methods and still be fine, because all five are finance rules
- `OrderService.place()` has one method but is not fine, because finance (tax), ops (storage) and marketing (email wording) all edit it

**L5 extra**

- Mechanism: each actor's change request lands in a different file, so diffs are smaller, merge conflicts drop, and tests target one reason
- Two classes touching the same database table is fine; SRP is about who changes the code, not where the data lives
- Wrong split 1: one-method classes everywhere gives 40 classes and a flow nobody can follow
- Wrong split 2: splitting by technical layer (validator, mapper, DAO) means every feature still edits all of them, which is shotgun surgery
- Actors usually map to teams, so SRP is partly Conway's law
- Test it with evidence: methods that share fields and change in the same commits belong together
- Source: Martin, *Clean Architecture* (2017); the early "one reason to change" wording was often misread as "one method"

#### Q5 How do you decide when to split a class?

**Intuitive:** Split when two different groups start tripping over each other in the same file.

**L4 answer**

- Split when two different actors request changes independently
- Signals: unrelated groups of fields, frequent merge conflicts, tests that need unrelated setup
- Don't split just because a class is long

**L5 extra**

- Use evidence: `git log` co-change shows which methods change together
- Check the direction of the pain: if a feature edits five files at once, I split along the wrong line and should merge
- Prefer extracting one collaborator with a clear owner over breaking a class into many pieces at once
- Keep the coordinator thin: it only calls the pieces, with no rules of its own
- Over-splitting is a real failure; if a feature now spans 10 tiny classes, I merge by actor
- Refactor in small, test-backed steps, one extraction per commit

#### Q6 This Spring service does three things. How do you fix it?

```java
@Service
class OrderService {
    public void place(Order o) {
        BigDecimal total = o.subtotal().multiply(new BigDecimal("1.08")); // finance
        jdbc.update("insert into orders ...", o.id(), total);              // ops
        mailer.send(o.email(), "Thanks! You paid " + total);               // marketing
    }
}
```

**Intuitive:** Give each of the three jobs its own class, and let `OrderService` only call them in order.

**L4 answer**

- Extract `PriceCalculator` (finance), `OrderRepository` (ops) and `OrderNotifier` (marketing)
- `OrderService` receives them through its constructor and only coordinates: price, save, notify
- A tax change now edits only `PriceCalculator`
- Tests can fake the repository and the notifier

**L5 extra**

- `@Transactional` stays on `OrderService.place`, because it owns the unit of work
- The email must not be sent inside the transaction: if the commit fails, the customer got a mail for an order that doesn't exist
- Better: send after commit (`@TransactionalEventListener(phase = AFTER_COMMIT)`), or write an outbox row in the same transaction and let a relay send it
- Don't over-split: if the tax rule is one line used in one place, a private method is enough
- Watch for circular dependencies between the new classes; the coordinator should depend on them, never the reverse
- Verify by change request: "change the tax rate" should touch one file

### 9.3 OCP

#### Q7 What is OCP? Does it mean you can never edit old code?

**Intuitive:** A new payment method should be a new class, not an edit to the `if/else` that already works.

**L4 answer**

- OCP: open for extension, closed for modification
- Adding a new variant (Apple Pay) should not edit tested code (`Card`, `PayPal`, the processor)
- You get that with an interface plus registered implementations in place of a `switch`
- Old code is not frozen: fixing a bug, or changing the rule of one variant (Card adds 3-D Secure), is a normal edit

**L5 extra**

- "Closed" is relative to one kind of change; you can only be closed against variation you chose
- The interface stays stable; adding a new *operation* to it is the case OCP does not protect you from (expression problem, Q10)
- The mechanism is polymorphism: the caller depends on the interface, the JVM picks the implementation at runtime
- Registration (a map, or Spring injecting `List<PaymentMethod>`) replaces the branch, so new behavior is additive
- Benefit: the tested class stays untouched, so no regression risk and no merge conflict on it
- Cost: indirection; a reader must find all implementations to know what runs
- Meyer's original version (1988) used inheritance; Martin's later version uses interfaces

#### Q8 How do you implement OCP in Java and Spring?

```java
interface PaymentMethod { String name(); String charge(BigDecimal amount); }

@Component class PaymentProcessor {
    private final Map<String, PaymentMethod> methods = new HashMap<>();
    PaymentProcessor(List<PaymentMethod> all) {              // Spring injects every bean
        for (PaymentMethod m : all)
            if (methods.putIfAbsent(m.name(), m) != null)
                throw new IllegalStateException("duplicate " + m.name());
    }
    String pay(String name, BigDecimal amt) {
        PaymentMethod m = methods.get(name);
        if (m == null) throw new IllegalArgumentException("unsupported " + name);
        return m.charge(amt);
    }
}
```

**Intuitive:** Define the shape once, drop new implementations in, and let Spring collect them.

**L4 answer**

- Define an interface (`PaymentMethod`) and one `@Component` per variant
- Spring injects `List<PaymentMethod>` into the processor
- The processor builds a map by name and looks up the right one
- Adding Apple Pay means adding one class; nothing else changes

**L5 extra**

- The duplicate-name check is not OCP itself; it protects the registry, because dropped-in classes could silently shadow each other, and now that fails at startup
- Unknown names fail with a clear message listing the known names
- Alternatives: `Map<String, PaymentMethod>` injection (Spring uses bean names as keys), `@ConditionalOnProperty` to enable variants, `ServiceLoader` for plugins outside Spring
- Order matters when variants overlap: use `@Order` or `Ordered` and document it
- Test: one contract test run against every implementation, plus a test that the registry rejects duplicates
- Watch for hidden coupling: a bean's name or `name()` becoming an external API (stored in the database), so renames break data

#### Q9 `if/else` chain, strategy or enum switch: which do you use?

**Intuitive:** Use a switch when the list is fixed; use classes when the list keeps growing.

**L4 answer**

- A short, stable `if/else` is fine
- A chain repeated in several places, or growing with every release, becomes strategy classes behind an interface
- A fixed set (days, fee kinds) is best as an enum with an exhaustive `switch`
- The deciding question is whether new variants keep arriving

**L5 extra**

- Strategy makes new types cheap and new operations expensive; a `switch` is the reverse (expression problem, see [java-oop.md](java-oop.md#7-the-expression-problem))
- Java 17: enum switch expressions are checked for exhaustiveness, so adding a constant breaks the build at every `switch`
- Java 21: sealed interfaces + pattern `switch` give the same check for class hierarchies
- A repeated `switch` on the same type in many files is the real smell: that's the signal to move behavior into the type
- Don't introduce an interface for two stable branches; the interface plus registry costs more than the `if`
- If both axes grow, consider the Visitor pattern, accepting its ceremony

#### Q10 When does OCP backfire?

**Intuitive:** Building plug-in points for changes that never come just gives you more code to read.

**L4 answer**

- Speculative interfaces: one implementation, never a second
- Wrong axis: you built for new payment methods, and the change that arrived was a new currency
- Adding an operation to an interface forces every class to change anyway
- Rule: wait until the variation has happened two or three times

**L5 extra**

- Vocabulary: a variation is what keeps changing; closing against it means shaping the code so that kind of change needs no edits to old code
- Wrong-axis failure: the abstraction is aligned to the wrong dimension, so the real change edits four classes instead of one
- Expression problem: `refund()` added to `PaymentMethod` edits `Card`, `PayPal` and `ApplePay`
- Speculative generality is the classic code smell; it conflicts with YAGNI
- Costs show up as one-implementation interfaces, factories nobody extends, and config-driven loading nobody uses
- Remedy: keep a concrete class, wait for the rule of three, then extract; refactoring is cheap when tests exist
- When you do extract, the interface should be born with at least two real implementations

### 9.4 LSP

#### Q11 What is LSP? Is a Square a Rectangle?

**Intuitive:** A replacement part must fit like the original; code that accepts the parent keeps working with any child.

**L4 answer**

- LSP: wherever the base type is expected, any subtype can be used without surprising the caller
- Rectangle/Square: `Square extends Rectangle` and overrides `setWidth` to also change the height
- Code that sets width 5 and height 4 on a `Rectangle` expects area 20; with a `Square` it gets 16
- In math a square is a rectangle; in code, behavior decides, so `Square` must not inherit `Rectangle`
- Fix: don't inherit; use an immutable shape type or separate types

**L5 extra**

- Formally (Liskov & Wing 1994): preconditions are not strengthened, postconditions are not weakened, invariants are preserved, no unexpected new exceptions
- The compiler checks only signatures; the broken promise here is "width and height are independent"
- Immutability helps: with no setters, a `Square` and a `Rectangle` can both implement `Shape`
- Inheritance used only to reuse code is a warning sign; composition avoids the substitution trap
- The smell in callers is `instanceof` checks or type flags: they mean polymorphism stopped paying
- Related rule: overriding methods may widen visibility and narrow return types, but never throw new checked exceptions

#### Q12 `GiftCardPayment.refund()` throws `UnsupportedOperationException`. What's wrong and how do you fix it?

**Intuitive:** The type claims an ability it doesn't have, so callers can't trust it.

**L4 answer**

- The base `Payment` promises `refund()` works; `GiftCardPayment` breaks that promise at runtime
- Callers start writing `if (p instanceof GiftCardPayment)` to protect themselves
- Fix: split the capability: `Payment` for all, `Refundable extends Payment` only for types that can refund
- Now a gift card cannot be passed where a refund is expected; the mistake becomes a compile error

**L5 extra**

- The fix moves the failure from runtime to compile time
- `refundAll(List<? extends Refundable>)` needs no type checks
- This is also an ISP move: small capability interfaces sized to what callers need
- Alternative: keep the method, but make "not supported" part of the contract (return a result type like `RefundResult.NOT_ALLOWED`); the caller must then handle it, which is honest but pushes work to every caller
- Don't use `instanceof` ladders to patch around it; they spread knowledge of subtypes everywhere
- Write one contract test for `Refundable` and run it against every implementation

#### Q13 How do you detect LSP violations?

**Intuitive:** Run the same checks against every implementation, and watch for callers that need to know which one they hold.

**L4 answer**

- Look for `instanceof` checks and casts in callers
- Look for overrides that throw `UnsupportedOperationException` or do nothing
- Write one contract test suite and run it against every implementation
- Code review: "does this subtype keep every promise of the parent?"

**L5 extra**

- Compilers check signatures, never behavior; a subtype can compile and still break callers (stricter validation, different rounding, different ordering)
- A contract test is parameterized: the same behavior assertions run with each implementation as input (JUnit parameterized tests, pytest parametrize)
- It only checks what you wrote down; unstated promises like latency or thread safety still drift
- Property-based testing finds violations of invariants by trying many inputs
- Static signals: overriding methods with narrower inputs, extra preconditions, or new thrown exceptions
- Production signal: a subtype causing errors only in one code path, found by tracing callers

#### Q14 Does `List.of(...).add(x)` throwing violate LSP? Is the JDK wrong?

**Intuitive:** Yes, the JDK knowingly traded a clean type hierarchy for fewer interfaces.

**L4 answer**

- `List.of` returns an immutable list, but its type is still `List`, which promises `add`
- Calling `add` compiles, then throws `UnsupportedOperationException`
- So it is an LSP break; the `Collection` docs call these "optional operations"
- You must know where the list came from before you can safely modify it

**L5 extra**

- The JDK chose this to avoid a large family of interfaces (`ImmutableList`, `ReadOnlyList`, …)
- Cost: callers can't trust the type alone; defensive copies (`new ArrayList<>(list)`) become common
- `Arrays.asList` is similar: `set` works, `add` throws, because the size is fixed
- Python's `collections.abc` splits `Sequence` from `MutableSequence`, which is the capability-split approach
- Guava's `ImmutableList` makes the immutability visible in the type
- In my code: expose read-only views as read-only types (`Collection` or `Iterable`) in method signatures, and copy at boundaries
- Lesson: a deliberate LSP break is acceptable only when documented, but the safe default is a type that tells the truth

### 9.5 ISP

#### Q15 What is ISP? Give an example.

**Intuitive:** Don't hand a client a remote with 40 buttons when it only presses two.

**L4 answer**

- ISP: no client should depend on methods it doesn't use
- Example: `OrderStore` with `find`, `save`, `purge`, `exportCsv`; the nightly report only reads
- Its test fake must stub four methods it never calls
- Fix: role interfaces `OrderReader`, `OrderWriter`, `OrderAdmin`; one adapter can implement all three

**L5 extra**

- Smaller dependency surface limits the blast radius: changes to `purge` don't ripple to the report
- Test fakes become one or two methods, and mocks stay readable
- The interface belongs to the client: let the consumer define what it needs, sized to what it calls
- In Python, `typing.Protocol` does this structurally, with no inheritance from the provider
- Wrong split: one interface per method creates wiring noise and hides the whole capability
- Wrong split: splitting by the provider's internals instead of the client's needs; clients then need three interfaces for one use case
- Spring Data does this with `CrudRepository` vs `ReadOnlyRepository`-style custom interfaces

#### Q16 What's the difference between ISP and SRP?

**Intuitive:** SRP is about who changes a class; ISP is about what a caller is forced to depend on.

**L4 answer**

- SRP looks at the class: one group of people asks for changes
- ISP looks at the interface from the caller's side: only the methods it calls
- A class can follow SRP and still expose a fat interface
- Both reduce the effect of changes

**L5 extra**

- SRP is about the provider's reasons to change; ISP is about the consumer's dependencies
- An ISP violation hurts at compile time and test time; an SRP violation hurts at edit time
- Fixing a fat interface often reveals an SRP issue in the class behind it, and the reverse
- A single class can implement several small interfaces: SRP is satisfied if all of them change for the same actor
- Related: LSP gets easier when interfaces are small, because there is less to promise
- Both are cohesion tools; the difference is the viewpoint (class vs client)

### 9.6 DIP

#### Q17 DIP vs Dependency Injection vs Inversion of Control?

**Intuitive:** DIP says who owns the plug shape; DI is how the plug arrives; IoC is who's in charge of the program flow.

**L4 answer**

- IoC: the framework controls the flow and calls my code (Spring creates and calls beans)
- DI: dependencies are supplied from outside, usually through the constructor
- DIP: high-level policy owns the abstraction, and low-level details implement it

**L5 extra**

- You can do DI without DIP: inject a concrete `PostgresOrderRepository` and nothing is inverted
- You can do DIP without a container: wire by hand in `main`
- The DIP test: does the domain package import the database or vendor SDK? If yes, the arrow points the wrong way
- Source dependency points opposite to control flow: the service calls the adapter, but the adapter imports the service's port
- Constructor injection is preferred: dependencies are explicit, required and the fields can be `final`
- The port should be shaped on domain needs (`save(order)`), not on a vendor API (`putItem`, `KeyConditionExpression`), or the abstraction leaks

#### Q18 How does DIP help testing, and do you need an interface for every class?

**Intuitive:** An interface at the boundary lets a test plug in a fake instead of a real database.

**L4 answer**

- With DIP, `OrderService(OrderRepository, Notifier)` runs with in-memory fakes, with no database or mail server
- Unit tests become fast and deterministic
- Adapters (JDBC, DynamoDB, SMTP) swap without editing the service
- No: not every class needs an interface; use one at architectural boundaries (I/O, vendors, other teams)

**L5 extra**

- A "header interface" for every class, with one implementation forever, doubles the files and gets in the way of navigation
- Hexagonal architecture applies DIP at scale: ports live with the domain, adapters in `infra`
- You still need integration tests for the real adapters; fakes can hide mismatches (SQL dialects, serialization)
- Mock libraries (Mockito) can mock concrete classes, so interfaces are not strictly needed for testing; they are needed when the owner of the abstraction should be the domain
- Layer rule: dependencies point inward toward the domain, never outward
- Cost to name: wiring complexity and more indirection; accept it where a swap or a test needs it

### 9.7 Putting it together

#### Q19 How do SOLID principles relate to design patterns?

**Intuitive:** The principles are the "why"; patterns are tried-and-true recipes for the "how".

**L4 answer**

- Strategy and Factory realize OCP: new behavior is a new class
- Adapter and Repository realize DIP: the domain owns the port, the adapter implements it
- Decorator realizes OCP and composition: add behavior by wrapping
- Template Method and State also rely on polymorphism and LSP

**L5 extra**

- Patterns are applications of the principles at a smaller scale, and each carries a cost
- Strategy: OCP and DIP together; Observer: loose coupling; Facade: reduces dependency surface (ISP flavor)
- The principle tells you when a pattern pays off; the pattern is not the goal
- Pattern overuse is the usual failure: AbstractFactoryFactory-style code
- Frameworks bake them in: Spring is IoC + DI + proxies (Decorator-like AOP)
- In an interview, say which principle drove the pattern and what change it makes cheaper

#### Q20 Review this code: which principles does it break and how would you fix it?

```java
class ReportService extends BaseService {
    private final MySqlOrderRepo repo = new MySqlOrderRepo();

    public String build(String type) {
        List<Order> orders = repo.findAll();
        String out;
        if (type.equals("PDF")) { out = toPdf(orders); }
        else if (type.equals("CSV")) { out = toCsv(orders); }
        else { throw new IllegalArgumentException(type); }
        repo.markExported(orders);
        mailer.send("ops@x.com", out);
        return out;
    }
}
```

**Intuitive:** Look for who asks for changes, what grows with every variant, what is hard-wired, and what is borrowed from a parent.

**L4 answer**

- SRP: `build` formats, marks rows exported and sends email; ops, finance and the report owner all edit it
- OCP: the `PDF`/`CSV` chain is edited for every new format
- DIP: `new MySqlOrderRepo()` hard-wires a database, so tests need MySQL
- Fix: `ReportFormatter` interface with `PdfFormatter`, `CsvFormatter`; inject `OrderRepository` and `Notifier` through the constructor
- Keep `ReportService` as the coordinator

**L5 extra**

- ISP: if `MySqlOrderRepo` exposes read, write and admin methods, the report should depend on only a reader plus a `markExported` role
- LSP: if `BaseService` has methods this class overrides with weaker behavior or throws, callers of `BaseService` break; also ask whether `extends` is needed (composition)
- Side effects order: marking rows exported and then failing to send leaves data in a wrong state; use a transaction or an outbox, and make the send idempotent
- The `markExported` call is a command mixed with a query-like `build`: split into `generate` and `markExported`
- Don't over-fix: two formats that rarely change may stay as an enum `switch`; the interface is justified only if formats keep arriving
- Test plan: formatter contract test across implementations, service test with fakes, integration test for the real repository
- State the order I would refactor in: DIP first (makes tests possible), then SRP extraction, then OCP for formats

## 10. Code Map

- Java `1x/java/src/main/java/com/lc/x/concept/_01core_01principles/solid/`; Python `1x/python/app/concept/_01core_01principles/solid.py`
- Enable: Java `x.principles.enabled=true`; Python `X_ENABLED=principles`; then GET `/principles/{name}`
- Every Java principle has nested `Violation` and `Fix` types and a static `demo()`; every Python principle has `<name>_demo()`

| File | Java | Python |
|---|---|---|
| [Single Responsibility Principle (SRP)](#3-single-responsibility-principle-srp) | `Srp.Violation.OrderService.place` vs `Srp.Fix.OrderService.place`, `Srp.demo` | `SrpViolationOrderService.place` vs `SrpOrderService.place`, `srp_demo` |
| [Open-Closed Principle (OCP)](#4-open-closed-principle-ocp) | `Ocp.Violation.PaymentProcessor.pay` vs `Ocp.Fix.PaymentProcessor.pay` (+ closed set `Fix.FeeKind` / `Fix.fee`), `Ocp.demo` | `OcpViolationProcessor.pay` vs `OcpPaymentProcessor.pay`, `ocp_demo` |
| [Liskov Substitution Principle (LSP)](#5-liskov-substitution-principle-lsp) | `Lsp.Violation.GiftCardPayment.refund` vs `Lsp.Fix.Refundable`, `Lsp.Fix.contractHolds`, `Lsp.demo` | `LspViolationGiftCard.refund` vs `Refundable`, `contract_holds`, `lsp_demo` |
| [Interface Segregation Principle (ISP)](#6-interface-segregation-principle-isp) | `Isp.Violation.OrderStore` vs `Isp.Fix.{OrderReader,OrderWriter,OrderAdmin}`, `Isp.Fix.NightlyReport.run`, `Isp.demo` | `IspViolationOrderStore` vs `OrderReader` (Protocol), `nightly_report`, `isp_demo` |
| [Dependency Inversion Principle (DIP)](#7-dependency-inversion-principle-dip) | `Dip.Violation.OrderService` vs `Dip.Fix.OrderService(OrderRepository, Notifier)`, `Dip.demo` | `DipViolationOrderService` vs `DipOrderService`, `dip_demo` |

## References

- [Robert C. Martin — The Principles of Object-Oriented Design (OOD)](http://butunclebob.com/ArticleS.UncleBob.PrinciplesOfOod) — Single Responsibility, Open-Closed, Liskov Substitution, Interface Segregation, Dependency Inversion (SOLID) papers index
- [Liskov & Wing, "A Behavioral Notion of Subtyping", Association for Computing Machinery (ACM) Transactions on Programming Languages and Systems (TOPLAS) 1994](https://doi.org/10.1145/197320.197383) — formal LSP
