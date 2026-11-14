# build.md — System Design Content Contract

**This file is the generation and quality contract for `1sd/`.** It contains the repository shape, primitive registry, question manifest, generation contract, and build order. Use [`00.sd plan.md`](./00.sd%20plan.md) for the learning schedule and [`0flow.md`](./0flow.md) for live interview execution.

> **Agent: read Part 7 (Build Order) before generating anything.** Generating everything at once is wrong and expensive. Build order is load-bearing.

---

## Part 1 — Mission & Constraints

**Target:** Amazon SDE II, Google L4. L5 captured as forward reference only, never as a current training target.

**Owner profile:** ~4 yrs backend. Java 17 / Spring Boot / AWS (ECS, Lambda, SQS/SNS, Glue, Aurora, DynamoDB, OpenSearch) / Terraform. Strong on event-driven AWS and observability. Rusty on DB/OS/distributed-systems internals. Kafka is conceptual only — **never generate content that implies operational Kafka experience.**

**Success metric — not question count:**

1. Cold-open decomposition of an unseen question in <5 min, ≥80% primitive hit rate.
2. ≥3 on all seven rubric dimensions across three consecutive recorded 45-min runs.

**Hard constraints on generation:**

| Constraint | Rule                                                                                                                                          |
| ---------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| Volume     | Skeletons for everything. Full 45-min artifacts **only** for P0, and only on explicit request.                                                |
| Ordering   | Never generate a full artifact for a question the owner hasn't attempted cold. Check `attempted:` front-matter; if empty, refuse and say why. |
| Level      | Generate to L4 bar by default. L5 sections are marked and separable. Over-engineering is a _failure mode_ at L4.                              |
| Honesty    | No invented production incidents. No implied experience with tech not in the owner profile.                                                   |
| Time       | This repo competes with coding prep, which is primary. Optimize for fewest files that cover the most primitives.                              |

---

## Part 2 — Repo Structure

```
1sd/
├── AGENTS.md                     ← directory-scoped generation/coaching rules
├── 00.sd plan.md                 ← learning plan and 2–3 week schedules
├── 0flow.md                      ← 45-minute execution and answer defense
├── build.md                      ← this contract
├── 1index.md                     ← authoritative question/concept index
├── 1bp.md                        ← broader interview-priority context from remote main
├── 00.base/                      ← transferable concepts and primitives
│   └── 00.sde.md                 ← concept learning map
├── 1AX/                          ← canonical Alex Xu chapters
├── 01.core/                      ← non-AX core questions
├── 02.social-media/ … 10.*/      ← non-duplicate questions by domain
├── full/                         ← optional post-attempt 45-minute references
├── runs/                         ← timed-run records
├── SCORECARD.md
└── FAILURE-LOG.md
```

**Naming rules** (an agent will glob these — inconsistency breaks the indexes):

- Keep the established `NN.<domain>` category names. Do not create parallel aliases for folders with spaces.
- Question files: `NNNN.kebab-case.md` where `NNNN` = folder number + two-digit index.
- Alex Xu files: `AX<volume>-<chapter>.<canonical-slug>.md` using the published chapter name.
- `1index.md` owns all question links. Update it in the same change as any add, move, rename, or deletion.

---

## Part 3 — Primitive Registry

The transferable layer. ~26 techniques cover the entire question set. **P0 primitives are the 14 marked `tier: P0`** — those are the MVP0 build.

