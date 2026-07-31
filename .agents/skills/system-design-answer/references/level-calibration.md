# Level Calibration — L4 vs L5

## Level mapping

| Artifact tier | Google | Amazon | Meta |
|---|---|---|---|
| **L4** | L4 (SWE III) | SDE II | E4 |
| **L5** | L5 (Senior) | SDE III / Senior | E5 |

Treat these as depth tiers, not guarantees about a specific ladder.

## Six structural differences

L5 is not L4 with more words.

### 1. Requirements: accept vs negotiate

- **L4** clarifies requirements and designs to them.
- **L5** proposes a scope cut and names what the cut buys.

### 2. Non-functionals: list vs rank

- **L4** lists availability, latency, consistency, and durability.
- **L5** gives them a priority order and lets it govern later choices.

### 3. Numbers: computed vs load-bearing

- **L4** computes QPS and storage correctly.
- **L5** uses a number to kill or force an option in real time.

### 4. Choices: made vs defended against an alternative

- **L4** picks and justifies a reasonable technology.
- **L5** names the rejected alternative and the condition that would flip the decision.

### 5. Operations: mentioned vs owned

- **L4** discusses monitoring and retries when asked.
- **L5** volunteers blast radius, degraded mode, rollout, migration, and cost.

### 6. Self-critique: absent vs leading

- **L4** responds well to pushback.
- **L5** identifies the weakest assumption and what would invalidate it.

## Worked examples

### Concurrent update

**L4:** Use optimistic locking with a version column. Reject a stale write and let the client retry.

**L5:** Choose optimistic locking because conflicts are rare at the estimated write distribution. Cap retries with jitter and return `409` rather than livelocking on a hot row. If traffic concentrates on a hot record, switch that field to a CRDT counter or single-writer partition.

The L5 answer ties the mechanism to a number, volunteers the failure mode, and names a flip condition.

### Storage choice

**L4:** Use DynamoDB for low-latency key-value lookups at scale.

**L5:** Use `tenantId#bucketDate` as the partition key to spread a dominant tenant, accepting that cross-tenant ranges require a secondary index and may lag. If cross-tenant queries become user-facing, change the key or table design.

## What L5 is not

1. **Unrequested scale.** Do not introduce sharding or multi-region for 500 QPS.
2. **Component name-dropping.** Every service name needs the mechanism bought and cost paid.
3. **Filibustering.** Pause at phase boundaries and let the interviewer probe.

Every generated artifact must name the sentence most likely to trigger an over-engineering warning.

## Company emphasis

| | Amazon SDE II / III | Google L4 / L5 |
|---|---|---|
| Probes | Operational ownership, cost, blast radius | Abstraction quality, general reasoning, algorithmic clarity |
| Typical pushback | “It is 3am and paging; what do you do?” | “Now support a different access pattern.” |
| Rewards | Concrete production judgment and a shippable design | Clean decomposition and correctness under changed premises |
| Punishes | Hand-waving operations | Memorized architectures that do not generalize |
