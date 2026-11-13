# 1qs — System Design Question List

## Index

- [0. Core Concepts](#s0)
  - [0.1 Partitioning](#s0-1)
  - [0.2 Replication & quorum](#s0-2)
  - [0.3 Consensus & leader election](#s0-3)
  - [0.4 CAP / PACELC & consistency models](#s0-4)
  - [0.5 Distributed ID generation](#s0-5)
  - [0.6 Rate limiting algorithms](#s0-6)
  - [0.7 Caching strategies & eviction](#s0-7)
  - [0.8 Idempotency & delivery semantics](#s0-8)
  - [0.9 Distributed lock & fencing](#s0-9)
  - [0.10 Outbox / CDC](#s0-10)
  - [0.11 Backpressure, retry, circuit breaker](#s0-11)
  - [0.12 Probabilistic structures](#s0-12)
  - [0.13 Geo indexing](#s0-13)
  - [0.14 Windowed aggregation & top-K](#s0-14)
- [1. Core Components](#s1)
  - [1.1 Distributed cache](#s1-1)
  - [1.2 Message queue / log](#s1-2)
  - [1.3 Rate limiter (per-tenant)](#s1-3)
  - [1.4 Load balancer](#s1-4)
  - [1.5 Distributed KV store](#s1-5)
  - [1.6 Object storage](#s1-6)
  - [1.7 Distributed job scheduler](#s1-7)
  - [1.8 Unique ID service](#s1-8)
  - [1.9 Metrics / logging system](#s1-9)
  - [1.10 Config service (staged rollout)](#s1-10)
  - [1.11 Distributed lock service](#s1-11)
- [2. Product Questions By Type](#s2)
  - [2.1 Realtime messaging](#s2-1)
    - [Chat (WhatsApp)](#h1)
    - [Live comments](#h2)
    - [Notification system](#h3)
    - [Presence (online status)](#h4)
  - [2.2 Media streaming](#s2-2)
    - [YouTube](#h5)
    - [Live streaming (Twitch)](#h6)
  - [2.3 Feed & social](#s2-3)
    - [News feed](#h7)
    - [Instagram](#h8)
  - [2.4 Search & discovery](#s2-4)
    - [Typeahead / autocomplete](#h9)
    - [Web crawler](#h10)
  - [2.5 Location](#s2-5)
    - [Uber](#h11)
    - [Proximity search (Yelp)](#h12)
  - [2.6 Storage & collaboration](#s2-6)
    - [Dropbox / Google Drive](#h13)
    - [Google Docs](#h14)
  - [2.7 Transactions](#s2-7)
    - [Ticket booking (Ticketmaster)](#h15)
    - [Payment system](#h16)
    - [E-commerce checkout / inventory](#h17)
  - [2.8 Analytics & ingestion](#s2-8)
    - [Ad click aggregation](#h18)
    - [Top-K trending](#h19)
  - [2.9 Simple read-heavy](#s2-9)
    - [URL shortener](#h20)
    - [Pastebin](#h21)
  - [2.10 Cloud infra (OCI flavor)](#s2-10)
    - [Async control-plane resource API](#h22)
    - [Multi-tenant rate limiter](#h23)
    - [Health monitoring for many hosts](#h24)
    - [Config rollout](#h25)
- [3. Priority For Oracle](#s3)

---

<a id="s0"></a>
## 0. Core Concepts

- These are the "how the parts work" topics, not full design questions
- For each, be able to say: problem → mechanism (3–5 steps) → catch → 🗣

<a id="s0-1"></a>
### 0.1 Partitioning ★★★

- Consistent hashing
  - Solves: adding or removing a node moves only a small share of keys
  - Key points: hash ring, virtual nodes
- Sharding strategies
  - Range / hash / directory
  - Hot keys and resharding

<a id="s0-2"></a>
### 0.2 Replication & quorum ★★★

- Leader-follower (sync / async), multi-leader, leaderless
- Why W + R > N reads the latest write
- Problems from replication lag: read-your-writes

<a id="s0-3"></a>
### 0.3 Consensus & leader election ★★

- Raft in short: term, log replication, majority
- Lease-based leader election + fencing token

<a id="s0-4"></a>
### 0.4 CAP / PACELC & consistency models ★★★

- During a partition: C or A
- Without a partition: latency or consistency
- Strong / linearizable, eventual, read-your-writes, causal

<a id="s0-5"></a>
### 0.5 Distributed ID generation ★★

- UUID, DB auto-increment, Snowflake (timestamp + machine id + sequence)
- Clock rollback problem

<a id="s0-6"></a>
### 0.6 Rate limiting algorithms ★★★

- Token bucket, leaky bucket, fixed window, sliding window log / counter
- Distributed counting: Redis + Lua

<a id="s0-7"></a>
### 0.7 Caching strategies & eviction ★★★

- Cache-aside, read/write-through, write-behind
- LRU / LFU / TTL
- Thundering herd, cache penetration, cache avalanche

<a id="s0-8"></a>
### 0.8 Idempotency & delivery semantics ★★★

- At-most-once, at-least-once, effectively-once
- Where to store the idempotency key, and for how long

<a id="s0-9"></a>
### 0.9 Distributed lock & fencing ★★

- Problems with Redis locks (GC pauses, clocks)
- etcd / ZooKeeper lease + fencing token

<a id="s0-10"></a>
### 0.10 Outbox / CDC ★★★

- Why dual writes are wrong
- Outbox table + relay; Debezium CDC

<a id="s0-11"></a>
### 0.11 Backpressure, retry, circuit breaker ★★

- Timeouts, exponential backoff + jitter, retry budget
- Circuit breaker's three states

<a id="s0-12"></a>
### 0.12 Probabilistic structures ★

- Bloom filter: says "definitely not present"
- Count-min sketch: approximate counts, heavy hitters

<a id="s0-13"></a>
### 0.13 Geo indexing ★★

- Geohash (shared prefix = nearby area)
- Quadtree (splits by density)

<a id="s0-14"></a>
### 0.14 Windowed aggregation & top-K ★★

- Tumbling / sliding windows
- Exact top-K (heap) vs approximate (count-min + heap)

---

<a id="s1"></a>
## 1. Core Components

- These are "design the node itself" questions
- Each lists only the core requirements for now; more later

<a id="s1-1"></a>
### 1.1 Distributed cache ★★★

- Features
  - get / set / delete, TTL
  - Scale horizontally across nodes
  - Losing a node does not lose all data
- Key challenges: sharding (consistent hashing), replication, hot keys
- Uses: 0.1, 0.2, 0.7

<a id="s1-2"></a>
### 1.2 Message queue / log ★★★

- Features
  - Publish / subscribe, topic + partition
  - Consumer groups, offset management
  - Durable, replayable
- Key challenges: per-partition ordering, replica sync, consumer rebalance
- Uses: 0.2, 0.8

<a id="s1-3"></a>
### 1.3 Rate limiter (per-tenant) ★★★

- Features
  - Limit by user / tenant / API
  - Configurable rules
  - Return 429 when over the limit
- Key challenges: accuracy of distributed counting, low latency, what happens if Redis is down
- Uses: 0.6

<a id="s1-4"></a>
### 1.4 Load balancer ★★

- Features
  - L4 / L7 forwarding
  - Health checks, automatic removal
  - Multiple algorithms
- Key challenges: LB's own availability, long-lived connections, config rollout
- Uses: 0.1

<a id="s1-5"></a>
### 1.5 Distributed KV store ★★

- Features
  - put / get by key
  - Tunable consistency
  - Scale out and in
- Key challenges: partitioning, quorum, conflict resolution, node failure
- Uses: 0.1, 0.2, 0.4

<a id="s1-6"></a>
### 1.6 Object storage ★★

- Features
  - put / get large objects, bucket + key
  - Multipart upload
  - High durability
- Key challenges: separating metadata from data, replication / erasure coding
- Uses: 0.2

<a id="s1-7"></a>
### 1.7 Distributed job scheduler ★★★

- Features
  - Submit jobs (now / at a time / cron)
  - Each job runs exactly once (in effect)
  - Retries on failure, status queries
- Key challenges: scheduler availability, preventing duplicate runs, job dependencies
- Uses: 0.3, 0.8, 0.9

<a id="s1-8"></a>
### 1.8 Unique ID service ★★

- Features
  - Globally unique, roughly time-ordered
  - High QPS, low latency
- Key challenges: clock rollback, assigning machine ids
- Uses: 0.5

<a id="s1-9"></a>
### 1.9 Metrics / logging system ★★★

- Features
  - Collect large volumes of metrics / logs
  - Query and aggregate by time range
  - Alerting
- Key challenges: write volume, storage cost, downsampling
- Uses: 0.14

<a id="s1-10"></a>
### 1.10 Config service (staged rollout) ★★

- Features
  - Versioned config
  - Staged rollout, rollback
  - Clients get new config quickly
- Key challenges: consistency, push vs pull, blast radius of a bad config
- Uses: 0.3

<a id="s1-11"></a>
### 1.11 Distributed lock service ★★

- Features
  - acquire / release with a lease
  - Auto-release when the holder dies
- Key challenges: fencing, split brain
- Uses: 0.3, 0.9

---

<a id="s2"></a>
## 2. Product Questions By Type

- Each question: core features (3–5) + key challenge + patterns used (see 1.sd.md section 6)

<a id="s2-1"></a>
### 2.1 Realtime messaging

<a id="h1"></a>
#### Chat (WhatsApp) ★★★

- Features
  - 1:1 messages with sent / delivered / read status
  - Group chat
  - Offline messages delivered on reconnect
  - Message history
- Key challenges: routing to long-lived connections, ordering, offline storage
- Patterns: realtime fan-out, write-heavy

<a id="h2"></a>
#### Live comments ★★★ (the question I failed last time)

- Features
  - Post a comment on a live stream / video
  - All viewers see it in real time
  - New viewers see recent comments
- Key challenges: fan-out for hot streams, SSE vs WebSocket, push rate
- Patterns: realtime fan-out

<a id="h3"></a>
#### Notification system ★★★

- Features
  - Multiple channels: push, email, SMS
  - User preferences, unsubscribe
  - Reliable delivery with retries
- Key challenges: third-party failures, dedup, rate limits
- Patterns: async job

<a id="h4"></a>
#### Presence (online status) ★★

- Features
  - Show friends online / offline
  - Last seen time
- Key challenges: heartbeat scale, fanning out status changes
- Patterns: realtime fan-out

<a id="s2-2"></a>
### 2.2 Media streaming

<a id="h5"></a>
#### YouTube ★★

- Features
  - Upload video
  - Transcode into multiple bitrates
  - Playback (adaptive bitrate)
  - View counts
- Key challenges: transcoding pipeline, CDN, large uploads
- Patterns: media pipeline

<a id="h6"></a>
#### Live streaming (Twitch) ★

- Features
  - Streamer pushes a live stream
  - Low-latency distribution to many viewers
  - Chat (see live comments)
- Key challenges: latency vs scale, live transcoding
- Patterns: media pipeline, realtime fan-out

<a id="s2-3"></a>
### 2.3 Feed & social

<a id="h7"></a>
#### News feed ★★★

- Features
  - Create posts
  - See posts from people you follow, by time / ranking
  - Pagination
- Key challenges: fan-out on write vs on read, celebrity problem
- Patterns: read-heavy, async job

<a id="h8"></a>
#### Instagram ★★

- Features
  - Upload photos
  - Feed
  - Likes, comments
- Key challenges: image storage + CDN, feed generation
- Patterns: media pipeline, read-heavy

<a id="s2-4"></a>
### 2.4 Search & discovery

<a id="h9"></a>
#### Typeahead / autocomplete ★★

- Features
  - Return top suggestions for a prefix
  - Low latency
  - Ranked by popularity
- Key challenges: trie and updates, caching
- Patterns: read-heavy, derived view

<a id="h10"></a>
#### Web crawler ★★

- Features
  - Crawl from seed URLs
  - Dedup
  - Politeness (per-domain rate limits)
- Key challenges: URL frontier, dedup at scale, DNS
- Patterns: async job, write-heavy

<a id="s2-5"></a>
### 2.5 Location

<a id="h11"></a>
#### Uber ★★

- Features
  - Drivers report location
  - Riders request a ride and get matched to a nearby driver
  - Trip state
- Key challenges: high-frequency location writes, nearby queries, matching consistency
- Patterns: write-heavy, geo index

<a id="h12"></a>
#### Proximity search (Yelp) ★★

- Features
  - Search nearby businesses
  - Sort by distance / rating
- Key challenges: geo index, read-heavy
- Patterns: read-heavy

<a id="s2-6"></a>
### 2.6 Storage & collaboration

<a id="h13"></a>
#### Dropbox / Google Drive ★★

- Features
  - Upload / download files
  - Sync across devices
  - Sharing
- Key challenges: chunking, incremental sync, conflicts
- Patterns: media pipeline (upload), async job

<a id="h14"></a>
#### Google Docs ★

- Features
  - Many users edit at once
  - See others' edits in real time
- Key challenges: OT / CRDT, merging conflicts
- Patterns: realtime fan-out

<a id="s2-7"></a>
### 2.7 Transactions

<a id="h15"></a>
#### Ticket booking (Ticketmaster) ★★★

- Features
  - Browse events
  - Pick a seat and hold it for a while
  - Confirm with payment
- Key challenges: no overselling, burst traffic at on-sale time
- Patterns: rate limit, async job

<a id="h16"></a>
#### Payment system ★★

- Features
  - Start a payment
  - Integrate with third-party PSPs
  - Reconciliation
- Key challenges: idempotency, exactly-once effect, state machine
- Patterns: async job, outbox

<a id="h17"></a>
#### E-commerce checkout / inventory ★★

- Features
  - Shopping cart
  - Place order and decrement inventory
  - Order status
- Key challenges: inventory consistency, distributed transactions (saga)
- Patterns: outbox, async job

<a id="s2-8"></a>
### 2.8 Analytics & ingestion

<a id="h18"></a>
#### Ad click aggregation ★★★

- Features
  - Ingest click events
  - Aggregate clicks per ad per minute
  - Query
- Key challenges: high write rate, dedup, windowed aggregation, late data
- Patterns: write-heavy ingestion

<a id="h19"></a>
#### Top-K trending ★★

- Features
  - Real-time top-K (topics / videos)
  - Per time window
- Key challenges: approximate counting, sliding windows
- Patterns: write-heavy ingestion

<a id="s2-9"></a>
### 2.9 Simple read-heavy

<a id="h20"></a>
#### URL shortener ★★ (warm-up)

- Features
  - Long URL → short URL
  - Redirect short URL
  - Optional: expiry, stats
- Key challenges: ID generation, read-heavy caching
- Patterns: read-heavy

<a id="h21"></a>
#### Pastebin ★

- Features
  - Store text, return a link
  - Expiry
- Key challenges: large text in object storage
- Patterns: read-heavy

<a id="s2-10"></a>
### 2.10 Cloud infra (OCI flavor)

<a id="h22"></a>
#### Async control-plane resource API ★★★

- Features
  - Create / update / delete resources, return a work request id immediately
  - Query work request status
  - Retries, idempotency
- Key challenges: state machine, long-running tasks, idempotency tokens
- Patterns: async job

<a id="h23"></a>
#### Multi-tenant rate limiter ★★★

- See 1.3, plus
  - Per-tenant quota
  - Fairness: one tenant can't starve others

<a id="h24"></a>
#### Health monitoring for many hosts ★★

- Features
  - Many hosts report heartbeats / metrics
  - Detect lost hosts
  - Alerting
- Key challenges: heartbeat scale, false alarms
- Patterns: write-heavy ingestion

<a id="h25"></a>
#### Config rollout ★★

- See 1.10

---

<a id="s3"></a>
## 3. Priority For Oracle

- Basis: I failed on live comments; OCI reports most often show scheduler, rate limiter, notification, ingestion

| Priority | Question | Section |
|---|---|---|
| P0 | Live comments | 2.1 |
| P0 | Rate limiter (per-tenant) | 1.3 / 2.10 |
| P0 | Distributed job scheduler | 1.7 |
| P0 | Async control-plane resource API | 2.10 |
| P0 | Notification system | 2.1 |
| P0 | Metrics / ingestion (same shape as ad click) | 1.9 / 2.8 |
| P1 | Chat, news feed, ticket booking, distributed cache | 2.1 / 2.3 / 2.7 / 1.1 |
| P2 | Everything else | — |

- Suggested order
  - First 0.6, 0.7, 0.8, 0.10 (all P0 questions depend on them)
  - Then one P0 question per day, in table order