```yaml
primitives:
  - id: fan-out
    name: Fan-out on write vs. read
    tier: P0
    covers: [celebrity problem, hybrid split rule, timeline materialization]

  - id: hot-key
    name: Hot key / hot partition
    tier: P0
    covers:
      [
        key salting,
        compound partition keys,
        local aggregation,
        request coalescing,
      ]

  - id: idempotency
    name: Idempotency & exactly-once processing
    tier: P0
    covers:
      [idempotency keys, dedupe stores + TTL, at-least-once + effectively-once]

  - id: saga
    name: Saga / distributed transaction
    tier: P0
    covers:
      [choreography vs orchestration, compensating actions, outbox pattern]

  - id: geospatial-index
    name: Geospatial indexing & matching
    tier: P0
    covers: [geohash, S2/H3, quadtree, proximity search, moving-object updates]

  - id: consistent-hashing
    name: Consistent hashing & partitioning
    tier: P0
    covers: [virtual nodes, rebalancing cost, range vs hash partitioning]

  - id: top-k
    name: Top-K / leaderboard / heavy hitters
    tier: P0
    covers:
      [
        sorted sets,
        count-min sketch,
        approximate vs exact,
        time-windowed ranking,
      ]

  - id: quorum-replication
    name: Replication & quorum
    tier: P0
    covers:
      [leader/follower, R+W>N, read-your-writes, replication lag, failover]

  - id: delivery-semantics
    name: Delivery semantics & message ordering
    tier: P0
    covers: [at-most/at-least/exactly-once, ordering scope, DLQ, poison pill]

  - id: cache-invalidation
    name: Caching & invalidation
    tier: P0
    covers:
      [
        read/write-through,
        TTL vs explicit,
        stampede,
        negative caching,
        coherence,
      ]

  - id: backpressure
    name: Backpressure, retries & overload
    tier: P0
    covers:
      [retry budgets, jitter, circuit breaker, load shedding, cascading failure]

  - id: rate-limiting-algorithms
    name: Rate limiting algorithms
    tier: P0
    covers:
      [
        token/leaky bucket,
        sliding window,
        distributed counter sync,
        local vs central,
      ]

  - id: sharding-strategies
    name: Sharding & resharding
    tier: P0
    covers:
      [shard key choice, cross-shard queries, online resharding, hot shard]

  - id: inverted-index
    name: Inverted index & retrieval
    tier: P0
    covers:
      [tokenization, posting lists, scoring, index refresh, typeahead tries]

  - id: presence-heartbeat
    name: Presence, heartbeat & connection state
    tier: P1
    covers:
      [
        long-lived connections,
        session affinity,
        TTL heartbeats,
        thundering herd on reconnect,
      ]

  - id: cdc
    name: Change data capture & the outbox
    tier: P1
    covers: [log tailing, dual-write hazard, ordering guarantees, replay]

  - id: dedup
    name: Deduplication at scale
    tier: P1
    covers: [bloom filters, windowed dedupe, content hashing]

  - id: conflict-resolution
    name: Concurrent edit conflict resolution
    tier: P1
    covers:
      [OT vs CRDT, last-writer-wins hazards, vector clocks, causal ordering]

  - id: stream-windowing
    name: Stream processing & windowing
    tier: P1
    covers:
      [tumbling/sliding/session windows, watermarks, late data, lambda vs kappa]

  - id: chunked-transfer
    name: Chunked upload, resume & CDN delivery
    tier: P1
    covers:
      [multipart, presigned URLs, adaptive bitrate, edge caching, origin shield]

  - id: scheduling-queue
    name: Delayed & scheduled execution
    tier: P1
    covers:
      [
        timing wheel,
        priority queue,
        visibility timeout,
        at-least-once fire,
        clock skew,
      ]

  - id: leader-election
    name: Leader election & coordination
    tier: P1
    covers:
      [
        leases,
        fencing tokens,
        why distributed locks fail,
        single-writer partitions,
      ]

  - id: ledger-integrity
    name: Ledger & financial integrity
    tier: P1
    covers:
      [
        double-entry,
        immutability,
        reconciliation,
        balance derivation vs snapshot,
      ]

  - id: multi-tenant-isolation
    name: Multi-tenant isolation
    tier: P2
    covers: [noisy neighbor, per-tenant quotas, data partitioning, blast radius]

  - id: vector-retrieval
    name: Vector retrieval & semantic search
    tier: P2
    covers:
      [
        ANN indexes (HNSW/IVF),
        recall/latency tradeoff,
        hybrid retrieval,
        freshness,
      ]

  - id: write-ahead-log
    name: Write-ahead log & durability
    tier: P2
    covers: [WAL, fsync semantics, LSM vs B-tree, compaction, crash recovery]
```

---

## Part 4 — Question Manifest

