# 1concurrency — Concurrency In One Walkthrough (Java + Python)

- **In plain words:** concurrency means several things are in progress at once, like a kitchen with several cooks. The hard part is the shared stuff (the one stove, the one fridge): two cooks grabbing it at the same moment is where bugs come from.
- A quick, high-level view with minimal code; the deep version with every case is [1concurrency-c.md](1concurrency-c.md)
- Java gets small snippets; Python gets the core modules and classes, with one or two snippets
- Related: [1dissys.md](1dissys.md) (the same problems across machines)

## Index

- [0. One-Minute Version](#0-one-minute-version)
- [1. Concurrency vs Parallelism, Threads vs Processes](#1-concurrency-vs-parallelism-threads-vs-processes)
- [2. The Three Problems: Atomicity, Visibility, Ordering](#2-the-three-problems-atomicity-visibility-ordering)
- [3. Java Toolbox](#3-java-toolbox)
  - [3.1 synchronized](#31-synchronized)
  - [3.2 volatile](#32-volatile)
  - [3.3 Explicit locks](#33-explicit-locks)
  - [3.4 Atomics and CAS](#34-atomics-and-cas)
  - [3.5 Concurrent collections](#35-concurrent-collections)
  - [3.6 Thread pools and executors](#36-thread-pools-and-executors)
  - [3.7 CompletableFuture](#37-completablefuture)
  - [3.8 Coordination: latch, semaphore, barrier](#38-coordination-latch-semaphore-barrier)
  - [3.9 ThreadLocal](#39-threadlocal)
  - [3.10 Virtual threads (Java 21)](#310-virtual-threads-java-21)
- [4. Deadlock And Other Liveness Failures](#4-deadlock-and-other-liveness-failures)
- [5. Picking The Tool](#5-picking-the-tool)
- [6. Python Concurrency](#6-python-concurrency)
  - [6.1 The GIL](#61-the-gil)
  - [6.2 The core modules](#62-the-core-modules)
  - [6.3 Which one when](#63-which-one-when)
- [7. Java vs Python Side By Side](#7-java-vs-python-side-by-side)
- [8. Failure Modes](#8-failure-modes)
- [9. Interview Questions](#9-interview-questions)
- [10. Where This Fits](#10-where-this-fits)
- [References](#references)

---

## 0. One-Minute Version

- **What:** running several tasks so they overlap in time, on one core (interleaving) or many (parallel)
- **Why:** keep CPUs busy and keep waiting on I/O (DB, HTTP) from blocking everything else
- **How:** threads share memory, so shared mutable state needs protection
  - Make the update atomic (lock, CAS), make it visible (happens-before), or don't share (immutability, confinement, message passing)
- **Catch:** races, deadlocks and pool exhaustion; bugs show up only under load and rarely reproduce
- 🗣 "First I avoid sharing; if I must share, I pick the smallest tool that protects the invariant: atomic, then concurrent collection, then lock."

## 1. Concurrency vs Parallelism, Threads vs Processes

- **In plain words:** concurrency is juggling several tasks; parallelism is several hands working at the same instant.

| Term | Meaning | Example |
|---|---|---|
| Concurrency | Tasks overlap in time, maybe on one core | A web server handling 200 requests on 8 cores |
| Parallelism | Tasks run at the same instant on different cores | A parallel sort splitting an array across cores |
| Process | Own memory space; isolated; costly to create and switch | Separate JVMs, Python `multiprocessing` workers |
| Thread | Shares its process's memory; cheaper; can corrupt shared data | Tomcat request threads |
| Virtual thread / coroutine | Very cheap task scheduled by the runtime, not the OS | Java 21 virtual threads, Python `asyncio` tasks |

- I/O-bound work (waiting on network or disk) gains from concurrency; CPU-bound work gains only from parallelism

## 2. The Three Problems: Atomicity, Visibility, Ordering

- **In plain words:** a "simple" `count++` is really three steps (read, add, write), and other threads can sneak in between them or see stale values.

1. **Atomicity:** a compound action must happen all at once
   - `count++` = read → add → write; two threads can both read 5 and both write 6
2. **Visibility:** a write on one core may sit in a cache and stay invisible to another thread
   - A `boolean running` flag that one thread never sees change
3. **Ordering:** the compiler and CPU may reorder instructions
   - Double-checked locking without `volatile` can publish a half-built object

- The fix for all three in Java is a **happens-before** relationship: lock release → acquire, `volatile` write → read, thread start / join, and `java.util.concurrent` handoffs
- 🗣 "A race needs shared, mutable state and at least one writer; remove any one of the three and the race is gone."

## 3. Java Toolbox

- **In plain words:** Java gives a ladder of tools, from a simple lock word to whole thread pools; climb only as high as you need.

### 3.1 synchronized

- One thread at a time inside the block; also makes writes visible to the next thread that takes the same lock
- Reentrant: the same thread can enter again
```java
class Counter {
    private int count;
    synchronized void inc() { count++; }        // atomic + visible
    synchronized int get() { return count; }
}
```
- Catch: lock on a private object, not on `this` or a shared String; keep the block short

### 3.2 volatile

- Guarantees visibility and ordering for one variable; no atomicity for compound actions
```java
private volatile boolean running = true;        // stop flag seen by the worker
void stop() { running = false; }
```
- Use for flags and safe publication; `volatile int count; count++` is still a race

### 3.3 Explicit locks

- `ReentrantLock`: `tryLock` with timeout, interruptible waits, optional fairness, several `Condition`s
- `ReadWriteLock`: many readers or one writer; good for read-heavy data
- `StampedLock`: optimistic reads, faster but not reentrant
```java
private final ReentrantLock lock = new ReentrantLock();
void transfer() {
    if (lock.tryLock()) {                        // or tryLock(100, MILLISECONDS)
        try { /* critical section */ } finally { lock.unlock(); }
    }
}
```
- Catch: always unlock in `finally`

### 3.4 Atomics and CAS

- Compare-and-swap (CAS): "set to new value only if it is still the old value", done by one CPU instruction, retried on conflict
- `AtomicInteger`, `AtomicLong`, `AtomicReference`, `LongAdder` (better under heavy contention)
```java
private final AtomicInteger hits = new AtomicInteger();
void hit() { hits.incrementAndGet(); }           // lock-free
```
- Catch: CAS covers one variable; an invariant across two variables needs a lock or an immutable object swapped via `AtomicReference`

### 3.5 Concurrent collections

| Class | Use | Note |
|---|---|---|
| `ConcurrentHashMap` | Shared map | `computeIfAbsent` / `merge` are atomic per key; `get` then `put` is not |
| `CopyOnWriteArrayList` | Read-mostly lists (listeners) | Every write copies the array |
| `ArrayBlockingQueue` / `LinkedBlockingQueue` | Producer-consumer | `put` / `take` block; bounded queues give backpressure |
| `ConcurrentLinkedQueue` | Non-blocking queue | No backpressure |
| `Collections.synchronizedMap` | Legacy wrapper | One lock for everything; iteration still needs manual locking |

### 3.6 Thread pools and executors

- **In plain words:** keep a fixed crew of worker threads and a queue of jobs, instead of hiring a new thread per job.
- `ThreadPoolExecutor(core, max, keepAlive, queue, rejectionHandler)`
  - Threads grow to `core`, then tasks queue, then threads grow to `max` only when the queue is full
  - Rejection when full: `AbortPolicy` (throw), `CallerRunsPolicy` (slow the caller down = backpressure), discard policies
```java
ExecutorService pool = new ThreadPoolExecutor(
        8, 16, 60, TimeUnit.SECONDS,
        new ArrayBlockingQueue<>(1_000),                 // bounded: overload becomes visible
        new ThreadPoolExecutor.CallerRunsPolicy());
Future<String> f = pool.submit(() -> callService());
```
- Sizing rule of thumb: CPU-bound ≈ number of cores; I/O-bound ≈ cores × (1 + wait time / compute time)
- Catch: `Executors.newFixedThreadPool` uses an unbounded queue (memory grows silently); `newCachedThreadPool` can create unbounded threads

### 3.7 CompletableFuture

- Compose async steps without blocking: run in parallel, combine, handle errors, time out
```java
CompletableFuture<User>  u = CompletableFuture.supplyAsync(() -> users.get(id), pool);
CompletableFuture<Order> o = CompletableFuture.supplyAsync(() -> orders.last(id), pool);
Profile p = u.thenCombine(o, Profile::new)
             .orTimeout(300, TimeUnit.MILLISECONDS)
             .exceptionally(ex -> Profile.partial())
             .join();
```
- Catch: without an explicit executor it uses the shared `ForkJoinPool.commonPool()`; blocking calls there starve everyone

### 3.8 Coordination: latch, semaphore, barrier

| Tool | In plain words | Use |
|---|---|---|
| `CountDownLatch` | Wait until N things have happened (one-shot) | Wait for N workers to finish starting |
| `Semaphore` | N permits; take one to enter | Cap concurrent calls to a fragile dependency |
| `CyclicBarrier` / `Phaser` | Everyone waits at a line, then all go together | Phased parallel computations |

### 3.9 ThreadLocal

- One value per thread (request id, transaction context, date formatter)
- Catch: in a thread pool the thread lives on; clear it in `finally` or the next request sees old data (and memory leaks)

### 3.10 Virtual threads (Java 21)

- Millions of cheap threads scheduled by the JVM on a few carrier threads; blocking I/O parks the virtual thread instead of an OS thread
```java
try (var exec = Executors.newVirtualThreadPerTaskExecutor()) {
    exec.submit(() -> httpCall());               // write blocking code; it scales like async
}
```
- Good for I/O-bound request handling; no gain for CPU-bound work
- Catch: pinning (blocking inside `synchronized` or native calls holds the carrier); still cap calls to a database with a semaphore or pool

## 4. Deadlock And Other Liveness Failures

- **In plain words:** a deadlock is two people each holding one chopstick and waiting forever for the other's.
- Four conditions, all required: mutual exclusion, hold-and-wait, no preemption, circular wait
- Prevention
  - Global lock order (always lock account with smaller id first)
  - `tryLock` with timeout and back off
  - Hold one lock at a time; never call unknown code while holding a lock
- Other liveness failures
  - Livelock: threads keep reacting to each other and make no progress
  - Starvation: a thread never gets the lock or CPU (unfair locks, priorities)
  - Pool-induced deadlock: tasks in a pool wait on other tasks queued behind them in the same pool
- Diagnose: thread dump (`jstack`) shows "Found one Java-level deadlock"

## 5. Picking The Tool

| What you need to protect | Tool |
|---|---|
| Nothing shared | Immutability, local variables, confinement |
| One counter or reference | `AtomicInteger`, `LongAdder`, `AtomicReference` |
| A shared map or queue | `ConcurrentHashMap`, `BlockingQueue` |
| A stop flag or published config | `volatile` |
| An invariant across several fields | `synchronized` or `ReentrantLock` |
| Read-heavy shared data | `ReadWriteLock`, or copy-on-write + `AtomicReference` |
| Limit concurrent access to a dependency | `Semaphore` or a bounded pool |
| Fan out calls and combine | `CompletableFuture` with a dedicated executor, or virtual threads |
| Across processes or machines | DB transactions, conditional writes, distributed locks ([1dissys.md](1dissys.md)) |

- Default: immutability and confinement first, then the concurrent library, locks last

## 6. Python Concurrency

- **In plain words:** in standard CPython only one thread runs Python code at a time, so threads help with waiting (I/O), and you need processes to use several cores.

### 6.1 The GIL

- The Global Interpreter Lock lets one thread execute Python bytecode at a time
- Released during blocking I/O and in many C extensions (NumPy), so I/O-bound threading still works
- CPU-bound pure-Python work does not speed up with threads; use processes
- Python 3.13 added an optional free-threaded build without the GIL (PEP 703); still experimental in 3.13 (Python docs, 2024)
- The GIL does not make your code thread-safe: `count += 1` is still a read-modify-write race

### 6.2 The core modules

| Module | Key classes / functions | Model |
|---|---|---|
| `threading` | `Thread`, `Lock`, `RLock`, `Condition`, `Event`, `Semaphore`, `BoundedSemaphore`, `Barrier`, `local` | OS threads sharing memory |
| `queue` | `Queue`, `LifoQueue`, `PriorityQueue` (thread-safe, blocking) | Producer-consumer between threads |
| `concurrent.futures` | `ThreadPoolExecutor`, `ProcessPoolExecutor`, `Future`, `as_completed`, `wait` | Pools with one simple API |
| `multiprocessing` | `Process`, `Pool`, `Queue`, `Manager`, `shared_memory` | Separate processes, true parallelism |
| `asyncio` | event loop, `async` / `await`, `create_task`, `gather`, `TaskGroup` (3.11), `wait_for`, `Semaphore`, `Queue` | One thread, cooperative tasks for high-concurrency I/O |

```python
# Fan out I/O calls with a cap (asyncio)
import asyncio, httpx

async def fetch_all(urls: list[str]) -> list[int]:
    sem = asyncio.Semaphore(20)                       # at most 20 in flight
    async with httpx.AsyncClient(timeout=2.0) as client:
        async def one(u: str) -> int:
            async with sem:
                return (await client.get(u)).status_code
        return await asyncio.gather(*(one(u) for u in urls))
```

```python
# CPU-bound work across cores
from concurrent.futures import ProcessPoolExecutor

with ProcessPoolExecutor() as pool:
    results = list(pool.map(heavy_compute, items))
```

### 6.3 Which one when

| Workload | Use | Why |
|---|---|---|
| Many network calls, async libraries available | `asyncio` | Thousands of tasks on one thread |
| Blocking libraries (requests, JDBC-style drivers) | `ThreadPoolExecutor` | GIL is released while waiting |
| CPU-heavy Python code | `ProcessPoolExecutor` / `multiprocessing` | Each process has its own GIL |
| Web servers | FastAPI on uvicorn (asyncio) with several worker processes | Async per process, processes for cores |

- Catch: one blocking call inside `async def` stalls the whole event loop; run it with `asyncio.to_thread`

## 7. Java vs Python Side By Side

| Need | Java | Python |
|---|---|---|
| Mutual exclusion | `synchronized`, `ReentrantLock` | `threading.Lock`, `RLock` |
| Atomic counter | `AtomicInteger`, `LongAdder` | Lock around it, or `itertools.count` in CPython |
| Thread-safe queue | `BlockingQueue` | `queue.Queue`, `asyncio.Queue` |
| Pool | `ThreadPoolExecutor` | `concurrent.futures.ThreadPoolExecutor` |
| Async composition | `CompletableFuture` | `asyncio.gather`, `TaskGroup` |
| Cheap concurrency for I/O | Virtual threads | `asyncio` tasks |
| True CPU parallelism | Threads (no GIL) | Processes |
| Cap concurrent calls | `Semaphore` | `threading.Semaphore`, `asyncio.Semaphore` |

## 8. Failure Modes

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Lost update | Unprotected read-modify-write | Counts lower than expected under load | Atomic, lock, or `merge` / `compute` |
| Stale read | Flag or field not `volatile` / not locked | Thread never stops | `volatile` or proper handoff |
| Deadlock | Two locks in different orders | Thread dump; requests hang | Lock ordering, `tryLock` with timeout |
| Pool exhaustion | Blocking calls in a small pool; no timeouts | Rising latency, queue depth, rejections | Timeouts, separate pools (bulkheads), bounded queues |
| Unbounded queue OOM | `newFixedThreadPool` under overload | Heap grows, GC thrash | Bounded queue + rejection policy |
| ThreadLocal leak | Not cleared in a pooled thread | Wrong user data; memory growth | `remove()` in `finally` |
| Event loop stall (Python) | Blocking call in `async def` | All requests slow at once | `asyncio.to_thread`, async drivers |

## 9. Interview Questions

**Q1. Why is `count++` not thread-safe, and how do you fix it?**
- L4: it is read, add, write; two threads can interleave and lose an update. Fix with `AtomicInteger`, `synchronized`, or a lock
- L5 extra: `volatile` alone doesn't help (visibility, not atomicity); under heavy contention `LongAdder` beats `AtomicLong` by spreading the count across cells

**Q2. `synchronized` vs `ReentrantLock`?**
- L4: both are reentrant mutual exclusion with the same visibility guarantees; `ReentrantLock` adds `tryLock`, timeouts, interruptible waits, fairness and multiple conditions
- L5 extra: prefer `synchronized` for simple cases (can't forget to unlock); with virtual threads before JDK 24, `synchronized` around blocking I/O pins the carrier thread, so `ReentrantLock` was preferred there

**Q3. How do you size a thread pool, and what happens when it's full?**
- L4: CPU-bound ≈ cores; I/O-bound larger, by wait-to-compute ratio; when the queue fills, the rejection policy decides
- L5 extra: bounded queue + `CallerRunsPolicy` turns overload into backpressure; separate pools per dependency (bulkheads) so one slow service can't take every thread

**Q4. What causes a deadlock and how do you prevent it?**
- L4: four conditions (mutual exclusion, hold-and-wait, no preemption, circular wait); prevent with a global lock order or timeouts
- L5 extra: pool-induced deadlock (tasks waiting on tasks in the same pool) and DB-level deadlocks, where the database picks a victim and you retry the transaction

**Q5. When do you use threads, processes, or asyncio in Python?**
- L4: threads or asyncio for I/O-bound work, processes for CPU-bound work, because of the GIL
- L5 extra: asyncio scales to thousands of connections on one thread but needs async libraries all the way down; free-threaded 3.13 may change the CPU story but is experimental

**Q6. Virtual threads: what do they change?**
- L4: blocking code scales like async because a blocked virtual thread doesn't hold an OS thread
- L5 extra: they don't add capacity to the database: limit concurrency with a semaphore or connection pool, and watch for pinning

## 10. Where This Fits

- Place: track B1.7 in [1x-plan](../../1x-plan.md); the deep version is [1concurrency-c.md](1concurrency-c.md)
- Time: 2–3 hours to read and say aloud
- I should be able to
  - Explain atomicity, visibility and ordering with `count++` and a stop flag
  - Pick the right Java tool for a given invariant in one sentence
  - Size a thread pool and explain its rejection behavior
  - Say when Python needs processes instead of threads

## References

- [Java SE 21 `java.util.concurrent` package summary](https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/concurrent/package-summary.html)
- [JEP 444: Virtual Threads](https://openjdk.org/jeps/444)
- [Python docs — Concurrent execution](https://docs.python.org/3/library/concurrency.html)
- [PEP 703 — Making the Global Interpreter Lock optional](https://peps.python.org/pep-0703/)
- Brian Goetz et al., *Java Concurrency in Practice* (2006)
