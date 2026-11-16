# Java OOP — Classes, Inheritance, Overriding, Polymorphism

- **In plain words:** object-oriented programming bundles data with the code that uses it, and lets one piece of calling code work with many kinds of objects, each doing the right thing for itself.
- Light on syntax, heavy on mechanism; Java 17 with notes for 21
- Used by: [solid.md](solid.md) (OCP, LSP lean on overriding and polymorphism), [design-principles.md](design-principles.md) (composition over inheritance), [design-patterns.md](design-patterns.md)

## Index

- [0. One-Minute Version](#0-one-minute-version)
- [1. The Four Pillars](#1-the-four-pillars)
- [2. Encapsulation](#2-encapsulation)
- [3. Inheritance, Abstract Classes, Interfaces](#3-inheritance-abstract-classes-interfaces)
- [4. Overriding](#4-overriding)
- [5. Overloading vs Overriding](#5-overloading-vs-overriding)
- [6. Polymorphism And Dynamic Dispatch](#6-polymorphism-and-dynamic-dispatch)
- [7. The Expression Problem](#7-the-expression-problem)
- [8. Composition Over Inheritance](#8-composition-over-inheritance)
- [9. Modern Java: Records, Sealed Types, Pattern Matching](#9-modern-java-records-sealed-types-pattern-matching)
- [10. equals And hashCode](#10-equals-and-hashcode)
- [11. Interview Questions](#11-interview-questions)
- [References](#references)

---

## 0. One-Minute Version

- **What:** classes bundle state + behavior; subtypes reuse or replace behavior; callers program against a supertype
- **Why:** one caller works with many implementations, so new kinds of objects plug in without editing the caller
- **How:** the JVM picks the method to run from the object's **actual** class at runtime (dynamic dispatch)
- **Catch:** this makes new *types* cheap and new *operations* expensive (the expression problem); and inheritance couples a subclass tightly to its parent
- 🗣 "Overloading is picked by the compiler from declared types; overriding is picked at runtime from the actual object. That runtime choice is polymorphism."

---

## 1. The Four Pillars ★★★

| Pillar | Plain meaning | Java tool | Main risk |
|---|---|---|---|
| Encapsulation | Hide the data; expose only safe operations | `private` fields, methods that enforce rules | Getters and setters for everything = no real hiding |
| Abstraction | Callers see *what* it does, not *how* | Interfaces, abstract classes | Abstractions with one implementation forever |
| Inheritance | A subtype reuses and extends a parent | `extends`, `implements` | Tight coupling to parent internals |
| Polymorphism | One call, many behaviors depending on the object | Overriding + a supertype reference | Subtypes that break the parent's promises (LSP) |

---

## 2. Encapsulation ★★

- **In plain words:** the object guards its own data, so no outside code can put it in an invalid state.

```java
public final class Account {
    private long balanceCents;                      // nobody outside can set this directly
    public void withdraw(long cents) {
        if (cents <= 0 || cents > balanceCents) throw new IllegalArgumentException("bad amount");
        balanceCents -= cents;                      // the rule lives next to the data
    }
    public long balanceCents() { return balanceCents; }
}
```

| Modifier | Visible to |
|---|---|
| `private` | Same class only |
| (none, package-private) | Same package |
| `protected` | Same package + subclasses |
| `public` | Everyone |

- Catch: a public setter `setBalance()` would undo the whole point; tell the object what to do (Tell, Don't Ask)

---

## 3. Inheritance, Abstract Classes, Interfaces ★★★

- **In plain words:** an interface is a promise of abilities; an abstract class is a half-built parent that shares code; a concrete class is the real thing.

| | Interface | Abstract class | Concrete class |
|---|---|---|---|
| Can be instantiated | No | No | Yes |
| State (fields) | Constants only | Yes | Yes |
| Method bodies | `default` and `static` methods (Java 8+), `private` (Java 9+) | Yes | Yes |
| Constructors | No | Yes (called by subclasses) | Yes |
| How many per class | Implement many | Extend one | Extend one |
| Use for | A capability many unrelated classes share (`Comparable`, `PaymentMethod`) | A family sharing code and state (template method) | The actual implementation |

- Constructor chaining: a subclass constructor always calls a parent constructor first (`super(...)`, implicit if omitted)
- `final class` cannot be extended; `final` method cannot be overridden
- Default: interfaces for types callers depend on; abstract classes only to share real code inside one family

---

## 4. Overriding ★★★

- **In plain words:** a subclass provides its own version of a method the parent already has, and that version runs whenever the object is really the subclass.

```java
interface PaymentMethod { String charge(long cents); }

final class Card implements PaymentMethod {
    @Override public String charge(long cents) { return "card " + cents; }
}
final class PayPal implements PaymentMethod {
    @Override public String charge(long cents) { return "paypal " + cents; }
}

PaymentMethod p = new PayPal();     // declared type: PaymentMethod; actual type: PayPal
p.charge(500);                      // runs PayPal.charge -> "paypal 500"
```

- Rules the compiler enforces
  - Same name and parameter types (the signature)
  - Return type same or a subtype (covariant return)
  - Visibility same or wider (`protected` to `public` OK, not the reverse)
  - No new or broader **checked** exceptions
  - `@Override` makes the compiler confirm you really override (catches typos like `chrage`)
- What is **not** overriding
  - `static` methods: a subclass static method with the same signature *hides* the parent's; which runs depends on the declared type
  - `private` methods: invisible to subclasses, so a same-named method is a new method
  - Fields: never polymorphic; `p.field` uses the declared type
- What the compiler cannot check: that the override keeps the parent's *promise* (that is LSP, [solid.md](solid.md#5-liskov-substitution-principle-lsp))

---

## 5. Overloading vs Overriding ★★★

| | Overloading | Overriding |
|---|---|---|
| What | Same name, different parameters, same class (or inherited) | Same signature in a subclass |
| Chosen by | Compiler, from **declared** argument types | JVM at runtime, from the **actual** object |
| Also called | Compile-time (static) polymorphism | Runtime (dynamic) polymorphism |
| Example | `print(int)`, `print(String)` | `Card.charge` vs `PayPal.charge` |

```java
void greet(Object o) { System.out.println("object"); }
void greet(String s) { System.out.println("string"); }
Object x = "hi";
greet(x);   // prints "object": overload chosen from the declared type Object
```

---

## 6. Polymorphism And Dynamic Dispatch ★★★

- **In plain words:** the caller writes `p.charge()` once; at runtime each object answers with its own version.
- How it works inside the JVM
  1. The compiler checks that `PaymentMethod` has `charge(long)` and emits an `invokeinterface` (or `invokevirtual` for classes) instruction
  2. Each loaded class has a method table listing which code implements each method (a vtable for classes, an itable lookup for interfaces)
  3. At runtime the JVM looks at the object's actual class and jumps to that class's `charge`
  4. The JIT compiler often removes the lookup: if a call site only ever sees `Card`, it inlines `Card.charge` directly (and re-optimizes if `PayPal` shows up)
- Why it matters: the caller depends only on the interface, so `ApplePay` can be added without touching the caller. This is what makes OCP possible
- Catch: you trade a visible `switch` for an invisible jump; reading the code, you must find all implementations to know what runs

---

## 7. The Expression Problem ★★

- **In plain words:** code is a grid of *types* (Card, PayPal) by *operations* (charge, refund). Object-oriented code makes adding a row cheap and adding a column expensive; `switch`-based code is the opposite.

| | `charge` | `refund` (new operation) |
|---|---|---|
| `Card` | `Card.charge` | must edit `Card` |
| `PayPal` | `PayPal.charge` | must edit `PayPal` |
| `ApplePay` (new type) | one new class, no edits elsewhere | must edit `ApplePay` |

- **New type is cheap with polymorphism**
  - Write `class ApplePay implements PaymentMethod`, implement the existing methods
  - Nothing else changes: callers, the processor and the other classes are untouched
- **New operation is expensive with polymorphism**
  - Add `refund()` to `PaymentMethod`
  - Now `Card`, `PayPal` and `ApplePay` all fail to compile until each implements `refund()`
  - So "add, don't edit" (OCP) fails here: you edit every class anyway. That's what "adding `refund()` to every payment edits every class anyway" means
- **The switch style is the mirror image**
```java
sealed interface Payment permits Card, PayPal {}
record Card(long cents) implements Payment {}
record PayPal(long cents) implements Payment {}

static String refund(Payment p) {           // new operation = one new function, no class edits
    return switch (p) {                     // Java 21 pattern switch; compiler checks every case is covered
        case Card c   -> "refund card " + c.cents();
        case PayPal pp -> "refund paypal " + pp.cents();
    };
}
```
  - New operation: write one new function with a `switch`; no class changes
  - New type: add a record, and the compiler flags every `switch` that now misses a case
- How to choose
  - Types keep growing, operations stable (payment methods, file parsers, plugins) → interface + polymorphism
  - Types fixed, operations keep growing (AST nodes, a fixed set of order states) → sealed types + exhaustive `switch`
  - Need both: Visitor pattern, at the cost of more ceremony
- 🗣 "Polymorphism makes adding a type cheap and adding an operation expensive; a sealed type with an exhaustive switch flips that. I pick by which one will keep growing."

---

## 8. Composition Over Inheritance ★★

- **In plain words:** build behavior by holding other objects ("has-a") instead of extending a parent ("is-a").

| | Inheritance | Composition |
|---|---|---|
| Relationship | is-a | has-a |
| Coupling | Subclass sees and depends on parent internals | Only the other object's public interface |
| Change at runtime | No | Yes (swap the field) |
| Combine behaviors | Class explosion (`LoggingRetryingEmailNotifier`) | Wrap: `new Logging(new Retrying(email))` |
| Use when | A true is-a that keeps every parent promise | Reusing behavior, combining features |

- Fragile base class: a harmless-looking change in the parent (say, `addAll` now calls `add`) silently breaks subclasses that override `add`
- Default: composition; inherit only for a real is-a that passes LSP

---

## 9. Modern Java: Records, Sealed Types, Pattern Matching ★★

| Feature | Version | What it gives |
|---|---|---|
| `record` | 16 | Immutable data class with constructor, accessors, `equals`, `hashCode`, `toString` generated |
| `sealed` / `permits` | 17 | A closed list of allowed subtypes; enables exhaustive checks |
| `instanceof` pattern | 16 | `if (p instanceof Card c)` binds `c` without a cast |
| Pattern `switch` over types | 21 | `switch (p) { case Card c -> ... }` with exhaustiveness checking |
| Record patterns | 21 | Destructure: `case Card(long cents) -> ...` |

- These make the "closed set + switch" side of the expression problem safe in Java

---

## 10. equals And hashCode ★★

- **In plain words:** if two objects are "equal", they must produce the same hash, or hash maps lose them.
- Contract: `a.equals(b)` ⇒ `a.hashCode() == b.hashCode()`; the reverse is not required
- Override both or neither; records do it for you
- Catch: mutable fields in `hashCode` + the object stored in a `HashSet` = changing the field makes the entry unfindable

---

## 11. Interview Questions

**Q1. Overloading vs overriding?**
- L4: overloading = same name, different parameters, picked at compile time; overriding = same signature in a subclass, picked at runtime
- L5 extra: overload resolution uses declared types (the `greet(Object)` trap); static methods hide rather than override; JIT inlines monomorphic call sites, so polymorphism is usually free

**Q2. Abstract class or interface?**
- L4: interface for a capability many classes share; abstract class to share code and state in one family
- L5 extra: since Java 8, default methods blur the line, but interfaces still can't hold state; prefer interfaces for public types and keep abstract classes internal

**Q3. Why composition over inheritance?**
- L4: looser coupling, runtime swapping, avoids class explosion
- L5 extra: fragile base class problem; inheritance is fine for a true is-a that keeps every parent promise (LSP)

**Q4. What is the expression problem?**
- L4: polymorphism makes new types cheap and new operations expensive; switch statements are the reverse
- L5 extra: Java 21 sealed types + pattern switch make the switch side compiler-checked; Visitor handles both at a ceremony cost; choose by which axis grows

---

## References

- [The Java Tutorials — Interfaces and Inheritance](https://docs.oracle.com/javase/tutorial/java/IandI/index.html)
- [Java Language Specification SE 21, §8.4.8 Inheritance, Overriding, and Hiding](https://docs.oracle.com/javase/specs/jls/se21/html/jls-8.html#jls-8.4.8)
- [JEP 441 — Pattern Matching for switch (Java 21)](https://openjdk.org/jeps/441)
- [Philip Wadler — The Expression Problem (1998)](https://homepages.inf.ed.ac.uk/wadler/papers/expression/expression.txt)