Tiers: **P0** = build and drill, no exceptions (14). **P1** = generate skeleton, drill if a loop is scheduled in that domain (~30). **P2** = skeleton only, recombinations of primitives already covered (~40).

`asked_at` is a rough frequency signal, not a guarantee — treat as a prior, not a fact.

```yaml
# ─────────────────────────── 01.core ───────────────────────────
- id: "0101"; slug: rate-limiter;              tier: P0; primitives: [rate-limiting-algorithms, hot-key, cache-invalidation]; asked_at: [amazon, google, meta]
- id: "0102"; slug: tinyurl;                   tier: P1; primitives: [sharding-strategies, cache-invalidation, consistent-hashing]; note: "warm-up only; nearly free once 0104+0103 are done"
- id: "0103"; slug: distributed-cache;         tier: P0; primitives: [cache-invalidation, consistent-hashing, hot-key]; asked_at: [amazon, google]
- id: "0104"; slug: global-unique-id-generator;tier: P0; primitives: [leader-election, sharding-strategies]; note: "snowflake, clock skew, coordination avoidance"
- id: "0105"; slug: api-gateway;               tier: P1; primitives: [rate-limiting-algorithms, backpressure, multi-tenant-isolation]
- id: "0106"; slug: feature-flag-service;      tier: P2; primitives: [cache-invalidation, cdc]
- id: "0107"; slug: leaderboard-service;       tier: P0; primitives: [top-k, hot-key, sharding-strategies]; asked_at: [amazon, meta]
- id: "0108"; slug: distributed-lock-service;  tier: P0; primitives: [leader-election, quorum-replication]; note: "fencing tokens; why locks fail"
- id: "0109"; slug: key-value-store;           tier: P1; primitives: [consistent-hashing, quorum-replication, write-ahead-log]; asked_at: [google]
- id: "0110"; slug: web-crawler;               tier: P1; primitives: [dedup, backpressure, scheduling-queue]; asked_at: [google, amazon]
- id: "0111"; slug: distributed-job-scheduler; tier: P1; primitives: [scheduling-queue, leader-election, delivery-semantics]; asked_at: [amazon]

# ─────────────────────── 02.social-media ───────────────────────
- id: "0201"; slug: news-feed;                 tier: P0; primitives: [fan-out, hot-key, cache-invalidation, top-k]; asked_at: [meta, amazon, google]; note: "highest-frequency question in the industry"
- id: "0202"; slug: chat-messaging;            tier: P0; primitives: [delivery-semantics, presence-heartbeat, sharding-strategies]; asked_at: [meta, amazon, google]
- id: "0203"; slug: follow-unfollow-timeline-fanout; tier: P1; primitives: [fan-out, hot-key]; note: "merge into 0201 unless a Meta loop is scheduled"
- id: "0204"; slug: social-graph-service;      tier: P1; primitives: [sharding-strategies, hot-key, cache-invalidation]; asked_at: [meta]
- id: "0205"; slug: group-chat;                tier: P1; primitives: [fan-out, delivery-semantics, presence-heartbeat]
- id: "0206"; slug: push-notification-service; tier: P0; primitives: [fan-out, backpressure, delivery-semantics, dedup]; asked_at: [amazon, meta]
- id: "0207"; slug: presence-service;          tier: P1; primitives: [presence-heartbeat, hot-key]; asked_at: [meta]
- id: "0208"; slug: stories-reels-ranking-pipeline; tier: P2; primitives: [fan-out, top-k, stream-windowing]
- id: "0209"; slug: comment-and-reply-system;  tier: P2; primitives: [sharding-strategies, cache-invalidation, top-k]
- id: "0210"; slug: content-moderation-pipeline; tier: P2; primitives: [stream-windowing, backpressure, dedup]

# ───────────────────── 03.commerce-marketplace ─────────────────
- id: "0301"; slug: order-management;          tier: P1; primitives: [saga, idempotency, cdc]; asked_at: [amazon]
- id: "0302"; slug: inventory-management;      tier: P0; primitives: [hot-key, idempotency, quorum-replication]; asked_at: [amazon]; note: "oversell + reservation under contention"
- id: "0303"; slug: checkout-payment-orchestration; tier: P0; primitives: [saga, idempotency, delivery-semantics]; asked_at: [amazon, google]
- id: "0304"; slug: product-catalog;           tier: P1; primitives: [inverted-index, cache-invalidation, cdc]; asked_at: [amazon]
- id: "0305"; slug: shopping-cart;             tier: P2; primitives: [conflict-resolution, cache-invalidation]
- id: "0306"; slug: ride-matching-platform;    tier: P0; primitives: [geospatial-index, presence-heartbeat, hot-key]; asked_at: [amazon, google, meta]
- id: "0307"; slug: food-delivery-platform;    tier: P1; primitives: [geospatial-index, saga, scheduling-queue]; note: "recombination of 0306 + 0303"
- id: "0308"; slug: ecommerce-recommendation;  tier: P2; primitives: [top-k, stream-windowing, vector-retrieval]
- id: "0309"; slug: seat-ticket-reservation;   tier: P1; primitives: [hot-key, idempotency, leader-election]; asked_at: [amazon]; note: "best pure contention question in the set"
- id: "0310"; slug: flash-sale-system;         tier: P2; primitives: [hot-key, backpressure, rate-limiting-algorithms]

# ────────────────── 04.collaboration-productivity ──────────────
- id: "0401"; slug: collaborative-document-editing; tier: P1; primitives: [conflict-resolution, delivery-semantics]; asked_at: [google]; note: "OT vs CRDT — the whole question"
- id: "0402"; slug: file-sync-storage;         tier: P1; primitives: [chunked-transfer, dedup, conflict-resolution]; asked_at: [amazon, google]
- id: "0403"; slug: calendar-scheduling;       tier: P2; primitives: [scheduling-queue, conflict-resolution]
- id: "0404"; slug: task-board-issue-tracker;  tier: P2; primitives: [cdc, multi-tenant-isolation]
- id: "0405"; slug: collaborative-whiteboard;  tier: P2; primitives: [conflict-resolution, presence-heartbeat]
- id: "0406"; slug: wiki-versioning-service;   tier: P2; primitives: [conflict-resolution, write-ahead-log]
- id: "0407"; slug: mention-and-notification-fanout; tier: P2; primitives: [fan-out, dedup]

# ───────────────────── 05.media-realtime ───────────────────────
- id: "0501"; slug: video-streaming-platform;  tier: P0; primitives: [chunked-transfer, cache-invalidation, sharding-strategies]; asked_at: [amazon, google, meta]
- id: "0502"; slug: video-upload-transcode-pipeline; tier: P1; primitives: [scheduling-queue, backpressure, chunked-transfer]; asked_at: [amazon]
- id: "0503"; slug: live-streaming;            tier: P1; primitives: [chunked-transfer, fan-out, backpressure]
- id: "0504"; slug: video-conferencing;        tier: P2; primitives: [presence-heartbeat, backpressure]
- id: "0505"; slug: image-hosting-cdn;         tier: P2; primitives: [chunked-transfer, cache-invalidation]
- id: "0506"; slug: realtime-collab-cursor-sync; tier: P2; primitives: [presence-heartbeat, conflict-resolution]

# ───────────────────── 06.data-platform ────────────────────────
- id: "0601"; slug: metrics-monitoring-system; tier: P0; primitives: [stream-windowing, top-k, sharding-strategies, backpressure]; asked_at: [amazon, google]
- id: "0602"; slug: log-aggregation-search;    tier: P1; primitives: [inverted-index, stream-windowing, backpressure]; asked_at: [amazon]
- id: "0603"; slug: ad-click-aggregation;      tier: P1; primitives: [stream-windowing, top-k, dedup]; asked_at: [google, meta]; note: "canonical exactly-once-under-late-data question"
- id: "0604"; slug: etl-batch-pipeline;        tier: P1; primitives: [backpressure, idempotency, cdc]; note: "closest to owner's JPMC work — strong story hook"
- id: "0605"; slug: cdc-replication-pipeline;  tier: P1; primitives: [cdc, delivery-semantics, quorum-replication]
- id: "0606"; slug: ab-experimentation-platform; tier: P2; primitives: [cache-invalidation, stream-windowing]
- id: "0607"; slug: event-bus-pubsub;          tier: P1; primitives: [delivery-semantics, sharding-strategies, backpressure]
- id: "0608"; slug: data-warehouse-query-layer; tier: P2; primitives: [sharding-strategies, cache-invalidation]

# ─────────────────────── 07.infra-devex ────────────────────────
- id: "0701"; slug: blob-object-storage;       tier: P1; primitives: [chunked-transfer, quorum-replication, consistent-hashing]; asked_at: [amazon, google]
- id: "0702"; slug: service-discovery;         tier: P2; primitives: [leader-election, cache-invalidation]
- id: "0703"; slug: ci-cd-pipeline;            tier: P2; primitives: [scheduling-queue, backpressure]
- id: "0704"; slug: config-management-service; tier: P2; primitives: [cache-invalidation, cdc]
- id: "0705"; slug: container-orchestrator;    tier: P2; primitives: [leader-election, scheduling-queue]; note: "skeleton only — owner has no k8s ops experience; do not imply otherwise"
- id: "0706"; slug: deployment-rollout-rollback; tier: P2; primitives: [backpressure, multi-tenant-isolation]
- id: "0707"; slug: distributed-tracing-system; tier: P1; primitives: [stream-windowing, sharding-strategies, dedup]; note: "strong observability story hook"

# ─────────────────────── 08.fintech-trust ──────────────────────
- id: "0801"; slug: payment-processing-service; tier: P1; primitives: [idempotency, saga, ledger-integrity]; asked_at: [amazon, google]
- id: "0802"; slug: ledger-double-entry;       tier: P1; primitives: [ledger-integrity, write-ahead-log, quorum-replication]
- id: "0803"; slug: wallet-balance-transfer;   tier: P1; primitives: [hot-key, idempotency, ledger-integrity]
- id: "0804"; slug: fraud-detection-pipeline;  tier: P2; primitives: [stream-windowing, top-k]
- id: "0805"; slug: trade-matching-engine;     tier: P2; primitives: [leader-election, write-ahead-log, hot-key]; note: "single-writer design — good contrast to distributed defaults"
- id: "0806"; slug: reconciliation-service;    tier: P2; primitives: [dedup, cdc, idempotency]; note: "direct JPMC story hook"

# ───────────────────────── 09.ai-search ────────────────────────
- id: "0901"; slug: search-engine;             tier: P0; primitives: [inverted-index, sharding-strategies, top-k, cache-invalidation]; asked_at: [google, amazon]
- id: "0902"; slug: typeahead-autocomplete;    tier: P1; primitives: [inverted-index, top-k, cache-invalidation]; asked_at: [google, amazon]
- id: "0903"; slug: vector-semantic-search;    tier: P2; primitives: [vector-retrieval, sharding-strategies]
- id: "0904"; slug: rag-retrieval-pipeline;    tier: P2; primitives: [vector-retrieval, cache-invalidation]; note: "ties to owner's rca-copilot project"
- id: "0905"; slug: recommendation-serving;    tier: P2; primitives: [top-k, cache-invalidation, vector-retrieval]
- id: "0906"; slug: llm-inference-gateway;     tier: P2; primitives: [rate-limiting-algorithms, backpressure, multi-tenant-isolation]
- id: "0907"; slug: feature-store;             tier: P2; primitives: [cdc, cache-invalidation, stream-windowing]

# ─────────────────── 10.enterprise-security ────────────────────
- id: "1001"; slug: authentication-sso-oauth;  tier: P1; primitives: [cache-invalidation, leader-election]; asked_at: [amazon]
- id: "1002"; slug: authorization-permission-service; tier: P1; primitives: [cache-invalidation, multi-tenant-isolation, hot-key]; note: "direct JPMC story hook — RBAC via EnumMap/EnumSet, document broker permission redesign"
- id: "1003"; slug: audit-log-service;         tier: P2; primitives: [write-ahead-log, ledger-integrity, sharding-strategies]
- id: "1004"; slug: secrets-management;        tier: P2; primitives: [quorum-replication, cache-invalidation]
- id: "1005"; slug: ddos-abuse-protection;     tier: P2; primitives: [rate-limiting-algorithms, backpressure, top-k]
- id: "1006"; slug: session-management;        tier: P2; primitives: [cache-invalidation, sharding-strategies]
- id: "1007"; slug: multi-tenant-isolation-platform; tier: P2; primitives: [multi-tenant-isolation, rate-limiting-algorithms]
```

