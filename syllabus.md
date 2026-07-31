# Google L4/L5 System Design Interview Crash Course — 4-Week Study Plan

You're in a good spot. Four years of Spring Boot microservices + AWS (Lambda, ECS, SQS, a bit of Kafka) means you've _seen_ most of the primitives in production; you just haven't had to architect them from a blank whiteboard under time pressure. The gap is pattern fluency, not fundamentals. This plan is built around that.

Below is the syllabus first, then a 4-week schedule, then validation checkpoints.

---

## Part 1: What a Google L4/L5 System Design Interview Actually Tests

Before the syllabus, calibrate on what's scored. Rubrics at Google (and Meta, Amazon) generally look at five signals:

1. **Requirements gathering** — do you drive the scoping, or wait for the interviewer to feed you?
2. **High-level architecture** — can you sketch a coherent end-to-end system in 5-10 minutes?
3. **Deep dives** — when pushed on one component, can you go 3-4 layers deep with concrete trade-offs?
4. **Data modeling & estimation** — schemas, QPS, storage, bandwidth, cache hit rates.
5. **Trade-off articulation** — the interviewer asks "why not X?" and you have a real answer, not hand-waving.

**L4 bar:** Lead one service's design end-to-end, reason about consistency/availability trade-offs, size the system, handle one or two curveballs ("what if traffic 10x's?"). You don't need to invent novel architectures.

**L5 bar:** Everything L4 plus — multi-service orchestration, explicit failure modes, scaling bottlenecks identified before the interviewer asks, and opinionated recommendations ("I'd pick Cassandra here because…"). L5 candidates _drive_ the interview.

The good news: you don't need to know everything. You need ~15 building blocks cold, and a repeatable framework to assemble them.

---

## Part 2: The Syllabus (Topics + Depth)

I'm organizing this by **depth tier**. Tier 1 you must know cold. Tier 2 you should be able to discuss with specific numbers and trade-offs. Tier 3 is "smart-sounding references" — know when to mention them, know roughly how they work, don't pretend to have implemented them.

### Tier 1 — Must Know Cold (can explain in 2 minutes, can draw it)

**1. The Interview Framework itself**

- Requirements clarification (functional + non-functional)
- Back-of-envelope estimation (QPS, storage/year, bandwidth, memory for cache)
- API design (REST endpoints, request/response shape)
- High-level architecture diagram (client → LB → service → DB/cache)
- Data model (tables/collections, keys, indexes)
- Deep dive on 1-2 components the interviewer picks
- Bottlenecks, scaling, failure modes

You should rehearse this flow until it's muscle memory. Most candidates fail here, not on technical depth.

**2. Load Balancers**

- L4 vs L7, round-robin vs least-connections vs consistent hashing
- Health checks, sticky sessions (and why to avoid them)
- Where they sit: client → DNS → LB → app servers, and LB in front of DBs

**3. Caching**

- Client-side, CDN, reverse proxy, application cache, DB cache
- Cache-aside vs write-through vs write-back vs write-around
- Eviction: LRU, LFU, TTL
- Cache invalidation (the hard problem — know why)
- Redis vs Memcached (Redis: data structures, persistence, replication; Memcached: simpler, multithreaded, pure KV)

**4. Databases — SQL vs NoSQL**

- When to pick SQL (Postgres/MySQL): transactions, joins, strong consistency, moderate scale
- When to pick NoSQL:
  - Key-value (DynamoDB, Redis) — session stores, lookups
  - Document (MongoDB) — flexible schema, nested data
  - Wide-column (Cassandra, HBase) — massive writes, time-series
  - Graph (Neo4j) — relationships (social, recommendations)
- ACID vs BASE
- Primary keys, secondary indexes, partition keys (huge for NoSQL)

**5. Sharding & Replication**

- Horizontal vs vertical partitioning
- Shard key selection (hot shard problem)
- Consistent hashing — you MUST be able to draw the ring
- Leader-follower replication, multi-leader, leaderless (Dynamo-style)
- Read replicas for read-heavy workloads
- Replication lag and what it breaks

**6. CAP Theorem & Consistency Models**

