# Antra Mock Interview — Answer Sheet

Terse recall format. 2–4 lines per question, screen-ready. Java 17/21 baseline.
Skipped per your call: Git/GitHub, CICD.

---

# JAVA (53)

**1. Interface vs abstract class**
Interface: no state (only `public static final` constants), multiple inheritance, `default`/`static`/`private` methods since Java 8. Abstract class: can hold instance fields and constructors, single inheritance, any access modifier.
Rule: interface = capability/contract, abstract class = shared partial implementation + state.

**2. HashMap vs ConcurrentHashMap**
`HashMap` unsynchronized, allows one null key + null values. `CHM` thread-safe, rejects nulls, per-bin `synchronized` on writes, lock-free reads.
`CHM` iterators are weakly consistent (never CME); `HashMap` is fail-fast. `CHM.size()` is approximate.

**3. Array vs ArrayList**
Array: fixed length, holds primitives or objects, covariant, `.length`. `ArrayList`: resizable (1.5× growth + `Arrays.copyOf`), objects only (boxing), invariant, `.size()`.
Array is faster/smaller; `ArrayList` gives you the Collection API.

**4. ArrayList vs LinkedList**
`ArrayList`: contiguous array, O(1) index, cache-friendly, ~4–8 bytes/element. `LinkedList`: doubly-linked nodes, O(n) index, ~40 bytes/node.
Default to `ArrayList` always. For queue/stack semantics use `ArrayDeque`, not `LinkedList`.

**5. Set vs Map**
`Set` = unique elements, `Map` = unique key → value pairs. `Map` is not a `Collection` (`add(E)` is meaningless for a pair).
`HashSet` is literally a `HashMap` with a shared dummy `PRESENT` value.

**6. `==` vs `equals()`**
`==` compares references for objects, values for primitives. `equals()` is logical equality, `Object`'s default is `==` until overridden.
Trap: `Integer` caches −128..127, so `==` "works" on small boxed ints and silently fails at 128.

**7. String vs StringBuilder vs StringBuffer**
`String` immutable, interned in the string pool, concatenation creates new objects. `StringBuilder` mutable, not synchronized — the default. `StringBuffer` mutable, synchronized, legacy.
Concatenation in a loop → use `StringBuilder`; a single `a + b` is compiled to it anyway.

**8. Runnable vs Callable**
`Runnable.run()` returns `void` and cannot throw checked exceptions. `Callable<V>.call()` returns `V` and can throw checked.
`ExecutorService.submit(Callable)` gives you a `Future<V>`; `execute(Runnable)` gives nothing back.

**9. final vs finally vs finalize**
`final`: non-reassignable variable / non-overridable method / non-extendable class. `finally`: block that always runs after try/catch (except `System.exit` or JVM kill).
`finalize()`: deprecated GC hook, unpredictable, never use — use try-with-resources / `Cleaner`.

**10. Overriding vs overloading**
Overriding: subclass redefines a superclass method — same signature, runtime polymorphism, dynamic dispatch. Overloading: same name, different parameter list, resolved at compile time.
Overriding rules: covariant return allowed, access can't narrow, checked exceptions can't widen.

**11. Future vs CompletableFuture**
`Future`: only `get()` (blocking), `isDone`, `cancel`. No composition, no callbacks.
`CompletableFuture`: non-blocking composition (`thenApply`, `thenCompose`, `thenCombine`, `allOf`), exception handling (`exceptionally`, `handle`), manual completion, custom executor.

**12. Process vs thread**
Process: own address space, isolated, heavier, IPC to communicate. Thread: shares heap/metaspace within a process, own stack + program counter, cheap to create.
Shared heap is why we need synchronization.

**13. sleep() vs wait()**
`Thread.sleep()` is static, **keeps** the monitor, wakes on timeout/interrupt. `Object.wait()` **releases** the monitor, must be inside `synchronized`, wakes on `notify`/`notifyAll`/timeout.
Always `wait()` in a `while` loop guarding the condition (spurious wakeups).

**14. equals() vs hashCode()**
Contract: equal objects **must** have equal hash codes; unequal objects may collide.
Break it and a `HashMap` can't find a key you just inserted, or a `HashSet` holds duplicates. Always override both together — or use a `record`.

**15. static vs non-static**
`static` belongs to the class — one copy, loaded at class init, no `this`, can't access instance members directly. Non-static is per-instance.
Static init order: static fields/blocks → instance fields/blocks → constructor.

**16. Comparator vs Comparable**
`Comparable.compareTo` = natural ordering baked into the type (one per class). `Comparator.compare` = external, pluggable, composable (`comparing(...).thenComparing(...).reversed()`).
Never `a.id - b.id` — int overflow breaks TimSort's contract. Use `Integer.compare`.

**17. Stream vs Collection**
Collection stores data, eager, external iteration, reusable. Stream is a pipeline over a source, lazy (terminal op triggers), internal iteration, single-use, stores nothing.
Streams can be parallel and can be infinite.

**18. OOP — four pillars**
Encapsulation: hide state behind behaviour. Inheritance: reuse via an is-a hierarchy. Polymorphism: one interface, many runtime implementations (dynamic dispatch). Abstraction: expose what, hide how.
Say "favour composition over inheritance" — it's the follow-up they want.

**19. Access modifiers**
`private` (class only) → package-private/default (same package) → `protected` (package + subclasses) → `public` (everywhere).
Modules (Java 9) add a layer: `exports` controls what's visible across module boundaries.

**20. Java collections**
Two roots: `Collection` (→ `List`, `Set`, `Queue`/`Deque`) and `Map`. Implementations: `ArrayList`/`LinkedList`, `HashSet`/`LinkedHashSet`/`TreeSet`, `ArrayDeque`/`PriorityQueue`, `HashMap`/`LinkedHashMap`/`TreeMap`.
Concurrent variants in `java.util.concurrent`: `ConcurrentHashMap`, `CopyOnWriteArrayList`, `BlockingQueue` family.

**21. Immutable class / why String is immutable**
Recipe: `final` class, all fields `private final`, no setters, defensive copy of mutable fields in and out, no `this` escaping the constructor.
`String` is immutable for: string-pool sharing, safe hash caching, thread safety without sync, and security (a mutable class name/URL/path could be changed after a security check).