**P0 set (14) — the only questions that must be drilled:**
`0101 · 0103 · 0104 · 0107 · 0108 · 0201 · 0202 · 0206 · 0302 · 0303 · 0306 · 0501 · 0601 · 0901`

These 14 exercise every P0 primitive at least twice. Everything else is recombination.

---

## Part 5 — Generation Contract

Three document types. Never blur them.

### 5A. Primitive/concept file — `00.base/<id>.md`

The transferable layer. **Target ≤120 lines.** Longer means it's become an essay and won't be reread.

```markdown
---
id: <primitive-id>
tier: P0 | P1 | P2
confidence: unset
---

# <Name>

> **Recall card** — exactly 5 sentences. What it is, the mechanism that matters,
> the one tradeoff, the one failure mode, the one number. This is the spaced-repetition unit.

## Mechanism

The algorithm or data structure. Not the label.

## The tradeoff

`Option | Buys you | Costs you | Choose when` table. Then a default recommendation and the
deciding variable.

## Defeaters

Every property claim with the condition under which it fails. `X guarantees Y — except when Z.`

## Failure modes

`Failure | Trigger | Blast radius | Detection signal | Mitigation` table.

## Numbers

Arithmetic shown or sourced with a date/version anchor. Never invented precision.

## Where it shows up

Links to the question files tagged with this primitive, one line each on how it manifests there.

## Say-it-in-90-seconds

The verbal version. This is what gets spoken in a round — write it as sentences, not bullets.
```

