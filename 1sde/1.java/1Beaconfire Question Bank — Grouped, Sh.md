# Beaconfire Question Bank — Grouped, Short L4 / L5 Answers

- Source: Beaconfire prep list (Java Core · Java 8 · Design Patterns · JDBC/Hibernate/DB · Spring · Microservices)
- Format: **L4** = correct, bounded · **L5** = mechanism / tradeoff / what breaks
- Overlap with the Randstad bank (`interview_qa_bank.md`) is cross-referenced as `→ see R §x.y` — short recap here, full depth there
- Bullets: `-` claim · `→` mechanism · `◆` edge case

## INDEX

1. Java Core — OOP & Language
2. Java Core — Collections & Strings
3. Java Core — Exceptions
4. Java Core — Concurrency
5. Java Core — Serialization, Memory, JVM
6. Java 8
7. Design Patterns
8. JDBC & Hibernate
9. Database & SQL
10. Spring Core
11. Spring MVC / REST
12. Spring Security, AOP, Testing, Config
13. Microservices & Messaging
14. Cloud, Kafka, Distributed

---

## 1. Java Core — OOP & Language

### 1.1 SOLID

**L4**

- S — one reason to change per class
- O — open for extension, closed for modification (strategy/polymorphism over `if` chains)
- L — subtypes must be substitutable without breaking callers
- I — many small interfaces > one fat one
- D — depend on abstractions; high-level modules don't import low-level ones

**L5**

- D is what makes hexagonal architecture work: domain defines the port, adapters implement it → domain has zero framework imports
- L violations show up as `instanceof` checks and overridden methods that throw `UnsupportedOperationException`
- 🗣 "SOLID is a checklist for _where change will hurt_, not a style guide"

### 1.2 OOP — inheritance, encapsulation, polymorphism, abstraction

**L4**

- Inheritance — IS-A; reuse + substitutability (`Bond extends Instrument`)
- Encapsulation — private state, controlled access via methods; invariants protected
- Polymorphism — runtime (override, dispatched on actual type) vs compile-time (overload, resolved on declared types)
- Abstraction — expose _what_, hide _how_: interfaces / abstract classes

**L5**

- Prefer composition over inheritance: inheritance couples to parent internals (fragile base class); composition + interfaces stays swappable
- Encapsulation's real test: can you change the representation without touching callers? — getters/setters for every field is _not_ encapsulation
- Records are the modern encapsulation shape for data; sealed hierarchies for closed polymorphism → see R §1.1–1.3

### 1.3 IS-A vs HAS-A

**L4**

- IS-A → inheritance / interface implementation (`Car extends Vehicle`)
- HAS-A → composition / aggregation (`Car` has an `Engine` field)

**L5**

- Default to HAS-A; use IS-A only when the subtype is substitutable _everywhere_ the parent is used (Liskov)
- Composition lets you change behavior at runtime (inject a different `Engine`); inheritance fixes it at compile time

### 1.4 Overriding vs overloading

**L4**

- Overriding — same signature in subclass; resolved at runtime on the object's actual type
- Overloading — same name, different parameter lists; resolved at compile time on declared argument types

```java
class Shape { double area() { return 0; } }
class Circle extends Shape { @Override double area() { return Math.PI * r * r; } }  // override
double area(int r) {...}  double area(double r) {...}                                 // overload
```

**L5**

- Overloading traps: `null` argument ambiguity, boxing vs widening preference (widening wins over boxing over varargs)
- Overriding rules: covariant return allowed; can't narrow visibility; can't throw broader checked exceptions; `static` methods hide, not override
- `@Override` is a compile-time guard — always use it

### 1.5 Interface vs abstract class

**L4**
| | Interface | Abstract class |
|---|---|---|
| Purpose | contract / capability | partial implementation, shared state |
| Fields | `public static final` only | any |
| Methods | abstract, `default`, `static`, `private` (9+) | any |
| Constructor | none | yes (called via `super`) |
| Inheritance | multiple | single |

**L5**

- Choose interface for _what it can do_ (Comparable, Runnable); abstract class for _what it is_ with shared state/template method
- Java 8 `default` methods blurred the line — but interfaces still can't hold instance state, which is the durable difference
- Abstract class constructor exists to initialize shared state for subclasses — it can't be called directly (Vanguard asked this)

### 1.6 Diamond problem

**L4**

- Two interfaces provide the same `default` method → class inheriting both must override and pick: `A.super.m()` or `B.super.m()`
- Classes avoid it entirely via single inheritance

**L5**

- Resolution rules: class wins over interface; more-specific interface wins over less-specific; otherwise compile error forces explicit choice
- Design smell if it happens often — default methods are for backward-compatible evolution, not mixins

### 1.7 Pass by value or reference?

**L4**

- Always **pass by value** — for objects, the value is a copy of the reference
- So: you can mutate the object the reference points to; you cannot reassign the caller's variable

**L5**

- 🗣 "Java passes references by value" — the swap-two-objects test proves it
- Immutable objects (String) make this moot; mutable params are a hidden-side-effect risk → defensive copies at boundaries

### 1.8 final / finally / finalize

**L4**

- `final` — variable can't be reassigned; method can't be overridden; class can't be extended
- `finally` — block that always runs after try/catch (cleanup)
- `finalize()` — GC hook before reclaim; deprecated (Java 9), unreliable

**L5**

- `finally` runs even on `return`; a `return` inside `finally` swallows exceptions — never do it
- Replace `finalize` with try-with-resources / `Cleaner`; finalizers delay GC by a full cycle and resurrect objects
- `final` on fields = safe publication under the JMM after construction — this is why immutable classes are thread-safe for free

### 1.9 Immutable class — how / why String is immutable

**L4**

