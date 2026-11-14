# 01core.01principles.04isp Interface Segregation Principle (ISP)

> Clients depend only on the methods they call; interfaces belong to the client.

## Index

- [1. Idea](#1-idea)
- [2. Mechanism](#2-mechanism)
- [3. Code](#3-code)
  - [3.1 Violation](#31-violation)
  - [3.2 Fix](#32-fix)
- [4. Catch](#4-catch)

Part A, SOLID (Java + Python). Back to [00index](00index.md).

## 1. Idea

No client should depend on methods it does not use.

- Running example (`Isp`)
  - Violation: `OrderStore` with `find`, `save`, `purge`, `exportCsv`
  - The nightly report job only reads but must mock everything
  - Fix: role interfaces `OrderReader`, `OrderWriter`, `OrderAdmin`
  - One adapter implements all three

## 2. Mechanism

A smaller dependency surface limits how far a change ripples.

- Changes to unused methods don't ripple to the client
- Test fakes are one or two methods
- One adapter can still implement every role; clients just see less of it

## 3. Code

The violation's report fake stubs five methods to use one; the fix depends on the reader role only.

### 3.1 Violation

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

### 3.2 Fix

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

## 4. Catch

Split by client role, not one interface per method.

→ One interface per method.  
⇒ Wiring noise; nobody can see the whole capability.  
→ Split by client role (reader, writer, admin), not by method.

→ Splitting by the provider's internals rather than the client's needs.  
⇒ Clients still need three interfaces for one use case.  
→ Let the consumer define the interface.  
→ In Python a `typing.Protocol` does this structurally, without the provider knowing.

- 🗣 "Interfaces belong to the client, sized to what it calls."
