# 03db.04mongodb.10replica-sets-oplog Replica Sets, Elections, And The Oplog

> One primary, secondaries tailing its oplog, majority elections: failover is a property, rollback is its price.

## Index

- [1. Topology](#1-topology)
  - [1.1 Components](#11-components)
  - [1.2 Member Count And Layout](#12-member-count-and-layout)
- [2. The Oplog](#2-the-oplog)
  - [2.1 Idempotent Entries](#21-idempotent-entries)
  - [2.2 Oplog Window](#22-oplog-window)
  - [2.3 Replication Flow](#23-replication-flow)
- [3. Elections And Failover](#3-elections-and-failover)
- [4. Rollback](#4-rollback)
- [5. Arbiters And Special Members](#5-arbiters-and-special-members)
- [6. Inspecting A Replica Set In Code](#6-inspecting-a-replica-set-in-code)
- [7. Local Dev: Single-Node Replica Set](#7-local-dev-single-node-replica-set)
- [8. Decisions And Best Practices](#8-decisions-and-best-practices)
- [9. Failure Modes](#9-failure-modes)
- [Related](#related)

## 1. Topology

A replica set is several `mongod` processes holding the same data, with exactly one writer.

- Plain idea: one leader takes writes; followers copy its change log
- Limits: max **50** members, max **7** voting (MongoDB 8.0 docs)
- Solves
  - Automatic failover: no human in the loop for a node loss
  - Durability beyond one machine
  - Read scale-out for stale-tolerant traffic
- Replaced master/slave replication
  - No automatic election; promotion was a manual procedure
- Every shard is a replica set; so is the config server set (CSRS)
- ⚠️ Replication is asynchronous
  - `w: "majority"` makes the acknowledgement wait, not the replication synchronous
- Wrong answer to: multi-region active-active writes
  - One primary ⇒ cross-region Round-Trip Time (RTT) on every majority write

```text
        client (driver monitors every member)
              | writes
              v
      +----------------------------+
      | PRIMARY                    |
      | apply write -> WT          |
      | append local.oplog.rs      |
      +------+--------------+------+
     pull    |              |   pull     heartbeats every 2 s
             v              v            (all-to-all)
      +------------+  +------------+
      | SECONDARY  |  | SECONDARY  |  may sync from another
      | apply +    |  | apply +    |  secondary (chaining)
      | own oplog  |  | own oplog  |
      +------------+  +------------+
```

Notice that secondaries pull; the primary never pushes.

### 1.1 Components

| Component | Single responsibility |
|---|---|
| Primary | Sole write acceptor; sole oplog producer |
| Oplog (`local.oplog.rs`) | Ordered, idempotent, capped record of writes |
| Secondary | Pull, apply, re-publish oplog; stale-tolerant reads |
| Heartbeat | Liveness + topology, every 2 s |
| Election (Protocol Version 1, PV1) + term | Pick a primary by majority; fence stale primaries |
| Arbiter | Vote without holding data |

### 1.2 Member Count And Layout

- Failure tolerance = `floor((N-1)/2)`
  - 3 members tolerate 1; 4 members also tolerate 1 (majority is 3)
  - ⇒ Always odd counts
- 3 members: default
- 5 members: survive a node loss during a maintenance window
- Region-loss survival with Recovery Point Objective (RPO) 0 = 5 voters across 3 regions, **2 / 2 / 1**
  - Any region lost ⇒ 3 of 5 remain ⇒ election succeeds
  - 3 / 2 fails: losing the 3-member region leaves 2 of 5 ⇒ read-only
  - Cost: every majority write pays the inter-region RTT (order of magnitude tens of milliseconds (ms) in-continent)
  - Cost: cross-region transfer on all replication traffic
- Never `w: 5` (all members): one slow member stops all writes

| Layout | Buys | Costs | Choose when |
|---|---|---|---|
| 3 members, 1 region | Simple, cheap, fast majority | Region loss = total loss | Single-region Service Level Agreement (SLA) |
| 5 members, 3 regions | Survives a region | Cross-region RTT per write | Regional Disaster Recovery (DR) is hard requirement |
| 3 + `priority: 0` DR member | DR copy, no election impact | No automatic DR promotion | DR is an RPO/Recovery Time Objective (RTO) promise, not High Availability (HA) |
| Arbiter | Cheap majority | Majority writes stall on data-node loss | Never, if you are on call |

## 2. The Oplog

The oplog is a capped WiredTiger collection holding every applied write, in order.

- Default size: **5% of free disk, min 990 megabytes (MB), max 50 gigabytes (GB)** (MongoDB 8.0 docs)
- Full ⇒ oldest entries overwritten
- Readers: secondaries, change streams, Kafka connector, Atlas triggers
- Oplog write and data write are one WiredTiger transaction
  - ⇒ "it happened" and "it is replicable" are atomic

### 2.1 Idempotent Entries

The server rewrites non-deterministic operations into their result before logging them.

- `{$inc: {n: 1}}` → logged as `{$set: {n: <resulting value>}}`
- `$push` with `$slice` → logged as the resulting array
- Why: a secondary may re-apply an entry during recovery
  - Idempotence makes that safe with no per-follower state on the primary
- ⚠️ Idempotence is per entry
  - Transactions use `applyOps` entries and their own commit protocol
- ⚠️ Size: tiny updates on large documents log large entries
  - Oplog bytes/s can be ~10× the app's write payload (order of magnitude)
  - Measure oplog bytes/s; do not derive it from app volume

### 2.2 Oplog Window

The window is the wall-clock time the current oplog covers: the key operational number.

- A secondary further behind than the window → `RECOVERING`
  ⇒ full initial sync, hours on a multi-terabyte (TB) node
- Size it: `peak_write_bytes/s × required_recovery_window`
  - Window must cover the longest maintenance op: index build, restore, partition
  - 5% of disk is a default, not a design
- Resize online: `replSetResizeOplog` (since 3.6)
- Alert on window **seconds**, not size in GB
  - Lag threshold = fraction of the window
  - 45 min lag is fine at a 6 h window, an emergency at 1 h
- ⚠️ Initial sync must finish inside the window plus oplog accrued during the sync
  - Undersized oplog ⇒ initial sync fails repeatedly (spiral)
  - Escape: dedicated sync source, file-copy initial sync (Enterprise/Atlas), snapshot restore + catch-up
  - Multi-TB nodes: plan snapshot restore as the primary recovery path

### 2.3 Replication Flow

- Secondaries **pull** (tail) the oplog
  - Deliberate deviation from Raft, where the leader pushes
- **Chaining** is on by default
  - A secondary syncs from a closer secondary
  - Saves primary egress in multi-region; costs one extra hop of lag
- Apply is batched and parallel, partitioned by document `_id`
  - Same-document order preserved
  - ⚠️ Mid-batch, a secondary can show a state the primary never had
    - `readConcern: "local"` on a secondary can see it
    - `readConcern: "majority"` reads a stable snapshot instead

## 3. Elections And Failover

Protocol version 1 is Raft-like: terms, majority votes, one vote per member per term.

- Trigger: no primary heartbeat for `electionTimeoutMillis` (default **10 000 ms**)
- Candidate increments the term → requests votes → needs a strict majority of configured voters
- Higher term wins; old primary steps down on seeing it
- `members[n].priority` biases who runs; `priority: 0` = never primary
- Observed failover ~10–15 s with defaults (order of magnitude, dominated by the timeout)
- Driver impact
  - Writes: `retryWrites=true` retries once on the new primary ⇒ near-zero impact
  - Reads without retry logic: hard error
- Differences from Raft
  - Followers pull; no log-matching property
  - ⇒ MongoDB needs rollback; Raft repairs divergence by truncation
- ⚠️ Lower `electionTimeoutMillis` = faster failover, more spurious elections on a jittery network
  - Do not tune below default without evidence
- Test it: `rs.stepDown()` on a schedule, in a prod-like env
  - Prevents finding untested driver retry config during an incident

## 4. Rollback

Writes the old primary accepted but never replicated to a majority are discarded when it rejoins.

→ Primary accepts writes  
→ Partitioned before a majority replicates them  
→ New primary elected; old one rejoins  
⇒ Its extra writes are rolled back

- Since **4.0**: `recoverToStableTimestamp`
  - WiredTiger rewinds storage to the last majority-committed timestamp
- Before 4.0: replayed rollback files, capped at **300 MB**
  - Beyond that ⇒ full resync, hours of reduced redundancy (MongoDB 4.0 release notes)
- ⚠️ "MongoDB never loses acknowledged writes" holds only for `w: "majority"`
  - `w: 1` acknowledged writes **can** be rolled back
  - That is why the default became `majority` in **5.0**
- The client cannot tell "rolled back" from "never happened"
  - ⇒ correctness needs idempotency keys ([11read-write-concern](04mongodb.11read-write-concern.md))

## 5. Arbiters And Special Members

An arbiter votes but holds no data; it is cheap and almost always a mistake.

→ Set `{P, S, A}` loses S  
⇒ P + A still a majority: primary stays writable  
⇒ No second data-bearing member: `w: "majority"` blocks until `wtimeout`  
⇒ Zero redundancy, still accepting writes, `readConcern: "majority"` meaningless  
→ Use a data-bearing `priority: 0` member instead

- The only defensible case: non-critical workload, explicit `w: 1`, rollback risk accepted in writing
- Cloud price gap between arbiter and small secondary is small
- Analytics member: `priority: 0`, `votes: 0`, own tag, sized differently
  - Can never win an election; Business Intelligence (BI) load has separate resources
- DR member: `priority: 0` in the DR region; manual promotion

## 6. Inspecting A Replica Set In Code

`replSetGetStatus` gives member states and optimes; the oplog's first and last `ts` give the window.

- Lag = primary optime − member optime
- `syncSourceHost` reveals chaining (lag compounds through a lagging source)

**Java**

```java
// infra/_03db_04mongodb/MongoAdmin.java
public Document replicaSetSummary() {
    Document status = client.getDatabase("admin").runCommand(new Document("replSetGetStatus", 1));
    List<Document> members = new ArrayList<>();
    Date primaryOptime = null;
    for (Document m : status.getList("members", Document.class)) {
        if ("PRIMARY".equals(m.getString("stateStr"))) {
            primaryOptime = m.getDate("optimeDate");
        }
    }
    for (Document m : status.getList("members", Document.class)) {
        Date optime = m.getDate("optimeDate");
        long lagS = primaryOptime == null || optime == null ? -1
                : (primaryOptime.getTime() - optime.getTime()) / 1000;
        members.add(new Document("name", m.getString("name"))
                .append("state", m.getString("stateStr"))
                .append("lagSeconds", lagS)
                .append("syncSource", m.getString("syncSourceHost")));
    }
    return new Document("set", status.getString("set"))
            .append("term", status.get("term"))
            .append("members", members)
            .append("oplogWindowSeconds", oplogWindowSeconds());
}

// Window = newest oplog ts - oldest oplog ts. Alert in SECONDS, not GB.
public long oplogWindowSeconds() {
    var oplog = client.getDatabase("local").getCollection("oplog.rs");
    Document first = oplog.find().sort(Sorts.ascending("$natural")).limit(1)
            .projection(Projections.include("ts")).first();
    Document last = oplog.find().sort(Sorts.descending("$natural")).limit(1)
            .projection(Projections.include("ts")).first();
    if (first == null || last == null) {
        return -1;
    }
    BsonTimestamp a = first.get("ts", BsonTimestamp.class);
    BsonTimestamp b = last.get("ts", BsonTimestamp.class);
    return (long) b.getTime() - a.getTime();
}
```

**Python**

```python
# app/infra/_03db_04mongodb.py
def replica_set_summary(self) -> Doc:
    """Member states, lag, and the oplog window in seconds."""
    status = get_client().admin.command("replSetGetStatus")
    primary = next((m["optimeDate"] for m in status["members"] if m["stateStr"] == "PRIMARY"), None)
    members = [
        {
            "name": m["name"],
            "state": m["stateStr"],
            "lagSeconds": int((primary - m["optimeDate"]).total_seconds()) if primary and "optimeDate" in m else -1,
            "syncSource": m.get("syncSourceHost"),
        }
        for m in status["members"]
    ]
    return {"set": status["set"], "term": status.get("term"), "members": members,
            "oplogWindowSeconds": self.oplog_window_seconds()}

def oplog_window_seconds(self) -> int:
    oplog = get_client().local["oplog.rs"]
    first = oplog.find_one({}, {"ts": 1}, sort=[("$natural", ASCENDING)])
    last = oplog.find_one({}, {"ts": 1}, sort=[("$natural", DESCENDING)])
    if not first or not last:
        return -1
    return last["ts"].time - first["ts"].time
```

**Catch**

- Needs `clusterMonitor`-level privileges; app users usually lack them
- Term incrementing rapidly = election storm (flapping network)
- DocumentDB returns a reduced `replSetGetStatus` and exposes no `local.oplog.rs`
  - Use CloudWatch replica lag there

## 7. Local Dev: Single-Node Replica Set

Transactions, change streams, retryable writes, and causal sessions all need a replica set.

- A one-member set `rs0` unlocks them at near-zero cost; it cannot fail over
- Standalone `mongod` = development-only topology, and even then limited
- [`1x/local/mongodb`](../../local/mongodb/docker-compose.yml) runs `mongod --replSet rs0` + a one-shot init

```javascript
// local/mongodb/init-replica.js (illustrative excerpt)
// host = localhost:27017 so apps on the HOST can follow replica-set discovery to it.
rs.initiate({ _id: "rs0", members: [{ _id: 0, host: "localhost:27017" }] });
// real sets add members; priority 0 = never primary (DR / analytics member)
```

- Connect: `mongodb://localhost:27017/?replicaSet=rs0`
- ⚠️ From another container, use `directConnection=true`: the advertised `localhost` resolves wrong there

## 8. Decisions And Best Practices

**Designer decisions**

| Decision | Rejected | Why / cost |
|---|---|---|
| Single primary | Multi-master + conflict resolution | Atomic single-doc writes without Conflict-free Replicated Data Type (CRDT)/Last-Writer-Wins (LWW); writes don't scale with replicas |
| Pull-based tailing | Leader push (Raft) | Chaining, own pace; no log matching ⇒ rollback |
| Idempotent entries | Logical op log | Safe re-apply; `$inc` → `$set` grows the oplog |
| Capped oplog | Unbounded log | Bounded disk; lagging member may fall off |
| `w: "majority"` default (5.0) | `w: 1` | Rollback-safe acks; one replication RTT per write |

**Rules → failure prevented**

- Alert on oplog window seconds
  - Prevents a growing write rate shrinking 48 h to 40 min unnoticed
- Keep `w: "majority"` + `retryWrites`
  - Prevents rolled-back acks and elections surfacing as write errors
- Odd member counts
  - Prevents paying for a node that adds no tolerance
- `priority: 0` data member over an arbiter
  - Prevents the majority-write stall
- `maxStalenessSeconds` on any secondary read preference
  - Prevents routing to a member hours behind
- Match secondary instance types to the primary
  - Prevents apply-bound lag at peak

**Lag triage, in order** (45 min lag, 6 h window, climbing)

→ Compute time-to-window-exhaustion at the current rate: mitigate or investigate?  
→ Apply-bound? smaller secondary instance ⇒ match types  
→ Index maintenance? lag correlates with a new index  
→ Long `majority` read on the secondary pinning the oldest timestamp ⇒ `currentOp`, kill it  
→ Chaining from a lagging source ⇒ `syncSourceHost`

- Mitigations by reversibility: pause batch writers → kill long reads → disable chaining → `replSetResizeOplog`
- ⚠️ Do not remove the secondary "to let it catch up": you lose a voter mid-incident

## 9. Failure Modes

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Fell off oplog window | Long index build, partition, slow disk | Member `RECOVERING`; window seconds dropping | Size oplog for longest op; throttle bulk writes |
| Rollback of `w:1` writes | Primary partitioned pre-replication | Rollback log on old primary | `w: "majority"` |
| Majority-write stall | Data-bearing majority lost | Write latency → `wtimeout`; `replSetGetStatus` | Odd counts; no arbiters |
| Election storm | Flapping network, low timeout | Term rising fast | Fix network; keep default timeout |
| Stale secondary reads | `secondaryPreferred` w/o staleness bound | "My update vanished" tickets | `maxStalenessSeconds`; causal session; primary |
| Lag from index maintenance | Too many indexes, bulk burst | Optime gap | Fewer indexes; throttle jobs |

- Exception handling
  - `NotWritablePrimary` (10107), `PrimarySteppedDown` (189): retryable; `retryWrites` retries once
    - The session's txnNumber makes that retry idempotent even if the first attempt applied
  - `WriteConcernFailed` / `wtimeout`: ambiguous, not a failure ([11read-write-concern](04mongodb.11read-write-concern.md#3-wtimeout-ambiguity))
- Canonical failure pattern (not a specific incident): the index build that cost a resync
  - 6 h build on 3 TB; oplog window was 4 h (sized at 5% of disk years ago)
  ⇒ one secondary `RECOVERING`, 9 h initial sync with zero failure tolerance
  - Fix: resize to 3× the longest expected op; alert on window seconds
- Public: 4.0 release notes (300 MB rollback limit → `recoverToStableTimestamp`)
- Public: 5.0 release notes (default `w: "majority"`, latency accepted to stop rollback loss)

## Related

- [00index](04mongodb.00index.md)
- [11read-write-concern](04mongodb.11read-write-concern.md)
- [13sharding](04mongodb.13sharding.md)
- [14change-streams](04mongodb.14change-streams.md)
