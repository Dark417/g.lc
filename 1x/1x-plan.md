# 1x Plan — Backend Knowledge Map (1 week → 2 months)

- What this is: the study map for backend 八股 and senior-level depth
  - Part A: the **lenses**, the fixed set of questions every concept is examined through
  - Part B: the **map**, ordered tracks going three levels deep (track → topic → concepts to cover)
- This file lists; it does not answer
  - Docs and code that answer go in `x-md/` and the Java/Python projects, indexed in [x.md](x.md)
- Scope: Java backend, Spring, data, APIs, networking, security, distributed basics
  - AI and agents: see `1A/`; data engineering (Spark, Glue, Databricks): separate track, not here
  - Python core: not covered here
- Created 2026-11-14 · aligned with Project `1D/1T/Senior Sprint Plan.md`

## Index
- [0. How to use this plan](#0-how-to-use-this-plan)
- [Part A. Lenses](#part-a-lenses)
  - [A1. The lens set](#a1-the-lens-set)
  - [A2. Which lenses weigh most, by kind of concept](#a2-which-lenses-weigh-most-by-kind-of-concept)
  - [A3. Numbers sheet to build](#a3-numbers-sheet-to-build)
  - [A4. How a generated doc uses the lenses](#a4-how-a-generated-doc-uses-the-lenses)
- [Part B. The map](#part-b-the-map)
  - [Phase W1 — interview sprint (this week)](#phase-w1--interview-sprint-this-week)
  - [Phase M1 — backend breadth (by mid-December)](#phase-m1--backend-breadth-by-mid-december)
  - [Phase M2 — senior depth (by mid-January)](#phase-m2--senior-depth-by-mid-january)
  - [Tracks](#tracks)
- [Amendments to the original ask](#amendments-to-the-original-ask)

---

## 0. How to use this plan
- Work track by track in the Part B order; tick `[ ]` → `[x]` per topic
- One topic is done when you can answer every **★★★ lens** in A1 aloud for it
  - Not when you've read about it
- Priority marks on topics
  - ★★★ asked in most backend loops; must answer 3 lenses deep
  - ★★ asked often; must explain mechanism + one limit
  - ★ nice to know; recognize and name it
- Phase marks: `W1` this week, `M1` by mid-December, `M2` by mid-January
- `✅x` = an `x-md` doc or code slice already exists (see [x.md](x.md))
- To generate a doc for a topic: "gen 1x-plan B5.2" (track 5, topic 2)
  - The doc answers the topic's concepts through the A1 lenses (A4)

---

## Part A. Lenses

- Plain idea: interviewers probe the same handful of angles on every component
  - Fix the angles once, then every concept gets examined the same way
  - A gap shows up as an empty lens, not as a surprise question

### A1. The lens set

- 18 lenses in 6 groups
- ★★★ = answer for every concept where it applies; ★★ = when relevant; ★ = senior extra

**Group 1: Understand**

| # | Lens | Questions to answer | Weight |
|---|---|---|---|
| L1 | Problem | What pain did it remove? What did people do before, and why did that fail? | ★★★ |
| L2 | Mechanism | How does it work underneath: data structures, algorithm, steps of one request? | ★★★ |
| L3 | Guarantees | What exactly does it promise (ordering, atomicity, consistency, durability), and only under which conditions? | ★★★ |
| L4 | Knobs | Which 2–3 settings matter? What does each trade, and what decides its value? | ★★ |

**Group 2: Numbers and scale**

| # | Lens | Questions to answer | Weight |
|---|---|---|---|
| L5 | Capacity limits | What does one instance / node / partition handle (QPS, throughput, size, connections)? Which limit is hit first? | ★★★ |
| L6 | Latency profile | What is the cost of one operation (memory vs disk vs network hop)? p50 vs p99? | ★★ |
| L7 | 10× test | Traffic or data grows 10×: what breaks first? Scale up or out? Which instance size or tier next? | ★★★ |
| L8 | Cost | What is billed (per request, per hour, per GB), and what makes it expensive? | ★ |

**Group 3: Correctness under concurrency**

| # | Lens | Questions to answer | Weight |
|---|---|---|---|
| L9 | Concurrency | Two requests at once on the same data: what happens? Which lock, version, or isolation level protects it? | ★★★ |
| L10 | Idempotency and retries | Same request sent twice: is the result still right? What is the idempotency key, and where is it stored? | ★★★ |
| L11 | Consistency model | Can a reader see stale data? Read-your-writes? Strong vs eventual, and what that costs | ★★ |

**Group 4: Failure**

| # | Lens | Questions to answer | Weight |
|---|---|---|---|
| L12 | Failure modes | What fails (node, network, dependency, overload), what the user sees, how it is detected | ★★★ |
| L13 | Recovery and redundancy | Replication, failover, backups, RPO/RTO; what is lost in a crash at the worst moment? | ★★ |
| L14 | Backpressure and limits | What happens when input exceeds capacity: queue, drop, throttle, shed? | ★★ |

**Group 5: Operate and secure**

| # | Lens | Questions to answer | Weight |
|---|---|---|---|
| L15 | Observability | Which 3 metrics tell you it's healthy? What alarm fires first? | ★★ |
| L16 | Security | Who can call it, how is data protected in transit and at rest, what is the common misconfiguration? | ★★ |
| L17 | Evolution | How do you change it safely: schema migration, versioning, rolling deploy, backward compatibility? | ★ |

**Group 6: Compare and say**

| # | Lens | Questions to answer | Weight |
|---|---|---|---|
| L18 | Siblings and choice | What are the alternatives? Which variable decides between them? Default pick + when to switch | ★★★ |

- Every topic also ends with two outputs (not lenses, but required)
  - 🗣 one line you can say aloud in an interview
  - 2–4 likely follow-up questions, each answered L4 + L5

### A2. Which lenses weigh most, by kind of concept

- Not every lens fits every concept; skip with "n/a" rather than padding
- Focus by kind

| Kind of concept | Examples | Lead with | Usually n/a |
|---|---|---|---|
| Language feature | HashMap, generics, GC, threads | L2, L3, L5, L9, L12 | L8, L15, L16 |
| Framework feature | IoC, AOP, `@Transactional`, JPA | L1, L2, L3, L4, L12 (pitfalls) | L5, L8 |
| Data store | Postgres, DynamoDB, Redis | All of groups 2–4, L18 | — (all apply) |
| Network / edge component | LB, gateway, CDN | L2, L5, L7, L12, L14, L16 | L9 |
| Protocol / API style | REST, gRPC, TLS, OAuth2 | L1, L2, L3, L10, L16, L18 | L5, L8 |
| Pattern / architecture | DDD aggregate, saga, outbox | L1, L3, L9, L10, L12, L18 | L5, L6, L8 |

### A3. Numbers sheet to build

- Plain idea: L5–L7 need numbers; keep them in one sheet, each with source + date or "order of magnitude"
- File to create: `x-md/00numbers.md` (task to add)
- Rows to fill (not answered here)
  - Latency ladder: L1 cache, RAM, SSD read, same-AZ hop, cross-region hop, disk seek
  - JVM: thread stack size, typical heap sizes, GC pause ranges by collector
  - Postgres / MySQL: simple-query QPS per instance by size, max connections, replica lag, max table size before partitioning helps
  - Aurora: replica count limit, failover time, storage limit
  - DynamoDB: per-partition read/write units, item size limit, GSI count limit, transaction item limit
  - MongoDB: document size limit, shard-key limits
  - Redis: ops/s per node, single-thread implications, max memory per node in practice
  - Kafka: throughput per partition, partitions per broker, message size default
  - SQS / Kinesis: message size, retention, per-shard throughput
  - S3: request rate per prefix, object size limits, multipart part limits
  - LB / API gateway: request limits, timeouts, payload limits
  - HTTP: typical header and payload sizes; TLS handshake round trips (1.2 vs 1.3)
  - Back-of-envelope constants: seconds/day, QPS from DAU, storage per year

### A4. How a generated doc uses the lenses

- Each topic doc keeps the project shape (one-minute version first), then adds a **Lens table**
  ```
  ## Lens check
  | Lens | Answer (1–3 lines) |
  | L1 Problem | ... |
  | L2 Mechanism | ... (or link to section) |
  | ... | n/a — reason |
  ```
- Rules
  - Every ★★★ lens is answered or marked n/a with a reason
  - Numbers in L5–L7 link to the numbers sheet row
  - L18 ends with "Default: X, unless Y"
- A topic can be reviewed in 2 minutes by reading only its one-minute version + lens table

---

## Part B. The map

- Order = study order; it builds bottom-up (language → framework → data → APIs → network → distributed)
- Each track: topics (level 2) with concepts to cover (level 3)

### Phase W1 — interview sprint (this week)
- Goal: the 八股 most asked in backend loops, matched to the Sprint Plan days
- B1 Java core (all ★★★ topics)
- B3 Spring core: B3.1–B3.4
- B4 Data access: B4.2–B4.4 (JPA essentials)
- B11 DB fundamentals: B11.1–B11.4
- B14 Cache: B14.1–B14.3
- B8 API design: B8.1 REST
- B2 SOLID review (✅x exists)

### Phase M1 — backend breadth (by mid-December)
- Rest of B3–B4, then B5–B10, B12–B13, B15–B17

### Phase M2 — senior depth (by mid-January)
- B18–B20, every ★ topic, GoF in full, the numbers sheet complete

### Tracks

- [B1. Java core](#b1-java-core)
- [B2. Design principles and patterns](#b2-design-principles-and-patterns)
- [B3. Spring core and Spring Boot](#b3-spring-core-and-spring-boot)
- [B4. Data access: JDBC, JPA, Hibernate, Spring Data](#b4-data-access-jdbc-jpa-hibernate-spring-data)
- [B5. Spring MVC and the web layer](#b5-spring-mvc-and-the-web-layer)
- [B6. Spring Security](#b6-spring-security)
- [B7. Microservice architecture](#b7-microservice-architecture)
- [B8. API design and communication protocols](#b8-api-design-and-communication-protocols)
- [B9. Domain-driven design and code structure](#b9-domain-driven-design-and-code-structure)
- [B10. Networking fundamentals](#b10-networking-fundamentals)
- [B11. Database fundamentals](#b11-database-fundamentals)
- [B12. Data modeling](#b12-data-modeling)
- [B13. Relational databases](#b13-relational-databases)
- [B14. Cache and in-memory stores](#b14-cache-and-in-memory-stores)
- [B15. NoSQL databases](#b15-nosql-databases)
- [B16. Choosing a database](#b16-choosing-a-database)
- [B17. Edge and traffic: LB, API gateway, CDN, rate limiting](#b17-edge-and-traffic-lb-api-gateway-cdn-rate-limiting)
- [B18. Security and security protocols](#b18-security-and-security-protocols)
- [B19. Messaging and async processing](#b19-messaging-and-async-processing)
- [B20. Distributed systems and reliability](#b20-distributed-systems-and-reliability)

---

#### B1. Java core
- Existing: `x-md/0java/` (check contents), `1sde/1.java/`

- [ ] **B1.1 OOP fundamentals** ★★★ W1
  - Class vs object; constructors; `static` vs instance; initialization order
  - Encapsulation; access modifiers
  - Inheritance: `extends`, `super`, constructor chaining, single inheritance
  - Polymorphism: overriding vs overloading, dynamic dispatch, covariant returns
  - Abstract class vs interface; default and static interface methods
  - Composition over inheritance
  - `final` on class / method / variable
- [ ] **B1.2 Object contract** ★★★ W1
  - `equals` / `hashCode` contract and what breaks in HashMap when violated
  - `toString`, `compareTo` / `Comparator`
  - Immutability: how to build an immutable class; records
  - `String` immutability, string pool, `StringBuilder`
  - Pass-by-value of references
- [ ] **B1.3 Collections** ★★★ W1
  - Hierarchy: `List`, `Set`, `Map`, `Queue`, `Deque`
  - `ArrayList` vs `LinkedList`; growth and complexity
  - `HashMap` internals: buckets, hashing, treeification, resize, load factor
  - `LinkedHashMap` (LRU), `TreeMap` (red-black tree), `PriorityQueue` (heap)
  - Fail-fast iterators, `ConcurrentModificationException`
  - Concurrent collections: `ConcurrentHashMap`, `CopyOnWriteArrayList`, `BlockingQueue`
- [ ] **B1.4 Generics** ★★
  - Type erasure; bounded types; wildcards and PECS
  - Why `List<Integer>` is not a `List<Number>`
- [ ] **B1.5 Exceptions** ★★
  - Checked vs unchecked; `Error` vs `Exception`
  - try-with-resources; `finally` pitfalls
  - Custom exceptions; exception translation across layers
- [ ] **B1.6 Concurrency basics** ★★★ W1
  - Thread lifecycle; `Runnable` / `Callable`; daemon threads
  - Race conditions, visibility, atomicity, ordering
  - `synchronized`, intrinsic locks, reentrancy
  - `volatile` and happens-before
  - Deadlock, livelock, starvation; how to prevent deadlock
  - `wait` / `notify` vs `Condition`
- [ ] **B1.7 java.util.concurrent** ★★★ W1
  - `ExecutorService`, thread pools, `ThreadPoolExecutor` parameters, rejection policies
  - `Future`, `CompletableFuture` composition
  - `ReentrantLock`, `ReadWriteLock`, `StampedLock`
  - Atomics and CAS; `LongAdder`
  - `CountDownLatch`, `CyclicBarrier`, `Semaphore`
  - `ThreadLocal` and its leak in pools
  - Virtual threads (Java 21): what changes, pinning
- [ ] **B1.8 JVM and memory** ★★★ W1
  - Memory areas: heap (young / old), stack, metaspace
  - Class loading: parent delegation
  - GC basics: reachability, generational hypothesis
  - Collectors: G1, ZGC, Parallel; pause vs throughput
  - `OutOfMemoryError` types; memory leak patterns
  - Diagnosing: heap dump, thread dump, GC logs
- [ ] **B1.9 Modern Java features** ★★
  - Lambdas, functional interfaces, method references
  - Streams: lazy evaluation, collectors, parallel streams pitfalls
  - `Optional` usage rules
  - Records, sealed classes, pattern matching, switch expressions, text blocks
- [ ] **B1.10 I/O and serialization** ★
  - Blocking I/O vs NIO; `Selector`
  - Java serialization pitfalls; JSON (Jackson) basics

#### B2. Design principles and patterns
- Existing: ✅x `01core.01principles` (SOLID, general, Spring principles); `1sde/1.core/design-patterns/`

- [ ] **B2.1 SOLID** ★★★ W1 ✅x
  - SRP, OCP, LSP, ISP, DIP: violation vs fix, one real example each
- [ ] **B2.2 General principles** ★★ ✅x
  - DRY, KISS, YAGNI, law of Demeter, composition over inheritance, high cohesion / low coupling
- [ ] **B2.3 Creational patterns** ★★
  - Singleton (thread-safe forms), Factory Method, Abstract Factory, Builder, Prototype
- [ ] **B2.4 Structural patterns** ★★
  - Adapter, Decorator, Proxy, Facade, Composite, Bridge, Flyweight
- [ ] **B2.5 Behavioral patterns** ★★
  - Strategy, Observer, Template Method, Chain of Responsibility, Command, State, Iterator, Visitor
- [ ] **B2.6 Patterns inside Spring and the JDK** ★★
  - Proxy (AOP), Template Method (`JdbcTemplate`), Factory (`BeanFactory`), Observer (events), Strategy, Decorator (I/O streams)

#### B3. Spring core and Spring Boot
- Existing: ✅x Spring principles in `01core.01principles` part C; ⬜ `06framework.01spring-ioc`

- [ ] **B3.1 IoC and DI** ★★★ W1
  - IoC vs DI vs DIP: three different things
  - Injection types: constructor vs setter vs field, and why constructor
  - `BeanFactory` vs `ApplicationContext`
  - Component scanning, `@Configuration` + `@Bean`, `@Qualifier`, `@Primary`
  - Circular dependencies: why they happen, how Spring handles them, why to avoid
- [ ] **B3.2 Bean lifecycle and scopes** ★★★ W1
  - Lifecycle: instantiate → populate → aware → `BeanPostProcessor` → init → destroy
  - `@PostConstruct`, `InitializingBean`, `@PreDestroy`
  - Scopes: singleton, prototype, request, session; prototype-in-singleton problem
  - Thread safety of singleton beans
- [ ] **B3.3 AOP** ★★★ W1
  - Concepts: aspect, advice, join point, pointcut
  - JDK dynamic proxy vs CGLIB
  - Self-invocation trap; final methods
  - Use cases: transactions, logging, security, caching, retries
- [ ] **B3.4 Transactions** ★★★ W1
  - `@Transactional` mechanism (proxy + `PlatformTransactionManager`)
  - Propagation: REQUIRED, REQUIRES_NEW, NESTED, and when each is right
  - Isolation settings mapped to DB isolation levels
  - Rollback rules (checked vs unchecked); `readOnly`
  - Pitfalls: self-invocation, private methods, swallowed exceptions, long transactions
  - Transactions + messaging: why the outbox exists (link B19)
- [ ] **B3.5 Spring Boot** ★★
  - Auto-configuration: `@Conditional*`, starters, how to see what was applied
  - Externalized config: profiles, `@ConfigurationProperties`, precedence order
  - Embedded server; fat jar; startup sequence
  - Actuator: health, metrics, readiness vs liveness
- [ ] **B3.6 Events and async** ★
  - `ApplicationEvent`, `@EventListener`, `@TransactionalEventListener`
  - `@Async`, `@Scheduled`; executor configuration
- [ ] **B3.7 Caching and retries in Spring** ★
  - `@Cacheable` and its proxy pitfalls; Spring Retry / Resilience4j annotations
- [ ] **B3.8 Testing** ★★
  - Unit vs slice (`@WebMvcTest`, `@DataJpaTest`) vs `@SpringBootTest`
  - Mocking (`@MockBean`); Testcontainers

#### B4. Data access: JDBC, JPA, Hibernate, Spring Data
- Existing: ✅x Aurora slice (JdbcTemplate, locks, keyset paging)

- [ ] **B4.1 JDBC and connection pools** ★★
  - `DataSource`, `Connection`, `PreparedStatement` (SQL injection, plan reuse)
  - HikariCP: pool size reasoning, timeouts, leak detection
  - `JdbcTemplate`, batch updates
- [ ] **B4.2 JPA core** ★★★ W1
  - JPA (spec) vs Hibernate (implementation) vs Spring Data JPA (repositories)
  - Entity, `@Id` generation strategies (IDENTITY vs SEQUENCE vs UUID) and batch-insert impact
  - Persistence context / first-level cache; entity states (transient, managed, detached, removed)
  - Dirty checking and flush modes
  - `EntityManager` operations: persist, merge, find, getReference, remove
- [ ] **B4.3 Relationships and fetching** ★★★ W1
  - `@OneToMany`, `@ManyToOne`, `@ManyToMany`, `@OneToOne`; owning side, `mappedBy`
  - Cascade types; orphan removal
  - Lazy vs eager; `LazyInitializationException`; open-session-in-view
  - N+1 problem; fixes: fetch join, `@EntityGraph`, batch size
  - Bidirectional sync helpers; `equals`/`hashCode` on entities
- [ ] **B4.4 Spring Data JPA** ★★★ W1
  - Repository interfaces; derived queries; `@Query` (JPQL vs native)
  - Pagination and sorting; why offset paging degrades
  - Projections (interface / DTO)
  - Auditing (`@CreatedDate`); `@Modifying` queries
- [ ] **B4.5 Locking and concurrency in JPA** ★★★
  - Optimistic locking with `@Version`; `OptimisticLockException` handling
  - Pessimistic locks (`PESSIMISTIC_WRITE`) and their SQL
  - Lost update scenarios
- [ ] **B4.6 Performance and caching** ★★
  - Second-level cache; query cache; when not to use them
  - Batch inserts/updates; `hibernate.jdbc.batch_size`
  - Reading SQL logs and query plans from JPA
- [ ] **B4.7 Alternatives** ★
  - MyBatis, jOOQ, plain JDBC: when each beats JPA
- [ ] **B4.8 Schema migration** ★★
  - Flyway / Liquibase; expand-and-contract migrations; zero-downtime column changes

#### B5. Spring MVC and the web layer
- [ ] **B5.1 Request flow** ★★
  - Servlet container, `DispatcherServlet`, handler mapping, handler adapter, message converters
  - Thread-per-request model; Tomcat thread pool limits
- [ ] **B5.2 Controllers** ★★
  - `@RestController`, request mapping, path vs query params, `ResponseEntity`
  - Validation (`@Valid`, Bean Validation), DTOs vs entities at the boundary
- [ ] **B5.3 Errors and cross-cutting** ★★
  - `@ControllerAdvice`, error response format (RFC 7807 problem details)
  - Filters vs interceptors vs AOP: order and use
  - CORS configuration
- [ ] **B5.4 Reactive web** ★
  - WebFlux vs MVC: event loop, backpressure; when reactive is worth it
  - Virtual threads as the alternative

#### B6. Spring Security
- [ ] **B6.1 Architecture** ★★
  - Filter chain, `SecurityFilterChain`, `SecurityContext`, thread-local holder
  - Authentication vs authorization flow; `AuthenticationManager`, providers
- [ ] **B6.2 Common setups** ★★
  - Session-based login vs stateless JWT
  - OAuth2 resource server (JWT validation), OAuth2 client login
  - Password storage (BCrypt / Argon2)
- [ ] **B6.3 Authorization** ★★
  - URL rules vs method security (`@PreAuthorize`)
  - Roles vs authorities; RBAC; ABAC hooks
- [ ] **B6.4 Web threats handled** ★
  - CSRF (when needed, when not), CORS vs CSRF confusion, security headers

#### B7. Microservice architecture
- [ ] **B7.1 Monolith vs microservices** ★★★
  - Modular monolith; when splitting pays off; costs (network, data, ops)
  - Service boundaries by business capability (link B9)
- [ ] **B7.2 Communication** ★★★
  - Sync (REST, gRPC) vs async (events, queues); temporal coupling
  - Request/response vs event-driven; choreography vs orchestration
- [ ] **B7.3 Data ownership** ★★★
  - Database per service; no shared tables
  - Cross-service queries: API composition, CQRS read models
  - Distributed transactions: saga (orchestrated / choreographed), outbox, inbox (link B19, B20)
- [ ] **B7.4 Resilience patterns** ★★★
  - Timeouts, retries with backoff and jitter, circuit breaker, bulkhead, fallback
  - Retry storms; idempotent endpoints as a prerequisite
- [ ] **B7.5 Platform pieces** ★★
  - Service discovery, config server, API gateway (link B17), service mesh (sidecar)
  - Containers, Kubernetes basics (pod, deployment, service, HPA)
- [ ] **B7.6 Observability** ★★
  - Correlation IDs, distributed tracing (OpenTelemetry), structured logs, RED / USE metrics
- [ ] **B7.7 Deployment** ★★
  - Rolling, blue-green, canary; feature flags; backward-compatible contracts

#### B8. API design and communication protocols
- [ ] **B8.1 REST** ★★★ W1
  - Resources and URIs; HTTP methods and their safety / idempotency
  - Status codes that matter (200, 201, 202, 204, 400, 401, 403, 404, 409, 422, 429, 5xx)
  - Idempotency keys for POST; retries
  - Pagination: offset vs cursor; filtering and sorting
  - Versioning strategies; backward compatibility
  - Error format; HATEOAS (recognize only)
  - Long-running operations: 202 + status resource
- [ ] **B8.2 GraphQL** ★★
  - Schema, queries, mutations, resolvers
  - N+1 in resolvers and DataLoader
  - Caching and rate-limiting difficulty; when it beats REST
- [ ] **B8.3 gRPC** ★★
  - Protobuf, HTTP/2, streaming modes (unary, server, client, bidi)
  - Schema evolution rules; deadlines; load balancing issues with long-lived connections
- [ ] **B8.4 Real-time and push** ★★★
  - Polling, long polling, SSE, WebSocket: mechanism, connection cost, scaling the connection layer
  - Webhooks: signing, retries, idempotent receivers
- [ ] **B8.5 Async contracts** ★★
  - Event schema design, schema registry, versioning events
- [ ] **B8.6 Choosing a style** ★★★
  - Comparison: REST vs GraphQL vs gRPC vs messaging; deciding variables

#### B9. Domain-driven design and code structure
- Existing: `ddd/` sample projects (`2stripe`, `2stripe2`); 1x uses hexagonal layers

- [ ] **B9.1 Strategic DDD** ★★
  - Domain, subdomain (core, supporting, generic)
  - Bounded context; ubiquitous language
  - Context map: shared kernel, customer/supplier, anti-corruption layer
- [ ] **B9.2 Tactical DDD** ★★★
  - Entity vs value object
  - Aggregate and aggregate root; consistency boundary; one transaction per aggregate
  - Repository; domain service vs application service
  - Domain events; factories
- [ ] **B9.3 Architecture styles** ★★★
  - Layered vs hexagonal (ports and adapters) vs clean architecture
  - Dependency direction; where Spring annotations belong
  - Package-by-layer vs package-by-feature
- [ ] **B9.4 From model to services** ★★
  - Bounded context → service boundary; when one context is several services
  - CQRS; event sourcing (recognize, know the cost)

#### B10. Networking fundamentals
- [ ] **B10.1 Layers** ★★
  - OSI vs TCP/IP model; what each layer adds
- [ ] **B10.2 TCP and UDP** ★★★
  - Three-way handshake, teardown, TIME_WAIT
  - Reliability: sequence numbers, ACKs, retransmission; flow control vs congestion control
  - Head-of-line blocking; when UDP wins
- [ ] **B10.3 HTTP** ★★★
  - HTTP/1.1 keep-alive; HTTP/2 multiplexing; HTTP/3 over QUIC
  - Headers that matter: caching, content negotiation, cookies
- [ ] **B10.4 DNS** ★★
  - Resolution path, TTLs, caching; DNS-based load balancing and failover
- [ ] **B10.5 TLS** ★★★
  - Handshake (1.2 vs 1.3), certificates and chain of trust, SNI
  - mTLS; TLS termination points
- [ ] **B10.6 Connections in practice** ★★
  - Connection pooling; ephemeral port exhaustion; timeouts (connect vs read)
  - "What happens when you type a URL" end to end

#### B11. Database fundamentals
- [ ] **B11.1 ACID** ★★★ W1
  - Atomicity (undo / WAL), consistency, isolation, durability (fsync, WAL)
- [ ] **B11.2 Isolation levels and anomalies** ★★★ W1
  - Dirty read, non-repeatable read, phantom, lost update, write skew
  - Read uncommitted → serializable; defaults in Postgres vs MySQL
  - MVCC: how snapshots work
- [ ] **B11.3 Locking** ★★★ W1
  - Row vs table locks; shared vs exclusive; `SELECT ... FOR UPDATE`, `SKIP LOCKED`
  - Deadlocks in the DB; optimistic vs pessimistic concurrency
- [ ] **B11.4 Indexes** ★★★ W1
  - B-tree vs hash vs LSM-tree; clustered vs secondary
  - Composite indexes and leftmost prefix; covering indexes
  - When indexes hurt (write cost, low selectivity)
  - Reading an `EXPLAIN` plan
- [ ] **B11.5 Replication** ★★★
  - Leader-follower; sync vs async; replica lag and read-your-writes
  - Multi-leader and leaderless (quorum reads/writes)
  - Failover and split brain
- [ ] **B11.6 Partitioning and sharding** ★★★
  - Vertical vs horizontal; range vs hash vs directory
  - Shard key choice; hot partitions; resharding; consistent hashing
  - Cross-shard queries and transactions
- [ ] **B11.7 CAP and PACELC** ★★
  - What CAP actually says; why PACELC is more useful day to day
- [ ] **B11.8 Durability and backup** ★★
  - WAL, checkpoints; backups, PITR; RPO / RTO

#### B12. Data modeling
- [ ] **B12.1 Entities and relations** ★★★
  - Identify entities from requirements; attributes vs entities
  - Cardinality: 1:1, 1:N, N:M (join tables)
  - ER diagrams; from ER to tables
- [ ] **B12.2 Normalization** ★★
  - 1NF–3NF in practice; when to denormalize (read paths, counters)
- [ ] **B12.3 Keys and IDs** ★★★
  - Natural vs surrogate keys; UUID v4 vs v7 vs Snowflake vs DB sequence
  - Unique constraints as business invariants
- [ ] **B12.4 Access-pattern-first modeling** ★★★
  - List queries first, then design tables and indexes
  - Modeling for NoSQL: single-table design, embedding vs referencing
- [ ] **B12.5 Common modeling problems** ★★
  - Soft delete, audit history, temporal data (valid-from / valid-to)
  - Money and time zones; enums; JSON columns
  - Multi-tenancy: shared table vs schema vs database
  - Hierarchies (adjacency list, closure table); counters

#### B13. Relational databases
- Existing: ✅x `03db.01aurora` (Aurora Postgres)

- [ ] **B13.1 Postgres** ★★★
  - MVCC with tuple versions; VACUUM and bloat
  - Index types: B-tree, GIN (JSONB, full text), GiST, BRIN
  - JSONB vs columns; partitioning (declarative)
  - Connection model (process per connection) and PgBouncer
  - Extensions: PostGIS, pgvector
- [ ] **B13.2 MySQL (InnoDB)** ★★
  - Clustered primary key; secondary index lookup cost
  - Gap and next-key locks; REPEATABLE READ default
  - Binlog and replication formats
- [ ] **B13.3 Postgres vs MySQL** ★★
  - Where they differ in practice; default pick
- [ ] **B13.4 Managed: Aurora / RDS** ★★ ✅x
  - Shared storage, 6 copies across 3 AZs; reader endpoint; failover; Serverless v2
- [ ] **B13.5 Scaling a relational DB** ★★★
  - Order: indexes and queries → connection pooling → read replicas → caching → vertical → partitioning → sharding
  - The point where you leave relational (link B16)

#### B14. Cache and in-memory stores
- [ ] **B14.1 Caching patterns** ★★★ W1
  - Cache-aside, read-through, write-through, write-behind
  - TTLs and invalidation; consistency between cache and DB
- [ ] **B14.2 Cache failure modes** ★★★ W1
  - Stampede / thundering herd (locking, early refresh)
  - Penetration (missing keys, Bloom filter) and avalanche (TTL jitter)
  - Hot keys (local cache, key replication)
- [ ] **B14.3 Redis** ★★★ W1
  - Single-threaded event loop; why it's fast; I/O threads
  - Data types: string, hash, list, set, sorted set, stream, HyperLogLog, bitmap, geo
  - Persistence: RDB vs AOF; durability limits
  - Eviction policies (LRU / LFU / TTL-based)
  - Replication, Sentinel, Cluster (hash slots)
  - Use cases: session store, rate limiter, leaderboard, distributed lock (and why Redlock is debated), pub/sub, queues
- [ ] **B14.4 Redis vs Memcached vs local cache** ★★
  - Caffeine / in-process caches; multi-level caching
- [ ] **B14.5 Where to cache** ★★
  - Browser, CDN, gateway, application, database buffer pool

#### B15. NoSQL databases
- [ ] **B15.1 NoSQL families** ★★★
  - Key-value, wide-column, document, graph, search, time-series: what each optimizes
- [ ] **B15.2 Key-value / wide-column: DynamoDB** ★★★ ✅x
  - Partition key and sort key; item collections
  - Partitions, throughput per partition, adaptive capacity, hot partitions
  - LSI vs GSI; GSI eventual consistency; projections
  - Query vs Scan; pagination
  - Conditional writes, optimistic locking, transactions
  - Capacity modes (on-demand vs provisioned); TTL; Streams
  - Single-table design
- [ ] **B15.3 Wide-column: Cassandra** ★★
  - Ring, consistent hashing, replication factor, tunable consistency (QUORUM)
  - LSM storage, compaction, tombstones; partition-key-first modeling
- [ ] **B15.4 Document: MongoDB** ★★ ✅x
  - Documents and embedding vs referencing; 16 MB limit
  - Indexes; aggregation pipeline
  - Replica sets, write concern, read concern / preference
  - Sharding and shard key choice; multi-document transactions
- [ ] **B15.5 Search: Elasticsearch / OpenSearch** ★★
  - Inverted index, analyzers; shards and replicas; near-real-time refresh
  - Keeping it in sync with the source of truth (CDC)
- [ ] **B15.6 Others** ★
  - Time-series (InfluxDB, Timestream), graph (Neo4j), NewSQL (Spanner, CockroachDB)

#### B16. Choosing a database
- [ ] **B16.1 Decision dimensions** ★★★
  - Data shape and relations; query patterns (point, range, join, aggregate, search)
  - Consistency needs; transaction scope
  - Read/write ratio and volume; latency target
  - Scale-out need; ops burden; cost model
- [ ] **B16.2 Comparison matrix to fill** ★★★
  - Rows: Postgres, MySQL, DynamoDB, MongoDB, Cassandra, Redis, Elasticsearch
  - Columns: the B16.1 dimensions + capacity limit (L5) + 10× path (L7) + main failure mode (L12)
- [ ] **B16.3 Polyglot persistence** ★★
  - One source of truth + derived stores (cache, search, analytics) via CDC / events
- [ ] **B16.4 Interview defaults** ★★★
  - "Default Postgres unless …"; when DynamoDB; when Redis is primary; when to add search

#### B17. Edge and traffic: LB, API gateway, CDN, rate limiting
- Existing: Project `1sd/0.cloud-equivalents.md` (naming across clouds)

- [ ] **B17.1 Load balancers** ★★★
  - L4 vs L7; algorithms (round robin, least connections, consistent hashing)
  - Health checks; connection draining; sticky sessions and why to avoid
  - LB for WebSockets / long-lived connections
- [ ] **B17.2 Reverse proxy and API gateway** ★★★
  - Responsibilities: auth, rate limiting, routing, TLS termination, transforms
  - Gateway vs LB vs service mesh; BFF pattern
- [ ] **B17.3 CDN** ★★★
  - Edge caching, cache keys, TTLs, invalidation, origin shield
  - Static vs dynamic content; signed URLs
- [ ] **B17.4 Rate limiting** ★★★
  - Token bucket, leaky bucket, fixed vs sliding window
  - Distributed rate limiting (Redis); where to enforce; 429 + Retry-After
- [ ] **B17.5 Autoscaling and capacity** ★★
  - Horizontal vs vertical; scaling signals; warm-up; stateless services

#### B18. Security and security protocols
- [ ] **B18.1 AuthN vs AuthZ** ★★★
  - Sessions + cookies vs tokens; where each breaks
- [ ] **B18.2 OAuth 2.0 and OIDC** ★★★
  - Roles; authorization code + PKCE; client credentials; refresh tokens
  - OIDC ID token vs access token; scopes
- [ ] **B18.3 JWT** ★★★
  - Structure, signing (HS256 vs RS256), validation steps, expiry and revocation problem
- [ ] **B18.4 Transport and PKI** ★★
  - TLS recap (link B10.5); certificates, CA hierarchy, rotation, mTLS for service-to-service
- [ ] **B18.5 Data protection** ★★
  - Encryption at rest; KMS envelope encryption; secrets management; hashing vs encryption
- [ ] **B18.6 Access control models** ★★
  - RBAC, ABAC, ReBAC (Zanzibar idea); least privilege; IAM policies
- [ ] **B18.7 Common attacks** ★★
  - OWASP top 10: injection, XSS, CSRF, SSRF, broken access control; mitigations
- [ ] **B18.8 API security** ★★
  - Input validation, rate limits, API keys vs tokens, webhook signatures, audit logs

#### B19. Messaging and async processing
- Existing: ⬜ `02messaging.*` slices planned (Kinesis, Kafka, Flink, SQS/SNS)

- [ ] **B19.1 Queue vs log vs pub/sub** ★★★
  - SQS vs Kafka vs SNS: consumption model, retention, replay
- [ ] **B19.2 Delivery semantics** ★★★
  - At-most-once, at-least-once, "exactly-once" and what it really means
  - Idempotent consumers; dedup keys
- [ ] **B19.3 Kafka** ★★★
  - Topics, partitions, offsets, consumer groups, rebalancing
  - Replication: leader, ISR, `acks`, `min.insync.replicas`
  - Ordering per partition; key choice; idempotent and transactional producers
- [ ] **B19.4 SQS / SNS** ★★
  - Visibility timeout, DLQ, FIFO groups, fan-out SNS → SQS
- [ ] **B19.5 Patterns** ★★★
  - Transactional outbox, inbox; CDC (Debezium)
  - Retry topics, DLQ handling, poison messages
  - Backpressure and consumer lag
- [ ] **B19.6 Stream processing** ★
  - Windows, watermarks, state (Flink / Kafka Streams); Kinesis basics

#### B20. Distributed systems and reliability
- [ ] **B20.1 Time and ordering** ★★
  - Clock skew; logical clocks; why "last write wins" loses data
- [ ] **B20.2 Consensus and coordination** ★★
  - Raft (leader election, log replication); quorum vs consensus
  - ZooKeeper / etcd uses: leader election, config, locks
- [ ] **B20.3 Distributed transactions** ★★★
  - 2PC and its blocking problem; saga with compensations; outbox
- [ ] **B20.4 Distributed locks and leases** ★★
  - Lease + fencing tokens; Redis vs DB vs ZooKeeper locks
- [ ] **B20.5 Idempotency end to end** ★★★
  - Keys, dedup stores, retention window, scope; idempotent vs exactly-once
- [ ] **B20.6 Reliability engineering** ★★
  - SLI / SLO / error budget; graceful degradation; load shedding
  - Multi-AZ vs multi-region; active-active vs active-passive
- [ ] **B20.7 Observability and incidents** ★★
  - Metrics, logs, traces; alerting on symptoms; postmortems
- [ ] **B20.8 Capacity planning** ★★
  - Back-of-envelope estimation; load testing; headroom

---

## Amendments to the original ask
- Added, because they come up in the same interviews
  - Networking fundamentals (B10) before security: TLS and HTTP underpin B18
  - Database fundamentals (B11) as its own track: ACID, isolation, indexes, replication, sharding
  - Messaging (B19) and distributed systems (B20): needed for outbox, saga, idempotency
  - Search (Elasticsearch) and Cassandra in NoSQL; numbers sheet (A3)
  - Schema migration (B4.8), testing (B3.8), observability, deployment
- Reordered
  - Spring MVC and Security come right after JPA, before microservices
  - API design (B8) before DDD (B9), so service boundaries can use the API vocabulary
  - Data modeling (B12) after DB fundamentals, so modeling choices can cite isolation and indexes
- Left out on purpose
  - Python core, data engineering, AI and agents: other tracks (`1A/`, `de-prep/`)
  - Kubernetes beyond basics; front end