- Recipe: `final` class · `private final` fields · no setters · all-args constructor · deep-copy mutable fields in and out
- Or: a `record` (with defensive copies in the compact constructor)
- String immutable because: string pool sharing safe · security (URLs, paths, class names can't change post-validation) · hashCode cached · thread-safe

**L5**

- Immutability = thread-safety without locks + safe as HashMap keys (hash never changes)
- Defeater: shallow immutability — a `final List` field is still mutable through the reference → `List.copyOf`
- String's cached hash is why it's the ideal map key; the pool is why `==` sometimes "works" and then betrays you

### 1.10 `==` vs `equals()` / access modifiers (default vs protected)

**L4**

- `==` — reference identity (same object); for primitives, value
- `equals()` — logical equality, per the class's override; must be consistent with `hashCode()`
- `default` (package-private) — same package only · `protected` — same package + subclasses anywhere

**L5**

- Break the `equals/hashCode` contract → objects vanish from HashSet/HashMap
- `Integer` cache (-128..127) makes `==` on boxed values pass in tests and fail in prod — classic
- `protected` leaks into subclasses across packages — it's wider than package-private, not narrower (common confusion)

---

## 2. Java Core — Collections & Strings

### 2.1 Array vs ArrayList / ArrayList vs LinkedList

**L4**

- Array: fixed size, primitives or objects, no API; ArrayList: dynamic, objects only (boxing), rich API
- ArrayList vs LinkedList → see R §1.8 — ArrayList wins on locality; LinkedList ~never

**L5**

- ArrayList grows 1.5× on capacity hit → presize with `new ArrayList<>(n)` for known sizes
- Arrays are covariant (`Integer[]` is an `Object[]`) → runtime `ArrayStoreException`; generics are invariant → compile-time safety

### 2.2 String vs StringBuilder vs StringBuffer

**L4**

- String immutable; Builder/Buffer mutable
- StringBuilder — single-thread, faster; StringBuffer — synchronized methods

**L5**

- StringBuffer is effectively legacy: method-level sync doesn't make compound operations atomic, so it rarely buys real safety
- Since Java 9 the compiler uses `invokedynamic` for `+` concatenation — loop concatenation is still O(n²); use a builder in loops

### 2.3 HashMap / HashSet internals

**L4**

- HashMap → see R §1.7: bucket array, `hashCode()` → index, `equals()` disambiguates, list → tree at 8, resize at 0.75
- HashSet = HashMap with elements as keys and a dummy value

**L5**

- Iteration order is undefined and changes on resize — code depending on it breaks silently; `LinkedHashMap` for insertion order, `TreeMap` for sorted
- Mutating a key after insertion strands the entry — why keys should be immutable

### 2.4 HashMap vs SynchronizedMap vs ConcurrentHashMap

**L4**

- HashMap — not thread-safe
- `Collections.synchronizedMap` — one lock on the whole map; iteration still needs external sync
- ConcurrentHashMap — per-bin locking, lock-free reads; no nulls

**L5**

- SynchronizedMap serializes _everything_ → readers block readers; CHM reads never block
- Both are "thread-safe map, not thread-safe logic" — use `compute`/`merge`/`putIfAbsent` for atomic compound ops
- CHM iterators are weakly consistent (no `ConcurrentModificationException`, may miss concurrent updates)

### 2.5 List vs Set vs Map vs Queue

**L4**

- List — ordered, duplicates, index access
- Set — unique elements (Hash/LinkedHash/Tree variants)
- Map — key→value, unique keys (not a `Collection`)
- Queue — FIFO (`ArrayDeque`, `LinkedList`, `PriorityQueue` for ordering by priority)

**L5**

- Pick by the _invariant_ you need enforced (uniqueness, order, priority) — the collection type is documentation
- `ArrayDeque` beats `LinkedList` for queue/stack; `PriorityQueue` is a binary heap — O(log n) offer/poll, not sorted iteration

---

## 3. Java Core — Exceptions

### 3.1 Types / handling / propagation / custom exceptions

**L4**

- Checked (compile-time, `extends Exception`) vs unchecked (`RuntimeException`) vs `Error` → see R §1.10
- Handling: `try/catch/finally`, `throws` to propagate, `throw` to raise
- Propagation: uncaught → walks up the call stack; checked must be declared at each level, unchecked propagate freely
- Custom: `extends Exception` (checked) or `extends RuntimeException` (unchecked); carry context fields (ids, code)

**L5**

- Catch low, wrap with context, rethrow, handle once at the edge — never catch-log-rethrow at every layer
- Custom exception hierarchy should encode _retryable vs terminal_ — that's what resilience policies key on
- Try-with-resources + suppressed exceptions replaced most `finally` cleanup

### 3.2 Exception handling in a web app

**L4**

- Centralized: `@RestControllerAdvice` + `@ExceptionHandler` → map domain exceptions to HTTP status + consistent error body
- Never leak stack traces to clients; log with correlation id server-side

**L5**

- Map by _category_: validation → 400, not-found → 404, conflict → 409, unexpected → 500 with generic message
- Use RFC 7807 Problem Details (Spring 6 `ProblemDetail`) as the error contract — clients get a stable shape
- Handler ordering matters: specific exception handlers before the catch-all `Exception` handler

---

## 4. Java Core — Concurrency

### 4.1 Creating threads / Runnable vs Callable / ExecutorService advantage

**L4**

- Create: extend `Thread` · implement `Runnable` · submit to `ExecutorService` (preferred)
- Runnable: `void run()`, no checked exceptions · Callable: `V call() throws Exception`, returns a `Future`
- Executor: thread pool reuse, bounded concurrency, task queue, lifecycle management, futures

**L5**

- Raw `new Thread()` = unbounded resource use, no backpressure, no observability — never in a service
- Pool sizing: CPU-bound ≈ cores; I/O-bound ≈ cores × (1 + wait/compute) — or virtual threads (21) and stop pooling threads entirely → see R §1.4
- Always name pool threads and set a rejection policy — the default `AbortPolicy` under saturation is your load-shedding decision, made for you

### 4.2 wait/notify in Object, join, sleep vs wait, thread lifecycle

**L4**

- `wait/notify` live on `Object` because every object has a monitor — you wait _on the lock_, not on a thread
- `join()` — caller blocks until that thread finishes
- `sleep` (Thread, keeps lock, fixed time) vs `wait` (Object, releases lock, until notified)
- Lifecycle: NEW → RUNNABLE → BLOCKED / WAITING / TIMED_WAITING → TERMINATED

**L5**

- `wait` must be in a loop checking the condition (spurious wakeups); `notifyAll` over `notify` unless you can prove one waiter suffices
- Modern code uses `Condition`, `BlockingQueue`, `CompletableFuture` — hand-rolled wait/notify is a code-review flag
- RUNNABLE includes "running" and "ready" — the JVM doesn't distinguish

### 4.3 CountDownLatch / Semaphore / ReadWriteLock

**L4**

- CountDownLatch — one-shot gate: N `countDown()`s release all `await()`ers (wait for N tasks to finish)
- Semaphore — N permits; bounds concurrent access to a resource (connection limiter)
- ReadWriteLock — many readers or one writer; for read-heavy shared state

**L5**

- Latch can't reset → `CyclicBarrier`/`Phaser` for reusable phases
- Semaphore is the correct throttle for virtual threads hitting a bounded downstream
- ReadWriteLock can starve writers; `StampedLock` optimistic reads are faster when writes are rare — but not reentrant

### 4.4 Future vs CompletableFuture

**L4**

- Future — blocking `get()`, no chaining, no manual completion
- CompletableFuture (8) — non-blocking composition (`thenApply/thenCompose/thenCombine`), exception handling (`exceptionally/handle`), manual `complete()`, `allOf/anyOf`

**L5**

- Default executor is the common ForkJoinPool → blocking I/O inside `supplyAsync` starves it; pass your own executor
- `thenApply` vs `thenApplyAsync`: the former runs on whichever thread completed the stage — thread-hopping surprises
- Spring `@Async` returns CompletableFuture via AOP proxy — same self-invocation caveat as `@Transactional`

### 4.5 Deadlock / synchronization / synchronized block vs method

**L4**

- Deadlock: two threads each hold a lock the other needs → both wait forever
  → prevent: consistent lock ordering · `tryLock` with timeout · minimize lock scope · avoid nested locks
- `synchronized` — one thread in the monitor at a time; visibility guaranteed on exit/entry
- Block over method: narrower scope, choose the lock object (private final lock, not `this`)

**L5**

- Detect with thread dumps (`jstack`) — "Found one Java-level deadlock"; `ThreadMXBean.findDeadlockedThreads()` for monitoring
- Locking on `this` or a String literal exposes your lock to outsiders → private lock object
- `synchronized` pins virtual threads pre-JDK 24 → `ReentrantLock` where virtual threads matter

### 4.6 Marker interface

**L4**

- Interface with no members — tags a class for the JVM/framework: `Serializable`, `Cloneable`, `RandomAccess`
- Checked via `instanceof`

**L5**

- Annotations replaced most marker uses (`@FunctionalInterface` is metadata; `Serializable` predates annotations)
- Marker interfaces participate in the type system (can be a generic bound); annotations can't — that's the one remaining reason to choose one

---

## 5. Serialization, Memory, JVM

### 5.1 Serialization / transient / how-to

**L4**

- Serialization = object → byte stream (`ObjectOutputStream`); deserialization reverses it; class implements `Serializable`
- `transient` — field excluded (secrets, derived caches, non-serializable references); comes back as default value
- Declare `serialVersionUID` explicitly

**L5**

- Java native serialization is a security hole (gadget-chain RCE) — use JSON (Jackson) or protobuf at boundaries; Java 17 filters (`ObjectInputFilter`) if you must
- Deserialization bypasses constructors → invariants unenforced; `readObject`/`readResolve` to re-validate (and to guard singletons)
- Missing `serialVersionUID` → `InvalidClassException` on any recompile

### 5.2 Memory leak / detection

**L4**

- Objects no longer needed but still referenced → GC can't reclaim → heap grows → OOM
- Typical: static collections, unclosed resources, listeners never removed, ThreadLocals in pools, caches without eviction
- Detect: heap dump (`-XX:+HeapDumpOnOutOfMemoryError`) → Eclipse MAT / JProfiler dominator tree → see R §1.12

**L5**

- Signal: old-gen occupancy trending up after full GCs (leak) vs sawtooth (healthy)
- ThreadLocal in a thread pool is the enterprise classic — pooled threads outlive requests; always `remove()` in `finally`
- Bounded caches (Caffeine with size/TTL) over `HashMap` caches — the fix is a policy, not a bigger heap

### 5.3 Young / Old / Metaspace · JVM components

**L4**

- Young gen (Eden + 2 survivors): new objects, minor GC frequent + cheap → survivors promoted to Old
- Old gen: long-lived objects, major/full GC expensive
- PermGen (≤7) → Metaspace (8+): class metadata, native memory, grows dynamically
- JVM: class loader → runtime data areas (heap, stacks, Metaspace, PC, native stacks) → execution engine (interpreter, JIT, GC)

**L5**

- Generational hypothesis: most objects die young → allocation is a pointer bump, minor GC cost ∝ live objects not dead ones
- Premature promotion (survivor too small, allocation bursts) fills Old with short-lived garbage → tune `-XX:MaxTenuringThreshold` / survivor ratio
- Metaspace leaks = classloader leaks (redeploys, dynamic proxies) — bounded by `MaxMetaspaceSize` or it eats native memory

---

## 6. Java 8

### 6.1 Features / lambdas / functional interfaces

**L4**

- Lambdas, functional interfaces, Stream API, `Optional`, `default`/`static` interface methods, `java.time`, `CompletableFuture`
- Lambda = anonymous function implementing a functional interface's single abstract method
- `@FunctionalInterface` optional; compiler error if the interface has ≠1 abstract method

```java
@FunctionalInterface interface Validator<T> { boolean isValid(T t); }
Validator<String> notBlank = s -> s != null && !s.isBlank();
```

**L5**

- Lambdas compile to `invokedynamic` + private synthetic methods — no anonymous-class files; capture only effectively-final locals
- `this` inside a lambda is the enclosing instance (anonymous class: itself) — matters for callbacks
- Built-ins to name: `Function`, `Supplier`, `Consumer`, `Predicate`, `BiFunction`, `UnaryOperator`

### 6.2 Comparator vs Comparable

**L4**

- Comparable — `compareTo(T)`, the class's _natural_ order, one per class
- Comparator — `compare(a, b)`, external custom order, many per class
- `Comparator.comparing(Emp::salary).thenComparing(Emp::name).reversed()`

**L5**

- Must be consistent with `equals` for `TreeSet`/`TreeMap` — elements comparing 0 are treated as duplicates
- `Comparator.comparingInt` avoids boxing; `nullsFirst/nullsLast` for null-safe sorts
- Never implement `compareTo` via subtraction on ints — overflow

### 6.3 Stream API / intermediate vs terminal / stream vs collection / parallel / flatMap

**L4**

- Stream = lazy pipeline over a source; doesn't store or mutate data; single-use
- Intermediate (lazy, return Stream): `map`, `filter`, `sorted`, `flatMap`, `distinct`, `limit`
- Terminal (eager, trigger execution): `collect`, `reduce`, `forEach`, `findAny`, `count`, `anyMatch`
- `stream().sorted()` returns a new order; `Collections.sort` sorts in place
- Parallel: `parallelStream()` / `.parallel()` → common ForkJoinPool → see R §1.5
- `flatMap` — one-to-many then flatten: `List<List<T>>` → `Stream<T>`

**L5**

- Fusion: intermediates run per-element in one pass; `findFirst` short-circuits — ordering of ops matters for cost (filter before map)
- `sorted`/`distinct` are stateful barriers — they buffer everything and kill laziness
- Side effects in streams break under parallel; `forEach` on parallel streams has no order — use `forEachOrdered` or collect

### 6.4 default / static methods · Optional

**L4**

- `default` — concrete method in an interface; added so `Collection` could gain `stream()` without breaking implementations
- `static` interface methods — utility on the interface, not inherited
- `Optional` — container that may be empty; forces null handling: `map/flatMap/orElse/orElseThrow/ifPresent`

**L5**

- `Optional` is for return types only — not fields, not parameters, not collections (`Optional<List>` is a smell)
- `orElse(expensive())` evaluates eagerly; use `orElseGet`
- `Optional.get()` without `isPresent` is just NPE with extra steps → prefer `orElseThrow`

---

## 7. Design Patterns

### 7.1 Patterns you've used

**L4**

- Creational: Builder (request DTOs, Lombok `@Builder`), Factory (instrument-type handlers), Singleton (Spring beans)
- Structural: Proxy (Spring AOP, `@Transactional`), Adapter (hexagonal ports), Facade (gateway)
- Behavioral: Strategy (comparison agents by instrument type), Observer (events/listeners), Chain of Responsibility (filters, validators), Template Method (batch steps)
- Distributed: Circuit Breaker, API Gateway, Saga, Outbox

**L5**

- Name the _problem_ each solved, not the pattern: "Strategy replaced a 200-line switch on instrument type that changed every sprint"
- Spring _is_ the pattern catalog: IoC = DI, `@Transactional` = Proxy, `ApplicationEvent` = Observer, `JdbcTemplate` = Template Method, filter chain = Chain of Responsibility

### 7.2 Singleton — eager / lazy / thread-safe / double-checked / reflection-serialization-cloning

**L4**

```java
public final class Config {
    private static volatile Config instance;          // volatile is required
    private Config() {}
    public static Config get() {
        if (instance == null) {                       // 1st check: skip lock on fast path
            synchronized (Config.class) {
                if (instance == null) instance = new Config();  // 2nd check: another thread may have won
            }
        }
        return instance;
    }
}
```

- Eager: `private static final Config INSTANCE = new Config();` — thread-safe via class loading
- Why double check: first check avoids locking after init; second check prevents two threads both passing the first check and creating two instances

**L5**

- Without `volatile`, instruction reordering can publish a partially constructed object → other thread sees non-null, uninitialized fields (JMM)
- Best lazy form: holder idiom (`static class Holder { static final Config I = new Config(); }`) or an `enum` — no volatile, no locks
- Defenses: reflection → throw in constructor if instance exists (enum is immune); serialization → `readResolve()` returns the instance (enum immune); cloning → override `clone()` to throw
- Spring singletons are per-container scope, not JVM — different concept

### 7.3 Factory / Abstract Factory / Builder (with code)

**L4**

```java
interface Parser { Record parse(String raw); }
class ParserFactory {
    static Parser forType(InstrumentType t) {
        return switch (t) { case BOND -> new BondParser(); case EQUITY -> new EquityParser(); };
    }
}
```

- Factory: one method creates one product family member; decouples callers from concrete classes
- Abstract Factory: an interface producing _families_ of related objects (e.g. `UiFactory` → Button + Checkbox for a theme)
- Builder: step-wise construction of complex objects, avoids telescoping constructors

```java
Order o = Order.builder().id("o1").amount(new BigDecimal("10.50")).currency("USD").build();
```

**L5**

- In Spring the factory is usually a `Map<InstrumentType, Parser>` injected from all beans — open-closed without touching a switch
- Builder's real value: enforce invariants in `build()` (validate required fields) and produce an immutable result
- Abstract Factory earns its weight only with ≥2 product families that must stay consistent — otherwise plain Factory

### 7.4 API Gateway / Circuit Breaker / Proxy / Observer / Chain of Responsibility

**L4**

- Gateway — reverse proxy + single entry: routing, auth, rate limit, aggregation → see R §6.9
- Circuit Breaker — closed → open on failure rate → half-open probe → closed; fail fast, protect the caller → see R §2.10
- Proxy — same interface, wraps the real object to add behavior (lazy load, access control, transactions — Spring AOP)
- Observer — subject notifies registered listeners on state change (`ApplicationEventPublisher`, Kafka consumers conceptually)
- Chain of Responsibility — request passes handlers until one handles it (servlet filters, Spring Security filter chain, validation chains)

**L5**

- Proxy in Spring: JDK dynamic proxies need an interface; CGLIB subclasses — why `final` methods and self-invocation escape `@Transactional`
- Observer in-process couples timing (sync listeners block the publisher) — `@TransactionalEventListener(AFTER_COMMIT)` for anything with side effects
- Chain of Responsibility failure mode: nobody handles → define the terminal handler explicitly

---

## 8. JDBC & Hibernate

### 8.1 SQL injection / Statement vs PreparedStatement / statement types / JdbcTemplate / manual TX

**L4**

- Injection: user input concatenated into SQL → attacker alters the query. Fix: parameterized queries (`PreparedStatement`, JPA params) — sanitization is secondary
- Statement (static SQL) · PreparedStatement (precompiled, parameterized, reusable, injection-safe) · CallableStatement (stored procedures)
- JdbcTemplate: removes connection/statement/resultset boilerplate, translates `SQLException` → `DataAccessException` hierarchy, RowMapper
- Manual TX: `conn.setAutoCommit(false)` → statements → `commit()` / `rollback()` in catch → restore autocommit in `finally`

**L5**

- PreparedStatement sends parameters separately from SQL text → data can never be parsed as code — that's _why_ it's injection-proof; also plan caching
- Injection still possible via dynamic table/column names — whitelist those, params can't cover identifiers
- Prefer `@Transactional`/`TransactionTemplate` over manual — manual TX code is where leaked connections come from

### 8.2 ORM / Hibernate / configuration / dialect vs driver

**L4**

- ORM maps tables ↔ objects; reduces boilerplate; DB-independent via HQL/JPQL
- Hibernate adds: entity state management, caching, lazy loading, connection management
- Config: datasource (url/driver/user/pass) + `dialect` + `hbm2ddl`/`ddl-auto` + entity scanning
- MySQL → Oracle: change the **dialect** (plus url/driver/creds)
- Driver: how to _connect_ to the DB; dialect: how to _translate_ HQL into that DB's SQL flavor (paging, functions, types)

**L5**

- Hibernate 6 auto-detects dialect from JDBC metadata — the question is a legacy-config fluency check; still know the answer
- "Hot-swap database" is theoretical: native queries, sequences, and type differences leak through — plan a migration, don't assume
- `ddl-auto=update` in prod is a data-loss risk → Liquibase/Flyway own DDL

### 8.3 Session / SessionFactory / getCurrentSession vs openSession

**L4**

- SessionFactory: heavyweight, one per DB, thread-safe, built at startup
- Session: one unit of work + first-level cache, NOT thread-safe, short-lived
- `openSession()` — new session, you close it; `getCurrentSession()` — context-bound (thread/transaction), auto-closed on commit

**L5**

- In Spring/JPA you never touch these — `EntityManager` proxy bound to the transaction; the question tests if you know what the abstraction hides
- Sharing a Session across threads = corrupted persistence context; Session-per-request is the pattern

### 8.4 Entity states / get vs load / update-merge-saveOrUpdate / flush-clear-commit

**L4**

- Transient (new, unmanaged) → Persistent (attached to session, dirty-checked) → Detached (session closed) → Removed
- `get()` — hits DB immediately, returns null if absent; `load()` — returns a proxy, hits DB on access, throws if absent
- `update()` — reattach detached (fails if a copy is already managed); `merge()` — copies state onto managed instance, returns it; `saveOrUpdate()` — insert or update by id
- `flush()` — push pending SQL to DB; `clear()` — detach everything; `commit()` — flush + end TX

**L5**

- Dirty checking means _managed_ entity setters become UPDATEs at flush — no `save()` call needed; the source of "surprise UPDATE" bugs
- `merge` returns a _different_ instance — using the original afterward is the classic mistake
- Flush order: inserts → updates → deletes; `FlushMode.AUTO` flushes before queries that need consistent state

### 8.5 Mappings / fetching / LazyInitializationException

**L4**

```java
@Entity class Order { @ManyToOne(fetch = LAZY) @JoinColumn(name="customer_id") Customer customer; }
@Entity class Customer { @OneToMany(mappedBy = "customer") List<Order> orders; }
@ManyToMany @JoinTable(name="student_course", joinColumns=@JoinColumn(name="student_id"),
    inverseJoinColumns=@JoinColumn(name="course_id")) Set<Course> courses;
```

- Lazy (default for collections/`@ManyToOne` should be): load on access. Eager: load with parent
- LazyInitializationException: accessing a lazy association after the session closed
- Fix: access inside TX · `JOIN FETCH` / `@EntityGraph` · DTO projection · (eager as last resort)

**L5**

- `@ManyToOne` defaults to EAGER — set LAZY explicitly or every load cascades
- Open-Session-In-View "fixes" LIE by holding the session through the view — hides N+1 and pins connections; disable it (`spring.jpa.open-in-view=false`)
- `@ManyToMany` with a `List` + extra columns → promote to an entity with two `@ManyToOne` — you'll need the extra columns eventually

### 8.6 Hibernate vs JDBC / HQL vs Criteria / type safety / caching

**L4**

- Hibernate preferred: less boilerplate, object graph navigation, caching, DB portability; JDBC for bulk/set-based work → see R §2.12
- HQL — object-oriented query strings (entity/field names); Criteria API — programmatic, type-safe with JPA metamodel (`Order_.amount`) → compile-time checked, dynamic query building
- First-level cache: per Session, always on. Second-level: per SessionFactory, opt-in (Ehcache/Caffeine/Redis), per-entity config
- Lookup order: L1 → L2 → DB

**L5**

- L2 cache is dangerous with external writers (stale data) — only for read-mostly reference data with a TTL; query cache doubly so
- Criteria's dynamic building is its strength (search filters); HQL's readability is HQL's — many teams use Spring Data `Specification` for the former

---

## 9. Database & SQL

### 9.1 ACID / locking / CAP

**L4**

- Atomicity (all or nothing) · Consistency (valid state → valid state) · Isolation (concurrent TXs don't interfere, per level) · Durability (committed survives crash)
- Optimistic locking: no lock, `@Version` column checked at update → retry on conflict — read-heavy, low contention
- Pessimistic: `SELECT ... FOR UPDATE` — high contention, must not lose
- CAP: under partition, choose consistency (reject) or availability (serve stale). MongoDB: CP (primary-only writes; secondaries can't accept writes during partition)

**L5**

- Isolation is the negotiable letter: READ COMMITTED (Postgres/Oracle default) allows non-repeatable reads; MySQL InnoDB default is REPEATABLE READ
- Optimistic fails "late" (at commit) — fine for UI forms; pessimistic fails "early" — required for inventory decrements with money attached
- CAP is oversimplified; PACELC adds the latency/consistency trade under _no_ partition — that's the everyday one

### 9.2 Employee/Department SQL set

```sql
-- a. count per dept
SELECT department, COUNT(*) FROM employee GROUP BY department;
-- b. max salary per dept
SELECT department, MAX(salary) FROM employee GROUP BY department;
-- c. employees with top salary per dept
SELECT * FROM (SELECT *, DENSE_RANK() OVER (PARTITION BY department ORDER BY salary DESC) rk FROM employee) t WHERE rk = 1;
-- d. all employees with the 3rd highest salary (overall)
SELECT * FROM (SELECT *, DENSE_RANK() OVER (ORDER BY salary DESC) rk FROM employee) t WHERE rk = 3;
```

**L5**

- Use `DENSE_RANK` (ties share rank, no gaps) not `ROW_NUMBER` (arbitrary tiebreak drops co-top earners) — say why
- Non-window alternative for (c): join to the grouped max — `WHERE (department, salary) IN (SELECT department, MAX(salary) ... GROUP BY department)`
- Nth-highest with `LIMIT 1 OFFSET n-1` on `DISTINCT salary` — works, but breaks if fewer than n distinct salaries

### 9.3 SQL vs NoSQL / joins / CTE / stored proc & trigger

**L4**

- SQL vs NoSQL → see R §7.1: rigid vs flexible schema, vertical vs horizontal scale, ACID vs BASE; structured/relational → SQL, unstructured/known-pattern-at-scale → NoSQL
- INNER — matches both sides; LEFT — all left + matches; RIGHT — mirror; FULL — union of both
- CTE: `WITH t AS (SELECT ...) SELECT ... FROM t` — readable subqueries, reusable in one statement, `WITH RECURSIVE` for hierarchies
- Stored procedure (explicit call) vs trigger (fires on DML) → see R §7.6

**L5**

- CTEs in older Postgres (<12) were optimization fences (materialized) — could be _slower_ than subqueries; know your engine
- LEFT JOIN + `WHERE right.col IS NULL` = anti-join (find orphans) — the idiom interviewers like
- Triggers = hidden side effects; use for audit columns at most

### 9.4 Clustered vs non-clustered index / window functions / slow queries

**L4**

- Index = B+Tree. Clustered: table rows physically stored in key order, leaf = data, one per table (PK in MySQL InnoDB). Non-clustered: leaf holds pointers/PK values, many per table
- Window function: aggregate over a partition without collapsing rows — `SUM() OVER (PARTITION BY ...)`, `ROW_NUMBER`, `RANK` (gaps after ties: 1,1,3), `DENSE_RANK` (no gaps: 1,1,2)
- Slow query → see R §7.4: `EXPLAIN`, right index, no `SELECT *`, sargable predicates, keyset pagination

**L5**

- InnoDB secondary index lookups do two B+Tree walks (secondary → PK → row) — covering indexes avoid the second
- Postgres has no clustered index (heap + `CLUSTER` command as a one-off) — the question is MySQL/SQL Server framed
- Window frame defaults (`RANGE UNBOUNDED PRECEDING`) change running-total semantics with ties — specify `ROWS`

---

## 10. Spring Core

### 10.1 Spring vs Spring Boot / DI & IoC / how to inject / setter vs constructor / mandatory setter

**L4**

- Boot = Spring + auto-configuration + starters + embedded server + actuator
- DI: container builds objects and hands in dependencies → loose coupling, testability. IoC container: reads bean definitions → instantiates → resolves dependencies → manages lifecycle
- Inject: constructor (preferred), setter, field. Constructor for required/immutable; setter for optional
- Mandatory setter: `@Autowired(required = true)` on the setter (default) — or just use the constructor → see R §2.4

**L5**

- Constructor injection makes circular dependencies fail at startup (correct) where field injection hides them
- Field injection + `final` impossible → no safe publication guarantee

### 10.2 Bean creation / BeanFactory vs ApplicationContext / scopes / singleton thread safety

**L4**

- Create: stereotype annotations (`@Component` & co) via scan, or `@Bean` methods in `@Configuration`
- BeanFactory: lazy, basic container. ApplicationContext: extends it — eager singleton init, events, i18n, AOP, environment. Always use ApplicationContext
- Scopes: singleton (default, one per container) · prototype (new per injection/lookup) · request · session · application
- Singleton beans are thread-safe only if stateless — Spring guarantees nothing about your fields
- Define: `@Scope("prototype")`

**L5**

- Stateful singleton with a mutable field = shared mutable state under a thread pool → the most common Spring concurrency bug
- Prototype beans aren't destroyed by the container — `@PreDestroy` never runs; you own their lifecycle

### 10.3 Singleton ↔ prototype injection

**L4**

- Prototype B ← singleton A: fine — each new B gets the same A
- Singleton A ← prototype B: A is created once, so B is injected once → B behaves as singleton
- Fix: `@Lookup` method (Spring subclasses A and overrides it to fetch a fresh B), or `ObjectProvider<B>`, or scoped proxy (`proxyMode = TARGET_CLASS`)

**L5**

- Scoped proxy injects a CGLIB proxy that resolves the target per call — transparent but every method call does a lookup
- `ObjectProvider` is explicit and testable — prefer it over the `@Lookup` magic

### 10.4 @Autowired resolution / @Qualifier / @Primary / circular dependency

**L4**

- Resolution: by type → `@Qualifier` → `@Primary` → parameter name; ambiguous → `NoUniqueBeanDefinitionException` → see R §2.4–2.5
- Circular: A needs B, B needs A. Prevent: redesign (extract shared piece) · `@Lazy` on one side · setter injection (last resort)

**L5**

- Spring Boot 2.6+ _rejects_ circular references by default — the `@Lazy` workaround defers, it doesn't fix the design
- A cycle almost always means one class is doing two jobs — the extraction is the real answer

### 10.5 @SpringBootApplication / @Component vs @Repository vs @Service

**L4**

- `@SpringBootApplication` = `@Configuration` + `@EnableAutoConfiguration` + `@ComponentScan` → see R §2.1–2.2
- All three register beans; `@Repository` adds persistence exception translation (`SQLException`/`PersistenceException` → `DataAccessException`); `@Service`/`@Controller` are semantic (and `@Controller` enables MVC handler detection)

**L5**

- Exception translation happens via a `BeanPostProcessor` adding a proxy — a `@Repository` with `final` methods won't get it
- Stereotypes are the seams for AOP pointcuts (`within(@Service *)`) — semantics become mechanics

### 10.6 Transactions in Spring Boot

**L4**

- `@Transactional` on service methods; propagation/isolation/rollbackFor attributes; `PlatformTransactionManager` auto-configured → see R §2.6, §7.5

**L5**

- Proxy-only (self-invocation), checked exceptions commit by default, connection held for the method — the three bugs to name

---

## 11. Spring MVC / REST

### 11.1 Spring MVC / DispatcherServlet / ViewResolver / @Controller vs @RestController

**L4**

- Flow: request → `DispatcherServlet` (front controller) → `HandlerMapping` picks controller → `HandlerAdapter` invokes → returns ModelAndView or data → `ViewResolver` maps view name → view renders (or `HttpMessageConverter` writes JSON)
- ViewResolver: logical view name → actual template (Thymeleaf/JSP)
- `@RestController` = `@Controller` + `@ResponseBody` → returns data, not views

**L5**

- Every `@RequestMapping` method runs through interceptors → argument resolvers → converters → return handlers; custom `HandlerMethodArgumentResolver` is how you inject the current user cleanly
- Content negotiation picks the converter (Jackson) — knowing this explains most "406/415" errors

### 11.2 @RequestBody/@ResponseBody · @PathVariable/@RequestParam · RestTemplate · Spring Data pagination

**L4**

- `@RequestBody` — deserialize body → object; `@ResponseBody` — serialize return → body
- `@PathVariable` — `/users/{id}` (identity); `@RequestParam` — `?page=2` (filters/options)
- RestTemplate — blocking HTTP client, maintenance mode → RestClient/WebClient → see R §2.13
- Spring Data: `Pageable` param → `Page<T>` (with total count query) or `Slice<T>` (has-next only, cheaper)

**L5**

- `Page` runs a `COUNT(*)` per request — expensive on big tables; `Slice` or keyset pagination for feeds → see R §7.7
- Path variables are part of the resource identity and cacheable; query params are not — REST design choice, not just syntax

### 11.3 HTTP methods / POST vs PUT vs PATCH / SOAP vs REST / stateless / RESTful principles / versioning

**L4**

- GET (safe, idempotent) · POST (create/action, not idempotent) · PUT (full replace, idempotent) · PATCH (partial update) · DELETE (idempotent)
- SOAP: XML envelope, WSDL contract, WS-\* security/transactions, protocol-agnostic; REST: HTTP-native, JSON, lighter, cacheable
- REST is stateless by principle: each request self-contained (token, not server session)
- Principles: client-server · stateless · cacheable · uniform interface (resources, representations, HATEOAS) · layered
- Versioning: URI (`/v1/`), header (`Accept: application/vnd.x.v1+json`), or query param; URI is most common/visible

**L5**

- PUT idempotency is what lets clients retry safely; POST needs an idempotency key to get the same property → see R §2.9
- "Stateless" ≠ "no state" — state lives in the DB/token; the _server process_ holds none → horizontal scaling
- Version by breaking changes only; additive changes shouldn't bump — tolerant readers (ignore unknown fields) make most versioning unnecessary

### 11.4 Validation / BindingResult / staying logged in with REST

**L4**

- `@Valid @RequestBody Dto dto` + constraint annotations → `MethodArgumentNotValidException` → 400 via advice
- `BindingResult` right after the `@Valid` param captures errors instead of throwing — you inspect and respond manually
- Logged-in with stateless REST: JWT in `Authorization` header; refresh token for renewal → see R §9.2–9.4

**L5**

- `BindingResult` must be the _immediately following_ parameter or Spring throws before your method runs
- Validation groups (`@Validated(Create.class)`) for create-vs-update rules on one DTO

---

## 12. Spring Security, AOP, Testing, Config

### 12.1 Spring AOP

**L4**

- Cross-cutting concerns (logging, transactions, security, metrics) applied via proxies: aspect, advice (`@Before/@After/@Around`), pointcut, join point
- Spring uses runtime proxies (JDK interface / CGLIB subclass) — method-execution join points only

**L5**

- Self-invocation bypasses advice; `final` classes/methods can't be CGLIB-proxied; private methods never advised — the three AOP "doesn't work" causes
- `@Around` must call `proceed()` and return its result — forgetting it silently swallows the call

### 12.2 Spring Security / JWT workflow

**L4**

- Authentication (who) → authorization (what) → CSRF (cookie-session forgery protection) → see R §2.7
- JWT flow: login → validate credentials → issue signed JWT → client sends Bearer → filter validates signature/claims → `SecurityContext` → `@PreAuthorize` checks

**L5**

- Stateless JWT APIs: `SessionCreationPolicy.STATELESS` + CSRF disabled (irrelevant without cookies) — say why
- Short TTL + refresh rotation; revocation is a policy, not a feature → see R §9.4

### 12.3 Unit vs integration testing / Mockito annotations / doReturn vs thenReturn / coverage tools

**L4**

- Unit: one class, dependencies mocked — JUnit 5 + Mockito. Integration: real wiring — `@SpringBootTest`, Testcontainers, Cucumber
- `@Mock`, `@InjectMocks`, `@Spy`, `@Captor`, `@MockBean` (Spring context)
- `when(x.m()).thenReturn(v)` — calls the real method during stubbing (bad on spies / void). `doReturn(v).when(x).m()` — no call, works on spies and void methods
- Coverage: JaCoCo (Maven/Gradle report), IntelliJ coverage, SonarQube

**L5**

- Slice tests (`@WebMvcTest`, `@DataJpaTest`) sit between: fast, real Spring layer, rest mocked
- Coverage % is a floor; mutation testing (PIT) tells you if tests actually assert → see R §2.15

### 12.4 Environments / profiles / Jasypt

**L4**

- `@Profile("dev")` on beans/config; `spring.profiles.active` selects `application-{profile}.yml`
- Jasypt: property encryption — `ENC(...)` values decrypted at startup with a master key from env

**L5**

- Profiles for _behavior_ differences; env vars / SSM / Secrets Manager for _values_ — don't encode secrets in profile files at all → see R §11.5
- Jasypt is fine for legacy; cloud-native answer is a secrets manager with IAM-scoped access and rotation

---

## 13. Microservices & Messaging

### 13.1 Monolith vs microservices

**L4**

- Monolith: one deployable — simple ops, easy TX, fast local calls; scales as a whole, slow to change at team scale
- Microservices: independent deploy/scale/tech per service, team ownership; costs: distributed complexity, eventual consistency, ops overhead, network failures

**L5**

- Split when _team_ scaling or independent deploy cadence demands it — not for a small team. Modular monolith first → see R §8.4
- 🗣 "microservices trade code complexity for operational complexity — make sure you have the ops budget"

### 13.2 Cascading failure / fault tolerance

**L4**

- One slow/down service exhausts its callers' threads/connections → they fail → their callers fail
- Prevent: timeouts → retries with backoff+jitter → circuit breaker → bulkhead → rate limit → fallback (Resilience4j) → see R §2.10, §8.8

**L5**

- Slow is worse than down: a fast 500 sheds load, a 30s hang consumes it
- Retry storms are self-inflicted cascades — retry budgets

### 13.3 Communication / Swagger / monitoring / gateway

**L4**

- Sync: REST (RestClient/Feign), gRPC. Async: Kafka/RabbitMQ/SQS → see R §3.7, §8.1
- Swagger/OpenAPI: API contract + docs + client generation (`springdoc-openapi`)
- Monitor: logs → ELK/Splunk/CloudWatch Logs; metrics/health → Actuator + Micrometer → Datadog/Prometheus; traces → X-Ray/Datadog APM → see R §6.6
- Gateway: single entry, auth, rate limit, routing, logging. Necessary? Not for 2 services behind an ALB; yes once cross-cutting policy or aggregation matters → see R §6.9

**L5**

- Contract-first OpenAPI + generated clients = drift caught at build time
- Alert on SLO symptoms not resource causes

### 13.4 Environments / deployment / Jenkins / debugging

**L4**

- Environments: local → dev → QA/test → staging (prod-like) → prod; sometimes UAT/perf
- Deploy path: Git → Jenkins/GitHub Actions (build, test, scan) → image → registry (ECR/Docker Hub) → ECS/EKS (or Spinnaker) → see R §11.1
- Jenkins: pipeline-as-code (`Jenkinsfile`), stages, agents, credentials, triggers
- Debug: gather (what changed, which requests) → logs with correlation id → traces/metrics → reproduce → fix → guardrail → see R §8.9

**L5**

- Same immutable artifact through every environment; only config changes
- Staging that isn't prod-like is theater — data shape and volume parity is the expensive but real part

### 13.5 Async in web apps

**L4**

- In-process: `@Async` + executor, `CompletableFuture`, `@Scheduled`
- Cross-service: message broker (Kafka/RabbitMQ/SQS) — producer returns immediately, consumer processes later
- Client-facing: return 202 Accepted + status endpoint / callback / websocket

**L5**

- `@Async` work dies with the pod — anything that must complete goes on a durable queue
- Async without a DLQ, idempotency, and a status model is fire-and-forget-and-lose

### 13.6 RabbitMQ — what / components / exchange types / DLX

**L4**

- AMQP broker: async communication, decoupling, buffering, work distribution
- Components: producer → exchange → (binding, routing key) → queue → consumer; vhost; connection/channel
- Exchange types: direct (exact routing key) · fanout (broadcast to all bound queues) · topic (pattern `order.*`, `#`) · headers (match on headers)
- DLX: exchange that receives messages rejected/nacked without requeue, expired (TTL), or overflowed → dead-letter queue for inspection/retry → see R §3.10

**L5**

- Exchange _is_ the routing layer — vs Kafka where routing is producer-side partitioning; Rabbit = smart broker/dumb consumer, Kafka = dumb broker/smart consumer
- Prefetch (`basic.qos`) is the consumer backpressure knob; unbounded prefetch = OOM on the consumer
- Quorum queues over classic mirrored for HA (Raft-based); classic mirrored is deprecated

### 13.7 Secure endpoints / config storage / authorization / scaling

**L4**

- Secure: HTTPS · JWT bearer + RBAC (Spring Security) · `@Valid` payloads · rate limiting · gateway enforcement → see R §9.1
- Config: Spring Cloud Config Server (Git-backed) or AWS SSM/Secrets Manager/AppConfig; env-injected, never in the image
- Authorization: gateway validates JWT → forwards claims → services enforce roles/ownership per resource
- Scaling: horizontal (stateless + LB + autoscale) default; vertical for DBs → see R §8.8

**L5**

- Object-level authorization (is this _your_ order?) is the check that survives gateway-only auth — and the one usually missing
- Config server is a runtime dependency — cache/fallback or a config outage becomes a startup outage

---

## 14. Cloud, Kafka, Distributed

### 14.1 Cloud experience (IAM / RDS / S3)

**L4**

- IAM: roles for services, least-privilege policies → see R §6.7
- RDS/Aurora: managed relational; Multi-AZ failover; read replicas; RDS Proxy for connection pooling → see R §5.1
- S3: object storage, events, lifecycle, presigned URLs → see R §6.1

**L5**

- Role assumption + STS = no static keys; the ECS task role is the unit of trust
- RDS failover is DNS-based — client-side connection validation/timeouts decide how long the blip lasts

### 14.2 Kafka — what / components / partitions / multiple consumers per partition / Kafka Streams

**L4**

- Distributed log → see R §3.1. Components: producer · broker · topic · partition · consumer group · offset · replication (leader/ISR) · KRaft controller (ZooKeeper removed in 4.0)
- Partition = unit of parallelism + ordering scope; key → partition
- Multiple consumers on one partition: within a _group_, no — one consumer per partition (extras idle); across _different_ groups, yes — each group reads independently
- Kafka Streams: client library for stream processing (map/filter/join/aggregate, windowing, state stores) directly on topics — no cluster to run

**L5**

- Partition count is the consumer-scaling ceiling and a one-way door for ordered keys → see R §3.2–3.3
- Streams exactly-once via transactions — but only Kafka→Kafka; external sinks are still your idempotency problem
- Consumer group protocol handles rebalancing; cooperative-sticky assignor avoids stop-the-world

### 14.3 ELK / event-driven / 2PC vs SAGA / microservice components

**L4**

- ELK: Elasticsearch (index/search) + Logstash (ingest/transform, or Filebeat) + Kibana (dashboards) — centralized logs
- Event-driven: services emit facts; others react asynchronously — Kafka/RabbitMQ; loose coupling, replay, eventual consistency
- 2PC: coordinator prepares all → commits all; blocking, coordinator SPOF, availability coupling — avoided across services
- Saga: local TXs + compensations, choreography or orchestration → see R §8.2
- Components: client → API gateway → LB → auth server → services (+ service discovery, config server) → message broker → per-service DB → observability stack

**L5**

- Outbox pattern bridges "write DB + publish event" atomically — the missing piece in most event-driven answers
- Service discovery is built into ECS/K8s (DNS) — Eureka is a pre-container-era answer; say which you'd use and why
- Sagas give up isolation: model pending states explicitly; compensations are semantic undos

---

_End · Full-depth versions of cross-referenced items live in `interview_qa_bank.md` (R §x.y)._