### 5B. Question skeleton — `<NN>.<domain>/<NNNN>.<slug>.md`

**Default for every question. Target 1 page, ≤90 lines.** This is a scaffold to attempt against, not a solution to read.

```markdown
---
id: "NNNN"
slug: <slug>
tier: P0 | P1 | P2
primitives: [<ids>]
asked_at: [<companies>]
attempted: [] # dates of COLD attempts, filled by hand
confidence: unset # unset | weak | ok | solid
---

# <Question as an interviewer would phrase it>

**Decomposes into:** <primitive links> — this is the line that matters most.

## Scope decisions to make

The 3–5 forks that change the design. Phrased as questions, NOT answered.
(e.g. "1:1 or group? — changes fan-out from N=1 to N=members")

## Non-functionals to pin down

Each with the _kind_ of number needed, not the number itself.

## The estimation that decides something

Which quantity, and which design fork it resolves. Do not compute it — that's the rep.

## Skeleton diagram

Boxes only, minimal ASCII. No annotations.

## The hard part

One paragraph: where the actual difficulty lives. Most of the design is boilerplate;
name the 20% that is not.

## Tradeoffs you'll be asked to defend

2–3, stated as forks with no answer given.

## Top failure mode

One line. The thing that breaks first.

## Story hook

Which of the owner's real projects attaches here, or `none — first principles`.
Never invent experience.

## Do NOT read past this line before a cold attempt.
```

