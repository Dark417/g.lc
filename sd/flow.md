# System Design Interview Flow

Universal step-by-step guide for a 45-minute system design interview.
Follow this pattern for every question. Time allocations are for a 45-min session.

---

## Step Index

1. [Clarify Scope](#1-clarify-scope) — 3–4 min
2. [Functional Requirements](#2-functional-requirements) — 3–4 min
3. [Non-Functional Requirements](#3-non-functional-requirements) — 2–3 min
4. [Capacity Estimation](#4-capacity-estimation) — 3–4 min
5. [High-Level Architecture](#5-high-level-architecture) — 5–6 min
6. [API Design](#6-api-design) — 3–4 min
7. [Data Model](#7-data-model) — 4–5 min
8. [Deep Dives](#8-deep-dives) — 10–12 min
9. [Reliability and Operations](#9-reliability-and-operations) — 3–4 min
10. [Security and Abuse](#10-security-and-abuse) — 2 min
11. [Tradeoffs and Wrap-up](#11-tradeoffs-and-wrap-up) — 2 min

---

## 1. Clarify Scope

**Goal:** Narrow the problem. Don't design everything. Show you think before coding.

**What to do:**
- Restate the problem in one sentence to confirm understanding.
- Ask about scale: DAU, QPS, data size. If interviewer says "assume large scale", estimate yourself.
- Ask which features are in scope. Pick the 2–3 core ones; explicitly defer the rest.
- Ask about consistency requirements: strong vs eventual. Ask about latency sensitivity.
- Clarify read/write ratio — this drives your whole architecture.
- State your assumptions explicitly. Don't wait to be corrected — say "I'll assume X".

**Must-ask questions:**
- "How many users / daily active users?"
- "Is this read-heavy or write-heavy?"
- "Do we need strong consistency or is eventual OK?"
- "Are we designing for global scale or single region?"
- "What's the latency target for the main read path?"

**What interviewers look for:** You don't blindly start drawing boxes. You understand the problem space. You make reasonable assumptions and state them.

**Avoid:** Spending >5 min here. Don't ask about every edge case — pick the most impactful constraints.

---

## 2. Functional Requirements

**Goal:** Define the exact behaviors the system must support.

**What to do:**
- List as user-facing actions: "User can do X", "System does Y when Z".
- Prioritize by core vs nice-to-have. Mark out-of-scope explicitly.
- Think in terms of reads and writes: what data flows in, what flows out.
- Consider both the happy path and key error paths (what happens if service is down?).

**Core template:**
```
Must have:
- [Primary write action]
- [Primary read action]
- [Key secondary behavior]

Out of scope:
- [Feature 1] — deferred
- [Feature 2] — deferred
```

**What interviewers look for:** You can identify the 3–5 most important behaviors without listing everything. You understand user journeys, not just APIs.

---

## 3. Non-Functional Requirements

**Goal:** Define the operating constraints that shape every architectural decision.

**What to specify:**

| Dimension | Typical target | What it drives |
|-----------|----------------|----------------|
| Availability | 99.9% – 99.99% | Redundancy, failover strategy |
| Latency (p99) | <100ms reads, <500ms writes | Caching, async writes, CDN |
| Durability | No data loss (RPO=0) | Replication factor, WAL |
| Consistency | Strong vs eventual | DB choice, cache invalidation |
| Scale | QPS, storage TB | Sharding, horizontal scale |
| Throughput | Messages/sec, events/sec | Queue depth, batch processing |

**Always mention:**
- "Reads should be <Xms p99 at the user-facing layer"
- "We can tolerate eventual consistency for [X] but need strong consistency for [Y]"
- "System should be available even during partial failures"

**What interviewers look for:** You distinguish between strong and eventual consistency. You can justify why you chose a specific latency target. You understand that every NFR is a design forcing function.

---

## 4. Capacity Estimation

**Goal:** Justify your scaling decisions with numbers. Shows you're thinking about production.

**Framework:**
1. Estimate DAU (daily active users)
2. Derive write QPS: `DAU × writes_per_day / 86400`
3. Derive read QPS: `write_QPS × read_write_ratio`
4. Estimate storage: `writes_per_day × record_size × retention_days`
5. Estimate bandwidth: `read_QPS × response_size`

**Key numbers to memorize:**
- 1M DAU, 10 writes/day → ~115 writes/sec
- 100M DAU, 10 writes/day → ~11,500 writes/sec
- 1KB per record × 100M writes/day → ~100GB/day
- A single DB can handle ~10K QPS; a Redis node ~100K QPS

**What to highlight:**
- "At 100K QPS, a single DB won't cut it — we need sharding or a cache layer"
- "Storage grows at ~10TB/year, so we need a tiered storage strategy"
- "Peak traffic is 3–5x average — plan for that, not average"

**What interviewers look for:** Ballpark numbers, not precision. Can you identify when you need a cache, when you need sharding, when a single machine is fine? Identify bottlenecks.

---

## 5. High-Level Architecture

**Goal:** Draw the major components and the critical data flows connecting them.

**Standard components to consider:**

```
Client → Load Balancer → API Layer → [Cache] → Database
                                  → Message Queue → Workers
                                  → Object Store
                                  → CDN (for static/media)
```

**What to cover:**
- **Client tier:** Web, mobile, SDK — where do requests originate?
- **Edge/CDN:** For read-heavy, latency-sensitive, or static content
- **API layer:** Stateless services, horizontally scalable
- **Cache layer:** Redis/Memcached — what do you cache? Cache-aside vs write-through?
- **Primary datastore:** Which DB type? Why? (RDBMS for ACID, NoSQL for scale/flexibility)
- **Async processing:** Message queue for fan-out, heavy jobs, decoupling
- **Object/blob storage:** S3 for large binary data
- **Search index:** Elasticsearch/Solr for full-text or geo queries

**Draw the write path first, then the read path.** Show data flowing through the system.

**What interviewers look for:** You can identify which components are needed and why. You don't add components just because they exist — every box must justify its presence. You understand the critical path.

---

## 6. API Design

**Goal:** Define the contract between callers and your system.

**What to specify per endpoint:**
- Method + path (REST) or message name (gRPC/event)
- Request parameters and their types
- Response schema
- Error codes and semantics
- Idempotency behavior (can you retry safely?)
- Rate limiting / auth requirements

**REST template:**
```
POST /v1/resource
Headers: Authorization: Bearer <token>
Body: { field1: string, field2: int }
Response 201: { id: string, created_at: timestamp }
Response 400: { error: "invalid_input", message: "..." }
Response 429: { error: "rate_limited", retry_after: int }
```

**Key considerations:**
- **Idempotency:** POST with idempotency-key header for financial/critical ops
- **Pagination:** Cursor-based (not offset) for large datasets
- **Versioning:** URL path `/v1/` is simplest; header versioning for backward compat
- **Async vs sync:** Long operations should return 202 + job ID, not block
- **Webhooks vs polling:** For event delivery to external systems

**What interviewers look for:** You don't skip API design. You think about idempotency, pagination, and error handling. You can articulate gRPC vs REST tradeoffs.

---

## 7. Data Model

**Goal:** Design the schema and access patterns that drive storage choices.

**Steps:**
1. List the core entities (nouns in the system)
2. Define attributes and types for each
3. Define relationships (1:1, 1:N, M:N)
4. Define the access patterns (reads by what key? joins needed?)
5. Choose storage: relational (normalized, ACID), NoSQL (denormalized, scale), time-series, graph
6. Define indexes and partition keys
7. Address hotspots: what if one row/partition gets hammered?

**Schema template:**
```
users:          id (PK), username, email, created_at
posts:          id (PK), user_id (FK), content, created_at
follows:        follower_id + followee_id (composite PK), created_at
timeline_cache: user_id (PK), post_ids[] (sorted by time)
```

**Partitioning strategy:**
- Partition by `user_id` hash for user-centric data
- Partition by `created_at` range for time-series data
- Be explicit: "hot user" scenario — celebrity with 100M followers writes 1 post → fan-out storm

**What interviewers look for:** You design for access patterns, not normalization. You think about what queries you need to run and work backwards to schema. You address hotspot/hot partition problems.

---

## 8. Deep Dives

**Goal:** Show depth on the 2–3 hardest or most interesting components. This is where L4 vs L5 differentiation happens.

**How to pick what to deep-dive:**
- The component that handles the highest traffic
- The component with the hardest consistency/correctness requirement
- The component the interviewer hints at ("how would you handle X?")

**Canonical deep-dive patterns:**

### Fan-out and Feed Generation
- Push model (write to followers' feeds on post): low read latency, expensive writes
- Pull model (compute feed at read time): cheap writes, expensive reads
- Hybrid: push to active users, pull for inactive / celebrity accounts

### Distributed Cache
- Cache-aside vs write-through vs write-behind
- TTL strategy — what's the right expiry?
- Cache invalidation — how do you avoid stale reads?
- Thundering herd — mutex/lock on cache miss, or probabilistic early expiration

### Sharding / Partitioning
- Hash partitioning (uniform distribution, hard to range scan)
- Range partitioning (enables scans, prone to hotspots)
- Consistent hashing (minimal rebalancing on node add/remove)
- Hotspot mitigation: add random suffix to hot keys, scatter reads

### Consistency and Replication
- Leader-follower: strong consistency on leader, eventual on followers
- Quorum reads/writes (R + W > N): tunable consistency
- Saga pattern for distributed transactions (choreography vs orchestration)
- Two-phase commit (2PC): strong but slow, single-point risk

### Search and Indexing
- Inverted index: term → posting list
- Trie for prefix search / autocomplete
- Elasticsearch: distributed inverted index with replicas
- Geo-index: geohash or S2 cells for proximity queries

### Rate Limiting
- Token bucket: allows bursts, refills at fixed rate
- Sliding window counter: more accurate than fixed window
- Distributed: Redis + Lua script for atomic operations
- Per-user vs per-IP vs per-endpoint

**What interviewers look for (L4):** You can explain the core tradeoff, pick an approach, and justify it. You handle the failure case.

**What L5 adds:** You proactively identify second-order problems. You quantify tradeoffs. You propose multiple options with explicit tradeoffs. You think about operational cost (who maintains this?). You think about future scale (10x growth, what breaks first?).

---

## 9. Reliability and Operations

**Goal:** Show that you design for failure, not just the happy path.

**Checklist:**

**Failure handling:**
- Retries with exponential backoff + jitter (avoid retry storm)
- Circuit breaker (stop calling a failing downstream immediately)
- Timeout + fallback (degrade gracefully, serve stale data, return empty)
- Bulkhead pattern (isolate failure domains — don't let one bad tenant kill all)

**Data durability:**
- Replication factor ≥ 3 for critical data
- Async replication for performance with sync for critical paths
- WAL (write-ahead log) before acknowledging writes
- Regular backups with tested restore procedures

**Idempotency and exactly-once:**
- Idempotency keys on all write APIs
- Deduplication at consumer layer with seen-message cache
- At-least-once delivery + idempotent consumers = effectively exactly-once

**Observability:**
- Metrics: QPS, error rate, p50/p99 latency per endpoint
- Logs: structured, searchable, retention policy
- Traces: distributed traces for request path debugging
- Alerts: on SLO breach, not just raw error rate

**Capacity and ops:**
- Auto-scaling (horizontal, triggered by QPS or queue depth)
- Graceful degradation under load (shed non-critical features first)
- Blue/green or canary deployments for zero-downtime releases

**What interviewers look for:** You don't just say "add a load balancer". You have specific mechanisms for retries, timeouts, and data loss prevention. You mention observability.

---

## 10. Security and Abuse

**Goal:** Show security awareness without derailing into a security deep-dive.

**AuthN / AuthZ:**
- API keys for service-to-service; JWT/OAuth2 for user-facing
- RBAC: role-based permissions at the API layer
- Least privilege for service accounts

**Data protection:**
- Encryption at rest (AES-256) and in transit (TLS 1.3)
- PII handling: separate store, access audit log, right to deletion
- Secrets management: Vault or AWS Secrets Manager, never hardcode

**Abuse and rate limiting:**
- Per-user and per-IP rate limits at the API gateway
- Bot detection: CAPTCHA, behavioral signals, device fingerprint
- Content moderation pipeline for user-generated content

**Common attack surfaces:**
- SQL injection → parameterized queries only
- SSRF (server-side request forgery) → allowlist outbound URLs
- DDoS → CDN/WAF, IP-based blocking, anycast routing

**What interviewers look for:** You mention auth, encryption, and rate limiting. You identify the specific abuse vectors for the system you're designing. You don't need to be a security expert, but you can't ignore it.

---

## 11. Tradeoffs and Wrap-up

**Goal:** Demonstrate engineering judgment. Every decision has a cost.

**Framework for discussing tradeoffs:**
```
I chose [X] over [Y] because [Z].
The cost of [X] is [A]. If that becomes a problem, we could migrate to [Y].
The first thing that will break at 10x scale is [B].
```

**Common tradeoff dimensions:**
- Consistency vs availability (CAP theorem)
- Latency vs cost (cache everything vs query DB)
- Complexity vs operability (microservices vs monolith)
- Write amplification vs read performance (pre-compute vs lazy compute)
- Strong schema vs schema flexibility (RDBMS vs document store)

**Closing move — always end with:**
- "The biggest risks in this design are X and Y."
- "If I had more time, I would: [1] detail the [component], [2] add [feature]."
- Optionally: "This is how I'd phase the rollout: start with [MVP], then add [X]."

**What interviewers look for:** You don't claim your design is perfect. You know what you traded away and why. You have a clear mental model of what breaks under load, what's operationally expensive, and what you'd revisit.

---

## Time Budget (45 min)

| Step | Time |
|------|------|
| Clarify scope | 3–4 min |
| Functional requirements | 3–4 min |
| Non-functional requirements | 2–3 min |
| Capacity estimation | 3–4 min |
| High-level architecture | 5–6 min |
| API design | 3–4 min |
| Data model | 4–5 min |
| Deep dives (2–3) | 10–12 min |
| Reliability and ops | 3–4 min |
| Security + tradeoffs + wrap | 3–4 min |

**Pace yourself.** If you're 20 min in and haven't drawn a diagram yet, you're moving too slow. If you haven't done deep dives by min 30, speed up.
