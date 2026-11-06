# Design patterns — classic catalog with Java and Python

## Index

- [0. How to read this guide](#reading)
- [1. Creational patterns](#creational)
  - [1.1 Abstract Factory](#abstract-factory)
  - [1.2 Builder](#builder)
  - [1.3 Factory Method](#factory-method)
  - [1.4 Prototype](#prototype)
  - [1.5 Singleton](#singleton)
- [2. Structural patterns](#structural)
  - [2.1 Adapter](#adapter)
  - [2.2 Bridge](#bridge)
  - [2.3 Composite](#composite)
  - [2.4 Decorator](#decorator)
  - [2.5 Facade](#facade)
  - [2.6 Flyweight](#flyweight)
  - [2.7 Proxy](#proxy)
- [3. Behavioral patterns](#behavioral)
  - [3.1 Chain of Responsibility](#chain-of-responsibility)
  - [3.2 Command](#command)
  - [3.3 Interpreter](#interpreter)
  - [3.4 Iterator](#iterator)
  - [3.5 Mediator](#mediator)
  - [3.6 Memento](#memento)
  - [3.7 Observer](#observer)
  - [3.8 State](#state)
  - [3.9 Strategy](#strategy)
  - [3.10 Template Method](#template-method)
  - [3.11 Visitor](#visitor)
- [4. Choosing between similar patterns](#comparison)
- [5. Production composition: transactions, ACID, and idempotency](#production)
- [6. Failure review](#failures)
- [7. Interview questions and further thinking](#interview)
- [8. References](#references)

<a id="reading"></a>
## 0. How to read this guide

- **Scope**
  - All 23 Gang of Four (GoF) object-oriented patterns.
  - Group order: creational, structural, behavioral.
  - Pattern order within each group follows the classic catalog.
  - This is a complete GoF catalog, not a claim to enumerate every architectural or distributed-systems pattern.
  - The catalog and category names come from the [original book's publisher](https://www.informit.com/store/design-patterns-elements-of-reusable-object-oriented-9780321770462).
  - The explanations and teaching examples below are original adaptations.
- **What a pattern buys**
  - A specific change becomes local to one component.
  - The price is another abstraction, object, or coordination boundary.
  - Start with a direct function when there is no independent variation to isolate.
- **Code conventions**
  - Java 17, with no preview features.
  - Python 3.11 or newer.
  - Each pattern has exactly two self-contained blocks: Java first, then Python.
  - Each block includes a classic example plus a meaningful variation or boundary check.
  - Save a Java block as `Main.java`; compile with `javac --release 17 Main.java`; run with `java -ea Main`.
  - Run each Python block separately with assertions enabled.
  - Standard collections, functions, and streams keep the pattern visible without requiring a framework.
  - In-memory examples illustrate object behavior, not persistence or distributed coordination.
  - Section 5 adds a Java/Python pair using a real SQL transaction.
- **Validation performed on 2026-10-08**
  - All 24 Java blocks compiled with JDK 25 using `--release 17` and ran with assertions enabled.
  - All 24 Python blocks ran under Python 3.11.
  - The JDBC transaction example ran against locally installed H2 2.2.224.
  - Additional concurrent-request checks used eight callers with the same request ID.
    - H2 callers retried losing attempts in fresh transactions.
    - SQLite callers used separate connections to one file-backed database.
    - Both checks observed one committed transfer and one outbox row.
  - SQLite replay was also checked after closing and reopening the database.
  - These checks do not simulate process crashes, power loss, or broker delivery.
- **Read each pattern in this order**
  - Problem and everyday analogy.
  - Participants and call flow.
  - Pros, cons, variations, and failure boundaries.
  - Code in both languages.
- **Three words to keep distinct**
  - *Thread safety*: concurrent access preserves an in-process invariant.
  - *Transaction atomicity*: database changes commit together or are rolled back together.
  - *Idempotency*: repeating the same logical request does not repeat its business effect within a defined scope and retention window.

| Type | Question it answers | Typical change being isolated |
| --- | --- | --- |
| Creational | Who creates which objects? | Product family, construction steps, copying, lifecycle |
| Structural | How do objects fit together? | Interfaces, wrappers, trees, shared representation |
| Behavioral | Who decides or performs the next action? | Algorithms, commands, transitions, notifications |

<a id="creational"></a>
## 1. Creational patterns

<a id="abstract-factory"></a>
### 1.1 Abstract Factory

#### Concept and analogy

- **Problem**
  - A screen constructs buttons and checkboxes directly.
  - Switching from one platform to another requires coordinated edits across the screen.
  - Independent choices can accidentally mix incompatible widget families.
- **Pattern**
  - Inject one factory that creates every product belonging to a compatible family.
- **Analogy**
  - Order a matching furniture collection from one showroom.
  - The showroom supplies both chairs and tables in the selected style.
- **Common uses**
  - UI themes.
  - Cloud-provider client families.
  - Database-dialect components that must agree about SQL and type mappings.

#### Mechanism and adaptation

- The client depends on product interfaces.
- A concrete factory owns the family choice.
- Each factory method creates one product type.
- Select the factory at application startup or at a tenant-specific boundary.
- A factory alone does not prevent mixing products created elsewhere.
  - Keep creation behind the same composition boundary when compatibility matters.

→ Select a light or dark factory.  
→ Ask it for a button and a checkbox.  
→ Render both through their product interfaces.

#### Tradeoffs and production boundaries

- **Pros**
  - Add a family without changing the screen.
  - Replace the entire family with test doubles.
- **Cons**
  - Adding a new product type requires changing every factory.
  - A large factory can become a service locator with unclear dependencies.
- **Variation shown**
  - Two complete theme families share one client.
- **Production adaptation**
  - A database factory may supply a connection source and SQL dialect.
  - It must not return one globally shared mutable connection.
  - The transaction still belongs to a request or unit of work.
- **Choose instead**
  - [Factory Method](#factory-method) when a subclass only needs to replace one product in a workflow.

```java
public class Main {
    interface Button { String draw(); }
    interface Checkbox { String draw(); }
    interface UiFactory {
        Button button();
        Checkbox checkbox();
    }
    static class Light implements UiFactory {
        public Button button() { return () -> "light button"; }
        public Checkbox checkbox() { return () -> "light checkbox"; }
    }
    static class Dark implements UiFactory {
        public Button button() { return () -> "dark button"; }
        public Checkbox checkbox() { return () -> "dark checkbox"; }
    }
    static String screen(UiFactory factory) {
        return factory.button().draw() + " + " + factory.checkbox().draw();
    }
    public static void main(String[] args) {
        assert screen(new Light()).equals("light button + light checkbox");
        assert screen(new Dark()).equals("dark button + dark checkbox");
    }
}
```

```python
from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class Widget:
    theme: str
    kind: str

    def draw(self) -> str:
        return f"{self.theme} {self.kind}"

class UiFactory(Protocol):
    def button(self) -> Widget: ...
    def checkbox(self) -> Widget: ...

@dataclass(frozen=True)
class ThemeFactory:
    theme: str  # Data-driven family variation instead of one class per theme.

    def button(self) -> Widget:
        return Widget(self.theme, "button")

    def checkbox(self) -> Widget:
        return Widget(self.theme, "checkbox")

def screen(factory: UiFactory) -> str:
    return factory.button().draw() + " + " + factory.checkbox().draw()

assert screen(ThemeFactory("light")) == "light button + light checkbox"
assert screen(ThemeFactory("dark")) == "dark button + dark checkbox"
```

<a id="builder"></a>
### 1.2 Builder

#### Concept and analogy

- **Problem**
  - A constructor has many optional arguments and invalid combinations.
  - Callers cannot easily distinguish a complete object from a half-configured one.
- **Pattern**
  - Accumulate construction choices in a builder.
  - Publish the product only after validation.
- **Analogy**
  - A meal order form collects the main dish and extras before the kitchen accepts it.
- **Common uses**
  - HTTP requests.
  - Immutable configuration.
  - SQL query objects with separately bound values.

#### Mechanism and adaptation

- The builder owns mutable assembly state.
- The product owns a validated snapshot.
- An optional director stores a reusable construction recipe.
- The classic GoF variation lets the same construction steps produce different representations.
  - The fluent builder below is the common API-oriented adaptation.
  - A director is useful only when multiple callers reuse a recipe.

→ Choose required main dish.  
→ Add optional extras or apply a preset recipe.  
→ Validate and copy the extras into an immutable product.

#### Tradeoffs and production boundaries

- **Pros**
  - Named steps improve readability.
  - Validation is centralized at publication.
- **Cons**
  - More code than a short constructor.
  - A mutable builder should not be shared between concurrent requests.
- **Variation shown**
  - A reusable lunch recipe.
  - A defensive copy prevents later builder changes from mutating earlier meals.
- **Production adaptation**
  - Validate a timeout budget across retries and per-attempt deadlines.
  - Prefer parameters over concatenating user input into a SQL string.
- **Choose instead**
  - A constructor or Python keyword arguments when the object has few independent fields.

```java
import java.util.*;

public class Main {
    record Meal(String main, List<String> extras) {
        Meal {
            if (main == null || main.isBlank()) throw new IllegalArgumentException();
            extras = List.copyOf(extras);
        }
    }
    static class Builder {
        private final String main;
        private final List<String> extras = new ArrayList<>();
        Builder(String main) { this.main = main; }
        Builder add(String item) { extras.add(item); return this; }
        Meal build() { return new Meal(main, extras); }
    }
    static Meal lunch() { // Director recipe.
        return new Builder("rice").add("beans").add("tea").build();
    }
    public static void main(String[] args) {
        Builder builder = new Builder("rice").add("beans");
        Meal first = builder.build();
        Meal second = builder.add("tea").build();
        assert first.extras().size() == 1;
        assert second.equals(lunch());
    }
}
```

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Meal:
    main: str
    extras: tuple[str, ...]

    def __post_init__(self):
        if not self.main.strip():
            raise ValueError("main dish required")

class Builder:
    def __init__(self, main: str):
        self.main = main
        self.extras: list[str] = []

    def add(self, item: str):
        self.extras.append(item)
        return self

    def build(self) -> Meal:
        return Meal(self.main, tuple(self.extras))

def lunch() -> Meal:
    return Builder("rice").add("beans").add("tea").build()

builder = Builder("rice").add("beans")
first = builder.build()
second = builder.add("tea").build()
assert first.extras == ("beans",)
assert second == lunch()
```

<a id="factory-method"></a>
### 1.3 Factory Method

#### Concept and analogy

- **Problem**
  - A reusable delivery workflow hardcodes which transport it constructs.
  - Adding a shipping mode means editing the workflow itself.
- **Pattern**
  - The base workflow calls an overridable creation method.
  - A subclass supplies the concrete product.
- **Analogy**
  - A logistics branch follows the same dispatch procedure but chooses its own vehicle.
- **Common uses**
  - Framework extension points.
  - Document creation in editor subclasses.
  - Transport-specific job runners.

#### Mechanism and adaptation

- Creator: the reusable logistics workflow.
- Factory method: `createTransport` or `create_transport`.
- Product: an object supporting delivery.
- A static method containing a `switch` is a simple factory, not this subclass-based mechanism.

→ Call the shared delivery workflow.  
→ Let the subclass create the transport.  
→ Invoke delivery through the product interface.

#### Tradeoffs and production boundaries

- **Pros**
  - The workflow remains stable while products change.
- **Cons**
  - One subclass per creation policy can become excessive.
- **Variation shown**
  - Road and sea delivery reuse the same workflow.
- **Production adaptation**
  - State whether creation returns a new owned resource or borrows a pooled one.
  - Release borrowed connections after use to prevent pool exhaustion.
- **Choose instead**
  - Inject a supplier when runtime composition is simpler than subclassing.

```java
public class Main {
    interface Transport { String deliver(String cargo); }
    static abstract class Logistics {
        abstract Transport createTransport();
        final String ship(String cargo) {
            if (cargo.isBlank()) throw new IllegalArgumentException("empty cargo");
            return createTransport().deliver(cargo);
        }
    }
    static class Road extends Logistics {
        Transport createTransport() { return cargo -> "truck:" + cargo; }
    }
    static class Sea extends Logistics {
        Transport createTransport() { return cargo -> "ship:" + cargo; }
    }
    public static void main(String[] args) {
        assert new Road().ship("books").equals("truck:books");
        assert new Sea().ship("books").equals("ship:books");
    }
}
```

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class Transport:
    mode: str

    def deliver(self, cargo: str) -> str:
        return f"{self.mode}:{cargo}"

class Logistics(ABC):
    @abstractmethod
    def create_transport(self) -> Transport: ...

    def ship(self, cargo: str) -> str:
        if not cargo.strip():
            raise ValueError("empty cargo")
        return self.create_transport().deliver(cargo)

class Road(Logistics):
    def create_transport(self) -> Transport:
        return Transport("truck")

class Sea(Logistics):
    def create_transport(self) -> Transport:
        return Transport("ship")

assert Road().ship("books") == "truck:books"
assert Sea().ship("books") == "ship:books"
```

<a id="prototype"></a>
### 1.4 Prototype

#### Concept and analogy

- **Problem**
  - Reconstructing a configured object requires knowing its concrete class and internal setup.
- **Pattern**
  - Create an object by copying a configured exemplar.
- **Analogy**
  - Duplicate a slide template, then edit the copy.
- **Common uses**
  - Drawing editors.
  - Configuration templates.
  - Test fixtures with expensive setup data.

#### Mechanism and adaptation

- The prototype defines copying semantics.
- A registry can hold named templates.
- Copy mutable owned state.
- Share immutable values deliberately.
- Identity and ownership are part of the contract, not incidental implementation details.

→ Obtain a configured shape.  
→ Copy its owned style data.  
→ Modify the copy without changing the template.

#### Tradeoffs and production boundaries

- **Pros**
  - Reuse an existing configuration without rebuilding it field by field at every call site.
- **Cons**
  - Deep copying graphs can be expensive.
  - Cycles and shared references require a defined policy.
- **Variation shown**
  - A clone owns its mutable style map.
  - A second clone demonstrates that later changes remain isolated.
- **Production adaptation**
  - Give a copied business entity a new identity when it represents a new entity.
  - Never duplicate a live connection, mutex, or open file by copying its fields.
- **Choose instead**
  - [Builder](#builder) when validation and explicit construction steps matter more than copying.

```java
import java.util.*;

public class Main {
    static class Shape {
        final String kind;
        final Map<String, String> style;
        Shape(String kind, Map<String, String> style) {
            this.kind = kind;
            this.style = new HashMap<>(style);
        }
        Shape copy() { return new Shape(kind, style); }
    }
    public static void main(String[] args) {
        Shape template = new Shape("circle", Map.of("color", "red"));
        Shape blue = template.copy();
        blue.style.put("color", "blue");
        Shape green = blue.copy();
        green.style.put("color", "green");
        assert template.style.get("color").equals("red");
        assert blue.style.get("color").equals("blue");
    }
}
```

```python
from dataclasses import dataclass, field
from copy import deepcopy

@dataclass
class Shape:
    kind: str
    style: dict[str, str] = field(default_factory=dict)

    def clone(self):
        return deepcopy(self)  # All fields here are ordinary owned data.

template = Shape("circle", {"color": "red"})
blue = template.clone()
blue.style["color"] = "blue"
green = blue.clone()
green.style["color"] = "green"
assert template.style["color"] == "red"
assert blue.style["color"] == "blue"
```

<a id="singleton"></a>
### 1.5 Singleton

#### Concept and analogy

- **Problem**
  - An application needs one shared configuration view or registry within a defined runtime scope.
- **Pattern**
  - Control creation and expose one shared instance.
- **Analogy**
  - One notice board serves an office.
  - Another office can still have its own notice board.
- **Common uses**
  - Immutable configuration.
  - Process-wide registries.
  - A dependency-injection container's application-scoped services.

#### Mechanism and adaptation

- Java's holder idiom defers initialization until first access.
  - Class initialization safely publishes the instance.
  - The instance is scoped to the defining class loader, not every JVM in a deployment.
- A Python module can construct one shared instance during import.
  - This is a conventional shared-instance adaptation, not a prohibition on constructing the class.
  - Separate interpreter or module identities can still produce separate instances.
- Neither mechanism elects one leader across processes or hosts.

→ Obtain the shared configuration reference.  
→ Pass that reference into a consumer.  
→ Inject a separate configuration for a test variation.

#### Tradeoffs and production boundaries

- **Pros**
  - A stable owner controls process-scoped lifecycle.
- **Cons**
  - Global access hides dependencies.
  - Mutable singleton state couples tests and concurrent requests.
- **Variation shown**
  - Lazy controlled creation in Java.
  - Module-scoped immutable configuration in Python.
  - Explicit injection keeps consumers testable.
- **Production adaptation**
  - A connection pool may be application-scoped.
  - An individual transaction connection should not be shared as a singleton.
  - A singleton is not a distributed lock.
- **Choose instead**
  - Dependency injection when lifecycle and test substitution are the real requirements.

```java
public class Main {
    record Config(int timeoutMs) {
        Config { if (timeoutMs <= 0) throw new IllegalArgumentException(); }
    }
    static final class Settings {
        private Settings() {}
        private static class Holder {
            static final Settings INSTANCE = new Settings();
        }
        static Settings instance() { return Holder.INSTANCE; }
        final Config config = new Config(1000);
    }
    static int timeout(Config config) { return config.timeoutMs(); }
    public static void main(String[] args) {
        assert Settings.instance() == Settings.instance();
        assert timeout(Settings.instance().config) == 1000;
        assert timeout(new Config(5)) == 5; // No global mutation for tests.
    }
}
```

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    timeout_ms: int

    def __post_init__(self):
        if self.timeout_ms <= 0:
            raise ValueError("positive timeout required")

# In a real application, put this in an imported settings module.
SETTINGS = Config(timeout_ms=1000)

def settings() -> Config:
    return SETTINGS

def timeout(config: Config) -> int:
    return config.timeout_ms

assert settings() is settings()
assert timeout(settings()) == 1000
assert timeout(Config(5)) == 5
```

<a id="structural"></a>
## 2. Structural patterns

<a id="adapter"></a>
### 2.1 Adapter

#### Concept and analogy

- **Problem**
  - A useful existing component exposes the wrong interface or units.
- **Pattern**
  - Wrap that component and translate the client's contract into the existing contract.
- **Analogy**
  - A travel adapter makes one plug fit another socket.
  - It does not automatically convert voltage.
- **Common uses**
  - Legacy APIs.
  - Database drivers.
  - Provider SDKs behind an application-owned interface.

#### Mechanism and adaptation

- Target: the interface expected by the caller.
- Adaptee: the incompatible existing implementation.
- Adapter: argument conversion plus result/error translation.
- The classic example adapts a round peg to a square hole using the peg's bounding width.

→ Caller asks whether a peg fits.  
→ Adapter converts radius to required square-hole width.  
→ Client evaluates the converted contract.

#### Tradeoffs and production boundaries

- **Pros**
  - Existing code can be reused without changing callers.
- **Cons**
  - Superficially matching signatures can hide incompatible semantics.
- **Variation shown**
  - A native square peg and an adapted round peg use the same client.
  - Boundary checks show that conversion changes fit behavior.
- **Production adaptation**
  - Translate cents versus dollars explicitly.
  - Preserve retryable versus terminal provider errors.
  - An adapter cannot invent atomicity missing from the provider.
- **Choose instead**
  - [Bridge](#bridge) when both interfaces are under your control and designed to vary independently.

```java
public class Main {
    interface Peg { double width(); }
    record SquarePeg(double width) implements Peg {}
    record RoundPeg(double radius) {}
    record RoundAdapter(RoundPeg peg) implements Peg {
        public double width() { return 2 * peg.radius(); }
    }
    record SquareHole(double width) {
        boolean fits(Peg peg) { return peg.width() <= width; }
    }
    public static void main(String[] args) {
        SquareHole hole = new SquareHole(10);
        assert hole.fits(new SquarePeg(9));
        assert hole.fits(new RoundAdapter(new RoundPeg(5)));
        assert !hole.fits(new RoundAdapter(new RoundPeg(6)));
    }
}
```

```python
from dataclasses import dataclass
from typing import Protocol

class Peg(Protocol):
    def width(self) -> float: ...

@dataclass
class SquarePeg:
    side: float

    def width(self) -> float:
        return self.side

@dataclass
class RoundPeg:
    radius: float

@dataclass
class RoundAdapter:
    peg: RoundPeg

    def width(self) -> float:
        return 2 * self.peg.radius

def fits(hole_width: float, peg: Peg) -> bool:
    return peg.width() <= hole_width

assert fits(10, SquarePeg(9))
assert fits(10, RoundAdapter(RoundPeg(5)))
assert not fits(10, RoundAdapter(RoundPeg(6)))
```

<a id="bridge"></a>
### 2.2 Bridge

#### Concept and analogy

- **Problem**
  - Two independent dimensions produce a growing cross-product of subclasses.
  - A shape hierarchy becomes `RasterCircle`, `VectorCircle`, `RasterSquare`, and so on.
- **Pattern**
  - Give the abstraction a reference to a separate implementation interface.
- **Analogy**
  - A remote-control model and a television brand evolve independently through a common control interface.
- **Common uses**
  - Shapes and renderers.
  - Notification types and delivery channels.
  - Business reports and output backends.

#### Mechanism and adaptation

- Abstraction: shape with geometry.
- Implementor: renderer with drawing primitives.
- Two hierarchies communicate through composition.
- Choose the renderer when composing the object graph.

→ Create a circle or square.  
→ Attach a raster or vector renderer.  
→ Delegate rendering while retaining shape-specific behavior.

#### Tradeoffs and production boundaries

- **Pros**
  - Add a shape or renderer without creating every possible combination class.
- **Cons**
  - The renderer interface must express the capabilities both sides need.
  - Backend differences can leak through an overly optimistic common interface.
- **Variation shown**
  - Two shapes combined with two rendering styles.
- **Production adaptation**
  - Define supported capabilities rather than silently dropping unsupported operations.
  - A storage bridge must expose transaction limits if backends differ.
- **Choose instead**
  - [Strategy](#strategy) when the variable part is one algorithm rather than a second structural dimension.

```java
public class Main {
    interface Renderer { String draw(String shape, int size); }
    static class Raster implements Renderer {
        public String draw(String shape, int size) { return "pixels:" + shape + size; }
    }
    static class Vector implements Renderer {
        public String draw(String shape, int size) { return "paths:" + shape + size; }
    }
    static abstract class Shape {
        final Renderer renderer;
        Shape(Renderer renderer) { this.renderer = renderer; }
        abstract String draw();
    }
    static class Circle extends Shape {
        Circle(Renderer r) { super(r); }
        String draw() { return renderer.draw("circle", 5); }
    }
    static class Square extends Shape {
        Square(Renderer r) { super(r); }
        String draw() { return renderer.draw("square", 8); }
    }
    public static void main(String[] args) {
        assert new Circle(new Raster()).draw().equals("pixels:circle5");
        assert new Circle(new Vector()).draw().equals("paths:circle5");
        assert new Square(new Vector()).draw().equals("paths:square8");
    }
}
```

```python
from dataclasses import dataclass
from typing import Protocol

class Renderer(Protocol):
    def draw(self, shape: str, size: int) -> str: ...

class Raster:
    def draw(self, shape: str, size: int) -> str:
        return f"pixels:{shape}{size}"

class Vector:
    def draw(self, shape: str, size: int) -> str:
        return f"paths:{shape}{size}"

@dataclass
class Shape:
    renderer: Renderer

class Circle(Shape):
    def draw(self) -> str:
        return self.renderer.draw("circle", 5)

class Square(Shape):
    def draw(self) -> str:
        return self.renderer.draw("square", 8)

assert Circle(Raster()).draw() == "pixels:circle5"
assert Circle(Vector()).draw() == "paths:circle5"
assert Square(Vector()).draw() == "paths:square8"
```

<a id="composite"></a>
### 2.3 Composite

#### Concept and analogy

- **Problem**
  - Clients repeatedly branch between an individual object and a collection of objects.
- **Pattern**
  - Give leaves and containers the same operation interface.
  - Containers implement the operation recursively over children.
- **Analogy**
  - Ask for the weight of a parcel whether it contains one item or several nested boxes.
- **Common uses**
  - Filesystem trees.
  - UI component trees.
  - Organization charts.

#### Mechanism and adaptation

- Component: operation shared by leaf and container.
- Leaf: owns a direct value.
- Composite: owns child components and aggregates their results.
- The example uses immutable children and defines a tree before traversal.

→ Ask a directory for its size.  
→ Ask each child for its size through the same interface.  
→ Sum the results regardless of nesting depth.

#### Tradeoffs and production boundaries

- **Pros**
  - Clients operate uniformly over a whole subtree.
- **Cons**
  - An operation meaningful for a leaf may not make sense for a container.
  - Deep recursion can overflow the call stack.
- **Variation shown**
  - Nested and empty directories.
  - Defensive child snapshots prevent mutation during traversal.
- **Production adaptation**
  - Reject cycles when adding nodes to a mutable tree.
  - Decide whether a shared child is counted once per reference or once per identity.
  - Use an explicit stack for untrusted depth.
  - Recursive writes are not atomic unless enclosed in a suitable transaction.
- **Choose instead**
  - [Visitor](#visitor) when many new operations must traverse a stable element hierarchy.

```java
import java.util.*;

public class Main {
    interface Node { long size(); }
    record File(long size) implements Node {}
    record Directory(List<Node> children) implements Node {
        Directory { children = List.copyOf(children); }
        public long size() { return children.stream().mapToLong(Node::size).sum(); }
    }
    public static void main(String[] args) {
        Node tree = new Directory(List.of(
            new File(10), new Directory(List.of(new File(20), new File(30)))));
        assert tree.size() == 60;
        assert new Directory(List.of()).size() == 0;
    }
}
```

```python
from dataclasses import dataclass
from typing import Protocol

class Node(Protocol):
    def size(self) -> int: ...

@dataclass(frozen=True)
class File:
    bytes_: int

    def size(self) -> int:
        return self.bytes_

@dataclass(frozen=True)
class Directory:
    children: tuple[Node, ...]

    def size(self) -> int:
        return sum(child.size() for child in self.children)

tree = Directory((File(10), Directory((File(20), File(30)))))
assert tree.size() == 60
assert Directory(()).size() == 0
```

<a id="decorator"></a>
### 2.4 Decorator

#### Concept and analogy

- **Problem**
  - Optional behaviors create a subclass for every combination.
- **Pattern**
  - Wrap an object with another object implementing the same interface.
  - Add behavior before or after delegation.
- **Analogy**
  - Add milk and syrup to a base coffee in different combinations.
- **Common uses**
  - Buffered I/O.
  - Compression streams.
  - Metrics and tracing wrappers.

#### Mechanism and adaptation

- Component: the base operation.
- Decorator: same operation plus a reference to the wrapped component.
- Nesting determines execution order.
- Python decorator syntax can implement function wrapping, but the GoF pattern is about composition and a compatible contract.

→ Start with a coffee.  
→ Wrap it in milk and syrup add-ons.  
→ Add an outer discount and compare the alternative ordering.

#### Tradeoffs and production boundaries

- **Pros**
  - Compose features without a subclass cross-product.
- **Cons**
  - Deep wrapper stacks make call order harder to inspect.
  - The same interface can hide very different costs.
- **Variation shown**
  - A price discount makes wrapper order observably significant.
  - Money is represented as integer cents.
- **Production adaptation**
  - Decide whether metrics count requests or retry attempts by placing the wrapper deliberately.
  - Authentication should run before reading a protected cache result.
  - Retry only operations whose effects are safe to repeat.
- **Choose instead**
  - [Proxy](#proxy) when the main intent is controlling access to a subject.

```java
public class Main {
    interface Drink { int cents(); }
    record Coffee() implements Drink { public int cents() { return 200; } }
    record AddOn(Drink inner, int extra) implements Drink {
        public int cents() { return inner.cents() + extra; }
    }
    record TenPercentOff(Drink inner) implements Drink {
        public int cents() { return inner.cents() * 90 / 100; }
    }
    public static void main(String[] args) {
        Drink flavored = new AddOn(new AddOn(new Coffee(), 50), 30);
        assert flavored.cents() == 280;
        assert new TenPercentOff(new AddOn(new Coffee(), 50)).cents() == 225;
        assert new AddOn(new TenPercentOff(new Coffee()), 50).cents() == 230;
    }
}
```

```python
from dataclasses import dataclass
from typing import Protocol

class Drink(Protocol):
    def cents(self) -> int: ...

class Coffee:
    def cents(self) -> int:
        return 200

@dataclass
class AddOn:
    inner: Drink
    extra: int

    def cents(self) -> int:
        return self.inner.cents() + self.extra

@dataclass
class TenPercentOff:
    inner: Drink

    def cents(self) -> int:
        return self.inner.cents() * 90 // 100

assert AddOn(AddOn(Coffee(), 50), 30).cents() == 280
assert TenPercentOff(AddOn(Coffee(), 50)).cents() == 225
assert AddOn(TenPercentOff(Coffee()), 50).cents() == 230
```

<a id="facade"></a>
### 2.5 Facade

#### Concept and analogy

- **Problem**
  - Every caller must know the setup sequence for a complicated subsystem.
- **Pattern**
  - Expose a small use-case API that coordinates the subsystem.
- **Analogy**
  - A theater's play button starts the projector and sound system for you.
- **Common uses**
  - SDK convenience APIs.
  - Application services.
  - Checkout or document-processing entry points.

#### Mechanism and adaptation

- The facade owns orchestration order.
- Subsystems retain their individual responsibilities.
- Advanced callers may still use subsystem APIs directly if the architecture allows it.

→ Power on the projector.  
→ Start sound.  
⇒ If sound startup fails, release the projector acquired by this operation.

#### Tradeoffs and production boundaries

- **Pros**
  - Centralizes sequencing and cleanup.
  - Reduces the API surface most callers need.
- **Cons**
  - A facade can accumulate unrelated business logic.
  - A single method name can conceal multiple failure boundaries.
- **Variation shown**
  - Successful startup and failed startup with cleanup.
- **Production adaptation**
  - Local resource cleanup does not undo an external payment.
  - Compensation is a new business action that can also fail.
  - Use a database transaction only for operations participating in that transaction.
- **Choose instead**
  - [Mediator](#mediator) when peer components must coordinate ongoing interactions.

```java
public class Main {
    static class Projector {
        boolean on;
        void start() { on = true; }
        void stop() { on = false; }
    }
    static class Sound {
        final boolean broken;
        Sound(boolean broken) { this.broken = broken; }
        void start() { if (broken) throw new IllegalStateException("speaker failure"); }
    }
    record Theater(Projector projector, Sound sound) {
        void watch() {
            projector.start();
            try { sound.start(); }
            catch (RuntimeException error) { projector.stop(); throw error; }
        }
    }
    public static void main(String[] args) {
        Projector ok = new Projector();
        new Theater(ok, new Sound(false)).watch();
        assert ok.on;
        Projector failed = new Projector();
        try {
            new Theater(failed, new Sound(true)).watch();
            throw new AssertionError("failure expected");
        } catch (IllegalStateException expected) { assert !failed.on; }
    }
}
```

```python
class Projector:
    def __init__(self):
        self.on = False

    def start(self):
        self.on = True

    def stop(self):
        self.on = False

class Sound:
    def __init__(self, broken=False):
        self.broken = broken

    def start(self):
        if self.broken:
            raise RuntimeError("speaker failure")

class Theater:
    def __init__(self, projector, sound):
        self.projector, self.sound = projector, sound

    def watch(self):
        self.projector.start()
        try:
            self.sound.start()
        except Exception:
            self.projector.stop()
            raise

ok = Projector()
Theater(ok, Sound()).watch()
assert ok.on
failed = Projector()
try:
    Theater(failed, Sound(broken=True)).watch()
    raise AssertionError("failure expected")
except RuntimeError:
    assert not failed.on
```

<a id="flyweight"></a>
### 2.6 Flyweight

#### Concept and analogy

- **Problem**
  - Many objects repeat the same large immutable data.
- **Pattern**
  - Share the repeated intrinsic state.
  - Supply per-use extrinsic state separately.
- **Analogy**
  - A printer reuses one glyph design at many positions on a page.
- **Common uses**
  - Text rendering.
  - Game sprite types.
  - Interned immutable descriptors.

#### Mechanism and adaptation

- Factory: map from complete intrinsic-state key to shared value.
- Flyweight: immutable glyph shape metadata.
- Context: position supplied on each draw.
- Position must not be written into the shared glyph.

→ Look up a glyph by character and font.  
→ Create it once for that key when absent.  
→ Draw the shared glyph at independently supplied positions.

#### Tradeoffs and production boundaries

- **Pros**
  - Removes repeated intrinsic data when many uses share relatively few keys.
- **Cons**
  - Adds lookup and ownership complexity.
  - An unbounded key space creates a memory leak disguised as a cache.
- **Variation shown**
  - Same character and font reuse one instance.
  - Different fonts produce distinct flyweights.
  - Java uses atomic map population for concurrent lookup.
- **Production adaptation**
  - Bound or evict entries when keys originate from untrusted input.
  - Include every rendering-relevant dimension in the key.
  - Python's simple registry below is for single-threaded use.
- **Choose instead**
  - [Prototype](#prototype) when callers need independently mutable copies.

```java
import java.util.concurrent.*;

public class Main {
    record Key(char character, String font) {}
    record Glyph(Key key) {
        String draw(int x, int y) { return key.character() + "@" + x + "," + y; }
    }
    static class Glyphs {
        private final ConcurrentMap<Key, Glyph> cache = new ConcurrentHashMap<>();
        Glyph get(char c, String font) {
            return cache.computeIfAbsent(new Key(c, font), Glyph::new);
        }
    }
    public static void main(String[] args) {
        Glyphs glyphs = new Glyphs();
        Glyph a = glyphs.get('A', "serif");
        assert a == glyphs.get('A', "serif");
        assert a != glyphs.get('A', "sans");
        assert !a.draw(0, 0).equals(a.draw(10, 0));
    }
}
```

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Glyph:
    character: str
    font: str

    def draw(self, x: int, y: int) -> str:
        return f"{self.character}@{x},{y}"

class Glyphs:
    def __init__(self):
        self.cache: dict[tuple[str, str], Glyph] = {}

    def get(self, character: str, font: str) -> Glyph:
        key = (character, font)
        if key not in self.cache:
            self.cache[key] = Glyph(character, font)
        return self.cache[key]

glyphs = Glyphs()
a = glyphs.get("A", "serif")
assert a is glyphs.get("A", "serif")
assert a is not glyphs.get("A", "sans")
assert a.draw(0, 0) != a.draw(10, 0)
```

<a id="proxy"></a>
### 2.7 Proxy

#### Concept and analogy

- **Problem**
  - Access to an object must be delayed, checked, or redirected without changing its callers.
- **Pattern**
  - Stand in for a subject behind the same interface.
  - Control whether and when calls reach the real subject.
- **Analogy**
  - A front-desk receptionist checks authorization before connecting you to a specialist.
  - The receptionist is a proxy when representing access to that specialist.
  - Coordinating several specialists with one another is closer to a mediator.
- **Common uses**
  - Lazy image loading.
  - Remote client stubs.
  - Authorization and transaction interceptors.

#### Mechanism and adaptation

- Subject interface: display an image for a principal.
- Real subject: owns the expensive loaded image.
- Virtual proxy: constructs the subject on first access.
- Protection proxy: checks the principal on every access.

→ Check access before delegation.  
→ Load the real image on the first authorized call.  
→ Reuse the loaded subject on subsequent authorized calls.

#### Tradeoffs and production boundaries

- **Pros**
  - Centralizes access policy.
  - Avoids eager work for unused resources.
- **Cons**
  - Hidden I/O makes an apparently cheap method slow or failure-prone.
  - Lazy initialization needs synchronization if shared across threads.
- **Variation shown**
  - Protection proxy wrapped around a lazy proxy.
  - Denied access does not trigger loading.
  - Java synchronizes initialization; Python is a single-threaded illustration.
- **Production adaptation**
  - Derive identity from trusted authentication, not a caller-supplied string as in the demo.
  - Include tenant and authorization scope in cache keys.
  - With Spring's usual proxy-based AOP, self-invocation bypasses proxy advice; a transaction annotation is not sufficient when the call never crosses the proxy. [Spring proxying documentation](https://docs.spring.io/spring-framework/reference/core/aop/proxying.html)
- **Choose instead**
  - [Decorator](#decorator) when the main intent is stacking optional behavior.

```java
import java.util.function.Supplier;

public class Main {
    interface Image { String show(String user); }
    record RealImage(String file) implements Image {
        public String show(String user) { return "image:" + file; }
    }
    static class LazyImage implements Image {
        final Supplier<Image> loader;
        Image real;
        LazyImage(Supplier<Image> loader) { this.loader = loader; }
        public synchronized String show(String user) {
            if (real == null) real = loader.get();
            return real.show(user);
        }
    }
    record ProtectedImage(Image inner) implements Image {
        public String show(String user) {
            if (!user.equals("admin")) throw new SecurityException();
            return inner.show(user);
        }
    }
    public static void main(String[] args) {
        int[] loads = {0};
        Image image = new ProtectedImage(new LazyImage(() -> {
            loads[0]++;
            return new RealImage("portrait.png");
        }));
        try { image.show("guest"); throw new AssertionError(); }
        catch (SecurityException expected) { assert loads[0] == 0; }
        assert image.show("admin").equals("image:portrait.png");
        image.show("admin");
        assert loads[0] == 1;
    }
}
```

```python
class RealImage:
    def __init__(self, file: str):
        self.file = file

    def show(self, user: str) -> str:
        return f"image:{self.file}"

class LazyImage:
    def __init__(self, loader):
        self.loader, self.real = loader, None

    def show(self, user: str) -> str:
        if self.real is None:
            self.real = self.loader()
        return self.real.show(user)

class ProtectedImage:
    def __init__(self, inner):
        self.inner = inner

    def show(self, user: str) -> str:
        if user != "admin":
            raise PermissionError("denied")
        return self.inner.show(user)

loads: list[str] = []
def load():
    loads.append("loaded")
    return RealImage("portrait.png")

image = ProtectedImage(LazyImage(load))
try:
    image.show("guest")
    raise AssertionError("denial expected")
except PermissionError:
    assert not loads
assert image.show("admin") == "image:portrait.png"
image.show("admin")
assert len(loads) == 1
```

<a id="behavioral"></a>
## 3. Behavioral patterns

<a id="chain-of-responsibility"></a>
### 3.1 Chain of Responsibility

#### Concept and analogy

- **Problem**
  - A sender knows every possible receiver and embeds a growing selection tree.
- **Pattern**
  - Pass a request along handlers until one handles it or the chain ends.
- **Analogy**
  - A support ticket escalates from the help desk to an engineer to a specialist.
- **Common uses**
  - Approval chains.
  - UI event bubbling.
  - HTTP middleware as a related continue-or-stop variation.

#### Mechanism and adaptation

- Each handler owns a decision and a next-handler reference.
- The sender knows only the first handler.
- Classic variation: one eligible receiver handles the request.
- Pipeline variation: each stage transforms or validates and then continues.
  - Be explicit about which semantics you intend.

→ Ask the supervisor to approve an amount.  
→ Forward larger amounts to the director.  
⇒ Reject explicitly when no authorized handler accepts the request.

#### Tradeoffs and production boundaries

- **Pros**
  - Change routing order without changing the sender.
- **Cons**
  - Misordered handlers can silently change policy.
  - A request can reach the end unhandled.
- **Variation shown**
  - Two approval thresholds and an explicit terminal denial.
- **Production adaptation**
  - Security chains should fail closed when no rule accepts.
  - Give retries a bounded owner to prevent retry multiplication across layers.
  - Repeating the chain must not repeat already committed effects without deduplication.
- **Choose instead**
  - [Strategy](#strategy) when the caller directly chooses one algorithm.

```java
public class Main {
    record Approver(String name, int limit, Approver next) {
        String approve(int cents) {
            if (cents <= 0) throw new IllegalArgumentException();
            if (cents <= limit) return name;
            if (next != null) return next.approve(cents);
            throw new SecurityException("no authorized approver");
        }
    }
    public static void main(String[] args) {
        Approver chain = new Approver("supervisor", 100,
            new Approver("director", 1000, null));
        assert chain.approve(50).equals("supervisor");
        assert chain.approve(500).equals("director");
        try { chain.approve(1001); throw new AssertionError(); }
        catch (SecurityException expected) { /* fail closed */ }
    }
}
```

```python
from dataclasses import dataclass

@dataclass
class Approver:
    name: str
    limit: int
    next: "Approver | None" = None

    def approve(self, cents: int) -> str:
        if cents <= 0:
            raise ValueError("positive amount required")
        if cents <= self.limit:
            return self.name
        if self.next is not None:
            return self.next.approve(cents)
        raise PermissionError("no authorized approver")

chain = Approver("supervisor", 100, Approver("director", 1000))
assert chain.approve(50) == "supervisor"
assert chain.approve(500) == "director"
try:
    chain.approve(1001)
    raise AssertionError("denial expected")
except PermissionError:
    pass
```

<a id="command"></a>
### 3.2 Command

#### Concept and analogy

- **Problem**
  - A button or queue knows the details of every action it can trigger.
  - Actions cannot easily be stored, scheduled, or undone.
- **Pattern**
  - Represent a request as an object containing its receiver and arguments.
- **Analogy**
  - A restaurant order ticket records what the kitchen must do.
  - The waiter transports the ticket without cooking the meal.
- **Common uses**
  - Editor actions.
  - Job queues.
  - Application command handlers.

#### Mechanism and adaptation

- Receiver: the light that owns actual state.
- Command: a desired state change plus enough information for local undo.
- Invoker: the remote storing a history of executed commands.
- A serializable durable command should store identifiers and values, not a live receiver reference.

→ Create a new command for each user action.  
→ Execute it and record it in history.  
→ Undo in reverse order using the saved prior state.

#### Tradeoffs and production boundaries

- **Pros**
  - Separates action selection from execution.
  - Enables history and queues.
- **Cons**
  - Stateful commands can be incorrectly reused.
  - Not every external effect has a valid inverse.
- **Variation shown**
  - Turn on, turn off, then undo both actions.
  - The command captures prior state at execution time.
- **Production adaptation**
  - A command object does not make a handler idempotent.
  - Durable consumers need a scoped command ID and atomic deduplication with the effect.
  - An undo of a shipment is a compensating business workflow, not a database rollback.
- **Choose instead**
  - [Memento](#memento) when opaque state snapshots are the right undo representation.

```java
import java.util.*;

public class Main {
    static class Light { boolean on; }
    interface Command { void execute(); void undo(); }
    static class SetLight implements Command {
        final Light light;
        final boolean target;
        boolean before;
        SetLight(Light light, boolean target) { this.light = light; this.target = target; }
        public void execute() { before = light.on; light.on = target; }
        public void undo() { light.on = before; }
    }
    static class Remote {
        final Deque<Command> history = new ArrayDeque<>();
        void press(Command command) { command.execute(); history.push(command); }
        void undo() { if (!history.isEmpty()) history.pop().undo(); }
    }
    public static void main(String[] args) {
        Light light = new Light();
        Remote remote = new Remote();
        remote.press(new SetLight(light, true));
        remote.press(new SetLight(light, false));
        remote.undo();
        assert light.on;
        remote.undo();
        assert !light.on;
    }
}
```

```python
from dataclasses import dataclass

@dataclass
class Light:
    on: bool = False

class SetLight:
    def __init__(self, light: Light, target: bool):
        self.light, self.target = light, target
        self.before = None

    def execute(self):
        self.before = self.light.on
        self.light.on = self.target

    def undo(self):
        if self.before is None:
            raise RuntimeError("not executed")
        self.light.on = self.before

class Remote:
    def __init__(self):
        self.history: list[SetLight] = []

    def press(self, command: SetLight):
        command.execute()
        self.history.append(command)

    def undo(self):
        if self.history:
            self.history.pop().undo()

light, remote = Light(), Remote()
remote.press(SetLight(light, True))
remote.press(SetLight(light, False))
remote.undo()
assert light.on
remote.undo()
assert not light.on
```

<a id="interpreter"></a>
### 3.3 Interpreter

#### Concept and analogy

- **Problem**
  - A small recurring rule language is implemented as scattered string checks.
- **Pattern**
  - Represent language expressions as a tree of objects.
  - Each expression evaluates itself against a context.
- **Analogy**
  - A sentence is understood by interpreting its words and grammatical combinations.
- **Common uses**
  - Small permission expressions.
  - Search filters.
  - Educational expression evaluators.

#### Mechanism and adaptation

- Terminal: a boolean literal or variable lookup.
- Nonterminal: `And`, `Or`, or `Not` combining child expressions.
- Context: variable bindings supplied for one evaluation.
- Parsing text into an expression tree is a separate concern.
  - The example constructs the tree directly.

→ Build `employee AND (admin OR on_call)`.  
→ Resolve variables from a context.  
→ Evaluate nested operators with short-circuit behavior.

#### Tradeoffs and production boundaries

- **Pros**
  - Small rules are composable and inspectable.
- **Cons**
  - Large grammars create many node types and slow tree walks.
  - Grammar evolution needs versioning and compatibility rules.
- **Variation shown**
  - Nested expressions.
  - Missing variables evaluate to false in this deliberately defined language.
- **Production adaptation**
  - Never replace a parser with `eval` on untrusted input.
  - Limit expression depth and evaluation work.
  - A missing variable under `Not` can become true; choose strict missing-variable errors for security policies that require fail-closed semantics.
- **Choose instead**
  - A parser plus compiler or established rule engine when the language grows beyond a small grammar.

```java
import java.util.*;

public class Main {
    interface Expr { boolean eval(Map<String, Boolean> context); }
    record Var(String name) implements Expr {
        public boolean eval(Map<String, Boolean> c) { return c.getOrDefault(name, false); }
    }
    record And(Expr left, Expr right) implements Expr {
        public boolean eval(Map<String, Boolean> c) { return left.eval(c) && right.eval(c); }
    }
    record Or(Expr left, Expr right) implements Expr {
        public boolean eval(Map<String, Boolean> c) { return left.eval(c) || right.eval(c); }
    }
    record Not(Expr child) implements Expr {
        public boolean eval(Map<String, Boolean> c) { return !child.eval(c); }
    }
    public static void main(String[] args) {
        Expr rule = new And(new Var("employee"),
            new Or(new Var("admin"), new Var("on_call")));
        assert rule.eval(Map.of("employee", true, "on_call", true));
        assert !rule.eval(Map.of("admin", true));
        assert new Not(new Var("missing")).eval(Map.of());
    }
}
```

```python
from dataclasses import dataclass
from typing import Protocol

class Expr(Protocol):
    def evaluate(self, context: dict[str, bool]) -> bool: ...

@dataclass(frozen=True)
class Var:
    name: str

    def evaluate(self, context: dict[str, bool]) -> bool:
        return context.get(self.name, False)

@dataclass(frozen=True)
class And:
    left: Expr
    right: Expr

    def evaluate(self, context: dict[str, bool]) -> bool:
        return self.left.evaluate(context) and self.right.evaluate(context)

@dataclass(frozen=True)
class Or:
    left: Expr
    right: Expr

    def evaluate(self, context: dict[str, bool]) -> bool:
        return self.left.evaluate(context) or self.right.evaluate(context)

@dataclass(frozen=True)
class Not:
    child: Expr

    def evaluate(self, context: dict[str, bool]) -> bool:
        return not self.child.evaluate(context)

rule = And(Var("employee"), Or(Var("admin"), Var("on_call")))
assert rule.evaluate({"employee": True, "on_call": True})
assert not rule.evaluate({"admin": True})
assert Not(Var("missing")).evaluate({})
```

<a id="iterator"></a>
### 3.4 Iterator

#### Concept and analogy

- **Problem**
  - A caller must know a collection's representation to traverse it.
- **Pattern**
  - Move traversal position into a separate iterator with a next-element protocol.
- **Analogy**
  - Two readers use independent bookmarks in the same book.
- **Common uses**
  - Collections.
  - Lazy generators.
  - Paged database or API reads.

#### Mechanism and adaptation

- Aggregate: supplies an iterator.
- Iterator: owns traversal position, not the collection itself.
- Multiple iterators can traverse independently.
- Decide whether traversal is a snapshot, fail-fast view, or weakly consistent view.

→ Capture a playlist snapshot when iteration begins.  
→ Advance a private cursor one item at a time.  
→ Allow a second iterator to start independently.

#### Tradeoffs and production boundaries

- **Pros**
  - Hides storage details and supports incremental consumption.
- **Cons**
  - Snapshot iteration allocates memory.
  - Lazy iteration can keep resources alive longer than callers expect.
- **Variation shown**
  - Changes after iterator creation do not affect its snapshot.
  - New iterators see the updated playlist.
- **Production adaptation**
  - Close database cursors and streams on early exit.
  - Keyset pagination needs a stable ordering key.
  - Multiple page requests do not imply one consistent database snapshot.
- **Choose instead**
  - A materialized list when the result is small and repeated traversal is important.

```java
import java.util.*;

public class Main {
    static class Playlist implements Iterable<String> {
        final List<String> songs = new ArrayList<>();
        void add(String song) { songs.add(song); }
        public Iterator<String> iterator() { return List.copyOf(songs).iterator(); }
    }
    public static void main(String[] args) {
        Playlist playlist = new Playlist();
        playlist.add("A");
        playlist.add("B");
        Iterator<String> first = playlist.iterator();
        playlist.add("C");
        assert first.next().equals("A");
        assert playlist.iterator().next().equals("A");
        assert first.next().equals("B");
        assert !first.hasNext();
        List<String> latest = new ArrayList<>();
        playlist.forEach(latest::add);
        assert latest.equals(List.of("A", "B", "C"));
    }
}
```

```python
class Playlist:
    def __init__(self):
        self.songs: list[str] = []

    def add(self, song: str):
        self.songs.append(song)

    def __iter__(self):
        # Snapshot happens now, not at the first next() of a generator body.
        return iter(tuple(self.songs))

playlist = Playlist()
playlist.add("A")
playlist.add("B")
first = iter(playlist)
playlist.add("C")
assert next(first) == "A"
assert next(iter(playlist)) == "A"
assert list(first) == ["B"]
assert list(playlist) == ["A", "B", "C"]
```

<a id="mediator"></a>
### 3.5 Mediator

#### Concept and analogy

- **Problem**
  - Every component coordinates directly with many other components.
  - Changing one interaction rule requires editing several peers.
- **Pattern**
  - Move interaction policy into a coordinating object.
- **Analogy**
  - An air-traffic controller coordinates aircraft instead of asking every pilot to negotiate with every other pilot.
- **Common uses**
  - Dialog widgets.
  - Chat rooms.
  - Application workflow coordinators.

#### Mechanism and adaptation

- Colleagues send requests or events to the mediator.
- The mediator chooses which colleagues to notify.
- Colleagues do not retain direct references to all peers.
- A controller is a role in an application architecture, not automatically this pattern.
  - It acts as a mediator only when it owns coordination among colleagues.

→ A chat member sends to the room.  
→ The room selects recipients.  
→ Broadcast to other members or route a private message.

#### Tradeoffs and production boundaries

- **Pros**
  - Interaction policy has one owner.
  - Peers depend on the mediator contract rather than each other.
- **Cons**
  - The mediator can become a large central bottleneck.
- **Variation shown**
  - Broadcast and private delivery.
  - Unknown senders and private recipients are rejected explicitly.
- **Production adaptation**
  - Partition mediators by room or workflow to bound state and contention.
  - Authentication and durable delivery require separate infrastructure.
  - This example's identity strings are not credentials.
- **Choose instead**
  - [Observer](#observer) when the publisher merely announces facts without coordinating a workflow.

```java
import java.util.*;

public class Main {
    static class Room {
        final Map<String, List<String>> inboxes = new HashMap<>();
        void join(String user) {
            if (inboxes.putIfAbsent(user, new ArrayList<>()) != null)
                throw new IllegalArgumentException("duplicate member");
        }
        void send(String from, String to, String text) {
            if (!inboxes.containsKey(from)) throw new IllegalArgumentException("sender");
            if (to != null) {
                if (!inboxes.containsKey(to)) throw new IllegalArgumentException("recipient");
                inboxes.get(to).add(from + ":" + text);
            } else {
                inboxes.forEach((name, inbox) -> {
                    if (!name.equals(from)) inbox.add(from + ":" + text);
                });
            }
        }
    }
    public static void main(String[] args) {
        Room room = new Room();
        room.join("A"); room.join("B"); room.join("C");
        room.send("A", null, "hello");
        room.send("B", "A", "private");
        assert room.inboxes.get("A").equals(List.of("B:private"));
        assert room.inboxes.get("C").equals(List.of("A:hello"));
    }
}
```

```python
class Room:
    def __init__(self):
        self.inboxes: dict[str, list[str]] = {}

    def join(self, user: str):
        if user in self.inboxes:
            raise ValueError("duplicate member")
        self.inboxes[user] = []

    def send(self, sender: str, text: str, to: str | None = None):
        if sender not in self.inboxes:
            raise ValueError("sender")
        if to is not None and to not in self.inboxes:
            raise ValueError("recipient")
        recipients = [to] if to is not None else [u for u in self.inboxes if u != sender]
        for user in recipients:
            self.inboxes[user].append(f"{sender}:{text}")

room = Room()
for member in ("A", "B", "C"):
    room.join(member)
room.send("A", "hello")
room.send("B", "private", to="A")
assert room.inboxes["A"] == ["B:private"]
assert room.inboxes["C"] == ["A:hello"]
```

<a id="memento"></a>
### 3.6 Memento

#### Concept and analogy

- **Problem**
  - Undo requires prior state, but external history code should not reconstruct object internals.
- **Pattern**
  - Let the object create and restore an opaque snapshot.
  - Let a caretaker store snapshots without interpreting them.
- **Analogy**
  - A game produces save points that a player can restore without understanding its internal data structures.
- **Common uses**
  - Text editor undo.
  - Workflow checkpoints.
  - Temporary configuration changes.

#### Mechanism and adaptation

- Originator: editor owning text.
- Memento: immutable captured state plus origin ownership.
- Caretaker: stack of saved states.
- Save before an edit; restore the most recent snapshot on undo.

→ Save the editor state.  
→ Apply an edit and save another state.  
→ Restore snapshots in reverse order, rejecting a snapshot from another editor.

#### Tradeoffs and production boundaries

- **Pros**
  - Snapshot logic stays with the object that understands its invariants.
- **Cons**
  - Large snapshots consume memory.
  - Restoring stale state may overwrite concurrent work.
- **Variation shown**
  - Multiple undo levels and owner validation.
- **Production adaptation**
  - Bound history length or use deltas for large states.
  - Use a version check before restoring shared persisted state.
  - Python's leading-underscore privacy is convention, not a security boundary.
  - Restoring memory cannot reverse an already committed database transaction.
- **Choose instead**
  - [Command](#command) with inverse operations when snapshots are expensive and inverses are reliable.

```java
import java.util.*;

public class Main {
    static class Editor {
        String text = "";
        static final class Snapshot {
            private final Editor owner;
            private final String text;
            private Snapshot(Editor owner, String text) { this.owner = owner; this.text = text; }
        }
        Snapshot save() { return new Snapshot(this, text); }
        void restore(Snapshot snapshot) {
            if (snapshot.owner != this) throw new IllegalArgumentException("wrong editor");
            text = snapshot.text;
        }
    }
    public static void main(String[] args) {
        Editor editor = new Editor();
        Deque<Editor.Snapshot> history = new ArrayDeque<>();
        history.push(editor.save());
        editor.text = "hello";
        history.push(editor.save());
        editor.text = "hello world";
        editor.restore(history.pop());
        assert editor.text.equals("hello");
        editor.restore(history.pop());
        assert editor.text.isEmpty();
        try { editor.restore(new Editor().save()); throw new AssertionError(); }
        catch (IllegalArgumentException expected) { /* ownership enforced */ }
    }
}
```

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class _Snapshot:
    owner: object
    text: str

class Editor:
    def __init__(self):
        self.text = ""
        self._token = object()

    def save(self) -> _Snapshot:
        return _Snapshot(self._token, self.text)

    def restore(self, snapshot: _Snapshot):
        if snapshot.owner is not self._token:
            raise ValueError("wrong editor")
        self.text = snapshot.text

editor = Editor()
history = [editor.save()]
editor.text = "hello"
history.append(editor.save())
editor.text = "hello world"
editor.restore(history.pop())
assert editor.text == "hello"
editor.restore(history.pop())
assert editor.text == ""
try:
    editor.restore(Editor().save())
    raise AssertionError("ownership error expected")
except ValueError:
    pass
```

<a id="observer"></a>
### 3.7 Observer

#### Concept and analogy

- **Problem**
  - A publisher directly knows every display or subsystem that reacts to its changes.
- **Pattern**
  - Let observers subscribe to changes through a common notification contract.
- **Analogy**
  - Subscribers receive a newspaper without the publisher embedding each reader's daily routine.
- **Common uses**
  - UI listeners.
  - In-process domain notifications.
  - Monitoring displays.

#### Mechanism and adaptation

- Subject: stores subscriptions and publishes an event.
- Observer: consumes the event.
- Push variation: event carries data.
- Pull variation: event indicates a change and the observer asks for current state.
- Take a subscription snapshot before iterating if callbacks may unsubscribe.

→ Register displays on a weather station.  
→ Publish temperature to a snapshot of subscribers.  
→ Collect individual callback failures while continuing other deliveries.

#### Tradeoffs and production boundaries

- **Pros**
  - New subscribers do not require changing the publisher.
- **Cons**
  - Synchronous slow observers delay the publisher.
  - Forgotten subscriptions retain objects.
- **Variation shown**
  - Explicit unsubscribe.
  - One failing observer does not prevent another from receiving the event.
  - Failures are returned to the caller rather than silently discarded.
- **Production adaptation**
  - In-process callbacks are not a durable message broker.
  - Do not send irreversible external notifications before the database commit.
  - Use an outbox for durable post-commit publication and make consumers idempotent. [AWS transactional outbox guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)
- **Choose instead**
  - [Mediator](#mediator) when central interaction rules matter more than subscriptions.

```java
import java.util.*;
import java.util.function.IntConsumer;

public class Main {
    static class Weather {
        final List<IntConsumer> observers = new ArrayList<>();
        Runnable subscribe(IntConsumer observer) {
            observers.add(observer);
            return () -> observers.remove(observer);
        }
        List<RuntimeException> publish(int temperature) {
            List<RuntimeException> errors = new ArrayList<>();
            for (IntConsumer observer : List.copyOf(observers)) {
                try { observer.accept(temperature); }
                catch (RuntimeException error) { errors.add(error); }
            }
            return errors;
        }
    }
    public static void main(String[] args) {
        Weather weather = new Weather();
        List<Integer> display = new ArrayList<>();
        weather.subscribe(t -> { throw new IllegalStateException("broken display"); });
        Runnable unsubscribe = weather.subscribe(display::add);
        assert weather.publish(20).size() == 1;
        assert display.equals(List.of(20));
        unsubscribe.run();
        weather.publish(21);
        assert display.equals(List.of(20));
    }
}
```

```python
class Weather:
    def __init__(self):
        self.observers: dict[object, object] = {}

    def subscribe(self, observer):
        token = object()
        self.observers[token] = observer
        return lambda: self.observers.pop(token, None)

    def publish(self, temperature: int) -> list[Exception]:
        errors = []
        for observer in list(self.observers.values()):
            try:
                observer(temperature)
            except Exception as error:
                errors.append(error)
        return errors

def broken_display(temperature):
    raise RuntimeError("broken display")

weather, display = Weather(), []
weather.subscribe(broken_display)
unsubscribe = weather.subscribe(display.append)
assert len(weather.publish(20)) == 1
assert display == [20]
unsubscribe()
weather.publish(21)
assert display == [20]
```

<a id="state"></a>
### 3.8 State

#### Concept and analogy

- **Problem**
  - Every operation repeats a switch over the object's current lifecycle stage.
  - Transitions can produce invalid combinations of flags.
- **Pattern**
  - Represent each state as an object implementing the same event interface.
  - Delegate event behavior to the current state.
- **Analogy**
  - A turnstile reacts differently to a coin when locked and when already unlocked.
- **Common uses**
  - Order lifecycles.
  - Connection protocols.
  - Vending machines.

#### Mechanism and adaptation

- Context: turnstile with a current-state reference.
- State: behavior for `coin` and `push`.
- Transition: replace the current-state reference after a valid event.
- Immutable stateless state objects may be shared.
  - Per-order data belongs to the context, not a shared state instance.

→ Locked turnstile receives a coin and becomes unlocked.  
→ Another coin is refunded without another transition.  
→ A push passes the user and returns the turnstile to locked.

#### Tradeoffs and production boundaries

- **Pros**
  - Makes allowed transitions and state-specific behavior explicit.
- **Cons**
  - Many tiny classes may be unnecessary for a small stable state machine.
  - Transitions spread across states can be difficult to audit.
- **Variation shown**
  - Repeated coin and repeated push events have defined behavior.
- **Production adaptation**
  - Persist a version with an order state.
  - Update using `WHERE id = ? AND version = ?` and verify the affected-row count.
  - A state class does not resolve concurrent transitions across processes.
  - Repeated-event behavior is not durable request deduplication.
- **Choose instead**
  - A transition table or enum switch when the state graph is small and behavior is simple.

```java
public class Main {
    interface State {
        String coin(Gate gate);
        String push(Gate gate);
    }
    enum Locked implements State {
        INSTANCE;
        public String coin(Gate g) { g.state = Open.INSTANCE; return "unlock"; }
        public String push(Gate g) { return "blocked"; }
    }
    enum Open implements State {
        INSTANCE;
        public String coin(Gate g) { return "refund"; }
        public String push(Gate g) { g.state = Locked.INSTANCE; return "pass"; }
    }
    static class Gate {
        State state = Locked.INSTANCE;
        String coin() { return state.coin(this); }
        String push() { return state.push(this); }
    }
    public static void main(String[] args) {
        Gate gate = new Gate();
        assert gate.push().equals("blocked");
        assert gate.coin().equals("unlock");
        assert gate.coin().equals("refund");
        assert gate.push().equals("pass");
        assert gate.push().equals("blocked");
    }
}
```

```python
class Locked:
    def coin(self, gate):
        gate.state = OPEN
        return "unlock"

    def push(self, gate):
        return "blocked"

class Open:
    def coin(self, gate):
        return "refund"

    def push(self, gate):
        gate.state = LOCKED
        return "pass"

LOCKED, OPEN = Locked(), Open()

class Gate:
    def __init__(self):
        self.state = LOCKED

    def coin(self):
        return self.state.coin(self)

    def push(self):
        return self.state.push(self)

gate = Gate()
assert gate.push() == "blocked"
assert gate.coin() == "unlock"
assert gate.coin() == "refund"
assert gate.push() == "pass"
assert gate.push() == "blocked"
```

<a id="strategy"></a>
### 3.9 Strategy

#### Concept and analogy

- **Problem**
  - An operation contains a growing conditional choosing among interchangeable algorithms.
- **Pattern**
  - Put each algorithm behind a shared contract and inject the chosen one.
- **Analogy**
  - A navigation app calculates a route using walking, driving, or cycling rules.
- **Common uses**
  - Pricing policies.
  - Sorting comparators.
  - Routing and retry policies.

#### Mechanism and adaptation

- Context: calls the selected strategy.
- Strategy: defines the input/output contract.
- Concrete strategy: one algorithm or policy.
- A function is sufficient when the algorithm needs no lifecycle or mutable state.

→ Choose a price policy.  
→ Pass a subtotal into the same checkout calculation.  
→ Switch policy without changing checkout.

#### Tradeoffs and production boundaries

- **Pros**
  - Algorithms can be tested and replaced independently.
- **Cons**
  - The caller still needs a selection policy.
  - Strategies are only interchangeable if their guarantees match.
- **Variation shown**
  - Standard pricing.
  - Percentage discount with integer rounding.
  - Fixed coupon with a nonnegative result.
- **Production adaptation**
  - Snapshot the pricing-policy version on a durable order.
  - A retry should not silently reprice an already accepted order under a new policy.
  - A retry strategy chooses attempts and delays; it does not make side effects idempotent.
- **Choose instead**
  - [State](#state) when the object's lifecycle determines behavior and transitions select the next behavior.

```java
import java.util.function.IntUnaryOperator;

public class Main {
    static int checkout(int subtotal, IntUnaryOperator price) {
        if (subtotal < 0) throw new IllegalArgumentException();
        return price.applyAsInt(subtotal);
    }
    static IntUnaryOperator coupon(int cents) {
        if (cents < 0) throw new IllegalArgumentException();
        return subtotal -> Math.max(0, subtotal - cents);
    }
    public static void main(String[] args) {
        IntUnaryOperator standard = subtotal -> subtotal;
        IntUnaryOperator member = subtotal -> (int) ((long) subtotal * 90 / 100);
        assert checkout(1000, standard) == 1000;
        assert checkout(1000, member) == 900;
        assert checkout(1000, coupon(1200)) == 0;
    }
}
```

```python
from collections.abc import Callable

def checkout(subtotal: int, price: Callable[[int], int]) -> int:
    if subtotal < 0:
        raise ValueError("negative subtotal")
    return price(subtotal)

def standard(subtotal: int) -> int:
    return subtotal

def member(subtotal: int) -> int:
    return subtotal * 90 // 100

def coupon(cents: int) -> Callable[[int], int]:
    if cents < 0:
        raise ValueError("negative coupon")
    return lambda subtotal: max(0, subtotal - cents)

assert checkout(1000, standard) == 1000
assert checkout(1000, member) == 900
assert checkout(1000, coupon(1200)) == 0
```

<a id="template-method"></a>
### 3.10 Template Method

#### Concept and analogy

- **Problem**
  - Several implementations repeat the same algorithm skeleton with a few differing steps.
- **Pattern**
  - Put the skeleton in a base method.
  - Let subclasses override selected steps or hooks.
- **Analogy**
  - Tea and coffee follow the same kitchen procedure but brew and add condiments differently.
- **Common uses**
  - Import pipelines.
  - Framework lifecycle methods.
  - Test fixture setup and teardown.

#### Mechanism and adaptation

- Template: fixed step ordering.
- Primitive operations: required subclass-specific steps.
- Hook: optional policy with a default implementation.
- Java can mark the skeleton `final` to prevent overriding its order.
  - Python relies on API discipline unless additional enforcement is added.

→ Boil water.  
→ Brew using a subclass step.  
→ Pour, then optionally add condiments through a hook.

#### Tradeoffs and production boundaries

- **Pros**
  - Shared ordering and invariants live in one place.
- **Cons**
  - Subclasses are coupled to the base class's lifecycle.
  - Too many hooks make the actual workflow difficult to predict.
- **Variation shown**
  - Tea and coffee share a skeleton.
  - A hook disables optional condiments.
- **Production adaptation**
  - A transaction template can own begin, work, commit, and rollback.
  - The work callback must use the connection supplied by that template.
  - Catching an error and returning success can accidentally commit partial work.
- **Choose instead**
  - [Strategy](#strategy) or callbacks when behavior must be composed at runtime without inheritance.

```java
import java.util.*;

public class Main {
    static abstract class Beverage {
        abstract String brew();
        abstract String condiment();
        boolean wantsCondiments() { return true; }
        final List<String> prepare() {
            List<String> steps = new ArrayList<>(List.of("boil", brew(), "pour"));
            if (wantsCondiments()) steps.add(condiment());
            return List.copyOf(steps);
        }
    }
    static class Tea extends Beverage {
        String brew() { return "steep tea"; }
        String condiment() { return "lemon"; }
    }
    static class Coffee extends Beverage {
        final boolean milk;
        Coffee(boolean milk) { this.milk = milk; }
        String brew() { return "brew coffee"; }
        String condiment() { return "milk"; }
        boolean wantsCondiments() { return milk; }
    }
    public static void main(String[] args) {
        assert new Tea().prepare().equals(List.of("boil", "steep tea", "pour", "lemon"));
        assert new Coffee(false).prepare().size() == 3;
        assert new Coffee(true).prepare().get(3).equals("milk");
    }
}
```

```python
from abc import ABC, abstractmethod

class Beverage(ABC):
    @abstractmethod
    def brew(self) -> str: ...

    @abstractmethod
    def condiment(self) -> str: ...

    def wants_condiments(self) -> bool:
        return True

    def prepare(self) -> tuple[str, ...]:
        steps = ["boil", self.brew(), "pour"]
        if self.wants_condiments():
            steps.append(self.condiment())
        return tuple(steps)

class Tea(Beverage):
    def brew(self):
        return "steep tea"

    def condiment(self):
        return "lemon"

class Coffee(Beverage):
    def __init__(self, milk: bool):
        self.milk = milk

    def brew(self):
        return "brew coffee"

    def condiment(self):
        return "milk"

    def wants_condiments(self):
        return self.milk

assert Tea().prepare() == ("boil", "steep tea", "pour", "lemon")
assert len(Coffee(False).prepare()) == 3
assert Coffee(True).prepare()[-1] == "milk"
```

<a id="visitor"></a>
### 3.11 Visitor

#### Concept and analogy

- **Problem**
  - Many new operations must run over a stable collection of element types.
  - Each new operation otherwise modifies all those element classes.
- **Pattern**
  - Elements accept a visitor and dispatch to the visitor method for their concrete type.
- **Analogy**
  - A building accepts different inspectors who each examine the same rooms for a different purpose.
- **Common uses**
  - Compiler syntax trees.
  - Document export.
  - Operations over stable shape hierarchies.

#### Mechanism and adaptation

- Element: exposes `accept`.
- Visitor: exposes one method per concrete element type.
- Double dispatch: element runtime type chooses the visitor entry point, and visitor runtime type chooses the operation.
- Java overload resolution alone is static; the element's `accept` method supplies the concrete type at the call site.

→ Pass an area or export visitor to a shape.  
→ Shape calls its type-specific visit method.  
→ Visitor returns the result without embedding that operation in every shape.

#### Tradeoffs and production boundaries

- **Pros**
  - Add operations without changing an established element hierarchy.
- **Cons**
  - Adding an element type requires updating all visitors.
  - Visitors may demand access to internal details.
- **Variation shown**
  - Area calculation and text export over circles and rectangles.
- **Production adaptation**
  - Keep visitors stateless or scope mutable accumulation to one traversal.
  - A read-only visitor is easier to reason about than a visitor mutating a graph during traversal.
  - Version AST schemas when visitor implementations are deployed separately.
- **Choose instead**
  - Polymorphic methods on elements when element types change often but operations are stable.

```java
import java.util.*;

public class Main {
    interface Shape { <R> R accept(Visitor<R> visitor); }
    interface Visitor<R> {
        R circle(Circle circle);
        R rectangle(Rectangle rectangle);
    }
    record Circle(double radius) implements Shape {
        public <R> R accept(Visitor<R> v) { return v.circle(this); }
    }
    record Rectangle(double width, double height) implements Shape {
        public <R> R accept(Visitor<R> v) { return v.rectangle(this); }
    }
    static class Area implements Visitor<Double> {
        public Double circle(Circle c) { return Math.PI * c.radius() * c.radius(); }
        public Double rectangle(Rectangle r) { return r.width() * r.height(); }
    }
    static class Export implements Visitor<String> {
        public String circle(Circle c) { return "circle:" + c.radius(); }
        public String rectangle(Rectangle r) { return "rectangle:" + r.width() + "," + r.height(); }
    }
    public static void main(String[] args) {
        List<Shape> shapes = List.of(new Circle(1), new Rectangle(2, 3));
        double total = shapes.stream().mapToDouble(s -> s.accept(new Area())).sum();
        assert Math.abs(total - (Math.PI + 6)) < 1e-9;
        assert shapes.get(1).accept(new Export()).equals("rectangle:2.0,3.0");
    }
}
```

```python
from dataclasses import dataclass
import math

@dataclass(frozen=True)
class Circle:
    radius: float

    def accept(self, visitor):
        return visitor.circle(self)

@dataclass(frozen=True)
class Rectangle:
    width: float
    height: float

    def accept(self, visitor):
        return visitor.rectangle(self)

class Area:
    def circle(self, circle: Circle) -> float:
        return math.pi * circle.radius ** 2

    def rectangle(self, rectangle: Rectangle) -> float:
        return rectangle.width * rectangle.height

class Export:
    def circle(self, circle: Circle) -> str:
        return f"circle:{circle.radius}"

    def rectangle(self, rectangle: Rectangle) -> str:
        return f"rectangle:{rectangle.width},{rectangle.height}"

shapes = [Circle(1), Rectangle(2, 3)]
assert math.isclose(sum(s.accept(Area()) for s in shapes), math.pi + 6)
assert shapes[1].accept(Export()) == "rectangle:2,3"
```

<a id="comparison"></a>
## 4. Choosing between similar patterns

- Choose the abstraction by the expected change.
  - A matching class diagram does not imply a matching intent.
  - A wrapper can implement more than one pattern when its responsibilities warrant it.

| Option | What it is | Strength | Weakness | Choose when |
| --- | --- | --- | --- | --- |
| Abstract Factory | Creates a compatible product family | One family decision controls related products | New product types affect every factory | Backend or theme families vary together |
| Factory Method | Subclass hook for creating a workflow's product | Reuses the workflow skeleton | Subclass proliferation | Framework subclasses determine a product |
| Builder | Staged, validated assembly | Expresses optional choices and invariants | Mutable intermediate state | Construction is complex |
| Prototype | Copy an existing configured object | Reuses setup state | Copy and identity semantics are difficult | Templates are the natural starting point |
| Singleton | Controlled instance within a runtime scope | Central lifecycle owner | Hidden dependencies and shared-state coupling | A genuinely process-scoped resource is required |
| Adapter | Translates incompatible contracts | Reuses a legacy component | Semantic mismatches may remain | An existing interface does not fit |
| Bridge | Composes two independently varying dimensions | Avoids combination subclasses | Requires a stable implementor contract | Both dimensions are part of the design |
| Composite | Uniform leaf and tree operations | Recursive composition | Cycles and deep trees need policy | The domain has part-whole hierarchy |
| Decorator | Adds behavior through compatible wrappers | Runtime feature combinations | Ordering and hidden cost | Optional responsibilities stack |
| Facade | Small API over a subsystem | Centralizes common use cases | Can become an oversized service | Callers need a simpler entry point |
| Flyweight | Shared immutable intrinsic state | Reduces repeated representation | Retention and key complexity | Repetition is high relative to key diversity |
| Proxy | Controlled access through a stand-in | Centralizes lazy or restricted access | Hidden latency and advice bypass | Access itself needs interception |
| Chain of Responsibility | Tries handlers in sequence | Configurable routing | Unhandled requests and order dependence | Receiver emerges from ordered rules |
| Command | Reifies an action as data plus execution | Queueing and history | Replay and undo require semantics | Requests need a lifecycle of their own |
| Interpreter | Expression tree evaluated in context | Small language composition | Poor fit for large grammars | Rules form a small stable grammar |
| Iterator | Separate traversal cursor | Hides storage and supports laziness | Resource and snapshot lifetime | Incremental traversal is useful |
| Mediator | Central interaction policy among colleagues | Reduces peer coupling | Central policy can grow too large | Peers need coordinated behavior |
| Memento | Opaque captured state | Encapsulated undo | Snapshot cost and stale restores | State restoration is the natural inverse |
| Observer | Subscription-based notification | Extensible reactions | Ordering and delivery are unspecified without extra policy | Publishers announce changes |
| State | Behavior selected by lifecycle state | Explicit transitions | State and transition complexity | History determines valid next actions |
| Strategy | Interchangeable algorithm | Independent policy replacement | Selection moves to caller | Algorithms vary independently |
| Template Method | Fixed skeleton with subclass steps | Preserves workflow order | Inheritance coupling | Sequence is stable and steps vary |
| Visitor | New operations over stable types | Operation growth without element edits | Type growth affects all visitors | Operations change more than element types |

### Defaults for common backend situations

- **Multiple payment providers**
  - Use an adapter to normalize each provider's API.
  - Use a strategy to select the routing policy.
  - Add an abstract factory only if several provider-specific collaborators must be selected together.
- **HTTP request handling**
  - A controller translates the transport request into an application call.
  - A facade or application service coordinates the use case.
  - Middleware often resembles a chain of responsibility.
  - MVC and front controller are architectural patterns outside the GoF catalog.
- **Database writes**
  - A repository hides data-access operations.
  - A unit of work coordinates changes within a transaction boundary.
  - Repository and Unit of Work are additional persistence patterns, not extra GoF entries.
  - The database and schema enforce the actual transactional guarantees.
- **One variable calculation**
  - Start with a strategy function.
  - Add a class when configuration, lifecycle, or a richer contract justifies it.
- **Front-desk analogy**
  - Proxy: gate access to one represented service.
  - Facade: offer one convenient request that invokes several services.
  - Mediator: coordinate how those services interact with one another.

<a id="production"></a>
## 5. Production composition: transactions, ACID, and idempotency

### 5.1 What belongs to the pattern and what belongs to the database

- A design pattern assigns responsibilities.
- A database transaction provides guarantees according to its engine, isolation level, and durability settings.
- A transaction wrapper is useful only if all relevant SQL uses the same participating connection.
- A mutex around a command protects only callers sharing that mutex.
  - It does not survive a crash.
  - It does not coordinate another process.

| ACID property | Concrete requirement | Mechanism | Important boundary |
| --- | --- | --- | --- |
| Atomicity | Debit, credit, deduplication result, and outbox row commit together | One database transaction | An HTTP call to another service is outside this local transaction |
| Consistency | Balances remain nonnegative and transfers satisfy domain rules | Constraints plus validated operations | A database cannot infer unspecified business rules |
| Isolation | Concurrent transfers do not observe or overwrite invalid intermediate state | Conditional updates, row locks, or serializable execution | Weaker isolation needs an anomaly-specific argument |
| Durability | An acknowledged commit survives the promised failures | Database logging and configured durable storage | An in-memory database cannot survive process loss |

- In JDBC, disabling auto-commit groups statements until explicit commit or rollback. [Java 17 `Connection`](https://docs.oracle.com/en/java/javase/17/docs/api/java.sql/java/sql/Connection.html)
- PostgreSQL serializable transactions can abort because of concurrency.
  - Retry the entire transaction with fresh reads.
  - Do not retry only its last statement. [PostgreSQL isolation documentation](https://www.postgresql.org/docs/16/transaction-iso.html)

### 5.2 Composition and invariant

- **Use case**
  - Transfer integer cents between two accounts.
  - Retrying one logical transfer must return its original receipt without debiting twice.
- **Assumptions**
  - The example serves one authenticated tenant.
  - The request ID is unique within this transfer operation.
  - There are no external side effects inside the transaction.
  - Real multi-tenant storage uses a unique key such as `(tenant_id, operation, request_id)`.
- **Invariant**
  - A successful request has one committed result row.
  - Its debit, credit, and outbox event exist in the same commit.
  - A duplicate ID with different source, destination, or amount is rejected.
  - A failed transfer leaves none of those writes committed.
- **Composition**
  - Command: immutable transfer arguments.
  - Facade: `transfer` entry point.
  - Template/Unit of Work: owns transaction start, commit, and rollback.
  - Observer boundary: an outbox stores an event for later publication.
  - Strategy extension: a bounded retry policy around the entire transaction.
  - Database uniqueness and transactions enforce deduplication, not the class names.

→ Authenticate and establish tenant scope.  
→ Validate the request.  
→ Begin a transaction and check the scoped request ID.  
→ If already committed, compare payload and return the stored receipt.  
→ Otherwise debit conditionally and credit the destination.  
→ Store the result and outbox event.  
→ Commit once, then return the receipt.  
⇒ A later retry returns the original result even if the first response was lost.

### 5.3 Why these examples use different concurrency mechanisms

- **Java**
  - Uses JDBC interfaces from Java SE.
  - Runtime requires an H2 JDBC driver and a JDBC URL.
  - Account updates use database locks through SQL writes.
  - The unique request ID is the final arbiter when concurrent requests race.
  - A losing concurrent attempt rolls back all its tentative changes.
  - The caller can retry that request to observe the winning result.
  - Compilation does not require importing H2 classes.
- **Python**
  - Uses the standard-library `sqlite3` module.
  - Explicit `BEGIN IMMEDIATE` acquires the SQLite write transaction before the read/check/write sequence.
  - SQLite's single-writer behavior serializes these writers.
    - `BEGIN IMMEDIATE` can wait or fail with a busy error when another writer holds the transaction. [SQLite transaction rules](https://www.sqlite.org/lang_transaction.html)
  - This is a useful small-database example, not a claim that a global writer lock scales to a large payment service.
  - The connection uses `isolation_level=None` so this snippet controls transactions explicitly. [Python sqlite3 transaction control](https://docs.python.org/3/library/sqlite3.html#transaction-control)
- **Both**
  - Use a fresh database for the demonstration's schema and seed data.
  - Preserve a receipt in the deduplication row rather than recomputing an answer from later balances.
  - Test a failure after the debit and before the credit to exercise rollback.
  - Memory-mode demo runs validate behavior, not crash durability.
  - Credit updates guard the signed 64-bit range so overflow cannot silently change the amount representation.

### 5.4 Worked Java and Python examples

- **Variations exercised by the included checks**
  - First successful transfer.
  - Replayed identical request.
  - Reused ID with a changed payload.
  - Injected mid-transaction failure followed by a safe retry.
  - Missing destination after a tentative debit.
  - Insufficient funds.
  - A destination balance at the supported integer limit.
- **Java runtime**
  - Put an H2 driver JAR on the runtime classpath.
  - Run `java -ea -cp ".;h2.jar" Main` on Windows after compilation.
  - The default URL is an in-memory H2 database kept alive for this process.
  - A file-backed H2 URL can be supplied as the first argument for a fresh test database.
  - Do not rerun the schema-creation demo against an existing production database.

→ Construct a transfer command.  
→ Execute it through the transaction-owning facade.  
→ Verify replay, payload conflict, rollback, balances, and outbox count.

```java
import java.sql.*;
import java.util.Objects;

public class Main {
    record Transfer(String id, String from, String to, long cents) {}
    static String url;
    static Connection open() throws SQLException { return DriverManager.getConnection(url); }

    static int write(Connection c, String sql, Object... values) throws SQLException {
        try (PreparedStatement p = c.prepareStatement(sql)) {
            for (int i = 0; i < values.length; i++) p.setObject(i + 1, values[i]);
            return p.executeUpdate();
        }
    }

    static void initialize() throws SQLException {
        try (Connection c = open(); Statement s = c.createStatement()) {
            s.execute("CREATE TABLE accounts (id VARCHAR(80) PRIMARY KEY, " +
                "cents BIGINT NOT NULL CHECK (cents >= 0))");
            s.execute("CREATE TABLE requests (id VARCHAR(80) PRIMARY KEY, " +
                "src VARCHAR(80) NOT NULL, dst VARCHAR(80) NOT NULL, " +
                "amount BIGINT NOT NULL CHECK (amount > 0), receipt VARCHAR(100) NOT NULL)");
            s.execute("CREATE TABLE outbox (id VARCHAR(80) PRIMARY KEY, " +
                "event_type VARCHAR(80) NOT NULL, request_id VARCHAR(80) NOT NULL " +
                "REFERENCES requests(id))");
            write(c, "INSERT INTO accounts VALUES (?, ?)", "A", 1000L);
            write(c, "INSERT INTO accounts VALUES (?, ?)", "B", 0L);
        }
    }

    static String transfer(Transfer t, boolean failAfterDebit) throws SQLException {
        Objects.requireNonNull(t.id());
        Objects.requireNonNull(t.from());
        Objects.requireNonNull(t.to());
        if (t.id().isBlank() || t.cents() <= 0 || t.from().equals(t.to()))
            throw new IllegalArgumentException("invalid transfer");
        try (Connection c = open()) {
            c.setAutoCommit(false);
            try {
                try (PreparedStatement p = c.prepareStatement(
                        "SELECT src, dst, amount, receipt FROM requests WHERE id = ?")) {
                    p.setString(1, t.id());
                    try (ResultSet r = p.executeQuery()) {
                        if (r.next()) {
                            if (!r.getString(1).equals(t.from()) ||
                                !r.getString(2).equals(t.to()) || r.getLong(3) != t.cents())
                                throw new IllegalArgumentException("ID reused with different payload");
                            String receipt = r.getString(4);
                            c.commit();
                            return receipt;
                        }
                    }
                }
                if (write(c, "UPDATE accounts SET cents = cents - ? " +
                        "WHERE id = ? AND cents >= ?", t.cents(), t.from(), t.cents()) != 1)
                    throw new IllegalArgumentException("missing source or insufficient funds");
                if (failAfterDebit) throw new IllegalStateException("injected failure");
                if (write(c, "UPDATE accounts SET cents = cents + ? WHERE id = ? AND cents <= ?",
                        t.cents(), t.to(), Long.MAX_VALUE - t.cents()) != 1)
                    throw new IllegalArgumentException("missing destination or balance overflow");
                String receipt = "accepted:" + t.id();
                write(c, "INSERT INTO requests VALUES (?, ?, ?, ?, ?)",
                    t.id(), t.from(), t.to(), t.cents(), receipt);
                write(c, "INSERT INTO outbox VALUES (?, ?, ?)",
                    t.id(), "transfer.accepted", t.id());
                c.commit();
                return receipt;
            } catch (SQLException | RuntimeException | Error error) {
                try { c.rollback(); }
                catch (SQLException rollbackError) { error.addSuppressed(rollbackError); }
                throw error;
            }
        }
    }

    static long scalar(String sql) throws SQLException {
        try (Connection c = open(); Statement s = c.createStatement();
             ResultSet r = s.executeQuery(sql)) {
            r.next();
            return r.getLong(1);
        }
    }

    public static void main(String[] args) throws Exception {
        url = args.length == 0 ? "jdbc:h2:mem:patterns;DB_CLOSE_DELAY=-1" : args[0];
        initialize();
        Transfer first = new Transfer("r1", "A", "B", 100);
        String receipt = transfer(first, false);
        assert transfer(first, false).equals(receipt);
        try { transfer(new Transfer("r1", "A", "B", 101), false); throw new AssertionError(); }
        catch (IllegalArgumentException expected) { /* same ID, different meaning */ }
        Transfer second = new Transfer("r2", "A", "B", 200);
        try { transfer(second, true); throw new AssertionError(); }
        catch (IllegalStateException expected) { /* debit must roll back */ }
        assert scalar("SELECT cents FROM accounts WHERE id = 'A'") == 900;
        assert scalar("SELECT COUNT(*) FROM requests") == 1;
        transfer(second, false);
        try { transfer(new Transfer("r3", "A", "missing", 10), false); throw new AssertionError(); }
        catch (IllegalArgumentException expected) { /* missing credit target */ }
        try { transfer(new Transfer("r4", "A", "B", 9999), false); throw new AssertionError(); }
        catch (IllegalArgumentException expected) { /* no overdraft */ }
        try (Connection c = open()) {
            write(c, "INSERT INTO accounts VALUES (?, ?)", "full", Long.MAX_VALUE);
        }
        try { transfer(new Transfer("r5", "A", "full", 1), false); throw new AssertionError(); }
        catch (IllegalArgumentException expected) { /* credit overflow rolls back debit */ }
        assert scalar("SELECT cents FROM accounts WHERE id = 'A'") == 700;
        assert scalar("SELECT cents FROM accounts WHERE id = 'B'") == 300;
        assert scalar("SELECT COUNT(*) FROM outbox") == 2;
    }
}
```

```python
from dataclasses import dataclass
import sqlite3

@dataclass(frozen=True)
class Transfer:
    id: str
    source: str
    destination: str
    cents: int

def initialize(c: sqlite3.Connection):
    c.executescript("""
        CREATE TABLE accounts (
            id TEXT PRIMARY KEY NOT NULL,
            cents INTEGER NOT NULL CHECK (typeof(cents) = 'integer' AND cents >= 0)
        );
        CREATE TABLE requests (
            id TEXT PRIMARY KEY NOT NULL,
            src TEXT NOT NULL, dst TEXT NOT NULL,
            amount INTEGER NOT NULL CHECK (amount > 0),
            receipt TEXT NOT NULL
        );
        CREATE TABLE outbox (
            id TEXT PRIMARY KEY NOT NULL,
            event_type TEXT NOT NULL,
            request_id TEXT NOT NULL REFERENCES requests(id)
        );
        INSERT INTO accounts VALUES ('A', 1000), ('B', 0);
    """)

def transfer(c: sqlite3.Connection, t: Transfer, fail_after_debit=False) -> str:
    max_cents = (1 << 63) - 1
    if (type(t.cents) is not int or not 0 < t.cents <= max_cents
            or not t.id.strip() or t.source == t.destination):
        raise ValueError("invalid transfer")
    c.execute("BEGIN IMMEDIATE")  # Acquire the write transaction before checking.
    try:
        prior = c.execute(
            "SELECT src, dst, amount, receipt FROM requests WHERE id = ?", (t.id,)
        ).fetchone()
        if prior is not None:
            if prior[:3] != (t.source, t.destination, t.cents):
                raise ValueError("ID reused with different payload")
            c.commit()
            return prior[3]
        debit = c.execute(
            "UPDATE accounts SET cents = cents - ? WHERE id = ? AND cents >= ?",
            (t.cents, t.source, t.cents),
        )
        if debit.rowcount != 1:
            raise ValueError("missing source or insufficient funds")
        if fail_after_debit:
            raise RuntimeError("injected failure")
        credit = c.execute(
            "UPDATE accounts SET cents = cents + ? WHERE id = ? AND cents <= ?",
            (t.cents, t.destination, max_cents - t.cents),
        )
        if credit.rowcount != 1:
            raise ValueError("missing destination or balance overflow")
        receipt = f"accepted:{t.id}"
        c.execute("INSERT INTO requests VALUES (?, ?, ?, ?, ?)",
                  (t.id, t.source, t.destination, t.cents, receipt))
        c.execute("INSERT INTO outbox VALUES (?, ?, ?)",
                  (t.id, "transfer.accepted", t.id))
        c.commit()
        return receipt
    except BaseException:
        c.rollback()
        raise

c = sqlite3.connect(":memory:", isolation_level=None)
c.execute("PRAGMA foreign_keys = ON")
try:
    initialize(c)
    first = Transfer("r1", "A", "B", 100)
    receipt = transfer(c, first)
    assert transfer(c, first) == receipt
    try:
        transfer(c, Transfer("r1", "A", "B", 101))
        raise AssertionError("payload conflict expected")
    except ValueError:
        pass
    second = Transfer("r2", "A", "B", 200)
    try:
        transfer(c, second, fail_after_debit=True)
        raise AssertionError("injected failure expected")
    except RuntimeError:
        pass
    assert c.execute("SELECT cents FROM accounts WHERE id = 'A'").fetchone()[0] == 900
    assert c.execute("SELECT COUNT(*) FROM requests").fetchone()[0] == 1
    transfer(c, second)
    for invalid in (Transfer("r3", "A", "missing", 10), Transfer("r4", "A", "B", 9999)):
        try:
            transfer(c, invalid)
            raise AssertionError("invalid transfer accepted")
        except ValueError:
            pass
    c.execute("INSERT INTO accounts VALUES (?, ?)", ("full", (1 << 63) - 1))
    try:
        transfer(c, Transfer("r5", "A", "full", 1))
        raise AssertionError("overflow expected")
    except ValueError:
        pass
    assert c.execute("SELECT cents FROM accounts WHERE id IN ('A', 'B') ORDER BY id").fetchall() == [(700,), (300,)]
    assert c.execute("SELECT COUNT(*) FROM outbox").fetchone()[0] == 2
finally:
    c.close()
```

### 5.5 Concurrent callers, ambiguous commits, and external effects

- **Concurrent same-ID calls in the Java example**
  - Both can initially read no result at ordinary read-committed isolation.
  - One may wait on the other's account update.
  - The unique request row prevents both from committing.
  - The loser can receive a uniqueness conflict, lock timeout, deadlock, or domain error after rechecking the balance.
  - Retry by the same ID on a fresh transaction to discover a committed winning result.
  - A production handler should classify these outcomes and query the request result before reporting a final domain rejection.
  - The example guarantees that duplicate tentative database effects cannot both commit; it does not transparently make every concurrent caller return success on its first attempt.
- **Alternative: claim the ID first**
  - Insert the unique request row before modifying balances, in the same transaction.
  - Store or complete the response before commit.
  - A conflict handler must first roll back an aborted transaction before reading a winner's result.
  - Avoid committing a permanent `IN_PROGRESS` claim without a recovery protocol.
- **Ambiguous commit**
  - A lost network connection during commit can leave the client unsure whether the database committed.
  - A subsequent rollback attempt cannot prove that the previous commit failed.
  - Return a retryable/unknown outcome according to the API contract.
  - Retry or reconcile using the same request ID.
  - Never generate a fresh ID merely because the response was lost.
- **Retry ownership**
  - Bound total attempts and elapsed time.
  - Retry a whole transaction after retryable concurrency failures.
  - Use exponential backoff with jitter where appropriate.
  - A validation failure or payload mismatch is terminal.
  - Keep external calls out of replayed transaction callbacks unless they use a separate proven idempotency protocol.
- **Outbox relay**
  - Read committed outbox rows.
  - Publish an event containing a stable event ID.
  - Mark the row delivered after broker acknowledgement.
  - A crash between publish and marking creates a duplicate delivery.
  - Consumers need deduplication committed atomically with their own business effect.
  - The examples only write the outbox; they do not implement a relay. [AWS transactional outbox guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)
- **Retention**
  - Deleting an idempotency record reopens the possibility of repeating its effect.
  - Retain records for the declared retry horizon, or retain a permanent business uniqueness constraint.
  - Store the canonical request fields or a versioned canonical digest to detect key reuse.
- **Account invariants beyond the demo**
  - Validate account ownership and tenant membership before authorizing a transfer.
  - Define supported currency and integer range.
  - Treat overflow as failure, never as a wrapped balance.
  - Use fixed-precision database numeric types where the supported range exceeds integer storage.
  - Define deterministic lock ordering for bidirectional transfers to reduce deadlocks.
  - Audit changes without recording secrets.

<a id="failures"></a>
## 6. Failure review

- These are canonical failure patterns, not claims about specific production incidents.

| Failure | Trigger | Blast radius | Detection signal | Mitigation |
| --- | --- | --- | --- | --- |
| Duplicate debit | Retry uses a fresh ID or dedup is outside the write transaction | Customer balance | Multiple effects for one logical request | Scoped unique ID and one atomic transaction |
| Cross-tenant cache disclosure | Proxy cache omits tenant or authorization scope | Tenant data | Access audit mismatch | Authorize before access and use complete cache keys |
| Stale state transition | Two workers read the same order version | Order lifecycle | Conditional update affects zero rows | Compare-and-set update and explicit conflict handling |
| Missing notification | Process dies after commit and before direct callback | Downstream state | Database row with no corresponding event | Transactional outbox and relay monitoring |
| Duplicate notification | Relay dies after publish but before marking delivered | Consumer side effects | Repeated event ID | Idempotent consumer transaction |
| Partial facade action | Later subsystem fails after an earlier external effect | Business workflow | Partially completed operation | Durable orchestration and compensations with recovery |
| Shared copy corruption | Prototype shares a nested mutable object unintentionally | All copies | Editing one copy changes another | Explicit ownership and copy contract |
| Shared singleton corruption | Request-specific state is stored globally | Concurrent requests | Cross-request values | Immutable configuration or request-scoped state |
| Pool exhaustion | Iterator or factory-created resource is never closed | Service availability | Active connections approach pool limit | Explicit ownership and structured cleanup |
| Retry storm | Every decorator and client layer retries | Dependencies | Attempts far exceed incoming requests | One retry owner and a shared time budget |
| Visitor races | One mutable visitor serves concurrent traversals | Computed results | Nondeterministic accumulation | Per-traversal state or immutable visitors |
| Unbounded flyweight registry | User-controlled keys never expire | Process memory | Increasing key cardinality and heap | Bounded retention and realistic key policy |

<a id="interview"></a>
## 7. Interview questions and further thinking

### 7.1 When is a factory just unnecessary indirection?

**L4 answer**

- When construction has no meaningful variation, a direct constructor is clearer.
- Introduce a factory when creation policy or lifecycle needs an independent owner.

**L5 answer**

- Define the variation boundary before choosing a factory shape.
- A factory that reads arbitrary global configuration can hide more dependencies than it removes.
- Keep family selection at a composition boundary and expose resource ownership in the contract.

### 7.2 Can the same wrapper be both a proxy and a decorator?

**L4 answer**

- Yes.
- Access control expresses proxy intent.
- Added metrics express decorator intent.

**L5 answer**

- Identify the order-sensitive behavior rather than debating the label.
- Placing a cache outside authorization can change the security contract.
- Placing metrics inside retries measures attempts rather than requests.

### 7.3 Why is a singleton connection usually a bad database design?

**L4 answer**

- Concurrent requests would share transaction state on one connection.
- Use an application-scoped pool and borrow a connection for a unit of work.

**L5 answer**

- Define acquisition deadlines, pool saturation behavior, and transaction duration limits.
- More connections can increase database contention rather than increase useful throughput.
- Pool lifecycle and transaction lifecycle are separate responsibilities.

### 7.4 What distinguishes State from Strategy in an order service?

**L4 answer**

- State determines valid behavior from the order's lifecycle.
- Strategy selects an interchangeable algorithm such as pricing.

**L5 answer**

- Persist lifecycle transitions using a concurrency guard.
- Snapshot algorithm versions when a replay must preserve the original business meaning.
- A strategy swap during a retry must not silently alter an accepted operation.

### 7.5 Does Command plus undo provide ACID?

**L4 answer**

- No.
- Command packages a request.
- Undo attempts to reverse an action and may not be possible.
- ACID depends on a transactional storage mechanism and correctly expressed invariants.

**L5 answer**

- Compensation can race with subsequent actions and can itself fail.
- Durable compensating workflows need progress state, idempotent steps, and reconciliation.
- A local database rollback is a different mechanism with a different boundary.

### 7.6 Why does an Observer not guarantee a committed event?

**L4 answer**

- A callback may run before a transaction that later rolls back.
- A process may crash before a post-commit callback executes.

**L5 answer**

- Commit event intent with the business write in an outbox.
- Relay asynchronously and tolerate duplicate delivery.
- Couple consumer deduplication with its local effect rather than claiming end-to-end exactly-once delivery.

### 7.7 When is Visitor the wrong extension mechanism?

**L4 answer**

- When element types change frequently, because every visitor must accommodate each new type.
- Prefer methods on the elements when operations are stable.

**L5 answer**

- Account for deployment boundaries and schema versioning.
- Independent plugins may need an open dispatch registry or versioned protocol rather than a closed visitor interface.
- Unknown element behavior should fail explicitly or degrade according to a documented compatibility policy.

### 7.8 What should a production iterator promise?

**L4 answer**

- Traversal order.
- Behavior under mutation.
- End-of-data semantics.
- Resource ownership and closing requirements.

**L5 answer**

- For remote pagination, define snapshot consistency and cursor expiry.
- Bind cursors to tenant and query identity.
- Resume after partial failure without assuming that page numbers define a stable dataset.

### 7.9 L5-only: the database committed, but the client saw a timeout

- Treat the outcome as ambiguous, not as a proven rollback.
- Use the original request ID to query or retry the operation.
- If the stored result exists and payload matches, return that result.
- If no committed result exists, retry through the same atomic deduplication path.
- Bound recovery time and provide a status endpoint when immediate resolution is impossible.
- Keep deduplication records long enough to cover the API's supported retry horizon.

### 7.10 L5-only: two independent systems must change together

- First identify whether one transaction manager can actually enlist both resources.
- If not, choose an explicit distributed workflow with recoverable intermediate states.
- Use an outbox for durable message intent.
- Make remote steps idempotent with a shared operation identifier.
- Persist compensation progress when reversal is a business requirement.
- Explain which temporary inconsistency is acceptable and how it is reconciled.
- A facade can expose the workflow, but its method boundary does not turn it into a distributed ACID transaction.

### 7.11 Further practice

- Extend the command example with a durable command ID and versioned payload.
- Extend the state example with two competing workers and an optimistic version check.
- Extend the SQL example with a real outbox relay and a consumer deduplication table.
- Add a duplicate-request race test against a file-backed database using independent connections.
- Decide which failures are retryable before adding a retry decorator.
- Practice removing a pattern when a direct function makes the same invariant clearer.

<a id="references"></a>
## 8. References

- [GoF catalog and classic ordering — Addison-Wesley / InformIT](https://www.informit.com/store/design-patterns-elements-of-reusable-object-oriented-9780321770462)
  - Source for catalog membership and organization.
  - This guide's code is an original set of teaching examples, not a transcription of the book.
- [Java 17 JDBC Connection](https://docs.oracle.com/en/java/javase/17/docs/api/java.sql/java/sql/Connection.html)
  - Auto-commit and explicit commit/rollback contracts.
- [Python sqlite3 documentation](https://docs.python.org/3/library/sqlite3.html)
  - Explicit SQL transaction control and connection lifecycle.
- [PostgreSQL 16 transaction isolation](https://www.postgresql.org/docs/16/transaction-iso.html)
  - Isolation behavior and retrying serialization failures.
- [Spring Framework proxying mechanisms](https://docs.spring.io/spring-framework/reference/core/aop/proxying.html)
  - Proxy boundaries and self-invocation.
- [AWS transactional outbox pattern](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)
  - Atomic message intent and duplicate-delivery considerations.
- [H2 database documentation](https://h2database.com/html/main.html)
  - Runtime database for the JDBC demonstration.
- [SQLite transaction documentation](https://www.sqlite.org/lang_transaction.html)
  - Single-writer behavior and the meaning of `BEGIN IMMEDIATE`.
