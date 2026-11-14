# Distributed Systems — Python + Java Implementation Practice

## Index

- [Contract and scope](#contract)
- [1. Why distribute?](#s1)
  - [1.1 Capacity and bounded admission](#s11)
  - [1.2 Partial failure and bounded retries](#s12)
- [2. Compute, state, and coordination](#s2)
  - [2.1 Stateless compute over a state owner](#s21)
  - [2.2 Ownership epochs and fencing](#s22)
- [3. Geo-routing](#s3)
  - [3.1 Edge versus home-cell routing](#s31)
  - [3.2 Residency and home-region reads](#s32)
- [4. Global unique IDs](#s4)
  - [4.1 UUIDs and ticket ranges](#s41)
  - [4.2 Snowflake](#s42)
- [5. Database guarantees](#s5)
  - [5.1 Transactional idempotency](#s51)
  - [5.2 Global username claims](#s52)
  - [5.3 Session consistency and causal dependencies](#s53)
- [6. Sharding and replication](#s6)
  - [6.1 Shards containing replicas](#s61)
  - [6.2 Partition routing, hot keys, and migration](#s62)
  - [6.3 Replication, failover, and quorum limits](#s63)
  - [6.4 CAP and PACELC read policy](#s64)
- [7. Design-round question-to-code map](#s7)
- [8. Local concurrency](#s8)
  - [8.1 Partition the contention domain](#s81)
  - [8.2 Publication and happens-before](#s82)
  - [8.3 Locks, read-heavy state, and deadlock](#s83)
  - [8.4 CAS, atomics, and ABA](#s84)
  - [8.5 Concurrent collections](#s85)
  - [8.6 Executors, futures, and virtual threads](#s86)
  - [8.7.1 Lazy singleton](#s871)
  - [8.7.2 Bounded buffer](#s872)
  - [8.7.3 Optimistic balance update](#s873)
  - [8.7.4 Token bucket](#s874)
- [9. References](#s9)

<a id="contract"></a>
## Contract and scope

- **Concept source:** [2.dissys.md](2.dissys.md).
- **Coverage:** same section order as the concept file.
  - Repeated interview prompts link to their implementations in §7.
  - The four coding prompts in source §8.7 have separate implementation sections.
- **Practice format:** classic requirement followed by an explanatory flow and an L4 implementation.
  - A flow precedes every baseline, variant, and follow-up code pair.
  - Python first.
  - Java second.
  - L5 extras explain the boundary of the guarantee.
  - Selected follow-ups add an extended requirement and both languages.
- **Follow-up selection:** recurring interview patterns worth practicing.
  - This is a preparation judgment.
  - The source does not provide measured interview frequencies.
- **Execution:**
  - Python 3.11+.
  - Java 17 unless marked Java 21+.
  - Each fenced snippet is isolated unless an explicit dependency is listed.
  - Java snippets include imports and use package-private classes.
  - PostgreSQL examples require a database at runtime.
  - Python PostgreSQL examples require `psycopg` 3.
  - Java PostgreSQL examples accept a JDBC `Connection` with its driver already configured.
- **Scope labels:**
  - `local`: protects one process.
  - `model`: exposes protocol decisions.
  - `database`: delegates atomicity to a real store.
  - A local lock does not coordinate independent services.
  - A replica model does not implement a durable consensus protocol.
  - A wall-clock timestamp does not prove causal order.
- **Validation:**
  - 44 Python snippets passed syntax checks.
  - 44 Java snippets compiled against their declared language release.
  - 21 Python behavior tests passed.
  - Java behavior checks passed with 2,076 assertions.
  - 29 SQL statements passed PostgreSQL syntax parsing.
  - PostgreSQL integration behavior remains untested because a local database runtime was unavailable.

<a id="s1"></a>
## 1. Why distribute?

<a id="s11"></a>
### 1.1 Capacity and bounded admission

- **Classic requirement:** reject excess concurrent work before memory or a downstream connection pool is exhausted.
- **L4 knowledge:** bound in-flight requests with a semaphore.
  - Select the limit from measured downstream capacity.
  - Release permits even when work fails.
  - Use a nonblocking acquisition for immediate overload rejection.
- **Interview question:** does this limit requests per second?
  - It limits concurrency.
  - Use §8.7.4 for a rate limit.

**Flow**

→ Validate a positive concurrency limit.  
→ Try to acquire one permit without waiting.  
→ If unavailable, reject the request.  
→ Run accepted work.  
→ Release the permit in a finally block, including on failure.

```python
from threading import BoundedSemaphore

class Admission:
    def __init__(self, limit: int):
        if limit <= 0:
            raise ValueError("limit must be positive")
        self.slots = BoundedSemaphore(limit)

    def run(self, work):
        if not self.slots.acquire(blocking=False):
            raise RuntimeError("overloaded")
        try:
            return work()
        finally:
            self.slots.release()
# Time: O(1) overhead per call, Space: O(1).
```

```java
import java.util.concurrent.Callable;
import java.util.concurrent.RejectedExecutionException;
import java.util.concurrent.Semaphore;

final class Admission {
    private final Semaphore slots;
    Admission(int limit) {
        if (limit <= 0) throw new IllegalArgumentException("limit");
        slots = new Semaphore(limit);
    }
    <T> T run(Callable<T> work) throws Exception {
        if (!slots.tryAcquire()) throw new RejectedExecutionException("overloaded");
        try { return work.call(); }
        finally { slots.release(); }
    }
}
```

- **L5 extra:** admission limits are per process.
  - Autoscaling changes aggregate concurrency.
  - Reserve downstream capacity across instances before increasing the local limit.

→ Offered work exceeds measured service capacity.  
⇒ Queues grow unless admission is bounded.  
→ Reject or shed work at the boundary.

<a id="s12"></a>
### 1.2 Partial failure and bounded retries

- **Classic requirement:** retry a transient failure with exponential backoff and jitter.
  - Reuse the same operation key on every attempt.
  - Limit both attempts and elapsed time.
  - Pass the remaining timeout to the transport.
- **Scope:** transport-independent retry wrapper.
  - `send(key, timeout_seconds)` must enforce that timeout on its network call.
  - Only the custom transient exception is retried.

**Flow**

→ Record one monotonic deadline and retain the original operation key.  
→ Pass the remaining time budget into each transport attempt.  
→ Return immediately on success.  
→ Retry only a transient failure while attempts remain.  
→ Wait for a jittered backoff that fits the remaining budget.  
→ Stop on a terminal error or an exhausted budget.

```python
import random
import time

class TransientError(Exception):
    pass

def retry(send, key: str, budget: float = 2.0, attempts: int = 4):
    if budget <= 0 or attempts <= 0:
        raise ValueError("positive budget and attempts required")
    deadline = time.monotonic() + budget
    for attempt in range(attempts):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("retry budget exhausted")
        try:
            return send(key, remaining)
        except TransientError:
            if attempt + 1 == attempts:
                raise
            remaining = deadline - time.monotonic()
            delay = random.uniform(0, min(0.05 * 2 ** attempt, 0.5))
            if delay >= remaining:
                raise TimeoutError("no retry budget")
            time.sleep(delay)
# Time: O(attempts) calls, Space: O(1).
```

```java
import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

final class Retry {
    static final class Transient extends Exception {}
    interface Send { String call(String key, double timeoutSeconds) throws Exception; }
    static String run(Send send, String key, long budgetMillis, int attempts)
            throws Exception {
        if (budgetMillis <= 0 || budgetMillis > 60_000 || attempts <= 0)
            throw new IllegalArgumentException();
        long start = System.nanoTime();
        long budget = TimeUnit.MILLISECONDS.toNanos(budgetMillis);
        for (int i = 0; i < attempts; i++) {
            long remaining = budget - (System.nanoTime() - start);
            if (remaining <= 0) throw new TimeoutException();
            try { return send.call(key, remaining / 1e9); }
            catch (Transient failure) {
                if (i + 1 == attempts) throw failure;
                long cap = 50_000_000L << Math.min(i, 3);
                long delay = ThreadLocalRandom.current().nextLong(cap + 1);
                remaining = budget - (System.nanoTime() - start);
                if (delay >= remaining) throw new TimeoutException();
                TimeUnit.NANOSECONDS.sleep(delay);
            }
        }
        throw new AssertionError();
    }
}
```

- **L5 extra:** a timeout gives an unknown outcome.
  - Query operation status or retry with the same key.
  - Retries at multiple service layers multiply load.
  - Choose one retry owner for a dependency call.
  - Authentication failures and invalid requests remain terminal.

<a id="s2"></a>
## 2. Compute, state, and coordination

<a id="s21"></a>
### 2.1 Stateless compute over a state owner

- **Classic requirement:** two service instances update the same account without relying on either instance's memory.
- **L4 knowledge:** keep state mutation behind one atomic owner API.
- **Scope:** local owner model.
  - Replace the owner with a database conditional update in a deployed service.
  - The service itself retains no account balance.

**Flow**

→ Validate the requested credit.  
→ Forward the account ID and amount to the shared state owner.  
→ Under the owner lock, read the balance and add the amount.  
→ Store and return the new balance.  
→ Release the owner lock.

```python
from threading import Lock

class AccountOwner:
    def __init__(self):
        self.balances = {}
        self.lock = Lock()

    def add(self, account: str, delta: int) -> int:
        with self.lock:
            value = self.balances.get(account, 0) + delta
            self.balances[account] = value
            return value

def handle_credit(owner: AccountOwner, account: str, amount: int) -> int:
    if amount <= 0:
        raise ValueError("positive credit required")
    return owner.add(account, amount)
# Time: O(1) average per call, Space: O(accounts).
```

```java
import java.util.HashMap;
import java.util.Map;

final class AccountOwner {
    private final Map<String, Long> balances = new HashMap<>();
    synchronized long add(String account, long delta) {
        long value = Math.addExact(balances.getOrDefault(account, 0L), delta);
        balances.put(account, value);
        return value;
    }
    static long handleCredit(AccountOwner owner, String account, long amount) {
        if (amount <= 0) throw new IllegalArgumentException();
        return owner.add(account, amount);
    }
}
```

- **L5 extra:** stateless compute still depends on state availability.
  - Replicate the state owner for fault tolerance.
  - Partition ownership when one owner exceeds measured capacity.
  - Add §5.1 deduplication before retrying credits.

<a id="s22"></a>
### 2.2 Ownership epochs and fencing

- **Classic requirement:** reject writes from a paused worker after leadership has transferred.
- **L4 knowledge:** allocate increasing epochs through a linearizable authority.
  - Install the new epoch at the protected resource before admitting the new leader.
  - Check the epoch atomically with each resource mutation.
- **Scope:** local protected-resource model.
  - Epoch allocation and lease election are external.
  - Tokens are trusted internal values, not caller-selected credentials.

**Flow**

→ Receive an epoch from the trusted ownership authority.  
→ Under the resource lock, install it only if it advances the current epoch.  
→ For each write, compare the supplied epoch with the installed epoch.  
→ If the epochs differ, reject the stale owner.  
→ Otherwise, mutate the resource while holding the same lock.

```python
from threading import Lock

class FencedResource:
    def __init__(self):
        self.epoch = 0
        self.value = None
        self.lock = Lock()

    def activate(self, token: int):
        with self.lock:
            if token <= self.epoch:
                raise ValueError("epoch must advance")
            self.epoch = token

    def write(self, token: int, value: str):
        with self.lock:
            if token != self.epoch or token <= 0:
                raise RuntimeError("stale owner")
            self.value = value
# Time: O(1), Space: O(1) excluding value.
```

```java
final class FencedResource {
    private long epoch;
    private String value;
    synchronized void activate(long token) {
        if (token <= epoch) throw new IllegalArgumentException("epoch must advance");
        epoch = token;
    }
    synchronized void write(long token, String next) {
        if (token <= 0 || token != epoch) throw new IllegalStateException("stale owner");
        value = next;
    }
    synchronized String read() { return value; }
}
```

- **Interview question:** does lease expiry automatically stop a worker?
  - The resource must reject the worker's obsolete epoch.
- **L5 extra:** persist the epoch with the resource.
  - Restarting a resource with epoch zero would admit obsolete writers.
  - Fencing does not deduplicate multiple requests from the current leader.

→ Old worker pauses while holding epoch 7.  
→ New leader installs epoch 8 at the resource.  
→ Old worker resumes and writes with epoch 7.  
⇒ The resource rejects that write.

<a id="s3"></a>
## 3. Geo-routing

<a id="s31"></a>
### 3.1 Edge versus home-cell routing

- **Classic requirement:** choose a healthy ingress region by measured latency, then route authenticated state access to the user's home cell.
- **Scope:** application routing model.
  - GeoDNS and BGP run outside these snippets.
  - A latency table is an input, not an implementation of Anycast.

**Flow**

→ Filter ingress regions by health and available latency measurements.  
→ Choose the region with the lowest measured latency.  
→ Look up the authenticated user in the home-cell directory.  
→ Return the ingress region separately from the home region and cell.  
→ Reject routing when no healthy ingress or no user mapping exists.

```python
def route(user: str, latency_ms: dict[str, int], healthy: set[str],
          directory: dict[str, tuple[str, str]]) -> tuple[str, str, str]:
    candidates = [r for r in healthy if r in latency_ms]
    if not candidates:
        raise RuntimeError("no healthy ingress")
    edge = min(candidates, key=lambda r: (latency_ms[r], r))
    home_region, cell = directory[user]
    return edge, home_region, cell
# Time: O(regions), Space: O(regions).
```

```java
import java.util.Comparator;
import java.util.Map;
import java.util.Set;

final class GeoRoute {
    record Home(String region, String cell) {}
    record Route(String edge, Home home) {}
    static Route route(String user, Map<String, Integer> latency,
                       Set<String> healthy, Map<String, Home> directory) {
        String edge = healthy.stream().filter(latency::containsKey)
            .min(Comparator.<String>comparingInt(latency::get).thenComparing(s -> s))
            .orElseThrow(() -> new IllegalStateException("no healthy ingress"));
        Home home = directory.get(user);
        if (home == null) throw new IllegalArgumentException("unknown user");
        return new Route(edge, home);
    }
}
```

- **L5 extra:** cache the directory with an ownership generation.
  - A stale generation must trigger refresh or redirection.
  - Treat ingress health and home-cell availability as separate signals.

<a id="s32"></a>
### 3.2 Residency and home-region reads

- **Classic requirement:** send writes to the home region and permit stale local reads only in configured storage regions.
- **Scope:** supplied residency policy, not legal advice.
  - Authentication has already supplied the user's trusted home region.
  - Replica membership is supplied by the control plane.

**Flow**

→ Validate that the home region is allowed by the supplied policy.  
→ For a write or a fresh-read request, select the home region.  
→ Otherwise, check whether the edge region is allowed and has a replica.  
→ Use that local replica when eligible.  
→ Fall back to the home region when it is not eligible.

```python
def data_region(home: str, edge: str, allowed: set[str], replicas: set[str],
                write: bool, needs_fresh: bool) -> str:
    if home not in allowed:
        raise ValueError("invalid home policy")
    if write or needs_fresh:
        return home
    if edge in allowed and edge in replicas:
        return edge
    return home
# Time: O(1) average, Space: O(1).
```

```java
import java.util.Set;

final class Residency {
    static String region(String home, String edge, Set<String> allowed,
                         Set<String> replicas, boolean write, boolean needsFresh) {
        if (!allowed.contains(home)) throw new IllegalArgumentException("home policy");
        if (write || needsFresh) return home;
        return allowed.contains(edge) && replicas.contains(edge) ? edge : home;
    }
}
```

- **L5 extra:** selecting home does not prove freshness after failover.
  - Require a valid leader epoch and the required committed prefix.
  - Rehoming uses the migration barrier in §6.2.
  - Restrict logs and backups as well as the primary database when policy requires it.

<a id="s4"></a>
## 4. Global unique IDs

<a id="s41"></a>
### 4.1 UUIDs and ticket ranges

- **Classic requirement:** generate a portable public identifier without contacting a coordinator.
- **L4 choice:** UUIDv4 from the standard library.
  - Collision resistance is probabilistic.
  - Keep a database uniqueness constraint.
  - Random IDs do not provide chronological order.

**Flow**

→ Ask the standard UUID generator for a fresh version-4 identifier.  
→ Encode the identifier in its standard string form.  
→ Return it without contacting a central allocator.

```python
import uuid

def new_public_id() -> str:
    return str(uuid.uuid4())
# Time: O(1), Space: O(1).
```

```java
import java.util.UUID;

final class PublicId {
    static String next() { return UUID.randomUUID().toString(); }
}
```

| Alternative | Classic implementation | Deciding requirement | Trap |
| --- | --- | --- | --- |
| UUIDv7 | Vetted RFC 9562 generator | Time-oriented 128-bit keys | Wall-clock order is not causal order |
| Snowflake | §4.2 | Compact 64-bit keys | Worker IDs must be unique |
| Database sequence | Database-owned atomic sequence | One database owns allocation | Rollbacks can leave gaps |
| Step/offset sequence | Disjoint residue classes | Fixed writer allocation | Changing allocation can create collisions |
| Ticket ranges | Atomic range reservation below | Reduce allocator round trips | Unused values are lost after a crash |

- **Classic range-allocation variant:** hand out disjoint inclusive ranges from one durable allocator.
- **Database setup:** initialize one allocator row before use.

**Flow**

→ Validate a positive range size.  
→ Atomically advance the allocator row by that size.  
→ Read the updated next-ID value from the same update.  
→ Commit the range reservation.  
→ Return the inclusive range immediately below the new next-ID value.  
→ If the allocator row is missing, fail instead of issuing IDs.

```sql
CREATE TABLE id_allocator (
    name TEXT PRIMARY KEY,
    next_id BIGINT NOT NULL CHECK (next_id > 0)
);
INSERT INTO id_allocator VALUES ('orders', 1);
```

```python
def reserve_ids(conn, size: int) -> tuple[int, int]:
    if size <= 0:
        raise ValueError("positive size required")
    with conn.transaction():
        row = conn.execute(
            "UPDATE id_allocator SET next_id = next_id + %s "
            "WHERE name = 'orders' RETURNING next_id", (size,)
        ).fetchone()
        if row is None:
            raise RuntimeError("allocator missing")
    return row[0] - size, row[0] - 1
# Time: O(1) indexed row update, Space: O(1).
```

```java
import java.sql.Connection;
import java.sql.SQLException;

final class TicketIds {
    // Connection is dedicated, idle, and in autocommit mode.
    static long[] reserve(Connection c, int size) throws SQLException {
        if (size <= 0 || !c.getAutoCommit()) throw new IllegalArgumentException();
        String sql = "UPDATE id_allocator SET next_id = next_id + ? "
                   + "WHERE name = 'orders' RETURNING next_id";
        try (var p = c.prepareStatement(sql)) {
            p.setInt(1, size);
            try (var r = p.executeQuery()) {
                if (!r.next()) throw new SQLException("allocator missing");
                long end = r.getLong(1);
                return new long[] {end - size, end - 1};
            }
        }
    }
}
```

- **L5 extra:** acknowledge ranges only after their reservation commits.
  - A lost response burns a range on retry.
  - Gaplessness is a separate coordination requirement.
  - The allocator still needs durable failover.

<a id="s42"></a>
### 4.2 Snowflake

- **Classic requirement:** issue unique 64-bit IDs from one externally assigned worker ID.
  - 41 timestamp bits.
  - 10 worker bits.
  - 12 sequence bits.
- **L4 policy:** reject clock rollback and per-millisecond sequence exhaustion.
  - The caller may retry after time advances.
  - Inject the clock for deterministic boundary testing.

**Flow**

→ Acquire the generator lock and read milliseconds since the custom epoch.  
→ Reject an invalid timestamp or clock rollback.  
→ In the same millisecond, increment the sequence.  
→ In a later millisecond, reset the sequence to zero.  
→ Reject sequence exhaustion before changing generator state.  
→ Store the timestamp and sequence, then pack the timestamp, worker ID, and sequence into the result.

```python
import time
from threading import Lock

class Snowflake:
    EPOCH = 1704067200000

    def __init__(self, worker: int, clock=None):
        if not 0 <= worker < 1024:
            raise ValueError("worker out of range")
        self.worker = worker
        self.clock = clock or (lambda: time.time_ns() // 1_000_000)
        self.last = -1
        self.seq = 0
        self.lock = Lock()

    def next_id(self) -> int:
        with self.lock:
            now = self.clock() - self.EPOCH
            if not 0 <= now < 1 << 41 or now < self.last:
                raise RuntimeError("clock outside safe range")
            seq = self.seq + 1 if now == self.last else 0
            if seq >= 4096:
                raise RuntimeError("millisecond exhausted")
            self.last, self.seq = now, seq
            return (now << 22) | (self.worker << 12) | seq
# Time: O(1), Space: O(1).
```

```java
import java.util.function.LongSupplier;

final class Snowflake {
    static final long EPOCH = 1704067200000L;
    private final int worker;
    private final LongSupplier clock;
    private long last = -1;
    private int sequence;
    Snowflake(int worker, LongSupplier clock) {
        if (worker < 0 || worker >= 1024) throw new IllegalArgumentException();
        this.worker = worker;
        this.clock = clock;
    }
    synchronized long nextId() {
        long now = clock.getAsLong() - EPOCH;
        if (now < 0 || now >= (1L << 41) || now < last)
            throw new IllegalStateException("clock outside safe range");
        int next = now == last ? sequence + 1 : 0;
        if (next >= 4096) throw new IllegalStateException("millisecond exhausted");
        last = now;
        sequence = next;
        return (now << 22) | ((long) worker << 12) | sequence;
    }
}
```

- **Interview question:** can this object safely restart with the same worker ID?
  - Only after excluding timestamps already used by the previous incarnation.
- **L5 extra:** retain a durable timestamp reservation or delay worker-ID reuse.
  - A lease alone cannot stop a paused old generator.
  - The storage fence in §2.2 protects writes, not uniqueness of IDs already handed out.
  - The bit layout permits 4,096 IDs per millisecond per worker.
  - That is a format limit, not a measured implementation throughput.

<a id="s5"></a>
## 5. Database guarantees

<a id="s51"></a>
### 5.1 Transactional idempotency

- **Classic requirement:** a retried internal account credit changes the balance once and returns the original resulting balance.
  - Scope the key by tenant and operation.
  - Reject reuse with a different account or amount.
  - Commit the deduplication record and balance update together.
- **Database contract:** PostgreSQL at `READ COMMITTED`.
  - Use a dedicated idle connection.
  - Python connection starts in autocommit mode.
  - Java checks that precondition.
  - The authenticated tenant must own the target account.
  - Amounts are positive integer minor units.
- **Boundary:** this credits an internal ledger balance.
  - An external card processor does not join this transaction.
  - Use the outbox follow-up for external work.

**Flow**

→ Validate the request and begin the database transaction.  
→ Attempt the unique deduplication insert scoped by tenant, operation, and request key.  
→ If inserted, credit the account and store its resulting balance in the deduplication row.  
→ If already present, compare the stored account and amount with the retried request.  
→ Return the stored balance only for a matching completed request.  
→ Commit before returning success, or roll back on failure.

```sql
CREATE TABLE account (
    tenant TEXT NOT NULL,
    id TEXT NOT NULL,
    balance BIGINT NOT NULL DEFAULT 0 CHECK (balance >= 0),
    PRIMARY KEY (tenant, id)
);
CREATE TABLE dedup (
    tenant TEXT NOT NULL,
    operation TEXT NOT NULL,
    request_key TEXT NOT NULL,
    account_id TEXT NOT NULL,
    amount BIGINT NOT NULL CHECK (amount > 0),
    result_balance BIGINT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (tenant, operation, request_key)
);
```

```python
def credit_once(conn, tenant: str, key: str, account: str, amount: int) -> int:
    if amount <= 0 or not key:
        raise ValueError("invalid request")
    with conn.transaction():
        inserted = conn.execute(
            "INSERT INTO dedup(tenant,operation,request_key,account_id,amount) "
            "VALUES (%s,'credit',%s,%s,%s) ON CONFLICT DO NOTHING RETURNING 1",
            (tenant, key, account, amount)
        ).fetchone()
        if inserted:
            row = conn.execute(
                "UPDATE account SET balance = balance + %s "
                "WHERE tenant = %s AND id = %s RETURNING balance",
                (amount, tenant, account)
            ).fetchone()
            if row is None:
                raise ValueError("account missing")
            conn.execute(
                "UPDATE dedup SET result_balance = %s WHERE tenant = %s "
                "AND operation = 'credit' AND request_key = %s",
                (row[0], tenant, key)
            )
            result = row[0]
        else:
            row = conn.execute(
                "SELECT account_id,amount,result_balance FROM dedup "
                "WHERE tenant = %s AND operation = 'credit' AND request_key = %s",
                (tenant, key)
            ).fetchone()
            if row is None or row[:2] != (account, amount):
                raise ValueError("key reused for another request")
            if row[2] is None:
                raise RuntimeError("invalid committed dedup row")
            result = row[2]
    return result
# Time: O(log rows) indexed operations excluding lock waits, Space: O(1).
```

```java
import java.sql.Connection;
import java.sql.SQLException;

final class IdempotentCredit {
    static long credit(Connection c, String tenant, String key,
                       String account, long amount) throws SQLException {
        if (amount <= 0 || key.isEmpty() || !c.getAutoCommit())
            throw new IllegalArgumentException();
        c.setTransactionIsolation(Connection.TRANSACTION_READ_COMMITTED);
        c.setAutoCommit(false);
        try {
            boolean inserted;
            try (var p = c.prepareStatement(
                    "INSERT INTO dedup(tenant,operation,request_key,account_id,amount) "
                  + "VALUES (?,'credit',?,?,?) ON CONFLICT DO NOTHING RETURNING 1")) {
                p.setString(1, tenant); p.setString(2, key);
                p.setString(3, account); p.setLong(4, amount);
                try (var r = p.executeQuery()) { inserted = r.next(); }
            }
            long result;
            if (inserted) {
                try (var p = c.prepareStatement("UPDATE account SET balance=balance+? "
                        + "WHERE tenant=? AND id=? RETURNING balance")) {
                    p.setLong(1, amount); p.setString(2, tenant); p.setString(3, account);
                    try (var r = p.executeQuery()) {
                        if (!r.next()) throw new SQLException("account missing");
                        result = r.getLong(1);
                    }
                }
                try (var p = c.prepareStatement("UPDATE dedup SET result_balance=? "
                        + "WHERE tenant=? AND operation='credit' AND request_key=?")) {
                    p.setLong(1, result); p.setString(2, tenant); p.setString(3, key);
                    p.executeUpdate();
                }
            } else {
                try (var p = c.prepareStatement("SELECT account_id,amount,result_balance "
                        + "FROM dedup WHERE tenant=? AND operation='credit' AND request_key=?")) {
                    p.setString(1, tenant); p.setString(2, key);
                    try (var r = p.executeQuery()) {
                        if (!r.next() || !account.equals(r.getString(1)) || amount != r.getLong(2))
                            throw new SQLException("key reused for another request");
                        result = r.getLong(3);
                        if (r.wasNull()) throw new SQLException("incomplete dedup row");
                    }
                }
            }
            c.commit();
            return result;
        } catch (SQLException | RuntimeException failure) {
            c.rollback();
            throw failure;
        } finally { c.setAutoCommit(true); }
    }
}
```

- **Interview question:** why does the duplicate path use a new SQL statement?
  - At `READ COMMITTED`, that statement can see the competing transaction after it commits.
  - A unique-constraint error would instead abort the transaction until rollback.
  - `ON CONFLICT DO NOTHING` avoids that error path. [PostgreSQL INSERT](https://www.postgresql.org/docs/current/sql-insert.html)
- **L5 extra:** retain deduplication records for the supported retry horizon.
  - Coordinate cleanup with active requests.
  - Never delete a live request's row during its duplicate lookup.
  - Durable transaction guarantees depend on the configured database failover policy.
  - Do not claim protection from acknowledged data loss on an asynchronous failover.

#### Follow-up — commit an event with the business write

- **Extended requirement:** survive a crash between committing the credit and publishing its event.
- **Implementation:** insert an outbox event inside the successful credit transaction, before commit.
  - Both helpers below depend on the caller's existing transaction.
  - Generate and persist an event ID once on the first successful request.
  - Do not invoke the helper on the duplicate response path.

**Flow**

→ During the business transaction, insert the event ID and payload into the outbox.  
→ Commit the business change and outbox event together.  
→ In a publisher transaction, lock one pending event while skipping already locked rows.  
→ Send the event and wait for a durable broker acknowledgement.  
→ Mark the event published and commit.  
→ If the publisher fails before that commit, leave the event eligible for retry.

```sql
CREATE TABLE outbox (
    event_id TEXT PRIMARY KEY,
    payload TEXT NOT NULL,
    published_at TIMESTAMPTZ
);
```

```python
def add_outbox(conn, event_id: str, payload: str):
    conn.execute("INSERT INTO outbox(event_id,payload) VALUES (%s,%s)",
                 (event_id, payload))

def publish_one(conn, broker_send) -> bool:
    with conn.transaction():
        row = conn.execute(
            "SELECT event_id,payload FROM outbox WHERE published_at IS NULL "
            "ORDER BY event_id FOR UPDATE SKIP LOCKED LIMIT 1"
        ).fetchone()
        if row is None:
            return False
        broker_send(row[0], row[1])  # Must wait for durable broker acknowledgement.
        conn.execute("UPDATE outbox SET published_at=now() WHERE event_id=%s", (row[0],))
    return True
# Time: O(backlog) without a pending-row index, Space: O(1) excluding payload.
```

```java
import java.sql.Connection;

final class Outbox {
    interface Broker { void send(String id, String payload) throws Exception; }
    static void add(Connection c, String id, String payload) throws Exception {
        if (c.getAutoCommit()) throw new IllegalArgumentException("transaction required");
        try (var p = c.prepareStatement("INSERT INTO outbox(event_id,payload) VALUES (?,?)")) {
            p.setString(1, id); p.setString(2, payload); p.executeUpdate();
        }
    }
    // Dedicated idle connection; broker call must have a bounded timeout.
    static boolean publishOne(Connection c, Broker broker) throws Exception {
        if (!c.getAutoCommit()) throw new IllegalArgumentException();
        c.setAutoCommit(false);
        try {
            String id, payload;
            try (var p = c.prepareStatement("SELECT event_id,payload FROM outbox "
                    + "WHERE published_at IS NULL ORDER BY event_id "
                    + "FOR UPDATE SKIP LOCKED LIMIT 1"); var r = p.executeQuery()) {
                if (!r.next()) { c.commit(); return false; }
                id = r.getString(1); payload = r.getString(2);
            }
            broker.send(id, payload);
            try (var p = c.prepareStatement("UPDATE outbox SET published_at=now() WHERE event_id=?")) {
                p.setString(1, id); p.executeUpdate();
            }
            c.commit(); return true;
        } catch (Exception failure) {
            c.rollback(); throw failure;
        } finally { c.setAutoCommit(true); }
    }
}
```

→ Publisher receives a broker acknowledgement.  
→ Publisher crashes before committing `published_at`.  
⇒ The next publisher sends the same event again.  
→ Consumer deduplicates `event_id` in its business transaction.

- **L5 extra:** the minimal publisher holds a row lock during the network call.
  - Use a timeout.
  - At higher volume, lease batches or use CDC.
  - A sent marker alone cannot provide exactly-once delivery.

<a id="s52"></a>
### 5.2 Global username claims

- **Classic requirement:** reserve a username globally while user records are sharded by user ID.
- **L4 implementation:** a strongly consistent claim directory with a unique primary key.
  - This chooses the source's global-directory option.
  - For a sharded directory, route by normalized username using §6.2.
  - All contenders for the same normalized value must reach the same authority.
- **Canonicalization:** deliberately restrict this exercise to ASCII lowercase letters, digits, and underscore.
  - Unicode identifiers need a documented normalization and confusable-character policy.

**Flow**

→ Normalize the username to lowercase.  
→ Reject characters or lengths outside the exercise policy.  
→ Begin a transaction on the username claim authority.  
→ Attempt to insert the normalized username and user ID without overwriting an existing claim.  
→ Read the recorded owner in a subsequent statement.  
→ Commit and report whether that owner matches the requesting user.

```sql
CREATE TABLE username_claim (
    username TEXT PRIMARY KEY,
    user_id TEXT NOT NULL
);
```

```python
import re

def claim_name(conn, username: str, user_id: str) -> bool:
    name = username.lower()
    if not re.fullmatch(r"[a-z0-9_]{3,32}", name):
        raise ValueError("invalid username")
    with conn.transaction():
        conn.execute("INSERT INTO username_claim VALUES (%s,%s) ON CONFLICT DO NOTHING",
                     (name, user_id))
        owner = conn.execute("SELECT user_id FROM username_claim WHERE username=%s",
                             (name,)).fetchone()
        return owner is not None and owner[0] == user_id
# Time: O(log claims), Space: O(1).
```

```java
import java.sql.Connection;
import java.util.Locale;

final class UsernameClaim {
    static boolean claim(Connection c, String username, String userId) throws Exception {
        String name = username.toLowerCase(Locale.ROOT);
        if (!name.matches("[a-z0-9_]{3,32}") || !c.getAutoCommit())
            throw new IllegalArgumentException();
        c.setTransactionIsolation(Connection.TRANSACTION_READ_COMMITTED);
        c.setAutoCommit(false);
        try {
            try (var p = c.prepareStatement(
                    "INSERT INTO username_claim VALUES (?,?) ON CONFLICT DO NOTHING")) {
                p.setString(1, name); p.setString(2, userId); p.executeUpdate();
            }
            boolean owned;
            try (var p = c.prepareStatement("SELECT user_id FROM username_claim WHERE username=?")) {
                p.setString(1, name);
                try (var r = p.executeQuery()) { owned = r.next() && userId.equals(r.getString(1)); }
            }
            c.commit(); return owned;
        } catch (Exception failure) {
            c.rollback(); throw failure;
        } finally { c.setAutoCommit(true); }
    }
}
```

- **L5 extra:** claim creation and user creation are separate transactions across shards.
  - Retry with the same user ID to complete a pending registration.
  - Record registration state for reconciliation.
  - Never release a claim merely because the user-service response timed out.
  - A confirmed cancellation may conditionally delete only the matching owner's claim.

<a id="s53"></a>
### 5.3 Session consistency and causal dependencies

- **Classic requirement:** route a session's reads to replicas that have applied at least its latest observed log offset.
- **L4 implementation:** carry a minimum required offset.
  - Advance it after a write acknowledgement.
  - Advance it after every read.
  - Refuse to serve from a replica below that offset.
- **Scope:** one committed partition log with contiguous replica prefixes.
  - The offset metadata must be trusted.
  - A failover must preserve the same committed history.

**Flow**

→ Receive the session minimum offset and replica applied-prefix metadata.  
→ Keep only replicas at or beyond the minimum offset.  
→ If none qualify, require replay progress or a verified leader read.  
→ Select the eligible replica with the highest applied offset.  
→ Return its value and advance the session minimum to the observed offset.

```python
def session_read(replicas: list[tuple[str, int, str]], minimum: int):
    eligible = [r for r in replicas if r[1] >= minimum]
    if not eligible:
        raise RuntimeError("wait for replay or use verified leader")
    name, applied, value = max(eligible, key=lambda r: r[1])
    return name, value, max(minimum, applied)
# Time: O(replicas), Space: O(replicas).
```

```java
import java.util.Comparator;
import java.util.List;

final class SessionRead {
    record Replica(String name, long applied, String value) {}
    record Result(String replica, String value, long minimum) {}
    static Result read(List<Replica> replicas, long minimum) {
        Replica r = replicas.stream().filter(x -> x.applied() >= minimum)
            .max(Comparator.comparingLong(Replica::applied))
            .orElseThrow(() -> new IllegalStateException("replica behind session"));
        return new Result(r.name(), r.value(), Math.max(minimum, r.applied()));
    }
}
```

| Source concept | Mechanism to implement | Boundary |
| --- | --- | --- |
| Linearizable read | Current leader authority plus committed-prefix/read barrier | Reading any server named leader is insufficient |
| Sequential consistency | One total operation order preserving each client's program order | Real-time recency is not required |
| Read-your-writes | Include acknowledged write offset in `minimum` | Applies to this session and partition |
| Monotonic reads | Include previously returned offset in `minimum` | Sticky routing alone fails after replica rollback |
| Causal consistency | Dependency vector checked before applying an event | One scalar does not cover independent partitions |
| Eventual consistency | Retry replication and deterministically merge concurrent updates | Convergence requires eventual communication |

- **Causal application variant:** defer an event until its dependencies have been applied.
  - Event `sequence` is contiguous within its origin.
  - Dependencies include everything the producer had observed before creating it.
  - Queue rejected events and retry after progress.
  - Missing events need fetching.
  - This predicate cannot recover them.

**Flow**

→ Compare the event sequence with the next expected sequence for its origin.  
→ Defer an event that is not the next contiguous event.  
→ Check each dependency against the locally observed origin offsets.  
→ Defer the event if any dependency is missing.  
→ Advance the origin offset when every prerequisite is satisfied.

```python
def apply_causal(seen: dict[str, int], origin: str, sequence: int,
                 dependencies: dict[str, int]) -> bool:
    if sequence != seen.get(origin, 0) + 1:
        return False
    if any(seen.get(node, 0) < required for node, required in dependencies.items()):
        return False
    seen[origin] = sequence
    return True
# Time: O(dependencies), Space: O(origins) retained in seen.
```

```java
import java.util.Map;

final class CausalApply {
    // One event-loop owner serializes calls and applies the business event together.
    static boolean apply(Map<String, Long> seen, String origin, long sequence,
                         Map<String, Long> dependencies) {
        if (sequence != seen.getOrDefault(origin, 0L) + 1) return false;
        for (var e : dependencies.entrySet())
            if (seen.getOrDefault(e.getKey(), 0L) < e.getValue()) return false;
        seen.put(origin, sequence);
        return true;
    }
}
```

- **L5 extra:** consistency models are not a single universally ordered ladder.
  - Session guarantees describe particular client histories.
  - Transaction isolation describes a different contract.
  - Unsynchronized memory access does not promise eventual convergence.

<a id="s6"></a>
## 6. Sharding and replication

<a id="s61"></a>
### 6.1 Shards containing replicas

- **Classic requirement:** route a key to a shard leader while retaining the shard's replica membership.
- **L4 implementation:** use a fixed hash partition and a topology directory.
- **Scope:** routing model with no membership changes.
  - The coordinator installs authoritative topology snapshots.
  - The returned leader still needs epoch validation at request time.

**Flow**

→ Hash the UTF-8 key with the shared SHA-256 encoding.  
→ Interpret the first eight bytes as an unsigned integer.  
→ Take the remainder by the fixed shard count.  
→ Load that shard from the supplied topology snapshot.  
→ Validate that its leader belongs to its replica membership.  
→ Return the shard routing information.

```python
import hashlib

def locate(key: str, topology: list[tuple[str, tuple[str, ...]]]):
    if not topology:
        raise ValueError("empty topology")
    digest = hashlib.sha256(key.encode("utf-8")).digest()
    shard = int.from_bytes(digest[:8], "big") % len(topology)
    leader, replicas = topology[shard]
    if leader not in replicas:
        raise ValueError("leader missing from membership")
    return shard, leader, replicas
# Time: O(key bytes + replicas), Space: O(key bytes).
```

```java
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.List;

final class Topology {
    record Shard(String leader, List<String> replicas) {}
    static Shard locate(String key, List<Shard> shards) throws Exception {
        if (shards.isEmpty()) throw new IllegalArgumentException();
        byte[] hash = MessageDigest.getInstance("SHA-256")
            .digest(key.getBytes(StandardCharsets.UTF_8));
        int id = (int) Long.remainderUnsigned(ByteBuffer.wrap(hash).getLong(), shards.size());
        Shard shard = shards.get(id);
        if (!shard.replicas().contains(shard.leader())) throw new IllegalStateException();
        return shard;
    }
}
```

- **L5 extra:** the same digest encoding is used in Python and Java.
  - Python's built-in string hash is unsuitable for cross-process stable routing.
  - Adding replicas changes redundancy.
  - Adding shards changes ownership and needs a migration protocol.

<a id="s62"></a>
### 6.2 Partition routing, hot keys, and migration

- **Classic requirement:** choose an owner with consistent hashing and virtual nodes.
- **L4 implementation:** hash virtual-node labels into a sorted ring.
  - Choose the first token clockwise from the key hash.
  - Wrap at the end of the ring.
  - Build an immutable ring for each membership generation.
  - Share the exact member list and hash encoding between clients.

**Flow**

→ Hash every node and virtual-node label into a ring token.  
→ Sort the tokens and reject collisions.  
→ Hash the requested key with the same encoding.  
→ Find the first token greater than or equal to the key hash.  
→ Wrap to the first ring token when the search reaches the end.  
→ Return the node that owns the selected token.

```python
import bisect
import hashlib

def ring_hash(text: str) -> int:
    return int.from_bytes(hashlib.sha256(text.encode("utf-8")).digest()[:8], "big")

class HashRing:
    def __init__(self, nodes: list[str], vnodes: int = 64):
        if not nodes or len(nodes) != len(set(nodes)) or vnodes <= 0:
            raise ValueError("invalid membership")
        entries = sorted((ring_hash(f"{node}#{i}"), node)
                         for node in nodes for i in range(vnodes))
        self.tokens = [token for token, _ in entries]
        if len(set(self.tokens)) != len(entries):
            raise ValueError("token collision; change seed")
        self.owners = [node for _, node in entries]

    def owner(self, key: str) -> str:
        i = bisect.bisect_left(self.tokens, ring_hash(key)) % len(self.tokens)
        return self.owners[i]
# Time: O(V log V) build, O(key bytes + log V) lookup; Space: O(V).
```

```java
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.HashSet;
import java.util.List;
import java.util.TreeMap;

final class HashRing {
    private final TreeMap<Long, String> ring = new TreeMap<>(Long::compareUnsigned);
    static long hash(String text) throws Exception {
        return ByteBuffer.wrap(MessageDigest.getInstance("SHA-256")
            .digest(text.getBytes(StandardCharsets.UTF_8))).getLong();
    }
    HashRing(List<String> nodes, int vnodes) throws Exception {
        if (nodes.isEmpty() || new HashSet<>(nodes).size() != nodes.size() || vnodes <= 0)
            throw new IllegalArgumentException();
        for (String node : nodes) for (int i = 0; i < vnodes; i++)
            if (ring.putIfAbsent(hash(node + "#" + i), node) != null)
                throw new IllegalArgumentException("token collision");
    }
    String owner(String key) throws Exception {
        var entry = ring.ceilingEntry(hash(key));
        return (entry == null ? ring.firstEntry() : entry).getValue();
    }
}
```

| Routing concept | Python / Java implementation in this file | Deciding workload |
| --- | --- | --- |
| Fixed hash modulo | §6.1 | Stable partition count |
| Consistent hashing | Ring above | Membership changes with limited reassignment |
| Directory | §3.1 | Explicit per-user or per-tenant placement |
| Range | Ordered boundary lookup below | Ordered scans |

- **Range variant:** boundaries are sorted exclusive upper bounds.
  - The number of shards is `len(boundaries) + 1`.
  - Equality routes to the next shard.

**Flow**

→ Receive sorted exclusive upper boundaries.  
→ Binary-search for the first boundary strictly greater than the key.  
→ Return that boundary index as the shard number.  
→ If no greater boundary exists, return the final shard index.

```python
from bisect import bisect_right

def range_shard(key: int, boundaries: list[int]) -> int:
    return bisect_right(boundaries, key)
# Time: O(log boundaries), Space: O(1).
```

```java
final class RangeShard {
    static int locate(long key, long[] boundaries) {
        int lo = 0, hi = boundaries.length;
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (key < boundaries[mid]) hi = mid;
            else lo = mid + 1;
        }
        return lo;
    }
}
```

#### Follow-up — split one hot counter

- **Extended requirement:** distribute increments for a celebrity counter across a fixed number of buckets.
- **Implementation:** assign each event to a stable salted bucket.
  - The snippets model bucket updates in one process.
  - A deployed version uses atomic increments on the corresponding owning shards.
  - Reads sum all buckets.
  - Delivery is assumed once per event in this exercise.
  - Stable bucketing alone does not deduplicate repeated events.

**Flow**

→ Hash the event ID into one of the fixed counter buckets.  
→ Atomically increment only that bucket.  
→ For a total, read and sum each bucket.  
→ Return the aggregated count after visiting all buckets.

```python
import hashlib
from threading import Lock

class SaltedCounter:
    def __init__(self, buckets: int):
        if buckets <= 0:
            raise ValueError("positive bucket count")
        self.counts = [0] * buckets
        self.locks = [Lock() for _ in range(buckets)]

    def add(self, event_id: str):
        digest = hashlib.sha256(event_id.encode()).digest()
        i = int.from_bytes(digest[:8], "big") % len(self.counts)
        with self.locks[i]:
            self.counts[i] += 1

    def total(self) -> int:
        result = 0
        for i, lock in enumerate(self.locks):
            with lock:
                result += self.counts[i]
        return result
# Time: O(event bytes) add, O(buckets) read; Space: O(buckets).
```

```java
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.concurrent.atomic.AtomicLongArray;

final class SaltedCounter {
    private final AtomicLongArray counts;
    SaltedCounter(int buckets) {
        if (buckets <= 0) throw new IllegalArgumentException();
        counts = new AtomicLongArray(buckets);
    }
    void add(String eventId) throws Exception {
        long hash = ByteBuffer.wrap(MessageDigest.getInstance("SHA-256")
            .digest(eventId.getBytes(StandardCharsets.UTF_8))).getLong();
        counts.incrementAndGet((int) Long.remainderUnsigned(hash, counts.length()));
    }
    long total() {
        long sum = 0;
        for (int i = 0; i < counts.length(); i++) sum += counts.get(i);
        return sum;
    }
}
```

- **L5 extra:** totals are not atomic multi-bucket snapshots.
  - Salting removes per-key total order.
  - Changing the bucket count needs versioned routing.

#### Migration variant — fence, catch up, then cut over

- **Classic requirement:** prevent a snapshot backfill from overwriting newer copied data.
- **Scope:** local versioned-copy model.
  - Versions come from one authoritative source log.
  - Deletions are represented by `None` / `null` tombstones.
  - Snapshot and change-log records share the same version space.

**Flow**

→ Receive a copied key with its authoritative version and value or tombstone.  
→ Compare it with the version already stored at the target.  
→ Replace the target row only when the incoming version is newer.  
→ Ignore older or equal-version copies.  
→ For cutover readiness, require old-owner fencing and a target applied prefix at the final source barrier.

```python
class MigrationTarget:
    def __init__(self):
        self.rows = {}

    def copy(self, key: str, version: int, value):
        old = self.rows.get(key)
        if old is None or version > old[0]:
            self.rows[key] = (version, value)

def ready_to_cutover(source_fenced: bool, barrier: int, applied_prefix: int) -> bool:
    return source_fenced and applied_prefix >= barrier
# Time: O(1) average per copy, Space: O(keys), including tombstones.
```

```java
import java.util.HashMap;
import java.util.Map;

final class MigrationTarget {
    record Row(long version, String value) {}
    private final Map<String, Row> rows = new HashMap<>();
    synchronized void copy(String key, long version, String value) {
        Row old = rows.get(key);
        if (old == null || version > old.version()) rows.put(key, new Row(version, value));
    }
    synchronized Row read(String key) { return rows.get(key); }
    static boolean ready(boolean sourceFenced, long barrier, long appliedPrefix) {
        return sourceFenced && appliedPrefix >= barrier;
    }
}
```

→ Capture a source snapshot and the corresponding log position.  
→ Copy the snapshot while replaying subsequent changes by version.  
→ Fence old-owner writes and record the final log barrier.  
→ Wait for the target's contiguous applied prefix to reach that barrier.  
→ Atomically advance the directory generation and admit target writes.  
⇒ Stale routers must refresh instead of writing to the old owner.

- **L5 extra:** counts and checksums alone do not prove a safe cutover.
  - Independent dual writes can lose one side.
  - Retain tombstones until older snapshots and delayed events cannot reappear.
  - The model's readiness predicate depends on trustworthy protocol inputs.

<a id="s63"></a>
### 6.3 Replication, failover, and quorum limits

- **Classic requirement:** expose the difference between local append, follower acknowledgement, and client acknowledgement.
- **Scope:** fixed-leader, no-election replication model.
  - Acknowledged entries are durable only under the stated storage assumption.
  - Each follower stores a contiguous prefix.
  - The model has no network or disk implementation.

**Flow**

→ Append the entry to the current leader log.  
→ Advance the leader applied prefix and return the entry offset.  
→ As a follower replays a contiguous prefix, advance its recorded offset.  
→ For a client acknowledgement, count replicas that have reached the entry offset.  
→ Report success only when that count meets the configured acknowledgement requirement.

```python
class ReplicatedLog:
    def __init__(self, replicas: int):
        if replicas <= 0:
            raise ValueError("replicas")
        self.log = []
        self.applied = [0] * replicas

    def append(self, value: str) -> int:
        self.log.append(value)
        self.applied[0] = len(self.log)
        return len(self.log)

    def replay(self, replica: int, prefix: int):
        if not 0 < replica < len(self.applied):
            raise ValueError("follower required")
        if not self.applied[replica] <= prefix <= len(self.log):
            raise ValueError("invalid prefix")
        self.applied[replica] = prefix

    def acknowledged(self, offset: int, required: int) -> bool:
        if not 1 <= required <= len(self.applied) or not 1 <= offset <= len(self.log):
            raise ValueError("invalid acknowledgement policy")
        return sum(prefix >= offset for prefix in self.applied) >= required
# Time: O(1) append/replay, O(replicas) acknowledgement; Space: O(log + replicas).
```

```java
import java.util.ArrayList;
import java.util.List;

final class ReplicatedLog {
    private final List<String> log = new ArrayList<>();
    private final int[] applied;
    ReplicatedLog(int replicas) {
        if (replicas <= 0) throw new IllegalArgumentException();
        applied = new int[replicas];
    }
    synchronized int append(String value) {
        log.add(value); applied[0] = log.size(); return log.size();
    }
    synchronized void replay(int replica, int prefix) {
        if (replica <= 0 || replica >= applied.length || prefix < applied[replica]
                || prefix > log.size()) throw new IllegalArgumentException();
        applied[replica] = prefix;
    }
    synchronized boolean acknowledged(int offset, int required) {
        if (required < 1 || required > applied.length || offset < 1 || offset > log.size())
            throw new IllegalArgumentException();
        int count = 0;
        for (int prefix : applied) if (prefix >= offset) count++;
        return count >= required;
    }
}
```

- **Interview question:** is majority acknowledgement alone a complete consensus algorithm?
  - Election safety and recovery must also preserve committed entries.
  - Membership changes need their own safe protocol.
  - Reading a replica still needs a freshness rule.
- **L5 extra:** zero-loss failover requires durable acknowledgements from a sufficient failure set.
  - The promoted replica must contain every acknowledged entry.
  - Fence the old leader using §2.2.
  - Do not promote an arbitrary reachable follower.

#### Leaderless variant — select the highest version in a read quorum

- **Classic requirement:** read from `R` distinct replicas and select the highest observed version.
- **Scope:** fixed membership with globally comparable versions.
  - `W + R > N` proves set overlap only.
  - This teaching function does not implement linearizable registers.
  - It does not hide concurrent conflicting values.

**Flow**

→ Require responses from at least the configured number of distinct replicas.  
→ Find the highest version among the received responses.  
→ Collect values reported at that version.  
→ Reject conflicting values that need an explicit merge.  
→ Return the highest version and its unambiguous value.

```python
def quorum_read(responses: dict[str, tuple[int, str]], required: int):
    if required <= 0 or len(responses) < required:
        raise RuntimeError("read quorum unavailable")
    newest = max(version for version, _ in responses.values())
    values = {value for version, value in responses.values() if version == newest}
    if len(values) != 1:
        raise RuntimeError("conflicting values need merge")
    return newest, values.pop()
# Time: O(responses), Space: O(responses).
```

```java
import java.util.HashSet;
import java.util.Map;

final class QuorumRead {
    record Value(long version, String data) {}
    static Value read(Map<String, Value> responses, int required) {
        if (required <= 0 || responses.size() < required)
            throw new IllegalStateException("quorum unavailable");
        long newest = responses.values().stream().mapToLong(Value::version).max().orElseThrow();
        var values = new HashSet<String>();
        for (Value v : responses.values()) if (v.version() == newest) values.add(v.data());
        if (values.size() != 1) throw new IllegalStateException("conflict");
        return new Value(newest, values.iterator().next());
    }
}
```

- **Multi-leader merge variant:** grow-only per-origin counters.
  - Each origin alone increments its component.
  - Merge each component with `max`.
  - Sum components for the visible total.
  - This is a CRDT for counts, not a merge rule for arbitrary balances.

**Flow**

→ For each remote origin, compare its count with the local component.  
→ Keep the larger component value.  
→ Repeat for every received origin.  
→ Sum the resulting local components.  
→ Return the merged visible count.

```python
def merge_counter(local: dict[str, int], remote: dict[str, int]):
    for origin, count in remote.items():
        local[origin] = max(local.get(origin, 0), count)
    return sum(local.values())
# Time: O(origins), Space: O(origins).
```

```java
import java.util.Map;

final class MergeCounter {
    static long merge(Map<String, Long> local, Map<String, Long> remote) {
        remote.forEach((origin, count) -> local.merge(origin, count, Math::max));
        long sum = 0;
        for (long count : local.values()) sum = Math.addExact(sum, count);
        return sum;
    }
}
```

- **L5 extra:** origin IDs must not be reused after resetting component state.
  - Retain state durably or allocate a new incarnation ID.
  - Arrival time and wall-clock LWW can discard a causally later update.

<a id="s64"></a>
### 6.4 CAP and PACELC read policy

- **Classic requirement:** a balance read requires verified fresh state while a feed read may accept stale state.
- **Scope:** read-path policy over a supplied leader-read callback.
  - `strong_read` must implement the database's valid leader/read-barrier protocol.
  - The cache may contain stale committed state.

**Flow**

→ Attempt the verified strong-read callback.  
→ Return its value as verified on success.  
→ If it times out, check whether stale reads are permitted and a cached value exists.  
→ Return the cache value with a stale marker only when both conditions hold.  
→ Otherwise, propagate the timeout.

```python
def read_policy(strong_read, cached_value, allow_stale: bool):
    try:
        return strong_read(), "verified"
    except TimeoutError:
        if not allow_stale or cached_value is None:
            raise
        return cached_value, "stale"
# Time: O(1) wrapper overhead, Space: O(1).
```

```java
import java.util.concurrent.Callable;
import java.util.concurrent.TimeoutException;

final class ReadPolicy {
    record Result(String value, boolean stale) {}
    static Result read(Callable<String> strongRead, String cached, boolean allowStale)
            throws Exception {
        try { return new Result(strongRead.call(), false); }
        catch (TimeoutException failure) {
            if (!allowStale || cached == null) throw failure;
            return new Result(cached, true);
        }
    }
}
```

- **L5 extra:** a stale-read fallback is one availability decision.
  - It does not establish availability for every operation in the CAP definition.
  - During healthy operation, §6.3's acknowledgement policy also trades latency against durability.
  - Replication mode alone does not determine every consistency guarantee.

<a id="s7"></a>
## 7. Design-round question-to-code map

| Source question | L4 implementation to write | L5 extension to defend |
| --- | --- | --- |
| Why not one big Postgres? | [Bound admission](#s11) | Measure the actual bottleneck before partitioning |
| Sharding versus replication? | [Shard topology](#s61) and [replication acknowledgements](#s63) | Separate ownership from durability |
| IDs for sharded orders? | [Snowflake](#s42) | Worker reuse and restart safety |
| What if one shard is hot? | [Salted counter](#s62) | Fan-in reads and loss of per-key order |
| Leader dies mid-write? | [Transactional idempotency](#s51) | [Fence stale leaders](#s22) and preserve the committed prefix |

- **Practice rule:** implement the linked snippet before discussing the extra.
  - The source repeats these concepts as interview questions.
  - Reuse the implementations instead of maintaining a second divergent copy.

<a id="s8"></a>
## 8. Local concurrency

<a id="s81"></a>
### 8.1 Partition the contention domain

- **Classic requirement:** update unrelated keys concurrently while serializing updates to the same key.
- **L4 implementation:** striped locks with one map per stripe.
  - Hash collisions share a lock safely.
  - All accesses to a stripe's map use its lock.
  - Python uses ordinary dictionaries.
- **Distributed analogy:** one owning partition per key.
  - Local lock ownership does not imply distributed ownership.

**Flow**

→ Hash the key to a local lock stripe.  
→ Acquire that stripe lock.  
→ Read and increment the key in the stripe-owned map.  
→ Store and return the updated count.  
→ Release the stripe lock.

```python
from threading import Lock

class StripedMap:
    def __init__(self, stripes: int = 16):
        if stripes <= 0:
            raise ValueError("stripes")
        self.locks = [Lock() for _ in range(stripes)]
        self.maps = [{} for _ in range(stripes)]

    def increment(self, key: str) -> int:
        i = hash(key) % len(self.maps)  # Stable only within this process is sufficient.
        with self.locks[i]:
            value = self.maps[i].get(key, 0) + 1
            self.maps[i][key] = value
            return value
# Time: O(1) average per update, Space: O(keys + stripes).
```

```java
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

final class StripedMap {
    private final List<Map<String, Long>> maps = new ArrayList<>();
    private final Object[] locks;
    StripedMap(int stripes) {
        if (stripes <= 0) throw new IllegalArgumentException();
        locks = new Object[stripes];
        for (int i = 0; i < stripes; i++) {
            locks[i] = new Object(); maps.add(new HashMap<>());
        }
    }
    long increment(String key) {
        int i = Math.floorMod(key.hashCode(), locks.length);
        synchronized (locks[i]) {
            long value = Math.addExact(maps.get(i).getOrDefault(key, 0L), 1L);
            maps.get(i).put(key, value); return value;
        }
    }
}
```

- **L5 extra:** an operation spanning stripes needs a locking order.
  - Acquire distinct stripes in increasing index order.
  - A sum assembled one stripe at a time is not an atomic snapshot.

<a id="s82"></a>
### 8.2 Publication and happens-before

- **Classic requirement:** publish an entire configuration snapshot to readers without exposing partially updated fields.
- **L4 implementation:** replace an immutable snapshot.
  - Python protects access with a lock.
  - Java publishes a defensive copy through a `volatile` reference.
  - Do not mutate the published object afterward.

**Flow**

→ Copy the incoming configuration into an immutable snapshot.  
→ Publish the snapshot through the Python lock or Java volatile reference.  
→ For a read, capture the currently published snapshot through the same publication mechanism.  
→ Read the request configuration from that one captured snapshot.

```python
from threading import Lock
from types import MappingProxyType

class ConfigSnapshot:
    def __init__(self):
        self.lock = Lock()
        self.current = MappingProxyType({})

    def publish(self, values: dict[str, str]):
        snapshot = MappingProxyType(dict(values))
        with self.lock:
            self.current = snapshot

    def read(self):
        with self.lock:
            return self.current
# Time: O(entries) publish, O(1) read; Space: O(entries) per retained snapshot.
```

```java
import java.util.Map;

final class ConfigSnapshot {
    private volatile Map<String, String> current = Map.of();
    void publish(Map<String, String> values) { current = Map.copyOf(values); }
    Map<String, String> read() { return current; }
}
```

- **Interview question:** can `volatile` make `count++` atomic?
  - The compound operation still needs a lock or atomic update.
- **L5 extra:** the snapshot must be deeply immutable for nested mutable values.
  - This example restricts values to immutable strings.
  - Capture one snapshot per request when multiple fields must be consistent.
  - Java `Thread.start()` and `join()` establish additional happens-before edges. [Java concurrency memory effects](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/concurrent/package-summary.html)
  - Python code does not assume that the GIL protects compound operations. [Python threading](https://docs.python.org/3/library/threading.html)

<a id="s83"></a>
### 8.3 Locks, read-heavy state, and deadlock

- **Classic requirement:** transfer between two in-memory accounts without deadlock.
- **L4 implementation:** acquire locks by a globally unique immutable account ID.
  - Reject invalid amounts.
  - Compute both resulting balances before mutating either account.
  - Bound time waiting for the locks.
- **Scope:** local account objects with no access outside their locks.
  - A registry must provide one object per account ID.
  - The timeout bounds lock acquisition, not arbitrary work inside the critical section.

**Flow**

→ Validate the amount and handle a transfer to the same object.  
→ Order the two distinct accounts by immutable account ID.  
→ Acquire the first lock within the timeout.  
→ Acquire the second lock using the remaining timeout budget.  
→ Check funds and compute the resulting balances before mutating either account.  
→ Apply the transfer and release both locks in finally blocks.

```python
import time
from threading import Lock

class LocalAccount:
    def __init__(self, account_id: int, balance: int):
        if balance < 0:
            raise ValueError("balance")
        self.id, self.balance = account_id, balance
        self.lock = Lock()

def transfer(source: LocalAccount, target: LocalAccount, amount: int, timeout: float = 1.0):
    if amount <= 0 or timeout < 0:
        raise ValueError("amount or timeout")
    if source is target:
        return
    if source.id == target.id:
        raise ValueError("duplicate account identity")
    first, second = sorted((source, target), key=lambda a: a.id)
    deadline = time.monotonic() + timeout
    if not first.lock.acquire(timeout=timeout):
        raise TimeoutError("first lock")
    try:
        if not second.lock.acquire(timeout=max(0, deadline - time.monotonic())):
            raise TimeoutError("second lock")
        try:
            if source.balance < amount:
                raise ValueError("insufficient funds")
            source.balance, target.balance = source.balance - amount, target.balance + amount
        finally:
            second.lock.release()
    finally:
        first.lock.release()
# Time: O(1) excluding lock waits, Space: O(1).
```

```java
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.concurrent.locks.ReentrantLock;

final class LocalAccount {
    final long id;
    long balance;
    final ReentrantLock lock = new ReentrantLock();
    LocalAccount(long id, long balance) {
        if (balance < 0) throw new IllegalArgumentException();
        this.id = id; this.balance = balance;
    }
    static void transfer(LocalAccount from, LocalAccount to, long amount, long timeoutMillis)
            throws InterruptedException, TimeoutException {
        if (amount <= 0 || timeoutMillis < 0 || timeoutMillis > 60_000)
            throw new IllegalArgumentException();
        if (from == to) return;
        if (from.id == to.id) throw new IllegalArgumentException("duplicate identity");
        LocalAccount first = from.id < to.id ? from : to;
        LocalAccount second = from.id < to.id ? to : from;
        long budget = TimeUnit.MILLISECONDS.toNanos(timeoutMillis), start = System.nanoTime();
        if (!first.lock.tryLock(budget, TimeUnit.NANOSECONDS)) throw new TimeoutException();
        try {
            long remaining = Math.max(0, budget - (System.nanoTime() - start));
            if (!second.lock.tryLock(remaining, TimeUnit.NANOSECONDS)) throw new TimeoutException();
            try {
                if (from.balance < amount) throw new IllegalStateException("insufficient");
                long nextTarget = Math.addExact(to.balance, amount);
                from.balance -= amount; to.balance = nextTarget;
            } finally { second.lock.unlock(); }
        } finally { first.lock.unlock(); }
    }
}
```

| Tool in source | Implementation here | Choose when |
| --- | --- | --- |
| `synchronized` / Python `Lock` | §2.1 and §8.7.4 | Short atomic critical section |
| `ReentrantLock` / timed Python lock | Transfer above | Timeout or interruption matters |
| `ReentrantReadWriteLock` | Read-heavy map below | Parallel readers justify extra lock overhead |
| `StampedLock` | Validated scalar snapshot below | Very short optimistic reads |
| `Condition` | §8.7.2 | Wait for a state predicate |

- **Read-heavy variant:** many readers share a dictionary while writes are infrequent.
  - Java uses a read/write lock.
  - Python's standard library has no direct read/write-lock counterpart.
  - Use a normal lock for the same correctness requirement before adding a custom primitive.

**Flow**

→ Choose the lock mode for the operation.  
→ For a read, acquire the Python mutex or Java read lock.  
→ Look up the key and release the lock.  
→ For a write, acquire the Python mutex or Java write lock.  
→ Replace the value and release the lock.

```python
from threading import Lock

class ReadMostlyMap:
    def __init__(self):
        self.data = {}
        self.lock = Lock()

    def get(self, key: str):
        with self.lock:
            return self.data.get(key)

    def put(self, key: str, value: str):
        with self.lock:
            self.data[key] = value
# Time: O(1) average, Space: O(keys).
```

```java
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.locks.ReentrantReadWriteLock;

final class ReadMostlyMap {
    private final Map<String, String> data = new HashMap<>();
    private final ReentrantReadWriteLock lock = new ReentrantReadWriteLock();
    String get(String key) {
        lock.readLock().lock();
        try { return data.get(key); }
        finally { lock.readLock().unlock(); }
    }
    void put(String key, String value) {
        lock.writeLock().lock();
        try { data.put(key, value); }
        finally { lock.writeLock().unlock(); }
    }
}
```

- **Optimistic-read variant:** read a coherent pair of coordinates.
  - Python takes a lock.
  - Java copies fields optimistically and validates before using them.
  - On failed validation, read again under a read lock. [StampedLock contract](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/concurrent/locks/StampedLock.html)

**Flow**

→ For a coordinate update, hold the write lock across both field assignments.  
→ In Python, read both coordinates while holding the same lock.  
→ In Java, obtain an optimistic stamp and copy both coordinates.  
→ Validate the stamp before using the copied coordinates.  
→ If validation fails, reread both coordinates under a read lock.  
→ Return the coherent coordinate pair.

```python
from threading import Lock

class PointSnapshot:
    def __init__(self):
        self.x = self.y = 0
        self.lock = Lock()

    def set(self, x: int, y: int):
        with self.lock:
            self.x, self.y = x, y

    def read(self):
        with self.lock:
            return self.x, self.y
# Time: O(1), Space: O(1).
```

```java
import java.util.concurrent.locks.StampedLock;

final class PointSnapshot {
    private long x, y;
    private final StampedLock lock = new StampedLock();
    void set(long x, long y) {
        long stamp = lock.writeLock();
        try { this.x = x; this.y = y; }
        finally { lock.unlockWrite(stamp); }
    }
    long[] read() {
        long stamp = lock.tryOptimisticRead();
        long a = x, b = y;
        if (!lock.validate(stamp)) {
            stamp = lock.readLock();
            try { a = x; b = y; }
            finally { lock.unlockRead(stamp); }
        }
        return new long[] {a, b};
    }
}
```

- **L5 extra:** optimistic reads must not perform side effects before validation.
  - Do not traverse mutable structures that can become invalid while reading.
  - `StampedLock` is not reentrant.
  - A read/write lock can starve writers under some access patterns.
  - Benchmark before replacing a short ordinary lock.

<a id="s84"></a>
### 8.4 CAS, atomics, and ABA

- **Classic requirement:** update a value only if both its value and version still match a previous observation.
- **L4 implementation:** attach a monotonically increasing version to each successful change.
  - Java uses `AtomicStampedReference`.
  - Python emulates compare-and-set under a lock.
  - Python's version is not a hardware lock-free primitive.
- **ABA question:** a value changes from A to B and back to A before your update.
  - A value-only comparison misses the intervening change.
  - A changed version rejects the stale update.

**Flow**

→ Read the current value together with its version.  
→ Prepare an update against that exact observation.  
→ Atomically compare both the expected value and version.  
→ If either differs, reject the stale update.  
→ Otherwise, install the new value with an incremented version.

```python
from threading import Lock

class VersionedCell:
    def __init__(self, value):
        self.value, self.version = value, 0
        self.lock = Lock()

    def read(self):
        with self.lock:
            return self.value, self.version

    def compare_set(self, expected, version: int, update) -> bool:
        with self.lock:
            if self.value != expected or self.version != version:
                return False
            self.value, self.version = update, self.version + 1
            return True
# Time: O(1) for scalar values, Space: O(1).
```

```java
import java.util.concurrent.atomic.AtomicStampedReference;

final class VersionedCell<T> {
    record Snapshot<T>(T value, int version) {}
    private final AtomicStampedReference<T> cell;
    VersionedCell(T initial) { cell = new AtomicStampedReference<>(initial, 0); }
    Snapshot<T> read() {
        int[] stamp = new int[1];
        T value = cell.get(stamp);
        return new Snapshot<>(value, stamp[0]);
    }
    boolean compareSet(Snapshot<T> expected, T update) {
        int next = Math.incrementExact(expected.version());
        return cell.compareAndSet(expected.value(), update, expected.version(), next);
    }
}
```

- **L5 extra:** Java reference CAS compares identity.
  - Keep the exact reference returned by `read()`.
  - This example rejects stamp overflow instead of silently wrapping.
  - A lock-free algorithm does not imply fairness for each contending thread.
  - The numeric CAS retry loop appears in §8.7.3.

<a id="s85"></a>
### 8.5 Concurrent collections

- **Classic requirement:** count events concurrently per key without a check-then-act race.
- **L4 implementation:** atomic map update.
  - Python protects a dictionary with a lock.
  - Java uses `ConcurrentHashMap.merge`.

**Flow**

→ Receive an event key.  
→ Atomically read the existing count or initialize it to zero.  
→ Increment and store the count within the same protected operation.  
→ Return the new per-key count.

```python
from threading import Lock

class KeyCounts:
    def __init__(self):
        self.counts = {}
        self.lock = Lock()

    def add(self, key: str) -> int:
        with self.lock:
            value = self.counts.get(key, 0) + 1
            self.counts[key] = value
            return value
# Time: O(1) average, Space: O(keys).
```

```java
import java.util.concurrent.ConcurrentHashMap;

final class KeyCounts {
    private final ConcurrentHashMap<String, Long> counts = new ConcurrentHashMap<>();
    long add(String key) { return counts.merge(key, 1L, Math::addExact); }
}
```

#### Follow-up — high-contention metrics

- **Extended requirement:** favor concurrent increments over an exact instantaneous total.
- **Implementation:** striped counters in Python and `LongAdder` in Java.
  - Python's implementation shows the partitioned mechanism explicitly.
  - Each update takes only its stripe lock.
  - Read aggregation is not an atomic snapshot.

**Flow**

→ Choose a counter stripe or let LongAdder select its internal update cell.  
→ Atomically increment that component.  
→ For a read, sum the component values.  
→ Return the total without claiming a simultaneous snapshot of all components.

```python
from threading import Lock

class MetricCounter:
    def __init__(self, stripes: int = 16):
        if stripes <= 0:
            raise ValueError("stripes")
        self.values = [0] * stripes
        self.locks = [Lock() for _ in range(stripes)]

    def add(self, worker_id: int):
        i = worker_id % len(self.values)
        with self.locks[i]:
            self.values[i] += 1

    def total(self):
        total = 0
        for i, lock in enumerate(self.locks):
            with lock:
                total += self.values[i]
        return total
# Time: O(1) update, O(stripes) read; Space: O(stripes).
```

```java
import java.util.concurrent.atomic.LongAdder;

final class MetricCounter {
    private final LongAdder value = new LongAdder();
    void add() { value.increment(); }
    long total() { return value.sum(); }
}
```

- **Snapshot-list variant:** notify listeners without holding a registry lock during callbacks.
  - Python copies a tuple reference under the lock.
  - Java iterates a `CopyOnWriteArrayList` snapshot.
  - Registration changes affect later snapshots.
  - This minimal version propagates a listener exception and stops that notification pass.

**Flow**

→ On registration, replace or copy the listener collection under its mutation mechanism.  
→ At notification time, capture an iteration snapshot.  
→ Invoke each listener from that snapshot without holding the registry mutation lock.  
→ Propagate a callback failure according to the stated notification policy.  
→ Allow later registrations to affect subsequent snapshots.

```python
from threading import Lock

class Listeners:
    def __init__(self):
        self.listeners = ()
        self.lock = Lock()

    def add(self, listener):
        with self.lock:
            self.listeners = self.listeners + (listener,)

    def notify(self, event):
        with self.lock:
            snapshot = self.listeners
        for listener in snapshot:
            listener(event)
# Time: O(listeners) register/notify, Space: O(listeners) per retained snapshot.
```

```java
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.function.Consumer;

final class Listeners<T> {
    private final CopyOnWriteArrayList<Consumer<T>> listeners = new CopyOnWriteArrayList<>();
    void add(Consumer<T> listener) { listeners.add(listener); }
    void notifyListeners(T event) {
        for (Consumer<T> listener : listeners) listener.accept(event);
    }
}
```

- **L5 extra:** atomic per-key methods do not make multi-key transactions atomic.
  - Keep map remapping functions short.
  - Avoid external side effects in functions that may be retried by an optimistic API.
  - Use the bounded queue in §8.7.2 for producer-consumer coordination.

<a id="s86"></a>
### 8.6 Executors, futures, and virtual threads

- **Classic requirement:** bound accepted background work and return a future for each accepted task.
- **L4 implementation:** fixed worker count with explicit overload rejection.
  - Python workers consume an explicitly bounded queue.
  - Java uses a bounded executor queue with `AbortPolicy`.
  - Neither version silently drops rejected work.
  - Owners shut down the executor after use.

**Flow**

→ Initialize the fixed worker pool and bounded work queue.  
→ On submission, reject closed or overloaded intake.  
→ Queue accepted work and return its future.  
→ A worker removes a task and skips it if cancellation already won.  
→ Otherwise, run it and complete the future with its value or exception.  
→ On close, stop intake and follow the language-specific drain or cancellation policy.

```python
from concurrent.futures import Future
from queue import Full, Queue
from threading import Lock, Thread

class BoundedExecutor:
    def __init__(self, workers: int, queued: int):
        if workers <= 0 or queued <= 0:
            raise ValueError("positive limits")
        self.queue = Queue(maxsize=queued)
        self.lock, self.closed = Lock(), False
        self.workers = [Thread(target=self._run) for _ in range(workers)]
        for worker in self.workers:
            worker.start()

    def _run(self):
        while True:
            entry = self.queue.get()
            try:
                if entry is None:
                    return
                future, work = entry
                if future.set_running_or_notify_cancel():
                    try:
                        future.set_result(work())
                    except BaseException as failure:
                        future.set_exception(failure)
            finally:
                self.queue.task_done()

    def submit(self, work):
        with self.lock:
            if self.closed:
                raise RuntimeError("closed")
            future = Future()
            try:
                self.queue.put_nowait((future, work))
            except Full:
                raise RuntimeError("overloaded") from None
            return future

    def close(self):
        with self.lock:
            if self.closed:
                return
            self.closed = True
        for _ in self.workers:
            self.queue.put(None)
        for worker in self.workers:
            worker.join()
# Time: O(1) submission overhead, Space: O(workers + queued) live tasks.
```

```java
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.Callable;
import java.util.concurrent.Future;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;

final class BoundedExecutor implements AutoCloseable {
    private final ThreadPoolExecutor pool;
    BoundedExecutor(int workers, int queued) {
        if (workers <= 0 || queued <= 0) throw new IllegalArgumentException();
        pool = new ThreadPoolExecutor(workers, workers, 0, TimeUnit.MILLISECONDS,
            new ArrayBlockingQueue<>(queued), new ThreadPoolExecutor.AbortPolicy());
    }
    <T> Future<T> submit(Callable<T> task) { return pool.submit(task); }
    private void stopNow() {
        for (Runnable queued : pool.shutdownNow())
            if (queued instanceof Future<?> future) future.cancel(false);
    }
    public void close() throws InterruptedException {
        pool.shutdown();
        try {
            if (!pool.awaitTermination(5, TimeUnit.SECONDS)) stopNow();
        } catch (InterruptedException failure) {
            stopNow(); throw failure;
        }
    }
}
```

- **L5 extra:** Java shutdown interruption is cooperative.
  - Tasks that ignore interruption can continue running.
  - Python cannot forcibly terminate a running thread.
  - Call `close()` from the owning thread after stopping intake.
  - A worker must not close and join its own pool.
  - Cancelled queued work retains its queue slot until a worker removes it.
  - Releasing a semaphore permit immediately on cancellation would not bound an executor's physical unbounded queue.
  - Keep transport timeouts inside each task. [Python futures](https://docs.python.org/3/library/concurrent.futures.html)
  - `CallerRunsPolicy` is an alternative only when blocking the submitter is acceptable.
  - With an unbounded Java executor queue, work ordinarily queues instead of expanding beyond the core pool. [ThreadPoolExecutor](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/concurrent/ThreadPoolExecutor.html)

#### Follow-up — fan out with one deadline

- **Extended requirement:** fetch several independent dependencies with a shared deadline and cancel remaining work on failure.
- **Contract:** the caller owns the executor and bounds the number of dependencies.
  - Python accepts a `concurrent.futures.Executor`.
  - Java accepts an `ExecutorService`.
  - Each dependency still needs its own I/O timeout.

**Flow**

→ Validate the timeout and record one monotonic deadline.  
→ Submit the bounded list of independent calls to the supplied executor.  
→ Collect results using only the remaining deadline budget for each wait.  
→ On failure or timeout, leave through the same cleanup path.  
→ Request cancellation for all outstanding futures in finally.

```python
import time

def fanout(pool, calls: list, timeout: float):
    if timeout <= 0:
        raise ValueError("timeout")
    deadline = time.monotonic() + timeout
    futures = []
    try:
        for call in calls:
            futures.append(pool.submit(call))
        return [f.result(timeout=max(0, deadline - time.monotonic())) for f in futures]
    finally:
        for future in futures:
            future.cancel()
# Time: O(calls) orchestration, Space: O(calls).
```

```java
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;

final class Fanout {
    static <T> List<T> fetch(ExecutorService pool, List<Callable<T>> calls, long timeoutMillis)
            throws Exception {
        if (timeoutMillis <= 0 || timeoutMillis > 60_000) throw new IllegalArgumentException();
        long start = System.nanoTime(), budget = TimeUnit.MILLISECONDS.toNanos(timeoutMillis);
        List<Future<T>> futures = new ArrayList<>();
        try {
            for (Callable<T> call : calls) futures.add(pool.submit(call));
            List<T> results = new ArrayList<>();
            for (Future<T> future : futures)
                results.add(future.get(Math.max(0, budget - (System.nanoTime() - start)),
                                       TimeUnit.NANOSECONDS));
            return results;
        } finally {
            for (Future<T> future : futures) future.cancel(true);
        }
    }
}
```

- **Composition variant:** combine independent computations without manually blocking for intermediate results.
  - Python uses async tasks.
  - Java uses `CompletableFuture` with an explicit executor.
  - Java's non-async combination runs on a completing thread.

**Flow**

→ Start both independent computations on async tasks or the supplied executor.  
→ Wait for both computations through the composition mechanism.  
→ Combine their results when both succeed.  
→ Surface a failure or the configured timeout.  
→ Respect the language-specific cancellation boundary described below.

```python
import asyncio

async def compose(first, second, timeout: float = 1.0):
    async with asyncio.timeout(timeout):
        async with asyncio.TaskGroup() as group:
            a = group.create_task(first())
            b = group.create_task(second())
    return a.result() + b.result()
# Time: O(1) orchestration, Space: O(1) tasks.
```

```java
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Executor;
import java.util.concurrent.TimeUnit;
import java.util.function.Supplier;

final class Compose {
    static CompletableFuture<Integer> combine(Executor pool,
            Supplier<Integer> first, Supplier<Integer> second) {
        var a = CompletableFuture.supplyAsync(first, pool);
        var b = CompletableFuture.supplyAsync(second, pool);
        return a.thenCombine(b, Integer::sum).orTimeout(1, TimeUnit.SECONDS);
    }
}
```

- **Trap:** a `CompletableFuture` timeout completes the future exceptionally.
  - It does not guarantee that the underlying supplier stops.
  - Use the `Future` variant when you need an explicit interruption request.

#### Virtual-thread variant — bound scarce I/O resources

- **Classic requirement:** serve many blocking I/O tasks while allowing at most a fixed number to use a downstream resource.
- **Java version:** Java 21+.
- **Python counterpart:** async tasks with a semaphore.
  - Async I/O requires an async-compatible client.
  - A Python task is not a Java virtual thread.
  - The input batch itself is bounded by the caller.

**Flow**

→ Validate the downstream concurrency limit.  
→ Create an async task or virtual thread for each call in the bounded batch.  
→ Acquire a semaphore permit before entering the downstream operation.  
→ Release the permit even when the operation fails.  
→ Collect successful results and request cancellation during failure cleanup.

```python
import asyncio

async def limited_io(calls: list, limit: int):
    if limit <= 0:
        raise ValueError("limit")
    gate = asyncio.Semaphore(limit)

    async def run(call):
        async with gate:
            return await call()

    async with asyncio.TaskGroup() as group:
        tasks = [group.create_task(run(call)) for call in calls]
    return [task.result() for task in tasks]
# Time: O(calls) orchestration, Space: O(calls).
```

```java
// Java 21+
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.Semaphore;

final class VirtualIo {
    static <T> List<T> run(List<Callable<T>> calls, int limit) throws Exception {
        if (limit <= 0) throw new IllegalArgumentException();
        Semaphore gate = new Semaphore(limit);
        try (var pool = Executors.newVirtualThreadPerTaskExecutor()) {
            List<Future<T>> futures = new ArrayList<>();
            try {
                for (Callable<T> call : calls) futures.add(pool.submit(() -> {
                    gate.acquire();
                    try { return call.call(); }
                    finally { gate.release(); }
                }));
                List<T> results = new ArrayList<>();
                for (Future<T> future : futures) results.add(future.get());
                return results;
            } finally {
                for (Future<T> future : futures) future.cancel(true);
            }
        }
    }
}
```

- **L5 extra:** virtual threads do not increase database connection capacity.
  - Bound the scarce resource independently.
  - The executor's close waits for tasks to terminate.
  - Bound network calls even after requesting cancellation. [Java virtual threads](https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html)
  - CPU-bound work still competes for CPU cores.

<a id="s871"></a>
### 8.7.1 Lazy singleton

- **Classic requirement:** initialize one process-local configuration object on first access.
- **L4 implementation:** Python lock and Java initialization-on-demand holder.
  - Python checks and initializes while holding the same lock.
  - Java delegates safe initialization to class initialization.

**Flow**

→ Receive the first request for the process-local configuration.  
→ Use the Python lock or Java holder-class initialization to serialize creation.  
→ Construct the instance once and publish it safely.  
→ Return the same instance on subsequent calls.

```python
from threading import Lock

class LazyConfig:
    _instance = None
    _lock = Lock()

    @classmethod
    def get(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = object()
            return cls._instance
# Time: O(1) per access, Space: O(1).
```

```java
final class LazyConfig {
    private LazyConfig() {}
    private static class Holder {
        static final LazyConfig INSTANCE = new LazyConfig();
    }
    static LazyConfig get() { return Holder.INSTANCE; }
}
```

#### Follow-up — implement double-checked locking

- **Extended requirement:** explain the Java publication edge when implementing lazy initialization manually.
- **Java mechanism:** `volatile` instance reference plus a second check inside the monitor.
- **Python answer:** retain a locked accessor for portable correctness.
  - Python has no direct `volatile` declaration.
  - Do not copy Java DCL by removing synchronization from Python reads.

**Flow**

→ In Python, acquire the accessor lock and check the explicit initialization flag.  
→ Invoke the factory once and mark initialization complete only after success.  
→ In Java, read the volatile instance reference before entering the monitor.  
→ If absent, enter the monitor and check the reference again.  
→ Construct and publish only if the second check still finds no instance.  
→ Return the safely published instance.

```python
from threading import Lock

class ManualLazy:
    def __init__(self, factory):
        self.factory = factory
        self.instance = None
        self.initialized = False
        self.lock = Lock()

    def get(self):
        with self.lock:
            if not self.initialized:
                self.instance = self.factory()
                self.initialized = True
            return self.instance
# Time: O(1) after initialization, Space: O(1) excluding instance.
```

```java
final class DclConfig {
    private static volatile DclConfig instance;
    final int timeoutMillis;
    private DclConfig() { timeoutMillis = 1000; }
    static DclConfig get() {
        DclConfig local = instance;
        if (local == null) {
            synchronized (DclConfig.class) {
                local = instance;
                if (local == null) instance = local = new DclConfig();
            }
        }
        return local;
    }
}
```

- **L5 extra:** a singleton is scoped to a process or Java class loader.
  - It cannot elect one leader across machines.
  - Avoid recursive initialization through the factory.
  - Prefer injected dependencies when tests need alternate implementations.

<a id="s872"></a>
### 8.7.2 Bounded buffer

- **Classic requirement:** multiple producers and consumers share a fixed-capacity FIFO.
  - Producers wait when full.
  - Consumers wait when empty.
- **L4 implementation:** conditions over one protecting lock.
  - Recheck the predicate in a `while` loop after waking.
  - Wake the opposite side after modifying the queue.
  - Reject zero or negative capacity.

**Flow**

→ Acquire the queue lock for the requested operation.  
→ For put, wait in a loop while the buffer is full.  
→ Append the item and wake waiting consumers.  
→ For take, wait in a loop while the buffer is empty.  
→ Remove the oldest item and wake waiting producers.  
→ Release the queue lock on every exit.

```python
from collections import deque
from threading import Condition

class BoundedBuffer:
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("capacity")
        self.capacity = capacity
        self.items = deque()
        self.changed = Condition()

    def put(self, item):
        with self.changed:
            while len(self.items) == self.capacity:
                self.changed.wait()
            self.items.append(item)
            self.changed.notify_all()

    def take(self):
        with self.changed:
            while not self.items:
                self.changed.wait()
            item = self.items.popleft()
            self.changed.notify_all()
            return item
# Time: O(1) excluding waits, Space: O(capacity).
```

```java
import java.util.ArrayDeque;
import java.util.Objects;
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.ReentrantLock;

final class BoundedBuffer<T> {
    private final int capacity;
    private final ArrayDeque<T> items = new ArrayDeque<>();
    private final ReentrantLock lock = new ReentrantLock();
    private final Condition notFull = lock.newCondition(), notEmpty = lock.newCondition();
    BoundedBuffer(int capacity) {
        if (capacity <= 0) throw new IllegalArgumentException();
        this.capacity = capacity;
    }
    void put(T value) throws InterruptedException {
        Objects.requireNonNull(value);
        lock.lockInterruptibly();
        try {
            while (items.size() == capacity) notFull.await();
            items.addLast(value); notEmpty.signal();
        } finally { lock.unlock(); }
    }
    T take() throws InterruptedException {
        lock.lockInterruptibly();
        try {
            while (items.isEmpty()) notEmpty.await();
            T value = items.removeFirst(); notFull.signal(); return value;
        } finally { lock.unlock(); }
    }
}
```

#### Follow-up — timed enqueue under overload

- **Extended requirement:** stop waiting for space after a caller-supplied timeout.
- **Implementation:** standard bounded queues.
  - Python raises `Full` when the timeout expires.
  - Translate it into a rejected result.
  - Java's `offer` returns a boolean.
  - Java propagates interruption.

**Flow**

→ Validate a nonnegative timeout.  
→ Attempt to enqueue into the standard bounded queue within that timeout.  
→ Return success when space becomes available.  
→ Return a rejected result when the wait expires.  
→ Propagate interruption where the language API supports it.

```python
from queue import Full, Queue

def timed_put(queue: Queue, item, timeout: float) -> bool:
    if timeout < 0:
        raise ValueError("timeout")
    try:
        queue.put(item, timeout=timeout)
        return True
    except Full:
        return False
# Time: O(1) excluding waits, Space: O(1) wrapper overhead.
```

```java
import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.TimeUnit;

final class TimedBuffer {
    static <T> boolean put(ArrayBlockingQueue<T> queue, T item, long timeoutMillis)
            throws InterruptedException {
        if (timeoutMillis < 0) throw new IllegalArgumentException();
        return queue.offer(item, timeoutMillis, TimeUnit.MILLISECONDS);
    }
}
```

- **L5 extra:** the handwritten baseline has no shutdown protocol.
  - Production owners need cancellation or a closed-state condition.
  - A full queue bounds memory, but rejected work still needs an explicit caller policy.
  - SQS visibility timeout hides an in-flight message.
  - It does not bound the local queue's capacity.

<a id="s873"></a>
### 8.7.3 Optimistic balance update

- **Classic requirement:** concurrent withdrawals must never make a balance negative.
- **L4 implementation:** atomic conditional debit.
  - Java retries a CAS after a competing update.
  - Python holds a lock across the check and debit.
  - Reject zero and negative withdrawal amounts.

**Flow**

→ Validate a positive withdrawal amount.  
→ Observe the current balance within the language-specific atomic update mechanism.  
→ Reject the withdrawal if funds are insufficient.  
→ In Python, subtract while holding the lock.  
→ In Java, compare-and-set the observed balance to the reduced balance.  
→ If the Java CAS loses a race, reread the balance and repeat the funds check.

```python
from threading import Lock

class Balance:
    def __init__(self, amount: int):
        if amount < 0:
            raise ValueError("initial balance")
        self.amount = amount
        self.lock = Lock()

    def withdraw(self, amount: int) -> int:
        if amount <= 0:
            raise ValueError("positive withdrawal required")
        with self.lock:
            if self.amount < amount:
                raise ValueError("insufficient funds")
            self.amount -= amount
            return self.amount
# Time: O(1) excluding lock waits, Space: O(1).
```

```java
import java.util.concurrent.atomic.AtomicLong;

final class Balance {
    private final AtomicLong value;
    Balance(long initial) {
        if (initial < 0) throw new IllegalArgumentException();
        value = new AtomicLong(initial);
    }
    long withdraw(long amount) {
        if (amount <= 0) throw new IllegalArgumentException();
        while (true) {
            long current = value.get();
            if (current < amount) throw new IllegalStateException("insufficient");
            if (value.compareAndSet(current, current - amount)) return current - amount;
        }
    }
}
```

#### Follow-up — optimistic update across service instances

- **Extended requirement:** reject a write based on an obsolete database row version.
- **Dependency:** §5.1's `account` table plus the version column below.
- **Contract:** both helpers perform one conditional database update.
  - Use a dedicated autocommit connection.
  - Return no value when the expected version or available balance fails the predicate.
  - Re-read before retrying a version conflict.

**Flow**

→ Validate a positive withdrawal amount.  
→ Issue one database update scoped by tenant and account ID.  
→ Require both the expected row version and sufficient balance in the update predicate.  
→ On a match, subtract the amount and increment the version atomically.  
→ Return the new balance and version, or an empty result when the predicate does not match.

```sql
ALTER TABLE account ADD COLUMN version BIGINT NOT NULL DEFAULT 0;
```

```python
def withdraw_versioned(conn, tenant: str, account: str, expected: int, amount: int):
    if amount <= 0:
        raise ValueError("positive withdrawal required")
    return conn.execute(
        "UPDATE account SET balance=balance-%s,version=version+1 "
        "WHERE tenant=%s AND id=%s AND version=%s AND balance>=%s "
        "RETURNING balance,version", (amount, tenant, account, expected, amount)
    ).fetchone()
# Time: O(log accounts) excluding lock waits, Space: O(1).
```

```java
import java.sql.Connection;
import java.util.Optional;

final class VersionedDebit {
    record Result(long balance, long version) {}
    static Optional<Result> withdraw(Connection c, String tenant, String account,
                                     long expected, long amount) throws Exception {
        if (amount <= 0 || !c.getAutoCommit()) throw new IllegalArgumentException();
        try (var p = c.prepareStatement("UPDATE account SET balance=balance-?,version=version+1 "
                + "WHERE tenant=? AND id=? AND version=? AND balance>=? RETURNING balance,version")) {
            p.setLong(1, amount); p.setString(2, tenant); p.setString(3, account);
            p.setLong(4, expected); p.setLong(5, amount);
            try (var r = p.executeQuery()) {
                return r.next() ? Optional.of(new Result(r.getLong(1), r.getLong(2))) : Optional.empty();
            }
        }
    }
}
```

- **L5 extra:** optimistic locking prevents stale updates, not duplicate business requests.
  - A retry after an unknown commit result needs §5.1's request key.
  - Every writer must increment the version once this concurrency scheme is adopted.
  - Update §5.1's credit SQL to increment the version if combining the exercises.
  - Avoid emitting external side effects inside a CAS retry loop.

<a id="s874"></a>
### 8.7.4 Token bucket

- **Classic requirement:** permit a burst up to capacity and refill tokens at a constant rate.
- **L4 implementation:** use a monotonic clock and one short critical section.
  - Refill before checking the request cost.
  - Cap accumulated tokens at capacity.
  - Accept a deterministic clock for testing.
  - Rates and capacity are positive finite values.

**Flow**

→ Validate the request cost and acquire the bucket lock.  
→ Read the monotonic clock and calculate elapsed time.  
→ Refill by elapsed time times refill rate, capped at capacity.  
→ Record the current refill timestamp.  
→ Reject the request if tokens are insufficient.  
→ Otherwise, subtract the cost and admit the request.

```python
import math
import time
from threading import Lock

class TokenBucket:
    def __init__(self, capacity: int, rate: float, clock=time.monotonic):
        if capacity <= 0 or not math.isfinite(capacity) or rate <= 0 or not math.isfinite(rate):
            raise ValueError("capacity and rate")
        self.capacity, self.rate, self.clock = capacity, rate, clock
        self.tokens = float(capacity)
        self.last = clock()
        self.lock = Lock()

    def acquire(self, cost: int = 1) -> bool:
        if not 0 < cost <= self.capacity:
            raise ValueError("cost")
        with self.lock:
            now = self.clock()
            if now < self.last:
                raise RuntimeError("non-monotonic clock")
            self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)
            self.last = now
            if self.tokens < cost:
                return False
            self.tokens -= cost
            return True
# Time: O(1), Space: O(1).
```

```java
import java.util.function.LongSupplier;

final class TokenBucket {
    private final long capacity;
    private final double rate;
    private final LongSupplier clock;
    private double tokens;
    private long last;
    TokenBucket(long capacity, double rate, LongSupplier nanoClock) {
        if (capacity <= 0 || rate <= 0 || !Double.isFinite(rate))
            throw new IllegalArgumentException();
        this.capacity = capacity; this.rate = rate; this.clock = nanoClock;
        tokens = capacity; last = clock.getAsLong();
    }
    synchronized boolean acquire(long cost) {
        if (cost <= 0 || cost > capacity) throw new IllegalArgumentException();
        long now = clock.getAsLong(), elapsed = now - last;
        if (elapsed < 0) throw new IllegalStateException("non-monotonic clock");
        tokens = Math.min(capacity, tokens + elapsed / 1e9 * rate);
        last = now;
        if (tokens < cost) return false;
        tokens -= cost; return true;
    }
}
```

#### Follow-up — isolate each tenant's quota

- **Extended requirement:** one noisy tenant must not consume another tenant's local allowance.
- **Dependency:** the preceding `TokenBucket` class in the same language.
- **Implementation:** one bucket per authenticated tenant.
  - The tenant set is bounded and preloaded for this exercise.
  - Unknown tenants are rejected.
  - Python protects lookup for portability.
  - Java's map is immutable after construction.

**Flow**

→ Preload one token bucket for each allowed tenant.  
→ Look up the bucket for the authenticated tenant.  
→ Reject an unknown tenant.  
→ Delegate admission to that tenant bucket with the request cost.  
→ Return its decision without consuming another tenant allowance.

```python
from threading import Lock

class TenantLimiter:
    def __init__(self, tenants: list[str], capacity: int, rate: float):
        self.buckets = {t: TokenBucket(capacity, rate) for t in tenants}
        self.lock = Lock()

    def acquire(self, tenant: str, cost: int = 1) -> bool:
        with self.lock:
            bucket = self.buckets[tenant]
        return bucket.acquire(cost)
# Time: O(1) average per request, Space: O(tenants).
```

```java
import java.util.HashMap;
import java.util.Map;
import java.util.Set;

final class TenantLimiter {
    private final Map<String, TokenBucket> buckets;
    TenantLimiter(Set<String> tenants, long capacity, double rate) {
        Map<String, TokenBucket> values = new HashMap<>();
        for (String tenant : tenants)
            values.put(tenant, new TokenBucket(capacity, rate, System::nanoTime));
        buckets = Map.copyOf(values);
    }
    boolean acquire(String tenant, long cost) {
        TokenBucket bucket = buckets.get(tenant);
        if (bucket == null) throw new IllegalArgumentException("unknown tenant");
        return bucket.acquire(cost);
    }
}
```

- **L5 extra:** independent service instances multiply the effective quota.
  - Static quota division is approximate during topology changes.
  - A global bucket needs an atomic state owner.
  - Redis scripting is one common owner-side implementation choice.
  - Atomic script execution does not itself guarantee durable state after failover.
  - Idle-bucket eviction must not grant a fresh full burst too early.

<a id="s9"></a>
## 9. References

- [Companion concept source](2.dissys.md).
  - Section coverage and question order.
- [Python threading](https://docs.python.org/3/library/threading.html).
  - Locks and condition predicates.
- [Python concurrent futures](https://docs.python.org/3/library/concurrent.futures.html).
  - Future cancellation and executor lifecycle.
- [Java concurrency package](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/concurrent/package-summary.html).
  - Publication and concurrency primitives.
- [Java StampedLock](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/concurrent/locks/StampedLock.html).
  - Optimistic-read validation.
- [Java ThreadPoolExecutor](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/concurrent/ThreadPoolExecutor.html).
  - Queue and rejection behavior.
- [Java virtual threads](https://docs.oracle.com/en/java/javase/21/core/virtual-threads.html).
  - Blocking I/O and resource limits.
- [PostgreSQL INSERT](https://www.postgresql.org/docs/current/sql-insert.html).
  - Conflict-handling semantics.
- [PostgreSQL transaction isolation](https://www.postgresql.org/docs/current/transaction-iso.html).
  - Read-committed statement snapshots.
- [RFC 9562](https://www.rfc-editor.org/rfc/rfc9562).
  - UUID layouts.
- [Dynamo paper](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf).
  - Partitioning and leaderless replication context.