### 5C. Full 45-min artifact — `full/<NNNN>.<slug>-45min.md`

**P0 only. Only after `attempted:` is non-empty.** If asked to generate one for an unattempted question, refuse and explain rule zero.

Structure is a timed round transcript ordered by wall clock, not by topic:

| Phase                      | Clock     |
| -------------------------- | --------- |
| Requirements & scope       | 0:00–0:05 |
| Estimation & API           | 0:05–0:10 |
| High-level design          | 0:10–0:22 |
| Deep dive                  | 0:22–0:37 |
| Failure, bottlenecks, wrap | 0:37–0:45 |

Contains, in order: **Part A — full L4 answer** (all five phases, with verbatim scripts for the requirements and wrap phases) → L4 signal check → pushbacks it invites → **Part B — full L5 answer** (same five phases, rewritten) → delta table → pushback ladder (P1 mechanism, P2 scale/failure, **P3 premise reversal at minute 35**) → over-reach warnings → shared reference (numbers with arithmetic, vocabulary, Amazon-vs-Google emphasis, sources).

**L5 must differ structurally, not by length.** The six axes:

1. Negotiates requirements down rather than accepting them, and names what the cut buys.
2. States a **priority ordering** over non-functionals that visibly governs later choices.
3. Lets a number kill an option in real time.
4. Names the rejected alternative **and the condition that flips the choice**.
5. Volunteers blast radius, degraded mode, rollout, migration, cost — unprompted.
6. Names its own weakest assumption before the interviewer does.

