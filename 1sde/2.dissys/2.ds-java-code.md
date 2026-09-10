# Core Java concurrency and threading: concepts, code, and usage patterns

## Index

- [1. Scope, Java versions, and priority](#scope)
- [2. All concepts ranked by preparation priority](#concept-map)
- [3. Choosing tools by the invariant](#choose)
- [4. Concept explanations and core snippets](#concepts)
- [5. Cases grouped by the problem being solved](#case-map)
- [6. Case walkthroughs and core code](#cases)
- [7. Common compositions and overload behavior](#compositions)
- [8. Interview questions: L4 + L5 extra](#questions)
- [9. Verification and reading order](#verification)
- [References](#references)

<a id="scope"></a>

## 1. Scope, Java versions, and priority

- **Scope**
  - Java language primitives and Java SE/JDK APIs only.
  - Concepts first.
  - A core snippet for every concept family.
  - Concrete service cases after the concept catalog.
  - No external concurrency library or framework dependency.
  - The JDBC example compiles against Java SE interfaces.
  - A real database connection still requires a database and JDBC driver.
- **Priority**
  - P0: be able to explain the invariant, write the core code, and handle failure in an interview.
  - P1: common backend extensions that you should recognize and adapt.
  - P2: specialized coordination or library-level mechanisms to understand after P0/P1.
  - Ranking is an editorial preparation order for backend interviews, not a measured interview-frequency dataset.
  - Within each priority, learn foundational correctness before optimizations.
- **Version contract**
  - Most snippets target Java 17.
  - Virtual-thread snippets target Java 21 or later.
  - ScopedValue targets the final Java 25 API.
  - StructuredTaskScope targets the Java 25 preview API and requires `--enable-preview`.
  - Java 26 also keeps structured concurrency in preview.
  - Preview source compatibility across releases is not assumed.
  - Monitor-related virtual-thread pinning changed in Java 24.
  - Do not apply the old Java 21 advice to replace every blocking synchronized region blindly to Java 24+.
  - Long lock-held I/O still serializes competing callers regardless of pinning.
  - Sources
    - [JDK virtual threads](https://docs.oracle.com/en/java/javase/25/core/virtual-threads.html)
    - [ScopedValue](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/ScopedValue.html)
    - [Java 25 task scopes](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/StructuredTaskScope.html)
    - [Java 26 task scopes](https://docs.oracle.com/en/java/javase/26/docs/api/java.base/java/util/concurrent/StructuredTaskScope.html)
- **Read every code contract**
  - Each Java fence contains a complete package-private class with imports.
  - The final composition explicitly depends on earlier snippet classes.
  - Call methods from a small harness to exercise them.
  - Capacities and durations are illustrative choices.
  - Local synchronization guarantees apply to one JVM unless the case explicitly delegates arbitration to a database.
  - For elapsed-time arithmetic, assume configured durations and gaps between observations are shorter than half the `long` nanosecond range.

<a id="concept-map"></a>

## 2. All concepts ranked by preparation priority

| Rank | Priority | Concept family / local detail | Common reason to use it | Java |
| --- | --- | --- | --- | --- |
| 1 | P0 | [Ownership, immutability, confinement](#concept-ownership) | Avoid races by minimizing shared mutable state before selecting a lock. | 17 |
| 2 | P0 | [Java Memory Model and happens-before](#concept-jmm) | Explain why another thread sees a completed write instead of relying on timing. | 17 |
| 3 | P0 | [synchronized: protect a complete invariant](#concept-monitor) | Keep a check and its update indivisible when several fields describe one state. | 17 |
| 4 | P0 | [volatile: flags and whole-snapshot publication](#concept-volatile) | Let readers observe replacement state without acquiring a mutual-exclusion lock. | 17 |
| 5 | P0 | [ReentrantLock: timed and interruptible locking](#concept-lock) | Bound lock waiting or support cancellation where a monitor acquisition cannot do so. | 17 |
| 6 | P0 | [Atomic variables, CAS loops, atomic references](#concept-atomic) | Perform a conditional update on one variable without a user-managed lock. | 17 |
| 7 | P0 | [ConcurrentHashMap: atomic per-key operations](#concept-chm) | Allow concurrent key access without one global map monitor. | 17 |
| 8 | P0 | [BlockingQueue and bounded producer/consumer handoff](#concept-queue) | Decouple producers from consumers without unbounded retained work. | 17 |
| 9 | P0 | [ExecutorService and bounded ThreadPoolExecutor](#concept-executor) | Separate task submission from thread creation and impose an overload policy. | 17 |
| 10 | P0 | [Runnable, Callable, Future, FutureTask](#concept-future) | Represent a task result, failure, cancellation request, and bounded wait. | 17 |
| 11 | P0 | [CompletableFuture and CompletionStage composition](#concept-completable) | Compose dependent asynchronous stages without blocking a worker at every boundary. | 17 |
| 12 | P0 | [Interruption, cancellation, and time budgets](#concept-interrupt) | Let task owners request cooperative termination and stop indefinite waiting. | 17 |
| 13 | P0 | [Deadlock, lock ordering, starvation, livelock](#concept-deadlock) | Prevent cyclic waiting when an operation touches multiple resources. | 17 |
| 14 | P0 | [Semaphore: bound concurrent resource use](#concept-semaphore) | Protect a dependency with fewer slots than the number of runnable requests. | 17 |
| 15 | P0 | [Virtual threads: blocking I/O at high concurrency](#concept-virtual) | Make a thread-per-task style affordable for many mostly-waiting operations. | 21 |
| 16 | P0 | [ThreadFactory, execution errors, shutdown, join](#concept-lifecycle) | Ensure every task has an owner responsible for errors and termination. | 17 |
| 17 | P1 | [Condition: wait for a protected predicate](#concept-condition) | Suspend until a state transition makes an operation legal instead of polling. | 17 |
| 18 | P1 | [Object.wait, notify, notifyAll](#concept-wait) | Understand intrinsic-monitor coordination used by legacy code and interviews. | 17 |
| 19 | P1 | [ReentrantReadWriteLock: consistent multi-key reads](#concept-rwlock) | Allow concurrent readers while preserving a single protected data structure. | 17 |
| 20 | P1 | [LongAdder and LongAccumulator: contended metrics](#concept-adder) | Reduce contention when many threads update a metric that does not require an atomic snapshot. | 17 |
| 21 | P1 | [ThreadLocal and task context](#concept-threadlocal) | Carry data tied to one executing thread through a synchronous call chain. | 17 |
| 22 | P1 | [CountDownLatch: one-shot completion or startup](#concept-latch) | Wait for a fixed number of independent events to finish. | 17 |
| 23 | P1 | [ScheduledExecutorService: refresh and periodic work](#concept-scheduler) | Schedule delayed work without inventing a sleeping management thread. | 17 |
| 24 | P1 | [ExecutorCompletionService: consume completed results](#concept-completion) | Avoid waiting on submission order when a later task finishes earlier. | 17 |
| 25 | P1 | [ForkJoinPool and parallel streams: CPU decomposition](#concept-forkjoin) | Divide a large independent CPU workload into tasks whose overhead is smaller than their useful work. | 17 |
| 26 | P1 | [ScopedValue: bounded immutable request context](#concept-scoped) | Bind context for one dynamic call scope without leaving mutable thread-local state behind. | 25 |
| 27 | P1 | [Thread states, dumps, contention, and diagnostics](#concept-diagnostics) | Distinguish CPU saturation, lock contention, queue delay, and dependency waiting before changing thread counts. | 17 |
| 28 | P1 | [AtomicReference, stamped references, arrays, and field updaters](#concept-atomicstate) | Atomically replace a multi-field logical value without mixing fields from different versions. | 17 |
| 29 | P2 | [StampedLock: optimistic reads](#concept-stamped) | Reduce read-side lock traffic for short snapshots that tolerate retry. | 17 |
| 30 | P2 | [CyclicBarrier: reusable fixed-party rendezvous](#concept-barrier) | Make a fixed team finish each round before any member starts the next. | 17 |
| 31 | P2 | [Phaser: dynamic parties and phases](#concept-phaser) | Coordinate phases when the number of participating tasks changes. | 17 |
| 32 | P2 | [CopyOnWriteArrayList and synchronized wrappers](#concept-cow) | Choose collection iteration semantics explicitly instead of assuming every thread-safe list behaves alike. | 17 |
| 33 | P2 | [ConcurrentSkipListMap and ordered concurrent sets](#concept-sorted) | Maintain concurrent sorted navigation when a hash map cannot answer range queries. | 17 |
| 34 | P2 | [SynchronousQueue, transfer queues, and Exchanger](#concept-handoff) | Coordinate direct ownership handoff when buffering is not the desired contract. | 17 |
| 35 | P2 | [Structured concurrency: child-task lifetime ownership](#concept-structured) | Keep related subtasks within the lifetime of the parent operation. | 25-preview |
| 36 | P2 | [VarHandle and explicit memory access modes](#concept-varhandle) | Implement a carefully proven low-level publication protocol without Unsafe. | 17 |
| 37 | P2 | [LockSupport and AQS internals](#concept-park) | Understand how higher-level synchronizers park contenders and signal progress. | 17 |
| 38 | P2 | [Flow API: demand-based asynchronous delivery](#concept-flow) | Express consumer demand when building an asynchronous stream of items. | 17 |
| 39 | P2 | [DelayQueue and priority queues: eligibility versus capacity](#concept-delayed) | Select work by due time or priority rather than FIFO arrival. | 17 |

<a id="choose"></a>

## 3. Choosing tools by the invariant

| Question | Default tool | Why | Escalate when |
| --- | --- | --- | --- |
| Can one task own all mutation? | Local variables / one owner | Removes shared-state coordination | Other threads genuinely need concurrent access |
| Can readers consume immutable replacement state? | volatile immutable snapshot | Readers capture one coherent version | Updates must conditionally preserve a version |
| Does one scalar need atomic read-modify-write? | AtomicInteger / AtomicLong | One atomic transition | Several values must change together |
| Do several fields form one invariant? | synchronized | Smallest easily reviewed critical section | Timed acquisition or custom wait conditions are required |
| Do I need timeout, interruption, or conditions on a lock? | ReentrantLock | Explicit acquisition policy | Read concurrency materially improves measured performance |
| Are operations independent per key? | ConcurrentHashMap | Concurrent key access and atomic remapping | Multiple keys require one consistent view |
| Do readers need a whole-map snapshot? | Read/write lock or immutable map replacement | Clear snapshot boundary | Copy cost or write contention changes the tradeoff |
| Is it only a high-contention metric? | LongAdder | Spreads update contention | The count authorizes a strict quota decision |
| Is the resource scarce? | Semaphore | Bounds active local use | Arrival rate also needs limiting |
| Is the input rate the contract? | Sliding window / token bucket | Accounts for requests over time | Coordination must span replicas |
| Is work waiting for CPU? | Bounded platform-thread executor | Caps runnable work and backlog | One job has a useful divide-and-conquer structure |
| Is work mostly blocking I/O? | Admitted virtual threads on Java 21+ | Simple blocking control flow | An async API already supplies the desired lifecycle |
| Does one async result depend on another? | thenCompose | Flattens a dependent async stage | Several required children need a shared lifetime |
| Must a producer slow down? | Bounded BlockingQueue / admission | Makes saturation explicit | Demand must be propagated through a streaming protocol |

### Lock and state alternatives

| Option | What it is | Strength | Weakness | Choose when |
| --- | --- | --- | --- | --- |
| synchronized | Intrinsic monitor | Simple reentrant exclusion and automatic release | No timed acquisition | Short compound invariant |
| ReentrantLock | Explicit reentrant lock | Timed/interruptible acquisition and conditions | Manual finally discipline | Acquisition policy matters |
| ReadWriteLock | Separate read and write modes | Concurrent protected reads | Coordination cost and writer contention | Reads do meaningful work |
| StampedLock | Stamped write/read/optimistic modes | Cheap successful optimistic snapshots | Non-reentrant and easy to misuse | Tiny read snapshots with infrequent writes |
| AtomicReference | CAS on immutable state identity | Atomic whole-state replacement | Allocation and retry contention | Small state with pure updates |
| volatile | Ordered publication of a field | Very simple snapshot/flag reads | No compound atomicity | One-writer replacement or explicit flag |
| LongAdder | Distributed internal update cells | High-contention statistics | Non-atomic aggregate observation | Metrics only |

### Waiting and task alternatives

| Option | Completion shape | Cancellation / failure | Common use |
| --- | --- | --- | --- |
| Thread + join | One explicitly owned thread | Owner interrupts and joins | Basic lifecycle and a few dedicated workers |
| Future | One result handle | Task exceptions through get; cancellation is cooperative | Submit then await with a budget |
| CompletableFuture | Dependency graph | Exceptional stages; underlying cancellation is separate | Async composition |
| CompletionService | Completion-order result queue | Owner tracks and cancels futures | First successful response or streaming completion |
| CountDownLatch | Fixed one-shot event count | No built-in result/error transport | Startup or test coordination |
| CyclicBarrier | Fixed repeated participants | One failed participant can break the round | Iterative parallel rounds |
| Phaser | Dynamic participants and phases | Explicit deregistration and termination policy | Changing batch membership |
| StructuredTaskScope | Related children under one parent | Join policy and scope cancellation | Required fan-out with lexical ownership; preview version applies |

### CompletableFuture method selection

| Method | Input / output shape | Use | Trap |
| --- | --- | --- | --- |
| supplyAsync | Supplier to future value | Start a task on an explicit executor | Blocking work should not accidentally use the common pool |
| thenApply | Value to value | Synchronous transformation | Slow work can occupy the completing thread |
| thenCompose | Value to future value | Dependent asynchronous call | thenApply would leave a nested future |
| thenCombine | Two future values to one value | Required independent results | Does not automatically cancel a failed sibling |
| allOf | Several futures to future void | Wait for all stages | Retrieve typed values separately after success |
| anyOf | Several futures to first completion | Race where any completion is meaningful | First failure can win |
| exceptionally | Failure to fallback value | Optional dependency fallback | Can hide a required dependency failure |
| handle | Success or failure to new value | Deliberate result/error translation | A normal return converts failure into success |
| whenComplete | Observe value or failure | Metrics / tracing side effects | A callback exception can affect the returned stage |
| orTimeout | Complete stage exceptionally after timeout | Bound result availability | Does not stop underlying work |
| completeOnTimeout | Complete with a default after timeout | Explicit optional fallback policy | Does not stop underlying work |
| thenApplyAsync and relatives | Callback dispatched to executor | Control callback placement | Pass the executor when isolation matters |

### Thread states and progress terms

| State | Meaning | Typical trigger |
| --- | --- | --- |
| NEW | Created but not started | Constructing a Thread |
| RUNNABLE | Executing in the JVM or eligible for execution | CPU work; some underlying OS waits are also represented this way |
| BLOCKED | Waiting to enter an intrinsic monitor | Contended synchronized entry |
| WAITING | Waiting without a specified timeout | Object.wait, join, or park without timeout |
| TIMED_WAITING | Waiting with a specified timeout | sleep, timed wait/join, or timed park |
| TERMINATED | The thread's run method has ended | Normal return or uncaught failure |

- **Scheduling hints**
  - Calling run directly executes on the caller thread.
  - Calling start schedules a new thread and is allowed only once per Thread instance.
  - sleep keeps any locks already held.
  - yield and onSpinWait are hints rather than correctness protocols.
  - Thread priorities cannot enforce a business fairness contract.
  - Deprecated stop/suspend/resume are unsuitable for safe application cancellation.
- **Progress guarantees**
  - Blocking: a stalled lock owner can prevent contenders from proceeding.
  - Lock-free: the system makes progress despite some stalled threads.
  - Wait-free: each operation has a bounded number of its own steps.
  - A hand-written CAS retry loop does not automatically provide wait-free progress.
  - Non-blocking I/O describes how I/O is awaited, not a proof that the application algorithm is lock-free.

- **Default decision**
  - Start with ownership and a clearly stated invariant.
  - Choose the simplest primitive that makes that invariant atomic.
  - Add a separate limit for queued work and for each scarce dependency.
  - Replace the primitive only when a capability or measurement justifies it.

<a id="concepts"></a>

## 4. Concept explanations and core snippets

<a id="concept-ownership"></a>

### 4.1. Ownership, immutability, confinement — P0

- **Why / L4 baseline**
  - Avoid races by minimizing shared mutable state before selecting a lock.
  - A thread-confined mutable object needs no synchronization
  - a shared immutable snapshot needs safe publication.
- **Common scenarios**
  - Build request-local results with ArrayList or StringBuilder.
  - Publish a complete configuration snapshot to readers.
- **Use together**
  - Use final fields for immutable structure and volatile or an atomic reference for replacement.
- **Trap**
  - A record or final reference is only shallowly immutable
  - copy mutable members and do not leak this during construction.
- **L5 extra**
  - Prefer one owner or immutable replacement when that removes a multi-field locking protocol.

→ Copy input collections.  
→ Finish construction.  
→ Publish one snapshot reference.  

```java
// Java 17
import java.util.Map;
class ConfigSnapshots {
    record Config(Map<String, Integer> limits) {
        Config { limits = Map.copyOf(limits); }
    }
    private volatile Config current = new Config(Map.of());
    void reload(Map<String, Integer> limits) { current = new Config(limits); }
    Config snapshot() { return current; }
}
```

<a id="concept-jmm"></a>

### 4.2. Java Memory Model and happens-before — P0

- **Why / L4 baseline**
  - Explain why another thread sees a completed write instead of relying on timing.
  - Synchronization establishes ordering and visibility
  - Thread.start, successful join, monitor handoff, and task submission/result retrieval provide publication edges.
- **Common scenarios**
  - Publish work to an executor.
  - Read a worker result after join or Future.get.
- **Use together**
  - Connect each shared field to its publication edge and its update protocol.
- **Trap**
  - Thread.sleep and println are not a visibility protocol
  - visibility alone does not make read-modify-write atomic.
- **L5 extra**
  - A data-race-free program still needs a correct higher-level invariant and linearization point.

→ Initialize input before start.  
→ Worker computes result.  
→ Join worker before reading result.  

```java
// Java 17
class JoinPublication {
    static int result() throws InterruptedException {
        int[] output = new int[1];
        Thread worker = new Thread(() -> output[0] = 42);
        worker.start();
        worker.join();
        return output[0];
    }
}
```

<a id="concept-monitor"></a>

### 4.3. synchronized: protect a complete invariant — P0

- **Why / L4 baseline**
  - Keep a check and its update indivisible when several fields describe one state.
  - One monitor excludes competing holders and publishes prior writes on unlock to a subsequent lock of the same monitor.
- **Common scenarios**
  - Reserve local inventory.
  - Maintain balance plus sequence number together.
- **Use together**
  - Use one private final lock or consistently synchronized instance methods.
- **Trap**
  - Locking the writer but not the reader is insufficient
  - instance and static synchronized methods lock different objects.
- **L5 extra**
  - Keep external I/O outside the critical section and identify the exact operation that takes effect atomically.

→ Acquire monitor.  
→ Validate capacity.  
→ Update stock.  
→ Release monitor.  

```java
// Java 17
class Inventory {
    private int stock;
    Inventory(int stock) {
        if (stock < 0) throw new IllegalArgumentException();
        this.stock = stock;
    }
    synchronized boolean reserve(int n) {
        if (n <= 0) throw new IllegalArgumentException();
        if (stock < n) return false;
        stock -= n;
        return true;
    }
    synchronized int remaining() { return stock; }
}
```

<a id="concept-volatile"></a>

### 4.4. volatile: flags and whole-snapshot publication — P0

- **Why / L4 baseline**
  - Let readers observe replacement state without acquiring a mutual-exclusion lock.
  - A volatile write and subsequent read of that field establish visibility and ordering, but do not lock a sequence of operations.
- **Common scenarios**
  - Publish a configuration reference.
  - Request shutdown of a CPU loop that regularly checks a flag.
- **Use together**
  - Use interruption for blocking waits and volatile for a separately needed state signal.
- **Trap**
  - volatile count++ still loses updates
  - a stop flag cannot wake a thread blocked in take or socket I/O.
- **L5 extra**
  - Read a volatile snapshot once per operation to avoid mixing two configuration versions.

→ Writer constructs a new value.  
→ Writer assigns the volatile reference.  
→ Reader captures one reference.  

```java
// Java 17
class Routing {
    record Route(String host, int port) { }
    private volatile Route route = new Route("localhost", 8080);
    void switchTo(String host, int port) { route = new Route(host, port); }
    String destination() {
        Route r = route;
        return r.host() + ":" + r.port();
    }
}
```

<a id="concept-lock"></a>

### 4.5. ReentrantLock: timed and interruptible locking — P0

- **Why / L4 baseline**
  - Bound lock waiting or support cancellation where a monitor acquisition cannot do so.
  - An explicit reentrant lock protects the same kind of invariant as synchronized and adds tryLock, lockInterruptibly, and conditions.
- **Common scenarios**
  - Fail fast when a refresh is already running.
  - Give a state mutation a bounded lock-acquisition wait.
- **Use together**
  - Release in finally only after successful acquisition
  - pass the remaining request budget to timed operations.
- **Trap**
  - Fairness can reduce throughput and does not guarantee application-level fairness
  - untimed tryLock can barge even on a fair lock.
- **L5 extra**
  - Choose it for required capabilities, not an assumption that explicit locks are inherently faster.

→ Attempt timed acquisition.  
→ Return overload result if unavailable.  
→ Mutate under lock.  
→ Unlock in finally.  

```java
// Java 17
import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.ReentrantLock;
class TimedCounter {
    private final ReentrantLock lock = new ReentrantLock();
    private int count;
    boolean increment(long waitNanos) throws InterruptedException {
        if (!lock.tryLock(waitNanos, TimeUnit.NANOSECONDS)) return false;
        try { count++; return true; }
        finally { lock.unlock(); }
    }
}
```

<a id="concept-atomic"></a>

### 4.6. Atomic variables, CAS loops, atomic references — P0

- **Why / L4 baseline**
  - Perform a conditional update on one variable without a user-managed lock.
  - Compare-and-set succeeds only if the observed value still matches
  - retry after interference.
- **Common scenarios**
  - Allocate a process-local sequence with AtomicLong.
  - Reserve a bounded number of seats.
  - Replace an immutable multi-field state with AtomicReference.
- **Use together**
  - Put fields that must move together into one immutable state object before CAS.
- **Trap**
  - Two atomics do not form one transaction
  - update functions may execute repeatedly and must not send emails or charge a card.
- **L5 extra**
  - CAS can starve under contention
  - ABA requires versioning such as AtomicStampedReference when identity returning to A matters.

→ Read current count.  
→ Reject exhausted state.  
→ CAS decremented count.  
→ Retry on contention.  

```java
// Java 17
import java.util.concurrent.atomic.AtomicInteger;
class AtomicSeats {
    private final AtomicInteger seats;
    AtomicSeats(int n) {
        if (n < 0) throw new IllegalArgumentException();
        seats = new AtomicInteger(n);
    }
    boolean take() {
        for (;;) {
            int old = seats.get();
            if (old == 0) return false;
            if (seats.compareAndSet(old, old - 1)) return true;
        }
    }
}
```

<a id="concept-chm"></a>

### 4.7. ConcurrentHashMap: atomic per-key operations — P0

- **Why / L4 baseline**
  - Allow concurrent key access without one global map monitor.
  - compute, merge, putIfAbsent, and conditional replace offer atomic operations at a key
  - a get followed by put remains a separate sequence.
- **Common scenarios**
  - Count events by user with merge.
  - Elect a same-key loader by putIfAbsent.
- **Use together**
  - Store immutable values or give each mutable value its own synchronization protocol.
- **Trap**
  - Do not perform slow network I/O inside computeIfAbsent
  - size and iteration are not an atomic whole-map snapshot.
- **L5 extra**
  - Cross-key invariants require an outer protocol
  - cache eviction and loader ownership must use compatible identities.

→ Find or create one key state.  
→ Perform a short atomic remapping.  
→ Return immutable result.  

```java
// Java 17
import java.util.concurrent.ConcurrentHashMap;
class UserCounts {
    private final ConcurrentHashMap<String, Long> counts = new ConcurrentHashMap<>();
    long record(String user) { return counts.merge(user, 1L, Long::sum); }
    long count(String user) { return counts.getOrDefault(user, 0L); }
}
```

<a id="concept-queue"></a>

### 4.8. BlockingQueue and bounded producer/consumer handoff — P0

- **Why / L4 baseline**
  - Decouple producers from consumers without unbounded retained work.
  - A bounded queue serializes insertion/removal and coordinates waiting for space or data.
- **Common scenarios**
  - Feed a small set of file writers.
  - Buffer database batches within an explicit memory budget.
- **Use together**
  - Use offer for rejection, timed offer for bounded waiting, and a lifecycle protocol for drain and stop.
- **Trap**
  - Queue capacity bounds item count, not bytes
  - LinkedBlockingQueue without a capacity is effectively unbounded.
- **L5 extra**
  - A queue admits work but supplies no durable acknowledgement across process failure.

→ Try to enqueue immutable work.  
→ Reject if full.  
→ Consumer takes and owns one item.  

```java
// Java 17
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;
class Inbox {
    private final BlockingQueue<String> queue = new ArrayBlockingQueue<>(128);
    boolean submit(String line) { return queue.offer(line); }
    String next() throws InterruptedException { return queue.take(); }
}
```

<a id="concept-executor"></a>

### 4.9. ExecutorService and bounded ThreadPoolExecutor — P0

- **Why / L4 baseline**
  - Separate task submission from thread creation and impose an overload policy.
  - A pool uses workers plus a queue
  - after core workers, tasks normally queue before the pool grows toward maximum size.
- **Common scenarios**
  - Run CPU work on a bounded platform-thread pool.
  - Isolate a blocking legacy dependency in its own pool.
- **Use together**
  - Pair bounded queues with rejection handling and owner-controlled shutdown.
- **Trap**
  - newFixedThreadPool has an unbounded queue
  - CallerRunsPolicy can block request/event-loop threads and silently drops work after shutdown.
- **L5 extra**
  - Choose capacity from service time, tolerated queue delay, and downstream capacity
  - measure queue age rather than only depth.

→ Create bounded workers and queue.  
→ Submit or receive rejection.  
→ Owner drains and shuts down.  

```java
// Java 17
import java.util.concurrent.*;
class BoundedPools {
    static ThreadPoolExecutor cpu(int workers, int backlog) {
        var sequence = new java.util.concurrent.atomic.AtomicInteger();
        ThreadFactory names = task -> {
            Thread thread = new Thread(task, "cpu-" + sequence.incrementAndGet());
            thread.setUncaughtExceptionHandler((t, e) -> System.err.println(t.getName() + ": " + e));
            return thread;
        };
        return new ThreadPoolExecutor(workers, workers, 0L, TimeUnit.MILLISECONDS,
            new ArrayBlockingQueue<>(backlog), names, new ThreadPoolExecutor.AbortPolicy());
    }
}
```

<a id="concept-future"></a>

### 4.10. Runnable, Callable, Future, FutureTask — P0

- **Why / L4 baseline**
  - Represent a task result, failure, cancellation request, and bounded wait.
  - Callable returns a value
  - submit returns a Future
  - get exposes completion or wraps a task failure in ExecutionException.
- **Common scenarios**
  - Fetch one expensive result with a deadline.
  - Run the same FutureTask from competing callers while computing it at most once.
- **Use together**
  - Use an executor for execution and Future.get for bounded observation
  - cancel owned tasks when abandoning their result.
- **Trap**
  - get(timeout) only limits the wait
  - cancel(true) requests interruption and cannot undo an external write.
- **L5 extra**
  - Do not block a worker waiting for a child queued to the same saturated pool.

→ Submit callable.  
→ Wait within budget.  
→ On abandonment request cancellation.  

```java
// Java 17
import java.util.concurrent.*;
class FutureCalls {
    static <T> T call(ExecutorService pool, Callable<T> task, long ms)
            throws InterruptedException, ExecutionException, TimeoutException {
        Future<T> f = pool.submit(task);
        try { return f.get(ms, TimeUnit.MILLISECONDS); }
        finally { if (!f.isDone()) f.cancel(true); }
    }
}
```

<a id="concept-completable"></a>

### 4.11. CompletableFuture and CompletionStage composition — P0

- **Why / L4 baseline**
  - Compose dependent asynchronous stages without blocking a worker at every boundary.
  - thenApply maps a value
  - thenCompose flattens an async dependency
  - thenCombine joins two values.
- **Common scenarios**
  - Read user then asynchronously fetch permissions.
  - Combine independently fetched profile and preferences.
- **Use together**
  - Provide explicit executors for blocking stages and preserve exceptional completion unless fallback is intentional.
- **Trap**
  - Non-async callbacks may run on a completing thread
  - default async callbacks commonly use the common pool
  - cancel(true) does not interrupt a supplyAsync computation.
- **L5 extra**
  - Timeout completion is not resource cancellation
  - allOf waits for all completions and anyOf means first completion, including failure.

→ Receive first async result.  
→ Compose the dependent async stage.  
→ Combine with independent work.  

```java
// Java 17
import java.util.concurrent.*;
import java.util.function.*;
class FuturePipeline {
    static CompletableFuture<String> start(Executor io, Supplier<String> load) {
        return CompletableFuture.supplyAsync(load, io);
    }
    static CompletableFuture<String> compose(CompletableFuture<String> user,
            Function<String, CompletableFuture<String>> permissions,
            CompletableFuture<String> preferences) {
        return user.thenCompose(permissions)
            .thenCombine(preferences, (a, b) -> a + ":" + b);
    }
    static CompletableFuture<String> optional(CompletableFuture<String> stage) {
        return stage.exceptionally(failure -> "unavailable");
    }
}
```

<a id="concept-interrupt"></a>

### 4.12. Interruption, cancellation, and time budgets — P0

- **Why / L4 baseline**
  - Let task owners request cooperative termination and stop indefinite waiting.
  - Interruptible blocking methods throw InterruptedException
  - CPU loops must inspect the interrupt flag themselves.
- **Common scenarios**
  - Stop a queue consumer.
  - Cancel a CPU scan after its caller times out.
- **Use together**
  - Propagate InterruptedException when possible
  - otherwise restore the flag and exit the task.
- **Trap**
  - Catching interruption and continuing loses cancellation
  - Thread.interrupted clears the flag whereas isInterrupted does not.
- **L5 extra**
  - Pass one monotonic deadline through queue, lock, network, and result waits instead of resetting a full timeout at each layer.

→ Check cancellation during chunks.  
→ Exit by throwing InterruptedException.  
→ Owner observes failure or cancellation.  

```java
// Java 17
class InterruptibleScan {
    static long sum(int[] input) throws InterruptedException {
        long total = 0;
        for (int i = 0; i < input.length; i++) {
            if ((i & 1023) == 0 && Thread.currentThread().isInterrupted())
                throw new InterruptedException();
            total += input[i];
        }
        return total;
    }
}
```

<a id="concept-deadlock"></a>

### 4.13. Deadlock, lock ordering, starvation, livelock — P0

- **Why / L4 baseline**
  - Prevent cyclic waiting when an operation touches multiple resources.
  - A stable total order on lock acquisition removes cycles for operations obeying that order.
- **Common scenarios**
  - Transfer between two in-memory accounts.
  - Update two independently locked partitions.
- **Use together**
  - Use immutable unique ordering keys and keep all paths consistent, including callbacks.
- **Trap**
  - Timeouts detect some waits but do not repair an invariant
  - immediate retries can create livelock.
- **L5 extra**
  - Thread-pool starvation is also dependency waiting, even when no Java monitor deadlock exists.

→ Sort resources by unique ID.  
→ Acquire lower ID then higher ID.  
→ Update both while holding both.  

```java
// Java 17
class OrderedAccounts {
    static final class Account {
        final long id;
        long cents;
        Account(long id, long cents) { this.id = id; this.cents = cents; }
    }
    static void transfer(Account from, Account to, long cents) {
        if (cents <= 0) throw new IllegalArgumentException();
        if (from == to) return;
        if (from.id == to.id) throw new IllegalArgumentException("IDs must be unique");
        Account first = from.id < to.id ? from : to;
        Account second = from.id < to.id ? to : from;
        synchronized (first) {
            synchronized (second) {
                if (from.cents < cents) throw new IllegalStateException("insufficient");
                long updated = Math.addExact(to.cents, cents);
                from.cents -= cents;
                to.cents = updated;
            }
        }
    }
}
```

<a id="concept-semaphore"></a>

### 4.14. Semaphore: bound concurrent resource use — P0

- **Why / L4 baseline**
  - Protect a dependency with fewer slots than the number of runnable requests.
  - A permit count limits simultaneous entrants
  - it does not establish a requests-per-second policy.
- **Common scenarios**
  - Bound active JDBC calls.
  - Bound third-party requests made by virtual threads.
- **Use together**
  - Acquire before consuming the resource and release only after that resource is actually no longer in use.
- **Trap**
  - Releasing after acquisition failed inflates capacity
  - a large number of waiting callers can still exhaust memory.
- **L5 extra**
  - Use admission before task creation or immediate rejection to bound waiting as well as execution.

→ Try to acquire one slot.  
→ Execute dependency call.  
→ Release in finally.  

```java
// Java 17
import java.util.concurrent.*;
class Bulkhead {
    private final Semaphore slots;
    Bulkhead(int max) {
        if (max <= 0) throw new IllegalArgumentException();
        slots = new Semaphore(max);
    }
    <T> T call(Callable<T> operation) throws Exception {
        if (!slots.tryAcquire()) throw new RejectedExecutionException("busy");
        try { return operation.call(); }
        finally { slots.release(); }
    }
}
```

<a id="concept-virtual"></a>

### 4.15. Virtual threads: blocking I/O at high concurrency — P0

- **Why / L4 baseline**
  - Make a thread-per-task style affordable for many mostly-waiting operations.
  - The JVM schedules virtual threads on carrier platform threads and can unmount them during supported blocking operations.
- **Common scenarios**
  - Serve independent blocking HTTP requests.
  - Run blocking JDBC calls while enforcing a database concurrency limit.
- **Use together**
  - Use one virtual thread per task with a semaphore or admission gate for scarce resources.
- **Trap**
  - More virtual threads do not add CPU cores, connections, or remote quota
  - do not pool virtual threads just to cap concurrency.
- **L5 extra**
  - Java 21-23 monitor-related pinning differs from Java 24+
  - still avoid long lock-held I/O and investigate native-code pinning.

→ Admit task at ingress.  
→ Start one virtual thread.  
→ Wait using blocking code.  
→ Join through the result handle.  

```java
// Java 21
import java.util.concurrent.*;
class VirtualCalls {
    static String run() throws Exception {
        try (ExecutorService tasks = Executors.newVirtualThreadPerTaskExecutor()) {
            Future<String> f = tasks.submit(() -> "result");
            return f.get();
        }
    }
}
```

<a id="concept-lifecycle"></a>

### 4.16. ThreadFactory, execution errors, shutdown, join — P0

- **Why / L4 baseline**
  - Ensure every task has an owner responsible for errors and termination.
  - shutdown rejects new work while allowing accepted work to finish
  - shutdownNow requests interruption and returns queued tasks that never started.
- **Common scenarios**
  - Drain service-owned workers on stop.
  - Name threads to connect dumps with dependency pools.
- **Use together**
  - Inspect submitted futures for task exceptions
  - uncaught-exception handlers are insufficient for errors captured by submit.
- **Trap**
  - Daemon threads do not keep the JVM alive
  - executor shutdown cannot forcibly terminate an interrupt-ignoring task.
- **L5 extra**
  - If shutdownNow returns queued FutureTasks, cancel them so their waiters do not wait for tasks that will never run.

→ Stop acceptance.  
→ Wait for graceful drain.  
→ Interrupt on expiry.  
→ Cancel returned pending futures.  

```java
// Java 17
import java.util.List;
import java.util.concurrent.*;
class PoolLifecycle {
    static void stop(ExecutorService pool) throws InterruptedException {
        pool.shutdown();
        try {
            if (!pool.awaitTermination(1, TimeUnit.SECONDS)) {
                cancelPending(pool.shutdownNow());
                if (!pool.awaitTermination(1, TimeUnit.SECONDS))
                    throw new IllegalStateException("tasks did not stop");
            }
        } catch (InterruptedException e) {
            cancelPending(pool.shutdownNow());
            throw e;
        }
    }
    private static void cancelPending(List<Runnable> pending) {
        for (Runnable r : pending) if (r instanceof Future<?> f) f.cancel(false);
    }
}
```

<a id="concept-condition"></a>

### 4.17. Condition: wait for a protected predicate — P1

- **Why / L4 baseline**
  - Suspend until a state transition makes an operation legal instead of polling.
  - await releases its associated lock and reacquires it before returning
  - separate condition queues express different predicates.
- **Common scenarios**
  - Wait for a buffer to become nonempty.
  - Pause workers until a service becomes ready.
- **Use together**
  - Change state and signal while holding the same lock
  - always recheck the predicate in a while loop.
- **Trap**
  - Signals are not stored events
  - spurious wakeups and other awakened contenders require the loop.
- **L5 extra**
  - Prefer BlockingQueue for standard bounded buffers
  - use Conditions for a custom invariant with several wait predicates.

→ Acquire lock.  
→ Await while not ready.  
→ Recheck after reacquisition.  
→ Proceed.  

```java
// Java 17
import java.util.concurrent.locks.*;
class ReadyGate {
    private final ReentrantLock lock = new ReentrantLock();
    private final Condition changed = lock.newCondition();
    private boolean ready;
    void awaitReady() throws InterruptedException {
        lock.lockInterruptibly();
        try { while (!ready) changed.await(); }
        finally { lock.unlock(); }
    }
    void open() {
        lock.lock();
        try { ready = true; changed.signalAll(); }
        finally { lock.unlock(); }
    }
}
```

<a id="concept-wait"></a>

### 4.18. Object.wait, notify, notifyAll — P1

- **Why / L4 baseline**
  - Understand intrinsic-monitor coordination used by legacy code and interviews.
  - wait releases only the target monitor
  - notifyAll makes its waiters eligible to reacquire that monitor.
- **Common scenarios**
  - Implement a one-shot promise for an interview.
  - Read legacy producer/consumer code.
- **Use together**
  - Guard the predicate and notification with synchronized on the exact same object.
- **Trap**
  - sleep does not release monitors
  - notification without ownership throws
  - notifying before a waiter arrives is safe only if the predicate records the event.
- **L5 extra**
  - Use CountDownLatch or CompletableFuture when their lifecycle already matches the problem.

→ Wait while incomplete.  
→ Publisher stores result and marks completion.  
→ Notify all waiters.  

```java
// Java 17
class MonitorPromise<T> {
    private boolean done;
    private T result;
    synchronized void complete(T value) {
        if (done) throw new IllegalStateException("already completed");
        result = value;
        done = true;
        notifyAll();
    }
    synchronized T get() throws InterruptedException {
        while (!done) wait();
        return result;
    }
}
```

<a id="concept-rwlock"></a>

### 4.19. ReentrantReadWriteLock: consistent multi-key reads — P1

- **Why / L4 baseline**
  - Allow concurrent readers while preserving a single protected data structure.
  - Read holders coexist
  - a write holder excludes both readers and other writers.
- **Common scenarios**
  - Snapshot an in-memory catalog.
  - Read several keys consistently against local writes.
- **Use together**
  - All access to the underlying HashMap must follow the read/write protocol.
- **Trap**
  - Do not upgrade while holding a read lock
  - release it, acquire write, and recheck
  - tiny reads may be slower than a simple lock.
- **L5 extra**
  - Downgrading write to read is possible, but benchmark writer latency and starvation under the actual workload.

→ Acquire read lock.  
→ Copy a consistent snapshot.  
→ Release read lock.  

```java
// Java 17
import java.util.*;
import java.util.concurrent.locks.*;
class Catalog {
    private final ReentrantReadWriteLock lock = new ReentrantReadWriteLock();
    private final Map<String, String> data = new HashMap<>();
    void put(String k, String v) {
        lock.writeLock().lock();
        try { data.put(k, v); }
        finally { lock.writeLock().unlock(); }
    }
    Map<String, String> snapshot() {
        lock.readLock().lock();
        try { return Map.copyOf(data); }
        finally { lock.readLock().unlock(); }
    }
}
```

<a id="concept-adder"></a>

### 4.20. LongAdder and LongAccumulator: contended metrics — P1

- **Why / L4 baseline**
  - Reduce contention when many threads update a metric that does not require an atomic snapshot.
  - Updates can spread across internal cells
  - reading combines their values.
- **Common scenarios**
  - Count requests by status.
  - Accumulate a maximum observed payload size.
- **Use together**
  - Use ConcurrentHashMap of adders for a bounded set of metric dimensions.
- **Trap**
  - sum during updates is not an atomic snapshot
  - never enforce a strict quota using sum followed by increment.
- **L5 extra**
  - High-cardinality labels still exhaust memory
  - sumThenReset can lose the meaning of an exact interval during concurrent writes.

→ Update a striped metric.  
→ Aggregate for observation.  
→ Keep correctness decisions elsewhere.  

```java
// Java 17
import java.util.concurrent.atomic.*;
class Metrics {
    final LongAdder requests = new LongAdder();
    final LongAccumulator maxBytes = new LongAccumulator(Long::max, 0);
    void record(long bytes) { requests.increment(); maxBytes.accumulate(bytes); }
}
```

<a id="concept-threadlocal"></a>

### 4.21. ThreadLocal and task context — P1

- **Why / L4 baseline**
  - Carry data tied to one executing thread through a synchronous call chain.
  - Each thread has its own binding
  - a reused pool thread retains a binding until it is removed or replaced.
- **Common scenarios**
  - Legacy request correlation context.
  - A bounded platform pool with an expensive non-thread-safe helper.
- **Use together**
  - Prefer explicit parameters
  - if using ThreadLocal, establish and clean up context at task boundaries.
- **Trap**
  - InheritableThreadLocal copies at thread creation, not executor submission
  - CompletableFuture callbacks do not automatically inherit request context.
- **L5 extra**
  - Per-thread caches can become per-request allocation at virtual-thread scale
  - consider ScopedValue for immutable context on Java 25.

→ Capture context explicitly.  
→ Set for this task.  
→ Run operation.  
→ Remove in finally.  

```java
// Java 17
class RequestContext {
    private static final ThreadLocal<String> REQUEST = new ThreadLocal<>();
    static void run(String id, Runnable task) {
        String previous = REQUEST.get();
        REQUEST.set(id);
        try { task.run(); }
        finally {
            if (previous == null) REQUEST.remove();
            else REQUEST.set(previous);
        }
    }
    static String current() { return REQUEST.get(); }
}
```

<a id="concept-latch"></a>

### 4.22. CountDownLatch: one-shot completion or startup — P1

- **Why / L4 baseline**
  - Wait for a fixed number of independent events to finish.
  - countDown moves a one-way count toward zero
  - await waits for zero and observes preceding published work.
- **Common scenarios**
  - Wait until all workers initialize.
  - Coordinate a concurrency test without sleeps.
- **Use together**
  - Count down in finally so task failure cannot leave the waiter blocked forever.
- **Trap**
  - The latch reports completion, not task success
  - use futures or a separate error channel.
- **L5 extra**
  - Submitting more latch-waiting workers than the pool has threads can prevent the remaining workers from ever starting.

→ Create count for submitted tasks.  
→ Each task records success or failure.  
→ Every task counts down.  
→ Await within budget.  

```java
// Java 17
import java.util.concurrent.*;
class LatchWork {
    static void run(Executor executor, Runnable task, CountDownLatch done) {
        try {
            executor.execute(() -> {
                try { task.run(); }
                finally { done.countDown(); }
            });
        } catch (RejectedExecutionException e) {
            done.countDown();
            throw e;
        }
    }
}
```

<a id="concept-scheduler"></a>

### 4.23. ScheduledExecutorService: refresh and periodic work — P1

- **Why / L4 baseline**
  - Schedule delayed work without inventing a sleeping management thread.
  - Fixed delay measures from completion to the next start
  - fixed rate targets a recurring schedule.
- **Common scenarios**
  - Refresh configuration after each completed attempt.
  - Periodically clean up local expired state.
- **Use together**
  - Keep scheduler callbacks short and observe failures
  - dispatch slow work only through bounded admission.
- **Trap**
  - An exception escaping a periodic task suppresses later executions
  - fixed-rate scheduling does not make an overrun disappear.
- **L5 extra**
  - A JVM scheduler is neither durable nor cluster-wide singleton scheduling.

→ Schedule after previous completion.  
→ Run refresh.  
→ Record ordinary failure.  
→ Continue next interval.  

```java
// Java 17
import java.util.concurrent.*;
class RefreshSchedule {
    static ScheduledFuture<?> start(ScheduledExecutorService timer, Runnable refresh) {
        return timer.scheduleWithFixedDelay(() -> {
            try { refresh.run(); }
            catch (RuntimeException e) { System.err.println("refresh failed: " + e); }
        }, 0, 30, TimeUnit.SECONDS);
    }
}
```

<a id="concept-completion"></a>

### 4.24. ExecutorCompletionService: consume completed results — P1

- **Why / L4 baseline**
  - Avoid waiting on submission order when a later task finishes earlier.
  - Completed task futures enter a completion queue that can be polled or taken.
- **Common scenarios**
  - Return the first successful replica response.
  - Stream completed batch results without head-of-line waiting.
- **Use together**
  - Retain every submitted Future so abandoned competitors can be cancelled.
- **Trap**
  - First completion may be failure
  - its default completion queue is unbounded, so bound outstanding submissions.
- **L5 extra**
  - Choose completion order for independent tasks and structured lifecycle ownership for tightly coupled subtasks.

→ Submit bounded independent tasks.  
→ Poll completed future.  
→ Read its result or failure.  

```java
// Java 17
import java.util.concurrent.*;
class CompletedResults {
    static <T> T next(CompletionService<T> completed, long nanos)
            throws InterruptedException, ExecutionException, TimeoutException {
        Future<T> f = completed.poll(nanos, TimeUnit.NANOSECONDS);
        if (f == null) throw new TimeoutException();
        return f.get();
    }
}
```

<a id="concept-forkjoin"></a>

### 4.25. ForkJoinPool and parallel streams: CPU decomposition — P1

- **Why / L4 baseline**
  - Divide a large independent CPU workload into tasks whose overhead is smaller than their useful work.
  - Fork/join workers steal tasks to balance uneven recursive work.
- **Common scenarios**
  - Aggregate a large numeric array.
  - Transform independent in-memory records without blocking I/O.
- **Use together**
  - Use a deliberate CPU pool and a measured cutoff
  - fork one side, compute the other, then join.
- **Trap**
  - Tiny tasks lose to overhead
  - shared mutable stream side effects race
  - parallel streams may contend for the common pool.
- **L5 extra**
  - For unavoidable blocking in custom fork/join code investigate ManagedBlocker, but prefer a separate I/O execution model.

→ Split sufficiently large range.  
→ Fork one half.  
→ Compute other half.  
→ Join and combine.  

```java
// Java 17
import java.util.concurrent.RecursiveTask;
class ParallelSum extends RecursiveTask<Long> {
    private final int[] values;
    private final int lo, hi;
    ParallelSum(int[] values, int lo, int hi) { this.values = values; this.lo = lo; this.hi = hi; }
    protected Long compute() {
        if (hi - lo <= 4096) {
            long sum = 0;
            for (int i = lo; i < hi; i++) sum += values[i];
            return sum;
        }
        int mid = (lo + hi) >>> 1;
        ParallelSum left = new ParallelSum(values, lo, mid);
        left.fork();
        long right = new ParallelSum(values, mid, hi).compute();
        return left.join() + right;
    }
}
```

<a id="concept-scoped"></a>

### 4.26. ScopedValue: bounded immutable request context — P1

- **Why / L4 baseline**
  - Bind context for one dynamic call scope without leaving mutable thread-local state behind.
  - where(...).run/call establishes a binding that disappears when the call scope exits.
- **Common scenarios**
  - Pass an authenticated principal down a synchronous call chain.
  - Share immutable context with structured child tasks.
- **Use together**
  - Bind an immutable record
  - ordinary executor submissions need explicit propagation rather than assumed inheritance.
- **Trap**
  - A binding does not make its referenced object immutable
  - this is not general shared storage.
- **L5 extra**
  - Use it on Java 25 as a final API
  - Java 21-24 variants were preview APIs and should not be mixed with the shown version.

→ Bind one request value.  
→ Invoke nested calls.  
→ Read binding.  
→ Exit scope and remove binding automatically.  

```java
// Java 25
class ScopedContext {
    private static final ScopedValue<String> USER = ScopedValue.newInstance();
    static String handle(String user) throws Exception {
        return ScopedValue.where(USER, user).call(() -> "hello " + USER.get());
    }
}
```

<a id="concept-diagnostics"></a>

### 4.27. Thread states, dumps, contention, and diagnostics — P1

- **Why / L4 baseline**
  - Distinguish CPU saturation, lock contention, queue delay, and dependency waiting before changing thread counts.
  - Thread state and stack traces locate waits
  - pool metrics locate backlog
  - duration measurements identify where a budget is spent.
- **Common scenarios**
  - Investigate a monitor deadlock.
  - Separate active worker count from completed throughput and queue age.
- **Use together**
  - Use JDK tools such as jcmd and JFR alongside application metrics and request IDs.
- **Trap**
  - BLOCKED is monitor acquisition, not every kind of wait
  - ThreadMXBean does not provide a complete virtual-thread inventory.
- **L5 extra**
  - A clean deadlock detector result does not rule out starvation, logical waiting cycles, or a stuck downstream service.

→ Detect monitor/ownable-synchronizer cycles.  
→ Print participating platform-thread stacks.  
→ Correlate with queue and dependency timings.  

```java
// Java 17
import java.lang.management.*;
class DeadlockReport {
    static void report() {
        ThreadMXBean bean = ManagementFactory.getThreadMXBean();
        long[] ids = bean.findDeadlockedThreads();
        if (ids == null) return;
        for (ThreadInfo info : bean.getThreadInfo(ids, true, true))
            System.err.println(info);
    }
}
```

<a id="concept-atomicstate"></a>

### 4.28. AtomicReference, stamped references, arrays, and field updaters — P1

- **Why / L4 baseline**
  - Atomically replace a multi-field logical value without mixing fields from different versions.
  - An AtomicReference CAS compares reference identity and replaces the whole immutable state.
- **Common scenarios**
  - Update balance and sequence together.
  - Use AtomicIntegerArray for independent per-slot state.
  - Use AtomicStampedReference when detecting A-to-B-to-A matters.
- **Use together**
  - Keep retry functions pure and publish immutable values
  - stamp updates belong in the same CAS as the reference.
- **Trap**
  - An atomic array makes individual slots atomic, not the entire array
  - field updaters require their field and access contracts to be respected.
- **L5 extra**
  - Use a lock when retry work is expensive or several resources cannot be represented by one immutable state.

→ Read one immutable state.  
→ Construct replacement.  
→ CAS the whole state.  
→ Retry without repeating external side effects.  

```java
// Java 17
import java.util.concurrent.atomic.AtomicReference;
class AtomicBalance {
    record State(long cents, long version) { }
    private final AtomicReference<State> state = new AtomicReference<>(new State(0, 0));
    State add(long cents) {
        return state.updateAndGet(old -> new State(
            Math.addExact(old.cents(), cents), Math.addExact(old.version(), 1)));
    }
    State get() { return state.get(); }
}
```

<a id="concept-stamped"></a>

### 4.29. StampedLock: optimistic reads — P2

- **Why / L4 baseline**
  - Reduce read-side lock traffic for short snapshots that tolerate retry.
  - Read fields into locals under an optimistic stamp, validate, and fall back to a real read lock on interference.
- **Common scenarios**
  - Read a coordinate pair.
  - Read a small numeric statistics snapshot.
- **Use together**
  - Writers must use the same StampedLock
  - compute on the copied values only after validation.
- **Trap**
  - It is not reentrant
  - optimistic traversal of a mutable HashMap is unsafe because traversal may fail before validation.
- **L5 extra**
  - Prefer immutable snapshot publication unless allocation or update patterns justify this extra protocol.

→ Obtain optimistic stamp.  
→ Copy fields.  
→ Validate.  
→ On failure recopy under read lock.  

```java
// Java 17
import java.util.concurrent.locks.StampedLock;
class PointSnapshot {
    private final StampedLock lock = new StampedLock();
    private double x, y;
    void set(double a, double b) {
        long s = lock.writeLock();
        try { x = a; y = b; }
        finally { lock.unlockWrite(s); }
    }
    double distance() {
        long s = lock.tryOptimisticRead();
        double a = x, b = y;
        if (!lock.validate(s)) {
            s = lock.readLock();
            try { a = x; b = y; }
            finally { lock.unlockRead(s); }
        }
        return Math.hypot(a, b);
    }
}
```

<a id="concept-barrier"></a>

### 4.30. CyclicBarrier: reusable fixed-party rendezvous — P2

- **Why / L4 baseline**
  - Make a fixed team finish each round before any member starts the next.
  - All parties call await
  - the last arrival triggers an optional barrier action and releases the round.
- **Common scenarios**
  - Iterative simulations.
  - Parallel algorithms with repeated reduction rounds.
- **Use together**
  - Allocate enough execution capacity for all blocking parties and handle broken rounds as group failure.
- **Trap**
  - A missing party can hang the team
  - interruption or timeout breaks the barrier for the waiting group.
- **L5 extra**
  - Use Phaser when membership changes instead of trying to manually reset a live barrier.

→ Compute local round.  
→ Await all fixed parties.  
→ Advance together.  

```java
// Java 17
import java.util.concurrent.*;
class RoundWorker {
    static void round(CyclicBarrier barrier, Runnable localWork)
            throws InterruptedException, BrokenBarrierException, TimeoutException {
        localWork.run();
        barrier.await(1, TimeUnit.SECONDS);
    }
}
```

<a id="concept-phaser"></a>

### 4.31. Phaser: dynamic parties and phases — P2

- **Why / L4 baseline**
  - Coordinate phases when the number of participating tasks changes.
  - Register before submission, arrive at a phase boundary, and deregister when a party permanently leaves.
- **Common scenarios**
  - Coordinate a dynamically discovered batch.
  - Track a parent and its submitted worker set.
- **Use together**
  - Deregister on rejection and in task finally
  - use a separate error channel for failures.
- **Trap**
  - Registering inside the worker is too late if the parent can advance first
  - non-interruptible waits need deliberate cancellation policy.
- **L5 extra**
  - A phase number proves participation completed, not that an operation committed successfully.

→ Register before submit.  
→ Worker runs.  
→ Worker deregisters even on failure.  

```java
// Java 17
import java.util.concurrent.*;
class PhasedWork {
    static void submit(Phaser phaser, Executor executor, Runnable task) {
        phaser.register();
        try {
            executor.execute(() -> {
                try { task.run(); }
                finally { phaser.arriveAndDeregister(); }
            });
        } catch (RejectedExecutionException e) {
            phaser.arriveAndDeregister();
            throw e;
        }
    }
}
```

<a id="concept-cow"></a>

### 4.32. CopyOnWriteArrayList and synchronized wrappers — P2

- **Why / L4 baseline**
  - Choose collection iteration semantics explicitly instead of assuming every thread-safe list behaves alike.
  - Copy-on-write publishes a fresh backing array for mutation
  - synchronized wrappers serialize individual operations on one monitor.
- **Common scenarios**
  - Read-mostly listener registries with snapshot iteration.
  - Small legacy collections whose compound operations can use one monitor.
- **Use together**
  - Use addIfAbsent for atomic duplicate prevention
  - externally synchronize wrapper iteration on the wrapper object.
- **Trap**
  - Copy-on-write copies references rather than mutable element state
  - frequent writes and large arrays create allocation cost.
- **L5 extra**
  - Removing a listener cannot retract a callback already captured in a reader snapshot.

→ Register rarely.  
→ Traverse a stable snapshot.  
→ Dispatch each callback.  

```java
// Java 17
import java.util.concurrent.CopyOnWriteArrayList;
class Listeners {
    private final CopyOnWriteArrayList<Runnable> listeners = new CopyOnWriteArrayList<>();
    void add(Runnable r) { listeners.addIfAbsent(r); }
    void fire() {
        for (Runnable r : listeners) {
            try { r.run(); }
            catch (RuntimeException e) { System.err.println(e); }
        }
    }
}
```

<a id="concept-sorted"></a>

### 4.33. ConcurrentSkipListMap and ordered concurrent sets — P2

- **Why / L4 baseline**
  - Maintain concurrent sorted navigation when a hash map cannot answer range queries.
  - A concurrent skip-list structure supports ordered key traversal and conditional map updates.
- **Common scenarios**
  - Maintain a local time-ordered index.
  - Query currently visible items in a key range.
- **Use together**
  - Use unique tie-breakers in keys when many items share a timestamp.
- **Trap**
  - Range traversal is weakly consistent, not a transaction snapshot
  - a local sorted map is not a durable scheduler.
- **L5 extra**
  - Use a read/write-locked TreeMap when atomic range snapshots matter more than independent-key concurrency.

→ Insert composite ordered key.  
→ Traverse desired range.  
→ Treat result as a weak snapshot.  

```java
// Java 17
import java.util.*;
import java.util.concurrent.ConcurrentSkipListMap;
class OrderedIndex {
    private final ConcurrentSkipListMap<Long, String> entries = new ConcurrentSkipListMap<>();
    void put(long uniqueId, String value) { entries.put(uniqueId, value); }
    List<String> between(long from, long to) {
        return List.copyOf(entries.subMap(from, true, to, false).values());
    }
}
```

<a id="concept-handoff"></a>

### 4.34. SynchronousQueue, transfer queues, and Exchanger — P2

- **Why / L4 baseline**
  - Coordinate direct ownership handoff when buffering is not the desired contract.
  - SynchronousQueue has no element capacity
  - TransferQueue can await consumer receipt
  - Exchanger rendezvous swaps two objects.
- **Common scenarios**
  - Reject when no worker is ready for direct handoff.
  - Exchange full and empty buffers between two pipeline stages.
- **Use together**
  - Use timed operations to avoid a vanished partner blocking forever.
- **Trap**
  - Consumer receipt is not business completion
  - LinkedTransferQueue is unbounded when using ordinary offer/put.
- **L5 extra**
  - Prefer a bounded BlockingQueue unless a rendezvous contract is specifically required.

→ Offer to an already-waiting consumer.  
→ Time out if no handoff occurs.  

```java
// Java 17
import java.util.concurrent.*;
class DirectHandoff {
    final SynchronousQueue<String> rendezvous = new SynchronousQueue<>();
    boolean send(String value) throws InterruptedException {
        return rendezvous.offer(value, 10, TimeUnit.MILLISECONDS);
    }
    String receive() throws InterruptedException { return rendezvous.take(); }
    static byte[] exchange(Exchanger<byte[]> pair, byte[] owned) throws Exception {
        return pair.exchange(owned, 1, TimeUnit.SECONDS);
    }
}
```

<a id="concept-structured"></a>

### 4.35. Structured concurrency: child-task lifetime ownership — P2

- **Why / L4 baseline**
  - Keep related subtasks within the lifetime of the parent operation.
  - A task scope forks children, joins under a join policy, and closes after its children terminate.
- **Common scenarios**
  - Fetch two required pieces of one response.
  - Cancel siblings when an all-required fan-out fails.
- **Use together**
  - Combine virtual threads, immutable ScopedValue context, and resource bulkheads.
- **Trap**
  - StructuredTaskScope is preview in the Java 25 API used here
  - closing still waits for children that ignore cancellation.
- **L5 extra**
  - Java 26 has a sixth preview
  - pin examples to a release rather than copying older ShutdownOnFailure examples into Java 25.

→ Open scope.  
→ Fork required subtasks.  
→ Join with failure propagation.  
→ Combine successful values.  
→ Close child lifetime.  

```java
// Java 25-preview
import java.util.concurrent.StructuredTaskScope;
class StructuredCalls {
    static String combine() throws InterruptedException {
        try (var scope = StructuredTaskScope.open()) {
            var a = scope.fork(() -> "profile");
            var b = scope.fork(() -> "preferences");
            scope.join();
            return a.get() + ":" + b.get();
        }
    }
}
```

<a id="concept-varhandle"></a>

### 4.36. VarHandle and explicit memory access modes — P2

- **Why / L4 baseline**
  - Implement a carefully proven low-level publication protocol without Unsafe.
  - A VarHandle exposes plain, opaque, acquire/release, volatile, and atomic access modes for a selected variable.
- **Common scenarios**
  - Understand concurrent-library internals.
  - Publish a one-writer payload using a release flag and acquire read.
- **Use together**
  - Prefer volatile or AtomicReference for application code
  - use weaker modes only with a complete memory-order proof.
- **Trap**
  - Acquire/release on a flag does not make later mutations of the published object safe
  - opaque access is not publication.
- **L5 extra**
  - Benchmark and reason about the Java memory model rather than assuming x86 behavior is the specification.

→ Write payload once.  
→ Release-publish ready.  
→ Acquire-read ready.  
→ Read published payload.  

```java
// Java 17
import java.lang.invoke.*;
class ReleasePublication {
    private int payload;
    private boolean ready;
    private static final VarHandle READY;
    static {
        try { READY = MethodHandles.lookup().findVarHandle(ReleasePublication.class, "ready", boolean.class); }
        catch (ReflectiveOperationException e) { throw new ExceptionInInitializerError(e); }
    }
    void publishOnce(int value) { payload = value; READY.setRelease(this, true); }
    Integer read() { return (boolean) READY.getAcquire(this) ? payload : null; }
}
```

<a id="concept-park"></a>

### 4.37. LockSupport and AQS internals — P2

- **Why / L4 baseline**
  - Understand how higher-level synchronizers park contenders and signal progress.
  - LockSupport gives a thread at most one permit
  - AQS combines atomic state with queued acquisition policies.
- **Common scenarios**
  - Read ReentrantLock or Semaphore internals.
  - Explain why park must be inside a predicate loop.
- **Use together**
  - Publish the predicate with volatile or atomics
  - use standard synchronizers for application-level protocols.
- **Trap**
  - park can return spuriously or on interrupt
  - unpark calls do not accumulate like semaphore permits.
- **L5 extra**
  - A custom AQS synchronizer needs ownership, interruption, fairness, and serialization decisions beyond a successful CAS.

→ Publish waiter identity.  
→ Recheck predicate before each park.  
→ Opener publishes state and unparks waiter.  

```java
// Java 17
import java.util.concurrent.locks.LockSupport;
class SingleWaiterGate {
    private volatile boolean open;
    private volatile Thread waiter;
    void await() throws InterruptedException {
        waiter = Thread.currentThread(); // Contract: exactly one waiter.
        while (!open) {
            if (Thread.interrupted()) throw new InterruptedException();
            LockSupport.park(this);
        }
    }
    void open() { open = true; LockSupport.unpark(waiter); }
}
```

<a id="concept-flow"></a>

### 4.38. Flow API: demand-based asynchronous delivery — P2

- **Why / L4 baseline**
  - Express consumer demand when building an asynchronous stream of items.
  - Publisher, Subscriber, Subscription, and Processor define a protocol in which request(n) grants demand.
- **Common scenarios**
  - Integrate a JDK publisher with a demand-aware consumer.
  - Understand backpressure in asynchronous streaming APIs.
- **Use together**
  - Coordinate publisher buffer limits with downstream asynchronous work, not just onNext return time.
- **Trap**
  - Flow is an interface protocol, not a complete processing framework
  - SubmissionPublisher.submit can block on slow subscribers.
- **L5 extra**
  - Requesting another item immediately after launching unbounded async work defeats downstream admission control.

→ Store subscription.  
→ Request one item.  
→ Finish processing it.  
→ Request the next item.  

```java
// Java 17
import java.util.concurrent.Flow;
class PrintSubscriber implements Flow.Subscriber<String> {
    private Flow.Subscription subscription;
    public void onSubscribe(Flow.Subscription s) { subscription = s; s.request(1); }
    public void onNext(String item) { System.out.println(item); subscription.request(1); }
    public void onError(Throwable failure) { System.err.println(failure); }
    public void onComplete() { System.out.println("complete"); }
}
```

<a id="concept-delayed"></a>

### 4.39. DelayQueue and priority queues: eligibility versus capacity — P2

- **Why / L4 baseline**
  - Select work by due time or priority rather than FIFO arrival.
  - DelayQueue.take waits until the head delay expires
  - PriorityBlockingQueue selects an available priority head without waiting for a due timestamp.
- **Common scenarios**
  - Build a small local expiration worker.
  - Prioritize an admitted set of local work items.
- **Use together**
  - Use an independent admission bound and a unique sequence tie-breaker when stable ordering matters.
- **Trap**
  - Both queues are unbounded by default
  - mutable priorities invalidate heap ordering unless the item is removed and reinserted.
- **L5 extra**
  - Prefer ScheduledExecutorService for ordinary delayed tasks
  - neither choice creates durable scheduled execution.

→ Construct an immutable due-time item.  
→ Offer under a separate capacity policy.  
→ Consumer takes only after it becomes eligible.  

```java
// Java 17
import java.util.concurrent.*;
class DueItem implements Delayed {
    final String key;
    private final long due;
    DueItem(String key, long delayNanos) {
        if (delayNanos < 0 || delayNanos > TimeUnit.DAYS.toNanos(365))
            throw new IllegalArgumentException();
        this.key = key; due = System.nanoTime() + delayNanos;
    }
    public long getDelay(TimeUnit unit) {
        return unit.convert(due - System.nanoTime(), TimeUnit.NANOSECONDS);
    }
    public int compareTo(Delayed other) {
        return Long.compare(due - ((DueItem) other).due, 0L);
    }
}
```

<a id="case-map"></a>

## 5. Cases grouped by the problem being solved

### A. Admission and dependency protection

| Priority | Case / local detail | Core combination |
| --- | --- | --- |
| P0 | [Per-user exact sliding-window rate limiter](#case-rate) | Fixed lock stripes + one HashMap per stripe + per-user ArrayDeque of accepted timestamps. |
| P0 | [Third-party HTTP: reusable client, deadline, bulkhead](#case-http) | HttpClient.send + Semaphore + blocking platform or virtual caller threads. |
| P1 | [Token bucket for controlled bursts](#case-token) | One synchronized token state; combine with the semaphore bulkhead to bound concurrent downstream calls. |
| P1 | [Bounded retry with backoff and one end-to-end deadline](#case-retry) | A monotonic deadline + interruptible sleep + an explicit retryable error type. |

### B. Shared in-memory state

| Priority | Case / local detail | Core combination |
| --- | --- | --- |
| P0 | [Thread-safe bounded LRU cache with TTL](#case-cache) | A synchronized access-order LinkedHashMap; immutable entries; no network or database call while locked. |
| P0 | [Coalesce concurrent cache misses for the same key](#case-singleflight) | ConcurrentHashMap + FutureTask + bounded admission + an injected executor with explicit rejection. |
| P0 | [Versioned in-memory KV store: compare-and-set writes](#case-kv) | ConcurrentHashMap.compute + an immutable versioned record; no mutable value is exposed. |
| P1 | [Process-local idempotency for an in-memory operation](#case-dedup) | One synchronized state owner for the business value and its deduplication map. |

### C. Database and external side effects

| Priority | Case / local detail | Core combination |
| --- | --- | --- |
| P0 | [Database access and conditional transactional writes](#case-db) | JDK JDBC interfaces + Semaphore + conditional UPDATE; a supplied DataSource provides real connections. |
| P1 | [Bounded write-behind queue with acknowledgement](#case-batch) | ArrayBlockingQueue + one worker thread + CompletableFuture per accepted job. |

### D. Task orchestration and CPU work

| Priority | Case / local detail | Core combination |
| --- | --- | --- |
| P0 | [Fan-out: first successful result with loser cancellation](#case-fanout) | ExecutorCompletionService + retained Future handles + a monotonic elapsed-time budget. |
| P0 | [Virtual-thread service with admission before task creation](#case-admission) | Virtual-thread-per-task executor + ingress Semaphore; dependency-specific bulkheads remain separate. |
| P1 | [Bounded CPU batch with isolated execution](#case-cpu) | ThreadPoolExecutor + invokeAll(timeout) for a small homogeneous batch. |

### E. Background work and context

| Priority | Case / local detail | Core combination |
| --- | --- | --- |
| P1 | [Immutable configuration refresh without overlapping runs](#case-refresh) | Volatile immutable state + one fixed-delay scheduler + a deadline-aware loader. |

### F. End-to-end composition

| Priority | Case / local detail | Core combination |
| --- | --- | --- |
| P0 | [Combine admission, per-user quota, cache, single flight, and I/O](#case-combined) | Compose the prior AdmittedVirtualTasks, SlidingWindow, TtlLru, SingleFlight, and PartnerApi patterns. |

<a id="cases"></a>

## 6. Case walkthroughs and core code

<a id="case-rate"></a>

### 6.1. Per-user exact sliding-window rate limiter — P0

- **Group**
  - A. Admission and dependency protection
- **Context**
  - An authenticated user can submit at most N requests in the last W nanoseconds to this JVM.
- **Classic requirement / L4**
  - Count accepted requests in the interval (now - W, now].
  - Serialize each user's prune/check/append operation.
  - Bound retained user identities and use monotonic elapsed time.
- **Core combination**
  - Fixed lock stripes + one HashMap per stripe + per-user ArrayDeque of accepted timestamps.

→ Select a stable stripe from the user ID.  
→ Lock stripe and read monotonic time.  
→ Remove expired timestamps.  
→ Reject if quota or identity capacity is exhausted.  
→ Append this acceptance timestamp.  

```java
// Java 17
import java.util.*;
import java.util.function.LongSupplier;
class SlidingWindow {
    private static final class Stripe {
        final Map<String, ArrayDeque<Long>> users = new HashMap<>();
    }
    private final Stripe[] stripes;
    private final int limit, maxUsersPerStripe;
    private final long windowNanos;
    private final LongSupplier clock;
    SlidingWindow(int limit, long windowNanos, int stripeCount,
                  int maxUsersPerStripe, LongSupplier clock) {
        if (limit <= 0 || windowNanos <= 0 || stripeCount <= 0 || maxUsersPerStripe <= 0)
            throw new IllegalArgumentException();
        this.limit = limit;
        this.windowNanos = windowNanos;
        this.maxUsersPerStripe = maxUsersPerStripe;
        this.clock = Objects.requireNonNull(clock);
        stripes = new Stripe[stripeCount];
        for (int i = 0; i < stripeCount; i++) stripes[i] = new Stripe();
    }
    boolean allow(String user) {
        Objects.requireNonNull(user);
        Stripe stripe = stripes[Math.floorMod(user.hashCode(), stripes.length)];
        synchronized (stripe) {
            long now = clock.getAsLong();
            ArrayDeque<Long> q = stripe.users.get(user);
            if (q == null) {
                if (stripe.users.size() >= maxUsersPerStripe) {
                    stripe.users.entrySet().removeIf(e ->
                        now - e.getValue().peekLast() >= windowNanos);
                }
                if (stripe.users.size() >= maxUsersPerStripe) return false;
                q = new ArrayDeque<>();
                stripe.users.put(user, q);
            }
            while (!q.isEmpty() && now - q.peekFirst() >= windowNanos) q.removeFirst();
            if (q.size() >= limit) return false;
            q.addLast(now);
            return true;
        }
    }
}
```

- **Failure boundaries / traps**
  - Use System::nanoTime in production and a controlled monotonic clock in tests.
  - The stripe lock protects both the map entry lifecycle and the queue
  - removing independently locked per-user objects can create two live locks for one user.
  - Memory is bounded by stripeCount × maxUsersPerStripe × limit timestamp entries, plus collection overhead.
  - Pruning costs O(limit) worst case for an acceptance after a long idle period
  - capacity cleanup scans O(maxUsersPerStripe).
  - Identity capacity can reject a new user even when other stripes have space
  - report this overload separately from quota exhaustion.
  - The guarantee is local to one JVM
  - several replicas need shared authoritative admission or an explicitly partitioned quota.
- **L5 extra / follow-up**
  - For smoother bursts choose a token bucket
  - for lower memory choose approximate bucketed rolling counts and explain boundary error.

<a id="case-http"></a>

### 6.2. Third-party HTTP: reusable client, deadline, bulkhead — P0

- **Group**
  - A. Admission and dependency protection
- **Context**
  - Many request handlers call a slower partner that can sustain only a bounded number of active calls.
- **Classic requirement / L4**
  - Reject excess in-flight work promptly.
  - Reuse one HttpClient.
  - Set connection and per-request timeouts.
  - Release a slot on success, failure, or interruption.
- **Core combination**
  - HttpClient.send + Semaphore + blocking platform or virtual caller threads.

→ Try dependency permit.  
→ Build a timed request.  
→ Send and inspect status.  
→ Release permit after send returns or throws.  

```java
// Java 17
import java.io.IOException;
import java.net.URI;
import java.net.http.*;
import java.time.Duration;
import java.util.concurrent.*;
class PartnerApi {
    private final Semaphore active = new Semaphore(32);
    private final HttpClient client = HttpClient.newBuilder()
        .connectTimeout(Duration.ofSeconds(2)).build();
    String get(URI uri, Duration remaining) throws IOException, InterruptedException {
        if (!active.tryAcquire()) throw new RejectedExecutionException("partner busy");
        try {
            HttpRequest request = HttpRequest.newBuilder(uri).timeout(remaining).GET().build();
            HttpResponse<String> r = client.send(request, HttpResponse.BodyHandlers.ofString());
            if (r.statusCode() < 200 || r.statusCode() >= 300)
                throw new IOException("partner status=" + r.statusCode());
            return r.body();
        } finally { active.release(); }
    }
}
```

- **Failure boundaries / traps**
  - The example assumes a trusted bounded response body
  - ofString buffers the body in memory.
  - A permit bounds active local send operations
  - remote execution can outlive local cancellation or a timeout.
  - The sample values are illustrative capacities, not production defaults.
  - Retry only classified transient failures and only when the operation is safe or the remote API honors an idempotency key.
- **L5 extra / follow-up**
  - For async HTTP, retain the original sendAsync future for cancellation and keep CPU-heavy response parsing on a dedicated executor.

<a id="case-token"></a>

### 6.3. Token bucket for controlled bursts — P1

- **Group**
  - A. Admission and dependency protection
- **Context**
  - An API permits short bursts but should converge to a configured average rate.
- **Classic requirement / L4**
  - Refill tokens according to elapsed monotonic time.
  - Cap accumulated credit at burst capacity.
  - Check and consume under one lock.
- **Core combination**
  - One synchronized token state
  - combine with the semaphore bulkhead to bound concurrent downstream calls.

→ Refill by elapsed time.  
→ Clamp to capacity.  
→ Reject without enough credit.  
→ Consume one token.  

```java
// Java 17
import java.util.function.LongSupplier;
class TokenBucket {
    private final double capacity, perNano;
    private final LongSupplier clock;
    private double tokens;
    private long last;
    TokenBucket(int capacity, double perSecond, LongSupplier clock) {
        if (capacity <= 0 || !Double.isFinite(perSecond) || perSecond <= 0)
            throw new IllegalArgumentException();
        this.capacity = this.tokens = capacity;
        this.perNano = perSecond / 1_000_000_000.0;
        this.clock = clock;
        last = clock.getAsLong();
    }
    synchronized boolean allow() {
        long now = clock.getAsLong();
        tokens = Math.min(capacity, tokens + (now - last) * perNano);
        last = now;
        if (tokens < 1) return false;
        tokens -= 1;
        return true;
    }
}
```

- **Failure boundaries / traps**
  - A token bucket is not the exact sliding-window contract.
  - Floating-point credit is suitable for this local example
  - specify precision and rate ranges for strict accounting.
- **L5 extra / follow-up**
  - Decide whether a rejected downstream call consumes quota
  - a different refund policy changes the public contract.

<a id="case-retry"></a>

### 6.4. Bounded retry with backoff and one end-to-end deadline — P1

- **Group**
  - A. Admission and dependency protection
- **Context**
  - A read-only partner call sometimes returns a transient failure but unlimited retries would amplify an outage.
- **Classic requirement / L4**
  - Cap attempts.
  - Reuse one total time budget.
  - Add bounded jitter to delay.
  - Propagate interruption.
  - Let the operation set its own I/O timeout from the remaining budget.
- **Core combination**
  - A monotonic deadline + interruptible sleep + an explicit retryable error type.

→ Compute remaining budget.  
→ Attempt using that budget.  
→ Retry only a classified transient failure.  
→ Sleep with jitter within budget.  
→ Stop at attempt or time limit.  

```java
// Java 17
import java.util.concurrent.*;
class RetryRead {
    static final class TransientFailure extends Exception { }
    interface Attempt<T> { T run(long remainingNanos) throws Exception; }
    static <T> T call(Attempt<T> operation, long budgetNanos) throws Exception {
        if (budgetNanos <= 0) throw new TimeoutException();
        long start = System.nanoTime();
        for (int attempt = 0; ; attempt++) {
            if (Thread.currentThread().isInterrupted()) throw new InterruptedException();
            long remaining = budgetNanos - (System.nanoTime() - start);
            if (remaining <= 0) throw new TimeoutException();
            try { return operation.run(remaining); }
            catch (TransientFailure e) {
                if (attempt == 2) throw e;
                remaining = budgetNanos - (System.nanoTime() - start);
                long cap = TimeUnit.MILLISECONDS.toNanos(20L << attempt);
                long delay = ThreadLocalRandom.current().nextLong(cap + 1);
                if (remaining <= delay) throw new TimeoutException();
                TimeUnit.NANOSECONDS.sleep(delay);
            }
        }
    }
}
```

- **Failure boundaries / traps**
  - Release dependency permits between attempts and before sleeping.
  - A timeout after a write may mean the write committed
  - retrying it requires remote deduplication.
  - Retrying in every layer multiplies the load
  - designate one layer as the retry owner.
- **L5 extra / follow-up**
  - Add a circuit breaker only when fast failure is a desired outage policy
  - model closed/open/half-open state plus a bounded number of probes.

<a id="case-cache"></a>

### 6.5. Thread-safe bounded LRU cache with TTL — P0

- **Group**
  - B. Shared in-memory state
- **Context**
  - Several request threads share a small process-local cache whose eviction order and TTL must remain consistent.
- **Classic requirement / L4**
  - Atomically read value and update recency.
  - Bound entry count.
  - Expire using elapsed monotonic time.
  - Treat the cache as reconstructible state.
- **Core combination**
  - A synchronized access-order LinkedHashMap
  - immutable entries
  - no network or database call while locked.

→ Acquire cache monitor.  
→ Look up and update recency.  
→ Remove expired entry.  
→ Return value or miss.  

```java
// Java 17
import java.util.*;
import java.util.function.LongSupplier;
class TtlLru<K, V> {
    private record Entry<V>(V value, long writtenAt) { }
    private final LinkedHashMap<K, Entry<V>> data = new LinkedHashMap<>(16, .75f, true);
    private final int capacity;
    private final long ttlNanos;
    private final LongSupplier clock;
    TtlLru(int capacity, long ttlNanos, LongSupplier clock) {
        if (capacity <= 0 || ttlNanos <= 0) throw new IllegalArgumentException();
        this.capacity = capacity; this.ttlNanos = ttlNanos; this.clock = clock;
    }
    synchronized V get(K key) {
        Entry<V> e = data.get(key);
        if (e == null) return null;
        if (clock.getAsLong() - e.writtenAt() >= ttlNanos) {
            data.remove(key); return null;
        }
        return e.value();
    }
    synchronized void put(K key, V value) {
        data.put(Objects.requireNonNull(key), new Entry<>(Objects.requireNonNull(value), clock.getAsLong()));
        while (data.size() > capacity) data.remove(data.keySet().iterator().next());
    }
    synchronized void invalidate(K key) { data.remove(key); }
    synchronized int size() { return data.size(); }
}
```

- **Failure boundaries / traps**
  - An access-order get mutates recency and therefore cannot use only a read lock.
  - TTL is checked on get
  - unused expired entries can remain resident, but total entry count is bounded.
  - Values must be immutable or defensively copied
  - returning a mutable value exposes an independent race.
  - Entry capacity does not bound bytes when values have arbitrary size.
- **L5 extra / follow-up**
  - Shard for throughput if approximate global LRU is acceptable
  - strict global recency remains a shared coordination point.

<a id="case-singleflight"></a>

### 6.6. Coalesce concurrent cache misses for the same key — P0

- **Group**
  - B. Shared in-memory state
- **Context**
  - A popular expired key causes many simultaneous requests to execute the same expensive load.
- **Classic requirement / L4**
  - Share one in-flight Future per key.
  - Run the loader outside map operations.
  - Bound the number of distinct in-flight keys.
  - Let a waiting caller time out without cancelling shared work.
- **Core combination**
  - ConcurrentHashMap + FutureTask + bounded admission + an injected executor with explicit rejection.

→ Read an existing flight.  
→ Elect a leader using putIfAbsent.  
→ Leader schedules the loader.  
→ All callers await the same future.  
→ Remove only the exact completed flight.  

```java
// Java 17
import java.util.concurrent.*;
class SingleFlight<K, V> {
    private final ConcurrentHashMap<K, FutureTask<V>> flights = new ConcurrentHashMap<>();
    private final Semaphore slots;
    private final Executor executor;
    SingleFlight(int maxKeys, Executor executor) {
        if (maxKeys <= 0) throw new IllegalArgumentException();
        slots = new Semaphore(maxKeys); this.executor = executor;
    }
    V get(K key, Callable<V> load, long waitNanos) throws Exception {
        java.util.Objects.requireNonNull(key);
        java.util.Objects.requireNonNull(load);
        FutureTask<V> f = flights.get(key);
        if (f == null) {
            if (!slots.tryAcquire()) throw new RejectedExecutionException("too many loading keys");
            FutureTask<V> mine = new FutureTask<>(load);
            FutureTask<V> existing = flights.putIfAbsent(key, mine);
            if (existing != null) { slots.release(); f = existing; }
            else {
                f = mine;
                try {
                    executor.execute(() -> {
                        try { mine.run(); }
                        finally { flights.remove(key, mine); slots.release(); }
                    });
                } catch (RuntimeException e) {
                    mine.cancel(false);
                    flights.remove(key, mine);
                    slots.release();
                    throw e;
                }
            }
        }
        return f.get(waitNanos, TimeUnit.NANOSECONDS);
    }
}
```

- **Failure boundaries / traps**
  - The loader must enforce its own I/O deadline
  - a waiter timeout does not stop the loader.
  - Require an executor that either accepts execution or throws
  - discard policies would strand the flight and permit.
  - The executor owner must drain accepted tasks before shutdown
  - shutdownNow can remove the cleanup wrapper before it runs.
  - On a race at full admission capacity a caller may be rejected even though a same-key flight just appeared
  - retry policy can recheck the map if needed.
  - This is only in-flight deduplication
  - cache the successful value separately.
- **L5 extra / follow-up**
  - Recheck TtlLru inside the elected loader before fetching
  - cache invalidation during an old load requires a generation/version fence to prevent stale repopulation.

<a id="case-kv"></a>

### 6.7. Versioned in-memory KV store: compare-and-set writes — P0

- **Group**
  - B. Shared in-memory state
- **Context**
  - Two clients read the same value and then attempt conflicting updates.
- **Classic requirement / L4**
  - Return a value with its version.
  - Accept a write only when its expected version still matches.
  - Update value and version together.
- **Core combination**
  - ConcurrentHashMap.compute + an immutable versioned record
  - no mutable value is exposed.

→ Read value and version.  
→ Submit new value with expected version.  
→ Atomically validate and replace.  
→ Report conflict when validation fails.  

```java
// Java 17
import java.util.Objects;
import java.util.concurrent.ConcurrentHashMap;
class VersionedKv {
    record Value(String text, long version) { }
    private final ConcurrentHashMap<String, Value> data = new ConcurrentHashMap<>();
    Value get(String key) { return data.get(key); }
    Value put(String key, long expectedVersion, String text) {
        Objects.requireNonNull(text);
        return data.compute(key, (k, old) -> {
            long version = old == null ? 0 : old.version();
            if (version != expectedVersion) throw new IllegalStateException("version conflict");
            return new Value(text, Math.addExact(version, 1));
        });
    }
}
```

- **Failure boundaries / traps**
  - The contract covers one key in one JVM and does not survive restart.
  - Adding delete must preserve a version/tombstone policy
  - resetting a recreated key to version 1 can let stale clients succeed.
  - Two compute calls on separate keys do not make an atomic transfer.
- **L5 extra / follow-up**
  - For atomic multi-key snapshots use the Catalog read/write lock
  - for durable transactions move arbitration into the database.

<a id="case-dedup"></a>

### 6.8. Process-local idempotency for an in-memory operation — P1

- **Group**
  - B. Shared in-memory state
- **Context**
  - A retried local operation must return the same result while its deduplication record remains retained.
- **Classic requirement / L4**
  - Scope the request key to caller and operation.
  - Reject reuse with different arguments.
  - Record the result in the same critical section as the local state change.
- **Core combination**
  - One synchronized state owner for the business value and its deduplication map.

→ Look up scoped request ID.  
→ Return the recorded result if arguments match.  
→ Apply local mutation.  
→ Record result atomically before returning.  

```java
// Java 17
import java.util.*;
class LocalIdempotentCounter {
    record Outcome(long delta, long result) { }
    private final Map<String, Outcome> completed = new HashMap<>();
    private long value;
    synchronized long add(String scopedRequestId, long delta) {
        Outcome old = completed.get(scopedRequestId);
        if (old != null) {
            if (old.delta() != delta) throw new IllegalArgumentException("key reused with different input");
            return old.result();
        }
        if (completed.size() >= 10_000) throw new IllegalStateException("dedup capacity reached");
        long next = Math.addExact(value, delta);
        completed.put(scopedRequestId, new Outcome(delta, next));
        value = next;
        return next;
    }
}
```

- **Failure boundaries / traps**
  - Capacity exhaustion rejects new work instead of silently forgetting earlier IDs.
  - Restart loses both the data and dedup history
  - this is an in-memory illustration, not durable exactly-once processing.
  - Moving the business write into JDBC while retaining this map breaks atomicity across crashes.
- **L5 extra / follow-up**
  - For durable writes, put the idempotency key, request fingerprint, business change, and response record in one database transaction
  - retain records for the declared retry horizon.

<a id="case-db"></a>

### 6.9. Database access and conditional transactional writes — P0

- **Group**
  - C. Database and external side effects
- **Context**
  - Concurrent requests reserve database inventory while the database has limited connection capacity.
- **Classic requirement / L4**
  - Give each operation its own connection/transaction scope.
  - Limit active database operations locally.
  - Make the stock check part of the SQL write.
  - Rollback on failure and close every JDBC resource.
- **Core combination**
  - JDK JDBC interfaces + Semaphore + conditional UPDATE
  - a supplied DataSource provides real connections.

→ Acquire database slot.  
→ Obtain connection and begin transaction.  
→ Run conditional update.  
→ Commit accepted reservation or rollback.  
→ Close resources then release slot.  

```java
// Java 17
import javax.sql.DataSource;
import java.sql.*;
import java.util.concurrent.*;
class JdbcReservations {
    private final DataSource source;
    private final Semaphore slots;
    JdbcReservations(DataSource source, int maxActive) {
        if (maxActive <= 0) throw new IllegalArgumentException();
        this.source = source; slots = new Semaphore(maxActive);
    }
    boolean reserve(long sku, int quantity) throws SQLException {
        if (quantity <= 0) throw new IllegalArgumentException();
        if (!slots.tryAcquire()) throw new RejectedExecutionException("database busy");
        try (Connection c = source.getConnection()) {
            c.setAutoCommit(false);
            try {
                try (PreparedStatement s = c.prepareStatement(
                        "UPDATE inventory SET stock = stock - ? WHERE sku = ? AND stock >= ?")) {
                    s.setInt(1, quantity); s.setLong(2, sku); s.setInt(3, quantity);
                    s.setQueryTimeout(2);
                    boolean accepted = s.executeUpdate() == 1;
                    if (accepted) c.commit(); else c.rollback();
                    return accepted;
                }
            } catch (SQLException | RuntimeException e) {
                try { c.rollback(); } catch (SQLException rollback) { e.addSuppressed(rollback); }
                throw e;
            }
        } finally { slots.release(); }
    }
}
```

- **Failure boundaries / traps**
  - java.sql and javax.sql are Java SE APIs
  - executing against a database still needs an actual database and a matching JDBC driver.
  - Assume sku is unique and the database supports transactional conditional updates
  - verify the target database isolation and lock semantics.
  - The semaphore bounds one application instance
  - the database transaction handles conflicting writers across instances.
  - Query timeout is a JDBC request to the driver and does not bound connection acquisition or commit
  - configure supported login/network/transaction deadlines separately.
  - A commit exception can leave the outcome unknown
  - do not blindly retry a non-idempotent reservation.
- **L5 extra / follow-up**
  - For multi-row updates lock rows in a consistent order, retry classified deadlocks within budget, and persist an idempotency record in the same transaction.

<a id="case-batch"></a>

### 6.10. Bounded write-behind queue with acknowledgement — P1

- **Group**
  - C. Database and external side effects
- **Context**
  - Request threads hand small writes to a single owner, and callers need to know whether the sink actually succeeded.
- **Classic requirement / L4**
  - Bound the queue.
  - Acknowledge only after sink completion.
  - Complete failures exceptionally.
  - Drain queued work on normal close.
- **Core combination**
  - ArrayBlockingQueue + one worker thread + CompletableFuture per accepted job.

→ Offer immutable job with a future.  
→ Worker polls and owns the job.  
→ Write to the sink.  
→ Complete its result.  
→ On close reject new jobs and drain.  

```java
// Java 17
import java.util.concurrent.*;
class WriteBehind implements AutoCloseable {
    interface Sink { void write(String value) throws Exception; }
    private record Job(String value, CompletableFuture<Void> result) { }
    private final BlockingQueue<Job> queue = new ArrayBlockingQueue<>(128);
    private final Sink sink;
    private final Thread worker;
    private volatile boolean closed;
    WriteBehind(Sink sink) {
        this.sink = sink;
        worker = new Thread(this::drain, "write-behind");
        worker.start();
    }
    synchronized CompletableFuture<Void> submit(String value) {
        CompletableFuture<Void> result = new CompletableFuture<>();
        if (closed || !queue.offer(new Job(value, result)))
            result.completeExceptionally(new RejectedExecutionException());
        return result;
    }
    private void drain() {
        Throwable terminal = null;
        try {
            while (!closed || !queue.isEmpty()) {
                Job j = queue.poll(100, TimeUnit.MILLISECONDS);
                if (j == null) continue;
                try { sink.write(j.value()); j.result().complete(null); }
                catch (InterruptedException e) { j.result().completeExceptionally(e); throw e; }
                catch (Exception e) { j.result().completeExceptionally(e); }
                catch (Error e) { j.result().completeExceptionally(e); throw e; }
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt(); terminal = e;
        } catch (Error e) {
            terminal = e; throw e;
        } finally {
            synchronized (this) { closed = true; }
            Job j;
            Throwable failure = terminal == null ? new IllegalStateException("writer stopped") : terminal;
            while ((j = queue.poll()) != null) j.result().completeExceptionally(failure);
        }
    }
    public void close() throws InterruptedException {
        if (Thread.currentThread() == worker) throw new IllegalStateException("worker cannot join itself");
        synchronized (this) { closed = true; }
        worker.join(2000);
        if (worker.isAlive()) {
            worker.interrupt();
            throw new IllegalStateException("sink did not drain within close budget");
        }
    }
}
```

- **Failure boundaries / traps**
  - The queue is volatile memory
  - acceptance into it does not survive process failure.
  - The sink defines success: a JDBC commit is different from a buffer write or an fsync.
  - A slow completion callback may run on the writer thread
  - callers should offload heavy callbacks.
  - Cancelling the returned future does not retract an accepted write.
- **L5 extra / follow-up**
  - Batch several jobs into one JDBC transaction and acknowledge all after commit
  - on an ambiguous commit use durable request IDs before retrying the batch.

<a id="case-fanout"></a>

### 6.11. Fan-out: first successful result with loser cancellation — P0

- **Group**
  - D. Task orchestration and CPU work
- **Context**
  - Two interchangeable read replicas can answer a request
  - return the first success within one budget.
- **Classic requirement / L4**
  - Treat a failure as a failed candidate, not a successful race winner.
  - Use completion order.
  - Cancel unfinished candidates when leaving.
  - Keep the candidate count small and bounded.
- **Core combination**
  - ExecutorCompletionService + retained Future handles + a monotonic elapsed-time budget.

→ Submit bounded candidates.  
→ Poll next completion within remaining budget.  
→ Skip failed candidate.  
→ Return first success.  
→ Cancel all unfinished candidates.  

```java
// Java 17
import java.util.*;
import java.util.concurrent.*;
class FirstSuccess {
    static <T> T race(ExecutorService executor, List<Callable<T>> reads, long budgetNanos)
            throws InterruptedException, ExecutionException, TimeoutException {
        if (reads.isEmpty() || reads.size() > 8) throw new IllegalArgumentException();
        CompletionService<T> done = new ExecutorCompletionService<>(executor);
        List<Future<T>> futures = new ArrayList<>();
        long start = System.nanoTime();
        ExecutionException last = null;
        try {
            for (Callable<T> read : reads) futures.add(done.submit(read));
            for (int i = 0; i < reads.size(); i++) {
                long remaining = budgetNanos - (System.nanoTime() - start);
                if (remaining <= 0) throw new TimeoutException();
                Future<T> f = done.poll(remaining, TimeUnit.NANOSECONDS);
                if (f == null) throw new TimeoutException();
                try { return f.get(); }
                catch (ExecutionException e) { last = e; }
            }
            throw last;
        } finally {
            for (Future<T> f : futures) if (!f.isDone()) f.cancel(true);
        }
    }
}
```

- **Failure boundaries / traps**
  - Cancellation is cooperative
  - an interrupt-ignoring HTTP or database operation can keep running.
  - The completion service does not impose request-specific timeouts on the Callable itself.
  - Hedging increases load
  - use only bounded read candidates or explicitly idempotent operations.
- **L5 extra / follow-up**
  - For two required results use thenCombine or a structured all-success scope
  - anyOf is not first-success semantics.

<a id="case-admission"></a>

### 6.12. Virtual-thread service with admission before task creation — P0

- **Group**
  - D. Task orchestration and CPU work
- **Context**
  - A burst of blocking requests should not create an unbounded population of parked virtual threads.
- **Classic requirement / L4**
  - Reject before creating more tasks than the service admits.
  - Retain permits until task execution actually ends.
  - Keep cancellation-before-start safe.
  - Own executor lifetime explicitly.
- **Core combination**
  - Virtual-thread-per-task executor + ingress Semaphore
  - dependency-specific bulkheads remain separate.

→ Acquire ingress permit without waiting.  
→ Submit wrapper to virtual executor.  
→ Wrapper runs or observes prior cancellation.  
→ Wrapper finally returns ingress permit.  

```java
// Java 21
import java.util.concurrent.*;
class AdmittedVirtualTasks implements AutoCloseable {
    private final ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();
    private final Semaphore admitted;
    AdmittedVirtualTasks(int maxTasks) {
        if (maxTasks <= 0) throw new IllegalArgumentException();
        admitted = new Semaphore(maxTasks);
    }
    <T> Future<T> submit(Callable<T> operation) {
        java.util.Objects.requireNonNull(operation);
        if (!admitted.tryAcquire()) throw new RejectedExecutionException("ingress full");
        FutureTask<T> task = new FutureTask<>(operation);
        try {
            executor.execute(() -> {
                try { task.run(); }
                finally { admitted.release(); }
            });
        } catch (RuntimeException e) { admitted.release(); throw e; }
        return task;
    }
    public void close() { executor.close(); }
}
```

- **Failure boundaries / traps**
  - Do not release the permit in FutureTask.done: cancellation can complete the Future while its underlying task still runs.
  - The admitted task count is not the number of active database calls
  - layer a database semaphore separately.
  - ExecutorService.close waits for termination and may exceed an HTTP deadline if tasks ignore cancellation.
- **L5 extra / follow-up**
  - Use an application-owned executor across requests
  - do not create and close one per timed request if close would wait past the response budget.

<a id="case-cpu"></a>

### 6.13. Bounded CPU batch with isolated execution — P1

- **Group**
  - D. Task orchestration and CPU work
- **Context**
  - A request needs to transform several bounded CPU-heavy items without competing with blocking partner calls.
- **Classic requirement / L4**
  - Use a CPU-sized bounded pool.
  - Preserve input order when collecting results.
  - Cancel unfinished work at batch timeout and surface task failures.
  - Limit batch size before submitting.
- **Core combination**
  - ThreadPoolExecutor + invokeAll(timeout) for a small homogeneous batch.

→ Validate batch size.  
→ Build pure independent tasks.  
→ Invoke with one batch timeout.  
→ Read each result in input order.  

```java
// Java 17
import java.util.*;
import java.util.concurrent.*;
class CpuBatch {
    static List<Long> sum(ExecutorService cpu, List<int[]> inputs, long timeoutMillis)
            throws InterruptedException, ExecutionException {
        if (inputs.size() > 32) throw new RejectedExecutionException("batch too large");
        List<Callable<Long>> tasks = new ArrayList<>();
        for (int[] input : inputs) {
            tasks.add(() -> {
                long total = 0;
                for (int i = 0; i < input.length; i++) {
                    if ((i & 1023) == 0 && Thread.currentThread().isInterrupted())
                        throw new InterruptedException();
                    total += input[i];
                }
                return total;
            });
        }
        List<Future<Long>> done = cpu.invokeAll(tasks, timeoutMillis, TimeUnit.MILLISECONDS);
        List<Long> results = new ArrayList<>();
        for (Future<Long> f : done) results.add(f.get());
        return results;
    }
}
```

- **Failure boundaries / traps**
  - A timed-out task appears as a cancelled Future and get throws CancellationException
  - map that explicitly at the service boundary.
  - invokeAll does not fail fast when one task fails
  - it waits for all completion or the timeout.
  - The caller must own immutable inputs for the duration of computation.
- **L5 extra / follow-up**
  - For early failure use completion order and cancel remaining tasks
  - use fork/join for one large recursively divisible array.

<a id="case-refresh"></a>

### 6.14. Immutable configuration refresh without overlapping runs — P1

- **Group**
  - E. Background work and context
- **Context**
  - Readers need low-latency configuration access while an external source refreshes periodically.
- **Classic requirement / L4**
  - Publish only a completely validated immutable snapshot.
  - Keep the previous snapshot when refresh fails.
  - Avoid overlapping refreshes.
  - Observe last-success age.
- **Core combination**
  - Volatile immutable state + one fixed-delay scheduler + a deadline-aware loader.

→ Load outside reader synchronization.  
→ Validate and copy new values.  
→ Publish one snapshot.  
→ Schedule next run after this run ends.  

```java
// Java 17
import java.util.*;
import java.util.concurrent.*;
class RefreshingConfig {
    record Snapshot(Map<String, String> values, long loadedAtNanos) {
        Snapshot { values = Map.copyOf(values); }
    }
    private volatile Snapshot current = new Snapshot(Map.of(), System.nanoTime());
    Snapshot snapshot() { return current; }
    ScheduledFuture<?> start(ScheduledExecutorService timer, Callable<Map<String, String>> loader) {
        return timer.scheduleWithFixedDelay(() -> {
            try {
                Map<String, String> loaded = loader.call();
                current = new Snapshot(loaded, System.nanoTime());
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                throw new CancellationException("refresh interrupted");
            } catch (Exception e) { System.err.println("keeping prior config: " + e); }
        }, 0, 30, TimeUnit.SECONDS);
    }
}
```

- **Failure boundaries / traps**
  - Call start once per refresh owner
  - duplicate schedules can overlap.
  - A loader that never returns stalls this schedule and delays shutdown
  - enforce its external I/O deadline.
  - Record successful-load status separately if an empty initial configuration is not valid for readiness.
- **L5 extra / follow-up**
  - Expose snapshot age and define fail-open versus fail-closed behavior when configuration becomes too stale.

<a id="case-combined"></a>

### 6.15. Combine admission, per-user quota, cache, single flight, and I/O — P0

- **Group**
  - F. End-to-end composition
- **Context**
  - A read endpoint serves user-specific data with a local cache and a slower backing service.
- **Classic requirement / L4**
  - Bound total admitted requests before task creation.
  - Enforce each user's exact local rolling quota.
  - Coalesce loads for the same user and resource.
  - Return cache hits without using a downstream slot.
  - Give shared loads their own fixed timeout policy.
- **Core combination**
  - Compose the prior AdmittedVirtualTasks, SlidingWindow, TtlLru, SingleFlight, and PartnerApi patterns.

→ Acquire ingress admission.  
→ Check per-user quota.  
→ Look up scoped cache key.  
→ On miss join or create one bounded flight.  
→ Leader rechecks cache and calls a bounded downstream loader.  
→ Publish cache value and return the shared result.  

```java
// Java 21
import java.util.concurrent.*;
class CachedReadService implements AutoCloseable {
    record Key(String user, String resource) { }
    interface Loader { String load(Key key) throws Exception; }
    private final AdmittedVirtualTasks requests = new AdmittedVirtualTasks(256);
    private final ExecutorService loads = Executors.newVirtualThreadPerTaskExecutor();
    private final SlidingWindow rate = new SlidingWindow(20, TimeUnit.SECONDS.toNanos(1),
        16, 256, System::nanoTime);
    private final TtlLru<Key, String> cache = new TtlLru<>(1000,
        TimeUnit.SECONDS.toNanos(30), System::nanoTime);
    private final SingleFlight<Key, String> flights = new SingleFlight<>(128, loads);
    private final Loader loader;
    CachedReadService(Loader loader) { this.loader = loader; }
    Future<String> get(String user, String resource) {
        Key key = new Key(user, resource);
        return requests.submit(() -> {
            if (!rate.allow(user)) throw new RejectedExecutionException("quota or user-state capacity");
            String hit = cache.get(key);
            if (hit != null) return hit;
            return flights.get(key, () -> {
                String secondCheck = cache.get(key);
                if (secondCheck != null) return secondCheck;
                String value = loader.load(key);
                cache.put(key, value);
                return value;
            }, TimeUnit.SECONDS.toNanos(1));
        });
    }
    public void close() {
        requests.close();
        loads.close();
    }
}
```

- **Failure boundaries / traps**
  - This composition compiles together with the named prior snippets
  - the other snippets compile individually.
  - The injected loader must apply the PartnerApi bulkhead/deadline pattern or an equivalent bounded JDBC operation.
  - The sample charges quota for admitted cache hits and misses
  - authentication/authorization must happen before using user as the quota identity.
  - A caller timeout leaves a shared load active
  - that load still consumes one of the 128 flight slots until it ends.
  - Authorization scope belongs in the cache key
  - resource-only keys can leak one user's cached result to another.
  - There is no write/invalidate path in this read-only example
  - adding one requires stale-load fencing.
- **L5 extra / follow-up**
  - Measure ingress rejection, quota rejection, cache hit rate, flight wait duration, dependency latency, and active calls separately.


<a id="compositions"></a>

## 7. Common compositions and overload behavior

| Pattern | Compose | Ownership / atomic boundary | Overload response | Frequent defect |
| --- | --- | --- | --- | --- |
| Local rate limit | Stable stripe + timestamp deque | One user's prune/check/append | Reject current request | Cleanup creates two locks for one user |
| Thread-safe LRU | Monitor + access-order map | Lookup, recency, expiry, eviction | Evict according to contract | Treating get as read-only |
| Cache miss coalescing | CHM + FutureTask + admission | Leader identity per key | Reject a new distinct flight | One caller cancels everyone else's load |
| Versioned KV | CHM.compute + immutable version | One conditional per-key write | Return version conflict | Reusing a version after delete/recreate |
| Database write | Connection scope + SQL transaction + bulkhead | Database commit boundary | Reject before acquiring a connection | JVM lock mistaken for cross-replica protection |
| Partner API | Shared HttpClient + timeout + semaphore | Active local dependency attempt | Reject / bounded wait | Releasing capacity while the attempt still runs |
| Async fan-out | CF composition + explicit executors | Completion graph, plus separately owned tasks | Time out and cancel owned work | Assuming orTimeout cancels I/O |
| Blocking fan-out | Virtual threads + result handles / scope | Parent owns child lifetime | Admission or deadline failure | Executor close exceeds request deadline |
| Write-behind | Bounded queue + owner + acknowledgement | Sink success determines acknowledgement | Reject queue overflow | Acknowledging merely because enqueue succeeded |
| Refresh | Fixed-delay scheduler + immutable volatile snapshot | Whole validated snapshot replacement | Retain old snapshot, expose staleness | Exception silently stops future executions |
| CPU batch | Bounded CPU pool + pure tasks | Independent task inputs/results | Reject or cancel after budget | Blocking I/O occupies CPU workers |

### One request's control path

→ Authenticate and derive the real caller identity.  
→ Check ingress admission before allocating more tasks.  
→ Apply the defined per-user rate policy.  
→ Capture request context and one overall deadline.  
→ Try the cache using an authorization-safe key.  
→ On miss, join a bounded in-flight load or start one.  
→ Acquire the specific downstream permit before consuming its resource.  
→ Run I/O with the remaining operation budget.  
→ Release the downstream permit when the local operation ends.  
→ Publish a safe result and complete waiting callers.  
→ Release ingress admission after actual task termination.

- **Do not hold while waiting**
  - Cache monitor while making HTTP or JDBC calls.
  - Read lock while attempting a write-lock upgrade.
  - Connection while sleeping between retries.
  - Partner semaphore while applying retry backoff.
  - CPU-pool worker while waiting for a child queued to the same full pool.
- **Do not confuse boundaries**
  - Thread safety with persistence.
  - Visibility with compound atomicity.
  - Future completion with physical task termination.
  - Local timeout with remote rollback.
  - Concurrency limit with request rate limit.
  - An immutable wrapper with immutable reachable data.
- **Local-state failure patterns**
  - Contention: identify the hot lock/key before increasing threads.
  - Deadlock: remove acquisition cycles or resource dependency cycles.
  - Starvation: inspect fairness, executor occupancy, and missing progress.
  - Livelock: bound retries and add randomized backoff where appropriate.
  - False sharing: investigate cache-line contention only after a reproducible profile.
  - Memory growth: count waiting tasks, queued bytes, retained keys, and callbacks.
  - Silent failure: observe Future exceptions and scheduled-task termination.

<a id="questions"></a>

## 8. Interview questions: L4 + L5 extra

### Q1. Why does volatile not fix a counter?

- **L4**
  - Increment is a read, arithmetic operation, and write.
  - Two threads can observe the same old value.
  - Use an atomic increment or guard the entire operation with one lock.
- **L5 extra**
  - Decide whether the number is a correctness gate or an approximate metric.
  - LongAdder helps the second case but cannot safely enforce a strict quota.

### Q2. Why is a ConcurrentHashMap not enough for a cache?

- **L4**
  - It does not add TTL, recency, capacity, or an atomic check-then-load protocol.
  - Mutable values need their own synchronization.
- **L5 extra**
  - Specify interactions among invalidation, loader completion, and eviction.
  - An old loader needs a version check before repopulating after a write.

### Q3. Why can a thread-safe LRU need an exclusive lock on get?

- **L4**
  - A hit changes the access order.
  - Recency mutation and eviction must use the same lock protocol.
- **L5 extra**
  - Exact global LRU introduces shared contention.
  - Sharded or approximate policies trade eviction precision for concurrency.

### Q4. How do you stop a task after Future.get times out?

- **L4**
  - Request cancellation on an owned task.
  - Make blocking operations and loops respond to interruption.
- **L5 extra**
  - A remote write may already have committed.
  - A shared cache load may belong to several callers and should outlive one waiter.

### Q5. Which is better: CompletableFuture or virtual threads?

- **L4**
  - CompletableFuture expresses asynchronous dependencies.
  - Virtual threads let many blocking tasks use straightforward control flow.
- **L5 extra**
  - Neither automatically sets admission, downstream capacity, or cancellation ownership.
  - Choose based on the dependency API, team code style, and required task lifetime.

### Q6. Why can a semaphore still allow memory exhaustion?

- **L4**
  - It can limit active calls while an unbounded number of callers wait for permits.
  - Bound admission or use prompt rejection.
- **L5 extra**
  - Measure retained request state and body size as well as waiter count.
  - Separate ingress budget from each dependency's concurrency budget.

### Q7. How does the sliding-window implementation avoid a cleanup race?

- **L4**
  - Map access, deque mutation, and cleanup use the same stable stripe lock.
  - Removing a user never removes the stripe's identity.
- **L5 extra**
  - Bound key cardinality as well as events per key.
  - A multi-replica deployment needs an explicit distributed quota policy.

### Q8. Can a synchronized method prevent database overselling across replicas?

- **L4**
  - Its monitor only coordinates callers sharing that object in the same JVM.
  - Use a database conditional write or a transaction with suitable locking.
- **L5 extra**
  - Handle ambiguous commit outcomes with an idempotency protocol.
  - Test deadlocks, retry classification, and isolation on the actual database engine.

### Q9. Why can a queue-based writer report success too early?

- **L4**
  - Enqueue confirms memory admission, not sink completion.
  - Complete an acknowledgement future after the sink succeeds.
- **L5 extra**
  - State whether sink success means buffering, transaction commit, or durable flush.
  - Reconcile retry and duplicate behavior across the acknowledgement-loss window.

### Q10. What does structured concurrency add beyond allOf?

- **L4**
  - It gives related children a parent-owned lifetime and join policy.
  - Scope closure waits for child termination.
- **L5 extra**
  - Cooperative cancellation still limits termination guarantees.
  - Preview version and deployment policy affect whether the API is usable.

### Q11. What happens if a scheduled refresh throws?

- **L4**
  - An escaping exception suppresses later executions of that periodic task.
  - Catch and observe expected refresh failures if continued scheduling is intended.
- **L5 extra**
  - Preserve the last valid snapshot and expose its age.
  - Define readiness and maximum-staleness behavior explicitly.

### Q12. How would you debug high latency with low CPU?

- **L4**
  - Inspect lock waits, queued work, connection acquisition, and remote latency.
  - Use thread dumps and time measurements at each boundary.
- **L5 extra**
  - Low CPU can reflect starvation or a dependency cycle rather than too few workers.
  - For virtual threads use supported JDK dumps/JFR instead of treating platform-thread counts as request concurrency.

<a id="verification"></a>

## 9. Verification and reading order

- **Read first**
  - P0 concepts in the ranked table.
  - Sliding window.
  - LRU + single flight.
  - JDBC conditional write.
  - HTTP bulkhead + fan-out.
  - The final composition.
- **Then extend**
  - Conditions and read/write locks.
  - Metrics, scheduling, context, and batch processing.
  - Specialized P2 mechanisms only after the simpler alternative is clear.
- **Verification contract**
  - Compile Java 17 examples with `javac --release 17`.
  - Compile virtual-thread examples with `javac --release 21`.
  - Compile ScopedValue with `javac --release 25`.
  - Compile the task-scope example with `javac --enable-preview --release 25`.
  - The composition must compile with its named earlier classes.
  - Exercise contention and timeout boundaries with latches/futures and bounded waits.
  - A passing stress run provides evidence, not a proof of all possible interleavings.
  - JDBC needs separate integration testing against the actual database and driver.
- **Validation performed for this document**
  - All 54 Java snippets compiled using JDK 25.0.1 with the declared release targets.
  - 49 snippets target Java 17.
  - 3 snippets target Java 21.
  - 1 snippet targets Java 25 final APIs.
  - 1 snippet targets Java 25 preview APIs.
  - A JDK-only harness passed 80 assertions across contention, quota boundaries, cache expiry/eviction, version conflicts, shared-load timeouts, cancellation, write acknowledgement, and composition.
  - JDBC lifecycle checks used proxy implementations of its interfaces.
  - No live database or third-party endpoint was used in those checks.
  - All 64 explicit anchors are unique and all 64 internal navigation links resolve.

<a id="references"></a>

## References

- [Java concurrency APIs and memory-consistency overview](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/package-summary.html)
- [JLS happens-before rules](https://docs.oracle.com/javase/specs/jls/se25/html/jls-17.html#jls-17.4.5)
- [Atomic API family](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/atomic/package-summary.html)
- [ReentrantLock](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/locks/ReentrantLock.html)
- [StampedLock](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/locks/StampedLock.html)
- [ConcurrentHashMap](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/ConcurrentHashMap.html)
- [ThreadPoolExecutor](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/ThreadPoolExecutor.html)
- [Future](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/Future.html)
- [CompletableFuture](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/CompletableFuture.html)
- [LockSupport](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/locks/LockSupport.html)
- [Virtual-thread behavior and diagnostics](https://docs.oracle.com/en/java/javase/25/core/virtual-threads.html)
- [ScopedValue, final since Java 25](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/ScopedValue.html)
- [StructuredTaskScope, Java 25 preview](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/concurrent/StructuredTaskScope.html)
- [StructuredTaskScope, Java 26 preview](https://docs.oracle.com/en/java/javase/26/docs/api/java.base/java/util/concurrent/StructuredTaskScope.html)
- [JDBC Connection contract](https://docs.oracle.com/en/java/javase/25/docs/api/java.sql/java/sql/Connection.html)
- [HttpClient lifecycle and cancellation](https://docs.oracle.com/en/java/javase/25/docs/api/java.net.http/java/net/http/HttpClient.html)
