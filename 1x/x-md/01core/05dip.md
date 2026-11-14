# 01core.01principles.05dip Dependency Inversion Principle (DIP)

> Policy owns the interface; details implement it, so the source arrow points at the policy.

## Index

- [1. Idea](#1-idea)
- [2. Mechanism](#2-mechanism)
- [3. Code](#3-code)
  - [3.1 Violation](#31-violation)
  - [3.2 Fix](#32-fix)
- [4. Catch](#4-catch)

Part A, SOLID (Java + Python). Back to [00index](00index.md).

## 1. Idea

High-level policy and low-level details both depend on abstractions.

- The abstraction is owned by the policy side (the domain package)
- Running example (`Dip`)
  - Violation: `OrderService` does `new PostgresOrderTable()` and `new SmtpMailer()`
  - Fix: `OrderService(OrderRepository, Notifier)`
  - Ports live with the domain; adapters implement them
- This is the `domain` / `infra` split every 1x slice uses (hexagonal)

## 2. Mechanism

Source dependency points opposite to the flow of control.

```text
 control flow:  OrderService ──calls──▶ PostgresAdapter
 source deps:   OrderService ──owns──▶ OrderRepository ◀──implements── PostgresAdapter
```

The adapter imports the domain port; the domain imports nothing from infra.

- Domain compiles and tests without a database or Software Development Kit (SDK)
- Adapters swap without editing the policy

## 3. Code

The violation constructs its own details; the fix receives ports and runs with in-memory adapters.

### 3.1 Violation

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

### 3.2 Fix

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

## 4. Catch

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

- See [IoC and DI](11ioc-di-pojo.md) for how Spring does the wiring
- 🗣 "The arrow of source dependency points at the policy, not the database."