If the delta table's "signal" column ever reads "more detail," the L5 answer is not yet an L5 answer.

> If the `system-design-answer` skill is installed, use it for 5C — this section is its compressed form.

### Writing rules (all three types)

- Mechanism over label. Never "fast," "scalable," "highly available" without the mechanism and its cost.
- Every property claim carries its defeater.
- Numbers sourced or hedged as `order of magnitude:`. Never invented precision. Service limits get `verify current limit` rather than a recalled figure.
- Every named managed service comes with its mechanism and its cost. "Use DynamoDB" earns nothing; "DynamoDB, partition key `tenantId#date`, spreads the hot tenant, makes cross-tenant queries a GSI read" earns the point.
- Every best practice names the failure it prevents.
- No fabricated incidents — cite public postmortems/docs, or label `Canonical failure pattern (not a specific incident)`.
- Mark uncertainty as `> ⚠️ Low confidence:` rather than writing smoothly around a gap.
- Java 17 baseline for code. Tables over paragraphs. English throughout.

---

## Part 6 — Index and Practice State

**`1index.md`** is the authoritative, deduplicated question map. It is intentionally maintained with question moves so broken ownership is visible in the same review. `1AX/` owns Alex Xu-covered prompts; domain folders contain only non-duplicates.

Optional derived views may be generated from front matter, but they never replace `1index.md`:

- `INDEX-by-primitive.md` — study coverage by primitive.
- `INDEX-by-domain.md` — browsing by folder, tier, and confidence.

**`SCORECARD.md`** — rubric trend. Row per run, column per dimension, scores 1–4.

| Date | Question | 1 Scope | 2 Estimation | 3 HLD | 4 Deep dive | 5 Tradeoffs | 6 Failure/ops | 7 Comms/clock | Notes |
| ---- | -------- | ------- | ------------ | ----- | ----------- | ----------- | ------------- | ------------- | ----- |

**3 = target hire for L4/SDE II. 4 = senior signal.** Gated on the weakest dimension — three 3s and a 2 is a fail. Trend matters more than average; a flat line after five runs means change the drill, not do more of it.

**`FAILURE-LOG.md`** — by cause, never by question. Causes: `scope · estimation · mechanism · assembly · sequencing · articulation · pushback`. Only `mechanism` has "read more" as its remedy; most real failures are articulation and sequencing, which reading cannot fix.

---

## Part 7 — Build Order

Execute in this order. Stop at the end of each step and report; do not run the whole thing unattended.

**Step 1 — Normalize.** Verify `1index.md` links, canonical Alex Xu ownership, and the question filename pattern. Do not create duplicate folder aliases.

**Step 2 — Front-matter backfill.** Add front-matter (schema in 5B) to every existing question file from the Part 4 manifest. Do not alter existing body content.

**Step 3 — MVP0 · P0 primitives (14 files).** Generate or strengthen the matching `00.base/` concept files for `tier: P0` only. Recall-card depth. This is the highest-value artifact in the repo—everything else links here.

**Step 4 — MVP0 · P0 skeletons (14 files).** Generate skeletons for the 14 P0 questions.
_Stop here._ Practice the material before expanding breadth. The trigger for more content is a failure-log mechanism gap, not repository completeness.

