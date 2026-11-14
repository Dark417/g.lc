# 01core.01principles.01srp Single Responsibility Principle (SRP)

> One module answers to one actor, so each stakeholder's change lands in one file.

## Index

- [1. Idea](#1-idea)
- [2. Mechanism](#2-mechanism)
- [3. Code](#3-code)
  - [3.1 Violation](#31-violation)
  - [3.2 Fix](#32-fix)
- [4. Catch](#4-catch)
- [References](#references)

Part A, SOLID (Java + Python).

- Name and grouping: Robert C. Martin, "Design Principles and Design Patterns" (2000)
- Acronym: Michael Feathers
- Shared goal of SOLID: classes whose changes stay local and whose substitutes are safe
- Back to [00index](00index.md)

## 1. Idea

Single Responsibility Principle (SRP) is about who asks for changes, not how many methods a class has.

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

## 2. Mechanism

Each actor's change request lands in a different file.

- Smaller diffs
- Fewer merge conflicts
- Tests target one reason
- Both versions produce the same output; only the cost per change request differs

## 3. Code

The violation mixes three actors' rules in one method; the fix gives each actor a class.

### 3.1 Violation

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

### 3.2 Fix

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

## 4. Catch

Split by actor, not by method; one-method classes everywhere is the opposite failure.

→ "One reason" is read as "one method".  
⇒ 40 one-method classes; the flow is spread across files and hard to follow.  
→ Split only when two actors really change the code independently.

→ The split follows technical layers instead of actors.  
⇒ Every feature still edits all the classes (shotgun surgery).  
→ Test: do these methods share fields and change in the same commits? Then they belong together.

- 🗣 "One reason to change means one stakeholder, not one method."

## References

- [Robert C. Martin — The Principles of Object-Oriented Design (OOD)](http://butunclebob.com/ArticleS.UncleBob.PrinciplesOfOod) — Single Responsibility, Open-Closed, Liskov Substitution, Interface Segregation, Dependency Inversion (SOLID) papers index
