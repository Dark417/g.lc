# 3storage-by-question — What Goes Where: CDN, Blob, SQL, NoSQL, Cache, Specialized

## Index

- [0. One-Minute Version](#s0)
- [1. What Each Store Holds (High Level)](#s1)
  - [1.1 The Six Families](#s1-1)
  - [1.2 Comparison Table](#s1-2)
  - [1.3 How To Decide (Flow)](#s1-3)
- [2. Storage In Every Hello Interview Question](#s2)
  - [2.1 Legend](#s2-1)
  - [2.2 hi01–hi08](#s2-2)
  - [2.3 hi09–hi16](#s2-3)
- [3. Patterns Across The Table](#s3)
- [4. Interview Lines](#s4)
- [5. Further Thinking](#s5)
- [6. References](#s6)

---

<a id="s0"></a>
## 0. One-Minute Version

- Bytes and metadata never live in the same store
  - Large bytes (video, files, photos, raw logs) live in **blob storage**
  - Facts about them (owner, status, link) live in a **database**
- The database family follows the access pattern
  - Needs transactions or joins: **relational**
  - Huge volume, one-key lookups: **NoSQL key-value / wide-column**
- Speed comes from copies
  - **Cache** = an in-memory copy near the service
  - **CDN** = a copy near the user
- Odd query shapes get a **specialized** store
  - Full-text search, geo, analytics rollups, time windows
- 🗣 "Bytes in S3, facts in a database, hot copies in Redis and the CDN, special queries in a special index."

---

<a id="s1"></a>
## 1. What Each Store Holds (High Level)

<a id="s1-1"></a>
### 1.1 The Six Families

- **CDN** (CloudFront, Cloud CDN, Akamai)
  - Holds
    - Static assets (JS, CSS, images)
    - Media chunks (video segments, manifests)
    - Short-lived API responses that many users share (search results, top-K)
  - Why
    - Copies sit in edge servers near users
    - Cuts round-trip time and origin load
  - Not for
    - Per-user private or fast-changing data
    - Anything that must be fresh to the second
- **Blob / object storage** (S3, GCS, Azure Blob, OCI Object Storage)
  - Holds
    - Large immutable bytes: uploads, photos, video, raw HTML, raw event archives, backups
  - Why
    - Cheap per GB
    - Effectively unlimited size
    - Very durable (S3 is designed for 11 nines of durability, per AWS docs)
    - Clients can upload directly with pre-signed URLs
  - Not for
    - Querying by field
    - Small, frequent updates
- **Relational** (Postgres, MySQL, Aurora)
  - Holds
    - Entities with relationships and invariants
    - Bookings, payments, users, anything where "two writes must both happen or neither"
  - Why
    - ACID transactions
    - Joins
    - Constraints (unique, foreign key)
    - Secondary indexes
  - Not for
    - Write rates far past one primary without sharding work
    - Unbounded fan-out writes
- **NoSQL key-value / wide-column / document** (DynamoDB, Cassandra, MongoDB)
  - Holds
    - Huge, simple-access data: messages, swipes, posts by id, file metadata, feeds
  - Why
    - Partitioned by key from day one
    - Scales writes horizontally
    - Predictable single-digit-ms point reads
  - Not for
    - Ad-hoc queries or joins
    - Multi-row transactions at scale
      - DynamoDB transactions exist, but are capped at 100 items (AWS docs)
- **Cache / in-memory** (Redis, Memcached)
  - Holds
    - Hot read copies (url → longUrl, post bodies, leaderboards)
    - Short-lived state: locks with TTL, dedupe sets, rate-limit buckets, driver locations
  - Why
    - Memory reads in sub-ms
    - Atomic operations: `INCR`, `SET NX PX`, sorted sets, Lua scripts
  - Not for
    - The only copy of data you can't lose
      - Async replication can drop recent writes on failover
- **Specialized**
  - Search index (Elasticsearch / OpenSearch): full-text and filters, usually fed by CDC
  - OLAP (ClickHouse, Druid, Pinot, BigQuery): pre-aggregated analytics, time ranges
  - Geo (Redis GEO, PostGIS, H3 cells): nearby queries
  - Stream state (Flink): running windows before results land in a DB
  - Coordination (ZooKeeper / etcd): small config, membership, watches

<a id="s1-2"></a>
### 1.2 Comparison Table

| Option | What it is | Strength | Weakness | Choose when |
|---|---|---|---|---|
| CDN | Edge copies near users | Lowest user latency; shields origin | Stale until TTL or purge; costs per GB served | Many users read the same bytes |
| Blob (S3) | Object store by key | Cheap, huge, durable; direct upload | No field queries; whole-object writes | Anything big or raw |
| Relational | Tables + ACID | Transactions, joins, constraints | One-primary write ceiling | Correctness across rows matters |
| NoSQL KV / wide-column | Partitioned by key | Horizontal writes, steady latency | Access patterns fixed up front | Huge volume, known key lookups |
| Cache (Redis) | In-memory structures | Sub-ms, atomic ops, TTL | Memory cost; loss on failover | Hot reads, short-lived state |
| Specialized | Search, OLAP, geo, stream | Query shapes others can't do | Extra copy to keep in sync | Search, analytics, nearby, windows |

- Default: relational for core entities, plus blob for bytes and Redis for hot paths
  - Unless the write volume or simple key access says NoSQL

<a id="s1-3"></a>
### 1.3 How To Decide (Flow)

→ Is it large bytes (over ~1 MB, media, files, raw logs)?  
⇒ Blob storage; keep only the link and metadata in a database.

→ Do many users read the same bytes or response?  
⇒ Put a CDN in front, with a TTL that matches how stale it may be.

→ Must two or more writes succeed together, or does a constraint guard money or inventory?  
⇒ Relational, or a NoSQL store with conditional writes.

→ Is it huge volume, with reads and writes by one key?  
⇒ NoSQL key-value or wide-column, partitioned by that key.

→ Is it read far more than written, or short-lived with a TTL?  
⇒ Redis in front, with the database as the source of truth.

→ Is the query full-text, nearby, an analytics rollup, or a time window?  
⇒ A specialized index, fed from the source of truth (CDC or stream).

---

<a id="s2"></a>
## 2. Storage In Every Hello Interview Question

<a id="s2-1"></a>
### 2.1 Legend

- **V:** what the video / write-up uses
- **Alt:** a reasonable swap
- **Me:** not in the video; I'd add it
- ★★★ = must use this family here; the design breaks without it
- `-` = not needed

<a id="s2-2"></a>
### 2.2 hi01–hi08

| Question | CDN | Blob (S3) | Relational | NoSQL | Cache (Redis) | Specialized |
|---|---|---|---|---|---|---|
| hi01 Ticketmaster | **V:** search API cache 30–60 s; static images | **Me:** event images, venue maps | ★★★ **V:** Postgres events, tickets, bookings; ACID stops double sale | **Alt:** DynamoDB with conditional writes / transactions | ★★★ **V:** seat hold lock with TTL; sorted-set waiting queue | **V:** Elasticsearch event search via CDC. **Alt:** Postgres full-text at small scale |
| hi02 Rate limiter | **Me:** edge/WAF limits for DDoS | - | **Me:** rules source of truth | - | ★★★ **V:** Redis Cluster token buckets, one Lua script per check | **V:** ZooKeeper / etcd to push rules |
| hi03 Bitly | **V:** skipped to keep 302 visibility. **Me:** CDN with short TTL | **V:** DB snapshots only | **V:** Postgres, PK = short code, 500 GB single node | **Alt:** DynamoDB; pure key lookup fits KV perfectly | ★★★ **V:** read-through LRU code → longUrl (reads ≫ writes); `INCR` counter. **Me:** durable sequence instead of Redis counter | - |
| hi04 Uber | - | **Me:** trip location trails | **Alt:** Postgres for the ride state machine | **V:** DynamoDB rides, drivers, driver lock. **Me:** lock via conditional write, not TTL | ★★★ **V:** Redis GEO driver locations (~600K writes/s). **Me:** `SET NX PX` offer lock | **Alt:** PostGIS (low write rate), H3 cells |
| hi05 Dropbox | **V:** opted out; users fetch own files near the DC. **Alt:** popular shared files | ★★★ **V:** S3 chunks, pre-signed multipart upload/download | **Alt:** Postgres if sharing / ACLs grow | **V:** DynamoDB file metadata with chunk list | - | **V:** client local DB for sync state; event log with cursor rejected as overkill |
| hi06 WhatsApp | **Me:** popular group media | ★★★ **V:** S3 media via pre-signed URLs | - | ★★★ **V:** DynamoDB Message, Inbox, Chat, ChatParticipant (GSI). **Alt:** Cassandra by chatId | **V:** Redis pub/sub per user (routing, not storage); user → socket map | **Alt:** ZooKeeper / etcd hash ring registry |
| hi07 Ad click aggregator | - | ★★★ **V:** S3 raw clicks for daily reconciliation | **V:** Ads DB (ad metadata) | **V:** Cassandra click DB in the early version, later dropped | ★★★ **V:** impression-ID dedupe set with TTL | ★★★ **V:** OLAP per ad per minute, sharded by advertiser; Flink window state |
| hi08 Live comments | - | - | - | ★★★ **V:** Cassandra, partition videoId, sort createdAt. **Alt:** DynamoDB same keys | **V:** recent-comment cache; pub/sub channels | **Alt:** ZooKeeper server/video registry |

<a id="s2-3"></a>
### 2.3 hi09–hi16

| Question | CDN | Blob (S3) | Relational | NoSQL | Cache (Redis) | Specialized |
|---|---|---|---|---|---|---|
| hi09 Twitter | **V:** media and static | **V:** S3 tweet media | **V:** SQL users / profiles | **V:** MongoDB tweets; replies DB indexed by tweetId. **Alt:** DynamoDB / Cassandra by tweetId | ★★★ **V:** precomputed home timelines + tweet cache | **V:** Elasticsearch via CDC; graph DB for followers. **Me:** a KV adjacency table is enough |
| hi10 YouTube | ★★★ **V:** popular segments + manifests | ★★★ **V:** originals (multipart), transcoded segments, manifests | **V:** Postgres metadata (status, manifest URL) | **Alt:** DynamoDB / Cassandra at metadata scale | **Me:** hot video metadata | - |
| hi11 Web crawler | - | ★★★ **V:** raw HTML + extracted text; parse stage replays from it | - | **V:** DynamoDB URL (PK url, hash GSI) and Domain (robots) tables | **V:** per-domain rate limit; DNS cache | **Alt:** Bloom filter for seen URLs |
| hi12 LeetCode | **Me:** static problem pages | **V:** large code / test files, if any | **V:** Postgres or DynamoDB; "doesn't matter" at 100K DAU | **Alt:** same | ★★★ **V:** sorted-set leaderboard, updated via CDC | - |
| hi13 Tinder | **Me:** profile photos | **Me:** S3 photos | **V:** Postgres + PostGIS profiles | ★★★ **V:** Cassandra swipes (huge write volume) | ★★★ **V:** atomic match check; precomputed stacks | **V:** Elasticsearch geo + filters via CDC; Bloom filter to avoid re-shows |
| hi14 FB news feed | **Me:** media | **Me:** post media | - | ★★★ **V:** DynamoDB Posts, Follow (+ reversed GSI), precomputed feed (200 IDs/user) | ★★★ **V:** redundant hot-post caches (random replica pick) | **V:** graph DB considered. **Me:** KV adjacency is enough |
| hi15 Top-K videos | **Me:** top-K responses are identical for all, so short TTL | **Me:** raw view archive | **V:** Postgres views by window, sharded by videoId. **Alt:** OLAP fits time windows better | - | ★★★ **V:** cached top-K from hourly cron | ★★★ **V:** Flink windows + checkpoints. **Alt:** count-min sketch + heap |
| hi16 FB post search | **V:** 1-min cache of results | **V:** cold index for long-tail keywords | **V:** Posts DB, Likes DB | **Alt:** posts / likes in KV | ★★★ **V:** Redis Cluster inverted index (sorted sets by likes and time); like counts | **Alt:** Elasticsearch for general full-text; count-min sketch for bigram thresholds |

---

<a id="s3"></a>
## 3. Patterns Across The Table

| Pattern | Questions | Store |
|---|---|---|
| Big bytes uploaded directly | Dropbox, WhatsApp, YouTube, crawler | Blob + pre-signed URL |
| Correctness under contention | Ticketmaster, Uber, Tinder | Relational transaction, conditional write, or atomic Redis op |
| Write-heavy, one-key access | WhatsApp, live comments, Tinder swipes, news feed | Cassandra / DynamoDB |
| Read-heavy hot set | Bitly, Twitter, news feed, top-K, post search | Redis in front |
| Same response for everyone | Ticketmaster search, top-K, post search, YouTube segments | CDN |
| Odd query shape | Ticketmaster, Twitter, Tinder, ad click, Uber | Elasticsearch, OLAP, geo index |

- Cache is ★★★ in 12 of 16 questions
  - Almost every design needs one hot path in memory
- Blob is ★★★ whenever users send big bytes
- Relational is ★★★ only where a transaction guards money or inventory (Ticketmaster)
  - Elsewhere it's a choice, not a must

---

<a id="s4"></a>
## 4. Interview Lines

- 🗣 "The bytes go to S3 with a pre-signed URL; the database keeps only metadata and the link."
- 🗣 "I pick the database by access pattern: transactions mean Postgres, huge key-based volume means DynamoDB or Cassandra."
- 🗣 "Redis is a copy or short-lived state, never the only copy of something we can't lose."
- 🗣 "Search and analytics get their own index, fed by CDC from the source of truth."
- 🗣 "I'd only add a CDN where many users read the same thing; private data doesn't benefit."

---

<a id="s5"></a>
## 5. Further Thinking

- Every extra store is a sync problem
  - CDC lag means search shows stale results for seconds
  - Say how long, and whether the product accepts it
- Cache invalidation has three tools
  - TTL
  - Delete on write
  - Version in the key
  - Name which one you use and why
- Hot keys hurt every family
  - Redis shard, DynamoDB partition, Cassandra partition
  - Fixes: key suffix spreading, local caches, replicated hot copies (news feed)
- L5 adds
  - Cost: CDN egress, Redis memory, OLAP storage
  - Retention: TTLs and archive tiers (S3 Glacier)
  - Multi-region: which store replicates how, and what that does to consistency

---

<a id="s6"></a>
## 6. References

- [Hello Interview: system design problem breakdowns](https://www.hellointerview.com/learn/system-design/problem-breakdowns/overview)
- [Amazon S3 durability (11 nines)](https://docs.aws.amazon.com/AmazonS3/latest/userguide/DataDurability.html)
- [DynamoDB transactions (100-item limit)](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/transaction-apis.html)
- [Redis data types (sorted sets, GEO)](https://redis.io/docs/latest/develop/data-types/)
- Local sources: `1sd/hello-interview/hi01`–`hi16` raw docs