- CAP: you pick 2 during a partition (really it's CP vs AP)
- PACELC extension (Else: Latency vs Consistency)
- Strong consistency, eventual consistency, read-your-writes, monotonic reads
- Quorum reads/writes (W + R > N)

**7. Message Queues / Async Processing**

- Kafka vs SQS vs RabbitMQ — this is in your wheelhouse, exploit it
- At-most-once vs at-least-once vs exactly-once (and why exactly-once is mostly a lie at the transport layer)
- Dead letter queues
- Pub/sub vs point-to-point
- Kafka specifics: partitions, consumer groups, offsets, retention

### Tier 2 — Know Enough to Discuss Trade-offs

**8. Rate Limiting**

- Token bucket, leaky bucket, fixed window, sliding window
- Where to enforce (edge vs service)
- Distributed rate limiting (Redis with Lua scripts)

**9. API Gateway & Service Mesh**

- Auth, rate limiting, request routing, aggregation
- Service mesh (Istio/Linkerd) — when it's worth the operational cost

**10. Search & Indexing**

- Inverted index concept
- Elasticsearch/OpenSearch at a high level
- When search is a separate concern from your primary DB

**11. Object Storage & CDNs**

- S3 characteristics (eventual consistency historically, now strong for new objects)
- CloudFront/CDN cache behavior, TTL, invalidation
- Signed URLs for private content

**12. Observability**

- Metrics (Prometheus/CloudWatch), logs (ELK/CloudWatch Logs), traces (Jaeger/X-Ray)
- SLIs, SLOs, error budgets — Google _invented_ this vocabulary, using it scores points

**13. Authentication & Authorization**

- OAuth 2.0 / OIDC flows (at least authorization code)
- JWT vs session cookies, refresh tokens
- API keys for service-to-service

### Tier 3 — Know They Exist, Know When to Mention

**14. Consensus**

- Paxos, Raft (for leader election, distributed config)
- When you need consensus vs when eventual consistency is fine
- Zookeeper, etcd use cases

**15. Stream Processing**

- Kafka Streams, Flink, Spark Streaming
- Event sourcing, CQRS

**16. Geo-distribution**

- Multi-region active-active vs active-passive
- DNS-based routing, Anycast

---

## Part 3: The Canonical Problems

You should be able to design each of these in 45 minutes. The interviewer will ask one of them or a close variant.

| Problem                            | What it tests                                              |
| ---------------------------------- | ---------------------------------------------------------- |
| URL shortener (bit.ly)             | Hashing, KV store, cache, read-heavy scaling               |
| Rate limiter                       | Algorithms, distributed state, Redis                       |
| Chat/messaging (WhatsApp)          | Websockets, fan-out, message ordering, delivery guarantees |
| News feed (Twitter/Facebook)       | Fan-out-on-write vs on-read, ranking, caching              |
| Video streaming (YouTube/Netflix)  | CDN, chunking/HLS, metadata vs blob storage                |
| Ride-sharing (Uber)                | Geospatial indexing, matching, real-time updates           |
| Web crawler                        | BFS, politeness, distributed workers, dedup                |
| Typeahead/autocomplete             | Trie, ranking, caching                                     |
| Distributed file storage (Dropbox) | Chunking, dedup, sync                                      |
| Notification system                | Fan-out, channels (push/email/SMS), retries                |
| Ad click aggregator                | Stream processing, exactly-once, time windows              |
| Distributed job scheduler          | Leader election, persistence, retries                      |

---

## Part 4: The 4-Week Plan

Assume ~10 hours/week. Adjust if you have more or less. Each week has three tracks: **Learn**, **Practice**, **Validate**.

### Week 1 — Framework + Fundamentals

**Goal:** Never freeze at the whiteboard. Own the first 10 minutes of any design interview.

| Day     | Focus                                                                                                                                                                                                |
| ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Mon-Tue | Read Alex Xu's _System Design Interview Vol 1_ chapters 1-4 (scale from zero, back-of-envelope, framework). Watch 2-3 Jordan Has No Life or ByteByteGo videos on the framework.                      |
| Wed     | Memorize estimation numbers: L1/L2 cache, RAM, SSD, network latencies (Jeff Dean's "numbers every programmer should know"). Practice estimating QPS, storage, bandwidth for 3 hypothetical products. |
| Thu     | Deep on load balancers + caching strategies. Build mental model: where does each cache layer sit?                                                                                                    |
| Fri     | Databases — SQL vs NoSQL decision tree. Pick 3 real products and argue which DB you'd use and why.                                                                                                   |
| Sat     | **Mock design:** URL shortener. Time-box to 45 min. Record yourself.                                                                                                                                 |
| Sun     | Review recording. Note where you stalled. Re-do the weakest section.                                                                                                                                 |

**Validation Week 1:**

- Can you recite the 7-step framework in 60 seconds?
- Can you estimate storage for "1M tweets/day for 5 years" in under 2 minutes on paper?
- Can you draw 4 caching layers from client to DB and explain when each wins?
- Can you defend SQL vs NoSQL for 3 different products without saying "it depends" as your main answer?

### Week 2 — Scaling Primitives + Data

**Goal:** Fluency with sharding, replication, consistency. These show up in every problem.

| Day | Focus                                                                                                                                              |
| --- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Mon | Sharding strategies. Draw consistent hashing from scratch 3 times. Understand resharding pain.                                                     |
| Tue | Replication: leader-follower, multi-leader, leaderless. Replication lag and its consequences.                                                      |
| Wed | CAP + PACELC. Read a summary of the Dynamo paper (or the DDIA chapter). You don't need the paper itself — know the model.                          |
| Thu | Message queues deep dive. Lean into your Kafka/SQS experience. Understand partitioning, consumer groups, ordering guarantees. Compare to RabbitMQ. |
| Fri | Rate limiting algorithms. Implement token bucket in Java/Python in ~30 lines to cement it.                                                         |
| Sat | **Mock design:** Rate limiter (distributed). Then **Mock design:** Twitter news feed.                                                              |
| Sun | Review. Focus especially on how you handled "what's your shard key?" and "fan-out on read vs write?"                                               |

**Validation Week 2:**

- Can you draw consistent hashing and explain virtual nodes without notes?
- Can you explain why W+R>N gives strong consistency in a quorum system?
- Can you name 3 concrete situations where at-least-once delivery causes bugs and how you'd fix them (idempotency keys, dedup tables)?
- Can you design fan-out for a user with 100M followers without saying "just use Kafka"?

### Week 3 — Canonical Problems + Deep Dives

**Goal:** Build a library of reusable sub-designs.

| Day | Focus                                                                                                    |
| --- | -------------------------------------------------------------------------------------------------------- |
| Mon | **Mock design:** Chat system (WhatsApp). Focus on websocket fan-out, message ordering, offline delivery. |
| Tue | **Mock design:** Video streaming (YouTube). Focus on CDN, HLS, metadata service vs blob storage.         |
| Wed | **Mock design:** Uber/ride-sharing. Focus on geohashing or quadtrees, matching service.                  |
| Thu | **Mock design:** Web crawler. Focus on distributed workers, politeness, URL dedup (bloom filters).       |
| Fri | **Mock design:** Typeahead. Trie + ranking + caching top-k.                                              |
| Sat | Pick the weakest of the above, redo from scratch.                                                        |
| Sun | Observability + auth crash course. Learn SRE vocabulary (SLI/SLO/error budget).                          |

**Validation Week 3:**

- For each of the 5 problems above, can you produce: API, data model, high-level diagram, one deep dive, one failure mode — in 45 min?
- Can you explain fan-out-on-write vs fan-out-on-read and pick one for a given user distribution?
- Can you explain why a CDN makes video streaming feasible and what the origin still does?

### Week 4 — Polish, Mocks, Trade-off Fluency

**Goal:** Interview-ready. Do real mocks with humans.

| Day | Focus                                                                                                              |
| --- | ------------------------------------------------------------------------------------------------------------------ |
| Mon | **Mock design:** Notification system or ad click aggregator (stream processing flavor).                            |
| Tue | **Mock design:** Dropbox/file sync.                                                                                |
| Wed | Schedule and do a **live mock interview** — paid (interviewing.io, Hello Interview) or a senior friend. Record it. |
| Thu | Review recording brutally. List every moment of hesitation. Fill the gaps.                                         |
| Fri | Second live mock if possible. Otherwise, redo your weakest canonical problem blindfolded (no notes).               |
| Sat | Review all your notes. Build a 1-page cheat sheet of numbers, patterns, decision trees.                            |
| Sun | Rest. Light review only.                                                                                           |

**Validation Week 4:**

- Did you score 3+ on the interviewer's rubric in a live mock? (Most platforms give written feedback.)
- Can you teach any one of your canonical designs to a non-expert in 10 minutes?
- Do you have a 1-page cheat sheet that fits your brain?

---

## Part 5: How to Actually Validate Mastery

This is the part most people skip. Validation is NOT "I read the chapter and it made sense." Use these concrete checkpoints:

**1. The Blank Whiteboard Test**
Pick a problem. Set a 45-min timer. No notes, no internet. Design it end-to-end, _out loud_, recording yourself. Play back at 1.5x. If you're saying "um" or "it depends" more than 3 times, or if you're skipping estimation, or if you can't name your shard key — you're not ready on that problem.

**2. The Why-Not Test**
For every component you choose, ask yourself: "Why not the alternative?" If you said Cassandra, why not DynamoDB? If you said Kafka, why not Kinesis? If you have a one-sentence answer with a concrete trade-off (latency, ops cost, consistency model, team familiarity), you're good. If you hand-wave, you have a gap.

**3. The 10x Test**
After designing, ask: "What breaks at 10x traffic?" You should identify the bottleneck without looking. Usually it's a single DB, a hot shard, or a synchronous call that should be async.

**4. The Failure Mode Test**
"What if the primary DB dies? What if the cache dies? What if a consumer lags by 2 hours?" For each, you should have a concrete response (failover, cache stampede protection, backpressure, DLQ). Not "we'd handle it."

**5. Peer Review**
Explain your design to a friend who doesn't know the domain. If they can't follow it, your structure is off — and that's exactly what the interviewer will see.

**6. Rubric Self-Scoring**
After each mock, score yourself 1-5 on: scoping, estimation, architecture, deep dive, trade-offs, failure modes, communication. Track over weeks. You should see clear upward movement.

---

## Part 6: Pitfalls Specific to Your Profile

Because you mentioned your team does the design and you mostly implement within existing patterns, watch for these traps:

- **Jumping to implementation.** You'll want to talk about Spring Boot annotations or Lambda cold starts. Don't — zoom out. Interviewers want architecture, not library names.
- **Defaulting to AWS services.** Saying "I'd use SQS" is fine, but at Google you should translate: "I'd use a distributed queue with at-least-once delivery — SQS on AWS, Pub/Sub on GCP." Shows you know the concept, not just the vendor.
- **Under-scoping.** Because you're used to getting requirements handed down, you may skip the clarification phase. Force yourself to spend the first 5 minutes on requirements — it's a graded step.
- **Over-hedging.** "I'm not sure but maybe…" loses points. Pick a position, commit, and be open to revising. L5 candidates commit.

---

## Resources (as required — prioritizing code/repos)

- **[donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)** — the canonical GitHub repo. Use as your reference index, not as linear reading.
- **[ByteByteGo / Alex Xu's companion repos](https://github.com/ByteByteGoHq/system-design-101)** — diagrams and summaries mirroring the books.
- **[karanpratapsingh/system-design](https://github.com/karanpratapsingh/system-design)** — well-structured notes, good for Tier 1/2 topic review.
- **[Hello Interview](https://www.hellointerview.com/)** — structured walkthroughs of the canonical problems with the exact rubric Google-style interviews use. Highest-leverage paid resource for your level.
- **[Jordan Has No Life — YouTube](https://www.youtube.com/@jordanhasnolife5163)** — deep dives on canonical problems, opinionated, the one YouTube channel worth time.
- **Designing Data-Intensive Applications** by Martin Kleppmann — the reference text for Tier 1 data concepts. Read chapters 5, 6, 7, 9, 11 specifically; skip the rest for now.

Good luck. You have the base; this is a pattern-matching problem, and four weeks of deliberate practice is enough.
