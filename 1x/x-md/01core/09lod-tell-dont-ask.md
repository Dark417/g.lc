# 01core.01principles.09lod-tell-dont-ask Law Of Demeter And Tell Dont Ask

> Talk only to direct collaborators, and tell objects to act instead of pulling their state.

## Index

- [1. Law Of Demeter](#1-law-of-demeter)
  - [1.1 Idea](#11-idea) · [1.2 Code](#12-code) · [1.3 Catch](#13-catch)
- [2. Tell Dont Ask](#2-tell-dont-ask)
  - [2.1 Idea](#21-idea) · [2.2 Code](#22-code) · [2.3 Catch](#23-catch)

Part B, general principles (Java + Python). Back to [00index](00index.md).

## 1. Law Of Demeter

A method should not depend on the structure of distant objects.

### 1.1 Idea

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

### 1.2 Code

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

### 1.3 Catch

Chains over plain data and fluent Application Programming Interfaces (APIs) are fine; Law of Demeter (LoD) targets behavior.

→ LoD read as "count the dots".  
⇒ Fluent builders, streams, and record navigation get wrapped for no gain.  
→ Chains that return the same type or plain data are fine; LoD targets behavior-rich objects.

→ Strict LoD on a middle object.  
⇒ It grows dozens of forwarding methods (wide interface).  
→ Pass the needed value in, or move the behavior to where the data is.

- 🗣 "Dots are fine on data and fluent APIs; LoD is about behavior-rich objects."

## 2. Tell Dont Ask

Put the decision next to the data that guards the invariant.

### 2.1 Idea

- Tell an object what to do
- Don't pull its state and decide for it
- Running example (`TellDontAsk`)
  - Violation: service checks `wallet.balance() >= amount` then sets the new balance
  - Fix: `wallet.debit(amount)` enforces "no overdraft" inside
- **Mechanism**
  - The invariant lives in one place, next to the data that guards it

### 2.2 Code

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

### 2.3 Catch

Queries for display are fine (Command-Query Separation, CQS); don't push I/O into entities.

→ Applied to reporting and display.  
⇒ Entities grow `printInvoice`, `toCsv`, `renderHtml`.  
→ Queries for display are fine (that is CQS's "query" side, [10cqs](10cqs-failfast-pola.md#1-command-query-separation)).

→ Everything pushed into entities.  
⇒ God entities that need mailers and repositories.  
→ Entities guard invariants; services orchestrate I/O.

→ Data pipelines (Spark, Databricks) are function-over-data, not objects.  
⇒ Tell-don't-ask does not apply to a DataFrame transform.  
→ Use it for stateful domain objects only.

- 🗣 "Put the decision next to the data that guards the invariant."