**22. SOLID**
**S**ingle responsibility · **O**pen-closed (extend without modifying) · **L**iskov substitution (subtype must be usable as the base) · **I**nterface segregation (small focused interfaces) · **D**ependency inversion (depend on abstractions).
Dependency inversion is why Spring DI exists — have one concrete example ready.

**23. Checked vs unchecked exceptions**
`Throwable` → `Error` (JVM, don't catch) and `Exception`. Checked = compile-time enforced (`IOException`, `SQLException`), must catch or declare. Unchecked = `RuntimeException` subclasses, not enforced.
Modern practice: prefer unchecked for programming errors; don't wrap everything in checked.

**24. ExecutorService**
Decouples task submission from thread management — thread reuse, queueing, lifecycle (`shutdown`/`shutdownNow`/`awaitTermination`), and a `Future` back.
Never use `Executors.newFixedThreadPool` / `newCachedThreadPool` in production — construct `ThreadPoolExecutor` with a **bounded** queue and an explicit rejection policy.

**25. Serialization**
Converting an object graph to bytes. `implements Serializable` (marker), `transient` skips a field, `serialVersionUID` controls version compatibility.
Java native serialization is a known deserialization-RCE vector — use JSON (Jackson) or Protobuf/Avro instead.

**26. Thread life cycle**
NEW → RUNNABLE → (BLOCKED waiting on a monitor / WAITING on `wait`,`join`,`park` / TIMED_WAITING on `sleep`, timed `wait`) → TERMINATED.
RUNNABLE covers both "running" and "ready to run" — the JVM doesn't distinguish.

**27. How many threads to create, and where**
CPU-bound: ~`Runtime.availableProcessors()`. I/O-bound: `cores × (1 + waitTime/serviceTime)` — measure, don't guess.
Where: never `new Thread()` in application code. One shared, named, bounded pool per workload type, configured centrally.

**28. Synchronization**
`synchronized` gives mutual exclusion **and** a happens-before edge (visibility). On a method it locks `this` (or the `Class` for static); on a block you pick the monitor.
Alternatives: `ReentrantLock` (tryLock, fairness, multiple conditions), `volatile` for visibility only, atomics for single-variable CAS.

**29. AtomicInteger**
Lock-free single-variable atomicity via CAS (`compareAndSet`), implemented on `Unsafe`/VarHandle intrinsics. `incrementAndGet`, `getAndAdd`, `accumulateAndGet`.
Under heavy contention CAS retries burn CPU — use `LongAdder`, which stripes into cells and sums on read.

**30. wait() / notify()**
Monitor-based coordination. `wait()` releases the lock and parks; `notify()` wakes one waiter, `notifyAll()` wakes all. All three require holding the monitor.
Always `while (!condition) wait();`, and prefer `notifyAll()`. Modern code: `BlockingQueue` or `Condition` instead.

**31. join()**
`t.join()` blocks the calling thread until `t` terminates — used to wait for completion. Timed variant `join(ms)`.
Implemented on top of `wait()` on the thread object, which is why you should never `synchronized(thread)` yourself.

**32. transient**
Marks a field to be skipped by Java serialization. Useful for derived values, caches, and secrets.
On deserialization the field gets its default (`null`/`0`).

**33. volatile**
Guarantees **visibility** (reads see the latest write) and prevents reordering around the access. Does **not** give atomicity — `count++` is still a race.
Right use: a status/shutdown flag, or the reference in a hot-swap pattern (build immutable state, assign to a volatile field).

**34. New in Java 8**
Lambdas, Stream API, functional interfaces + `@FunctionalInterface`, `default`/`static` interface methods, method references, `Optional`, new `java.time` API, `CompletableFuture`, PermGen → Metaspace.

**35. Stream API — pros/cons**
Pros: declarative, composable, lazy, easy parallelism, less boilerplate than loops.
Cons: harder to debug (deep stack traces), single-use, boxing overhead on primitives (use `IntStream`), and `parallelStream()` shares the common `ForkJoinPool` — a blocking task there starves the whole JVM.

**36. Lambda — pros/cons**
Pros: concise, enables the Stream API, replaces anonymous inner classes, captures effectively-final locals.
Cons: no state, `this` refers to the enclosing instance (unlike an anonymous class), unreadable when long, and stack traces are opaque.

**37. @FunctionalInterface**
Marks an interface with exactly one abstract method — the compiler enforces it. Not required for a lambda to work, but it documents intent and prevents someone adding a second method.
`Function`, `Supplier`, `Consumer`, `Predicate`, `Runnable`, `Callable`, `Comparator`.

**38 / 46. How do you handle exceptions**
`try/catch/finally`, try-with-resources for `AutoCloseable`. Catch the narrowest type; never swallow (`catch (Exception e) {}`); never `catch (Throwable)`.
In Spring: `@ControllerAdvice` + `@ExceptionHandler` for a consistent error contract; map domain exceptions to HTTP codes; log with correlation IDs and don't leak internals to the client.

**39. How HashMap works**
`hash = h ^ (h >>> 16)` → `index = (n-1) & hash` (table is a power of two) → bucket. Collision → linked list; at 8 nodes **and** table ≥ 64 it becomes a red-black tree.
Resize doubles capacity at `size > capacity × 0.75`; Java 8 splits each bin into lo/hi using `hash & oldCap` — no rehash needed.

**40. How ConcurrentHashMap works**
Java 8 dropped segments. Empty bin → CAS to install the first node (lock-free). Non-empty bin → `synchronized` on the bin's head node, so lock granularity is one bucket. Reads are fully lock-free (`volatile` node fields).
Resize is cooperative: transferred bins get a `ForwardingNode`, and a writer that hits one calls `helpTransfer` instead of blocking.

**41. Optimistic locking**
No lock held. Read a version/timestamp with the row, and on update do `WHERE id = ? AND version = ?`; zero rows affected → someone else won → retry or fail.
JPA: `@Version` field → `OptimisticLockException`. Right choice when conflicts are rare.

**42. Exclusive lock**
A pessimistic write lock — blocks other readers-for-update and writers until commit. `SELECT ... FOR UPDATE`, JPA `LockModeType.PESSIMISTIC_WRITE`.
Correct when contention is high or the retry cost is unacceptable; costs throughput and risks deadlock — always lock rows in a consistent order.

**43. How GC works**
Reachability from GC roots (stacks, statics, JNI); unreachable objects are collected. Generational heap: Eden → Survivor → Old. Minor GC on young (fast, copying), major/full on old.
G1 is the default since Java 9 (region-based, pause-target driven). ZGC/Shenandoah for sub-millisecond pauses on large heaps.

**44. ThreadLocal**
Per-thread variable copy, stored in a `ThreadLocalMap` on the `Thread` object. Used for request/security/MDC context.
Leak risk: in a pooled-thread environment the thread lives forever, and the map's *values* are strongly referenced. Always `remove()` in a `finally`.

**45. throw vs throws**
`throw` is a statement that raises an exception instance. `throws` is a method-signature clause declaring checked exceptions the caller must handle.

**47. New in Java 17 / 21**
17 (LTS): sealed classes, records (16), pattern matching for `instanceof` (16), text blocks (15), switch expressions (14), helpful NPEs, strong encapsulation of internals.
21 (LTS): **virtual threads**, pattern matching for `switch`, record patterns, sequenced collections (`getFirst`/`getLast`), generational ZGC.

**48. sealed**
Restricts which classes may extend/implement: `sealed interface Shape permits Circle, Square`. Every permitted subclass must be `final`, `sealed`, or `non-sealed`.
Point: an exhaustive hierarchy, so `switch` pattern matching needs no `default` — algebraic data types in Java.

**49. Virtual thread vs OS thread**
Platform thread = 1:1 with an OS thread, ~1MB stack, expensive, thousands max. Virtual thread = JVM-scheduled, stack on the heap, millions possible; it mounts on a carrier thread and unmounts when it blocks.
Wins for I/O-bound, not CPU-bound. Pools become pointless — use `newVirtualThreadPerTaskExecutor`. Watch pinning inside `synchronized` blocks and `ThreadLocal` memory at scale.

**50. Heap vs stack**
Heap: shared across threads, holds objects/arrays, GC-managed, `OutOfMemoryError`. Stack: per-thread, holds frames with locals and references, LIFO, freed on return, `StackOverflowError`.
Metaspace (off-heap) holds class metadata.

**51. Stream vs parallel stream**
Sequential = one thread. Parallel splits via `Spliterator` and runs on the shared common `ForkJoinPool` (`cores - 1` workers).
Only pays off with large N, cheap splitting (`ArrayList`/array, not `LinkedList`), independent per-element work, and no blocking I/O. In a web service the request layer is already parallel — I default to sequential.

**52. record**
Immutable transparent data carrier: `record Point(int x, int y) {}` generates final fields, accessors, `equals`/`hashCode`/`toString`, canonical constructor.
Implicitly final, can't extend a class (can implement interfaces), no additional instance fields. Use a compact constructor for validation and defensive copies.

**53. Deque**
Double-ended queue — insert/remove at both ends (`addFirst`/`addLast`, `pollFirst`/`pollLast`), plus `push`/`pop` for stack semantics.
`ArrayDeque` is the implementation to use (circular array, no nulls); it beats `Stack` as a stack and `LinkedList` as a queue.

---

# SPRING BOOT (28)

**1. Spring vs Spring Boot**
Spring = the core DI/AOP framework, configured manually (XML or Java config), deploy a WAR to an external container.
Boot = Spring plus auto-configuration, starter dependencies, embedded server, sensible defaults, externalized config, and Actuator. Convention over configuration; it adds no new DI capability.

**2. Actuator**
Production-readiness endpoints over HTTP/JMX: `/health`, `/metrics`, `/info`, `/env`, `/loggers`, `/threaddump`, `/prometheus`.
`/health` drives k8s/ECS liveness+readiness probes. Only `/health` and `/info` are exposed by default — secure and whitelist the rest deliberately.

**3. DI / IoC / AOP**
IoC: the container owns object creation and wiring instead of your code. DI is how IoC is delivered — dependencies are injected (constructor/setter/field).
AOP: modularize cross-cutting concerns (transactions, security, logging) into aspects applied via proxies, so business code stays clean.

**4. Joinpoint / pointcut**
Joinpoint = a point where advice *can* run (in Spring AOP, always a method execution). Pointcut = the expression selecting which joinpoints match (`execution(* com.x.service.*.*(..))`).
Advice = the code that runs (`@Before`, `@After`, `@Around`, `@AfterReturning`, `@AfterThrowing`). Aspect = pointcut + advice.

**5. Bean injection types**
Constructor (**preferred**): immutable, fields can be `final`, fails fast on missing deps, trivially testable. Setter: optional/reconfigurable deps. Field (`@Autowired` on the field): concise but hides dependencies and can't be set without reflection — avoid.
Single-constructor classes don't need `@Autowired` since Spring 4.3.

**6. Bean life cycle**
Instantiate → populate properties → `*Aware` callbacks → `BeanPostProcessor.postProcessBeforeInitialization` → `@PostConstruct` → `InitializingBean.afterPropertiesSet` → custom `init-method` → BPP after-init → **in use** → `@PreDestroy` → `DisposableBean.destroy` → destroy-method.
Prototype beans get no destruction callback — the container stops tracking them.

**7. Spring servlet / components**
`DispatcherServlet` is the front controller. Flow: request → `HandlerMapping` picks the handler → `HandlerAdapter` invokes it → argument resolvers bind params → return value handlers / `HttpMessageConverter` → `ViewResolver` (MVC) or JSON straight out (REST) → response.
Filters sit outside it (servlet container); interceptors sit inside it.

**8. BeanFactory vs ApplicationContext**
`BeanFactory` = the bare DI container, lazy instantiation. `ApplicationContext` extends it and eagerly instantiates singletons at startup, plus adds i18n, event publishing, resource loading, and AOP/annotation support.
Use `ApplicationContext` — eager startup surfaces wiring errors at boot, not at first request.

**9. Bean scopes**
`singleton` (**default**, one per container), `prototype` (new instance per lookup), and web-only: `request`, `session`, `application`, `websocket`.
Singleton beans must be stateless. Injecting a prototype into a singleton needs `@Lookup`, `ObjectProvider`, or a scoped proxy.

**10. @Autowired vs @Qualifier**
`@Autowired` injects by type. With multiple candidates it throws `NoUniqueBeanDefinitionException`.
`@Qualifier("beanName")` disambiguates; `@Primary` sets a default winner. Constructor param names can also resolve it.

**11. @SpringBootApplication**
Meta-annotation combining `@Configuration` + `@EnableAutoConfiguration` + `@ComponentScan` (scanning starts from the annotated class's package downward).

**12. @Component / @Repository / @Service**
All are `@Component` stereotypes — same registration behaviour, different semantics.
`@Repository` additionally enables persistence exception translation (vendor `SQLException` → Spring's `DataAccessException` hierarchy). `@Service` is purely documentary.

**13. @Controller vs @RestController**
`@Controller` returns view names resolved by a `ViewResolver`. `@RestController` = `@Controller` + `@ResponseBody`, so every return value is serialized directly into the response body.

**14. @RequestBody vs @ResponseBody**
`@RequestBody` deserializes the incoming request body into a method parameter (via `HttpMessageConverter`/Jackson). `@ResponseBody` serializes the return value into the response body instead of resolving a view.

**15. @PathVariable vs @RequestParam**
`@PathVariable` extracts a segment of the URI template — `/orders/{id}`, identifies a resource. `@RequestParam` reads a query string or form parameter — `?status=OPEN`, filters/options.
`@RequestParam` supports `required=false` and `defaultValue`.

**16. @Transactional**
Proxy-based declarative transaction. Default: propagation `REQUIRED`, isolation `DEFAULT` (DB's), rollback **only on unchecked** exceptions — checked exceptions commit unless you set `rollbackFor`.
Two classic pitfalls: **self-invocation** (calling an annotated method from within the same bean bypasses the proxy) and putting it on a non-public method (silently ignored).

**17. Circular dependency**
A → B → A. Constructor injection fails outright; setter/field injection works because Spring can expose a partially built singleton.
Spring Boot 2.6+ **disallows it by default** (`spring.main.allow-circular-references`). The real fix is refactoring — extract the shared logic into a third bean. `@Lazy` is a workaround, not a solution.

**18. HTTP methods / status codes**
GET (safe, idempotent), POST (neither), PUT (idempotent), PATCH (not necessarily), DELETE (idempotent), HEAD, OPTIONS.
2xx success (200, 201 Created, 202 Accepted, 204 No Content) · 3xx redirect (301, 304) · 4xx client (400, 401 unauthenticated, 403 unauthorized, 404, 409 conflict, 422, 429) · 5xx server (500, 502, 503, 504).

**18a. POST vs PUT vs PATCH**
POST creates a subordinate resource at a server-chosen URI — not idempotent, calling twice creates two. PUT replaces the whole resource at a client-known URI — idempotent. PATCH applies a partial update.
If you need a safe retry on POST, that's what an idempotency key is for.

**19. RESTful principles**
Client–server, **stateless** (no server session between requests), cacheable, uniform interface (resources as nouns, HTTP verbs as actions), layered system, HATEOAS (optional in practice).
Plus: proper status codes, plural resource nouns, versioning strategy, and pagination on collections.

**20. Spring Security**
A filter chain in front of the servlet: authenticate → establish a `SecurityContext` → authorize. Configured today as a `SecurityFilterChain` `@Bean` (`WebSecurityConfigurerAdapter` is removed).
Covers authentication (form, basic, JWT, OAuth2), authorization (URL-based + method-level), CSRF, CORS, session management, and password encoding.

**21. JWT**
`header.payload.signature`, base64url-encoded, signed with HMAC (shared secret) or RSA/EC (public key). Self-contained and stateless — the server validates by signature, no session store.
Payload is **encoded, not encrypted** — never put secrets in it. No native revocation, so use a short TTL plus a refresh token.

**22. How did you do testing**
JUnit 5 + Mockito for unit tests on service logic. `@WebMvcTest` + MockMvc for the controller layer. `@DataJpaTest` for repositories. Testcontainers for integration against a real Postgres/Localstack.
Coverage as a signal not a target — I raised unit coverage above 90% on the enrichment services, but the value was in the mock-data Lambda that let us run true end-to-end scenarios.

**23. TDD**
Red → green → refactor: write a failing test, write the minimum code to pass, then clean up with the test as a safety net.
Honest framing: I use it where the contract is clear (parsers, validators, calculations) and write tests alongside rather than strictly first for exploratory integration work.

**24. JDBC vs Hibernate**
JDBC: raw SQL, manual `Connection`/`PreparedStatement`/`ResultSet` mapping, full control, verbose. Hibernate: ORM — maps objects to tables, generates SQL, gives caching, lazy loading, dirty checking, HQL/JPQL.
Hibernate's costs: N+1 selects, lazy-init exceptions, and hidden SQL. For heavy analytical queries I'd drop to JDBC/native SQL.

**25. BeanFactory vs FactoryBean**
`BeanFactory` is *the container*. `FactoryBean<T>` is a *bean* that produces other beans — a factory pattern hook for complex construction.
Gotcha: `context.getBean("x")` returns the produced object; `getBean("&x")` returns the factory itself.

**26. @Async**
Runs a method on another thread and returns immediately (`void`, `Future`, or `CompletableFuture`). Requires `@EnableAsync`.
Same proxy limitations as `@Transactional` — self-invocation doesn't work. Always define your own bounded `TaskExecutor`; the default `SimpleAsyncTaskExecutor` creates an unbounded number of threads.

**27. @SpringBootApplication** — see Spring Boot #11.

**28. WebClient vs RestTemplate**
`RestTemplate` is synchronous, blocking, one thread per request — in maintenance mode, no new features. `WebClient` is the reactive non-blocking client (from `spring-webflux`) and works fine inside a blocking MVC app via `.block()`.
`WebClient` is the recommended default for new code; `RestClient` (Spring 6.1) gives WebClient's fluent API with synchronous semantics.

---

# TESTING (13)

**1. Unit vs integration**
Unit: one class in isolation, collaborators mocked, milliseconds, no Spring context. Integration: multiple real components wired together — Spring context, real DB, real HTTP.
Pyramid: many unit, fewer integration, fewest E2E.

**2. What do you use**
JUnit 5, Mockito, AssertJ for fluent assertions, `@SpringBootTest`/`@WebMvcTest`/`@DataJpaTest` slices, Testcontainers for real Postgres/LocalStack, WireMock for external HTTP.

**3. doAnswer vs when/thenReturn**
`when(x.f()).thenReturn(v)` — static value; it actually calls the method, so it's unsafe on spies and void methods.
`doAnswer`/`doReturn`/`doThrow`/`doNothing` use the `do...when(spy).method()` form, which doesn't invoke the real method. `doAnswer` computes the return from the invocation args, or captures/mutates them — the only option for void methods with side effects.

**4. TDD** — see Spring Boot #23.

**5 / 9 / 10. Mock vs spy**
Mock: a fully fake object; every method returns a default (`null`/`0`/`false`) until stubbed. Spy: wraps a **real** instance; unstubbed methods run the real code, stubbed ones don't.
Use mocks by default. A spy is usually a smell that the class does too much — but it's pragmatic for partially stubbing legacy code.

**6 / 12. Testing experience / last project**
Framing: service-layer unit tests with mocked AWS SDK clients; `@WebMvcTest` + MockMvc for the GraphQL/REST controllers; Testcontainers Postgres for repository and Liquibase migration tests; and the mock-data Lambda injecting 30+ record types on demand for end-to-end pipeline validation — that one cut debugging time ~80% because we could reproduce a broken ingest scenario in minutes.

**7. @ParameterizedTest**
Runs the same test over multiple inputs. Sources: `@ValueSource`, `@CsvSource`, `@MethodSource` (a static factory returning a `Stream<Arguments>`), `@EnumSource`, `@NullAndEmptySource`.
Requires `junit-jupiter-params`. Replaces copy-pasted near-identical tests and makes boundary/edge cases explicit.

**8. How to test a backend API**
Layer by layer: unit-test the service; `@WebMvcTest` + MockMvc for routing, validation, serialization, and status codes with the service mocked; `@SpringBootTest(webEnvironment = RANDOM_PORT)` + `TestRestTemplate`/RestAssured for the full stack; Testcontainers for the DB; WireMock for downstream calls.
Cover: happy path, validation failures (400), auth (401/403), not-found (404), and downstream failure/timeout behaviour.

**11. Clean test code**
Arrange–Act–Assert. One behaviour per test. Descriptive names (`shouldRejectOrderWhenInstrumentIsExpired`). No conditionals or loops in the test body. Deterministic — no real clock, no random, no sleeps, no shared state between tests.
Builders/object mothers for fixtures instead of huge inline setup. A test should read as documentation.

**13. How to test an application without code**
Black-box: exercise the API from Postman/curl/RestAssured against the contract (OpenAPI spec). Contract testing (Pact/Spring Cloud Contract). Exploratory testing on edge cases and error paths.
Plus observability-driven checks — logs, metrics, traces confirm the behaviour you can't see in a response body. Load testing with JMeter/k6.

---

# KAFKA (10)

> Positioning note: your hands-on messaging work is SQS/SNS/Lambda, not Kafka. Answer these as design and conceptual knowledge, and pivot to the SQS story when they ask "in your project." Don't claim Kafka production ownership — it won't survive five minutes of follow-up.

**1. What is Kafka**
A distributed, partitioned, replicated **commit log**. Producers append to topic partitions; consumers read by offset. Messages are retained by time or size, not deleted on read — so multiple consumer groups can replay independently.
Not a queue: it's a durable log with a cursor.

**2. How you use Kafka in your project**
Honest version: "We used SQS and SNS rather than Kafka — SQS for the ingestion pipeline with Glue ETL triggered off the queue, SNS for fan-out. The reasoning was the same set of concerns: at-least-once delivery, idempotent consumers, DLQ and redrive, visibility timeout tuning. I know Kafka's model but haven't operated a cluster."

**3. Consumer group / consumer / partition / topic**
Topic = a named stream, split into partitions. Partition = the ordered, immutable unit of parallelism and ordering. Consumer group = a set of consumers sharing a group ID; each partition is assigned to exactly one consumer in the group.
So group parallelism is capped at the partition count; extra consumers idle.

**4. How Kafka works**
Brokers hold partitions; each has one leader and N followers (replicas). Producers write to the leader; followers replicate. The ISR (in-sync replicas) set determines durability. Offsets are committed to the internal `__consumer_offsets` topic.
KRaft has replaced ZooKeeper for metadata since 3.x.

**5. Producer → consumer journey**
Producer serializes → partitioner picks a partition (key hash, or sticky round-robin if no key) → batched in an accumulator → sent to the partition leader → leader appends and replicates → acked per `acks` setting.
Consumer polls, gets records from its assigned partitions, processes, commits its offset.

**6. Ensuring message order**
Order is guaranteed **only within a partition**. Use a partition key so all events for the same entity land on the same partition (e.g. key by `accountId` or `instrumentId`).
Also set `max.in.flight.requests.per.connection=1` — or enable idempotent producer, which preserves ordering up to 5 in-flight.

**7. Monitoring Kafka**
Consumer lag (the primary signal — per group, per partition), under-replicated partitions, offline partitions, ISR shrink/expand, broker disk and request latency, producer error rate, DLQ depth.
Tooling: Kafka's JMX metrics → Prometheus/Datadog, plus Burrow or Confluent Control Center for lag. My equivalent on SQS was queue depth **and** age-of-oldest-message.

**8. Validating and deduplicating events**
Validate at the edge with a schema (Avro/Protobuf + Schema Registry) so bad messages are rejected before they enter the topic. Dedup with a business idempotency key persisted in a store with a TTL — a conditional write to DynamoDB or a unique constraint in Postgres.
In-memory dedup sets are a leak; they need a TTL'd store.

**9. Handling failed messages**
Classify first: transient (retry with backoff) vs poison (never succeeds). Retry topics with increasing delays, then a dead-letter topic. Never block the partition retrying forever — that stalls every message behind it.
DLQ needs an owner, an alarm, and a documented redrive procedure, or it's just a bucket where data goes to die.

**10. Idempotency in Kafka**
Producer side: `enable.idempotence=true` gives exactly-once *within a partition* via a producer ID and sequence numbers, deduplicating broker-side retries. Transactions add atomic multi-partition writes with `read_committed` consumers.
Consumer side: exactly-once end-to-end is a myth unless the sink is transactional — so make the **handler** idempotent: natural keys, conditional updates, or a state machine that ignores repeat transitions.

---

# SPRING SECURITY + JWT (23)

**1. How do you do security**
Spring Security filter chain, stateless JWT bearer tokens (`SessionCreationPolicy.STATELESS`), BCrypt for stored passwords, role/authority checks at both the URL and method level, HTTPS everywhere, and secrets in a vault rather than config.
On the AWS side: IAM roles over static keys, and RBAC enforced in the service — which is what the document broker's permission-resolution flow does.

**2 / 5. Spring Security internal flow**
Request → `FilterChainProxy` → a chain of filters. The authentication filter builds an unauthenticated `Authentication` token → `AuthenticationManager` (`ProviderManager`) → loops `AuthenticationProvider`s until one `supports()` the token type → provider calls `UserDetailsService.loadUserByUsername` and verifies via `PasswordEncoder` → returns an authenticated `Authentication` with authorities → stored in `SecurityContextHolder`.
Then `AuthorizationFilter` checks access; `ExceptionTranslationFilter` converts failures to 401/403.

**3 / 13. Authentication vs authorization**
Authentication = who you are (credentials verified). Authorization = what you're allowed to do (roles/permissions/scopes).
401 = not authenticated. 403 = authenticated but not permitted.

**4. Where and how passwords are stored**
Hashed in the DB, never encrypted and never plaintext. `BCryptPasswordEncoder` (or Argon2/scrypt) — adaptive, salt embedded in the hash output, work factor tunable.
`DelegatingPasswordEncoder` is the Spring default: the `{bcrypt}` prefix lets you migrate algorithms without invalidating existing hashes.

**5. How JWT works and is validated**
Login issues a signed token. Every subsequent request sends `Authorization: Bearer <token>`. A custom filter extracts it, verifies the **signature**, then checks `exp`, `iss`, `aud`, and `nbf`, loads authorities from claims, and sets the `SecurityContext`.
Signature verification is what makes it trustworthy — never trust decoded claims without it.

**6. How did you implement Spring Security**
A `SecurityFilterChain` bean: `csrf.disable()` (stateless API), `sessionManagement(STATELESS)`, `authorizeHttpRequests` with public paths permitted and everything else authenticated, and a custom `JwtAuthenticationFilter` added before `UsernamePasswordAuthenticationFilter`. Method-level `@PreAuthorize` on sensitive service methods.

**7 / 20. Why SecurityContext / what is SecurityContextHolder**
`SecurityContextHolder` holds the `SecurityContext` (which holds the `Authentication`) in a **`ThreadLocal`** by default, so any layer can ask "who is the current user" without threading it through every method signature.
It must be cleared at the end of the request — the filter does this — or in a pooled thread you leak one user's identity into the next request. For `@Async`, use `MODE_INHERITABLETHREADLOCAL` or a `DelegatingSecurityContextExecutor`.

**8. Multiple authentication mechanisms**
Two options. (a) Register multiple `AuthenticationProvider`s in the `ProviderManager` — each `supports()` a different `Authentication` token type. (b) Cleaner: multiple `SecurityFilterChain` beans with `@Order` and a `securityMatcher`, so `/api/**` uses JWT and `/internal/**` uses mTLS or basic.

**9. ProviderManager loops through all providers — how to speed it up**
It doesn't actually try each one: `supports(Class<? extends Authentication>)` short-circuits on the token type, so give each mechanism its own `Authentication` implementation and only one provider is ever invoked.
Better still, split into separate filter chains by path matcher so each chain holds a single provider. And cache/short-circuit the expensive part — `UserDetailsService` hitting the DB on every request is the real cost, not the loop.

**10. How to configure Spring Security**
A `@Configuration` class exposing a `SecurityFilterChain` bean using the lambda DSL. `WebSecurityConfigurerAdapter` was deprecated in 5.7 and removed in 6.
Also expose `PasswordEncoder` and, if needed, `AuthenticationManager` as beans; `@EnableMethodSecurity` for annotation-based method rules.

**11. How to configure a filter in Spring Security**
`http.addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class)` (or `addFilterAfter`/`addFilterAt`). Extend `OncePerRequestFilter` so it runs exactly once per request even through forwards.
Don't register it as a plain `@Component` `Filter` as well, or it runs twice — once in the servlet chain and once in the security chain.

**12 / 18. Verifying roles / restricting methods**
URL level: `.requestMatchers("/admin/**").hasRole("ADMIN")`. Method level: `@EnableMethodSecurity` + `@PreAuthorize("hasAuthority('DOC_WRITE')")`, `@PostAuthorize`, `@Secured`.
`hasRole("ADMIN")` implicitly prefixes `ROLE_`; `hasAuthority("ROLE_ADMIN")` does not. Mixing them up is the classic bug.

**14. Core components**
`SecurityFilterChain` / `FilterChainProxy`, `AuthenticationManager` (`ProviderManager`), `AuthenticationProvider`, `UserDetailsService` + `UserDetails`, `PasswordEncoder`, `SecurityContextHolder` / `SecurityContext` / `Authentication`, `GrantedAuthority`, and `AuthorizationManager` (replaced `AccessDecisionManager` in Spring Security 6).

**15. Implementing security in a Boot app**
Add `spring-boot-starter-security` (which secures everything by default), then define a `SecurityFilterChain` to specify what's public, choose the authentication mechanism, register a `PasswordEncoder`, and add method-level rules where the URL granularity isn't enough.

**16. Custom user details**
Implement `UserDetailsService.loadUserByUsername(String)` returning a `UserDetails` — either Spring's `User` builder or your own class implementing `UserDetails` so you can carry extra fields (tenant ID, employee ID).
Throw `UsernameNotFoundException` when absent; map your roles to `GrantedAuthority`.

**17. AuthenticationManager's role**
The entry point for authentication: takes an unauthenticated `Authentication`, delegates to the appropriate `AuthenticationProvider`, and returns a fully populated authenticated token or throws an `AuthenticationException`.
`ProviderManager` is the standard implementation; it supports a parent manager for shared providers.

**19. Securing REST APIs**
Stateless (no session, CSRF disabled since there's no cookie), bearer tokens or OAuth2 resource server, HTTPS only, `authorizeHttpRequests` deny-by-default, method-level checks for object-level permissions, CORS configured explicitly.
Plus: rate limiting, input validation, no stack traces in error responses, and audit logging on privileged operations.

**21. Integrating OAuth2**
As a **resource server**: `spring-boot-starter-oauth2-resource-server` + `oauth2ResourceServer(oauth2 -> oauth2.jwt(...))` and point `issuer-uri` at the IdP — Spring fetches the JWKS and validates tokens for you.
As a **client**: `spring-boot-starter-oauth2-client` with registration/provider config for the login flow.

**22. UserDetailsService purpose**
The bridge between Spring Security and your user store. It answers one question: given a username, return the credentials and authorities. It performs no password comparison itself — `DaoAuthenticationProvider` does that with the `PasswordEncoder`.

**23. OAuth2 flow (Authorization Code + PKCE)**
Client redirects the user to the authorization server → user authenticates and consents → AS redirects back with a short-lived **authorization code** → client exchanges the code (plus its secret / PKCE verifier) at the token endpoint for an **access token** (+ refresh token, + ID token in OIDC) → client calls the resource server with the access token.
The code exchange happens back-channel so the token never rides in the browser URL. PKCE protects public clients (SPA/mobile) that can't hold a secret. Roles: resource owner, client, authorization server, resource server.

---

# DATABASE & ORM (3)

**1. Improving slow query performance**
Start with `EXPLAIN ANALYZE` — find the sequential scans, bad join order, and row-estimate errors. Then: add or fix indexes (composite in the right column order, covering indexes to avoid a heap fetch), avoid `SELECT *`, avoid functions on indexed columns in the `WHERE` (kills index use), keyset pagination instead of large `OFFSET`.
ORM-specific: fix N+1 with a `JOIN FETCH` or `@EntityGraph`, batch inserts, and set a fetch size. Then consider caching, denormalization, or a read replica — in that order.

**2. Join types**
`INNER JOIN` — rows matching in both. `LEFT JOIN` — all left rows, nulls where no right match. `RIGHT JOIN` — mirror image. `FULL OUTER JOIN` — all rows from both sides, nulls where unmatched.
`CROSS JOIN` is the cartesian product. A `LEFT JOIN ... WHERE right.col = x` silently becomes an inner join — put the condition in the `ON` clause instead.

**3. Hibernate vs JPA vs ORM**
ORM is the *concept* — mapping objects to relational tables. JPA is the *specification* (interfaces: `EntityManager`, `@Entity`, JPQL). Hibernate is the most common *implementation* of that spec, plus extras beyond it.
Spring Data JPA sits on top and generates repository implementations from method names.

---

# DESIGN PATTERNS (15)

**1. What patterns have you used**
Concretely: Strategy (instrument-type routing in the reconciliation agent), Factory (per-type parsers/handlers), Builder (request/DTO construction), Template Method (shared ETL skeleton), Observer (event-driven SQS/SNS consumers), Proxy (Spring AOP for `@Transactional`), Singleton (Spring beans), Circuit Breaker and Retry (Resilience4j on outbound calls).
Name one and be ready to explain *why it beat the simpler alternative* — that's the real question.

**2. Singleton**
One instance per JVM with a global access point. Used for stateless shared services, caches, config, connection pools.
In Spring you rarely hand-write it — a singleton-scoped bean gives you the same thing with testability and no static state.

**3. How to create one (eager vs lazy)**
Eager: `private static final Instance INSTANCE = new Instance();` — thread-safe by class-init semantics, but built even if unused.
Lazy: double-checked locking with a **`volatile`** field, or better, the **holder idiom** — a private static nested class whose static field is initialized on first access. The JVM's class-init lock makes it thread-safe with zero synchronization cost.

**4. Is Singleton thread safe**
The *creation* is only thread-safe if you make it so. Naive lazy init (`if (instance == null) instance = new X()`) races and can create two instances.
Separately, the instance's *state* is shared across all threads, so any mutable field needs its own synchronization.

**5. Making it thread safe**
Eager: already safe — static initializers run under the JVM's class-initialization lock.
Lazy: holder idiom (best), `volatile` + double-checked locking, `synchronized getInstance()` (correct but locks on every call), or an **enum singleton** — thread-safe and free from reflection/serialization attacks by construction.

**6. Preventing reflection / serialization / cloning attacks**
Reflection: throw from the private constructor if the instance already exists. Serialization: implement `readResolve()` returning the existing instance. Cloning: override `clone()` to throw `CloneNotSupportedException`.
Or use a single-element `enum`, which the JVM guarantees against all three. That's Effective Java Item 3.

**7. Factory pattern**
Encapsulates object creation behind a method so callers depend on an interface, not a concrete class. Use when the concrete type depends on runtime input or config, and to keep `new` out of business logic.
Concrete: a `ParserFactory` returning the right parser per document type — adding a new type touches one place.

**8. Factory code example**
```java
interface Parser { Doc parse(byte[] in); }

class ParserFactory {
    private final Map<DocType, Parser> parsers;   // injected by Spring
    Parser forType(DocType t) {
        return Optional.ofNullable(parsers.get(t))
            .orElseThrow(() -> new UnsupportedDocTypeException(t));
    }
}
```
In Spring, inject `Map<String, Parser>` or `List<Parser>` and let the container populate every implementation — the factory becomes a lookup.

**9. Factory vs abstract factory**
Factory Method: one method creating one product; subclasses decide which concrete type.
Abstract Factory: an interface creating a **family** of related products that must be used together (e.g. `UiFactory` producing a matching `Button` + `Checkbox`). Use it when the products must be consistent with each other.

**10. Builder code example**
```java
Order o = Order.builder()
    .instrumentId("US0378331005")
    .quantity(100)
    .side(Side.BUY)
    .build();                      // validate invariants inside build()
```
Use when a constructor has many parameters, several optional, or the same type repeatedly (telescoping constructors and positional confusion). Lombok `@Builder` generates it; put validation in `build()`.

**11. API Gateway pattern**
A single entry point in front of the microservices. Handles routing, authentication, rate limiting, TLS termination, request aggregation, and protocol translation, so clients don't talk to N services directly.
Tradeoff: it's a single point of failure and can become a distributed monolith if business logic leaks into it. Implementations: Spring Cloud Gateway, AWS API Gateway, Kong.

**12. Circuit breaker**
Wraps a remote call and tracks failures. **Closed** = calls pass through. Failure rate crosses a threshold → **Open** = calls fail fast without hitting the dependency. After a wait, **Half-open** = a few trial calls decide whether to close or re-open.
Prevents a slow dependency from exhausting your thread pool and cascading. Resilience4j; pair it with a timeout, bulkhead, and a fallback.

**13. Proxy**
A stand-in object with the same interface that controls access to the real one — adding lazy loading, access control, caching, logging, or remote invocation.
This is exactly how Spring AOP works: `@Transactional` and `@Async` are JDK dynamic proxies (interface-based) or CGLIB subclasses. It's also why self-invocation bypasses them.

**14. Observer**
Subject maintains a list of observers and notifies them on state change — one-to-many, loosely coupled, publishers don't know subscribers.
Java: `ApplicationEventPublisher` + `@EventListener` in Spring. At the infrastructure level, SNS fan-out to multiple SQS queues is the same pattern across process boundaries.

**15. Chain of Responsibility**
A request passes along a chain of handlers; each either handles it or forwards it. Decouples sender from receiver and makes the handler set configurable.
Canonical examples: the servlet filter chain, the **Spring Security filter chain**, and OkHttp/Netty interceptors. Good answer for "how would you build a pluggable validation pipeline."

---

# BEHAVIOURAL (7)

These need *your* content — here's the framing, not the answer.

**1. Most challenging problem you solved**
Use STAR, and pick something with a real technical decision, not just effort. Strongest candidates from your work: the ETL false-alarm reduction (90% — root cause analysis via Datadog/Splunk, and *why* the alerts were wrong, not just that you tuned them), or the inherited document broker's permission-resolution redesign (you had to understand undocumented code and change an access-control flow without breaking existing consumers).
End with what you'd do differently.

**2. Introduce yourself and your project**
60–90 seconds, in this order: ~4 years backend, Java/Spring Boot microservices on AWS → current project in one sentence (a financial data platform ingesting 30k+ instruments/day) → your specific ownership (the pipeline end to end: ingestor, Glue ETL, serving layer, plus the enrichment and broker services) → one quantified outcome → why you're looking.
Don't narrate your resume top to bottom.

**3. Next five years**
Deeper technical ownership — designing systems rather than components, and being the person accountable for a platform's reliability. Optionally: growing toward tech lead through mentoring rather than moving off the tools.
Keep it concrete and aligned with the role; don't say "management" in an IC interview unless asked.

**4. Team size**
Just answer factually — team size, your role in it, who you interfaced with (product, partner teams, the partner storage service). They're calibrating scope and collaboration surface, not testing you.

**5. How do you scale your Java/SQL/Spring skills**
Give a real mechanism, not "I read blogs." Something like: reading the actual JDK/Spring source when a behaviour surprises me; a side project where I own decisions end to end (the RCA copilot); and code review as the highest-signal feedback loop.
Name one specific thing you learned recently and how.

**6. Your responsibilities**
Frame as ownership, not tasks: "I own the ingestion-to-serving path — the ingestor, the Glue ETL, and the Aurora/DynamoDB/OpenSearch serving layer — plus the biweekly release across 10+ cloud services and the on-call triage for that pipeline."

**7. Strength and weakness**
Strength: pick one and evidence it (end-to-end ownership — you took an inherited service nobody understood and made it changeable).
Weakness: a real one with an active correction, not a humblebrag. Something like: "I've gone deep on my own stack and let broader distributed-systems fundamentals get rusty — I've been working through Kleppmann and rebuilding those from first principles rather than pattern-matching." Never "I work too hard."

---

## What to drill first

1. **Spring `@Transactional` (SB-16) and `@Async` (SB-26)** — the self-invocation proxy pitfall is the single most common follow-up trap, and it tests whether you understand AOP or just memorized annotations.
2. **Spring Security flow (SS-2)** — 23 of ~150 questions are Security/JWT. It's the heaviest-weighted section and the one with the most sequential detail to get right.
3. **Kafka (all 10)** — your weakest area by actual experience. Get the conceptual answers solid *and* rehearse the honest pivot to SQS. Overclaiming here is the highest-risk failure in this bank.
4. **`HashMap`/`CHM` internals (J-39, J-40)** — already covered in depth in the collections guide; just re-read those two entries.
5. **Virtual threads (J-49) and records/sealed (J-52, J-48)** — the "do you keep current" questions. Cheap to learn, disproportionately signalling.

---

## References

1. **[Spring Security — Architecture](https://docs.spring.io/spring-security/reference/servlet/architecture.html)** — the filter chain diagrams are exactly what SS-2 is asking you to reproduce. Read this before the screen.
2. **[Spring Framework — Data Access / Transaction Management](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative.html)** — the proxy limitations section is the source for the self-invocation answer.
3. **[Kafka Documentation — Design](https://kafka.apache.org/documentation/#design)** — sections 4.1–4.7 cover Q3–Q6 and Q10 directly, including the idempotent-producer semantics.
4. **[Baeldung — Spring Security series](https://www.baeldung.com/security-spring)** — code-level walkthroughs for the JWT filter and custom `UserDetailsService`.
5. *Effective Java* 3rd ed. — Item 3 (enum singleton, DP-6), Items 10–11 (equals/hashCode, J-14), Item 17 (immutability, J-21).
