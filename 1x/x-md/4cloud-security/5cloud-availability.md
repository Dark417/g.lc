# 5cloud-availability — Regions, Zones, Availability And Reliability

- **In plain words:** a cloud region is a city of data centers, and each availability zone is a separate building with its own power and network. You stay up by spreading copies across buildings, and across cities if you need to survive losing a city.
- Part 0 is new: how regions and zones work and what each AWS service does with them
- Parts A1–A11 moved here from `5reliability-security.md` (reliability math, resilience patterns, multi-region, safe change, DR); on 2026-11-15 merged with `1sd/00.base/11.reliability.md` (timeout types, deadline propagation, retry rules, breaker knobs, bulkhead forms, fallbacks, tools, pitfalls)
- Security moved to [7security.md](7security.md); clusters (ECS, EKS) are in [6ecs.md](6ecs.md) and [6eks.md](6eks.md)

## Index

- [0. Regions, Zones, And What "Available" Means](#s0a)
  - [0.1 The failure domains](#s0a-1)
  - [0.2 Zonal, regional, global services](#s0a-2)
  - [0.3 Laying a service across three zones](#s0a-3)
  - [0.4 How managed data stores spread across zones](#s0a-4)
  - [0.5 The catches](#s0a-5)
- [0b. One-Minute Version](#s0)
- [Part A — Reliability](#h1)
- [1. Vocabulary And Math](#s1)
  - [1.1 Availability Targets](#s1-1)
  - [1.2 Composing Availability](#s1-2)
  - [1.3 Terms](#s1-3)
- [2. What Fails](#s2)
- [3. Redundancy And Failure Domains](#s3)
- [4. Resilience Patterns](#s4)
  - [4.1 Timeouts And Deadlines](#s4-1)
  - [4.2 Retries](#s4-2)
  - [4.3 Circuit Breaker](#s4-3)
  - [4.4 Bulkheads](#s4-4)
  - [4.5 Load Shedding And Admission Control](#s4-5)
  - [4.6 Graceful Degradation And Fallbacks](#s4-6)
  - [4.7 Hedged Requests](#s4-7)
  - [4.8 Composing The Patterns](#s4-8)
  - [4.9 Tools](#s4-9)
- [5. Overload And Cascading Failure](#s5)
- [6. Multi-AZ And Multi-Region](#s6)
  - [6.1 Modes](#s6-1)
  - [6.2 Failover Mechanics](#s6-2)
  - [6.3 Data Placement Choices](#s6-3)
  - [6.4 Static Stability](#s6-4)
- [7. Cell-Based Architecture](#s7)
- [8. Safe Change](#s8)
- [9. Durability, Backups, Disaster Recovery](#s9)
- [10. Observability And Incident Response](#s10)
- [11. Testing Reliability](#s11)
- [11b. Interview Pitfalls](#s11b)
- [12. Failure Modes](#s23)
- [13. Where This Fits](#s24)

---

<a id="s0a"></a>
## 0. Regions, Zones, And What "Available" Means

- **In plain words:** "available" means users get correct answers in time. In the cloud you get there by placing copies in independent failure domains, so one failure takes out only one copy.

<a id="s0a-1"></a>
### 0.1 The failure domains

| Level | What it is | Fails together because | Typical blast radius |
|---|---|---|---|
| Host / rack | One machine, one rack | Shared hardware, top-of-rack switch | A few instances |
| Availability zone (AZ) | One or more data centers with separate power, cooling, network | Shared building, power feed | Everything zonal in it |
| Region | 3+ AZs in one metro, linked by low-latency fiber | Shared control plane, regional software bugs | A whole region's services |
| Global | Services with one worldwide control plane | One config or software push | Every region |

- AWS regions have at least three AZs; AZs in a region are typically single-digit milliseconds apart (order of magnitude; AWS global infrastructure page)
- OCI names: region → availability domain (AD) → fault domain (FD); Azure and GCP use region → zone
- AZ names are per account: `us-east-1a` in your account may be a different building than in mine
  - Use AZ IDs (`use1-az1`) when coordinating across accounts

<a id="s0a-2"></a>
### 0.2 Zonal, regional, global services

- Plain idea: know which services die with one zone, which survive it on their own, and which you must spread yourself

| Scope | AWS examples | What you must do |
|---|---|---|
| Zonal | EC2 instance, EBS volume, subnet, single-AZ RDS, NAT gateway | Run copies in 2–3 AZs yourself |
| Regional, spread by AWS | S3, DynamoDB, SQS, SNS, Lambda, ALB / NLB (with subnets in several AZs), Aurora storage | Mostly nothing; give them subnets in several AZs |
| Regional, spread by you | ECS service, EKS node groups, Auto Scaling group, ElastiCache, MSK | Configure several AZs and enough capacity per AZ |
| Global | IAM, Route 53, CloudFront, Global Accelerator | Treat as dependencies; avoid them on the hot path where possible |

- The catch: one NAT gateway per VPC is a zonal single point of failure; use one per AZ

<a id="s0a-3"></a>
### 0.3 Laying a service across three zones

```text
              Route 53 / CloudFront
                      |
           ALB (subnets in AZ-a, AZ-b, AZ-c)
          /           |            \
   tasks AZ-a     tasks AZ-b     tasks AZ-c      <- stateless, N+1 per AZ
          \           |            /
   Aurora writer AZ-a, readers AZ-b / AZ-c       <- storage: 6 copies across 3 AZs
```

1. Put the load balancer in public or private subnets in three AZs
2. Spread stateless tasks or pods evenly across the AZs (ECS spread placement, K8s topology spread constraints)
3. Size for losing one AZ: with three AZs, each must carry 50% of peak, so provision 150% in total
4. Replicate state across AZs with automatic failover (Aurora, RDS Multi-AZ, ElastiCache replicas, MSK brokers per AZ)
5. Health checks at the LB remove a sick AZ's targets; zonal shift in the ALB moves traffic away deliberately

- 🗣 "Three AZs, each sized to take half of peak, so losing one zone costs no capacity; state replicates synchronously across zones."

<a id="s0a-4"></a>
### 0.4 How managed data stores spread across zones

| Store | Cross-AZ design | Failover |
|---|---|---|
| Aurora | Shared storage with 6 copies across 3 AZs; writer + readers | Reader promoted, typically under a minute (AWS docs, order of magnitude) |
| RDS Multi-AZ | Synchronous standby in another AZ | DNS flips to the standby, typically 1–2 minutes |
| DynamoDB | Replicated across 3 AZs automatically | Transparent |
| S3 Standard | Stored across ≥ 3 AZs | Transparent; One Zone-IA is the exception |
| ElastiCache Redis | Primary + replicas in other AZs, Multi-AZ enabled | Replica promoted automatically |
| MSK / Kafka | Brokers spread across AZs; replication factor 3, `min.insync.replicas=2` | Leader election per partition |

<a id="s0a-5"></a>
### 0.5 The catches

- Cross-AZ traffic is billed per GB; chatty services spread across zones cost real money
- Multi-AZ protects against a building, not a bad deploy or a regional bug: that needs safe change (section 8) and possibly multi-region (section 6)
- Autoscaling during an AZ outage is slow and capacity may be short; pre-provision (static stability, section 6.4)
- A synchronous call chain across many services multiplies failure: availability composes (section 1.2)

---

<a id="s0"></a>
## 0b. One-Minute Version

- **Reliability = expect failure, limit its blast radius, recover fast**
  - Redundancy across failure domains, timeouts + retries with jitter + circuit breakers, load shedding, safe deploys, tested backups
- **Multi-region** is a choice of RPO / RTO and cost: backup-restore → active-passive → active-active
- **Cells** cap blast radius; **static stability** keeps the data plane serving when the control plane is down
- 🗣 "Multi-AZ by default, cells to cap blast radius, active-passive across regions with a stated RPO and RTO."

---

<a id="h1"></a>
## Part A — Reliability

<a id="s1"></a>
## 1. Vocabulary And Math ★★★

<a id="s1-1"></a>
### 1.1 Availability Targets

| Availability | Downtime per year | Per 30 days |
|---|---|---|
| 99% | ~3.65 days | ~7.2 h |
| 99.9% | ~8.76 h | ~43 min |
| 99.95% | ~4.4 h | ~22 min |
| 99.99% | ~52.6 min | ~4.3 min |
| 99.999% | ~5.3 min | ~26 s |

<a id="s1-2"></a>
### 1.2 Composing Availability

- **Serial** (A calls B, both needed): A × B → 99.9% × 99.9% ≈ 99.8%
- **Parallel** (either replica works): 1 − (1 − A)² → two 99% replicas ≈ 99.99%
- Lesson: long sync call chains lower availability; redundancy raises it (only if failures are independent)

<a id="s1-3"></a>
### 1.3 Terms

- **SLI**: what you measure (success rate, p99 latency)
- **SLO**: the target (99.9% of requests succeed within 300 ms over 30 days)
- **SLA**: contractual promise with penalties (looser than the SLO)
- **Error budget**: 1 − SLO; spend it on releases, freeze when exhausted
- **MTBF / MTTR**: mean time between failures / to recover; reliability work mostly shrinks MTTR
- **RPO**: how much data you can lose (time); **RTO**: how long until service is back
- 🗣 "A 99.9% SLO gives ~43 minutes of error budget a month; when we burn it, we slow releases."

---

<a id="s2"></a>
## 2. What Fails ★★

| Failure class | Examples | Main defense |
|---|---|---|
| Hardware | Disk, host, rack, power | Redundancy across failure domains |
| Bad change | Code deploy, config push, schema migration | Canary, staged rollout, fast rollback |
| Dependency | Slow DB, third-party API down | Timeouts, circuit breakers, fallbacks |
| Overload | Traffic spike, retry storm | Load shedding, rate limits, autoscaling |
| Network | Partition, packet loss, DNS issues | Retries, multi-AZ, health checks |
| Gray failure | Node half-working, slow but "healthy" | Outlier detection, latency-based health checks |
| Correlated failure | Same bug on every node, region outage | Staged rollout, cells, multi-region |
| Human error | Wrong command, deleted data | Guardrails, two-person review, backups, soft delete |
| Data corruption | Bad write propagated to replicas | Point-in-time recovery, checksums, versioning |

- Canonical pattern: a large share of incidents start with a change (deploy or config), which is why safe change (section 8) is a reliability topic

---

<a id="s3"></a>
## 3. Redundancy And Failure Domains ★★★

- **N+1 / N+2**: enough capacity to lose 1–2 units and still meet load
- Failure domains, smallest to largest
  - Host → rack → fault domain → availability domain / zone → region
  - OCI terms: region → availability domain (AD) → fault domain (FD)
- Spread replicas across zones; quorum systems across 3 zones (lose one, keep a majority)
- Stateless tiers: spread instances across zones behind the LB
- Stateful tiers: replicate data across zones; automatic failover with fencing
- 🗣 "Three replicas across three ADs: losing one AD still leaves a quorum of two."

---

<a id="s4"></a>
## 4. Resilience Patterns ★★★

<a id="s4-1"></a>
### 4.1 Timeouts And Deadlines

- **In plain words:** a timeout is how long you're willing to wait before giving up; without one, a slow dependency quietly eats all your threads.
- Every network call has one; derive it from the caller's latency budget
- Why it matters, by Little's law (in-flight = rate × wait): at 100 RPS, a 100 ms timeout caps waiting requests at ~10; a 30 s timeout lets ~3,000 pile up
- Timeout types
  - **Connect timeout:** establishing the TCP / TLS connection; short (about 1–2 s)
  - **Read (socket) timeout:** waiting for response bytes; about 2× the dependency's p99
  - **Request (total) timeout:** the whole call including retries
- **Deadline propagation:** the request carries an absolute deadline; each hop spends part of it and passes the rest on
  → Request arrives with a 500 ms deadline  
  → API spends 50 ms, calls auth with what's left  
  → Auth hits the DB, returns at 70 ms elapsed  
  → Business call gets the remaining ~430 ms  
  ⇒ If the deadline has already passed, return 503 at once and call nothing downstream
- gRPC propagates deadlines natively through its context; for HTTP, pass a header (for example a deadline timestamp) and enforce it in middleware
- Catch: a timeout longer than the caller's own timeout is wasted work; downstream timeouts must be shorter than upstream ones

<a id="s4-2"></a>
### 4.2 Retries

- **In plain words:** try again after a short, growing, random wait, but only for errors that might go away and only for requests that are safe to repeat.
- Retry transient errors only: timeouts, connection resets, 429, 503
  - Never 400, 401, 403, 404, 409, 422: they will fail the same way again
- Only for idempotent operations (or with idempotency keys)
- Exponential backoff + **full jitter**: wait a random time between 0 and `min(cap, base × 2^attempt)`
```python
def retry(fn, attempts=5, base=0.1, cap=10.0):
    for i in range(attempts):
        try:
            return fn()
        except TransientError:
            if i == attempts - 1:
                raise
            time.sleep(random.uniform(0, min(cap, base * 2 ** i)))   # full jitter
```
- Why jitter: without it, every client retries at the same moments after an outage (a synchronized retry storm)
- **Retry budget**: retries ≤ ~10% of requests, so retries can't multiply load
- Retry at one layer, not every layer (5 layers × 3 retries = 243× amplification)
- Honor `Retry-After` from the server

<a id="s4-3"></a>
### 4.3 Circuit Breaker

- States: closed (normal) → open (fail fast after errors exceed a threshold) → half-open (probe)
- Protects the caller's threads and the struggling dependency
- Knobs: failure-rate threshold (e.g. 50%), sliding window (e.g. last 100 calls or 60 s), minimum calls before it can trip, open duration (e.g. 30 s), number of half-open probe calls, and which exceptions count as failures
- Slow calls can count as failures too (resilience4j `slowCallRateThreshold`)
- When open: fail fast with a fallback, not a hang
- Catch: one breaker per dependency (or per dependency + endpoint); a single global breaker trips healthy paths too

<a id="s4-4"></a>
### 4.4 Bulkheads

- Separate thread pools / connection pools / queues per dependency or tenant class
- One slow dependency can't exhaust all workers
- Two forms
  - **Thread-pool bulkhead:** a dedicated pool per dependency (e.g. 100 threads for user APIs, 20 for reports, 10 for batch jobs)
  - **Semaphore bulkhead:** cap concurrent calls on the caller's own threads
```python
payment_slots = threading.Semaphore(10)          # at most 10 concurrent payment calls
def charge(amount):
    if not payment_slots.acquire(timeout=0.05):
        raise Overloaded()                       # fail fast instead of queueing
    try:
        return payment_client.charge(amount)
    finally:
        payment_slots.release()
```
- At the architecture level: separate services, connection pools, queues and even cells per tenant tier

<a id="s4-5"></a>
### 4.5 Load Shedding And Admission Control

- Under overload, reject early (429 / 503) rather than queueing forever
- Prioritize: drop background / low-priority work first, keep checkout / login
- Bound queues; shed by queue age (work older than the client timeout is wasted)

<a id="s4-6"></a>
### 4.6 Graceful Degradation And Fallbacks

- **In plain words:** when a part breaks, keep the core working with less, instead of failing the whole page.
- Fallbacks
  - Stale cache: last known value beats an error for prices shown, profiles, catalogs
  - Default response: recommendations down → show top sellers
  - Static fallback content; read-only mode
- Feature shedding order under load: marketing and analytics first, then secondary features, never the core flow (checkout, login)
- Writes vs reads: accept writes into a queue and degrade reads (stale data), since a lost write hurts more than a stale read
- Fallbacks must be cheap and tested; a fallback that calls another overloaded service makes things worse

<a id="s4-7"></a>
### 4.7 Hedged Requests ★

- Send a second request if the first is slower than ~p95; take the first answer
- Cuts tail latency ("The Tail at Scale", Dean & Barroso) at a small extra load cost

<a id="s4-8"></a>
### 4.8 Composing The Patterns

- Order around one outbound call, outermost first: bulkhead → time limiter → circuit breaker → retry → the call (resilience4j's documented default decorator order is Retry ( CircuitBreaker ( RateLimiter ( TimeLimiter ( Bulkhead ( call ) ) ) ) ); the point is that each retry passes through the breaker, so an open breaker stops retries)
- Health checks: liveness ("restart me") vs readiness ("send me traffic"); readiness should fail when critical dependencies are down, liveness should not
- Idempotency keys make retries safe; outbox makes "DB write + event" safe (see [1dissys.md](1dissys.md) section 9)

<a id="s4-9"></a>
### 4.9 Tools

| Tool | Gives you | Where |
|---|---|---|
| resilience4j | Retry, circuit breaker, bulkhead, rate limiter, time limiter; Spring Boot annotations | Java services |
| Polly | The same set for .NET | .NET |
| Envoy / Istio / Linkerd | Timeouts, retries, outlier detection, circuit breaking at the proxy, no code change | Service mesh sidecars |
| AWS: ALB health checks, Route 53 failover, Auto Scaling | Remove bad targets, fail over regions (bounded by DNS TTL), replace instances | Infrastructure |
| PagerDuty / Opsgenie | Alert routing, on-call, escalation | Operations |

- 🗣 "Timeouts from the latency budget, retries with jitter under a budget, a breaker on each dependency, and shed low-priority work first."

---

<a id="s5"></a>
## 5. Overload And Cascading Failure ★★

- How cascades happen
  1. A dependency slows down
  2. Callers hold threads / connections longer → pools exhaust
  3. Callers time out → clients retry → load rises further
  4. More nodes fall over; the LB shifts load to survivors, which then fail too
- Related traps
  - Thundering herd after a restart or cache flush
  - Cache stampede on a hot key expiry
  - Metastable failure: the system stays broken even after the trigger is gone, because retries keep it overloaded
- Defenses: timeouts, retry budgets, breakers, load shedding, request coalescing, warm-up / slow start, capacity headroom
- 🗣 "The danger isn't the first failure, it's retries turning it into a cascade, so I cap retries and shed load early."

---

<a id="s6"></a>
## 6. Multi-AZ And Multi-Region ★★★

<a id="s6-1"></a>
### 6.1 Modes

| Mode | How | RPO | RTO | Cost |
|---|---|---|---|---|
| Backup + restore | Copy backups to another region | Hours | Hours | Low |
| Pilot light | Data replicated, minimal compute in standby | Minutes | Tens of minutes | Low–medium |
| Warm standby (active-passive) | Scaled-down full stack, data replicated | Seconds–minutes | Minutes | Medium |
| Active-active | All regions serve traffic | ~0 (for reads; writes depend on design) | ~0 | High; write conflicts |

<a id="s6-2"></a>
### 6.2 Failover Mechanics

1. Detect: health checks / synthetic probes from several vantage points
2. Decide: automatic for clear failures, human-approved for ambiguous ones
3. Promote the standby database (with fencing so the old primary can't write)
4. Shift traffic: DNS (bounded by TTL) or anycast / global LB
5. Failback later, deliberately, after data reconciliation

<a id="s6-3"></a>
### 6.3 Data Placement Choices

- Home region per user / tenant: writes go there; simplest correct active-active for many apps
- Global read replicas: local reads, single-region writes
- Multi-leader / CRDTs: local writes everywhere, merge conflicts
- Spanner-style global consensus: strong consistency, higher write latency
- Data residency rules may force regional data

<a id="s6-4"></a>
### 6.4 Static Stability ★★★

- The data plane keeps serving with its last known good state when the control plane or a dependency fails
- Pre-provision capacity instead of relying on autoscaling during an outage
- Example: load balancers keep routing with cached config if the config service is down
- 🗣 "The data plane is statically stable: it serves from last known good config and never calls the control plane on the request path."

---

<a id="s7"></a>
## 7. Cell-Based Architecture ★★★

- Plain idea: run many independent copies of the full stack ("cells"), each serving a slice of tenants
- How
  1. A thin **cell router** maps tenant → cell (by tenant id)
  2. Each cell has its own services, DBs, queues
  3. Deploy cell by cell (canary cell first)
  4. A bad deploy or poison tenant affects only one cell
- Sizing: cells have a max size; new tenants go to new cells
- Big tenants: dedicated cells
- **Shuffle sharding**: give each tenant a random small subset of workers; two tenants rarely share the full subset, so one bad tenant hurts few others
- The catch: cross-cell queries, tenant migration between cells, more operational units
- 🗣 "Cells cap blast radius: a bad deploy or a noisy tenant takes down one cell, not the region."

---

<a id="s8"></a>
## 8. Safe Change ★★★

- Deploy strategies

| Strategy | How | Good | Cost |
|---|---|---|---|
| Rolling | Replace instances in batches | Simple | Mixed versions during rollout |
| Blue / green | Switch traffic to a new full fleet | Instant rollback | Double capacity briefly |
| Canary | Small % of traffic first, then expand | Catches bad changes early | Needs good metrics |
| One-box / one-cell first | Single host or cell first, bake time | Small blast radius | Slower rollout |

- Bake time between stages; automatic rollback on SLO regression
- Feature flags: decouple deploy from release; kill switches
- Config changes go through the same staged pipeline as code
- Database migrations: expand-migrate-contract (4persistence.md section 10)
- 🗣 "Every change, code or config, goes one-box, then one cell, then waves, with automatic rollback on SLO burn."

---

<a id="s9"></a>
## 9. Durability, Backups, Disaster Recovery ★★

- Replication protects against hardware loss, **not** against bad writes (they replicate too)
- Backups + point-in-time recovery protect against corruption and human error
- Cross-region backup copies for regional disasters
- Object storage: versioning + object lock for ransomware / accidental delete
- Replication vs erasure coding: erasure coding stores data more cheaply at similar durability, with more CPU and slower repairs
- **Test restores** regularly; an untested backup isn't a backup
- 🗣 "Replication handles node loss; PITR backups in another region handle bad writes and regional loss, and we test restores monthly."

---

<a id="s10"></a>
## 10. Observability And Incident Response ★★

- Full treatment: [5observability.md](5observability.md)
- Golden signals: latency, traffic, errors, saturation
- SLO burn-rate alerts with two windows (fast burn pages, slow burn tickets)
- Distributed tracing across services; logs with trace ids; high-cardinality per-tenant metrics where affordable
- Incident roles: incident commander, communications, operations
- Mitigate first (roll back, fail over, shed load), diagnose later
- Blameless postmortems with tracked action items

---

<a id="s11"></a>
## 11. Testing Reliability ★

- Load tests to find the knee of the latency curve
- Chaos engineering / fault injection (kill nodes, add latency, drop a zone)
- Game days: practice failover and restore with the real runbook
- Canonical tools: Netflix Chaos Monkey (kills instances), Chaos Kong (simulates losing a region), AWS Fault Injection Service, Gremlin
- Start in staging, then small blast radius in production with a stop condition

<a id="s11b"></a>
## 11b. Interview Pitfalls ★★

- "I'll add retries" without timeouts, jitter, a budget, and an idempotency check
- No answer to "what if Redis / the DB / the payment provider is down?": always name the fallback
- "Active-active is always better": match the DR mode to RPO / RTO and budget
- Mixing up RPO (how much data you can lose) and RTO (how long you can be down)
- Alerting on CPU instead of user-facing symptoms (see [5observability.md](5observability.md))
- Retrying at every layer of a call chain

---

<a id="s23"></a>
## 12. Failure Modes

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Cascading failure | Slow dependency + retries | Rising latency across services | Timeouts, retry budgets, breakers, shedding |
| Retry storm | Every layer retries | Traffic multiplies during incidents | Retry at one layer, budgets, jitter |
| Bad config push | Global config change | Errors everywhere at once | Staged config rollout, validation, rollback |
| Regional outage | Region / AD failure | Health checks fail | Failover runbook, standby region, static stability |
| Split brain | Failover without fencing | Divergent writes | Fencing tokens, consensus election |
| Untested backup | Restore needed for the first time | Restore fails | Regular restore drills |

---

<a id="s24"></a>
## 13. Where This Fits

- Place: the deep doc behind 1sd.md sections 5.17, 7.3, 8.3; clusters in [6ecs.md](6ecs.md) and [6eks.md](6eks.md)
- Time: 1–2 days; most valuable for Oracle OCI and Amazon
- I should be able to
  - Say which AWS services are zonal, regional or global, and lay a service across three AZs
  - Do availability math and state an SLO, RPO and RTO for any design
  - Explain how a cascade happens and the four defenses that stop it
  - Choose a multi-region mode and justify it by RPO / RTO / cost
