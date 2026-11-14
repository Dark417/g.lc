# 03db.04mongodb.11read-write-concern Write Concern, Read Concern, Read Preference

> Three orthogonal per-operation knobs: when a write is acked, what a read may see, and who serves it.

## Index

- [1. Three Knobs](#1-three-knobs)
- [2. Write Concern](#2-write-concern)
- [3. wtimeout Ambiguity](#3-wtimeout-ambiguity)
  - [3.1 Idempotent Ledger Write In Code](#31-idempotent-ledger-write-in-code)
- [4. Read Concern](#4-read-concern)
- [5. Read Preference](#5-read-preference)
- [6. Causal Sessions](#6-causal-sessions)
- [7. Profiles Per Data Flow](#7-profiles-per-data-flow)
- [8. Outbox Phantom Event](#8-outbox-phantom-event)
- [9. Best Practices And Failure Modes](#9-best-practices-and-failure-modes)
- [Related](#related)

## 1. Three Knobs

One deployment serves "never lose this" and "stale is fine" by tuning each operation.

- **Write concern** (`w`, `j`, `wtimeout`): when is the write acknowledged?
- **Read concern** (`local`, `available`, `majority`, `linearizable`, `snapshot`): what may a read see?
- **Read preference** (`primary`, `primaryPreferred`, `secondary`, `secondaryPreferred`, `nearest`): which member serves it?
- Replaced: a single fixed consistency level
  - Audit write and click write differ in durability need by orders of magnitude
- ⚠️ Not a Consistency, Availability, Partition tolerance (CAP)/American National Standards Institute (ANSI) consistency level
  - Wrong combinations are weaker than either knob implies
- ⚠️ `w: "majority"` gives durability, not serializability
  - Lost updates still need a version field ([04crud-update-operators](04mongodb.04crud-update-operators.md))

```text
WRITE CONCERN        READ CONCERN          READ PREFERENCE
"when acked?"        "what may I see?"     "who serves me?"
w:0  fire+forget     local     this node   primary
w:1  primary mem     available sharded,    primaryPreferred
w:"majority"                   orphans ok  secondary
  (default 5.0)      majority  committed   secondaryPreferred
j:true journal       linearizable          nearest
wtimeout: ms           real-time, 1 doc    + maxStalenessSeconds
                     snapshot  txn view    + tag sets
```

Notice: `w:"majority"` + `readConcern:"local"` on a secondary is normal and stale.

## 2. Write Concern

`w` says how many members must have the write before the client hears "done".

- `w: 0`: fire and forget; no error path at all ⇒ never use it
- `w: 1`: primary memory; may not be on the primary's disk, surely not on a secondary
  - Rolled back on failover ([10replica-sets-oplog](04mongodb.10replica-sets-oplog.md#4-rollback))
- `w: "majority"` (default since **5.0**)
  - A majority of data-bearing voters applied it to their oplog
  - Rollback rewinds only to the majority point ⇒ such a write is never rolled back
  - ⚠️ Not synchronous to all: a member outside the majority can lag arbitrarily
- `j: true`: wait for the primary's journal fsync (else ~100 milliseconds (ms) group commit)
  - With majority on 3+ data nodes it guards only simultaneous majority crash
  - Roughly doubles write latency ⇒ leave `j` unset unless a regulation demands it

| Option | Buys | Costs | Choose when |
|---|---|---|---|
| `w:1` | Lowest latency | Acked data can vanish | Metrics, logs, caches |
| `w:"majority"` | Rollback-safe | One replication Round-Trip Time (RTT) | Default; everything transactional |
| `majority` + `j:true` | Survives majority crash | ~2× latency | A regulation you can point to |

## 3. wtimeout Ambiguity

`wtimeout` bounds the wait, and creates an answer that is neither success nor failure.

- On expiry: `WriteConcernError`
  - The write was likely applied on the primary
  - It may still replicate afterwards
- Not a rollback, not a cancel
  ⇒ blind retry of a non-idempotent write double-applies
- Design answer: make writes idempotent, not acks reliable
  - Upsert keyed by a client-generated id instead of `insertOne`
  - `retryWrites=true`: driver retries once with the session txnNumber
    - Server records the outcome in `config.transactions` ⇒ retry returns the original result
    - Covers one automatic retry of specific errors; your own retry loop needs its own key
- ⚠️ A rising `wtimeout` rate is a symptom
  - Majority unreachable, or lag beyond the timeout
  - Shed load, check `replSetGetStatus`; raising the timeout turns fast failure into queue depth
- `writeError` (the write failed, e.g. `DuplicateKey`) ≠ `writeConcernError` (applied, concern unmet)
  - Conflating them is the bug

### 3.1 Idempotent Ledger Write In Code

The payment id is the `_id`; `$setOnInsert` upsert converges on retry; a write-concern error means re-check.

**Java**

```java
// infra/_03db_04mongodb/MongoShowcase.java
public enum LedgerWrite { APPLIED, ALREADY_APPLIED, UNKNOWN_RECHECK }

public LedgerWrite recordLedgerEntry(String paymentId, long amountCents) {
    MongoCollection<Document> ledger = ConsistencyProfiles.ledger(db, OrderDocuments.LEDGER);
    try {
        UpdateResult r = ledger.updateOne(eq("_id", paymentId),
                Updates.combine(Updates.setOnInsert("amountCents", amountCents),
                        Updates.setOnInsert("at", OrderDocuments.nowMillis())),
                new UpdateOptions().upsert(true));
        return r.getUpsertedId() != null ? LedgerWrite.APPLIED : LedgerWrite.ALREADY_APPLIED;
    } catch (MongoWriteConcernException e) {
        return LedgerWrite.UNKNOWN_RECHECK; // applied locally? maybe. Re-read, never blind-retry
    }
}
```

**Python**

```python
# app/infra/_03db_04mongodb.py
def record_ledger_entry(self, payment_id: str, amount_cents: int) -> LedgerWrite:
    """Idempotent upsert keyed by payment id; a wtimeout is ambiguous, so re-check instead of retrying."""
    try:
        r = ledger_collection(self.db, LEDGER).update_one(
            {"_id": payment_id},
            {"$setOnInsert": {"amountCents": amount_cents, "at": now_millis()}},
            upsert=True,
        )
        return LedgerWrite.APPLIED if r.upserted_id is not None else LedgerWrite.ALREADY_APPLIED
    except WriteConcernError:
        return LedgerWrite.UNKNOWN_RECHECK
```

**Catch**

- Re-running the same call after `UNKNOWN_RECHECK` is safe here only because the write is an idempotent upsert
- `matched 1, modified 0` on a plain update = the retry already ran

## 4. Read Concern

Read concern is the visibility rule applied at read time.

- `local`: whatever this node has, possibly later rolled back; fine for most reads on the primary
- `available`: sharded; may return **orphan** documents ⇒ never use it
- `majority`: only majority-committed data, never a doomed write
  - Cost: the node keeps a majority snapshot, pinning WiredTiger's oldest timestamp
  - Long majority reads hold old versions in cache ⇒ `maxTimeMS` is mandatory
  - ⚠️ Not "latest": on a secondary it is majority-committed as that secondary knows it
  - `ReadConcernMajorityNotAvailableYet`: fresh node, retryable
- `linearizable`: reflects all writes completed before it began
  - Primary only, single-document only, not on sharded collections
  - Server does a no-op majority write to prove it is still primary ⇒ majority RTT per read
  - Can block indefinitely ⇒ pair with `maxTimeMS`; use approximately never
- `snapshot`: the transaction's point-in-time view ([12transactions](04mongodb.12transactions.md))

| Read concern | Buys | Costs | Choose when |
|---|---|---|---|
| `local` on primary | Fastest correct-ish read | May read a later-rolled-back value | Most reads |
| `majority` | Never reads a doomed write | Snapshot cost; still lags on secondaries | Reads that cause side effects |
| `linearizable` | Real-time order | Majority RTT; 1 doc; no sharding | Almost never |

## 5. Read Preference

Read preference picks the member; it says nothing about freshness unless you bound it.

- `secondaryPreferred` falls back to the primary when no secondary qualifies
  ⇒ under failure, analytics load lands on the primary exactly when it is weakest (fails open)
- `secondary` with a tag set fails **closed**: the report errors, Online Transaction Processing (OLTP) survives
- `maxStalenessSeconds` (minimum **90**) excludes lagging members
  - Without it the driver routes to an arbitrarily stale member
- Tag sets (`{nodeType: "analytics"}`) isolate analytics explicitly per client
- ⚠️ Secondaries are not idle: they replay every primary write and index update
  - Extra reads raise lag, which degrades the staleness bound (sublinear read scaling)
  - Cache-bound workloads gain nothing from replicas: same working set, same misses

## 6. Causal Sessions

A causally consistent session gives read-your-writes even on secondaries.

→ Session records the cluster time of its last operation  
→ Next read sends `afterClusterTime`  
→ Target secondary waits until it has replicated that far

- Cost: a stale read becomes a slow read
- ⚠️ Per session: two services acting for one user do not share it
  - Unless the cluster time is propagated explicitly (almost nobody does)

**Java**

```java
// infra/_03db_04mongodb/MongoShowcase.java
public Optional<Order> insertThenReadFromSecondary(NewOrder o) {
    try (ClientSession session = client.startSession(
            ClientSessionOptions.builder().causallyConsistent(true).build())) {
        Instant now = OrderDocuments.nowMillis();
        Document doc = OrderDocuments.newOrderDocument(new ObjectId(), o, now);
        orders.insertOne(session, doc); // majority write (userFacing profile)
        Document read = orders.withReadPreference(ReadPreference.secondaryPreferred())
                .find(session, eq("_id", doc.getObjectId("_id")))
                .maxTime(maxTimeMs, TimeUnit.MILLISECONDS)
                .first();
        return Optional.ofNullable(read).map(OrderDocuments::toOrder);
    }
}
```

**Python**

```python
# app/infra/_03db_04mongodb.py
def insert_then_read_from_secondary(self, o: NewOrder) -> Order | None:
    """Causal session: the secondary waits for afterClusterTime, so we read our own write (slowly)."""
    with get_client().start_session(causal_consistency=True) as s:
        doc = new_order_document(ObjectId(), o, now_millis())
        self.orders.insert_one(doc, session=s)
        d = self.orders.with_options(read_preference=ReadPreference.SECONDARY_PREFERRED).find_one(
            {"_id": doc["_id"]}, session=s, max_time_ms=self.max_time_ms
        )
        return to_order(d) if d else None
```

**Catch**

- Full guarantee needs majority write + majority read concern in the session
- For low-volume flows (profile edit), reading the primary is simpler than a causal session

## 7. Profiles Per Data Flow

Decide the three knobs once per flow and give the combination a name.

| Flow | `w` | `readConcern` | `readPreference` |
|---|---|---|---|
| Payment ledger | `majority` | `majority` on side-effect reads | `primary` |
| User profile / order | `majority` | `local` (or causal session) | `primary` |
| Internet of Things (IoT) telemetry | `1` | `local` | `secondaryPreferred` + 90 s staleness |
| Nightly Business Intelligence (BI) extract | n/a | `local` | `secondary` + `nodeType: analytics` tag |

- Ledger: a rolled-back entry is unrecoverable; no `j:true` (majority already covers a node crash)
- Profile: the requirement is read-your-writes, not durability
- Telemetry: the one place `w: 1` is correct, as a documented decision
- BI: fail closed; add `maxTimeMS` + `allowDiskUse`; the risk is evicting the OLTP working set
- ⚠️ Drift: someone copies telemetry `w: 1` into a ledger path ⇒ named constants in one class

**Java**

```java
// infra/_03db_04mongodb/ConsistencyProfiles.java
public static MongoCollection<Document> ledger(MongoDatabase db, String name) {
    return db.getCollection(name)
            .withWriteConcern(WriteConcern.MAJORITY.withWTimeout(5, TimeUnit.SECONDS))
            .withReadConcern(ReadConcern.MAJORITY)
            .withReadPreference(ReadPreference.primary());
}

public static MongoCollection<Document> telemetry(MongoDatabase db, String name) {
    return db.getCollection(name)
            .withWriteConcern(WriteConcern.W1)
            .withReadConcern(ReadConcern.LOCAL)
            .withReadPreference(ReadPreference.secondaryPreferred(MAX_STALENESS_S, TimeUnit.SECONDS));
}

// secondary (NOT secondaryPreferred) on a tagged member: fails CLOSED
public static MongoCollection<Document> analytics(MongoDatabase db, String name) {
    return db.getCollection(name)
            .withReadConcern(ReadConcern.LOCAL)
            .withReadPreference(ReadPreference.secondary(
                    new TagSet(new Tag("nodeType", "analytics")), MAX_STALENESS_S, TimeUnit.SECONDS));
}
// ... userFacing(db, name): MAJORITY write, LOCAL read, primary
```

**Python**

```python
# app/infra/_03db_04mongodb.py
def ledger_collection(db: Database, name: str) -> Collection:
    return db.get_collection(
        name,
        write_concern=WriteConcern("majority", wtimeout=5000),
        read_concern=ReadConcern("majority"),
        read_preference=ReadPreference.PRIMARY,
    )

def telemetry_collection(db: Database, name: str) -> Collection:
    return db.get_collection(
        name,
        write_concern=WriteConcern(w=1),
        read_concern=ReadConcern("local"),
        read_preference=SecondaryPreferred(max_staleness=MAX_STALENESS_S),
    )

def analytics_collection(db: Database, name: str) -> Collection:
    return db.get_collection(
        name,
        read_concern=ReadConcern("local"),
        read_preference=Secondary(tag_sets=[{"nodeType": "analytics"}], max_staleness=MAX_STALENESS_S),
    )
# ... user_facing_collection(db, name): majority write, local read, PRIMARY
```

**Catch**

- Uniform Resource Identifier (URI) options (`?w=majority&readPreference=...`) set client-wide defaults; per-collection overrides win
- Spring Data: `WriteConcernResolver` / `@ReadPreference` do the same, but scatter the decision
- DocumentDB: no tag sets, no `linearizable`; isolate analytics via a replica's instance endpoint

## 8. Outbox Phantom Event

Write-then-publish is broken twice; write concern alone fixes neither.

→ Service writes with `w: 1`, reads back `local`, publishes to the broker  
→ Failover rolls the write back  
⇒ Broker holds an event for an entity that never existed; no compensating action

→ Crash between write and publish  
⇒ Event lost

- Fix A: transactional outbox
  - Domain doc + outbox doc in one transaction
  - Poller reads with `readConcern: "majority"` ⇒ never sees a doomed write
- Fix B ✅: change streams, majority-committed by construction ([14change-streams](04mongodb.14change-streams.md))
- Either way delivery is at-least-once ⇒ idempotent consumers

## 9. Best Practices And Failure Modes

**Designer decisions**

- Three per-operation knobs, not one isolation level
  - Cost: huge room for wrong combinations, no single place to reason
- Causal consistency is opt-in per session
  - Cost: most apps don't have it and don't know
- `linearizable` limited to single-doc primary reads
  - Anything broader needs coordination on every read

**Rules → failure prevented**

- Never `w: 0` → silent, undetectable loss
- `readConcern: "majority"` on reads that trigger external effects → phantom events/payments
- Pair secondary reads with `maxStalenessSeconds` → hours-stale reads
- Never retry `wtimeout` without an idempotency key → double-apply
- Tag sets for analytics, not global `secondaryPreferred` → failover moves BI onto the primary
- Document `w` + read concern as a pair per flow → "we use majority so we're consistent"

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Silent write loss | `w:0`, or `w:1` + failover | Reconciliation only | `w: "majority"` |
| `wtimeout` double-apply | Retry on write concern error | Duplicates downstream | Idempotency keys; natural-key upsert |
| Stale read after write | Secondary read, no causal session | Update vanishes then reappears | Causal session or primary |
| Reads collapse to primary | `secondaryPreferred` during outage | Primary ops jump | Tag-set routing; headroom |
| Cache pressure from majority reads | Long-held majority snapshots | Oldest-timestamp lag | `maxTimeMS` |

- Canonical failure pattern (not a specific incident): the outbox that published a rolled-back write
  - Fix: majority write + majority outbox read; better, change streams
- Public: 5.0 release notes changed the default to `w: "majority"`
  - A vendor paying latency to change a default = evidence `w: 1` lost data in the field
- Background: "Tunable Consistency in MongoDB" (Very Large Data Bases (VLDB) 2019)

## Related

- [00index](04mongodb.00index.md)
- [10replica-sets-oplog](04mongodb.10replica-sets-oplog.md)
- [12transactions](04mongodb.12transactions.md)
- [14change-streams](04mongodb.14change-streams.md)
