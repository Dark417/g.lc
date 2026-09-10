# Java 快速背诵模板(中英结合)

> 用法:每条 = `English term` → 一句话标准答案 → ⚠️陷阱 / follow-up。
> 🔥 = 高频必背  ⚠️ = 易错点  【码】= 能现场手写

## Index

- [1. 语言基础 Language Fundamentals](#java-section-1)
- [2. 对象契约 Object Contracts](#java-section-2)
- [3. 集合 Collections](#java-section-3)
- [4. 异常 Exception](#java-section-4)
- [5. 泛型 Generics](#java-section-5)
- [6. Java 8+ 函数式](#java-section-6)
- [7. 并发 Concurrency 🔥(bank 深挖区)](#java-concurrency)
- [8. JVM 🔥](#java-section-8)
- [背诵优先级(时间不够就按这个背)](#java-section-9)
- [References](#java-section-10)

---

<a id="java-section-1"></a>

## 1. 语言基础 Language Fundamentals

- 🔥 **pass-by-value**:Java 只有值传递。传对象时传的是**引用的副本**,方法内改对象内容会生效,但重新赋值引用不影响外部。
- 🔥 **String immutable**:`String` 是 `final class` + 内部 `char[]` 不可变。好处:线程安全、可缓存 hash、可放 **string pool(常量池)**。
  - ⚠️ `"a"+"b"` 编译期直接优化成 `"ab"`;`new String("a")` 在堆上新建对象,不进池。
  - `StringBuilder`(非线程安全,快)vs `StringBuffer`(`synchronized`,线程安全)。
- 🔥 **final / finally / finalize**
  - `final`:变量=常量、方法=不可 override、类=不可继承。
  - `finally`:一定执行(除非 `System.exit()` / JVM 崩)。
  - `finalize`:GC 前回调,**已废弃**,别用。
- 🔥 **overload vs override**:overload=**编译期**、同名不同参;override=**运行时**、签名相同、子类重写(多态)。
- 🔥 **abstract class vs interface**
  - interface:可**多实现**、常量、`default`/`static` 方法(Java8)、无状态。
  - abstract class:单继承、可有**成员状态**和构造器。
  - 选择:能力/契约用 interface,共享代码+状态用 abstract。
- **primitive vs wrapper**:`int` vs `Integer`。⚠️ **Integer 缓存 -128~127**,`==` 比较超范围会 false,比值用 `.equals()`。
- **immutable object 设计**【码】:`final class` + 全 `final` 字段 + 无 setter + 构造器深拷贝可变字段 + getter 返回副本。
- **record**(Java16):不可变数据载体,自动生成 `equals/hashCode/toString`。
- **static**:类级别,随类加载;不能访问非静态成员;`static` 块在类初始化时执行一次。

---

<a id="java-section-2"></a>

## 2. 对象契约 Object Contracts

- 🔥【码】**equals() / hashCode() 契约**
  - 重写 `equals` **必须**重写 `hashCode`。
  - `equal` 的对象 → `hashCode` **必相等**;`hashCode` 相等 → 不一定 `equal`(哈希冲突)。
  - 默认 `equals` 比引用(`==`),默认 `hashCode` 是对象地址。
  - ⚠️ 不重写就放进 HashMap/HashSet → 逻辑相等的对象被当成两个。
- **Comparable vs Comparator**:`Comparable.compareTo`(自身自然序,一个)vs `Comparator.compare`(外部定义,可多个,`Comparator.comparing(...)`)。
- **shallow vs deep copy**:浅拷贝共享内部引用对象;深拷贝递归复制。`clone()` 默认浅拷贝。

---

<a id="java-section-3"></a>

## 3. 集合 Collections

- **ArrayList vs LinkedList**:ArrayList=动态数组,随机访问 O(1)、中间插删 O(n);LinkedList=双向链表,插删 O(1)(拿到节点)、随机访问 O(n)。实战几乎都用 ArrayList。
- 🔥 **HashMap 内部结构**(必考)
  - 结构:**数组 + 链表 + 红黑树**(Java8)。
  - 默认容量 **16**,load factor **0.75**,超阈值 **resize 扩容 2 倍**。
  - **链表长度 ≥ 8 且数组长度 ≥ 64** → 转红黑树;< 6 退化回链表。
  - key 通过 `hashCode()` 定位桶 + `equals()` 判等。
  - ⚠️ Java7 头插法多线程 resize 会成环死循环 → **Java8 改尾插**;但 HashMap 仍**非线程安全**。
- 🔥 **ConcurrentHashMap**
  - Java8:**CAS + synchronized 锁桶头节点**(放弃 Java7 的 Segment 分段锁)。
  - ⚠️ **不允许 null key/value**(HashMap 允许)。
- **TreeMap**:红黑树,有序,O(log n);**LinkedHashMap**:保插入/访问顺序(可做 LRU);**PriorityQueue**:堆,取最值 O(log n)。
- **fail-fast vs fail-safe**:fail-fast=遍历时结构改变抛 `ConcurrentModificationException`(ArrayList/HashMap);fail-safe=遍历副本不抛(CopyOnWriteArrayList/ConcurrentHashMap)。

---

<a id="java-section-4"></a>

## 4. 异常 Exception

- 🔥 **checked vs unchecked**
  - checked:编译期强制处理(`IOException`、`SQLException`)。
  - unchecked:`RuntimeException` 及子类(`NPE`、`IllegalArgument`),不强制。
  - ⚠️ 接 Spring:**默认只对 RuntimeException 回滚事务**。
- 【码】**try-with-resources**:实现 `AutoCloseable` 自动关流,逆序关闭。
- REST 里:`@ControllerAdvice` + `@ExceptionHandler` 全局兜底,转标准错误响应。

---

<a id="java-section-5"></a>

## 5. 泛型 Generics

- **type erasure(类型擦除)**:编译后泛型被擦成 `Object`/边界,运行时无泛型信息。⚠️ 不能 `new T[]`、不能 `instanceof List<String>`。
- 🔥 **PECS**:`Producer extends, Consumer super`。取数据用 `? extends T`,存数据用 `? super T`。
- **bounded type**:`<T extends Comparable<T>>`。

---

<a id="java-section-6"></a>

## 6. Java 8+ 函数式

- **lambda / functional interface**:单抽象方法接口(`Function/Consumer/Supplier/Predicate`),`@FunctionalInterface`。
- 🔥【码】**Stream**:
  - 中间操作(**lazy**):`map / filter / flatMap / sorted`。
  - 终止操作:`collect / reduce / forEach / count`。
  - `flatMap` = 展平嵌套流。
  - ⚠️ **parallel stream** 用公共 `ForkJoinPool`,注意共享可变状态 + 顺序,IO 密集别用。
- **Optional**:防 NPE。用 `orElse / orElseGet / map / ifPresent`,⚠️ **别直接 `.get()`**。
- **CompletableFuture**:异步编排。`thenApply`(转换)/`thenCompose`(串联另一个 future)/`thenCombine`(合并)/`allOf`。

---

<a id="java-concurrency"></a>

## 7. 并发 Concurrency 🔥(bank 深挖区)

- Java 17 baseline; Java 21 virtual threads and preview structured concurrency are explicitly marked. Anchor: Spring Boot services on ECS, shared beans, request workers, and Hikari connections.

- [7.1. Memory model — visibility, ordering, happens-before](#concurrency-1)
- [7.2. Threads and why you don't create them](#concurrency-2)
- [7.3. Synchronization](#concurrency-3)
- [7.4. Concurrent collections](#concurrency-4)
- [7.5. Executors and pool sizing](#concurrency-5)
- [7.6. CompletableFuture](#concurrency-6)
- [7.7. Virtual threads & structured concurrency (Java 21)](#concurrency-7)
- [7.8. Thread safety in Spring — where it actually goes wrong](#concurrency-8)
- [7.9. Failure modes](#concurrency-9)
- [7.10. Interview Q&A](#concurrency-10)

<a id="concurrency-1"></a>

### 7.1. Memory model — visibility, ordering, happens-before

```
Thread A                     Thread B
 write x=1  ──┐               read x  →  may see 0 forever
 write f=true │ no ordering    read f  →  may see true before x=1
              └─ compiler reorders, CPU reorders, caches don't sync
```

- **Intuition**: multithreading breaks in two independent ways — *atomicity* (a compound operation interleaves) and *visibility/ordering* (one thread never sees another's write, or sees writes out of order). Locks fix both; `volatile` fixes only the second.
  - **Happens-before** is the JMM's ordering guarantee: if action A happens-before B, A's effects are visible to B. Edges are established by: unlocking a monitor → subsequent locking of the same monitor; a `volatile` write → subsequent read of that variable; `Thread.start()` → everything in that thread; everything in a thread → another thread's successful `join()`. `final` fields have separate initialization-safety rules; they are not a general publication edge for every mutable field.
  - Without a suitable publication/ordering mechanism, there is **no guarantee of observing the intended update** — not "probably fine," not "eventually visible." A non-volatile flag loop can hoist out of the loop and spin forever. This is the single most-missed point.
- **`volatile`** — guarantees visibility and prevents reordering around the access; does **not** make `count++` atomic (read-modify-write is three operations). Use for: a status/stop flag, a reference published once, the double-checked-locking instance field.
- **`final` fields** — safe publication: if an object is constructed correctly and its reference published, other threads see fully-initialized `final` fields without synchronization. Defeater: leaking `this` from the constructor (registering a listener, starting a thread) destroys the guarantee.
- 🗣 "Locks buy atomicity *and* visibility. `volatile` buys visibility only. Atomics buy atomicity for a single variable without a lock."

<a id="concurrency-2"></a>

### 7.2. Threads and why you don't create them

```
platform Thread.start() → OS-backed thread; stack cost depends on JVM / -Xss
ThreadPoolExecutor      → reusable workers; queue / limits / rejection are configuration
virtual thread (21)     → JVM-scheduled; unmounts on supported blocking operations
```

- Platform threads map 1:1 to OS threads. Creating one per request means the OS scheduler, not you, decides your concurrency limit, and memory grows with load — under a traffic spike you get `OutOfMemoryError: unable to create new native thread` rather than graceful degradation.
- Lifecycle states: NEW → RUNNABLE → (BLOCKED on a monitor | WAITING on `wait`/`join`/`park` | TIMED_WAITING) → TERMINATED. Know these because they're what you read in a thread dump.
- **`Thread.interrupt()` is cooperative** — it sets a flag; blocking methods that declare `InterruptedException` throw it. Never swallow it: either propagate the exception or restore the flag with `Thread.currentThread().interrupt()`. Swallowing it makes a task uncancellable, which is why a hung pool won't shut down.
- **Never call `Thread.stop()`** (unsafe and deprecated in Java 17; still present but throws `UnsupportedOperationException` in Java 21) — it unlocked monitors at arbitrary points, leaving shared state half-mutated.

<a id="concurrency-3"></a>

### 7.3. Synchronization

- **`synchronized`** — intrinsic monitor per object; reentrant; releases on exit *and* on exception. Simplest correct thing; use it by default.
  - Defeater: no timeout, no interruptibility, no try-lock, no fairness, and always exclusive (readers block readers).
  - Lock the *right* object: `synchronized(this)` on a public class publishes your lock to anyone holding a reference. Prefer a private final lock object.
- **`ReentrantLock`** — explicit lock/unlock in try/finally. Buys `tryLock(timeout)` (deadlock avoidance), `lockInterruptibly()`, optional fairness, and multiple `Condition` objects.
  - Costs: you can forget `unlock()` — the failure `synchronized` cannot have. Fairness can reduce throughput under contention; measure it against the starvation/latency requirement. Untimed `tryLock()` can still barge on a fair `ReentrantLock`.
- **`ReadWriteLock` / `StampedLock`** — many readers or one writer. Pays off only when reads dominate and critical sections are long enough to amortize the extra bookkeeping; under write-heavy load it's slower than `synchronized`. `StampedLock` adds optimistic reads (read a stamp, read the data, validate — retry if a writer intervened) but is not reentrant, which is a real footgun.
- **Atomics (`AtomicInteger`, `AtomicReference`)** — atomic updates commonly use CAS (compare-and-swap); implementation-level progress guarantees vary by operation/platform: read the value, compute the new one, swap only if unchanged, retry on failure.
  - Defeater: CAS retry loops *degrade* under high contention (many threads, many failed swaps). `LongAdder` fixes this for counters by striping across cells and summing on read — use it for high-frequency counters, `AtomicLong` when you need an exact instantaneous value.
  - ABA problem: a value can change A→B→A between your read and swap; `AtomicStampedReference` adds a version to detect it. Rarely needed in application code; a good depth answer.

```java
// Correct double-checked locking — volatile is load-bearing, not decoration
class Holder {
  static final class Config {} // Minimal stand-in for immutable configuration
  private static volatile Config instance;          // without volatile, another thread
  static Config get() {                             // can see a non-null reference to a
    Config c = instance;                            // partially constructed object
    if (c == null) {
      synchronized (Holder.class) {
        c = instance;
        if (c == null) instance = c = new Config();
      }
    }
    return c;
  }
}
// In practice: prefer a static holder class (lazy, thread-safe by classloading) or an enum.
```



#### Primitive selection

| Option | What it is | Strength | Weakness | Choose when |
|---|---|---|---|---|
| `synchronized` | Intrinsic reentrant monitor | Automatic release; guards compound invariants | No timed or interruptible acquisition | A small shared invariant needs one lock |
| `ReentrantLock` | Explicit reentrant lock | Timed acquisition, interruption, multiple conditions | Requires `finally`; fairness costs throughput | Cancellation or separate wait conditions matter |
| `ReadWriteLock` / `StampedLock` | Reader/writer coordination; optional optimistic reads | Can reduce reader contention | Extra bookkeeping; stamp validation; non-reentrant stamped lock | Measurements show long read-heavy critical sections |
| `AtomicLong` / `AtomicReference` | Atomic single-value operations | Atomic update without an application lock | Retry contention; no automatic multi-field invariant | One value or immutable snapshot defines the invariant |
| `LongAdder` | Striped accumulator | Reduces contended metric updates | Sum is not an atomic snapshot | Approximate live metrics, not quota enforcement |
| `Semaphore` | Permit-based admission | Caps scarce downstream concurrency | Permit release must be guaranteed | DB/API capacity must be bounded independently of threads |

- Decide by invariant scope first, cancellation requirements second, and measured contention third.

<a id="concurrency-4"></a>

### 7.4. Concurrent collections

| Need | Use | Mechanism / defeater |
|---|---|---|
| Map, high concurrency | `ConcurrentHashMap` | Per-bin CAS + synchronized bin heads (Java 8+). Defeater: `get` then `put` is **not** atomic — use `compute`/`merge`/`putIfAbsent` |
| Atomic counter map | `ConcurrentHashMap` + `merge` / `LongAdder` values | `map.merge(k, 1L, Long::sum)` is atomic; `map.put(k, map.get(k)+1)` is a lost-update bug |
| Read-mostly list | `CopyOnWriteArrayList` | Every write copies the whole array — O(n) writes. Fine for listener lists, catastrophic for hot writes |
| Producer/consumer handoff | `LinkedBlockingQueue` (**bounded**) / `ArrayBlockingQueue` | Bounded = backpressure. Unbounded queue = an OOM waiting for a slow consumer |
| Low-contention queue | `ConcurrentLinkedQueue` | Non-blocking, unbounded; `size()` is O(n) and approximate |
| Ordered/time-based | `PriorityBlockingQueue`, `DelayQueue` | Unbounded — same OOM caveat |

- **Iteration semantics matter**: `ConcurrentHashMap` iterators are weakly consistent (no `ConcurrentModificationException`, may or may not reflect concurrent updates); `Collections.synchronizedMap` iterators require you to hold the lock manually ; without it, traversal is unsafe and may throw `ConcurrentModificationException` (detection is best-effort). People assume the wrapper is safe to iterate; it isn't.
- `Collections.synchronizedX` wraps every method in one lock — correct but serializes everything; it is a valid coarse-lock strategy when contention is low or a compound invariant must share that lock.

<a id="concurrency-5"></a>

### 7.5. Executors and pool sizing

```
submit ─▶ [core threads busy?] ─▶ queue ─▶ [queue full?] ─▶ up to maxPoolSize
                                                        └─▶ RejectedExecutionHandler
```

- **Queue-before-maximum ordering**: `ThreadPoolExecutor` grows to `maxPoolSize` only when the **queue is full**. With an unbounded queue, `maxPoolSize` is dead configuration — the pool never grows past core, and work piles up invisibly until memory dies.
  - Therefore: **bounded queue + explicit rejection policy** (`CallerRunsPolicy` for natural backpressure, or `AbortPolicy` + a metric). This is the rule that converts a silent OOM into a visible, sheddable failure.
- **Avoid `Executors.newFixedThreadPool` / `newCachedThreadPool` in production**: the first uses an unbounded queue, the second creates unbounded threads. Construct `ThreadPoolExecutor` explicitly, name your threads (thread dumps become readable), and set a rejection policy.
- **Sizing**: CPU-bound ≈ number of cores (+1). I/O-bound ≈ cores × (1 + wait/compute) — but in a Spring service the real constraint is almost never CPU:
  - **Size to the scarcest downstream resource.** 200 request threads against a 20-connection Hikari pool means 180 threads parked waiting for a connection; you haven't added throughput, you've added queueing and latency variance. Match the executor to the pool, or bulkhead per dependency.
  - In containers: verify the JVM sees the right CPU count (`availableProcessors` respects cgroup limits on modern JDKs; a fractional CPU limit can round to 1 and silently shrink every default pool — including ForkJoin common pool).
- **`ForkJoinPool.commonPool()`** backs parallel streams and default `CompletableFuture.*Async` — it's **shared JVM-wide**; default target parallelism is generally max(1, available processors − 1), subject to configuration. Default `CompletableFuture` async methods use a new thread per task if the common pool cannot support parallelism of at least two. Running blocking I/O on it starves everything else that uses it. Always pass your own executor for blocking work.
- Shutdown: `shutdown()` (no new tasks, finish current) → `awaitTermination(timeout)` → `shutdownNow()` (interrupts). Skipping this in a Spring bean leaves non-daemon threads holding shutdown open.

- **Constructor parameters:** `corePoolSize`, `maximumPoolSize`, `keepAliveTime`, `unit`, `workQueue`, `threadFactory`, `handler` (the seven-argument overload).
- **Rejection choices:** abort, caller-runs, discard, discard-oldest. For work whose result matters, avoid silent discard; caller-runs can block an event loop and discards after shutdown.
- **Producer/consumer:** bounded `BlockingQueue.put` / `take` supply interruptible blocking; `offer` with a deadline lets callers shed overload.

<a id="concurrency-6"></a>

### 7.6. CompletableFuture

- **Intuition**: a value that will exist later, plus a way to compose what happens next without blocking.
- Core moves: `supplyAsync(sup, executor)`, `thenApply` (transform), `thenCompose` (flatMap — chain another future), `thenCombine` (join two independent futures), `allOf`/`anyOf`, `exceptionally`/`handle`/`whenComplete`, `orTimeout` (Java 9+).
- Defeaters that get people:
  - **Always pass an executor.** The no-arg `*Async` variants use the common ForkJoin pool (§5).
  - **Non-`Async` callbacks run on whichever thread completed the future** — possibly your I/O thread, possibly the caller's; a heavy `thenApply` can hijack a netty/event thread.
  - `join()`/`get()` inside a callback re-introduces blocking and can deadlock a bounded pool where all threads are waiting on tasks queued behind them (thread-starvation deadlock).
  - **`allOf` returns `CompletableFuture<Void>`** — you re-read each future's value afterward; and it does not cancel siblings on first failure. `anyOf` completes on the first completion, including success; it is not a fail-fast all-results combinator. Use explicit failure coordination/cancellation or a Java 21 preview `ShutdownOnFailure` scope.
  - An exception inside an async stage is captured, not thrown — silently swallowed unless you attach `exceptionally`/`handle` or check completion.

- Composition sketch: application types (`Instrument`, `Price`), clients, and `ioPool` are supplied by the service; static imports for `supplyAsync` and `MILLISECONDS` are assumed.

```java
CompletableFuture<Instrument> base = supplyAsync(() -> repo.find(id), ioPool);
CompletableFuture<Price>      px   = supplyAsync(() -> pricing.get(id), ioPool)
                                       .orTimeout(300, MILLISECONDS)
                                       .exceptionally(e -> Price.UNAVAILABLE);  // degrade, don't fail
return base.thenCombine(px, Instrument::withPrice);
```

- **Timeout is not cancellation:** `orTimeout` completes the future exceptionally but does not stop the repository/HTTP operation. Set client deadlines and design cooperative cancellation; `CompletableFuture.cancel(true)` does not interrupt its computation.

<a id="concurrency-7"></a>

### 7.7. Virtual threads & structured concurrency (Java 21)

```
platform: 1 thread : 1 OS thread    → blocking wastes an OS thread
virtual : N threads : few carriers  → blocking parks the VT, frees the carrier
```

- **What they are**: JVM-scheduled threads mounted onto a small pool of carrier (platform) threads. On supported blocking operations the JVM can unmount the virtual thread and run other work on its carrier. Stack chunks live on the heap and grow with use; memory and concurrency limits depend on workload, retained state, and native/pinning behavior.
- **What they buy**: thread-per-request becomes viable for I/O-bound work. You write plain blocking code and get async-level scalability, with readable stack traces and working `try/finally` and thread-locals — the readability of blocking with the scalability of reactive. In Spring Boot 3.2+, `spring.threads.virtual.enabled=true` runs MVC handling on them.
- **Defeaters to volunteer** (this is the differentiator):
  - **They don't create resources.** If your bottleneck is a 20-connection DB pool, virtual threads only move the queue from the thread pool to the connection pool. They fix *thread scarcity*, not *resource scarcity*.
  - **Pooling them is an anti-pattern** — they're cheap and disposable; `Executors.newVirtualThreadPerTaskExecutor()` creates one per task by design.
  - **Pinning**: a virtual thread inside a `synchronized` block that blocks cannot unmount, pinning the carrier. The classic case is JDBC drivers using `synchronized` internally. JDK 24 (JEP 491) largely removed this limitation; before that, `ReentrantLock` was the workaround. Knowing the JEP number is cheap credibility.
  - **CPU-bound work gains nothing** — you still have only so many cores.
- **Structured concurrency** (`StructuredTaskScope`, preview in 21): child tasks belong to a lexical scope. In Java 21, use `fork` → `join` → inspect results or `throwIfFailed`; `close()` waits for child termination. `ShutdownOnFailure` supplies the failure policy; the base scope does not automatically cancel siblings on failure. Cancellation is cooperative, so non-cooperative tasks can delay scope closure. Preview APIs require `--enable-preview` and may differ across JDK releases. It's the fix for the orphaned-task and forgotten-cancellation failure modes that `ExecutorService` allows by construction.

<a id="concurrency-8"></a>

### 7.8. Thread safety in Spring — where it actually goes wrong

- **Spring beans are singletons by default; every request thread shares them.** Therefore: **beans must be stateless**, or their state must be immutable or properly guarded. Injected dependencies must also support concurrent use; injection alone does not make them thread-safe. JPA `EntityManager` instances are not thread-safe; Spring commonly injects a proxy that resolves the transaction-bound instance. Any mutable instance field is a bug until proven otherwise.
  - This is the singleton-with-`ArrayList` review question: shared mutable collection, no synchronization, hit by concurrent request threads → corrupted internal state (lost elements, `ArrayIndexOutOfBoundsException`), `ConcurrentModificationException` on iteration, and no visibility guarantee even without corruption. And beyond thread safety: it's an unbounded accumulator on a singleton — a memory leak and a cross-request data-exposure risk.
- **`@Transactional` and threads**: the transaction lives in a `ThreadLocal` (`TransactionSynchronizationManager`). Work you hand to another thread is **outside** the transaction — the new thread has no connection, no rollback participation. Same for `SecurityContextHolder` (auth principal) and MDC (correlation id/trace id): all thread-local, all lost across an executor boundary unless you propagate security/logging context explicitly (`DelegatingSecurityContextExecutor`, an MDC-copying task decorator with cleanup). Do not copy transaction ThreadLocals or share a JDBC connection across threads; create an independent transaction in the worker when needed. This discussion is for imperative transactions; reactive transactions use Reactor context.
  - 🗣 "Across an executor boundary, explicitly propagate security and logging context; create a separate worker transaction rather than copying the caller's transaction."
- **`@Async`**: returns immediately, runs on a `TaskExecutor` — configure your own bounded one; the default (`SimpleAsyncTaskExecutor` historically) created a new thread per call. Exceptions in `void` `@Async` methods cannot return to the caller; the default handler logs them, and a custom `AsyncUncaughtExceptionHandler` can report them to monitoring. Self-invocation doesn't work (proxy-based, same as `@Transactional`).
- **Hikari pool sizing** is your real concurrency limit for DB work; `leakDetectionThreshold` warns about connections held past a threshold; it does not prove a leak or reclaim the connection. A connection held across a slow external call is the classic pool exhaustion cause — keep external I/O outside the DB transaction where possible; when unavoidable, bound it with deadlines and account for connection hold time.

<a id="concurrency-9"></a>

### 7.9. Failure modes

| Failure | Trigger | Detection | Mitigation |
|---|---|---|---|
| **Deadlock** | Two threads acquire locks A,B in opposite orders | Thread dump shows BLOCKED cycle; `jstack` reports "Found one Java-level deadlock" | Global lock ordering; `tryLock(timeout)`; hold one lock at a time |
| **Livelock** | Threads keep retrying and yielding to each other | High CPU, no progress | Randomized backoff |
| **Starvation** | Unfair locks / low-priority threads never scheduled | Latency outliers on specific operations | Fair locks (at a throughput cost); bounded queues |
| **Thread leak** | Executor never shut down; tasks blocked forever | Thread count climbing in JVM metrics | Named pools + shutdown hooks + thread-count alarm |
| **Pool exhaustion** | All threads blocked on a slow dependency | p99 up, DB time flat, queue depth up | Timeouts, bulkheads, circuit breaker |
| **Unbounded queue OOM** | Producer faster than consumer, unbounded queue | Heap growth, then OOM | Bounded queue + rejection policy = backpressure |
| **Lost update** | Read-modify-write without atomicity | Silent wrong data — the worst class | Atomics, `merge`/`compute`, or DB-level optimistic locking |
| **Race on lazy init** | Unsafe double-checked locking | Intermittent NPE / half-built object | `volatile`, holder class, or enum singleton |

- **Canonical failure pattern (not a specific incident):** a service adds a call to a slow downstream inside a request path with no timeout. Request threads park; the configured request-worker limit is reached (illustratively, 200 workers); unrelated healthy endpoints on the same service start timing out; upstream callers retry, amplifying load. Root cause is not the slow dependency — it's the absence of a timeout and a bulkhead, which let one dependency's latency become the whole service's outage.

<a id="concurrency-10"></a>

### 7.10. Interview Q&A

- **Q:** What's the difference between `synchronized` and `ReentrantLock`?

  **L4 answer**
  - Both mutual exclusion, both reentrant. `synchronized` is a keyword, auto-released on scope exit or exception, no timeout or interruptibility. `ReentrantLock` is an object requiring try/finally, and adds `tryLock` with timeout, `lockInterruptibly`, optional fairness, and multiple conditions.

  **L5 answer**
  - Choose by what you need to *avoid*: if the risk is deadlock, `tryLock(timeout)` is the only one that lets you back out; if the risk is a forgotten `unlock()`, `synchronized` removes that failure entirely. Fairness sounds free and isn't — a fair lock disallows barging, so throughput drops materially under contention; use it only when starvation is a demonstrated problem. Uncontended monitor cost depends on JVM optimizations; do not assume biased locking on the Java 17 baseline. Measure contention and critical-section duration rather than choosing by a blanket performance claim.

- **Q:** Is `volatile` enough to make a counter thread-safe?

  **L4 answer**
  - No. `volatile` gives visibility and ordering but not atomicity; `count++` is read-modify-write, so two threads can read the same value and both write the same increment — a lost update. Use `AtomicInteger` or a lock.

  **L5 answer**
  - The right choice depends on contention: `AtomicInteger` CAS-loops, which degrades as contention rises because failed swaps retry; `LongAdder` stripes across cells and sums on read, trading an exact instantaneous value for much better write throughput. For a metrics counter under load, `LongAdder`; for a value you must read exactly and act on, `AtomicLong` — or push the invariant into the database with optimistic locking, which is usually the honest answer for anything that must survive a restart.

- **Q:** What happens when a `ThreadPoolExecutor`'s queue fills?

  **L4 answer**
  - It creates threads up to `maxPoolSize`; beyond that, the `RejectedExecutionHandler` runs — abort (throws), caller-runs, discard, or discard-oldest.

  **L5 answer**
  - The trap is the reverse: threads are only added *after* the queue is full, so an unbounded queue means the pool never exceeds core size and `maxPoolSize` is dead config while memory grows silently until OOM. Bounded queue plus `CallerRunsPolicy` is a backpressure mechanism — the submitting thread executes the task, which naturally slows the producer. What breaks at scale: `CallerRunsPolicy` on an HTTP request thread means a request thread now does background work, so pick it deliberately.

- **Q:** How do you make a Spring `@Service` thread-safe?

  **L4 answer**
  - Make it stateless: no mutable instance fields; hold per-request data in method parameters and local variables. Injected dependencies are shared and must have their own concurrency guarantees. If shared state is genuinely required, use a concurrent collection or explicit synchronization, and bound its size.

  **L5 answer**
  - The deeper answer is that thread safety in Spring is mostly a *scope* decision, not a locking decision: request-scoped state belongs on the stack; application-scoped state belongs behind a concurrent structure with an eviction policy; anything that must survive a restart belongs in a database, not a field. And the invisible hazard is thread-local context — transactions, `SecurityContextHolder`, and MDC don't cross executor boundaries, so an async worker does not inherit the caller's transaction by default. Give worker DB work an independent transaction if required, propagate security/log context explicitly, and clear copied context after execution.

- **Q:** Deadlock — how do you detect and prevent it?

  **L4 answer**
  - Detect: thread dump (`jstack`, or Datadog's JVM profiler) reports a Java-level deadlock with the cycle. Symptom is stalled threads: monitor waiters may be BLOCKED; explicit-lock or future waiters may be WAITING/PARKED. Executor starvation may have no detectable monitor-lock cycle. Prevent: consistent global lock ordering, minimize lock scope, prefer a single lock, use `tryLock` with timeout to break cycles.

  **L5 answer**
  - The four Coffman conditions (mutual exclusion, hold-and-wait, no preemption, circular wait) tell you which lever to pull — you break circular wait with lock ordering, hold-and-wait by acquiring all locks at once or none, and hold-and-wait by releasing held locks when timed acquisition fails. `tryLock` does not preempt a lock held by another thread. At scale the deadlocks that actually bite aren't in-process: they're a DB deadlock from two transactions updating rows in opposite order (Postgres detects and kills one — retry the loser), or a distributed one where service A synchronously calls B while B calls A and both pools are full. The in-process fix is discipline; the distributed fix is asynchrony and bulkheads.

- **Q:** Virtual threads — should we switch everything?

  **L4 answer**
  - They make thread-per-request cheap for I/O-bound work and remove most pool-sizing guesswork. Enable in Spring Boot 3.2+ with a property. Not useful for CPU-bound work, and don't pool them.

  **L5 answer**
  - Switching changes where your queue forms, not whether you have one. If the real constraint is a 20-connection DB pool or a rate-limited downstream, virtual threads let ten thousand requests arrive at that bottleneck instead of two hundred — which is *worse* without an explicit concurrency limiter, because you've converted fast rejection into slow queueing. So the migration is: enable virtual threads, then add explicit semaphores or bulkheads per downstream to reintroduce the limit the thread pool used to imply. And check for pinning if you're pre-JDK 24 with a driver that uses `synchronized` internally.

- **Q:** Where have you used multithreading in your work? (they will ask this)
- Have a real answer, honestly bounded. Candidates from your work: parallel resolution across Aurora/Mongo/OpenSearch in a single GraphQL request via `CompletableFuture`; Spark executors as the parallelism model in the Glue pipeline (data parallelism, not thread management); async processing of SNS/SQS consumers; the Lambda injector's concurrency limits. If you mostly consumed framework-managed concurrency rather than writing thread code, **say that** — "I've reasoned about it constantly at the framework level; I've written raw thread code rarely" is a credible senior answer, and it invites the questions you can win.

#### L5-only follow-ups

- **Q:** How do you migrate to virtual threads without overwhelming Aurora?
  - Establish a connection/transaction concurrency budget, cap admission per dependency and tenant, and keep deadlines on wait plus execution. Compare queue time, rejected requests, connection hold time, and p99 under load; roll out gradually with a rollback gate.
- **Q:** A timed-out fan-out request still consumes capacity; what must change?
  - Trace child operations after parent completion. Future timeout alone does not end I/O; propagate deadlines, cancel through client APIs where supported, release resources in `finally`, and bound orphaned work. Structured scope ownership improves lifetime accounting but still requires cooperative termination.


---

<a id="java-section-8"></a>

## 8. JVM 🔥

- 🔥 **运行时数据区**
  - **heap**(共享,对象实例,GC 主战场)。
  - **metaspace/方法区**(类信息,Java8 起用**本地内存**,取代永久代 PermGen)。
  - **JVM stack**(线程私有,栈帧=局部变量+操作数栈)。
  - **PC 寄存器 / native method stack**。
- 🔥 **class loading 流程**:加载 → 验证 → 准备 → 解析 → 初始化。
- 🔥 **双亲委派(parent delegation)**:Bootstrap → Platform/Ext → App → 自定义。**向上委托,向上找不到才向下加载**。作用:避免重复加载 + 核心类安全(防篡改)。
- 🔥 **GC 分代**:young(Eden + 2×Survivor)+ old。
  - **Minor GC**=回收 young(频繁快);**Full GC**=整堆(慢,要避免)。
  - 对象:Eden 分配 → 存活进 Survivor → 熬过多次进 old。
  - 算法:标记-清除(碎片)/复制(young)/标记-整理(old)。
  - **GC Roots**:栈局部变量、静态变量、常量、JNI 引用(可达性分析)。
  - 收集器:**G1**(Java9+ 默认)、ZGC(低延迟)、CMS(已废弃)。
- 🔥 **4 种引用**:strong(不回收)/ soft(内存不足才回收,做缓存)/ weak(下次 GC 回收,`ThreadLocal`/`WeakHashMap`)/ phantom(回收通知)。
- ⚠️ **OOM vs StackOverflowError**:OOM=堆/元空间满;SOE=递归太深栈溢出。
- **memory leak 场景**:静态集合持有对象、未关资源、`ThreadLocal` 不 remove、监听器未注销。
- 工具:`jstack`(thread dump 查死锁)、`jmap`(heap dump 查内存)、`jstat`(看 GC)。

---

<a id="java-section-9"></a>

## 背诵优先级(时间不够就按这个背)

1. **必背 🔥**:pass-by-value、String immutable、equals/hashCode 契约、HashMap 内部、ConcurrentHashMap、volatile vs synchronized、线程池流程 + 拒绝策略、GC 分代 + Full GC、双亲委派、4 种引用、事务回滚(见 Spring 篇)。
2. **能现场码【码】**:equals/hashCode、Stream、线程池创建、producer-consumer、immutable 对象。
3. **能画/讲**:HashMap resize、class loading、GC 流程、线程池执行链路。

---

<a id="java-section-10"></a>

## References

1. **JavaGuide**(github.com/Snailclimb/JavaGuide)— 中文 Java 面试知识树,和这份模板逐条对得上,深挖首选。
2. **Oracle Java Documentation / JLS** — 技术事实以官方为准(String pool、pass-by-value、generics erasure)。
3. **Baeldung**(baeldung.com)— Spring/Java 每个概念配可运行代码,查 CompletableFuture、ThreadPoolExecutor 用。
4. **《Java Concurrency in Practice》** — 并发深挖(volatile/CAS/线程池语义)。

- [JLS 17 §17 — JMM and final-field semantics](https://docs.oracle.com/javase/specs/jls/se17/html/jls-17.html).
- [Thread — Java 17](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/lang/Thread.html) and [Java 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/Thread.html).
- [ThreadPoolExecutor — Java 21](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/ThreadPoolExecutor.html).
- [CompletableFuture — Java 17](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/concurrent/CompletableFuture.html).
- [JEP 444 — Virtual Threads](https://openjdk.org/jeps/444); [JEP 491 — synchronized without pinning](https://openjdk.org/jeps/491); [JDK 24 migration notes](https://docs.oracle.com/en/java/javase/24/migrate/significant-changes-jdk-24.html).
- [StructuredTaskScope — Java 21 preview](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/StructuredTaskScope.html).
- [Spring transaction annotations](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html) and [Boot task execution / virtual threads](https://docs.spring.io/spring-boot/reference/features/task-execution-and-scheduling.html).
