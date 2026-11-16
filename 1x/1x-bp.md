# 1x Plan — Backend Knowledge Map (1 week → 2 months)

- What this is: the study map for backend 八股 and senior-level depth
  - Part A: the **lenses**, the fixed questions every concept is examined through
  - Part B: the **map**, 22 tracks, three levels deep (track → topic → concepts)
- This file lists; it does not answer
  - Answers live in `x-md/` and the Java/Python projects, indexed in [x.md](x.md)
- Scope: Java backend, Spring, architecture, APIs, network, security, data, messaging, cloud
  - Out: AI and agents (`1A/`), data engineering (`de-prep/`), Python core, front end
- v2 · 2026-11-14 · reviewed against what already exists in `x-md/` (see [Changes in v2](#changes-in-v2))
- Mirror: Project `1D/X/1x-plan.md`; sprint days in `1D/1T/Senior Sprint Plan.md`

## Index
- [0. Strategy](#0-strategy)
  - [0.1 The real bottleneck](#01-the-real-bottleneck)
  - [0.2 Three passes](#02-three-passes)
  - [0.3 Scope check: does it fit the time](#03-scope-check-does-it-fit-the-time)
  - [0.4 Marks and how to track](#04-marks-and-how-to-track)
  - [0.5 W1 day by day](#05-w1-day-by-day)
- [Part A. Lenses](#part-a-lenses)
  - [A1. The core chain (say it aloud)](#a1-the-core-chain-say-it-aloud)
  - [A2. The full lens set](#a2-the-full-lens-set)
  - [A3. Which lenses lead, by kind of concept](#a3-which-lenses-lead-by-kind-of-concept)
  - [A4. Numbers sheet to build](#a4-numbers-sheet-to-build)
  - [A5. What each pass produces](#a5-what-each-pass-produces)
- [Part B. The map](#part-b-the-map)
- [Housekeeping noticed](#housekeeping-noticed)
- [Changes in v2](#changes-in-v2)

---

## 0. Strategy

### 0.1 The real bottleneck
- `x-md/` already holds about 1.8 MB of docs and four question banks
  - Kafka, Redis, REST, MongoDB, DynamoDB, Aurora, S3, messaging, load balancing: written
  - Banks: Antra, Beaconfire, the regrouped Q&A bank, the Java recite template
- So the gap is not material; it is **recall and spoken depth**
  - Reading more docs won't close it; answering aloud will
- Rule for this plan
  - A topic with a doc is never regenerated; it gets a short card and gets drilled
  - New docs only for topics marked **Gap**

### 0.2 Three passes
- Plain idea: go wide first, then deep, then keep it alive
- Pass 1, breadth (W1 for the ★★★ core; M1 for the rest)
  - Per topic: answer the 6-line core chain aloud ([A1](#a1-the-core-chain-say-it-aloud))
  - Source: the existing doc or bank section listed under **Have**
  - Output: a 6-line card; a self-score 0 / 1 / 2
  - Time box: ★★★ 20 min, ★★ 10 min, ★ 3 min
- Pass 2, depth (M1 → M2, ★★★ topics)
  - Per topic: fill the full lens table ([A2](#a2-the-full-lens-set)); 2–4 follow-ups answered L4 + L5
  - Output: lens table added to the topic's doc; numbers added to the numbers sheet
  - Time box: ★★★ 30 min
  - ★★ topics get pass 2 only on demand: scored 0, or asked in a real interview
- Pass 3, retrieval (runs alongside from day 2)
  - Re-answer every topic scored 0 or 1: next day, +3 days, +7 days
  - Use "drill X" in chat for a graded mock on one track
  - 10–15 min at the start of each study block

### 0.3 Scope check: does it fit the time
- Topic counts and time, computed from the map below

| Slice | Topics | Pass 1 | Pass 2 |
|---|---|---|---|
| W1 set (this week) | 29 | 9.7 h | later |
| All ★★★ | 66 | 22 h | 33 h |
| All ★★ | 62 | 10.3 h | on demand |
| All ★ | 11 | 0.6 h | none |
| **Total** | 139 | 33 h | 33 h |

- Time available (assumption: `x` keeps its 20% share after this week)
  - W1: about 12.5 h (2.5 h × 5 days, from the Sprint Plan)
  - M1 + M2: about 8 h/week × 8 weeks = 64 h
- Verdict
  - W1 fits: 9.7 h of pass 1 against 12.5 h; the rest goes to pass 3
  - Whole plan: 33 h + 33 h + about 8 h of retrieval = 74 h, against about 76 h
    - It fits, with almost no slack; one week under 8 h pushes M2 later
  - A full pass 2 on ★★ topics too would add 15.5 h and no longer fit: that is why it is on demand
  - If time runs short, cut in this order: Part VII, then ★ topics, then M2 ★★ topics
- What not to cut: pass 3
  - Without it, pass 1 decays within a week and the hours are lost

### 0.4 Marks and how to track
- Priority
  - ★★★ asked in most backend loops; pass 1 + pass 2
  - ★★ asked often; pass 1, pass 2 on demand
  - ★ recognize and name; pass 1 only
- Phase: `W1` this week · `M1` by mid-December · `M2` by mid-January
- Score in the box after each attempt: `[0]` can't answer · `[1]` first line only · `[2]` core chain complete
  - `[x]` = scored 2 on two different days
- Per track
  - **Have** = existing files to study from (paths under `x-md/`)
  - **Gap** = missing; generate with "gen 1x-plan B13.5"
  - **Home** = the group new docs go in

### 0.5 W1 day by day
- Matches the Sprint Plan days; 2.5 h each; answer aloud

| Day | Topics | Study from |
|---|---|---|
| D1 Sat 11-14 | B1.1, B1.2, B1.3, B1.7, B1.8, B1.9 | `0java/1java0.md`, `0java/1java.collections.md`, Beaconfire §1–5 |
| D2 Sun 11-15 | B3.1–B3.4, B4.2–B4.4, B2.1 | `01core/spring.md`, `solid.md`, Beaconfire §7–12, Antra "Spring Boot", `03db/01aurora.09` |
| D3 Mon 11-16 | B13.1–B13.5, B16.1–B16.3 | `03db/01aurora.07`, `.08`, `.12`; `02backend/4redis.md`; bank §7 |
| D4 Tue 11-17 | B9.1, B8.4, B19.1–B19.3, B21.1, B21.2 | `02backend/2rest101.md`, `3kafka.md`; bank §3–6, §8 |
| D5 Wed 11-18 | AI 八股 (in `1A/`) + re-answer every `[0]` and `[1]` | cards from D1–D4 |

- If the C3 AI round lands early in the week: swap D5's AI block with D3

---

## Part A. Lenses

- Plain idea: interviewers probe the same angles on every component
  - Fix the angles once; a gap then shows up as an empty lens, not a surprise question

### A1. The core chain (say it aloud)
- Six lines, in this order, for any concept; this is the pass 1 answer and the interview answer

| # | Line | Starts with |
|---|---|---|
| 1 | Problem | "It exists because …" |
| 2 | Mechanism | "Underneath, it …" |
| 3 | Guarantee | "It promises …, only when …" |
| 4 | Limit | "One instance handles about …; the first limit hit is …" |
| 5 | Break | "At 10× or on failure, what goes wrong first is …" |
| 6 | Choice | "I'd pick it when …; otherwise …" |

- 🗣 Template: "X exists because A. It works by B. It guarantees C only when D. Its limit is E; past that, F breaks first. I'd choose it over Y when Z."
- For a language or framework feature, line 4 becomes the **pitfall**: "the common mistake is …"

### A2. The full lens set
- 21 lenses in 6 groups; pass 2 fills all that apply
- ★★★ = always when it applies · ★★ = when relevant · ★ = senior extra
- "Core" marks the lens behind each line of the chain

**Group 1: Understand**

| # | Lens | Questions | Weight |
|---|---|---|---|
| L1 | Problem (core 1) | What pain did it remove? What came before, and why did that fail? | ★★★ |
| L2 | Mechanism (core 2) | How does it work underneath: data structures, algorithm, the steps of one request? | ★★★ |
| L3 | Guarantees (core 3) | What exactly does it promise (ordering, atomicity, durability), and under which conditions? | ★★★ |
| L4 | Knobs | Which 2–3 settings matter? What does each trade, and what decides its value? | ★★ |
| L5 | Pitfalls | How do people misuse it? What silently doesn't work? | ★★★ |

**Group 2: Numbers and scale**

| # | Lens | Questions | Weight |
|---|---|---|---|
| L6 | Capacity limits (core 4) | What does one instance / node / partition handle (QPS, size, connections)? Which limit is hit first? | ★★★ |
| L7 | Latency profile | What does one operation cost (memory vs disk vs network hop)? p50 vs p99? | ★★ |
| L8 | 10× test (core 5) | Load or data grows 10×, or one key gets most of it (skew): what breaks first? Scale up or out? Which instance size or tier next? | ★★★ |
| L9 | Cost | What is billed (request, hour, GB), and what makes it expensive? | ★ |

**Group 3: Correctness under concurrency**

| # | Lens | Questions | Weight |
|---|---|---|---|
| L10 | Concurrency | Two requests at once on the same data: what happens? Which lock, version, or isolation level protects it? | ★★★ |
| L11 | Idempotency and retries | The same request arrives twice: is the result still right? What is the key, and where is it stored? | ★★★ |
| L12 | Consistency model | Can a reader see stale data? Read-your-writes? Strong vs eventual, and what that costs | ★★ |

**Group 4: Failure**

| # | Lens | Questions | Weight |
|---|---|---|---|
| L13 | Failure modes (core 5) | What fails (node, network, dependency, overload), what the user sees, how it is detected | ★★★ |
| L14 | Recovery and redundancy | Replication, failover, backups, RPO/RTO; what is lost in a crash at the worst moment? | ★★ |
| L15 | Backpressure | Input exceeds capacity: queue, drop, throttle, or shed? | ★★ |

**Group 5: Operate and secure**

| # | Lens | Questions | Weight |
|---|---|---|---|
| L16 | Observability | Which 3 metrics show it's healthy? Which alarm fires first? | ★★ |
| L17 | Security | Who can call it? Data in transit and at rest? The common misconfiguration? | ★★ |
| L18 | Evolution | How to change it safely: migration, versioning, rolling deploy, backward compatibility | ★ |
| L21 | State | Stateful or stateless? Where does the state live (memory, session store, DB, token), who owns it, and what happens to it on restart, scale-out or failover? | ★★★ |

**Group 6: Decide and tell**

| # | Lens | Questions | Weight |
|---|---|---|---|
| L19 | Siblings and choice (core 6) | Alternatives? The deciding variable? Default pick, when to switch, when not to use it at all | ★★★ |
| L20 | My experience | Where did I use or meet it (JPMC, Databricks, own projects)? What decision was made, and why? "Not used" is a valid answer | ★★ |

- L20 is the bridge to behavioral answers
  - It turns "I know X" into "I chose X because …", the depth the BQ rounds probe

### A3. Which lenses lead, by kind of concept
- Not every lens fits; write "n/a" with a reason rather than padding

| Kind | Examples | Lead with | Usually n/a |
|---|---|---|---|
| Language feature | HashMap, generics, GC, threads | L2, L3, L5, L10 | L9, L14–L17 |
| Framework feature | IoC, AOP, `@Transactional`, JPA | L1, L2, L3, L5, L20 | L6–L9 |
| Data store | Postgres, DynamoDB, Redis | L2, L3, L6, L8, L10–L14, L19 | none |
| Network / edge component | LB, gateway, CDN | L2, L6, L8, L13, L15, L17 | L10 |
| Protocol / API style | REST, gRPC, TLS, OAuth2 | L1, L2, L3, L11, L17, L19 | L6, L9 |
| Pattern / architecture | aggregate, saga, outbox | L1, L3, L5, L10, L11, L13, L19 | L6, L7, L9 |

### A4. Numbers sheet to build
- Plain idea: L6–L8 need numbers; keep them in one sheet, each with source + date or "order of magnitude"
- File: `x-md/00numbers.md` (**Gap**)
- Rows to fill (not answered here)
  - Latency ladder: CPU cache, RAM, SSD read, same-AZ hop, cross-region hop
  - JVM: thread stack size, typical heap sizes, GC pause ranges by collector
  - Tomcat / Hikari: default thread pool and connection pool sizes
  - Postgres / MySQL: simple-query QPS per instance by size, max connections, typical replica lag, table size where partitioning starts to help
  - Aurora: replica count limit, failover time, storage limit
  - DynamoDB: per-partition read/write limits, item size, GSI count, transaction item limit
  - MongoDB: document size, shard-key limits
  - Redis: ops/s per node, memory per node in practice
  - Kafka: throughput per partition, partitions per broker, default message size
  - SQS / Kinesis: message size, retention, per-shard throughput
  - S3: request rate per prefix, object and part size limits
  - Lambda: timeout, memory, concurrency, payload limits
  - LB / API gateway: timeouts, payload limits
  - TLS handshake round trips (1.2 vs 1.3); typical HTTP header size
  - Estimation constants: seconds/day, QPS from DAU, storage per year

### A5. What each pass produces
- Pass 1: a **card** per topic, six lines, in `x-md/<group>/00cards.md`
  ```
  ### B16.3 Redis                                    score: 1 → 2
  1 Problem   …
  2 Mechanism …
  3 Guarantee …
  4 Limit     …
  5 Break     …
  6 Choice    …
  ```
  - The cards file is the pre-interview review: one screen per track
- Pass 2: a **lens table** at the end of the topic's doc
  ```
  ## Lens check
  | Lens | Answer (1–3 lines) |
  | L1 Problem | … |
  | L6 Capacity | … (numbers sheet row) |
  | L9 Cost | n/a: language feature |
  ```
  - Every ★★★ lens answered or marked n/a with a reason
  - L19 ends with "Default: X, unless Y"
  - Then 2–4 follow-up questions, each answered L4 + L5

---

## Part B. The map

- Order = study order
  - Parts I–II: what Java interviews ask first
  - Parts III–VII: follow a request, from design and API through the network and edge to data, async work, and the cloud it runs on

| Part | Tracks |
|---|---|
| I. Language and code | [B1 Java core](#b1-java-core) · [B2 Principles and patterns](#b2-design-principles-and-patterns) |
| II. Spring stack | [B3 Spring core and Boot](#b3-spring-core-and-spring-boot) · [B4 Data access](#b4-data-access-jdbc-jpa-hibernate-spring-data) · [B5 Spring MVC](#b5-spring-mvc-and-the-web-layer) · [B6 Spring Security](#b6-spring-security) |
| III. Architecture and APIs | [B7 DDD](#b7-domain-driven-design-and-code-structure) · [B8 Microservices](#b8-microservice-architecture) · [B9 API design](#b9-api-design-and-communication-protocols) |
| IV. Network, security, edge | [B10 Networking and OS](#b10-networking-and-os-essentials) · [B11 Security](#b11-security-and-security-protocols) · [B12 Edge and traffic](#b12-edge-and-traffic-lb-api-gateway-cdn-rate-limiting) |
| V. Data | [B13 DB fundamentals](#b13-database-fundamentals) · [B14 Data modeling](#b14-data-modeling) · [B15 Relational](#b15-relational-databases) · [B16 Cache](#b16-cache-and-in-memory-stores) · [B17 NoSQL](#b17-nosql-databases) · [B18 Choosing a database](#b18-choosing-a-database) |
| VI. Async and distributed | [B19 Messaging](#b19-messaging-and-async-processing) · [B20 Distributed systems](#b20-distributed-systems-and-reliability) |
| VII. Cloud and delivery | [B21 AWS core](#b21-aws-core-services) · [B22 Containers, CI/CD, IaC](#b22-containers-cicd-and-iac) |

---

### Part I. Language and code

#### B1. Java core
- Have: `0java/1java0.md` (recite template), `0java/1java.collections.md`, `0java/1Beaconfire…` §1–6, `0java/1antra0.md` "Java (53)", `02backend/1concurrency.md` (quick walkthrough), `1concurrency-c.md`
- Gap: B1.5 (reflection, annotations, proxies); cards
- Home: `00java`

- [ ] **B1.1 OOP fundamentals** ★★★ W1
  - Class vs object; constructors; `static` vs instance; initialization order
  - Encapsulation; access modifiers
  - Inheritance: `extends`, `super`, constructor chaining
  - Polymorphism: overriding vs overloading, dynamic dispatch
  - Abstract class vs interface; default methods
  - Composition over inheritance; `final` on class / method / variable
  - Enums; nested and anonymous classes
- [ ] **B1.2 Object contract** ★★★ W1
  - `==` vs `equals`; `equals` / `hashCode` contract and what breaks in a HashMap
  - `Comparable` vs `Comparator`
  - Immutability; records
  - `String` immutability, string pool, `StringBuilder`
  - Primitives vs wrappers, autoboxing, the Integer cache
  - Pass-by-value of references
- [ ] **B1.3 Collections** ★★★ W1
  - Hierarchy: `List`, `Set`, `Map`, `Queue`, `Deque`
  - `ArrayList` vs `LinkedList`: growth and complexity
  - `HashMap` internals: hashing, buckets, treeification, resize, load factor
  - `LinkedHashMap` (LRU), `TreeMap`, `PriorityQueue`
  - Fail-fast iterators, `ConcurrentModificationException`
  - `ConcurrentHashMap`, `CopyOnWriteArrayList`, `BlockingQueue`
- [ ] **B1.4 Generics** ★★ M1
  - Type erasure; bounded types; wildcards and PECS
  - Why `List<Integer>` is not a `List<Number>`
- [ ] **B1.5 Reflection, annotations, dynamic proxies** ★★ M1
  - Reflection API and its cost; annotations and retention
  - JDK dynamic proxy vs bytecode generation: the base of Spring AOP (B3.3)
- [ ] **B1.6 Exceptions** ★★ M1
  - Checked vs unchecked; `Error` vs `Exception`
  - try-with-resources; `finally` pitfalls
  - Exception translation across layers
- [ ] **B1.7 Concurrency** ★★★ W1
  - Thread lifecycle; `Runnable` / `Callable`
  - Race condition, visibility, atomicity
  - `synchronized`, reentrancy; `volatile` and happens-before
  - Deadlock: the four conditions and prevention
  - Thread pools: `ThreadPoolExecutor` parameters, queue, rejection policies
  - `CompletableFuture`; `ReentrantLock`, `ReadWriteLock`
  - Atomics and CAS; `CountDownLatch`, `Semaphore`
  - `ThreadLocal` and its leak in pools
- [ ] **B1.8 JVM and memory** ★★★ W1
  - Memory areas: heap (young / old), stack, metaspace
  - GC: reachability, generations; G1 vs ZGC vs Parallel (pause vs throughput)
  - `OutOfMemoryError` types; memory leak patterns
  - Diagnosing: heap dump, thread dump, GC logs
  - Class loading and parent delegation
- [ ] **B1.9 Java 8+ features** ★★★ W1
  - Lambdas, functional interfaces, method references
  - Streams: laziness, collectors, parallel-stream pitfalls
  - `Optional` usage rules
- [ ] **B1.10 Modern Java (17–21)** ★★ M1
  - Records, sealed classes, pattern matching, switch expressions
  - Virtual threads: what changes, pinning
- [ ] **B1.11 Concurrency internals** ★ M2
  - AQS, lock states, `StampedLock`, `LongAdder`; the Java memory model in detail
- [ ] **B1.12 I/O and serialization** ★ M2
  - Blocking I/O vs NIO; Java serialization pitfalls; Jackson basics

#### B2. Design principles and patterns
- Have: `01core/solid.md`, `01core/design-principles.md`, `01core/1design-patterns.md` (23 GoF + non-GoF map), `02backend/8low-level-design.md`; code in `_01core_01principles`
- Gap: none; cards only
- Home: `01core`

- [ ] **B2.1 SOLID** ★★★ W1
  - SRP, OCP, LSP, ISP, DIP: violation vs fix, one real example each
- [ ] **B2.2 General principles** ★★ M1
  - DRY, KISS, YAGNI, law of Demeter, cohesion and coupling, fail fast
- [ ] **B2.3 Creational patterns** ★★ M1
  - Singleton (thread-safe forms), Factory Method, Abstract Factory, Builder
- [ ] **B2.4 Structural patterns** ★★ M1
  - Adapter, Decorator, Proxy, Facade, Composite
- [ ] **B2.5 Behavioral patterns** ★★ M1
  - Strategy, Observer, Template Method, Chain of Responsibility, Command, State
- [ ] **B2.6 Patterns inside Spring and the JDK** ★★ M1
  - Proxy (AOP), Template Method (`JdbcTemplate`), Factory (`BeanFactory`), Observer (events), Decorator (I/O streams)
- [ ] **B2.7 Remaining GoF** ★ M2
  - Prototype, Bridge, Flyweight, Iterator, Visitor, Mediator, Memento, Interpreter

### Part II. Spring stack

#### B3. Spring core and Spring Boot
- Have: `01core/spring.md`, `01core/spring-boot.md`; Beaconfire §10, §12; Antra "Spring Boot (28)", "Testing (13)"
- Gap: bean lifecycle and scopes (B3.2), transactions as a Spring topic (B3.4 lives only in the Aurora doc), testing (B3.7)
- Home: `06framework`

- [ ] **B3.1 IoC and DI** ★★★ W1
  - IoC vs DI vs DIP: three different things
  - Constructor vs setter vs field injection
  - `BeanFactory` vs `ApplicationContext`
  - Component scanning, stereotypes, `@Configuration` + `@Bean`
  - `@Autowired` resolution, `@Qualifier`, `@Primary`
  - Circular dependencies
- [ ] **B3.2 Bean lifecycle and scopes** ★★★ W1
  - Instantiate → populate → `BeanPostProcessor` → init → destroy
  - `@PostConstruct`, `@PreDestroy`
  - Singleton, prototype, request, session; prototype inside a singleton
  - Thread safety of singleton beans
- [ ] **B3.3 AOP** ★★★ W1
  - Aspect, advice, join point, pointcut
  - JDK proxy vs CGLIB
  - Self-invocation trap; final and private methods
  - Uses: transactions, logging, security, caching, retries
- [ ] **B3.4 Transactions** ★★★ W1
  - `@Transactional` = proxy + `PlatformTransactionManager`
  - Propagation: REQUIRED, REQUIRES_NEW, NESTED
  - Isolation settings; rollback rules; `readOnly`
  - Pitfalls: self-invocation, swallowed exceptions, long transactions
  - Transactions and messaging: why the outbox exists (B19.5)
- [ ] **B3.5 Spring Boot** ★★★ M1
  - Spring vs Spring Boot
  - Auto-configuration, `@Conditional*`, starters
  - Config: profiles, `@ConfigurationProperties`, precedence
  - Embedded server, fat jar
  - Actuator: health, metrics, readiness vs liveness
- [ ] **B3.6 Events, async, scheduling, caching** ★ M2
  - `@EventListener`, `@TransactionalEventListener`, `@Async`, `@Scheduled`, `@Cacheable`
- [ ] **B3.7 Testing** ★★ M1
  - Unit vs slice (`@WebMvcTest`, `@DataJpaTest`) vs `@SpringBootTest`
  - Mockito, `@MockBean`; Testcontainers
  - Test pyramid; contract tests

#### B4. Data access: JDBC, JPA, Hibernate, Spring Data
- Have: `03db/01aurora.06pools-rds-proxy.md`, `.09transactions-propagation.md`, `.11crud-batch-upsert.md`, `.12locking.md`, `.14pagination.md`; Beaconfire §8; `02backend/4persistence.md` (section 6 partitioning, merged 2026-11-15), `4database.md`
- Gap: JPA / Hibernate itself (B4.2–B4.6) has no doc
- Home: `06framework`

- [ ] **B4.1 JDBC and connection pools** ★★ M1
  - `DataSource`, `PreparedStatement` (injection, plan reuse)
  - HikariCP: pool size reasoning, timeouts
  - `JdbcTemplate`, batch updates
- [ ] **B4.2 JPA core** ★★★ W1
  - JPA (spec) vs Hibernate (implementation) vs Spring Data JPA (repositories)
  - Entity; `@Id` strategies (IDENTITY vs SEQUENCE vs UUID) and batch inserts
  - Persistence context, first-level cache
  - Entity states: transient, managed, detached, removed
  - Dirty checking and flush
- [ ] **B4.3 Relationships and fetching** ★★★ W1
  - `@OneToMany`, `@ManyToOne`, `@ManyToMany`; owning side, `mappedBy`
  - Cascade types; orphan removal
  - Lazy vs eager; `LazyInitializationException`; open-session-in-view
  - N+1 and its fixes: fetch join, `@EntityGraph`, batch size
- [ ] **B4.4 Spring Data JPA** ★★★ W1
  - Repositories; derived queries; `@Query` (JPQL vs native)
  - `save()` semantics: persist vs merge
  - Pagination and sorting; projections
  - `@Modifying` queries; auditing
- [ ] **B4.5 Locking in JPA** ★★★ M1
  - Optimistic locking with `@Version`; handling the conflict
  - Pessimistic locks and the SQL they emit
  - Lost-update scenarios
- [ ] **B4.6 Performance** ★★ M1
  - Second-level cache; batch settings; reading the generated SQL
  - Inheritance mapping strategies
- [ ] **B4.7 Schema migration** ★★ M1
  - Flyway / Liquibase; expand-and-contract; zero-downtime column changes
- [ ] **B4.8 Alternatives** ★ M2
  - MyBatis, jOOQ, plain JDBC: when each beats JPA

#### B5. Spring MVC and the web layer
- Have: Beaconfire §11; `02backend/2rest101.md` (REST side)
- Gap: request flow and error handling doc
- Home: `06framework`

- [ ] **B5.1 Request flow** ★★★ M1
  - Servlet container → `DispatcherServlet` → handler mapping → controller → message converter
  - Thread-per-request; Tomcat thread pool limits
- [ ] **B5.2 Controllers and validation** ★★ M1
  - `@RestController`, mappings, `ResponseEntity`
  - Bean Validation; DTOs vs entities at the boundary
- [ ] **B5.3 Errors and cross-cutting** ★★ M1
  - `@ControllerAdvice`; problem-details error format
  - Filter vs interceptor vs AOP: order and use
  - CORS
- [ ] **B5.4 Reactive web** ★ M2
  - WebFlux vs MVC; when reactive pays off; virtual threads as the alternative

#### B6. Spring Security
- Have: Antra "Spring Security + JWT (23)"; Beaconfire §12; bank §9
- Gap: architecture doc
- Home: `06framework` · read B11.1–B11.3 first

- [ ] **B6.1 Architecture** ★★ M1
  - Filter chain, `SecurityFilterChain`, `SecurityContext`
  - Authentication flow: `AuthenticationManager`, providers
- [ ] **B6.2 Common setups** ★★★ M1
  - Session login vs stateless JWT
  - OAuth2 resource server; OAuth2 login
  - Password storage (BCrypt)
- [ ] **B6.3 Authorization** ★★ M1
  - URL rules vs method security (`@PreAuthorize`); roles vs authorities
- [ ] **B6.4 Web threats** ★ M2
  - CSRF (when needed), CORS vs CSRF, security headers

### Part III. Architecture and APIs

#### B7. Domain-driven design and code structure
- Have: `ddd/2stripe`, `ddd/2stripe2` (sample projects); 1x code uses hexagonal layers
- Gap: concept doc
- Home: `07arch` (proposed)

- [ ] **B7.1 Tactical DDD** ★★★ M1
  - Entity vs value object
  - Aggregate and aggregate root; one transaction per aggregate
  - Repository; domain service vs application service
  - Domain events
- [ ] **B7.2 Architecture styles** ★★★ M1
  - Layered vs hexagonal (ports and adapters) vs clean
  - Dependency direction; where framework annotations belong
  - Package-by-layer vs package-by-feature
- [ ] **B7.3 Strategic DDD** ★★ M1
  - Subdomains (core, supporting, generic)
  - Bounded context; ubiquitous language
  - Context map; anti-corruption layer
- [ ] **B7.4 From model to services** ★★ M2
  - Bounded context → service boundary
  - CQRS; event sourcing (know the cost)

#### B8. Microservice architecture
- Have: bank §8; `02backend/1dissys.md`, `5cloud-availability.md`, `5observability.md`, `5performance-capacity.md`, `6ecs.md`, `6eks.md`, `5docker.md`
- Gap: none large; cards
- Home: `07arch` (proposed)

- [ ] **B8.1 Monolith vs microservices** ★★★ M1
  - Modular monolith; when splitting pays; the distributed-monolith trap
- [ ] **B8.2 Communication** ★★★ M1
  - Sync (REST, gRPC) vs async (events, queues)
  - Choreography vs orchestration
- [ ] **B8.3 Data ownership** ★★★ M1
  - Database per service
  - Cross-service queries: API composition, read models
  - Saga, outbox (B19.5, B20.3)
- [ ] **B8.4 Resilience patterns** ★★★ W1
  - Timeouts; retries with backoff and jitter; retry storms
  - Circuit breaker, bulkhead, fallback
  - Idempotent endpoints as the prerequisite
- [ ] **B8.5 Platform pieces** ★★ M1
  - Service discovery, config, API gateway (B12.2), service mesh
- [ ] **B8.6 Observability** ★★ M1
  - Correlation IDs, tracing (OpenTelemetry), structured logs, RED metrics
- [ ] **B8.7 Deployment** ★★ M1
  - Rolling, blue-green, canary; feature flags; backward-compatible contracts

#### B9. API design and communication protocols
- Have: `2backend/2api-ds.md` (API design, contracts, estimation; merged 2026-11-15), `2rest101.md`, `2rest102.md`, `2rest-gql.md`, `2rest-grpc-websocket.md`; bank §10 (GraphQL)
- Gap: none; cards
- Home: `07arch` (proposed)

- [ ] **B9.1 REST** ★★★ W1
  - Resources and URIs; methods: safe vs idempotent; PUT vs PATCH
  - Status codes that matter
  - Idempotency keys for POST
  - Pagination: offset vs cursor
  - Versioning; backward compatibility
  - Error format; long-running operations (202 + status resource)
  - Conditional requests (ETag) and caching headers
- [ ] **B9.2 Real-time and push** ★★★ M1
  - Polling, long polling, SSE, WebSocket: mechanism, connection cost, scaling the connection layer
  - Webhooks: signing, retries, idempotent receivers
- [ ] **B9.3 GraphQL** ★★ M1
  - Schema, queries, mutations, resolvers
  - N+1 and DataLoader; caching and rate-limit difficulty
- [ ] **B9.4 gRPC** ★★ M1
  - Protobuf, HTTP/2, streaming modes
  - Schema evolution; deadlines; load balancing long-lived connections
- [ ] **B9.5 Choosing a style** ★★★ M1
  - REST vs GraphQL vs gRPC vs messaging: the deciding variables
- [ ] **B9.6 Async contracts** ★ M2
  - Event schema design, schema registry, versioning events

### Part IV. Network, security, edge

#### B10. Networking and OS essentials
- Have: none in 1x (TechPrep / BBG videos listed in `1sd/1ytb-cata.md` §3)
- Gap: the whole track
- Home: `08netsec` (proposed)

- [ ] **B10.1 TCP and UDP** ★★★ M1
  - Handshake and teardown
  - Reliability; flow control vs congestion control
  - Head-of-line blocking; when UDP wins
- [ ] **B10.2 HTTP** ★★★ M1
  - HTTP/1.1 keep-alive; HTTP/2 multiplexing; HTTP/3 over QUIC
  - Caching headers; cookies
- [ ] **B10.3 TLS** ★★★ M1
  - Handshake (1.2 vs 1.3); certificates and chain of trust
  - mTLS; where TLS terminates
- [ ] **B10.4 DNS** ★★ M1
  - Resolution path, TTLs; DNS-based load balancing and failover
- [ ] **B10.5 The full request** ★★★ M1
  - "What happens when you type a URL", end to end
- [ ] **B10.6 Connections in practice** ★★ M1
  - Connection pooling; connect vs read timeouts; idle-timeout mismatches
- [ ] **B10.7 OS essentials** ★★ M2
  - Process vs thread; context switch
  - Virtual memory; file descriptors
  - Blocking vs non-blocking I/O; epoll and event loops
- [ ] **B10.8 Layer models** ★ M2
  - OSI vs TCP/IP; NAT, ports, sockets

#### B11. Security and security protocols
- Have: `02backend/7security.md` (stack from keys to SSO), `7security-c.md` (Spring, FastAPI, Flask, Angular code); bank §9; `03db/01aurora.05iam-auth-tls.md`, `03s3.06encryption.md`
- Gap: OAuth2 / OIDC / JWT doc
- Home: `08netsec` (proposed)

- [ ] **B11.1 AuthN vs AuthZ; sessions vs tokens** ★★★ M1
  - Session + cookie vs token; where each breaks
- [ ] **B11.2 OAuth 2.0 and OIDC** ★★★ M1
  - Roles; authorization code + PKCE; client credentials; refresh tokens
  - ID token vs access token; scopes
- [ ] **B11.3 JWT** ★★★ M1
  - Structure; HS256 vs RS256; validation steps; the revocation problem
- [ ] **B11.4 Data protection** ★★ M1
  - Encryption at rest; KMS envelope encryption; secrets management
  - Hashing vs encryption; password hashing
- [ ] **B11.5 Access control models** ★★ M1
  - RBAC, ABAC; least privilege; IAM policy evaluation
- [ ] **B11.6 Common attacks** ★★ M1
  - Injection, XSS, CSRF, SSRF, broken access control; mitigations
- [ ] **B11.7 PKI and service-to-service** ★★ M2
  - CA hierarchy, rotation, mTLS between services
- [ ] **B11.8 API security** ★★ M2
  - API keys vs tokens; webhook signatures; audit logs

#### B12. Edge and traffic: LB, API gateway, CDN, rate limiting
- Have: `02backend/5lb-api-gateway.md`, `5cloud-equivalents.md`; `1sd/hello-interview/hi02` (rate limiter)
- Gap: CDN; cards
- Home: `08netsec` (proposed)

- [ ] **B12.1 Load balancers** ★★★ M1
  - L4 vs L7; algorithms
  - Health checks; connection draining; sticky sessions
  - Long-lived connections (WebSocket)
- [ ] **B12.2 Reverse proxy and API gateway** ★★★ M1
  - Auth, rate limiting, routing; TLS termination
  - Gateway vs LB vs service mesh
- [ ] **B12.3 CDN** ★★★ M1
  - Edge caching, cache keys, TTLs, invalidation
  - Static vs dynamic content; signed URLs
- [ ] **B12.4 Rate limiting** ★★★ M1
  - Token bucket, leaky bucket, fixed vs sliding window
  - Distributed limiting with Redis; 429 + Retry-After
- [ ] **B12.5 Autoscaling** ★★ M2
  - Horizontal vs vertical; signals; warm-up; stateless services

### Part V. Data

#### B13. Database fundamentals
- Have: `03db/01aurora.07mvcc-vacuum.md`, `.08isolation-levels.md`, `.12locking.md`; `02backend/4persistence.md`, `4storage.md`, `1dissys.md` (9.8 isolation, 9.9 conflict resolution); Beaconfire §9; bank §7
- Gap: indexes doc, SQL fluency (B13.5), replication and sharding as general topics
- Home: `03db`

- [ ] **B13.1 ACID** ★★★ W1
  - Atomicity (undo), consistency, isolation, durability (WAL, fsync)
- [ ] **B13.2 Isolation levels and anomalies** ★★★ W1
  - Dirty read, non-repeatable read, phantom, lost update, write skew
  - Levels; Postgres vs MySQL defaults; MVCC snapshots
- [ ] **B13.3 Locking** ★★★ W1
  - Row vs table; shared vs exclusive
  - `SELECT … FOR UPDATE`, `SKIP LOCKED`
  - DB deadlocks; optimistic vs pessimistic
- [ ] **B13.4 Indexes** ★★★ W1
  - B-tree vs hash vs LSM-tree; clustered vs secondary
  - Composite indexes and leftmost prefix; covering indexes
  - When an index hurts; reading `EXPLAIN`
- [ ] **B13.5 SQL fluency** ★★★ W1
  - Joins (inner, left, self); `GROUP BY` + `HAVING`
  - Window functions: `ROW_NUMBER`, `RANK`, running totals
  - CTEs; subquery vs join; top-N per group
  - NULL semantics
- [ ] **B13.6 Replication** ★★★ M1
  - Leader-follower; sync vs async; replica lag and read-your-writes
  - Multi-leader, leaderless (quorums)
  - Failover and split brain
- [ ] **B13.7 Partitioning and sharding** ★★★ M1
  - Range vs hash vs directory
  - Shard key; hot partitions; resharding; consistent hashing
  - Cross-shard queries and transactions
- [ ] **B13.8 Query execution** ★★ M1
  - Planner and statistics; join algorithms (nested loop, hash, merge)
- [ ] **B13.9 CAP and PACELC** ★★ M1
  - What CAP says and doesn't; why PACELC is more useful
- [ ] **B13.10 Durability and backup** ★★ M2
  - WAL and checkpoints; backups, PITR; RPO / RTO

#### B14. Data modeling
- Have: `02backend/4data-modeling.md` (root), `4data-rds-ds.md` (relational), `4data-nosql-ds.md` (DynamoDB, MongoDB, Cassandra, S3), `4data-redis-ds.md` (cache keys), `4data-caching.md`, `03db/02dynamodb.05single-table-design.md`, `04mongodb.03schema-design.md`
- Gap: relational modeling doc
- Home: `03db`

- [ ] **B14.1 Access-pattern-first modeling** ★★★ M1
  - List the queries and invariants first; tables and indexes follow
  - Relational vs NoSQL modeling: joins vs pre-joined items
- [ ] **B14.2 Entities and relations** ★★★ M1
  - Entities from requirements; 1:1, 1:N, N:M
  - ER diagram to tables
- [ ] **B14.3 Keys and IDs** ★★★ M1
  - Natural vs surrogate; sequence vs UUID v4 vs v7 vs Snowflake
  - Unique constraints as business invariants
- [ ] **B14.4 Normalization** ★★ M1
  - 1NF–3NF in practice; when to denormalize
- [ ] **B14.5 Common modeling problems** ★★ M2
  - Soft delete, audit history, temporal data
  - Money, time zones, enums, JSON columns
  - Multi-tenancy; hierarchies; counters

#### B15. Relational databases
- Have: `03db/01aurora.*` (17 files); code slice `_03db_01aurora`
- Gap: Postgres vs MySQL comparison
- Home: `03db`

- [ ] **B15.1 Postgres** ★★★ M1
  - MVCC with tuple versions; VACUUM and bloat
  - Index types: B-tree, GIN, GiST, BRIN
  - JSONB; declarative partitioning
  - Process-per-connection and PgBouncer
- [ ] **B15.2 Scaling a relational DB** ★★★ M1
  - Order: queries and indexes → pooling → read replicas → cache → bigger instance → partitioning → sharding
  - The point where you leave relational (B18)
- [ ] **B15.3 Aurora / RDS** ★★ M1
  - Shared storage, 6 copies in 3 AZs; reader endpoint; failover; Serverless v2
- [ ] **B15.4 MySQL (InnoDB)** ★★ M2
  - Clustered primary key; gap locks; REPEATABLE READ default; binlog
- [ ] **B15.5 Postgres vs MySQL** ★★ M2
  - Practical differences; default pick

#### B16. Cache and in-memory stores
- Have: `02backend/4redis.md`, `4redis-c.md`, `4data-redis-ds.md`
- Gap: none; cards
- Home: `03db`

- [ ] **B16.1 Caching patterns** ★★★ W1
  - Cache-aside, read-through, write-through, write-behind
  - TTL and invalidation; cache vs DB consistency
- [ ] **B16.2 Cache failure modes** ★★★ W1
  - Stampede; penetration; avalanche; hot keys; and the fix for each
- [ ] **B16.3 Redis** ★★★ W1
  - Single-threaded event loop; why it is fast
  - Data types and one use each
  - Persistence: RDB vs AOF; durability limits
  - Eviction policies
  - Replication, Sentinel, Cluster (hash slots)
  - Uses: session, rate limiter, leaderboard, lock, pub/sub
- [ ] **B16.4 Where to cache** ★★ M1
  - Browser, CDN, gateway, application, DB buffer pool
- [ ] **B16.5 Redis vs Memcached vs local cache** ★★ M2
  - Caffeine; multi-level caching

#### B17. NoSQL databases
- Have: `03db/02dynamodb.*` (13 files), `03db/04mongodb.*` (16 files), `02backend/4mongodb.md`, `4mongodb-c.md`; bank §5
- Gap: Cassandra, Elasticsearch
- Home: `03db`

- [ ] **B17.1 NoSQL families** ★★★ M1
  - Key-value, wide-column, document, search, graph, time-series: what each optimizes
- [ ] **B17.2 DynamoDB** ★★★ M1
  - Partition key and sort key; item collections
  - Partitions and per-partition throughput; hot partitions
  - LSI vs GSI; GSI eventual consistency
  - Query vs Scan; pagination
  - Conditional writes; transactions
  - Capacity modes; TTL; Streams
  - Single-table design
- [ ] **B17.3 MongoDB** ★★ M1
  - Embedding vs referencing; document size limit
  - Indexes; aggregation pipeline
  - Replica sets; write and read concern
  - Sharding and shard key
- [ ] **B17.4 Elasticsearch / OpenSearch** ★★ M1
  - Inverted index, analyzers; shards and replicas; near-real-time refresh
  - Keeping it in sync with the source of truth (CDC)
- [ ] **B17.5 Cassandra** ★★ M2
  - Ring, replication factor, tunable consistency
  - LSM storage, compaction, tombstones
- [ ] **B17.6 Others** ★ M2
  - Time-series, graph, NewSQL (Spanner, CockroachDB)

#### B18. Choosing a database
- Have: `02backend/4storage-by-question.md`, `4storage.md`, `03db/*.98tradeoffs.md`
- Gap: the comparison matrix (planned as `04dissys.01tech-choice`, task X-026)
- Home: `04dissys`

- [ ] **B18.1 Decision dimensions** ★★★ M1
  - Data shape and relations; query patterns
  - Consistency and transaction scope
  - Read/write ratio, volume, latency target
  - Scale-out need; ops burden; cost
- [ ] **B18.2 Comparison matrix** ★★★ M1
  - Rows: Postgres, MySQL, DynamoDB, MongoDB, Cassandra, Redis, Elasticsearch
  - Columns: B18.1 dimensions + capacity (L6) + 10× path (L8) + main failure (L13)
- [ ] **B18.3 Interview defaults** ★★★ M1
  - "Postgres unless …"; when DynamoDB; when to add a cache or search
- [ ] **B18.4 Polyglot persistence** ★★ M2
  - One source of truth + derived stores via CDC / events

### Part VI. Async and distributed

#### B19. Messaging and async processing
- Have: `02backend/3kafka.md`, `3kafka-c.md`, `3messaging-review.md`, `3messaging.md`, `3messaging-zh.md`, `3messaging-async.md`; bank §3; Antra "Kafka (10)"
- Gap: none in docs; code slices planned (X-015, X-016, X-025)
- Home: `02messaging`

- [ ] **B19.1 Queue vs log vs pub/sub** ★★★ W1
  - SQS vs Kafka vs SNS: consumption model, retention, replay
- [ ] **B19.2 Delivery semantics** ★★★ W1
  - At-most-once, at-least-once, "exactly-once" and what it really means
  - Idempotent consumers; dedup keys
- [ ] **B19.3 Kafka** ★★★ W1
  - Topics, partitions, offsets, consumer groups, rebalancing
  - Replication: leader, ISR, `acks`, `min.insync.replicas`
  - Ordering per partition; key choice
  - Idempotent and transactional producers
- [ ] **B19.4 SQS / SNS** ★★ M1
  - Visibility timeout, DLQ, FIFO groups, SNS → SQS fan-out
- [ ] **B19.5 Patterns** ★★★ M1
  - Transactional outbox; CDC
  - Retry topics, DLQ handling, poison messages
  - Consumer lag and backpressure
- [ ] **B19.6 Stream processing** ★ M2
  - Windows, watermarks, state; Kinesis basics

#### B20. Distributed systems and reliability
- Have: `02backend/1dissys.md` (now with clocks, consensus, fencing, sagas), `1dissys-c.md`, `5cloud-availability.md`; `03db/01aurora.10retries-idempotency.md`
- Gap: none large; cards
- Home: `04dissys`

- [ ] **B20.1 Idempotency end to end** ★★★ M1
  - Keys, dedup store, retention window; idempotent vs exactly-once
- [ ] **B20.2 Distributed transactions** ★★★ M1
  - 2PC and its blocking problem; saga with compensations; outbox
- [ ] **B20.3 Consensus and coordination** ★★ M2
  - Raft in outline; quorum vs consensus
  - etcd / ZooKeeper uses: leader election, locks, config
- [ ] **B20.4 Distributed locks and leases** ★★ M2
  - Lease + fencing token; Redis vs DB vs ZooKeeper locks
- [ ] **B20.5 Reliability engineering** ★★ M2
  - SLI / SLO / error budget; graceful degradation; load shedding
  - Multi-AZ vs multi-region; active-active vs active-passive
- [ ] **B20.6 Time and ordering** ★★ M2
  - Clock skew; logical clocks; why last-write-wins loses data
- [ ] **B20.7 Capacity planning** ★★ M2
  - Back-of-envelope estimation; load testing; headroom

### Part VII. Cloud and delivery

#### B21. AWS core services
- Have: bank §4 (Lambda), §5 (DynamoDB, Aurora), §6 (other services); `03db/03s3.*`; Terraform modules in `terraform/`
- Gap: compute and IAM / VPC cards
- Home: `09cloud` (proposed)

- [ ] **B21.1 Compute choices** ★★★ W1
  - EC2 vs ECS / Fargate vs Lambda: the deciding variables
  - Lambda: cold start, concurrency, timeout, triggers, idempotent handlers
- [ ] **B21.2 IAM** ★★★ W1
  - Users vs roles; assume-role; policy evaluation; least privilege
- [ ] **B21.3 VPC networking** ★★ M1
  - Subnets, route tables, NAT, security group vs NACL, VPC endpoints
- [ ] **B21.4 Integration services** ★★ M1
  - SQS, SNS, EventBridge, Step Functions: which for what
- [ ] **B21.5 S3** ★★ M1
  - Consistency, request rate, multipart, presigned URLs, lifecycle
- [ ] **B21.6 Observability** ★★ M1
  - CloudWatch metrics, logs, alarms; X-Ray
- [ ] **B21.7 High availability** ★★ M2
  - Multi-AZ, auto scaling groups, Route 53 failover

#### B22. Containers, CI/CD, and IaC
- Have: bank §11; `ddd/k8s`; Terraform rules in `1tf.md`
- Gap: Kubernetes basics doc
- Home: `09cloud` (proposed)

- [ ] **B22.1 Docker** ★★ M1
  - Image vs container; layers; multi-stage builds; container vs VM
- [ ] **B22.2 Kubernetes basics** ★★ M2
  - Pod, deployment, service, ingress; config and secrets
  - Probes; rolling update; HPA; requests vs limits
- [ ] **B22.3 CI/CD** ★★ M1
  - Pipeline stages; artifact promotion; rollback; deployment strategies (B8.7)
- [ ] **B22.4 Terraform** ★★ M2
  - State and locking; modules; plan vs apply; drift

---

## Housekeeping noticed
- Not changed; for you to decide after the interviews
- Duplicate file: `x-md/0java/1.Interview Q&A Bank — Regrouped from Ar.md` and `x-md/0java/2.antra2.md` are byte-identical
- `x-md/0java/` and `x-md/02backend/` don't follow the `AGENTS.md` §4 naming
  - Group folder should be `00java`; `02backend` is not a group in §4.1
  - 26 files in `02backend` keep their old `1sde` names
- Proposed new groups for tracks with no home (need your word before any rename)
  - `07arch`: DDD, microservices, API design
  - `08netsec`: networking, security, edge
  - `09cloud`: AWS, containers, CI/CD

## Changes in v2
- Strategy
  - Added: the three passes, the time budget, and the scope check with real counts
  - Added: W1 day-by-day table tied to the files you already have
  - Changed: existing docs are drilled, not regenerated; every track now lists Have / Gap
- Lenses
  - Added: the 6-line core chain for speaking
  - Added: L5 Pitfalls and L20 My experience; skew folded into the 10× test
- Map
  - Reordered: DDD → microservices → API design (model, then boundaries, then contracts)
    - v1 had API design before DDD; that was the wrong way round
  - Reordered: networking → security → edge moved before data, following a request's path
  - Added tracks: B21 AWS core, B22 containers / CI/CD / IaC
  - Added topics: SQL fluency (B13.5), reflection and proxies (B1.5), OS essentials (B10.7), query execution (B13.8)
  - Split: common Java topics from rarely asked internals (B1.11); common GoF from the rest (B2.7)
  - Every topic now carries a phase