**Step 5 — Index + practice scaffolds.** Refresh `1index.md`; generate `SCORECARD.md`, `FAILURE-LOG.md`, and `runs/` only when practice begins.

**Step 6 — P1 skeletons (~30).** Trigger: an onsite is scheduled. Generate only for domains matching the company.

**Step 7 — Full artifacts.** Trigger: a P0 question has been attempted cold and scored ≤2 on any dimension. Generate `full/` for that question only. **Check `attempted:` first — refuse if empty.**

**Step 8 — P1 primitives, then P2 skeletons.** Only if time exists after Steps 1–7. It probably won't, and that is the correct outcome.

**Idempotency:** re-running any step overwrites generated files deterministically but must never overwrite `attempted:`, `confidence:`, `runs/`, `SCORECARD.md` rows, or `FAILURE-LOG.md` entries. Those are human state.

---

## Part 8 — Quality Gate

Run before emitting any file. Any "no" gets fixed first.

1. Does every property claim state its defeater?
2. Is every precise number arithmetic-shown or sourced with a date/version anchor?
3. Is every named service accompanied by its mechanism and its cost?
4. Is every production issue cited or labeled canonical?
5. Does every best practice name the failure it prevents?
6. Does every skeleton stop short of answering — is it a scaffold, not a solution?
7. For full artifacts: does L5 differ **structurally** from L4 on at least four of the six axes?
8. Does the delta table's "signal" column ever say "more detail"? If yes, rewrite.
9. Does the pushback ladder's P3 actually reverse a premise?
10. Does any content imply experience the owner does not have (Kafka ops, Kubernetes, GCP, Databricks)?
11. Could a principal engineer point at any paragraph and say "that's hand-wavy"?

---

## Part 9 — Study Loop

The canonical schedule lives in `00.sd plan.md`; this section defines the non-negotiable loop.

**Rule zero: attempt before reading.** Cold attempt → then read → the delta _is_ the learning. Reading the solution first builds recognition, not generation, and is the reason people with 60 questions "covered" fail rounds. The `Do NOT read past this line` marker in every skeleton exists for this.

| Rep                    | Time   | Frequency       | What it trains                                                                                                                                  |
| ---------------------- | ------ | --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| **A · Cold-open**      | 5 min  | 3–5×/wk         | Assembly. Bound the problem + name the primitives, aloud, then check against the tags. If hit rate <80%, do more of these instead of full runs. |
| **B · Full timed run** | 60 min | 2–3×/wk in ramp | Performance. 45 min **spoken aloud and recorded**, self-grade, play back the two weakest phases, log by cause, _then_ read.                     |
| **C · Adversarial**    | 20 min | 1×/wk           | Pushback. Answer the three-step ladder cold on a design already done.                                                                           |

**Recording is the highest-leverage cheap thing here.** Rambling and circling are invisible from the inside and obvious on playback.

**Scale the loop to available time:**

| Time available | Do |
| --- | --- |
| Maintenance | Two cold-opens + one focused defense per week |
| Three-week ramp | Foundations, core assembly, then adversarial runs |
| Two-week intensive | 90–120 min/day; alternate full runs with mechanism repair |
| Final 2 days | Failure log + recall cards; no new material |

See `00.sd plan.md` for exact two-week and three-week schedules and 30/60/90/120-minute daily templates.

**Anti-patterns:** reading first · practicing silently · treating question count as a metric · **building the repo instead of using it** · training L5 depth at an L4 target (over-engineering is a failure mode) · skipping estimation because it feels like busywork.

---

## References

1. [DDIA — Kleppmann](https://dataintensive.net/) — ch. 5–9. Organized by primitive, which is why this repo has a `00.base/` axis.
2. [AWS Builders' Library](https://aws.amazon.com/builders-library/) — timeouts, retries, backpressure, blast radius. Source material for failure sections and Amazon-flavored pushback.
3. [Google SRE Book — Addressing Cascading Failures](https://sre.google/sre-book/addressing-cascading-failures/) — degraded-mode reasoning; where rubric-dimension-6 fours come from.
4. [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer) — naming source for primitives; skip its worked solutions until after a cold attempt.
