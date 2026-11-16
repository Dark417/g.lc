# Load Balancing & API Gateway

## INDEX

1. [API Gateway Anatomy](#1-api-gateway-anatomy)
   - 1.1 What runs at the gateway
   - 1.2 Concept vs product: Spring Cloud Gateway vs AWS API Gateway
   - 1.3 Where gateway state lives — and why the route table is "state"
   - 1.4 The gateway is itself a replicated, load-balanced fleet
   - 1.5 Build-vs-configure matrix per function
2. [Routing Hierarchy](#2-routing-hierarchy)
   - 2.1 The five routing decisions
   - 2.2 DNS knows hostnames, never paths
   - 2.3 Host-based vs path-based routing (pattern names)
   - 2.4 How google.com / maps.google.com actually resolve
   - 2.5 Request lifecycle end-to-end (numbered)
3. [Load Balancer Fundamentals](#3-load-balancer-fundamentals)
   - 3.1 What it is, and what breaks without it
   - 3.2 Types: by deployment and by layer (L4 / L7 / GSLB)
   - 3.3 Algorithms
   - 3.4 Health checking
   - 3.5 Sticky sessions (session persistence)
   - 3.6 The LB as its own SPOF: active-active vs active-passive
   - 3.7 Connection draining & autoscaling integration
   - 3.8 Interview pop-ups
4. [References](#4-references)

---

## 1. API Gateway Anatomy

### 1.1 What runs at the gateway

```
Client ──► [ Edge LB (L4) ] ──► [ API Gateway (L7) ] ──► services...
              TCP/TLS               HTTP-aware
```

The gateway is an **L7 reverse proxy with policy enforcement bolted on**. Request hits these in order:

- **TLS termination** — decrypt once at the edge so internal hops use mTLS or plaintext-in-VPC.
  → Defeater: gateway now sees plaintext; zero-trust setups re-encrypt (mTLS) to backends.
- **Routing** — host + path + header → backend service mapping. This is dispatch, not balancing.
- **AuthN** — JWT signature validation (stateless, JWKS cached in memory) or API-key/opaque-token lookup (stateful, see 1.3).
- **AuthZ (coarse)** — "does this client tier get this route at all." Fine-grained authZ (row/document-level, e.g. ABAC on document types) stays in the service — the gateway doesn't know domain objects.
- **Rate limiting / quotas** — token bucket per key / IP / tenant.
- **Request validation & shaping** — size limits, header normalization, protocol translation (HTTP↔gRPC).
- **Resilience policy** — per-upstream timeouts, retries with budget, circuit breakers.
- **Observability** — access logs, trace-ID injection (traces usually _start_ here), per-route metrics.
- **Instance-level LB** — after routing picks _which service_, gateway or mesh picks _which instance_.

🗣 "The gateway does cross-cutting concerns identical for every service — anything requiring domain knowledge stays in the service."

The gateway does **not** implement any endpoint. After policy checks pass, it **proxies** the request to the internal service that owns the endpoint, streams the response back, and applies response-side policy (headers, logging). The service implements the business logic; the gateway forwards.

### 1.2 Concept vs product: Spring Cloud Gateway vs AWS API Gateway

```
        "API Gateway" (role / pattern)
              /                \
   Self-hosted app          Fully managed
   you deploy & run         provider runs the fleet
   ─ Spring Cloud Gateway   ─ AWS API Gateway
   ─ Envoy / Kong / NGINX   ─ GCP API Gateway / Apigee
   ─ Zuul (legacy)          ─ Azure API Management
```

- "API Gateway" is a **role**, not one product. Two implementation classes:
  → **Self-hosted**: a normal application you build, containerize, and deploy. **Spring Cloud Gateway (SCG)** is literally a Spring Boot app (Netty-based, reactive) — you add the dependency, declare routes, deploy to ECS/EKS like any service.
  → **Managed**: AWS API Gateway is a multi-tenant service — you define routes/authorizers/limits as config (Terraform, OpenAPI import, console), AWS runs the actual proxy fleet. You never see an instance.
  ◆ Deciding variable: control + cost-at-scale vs zero ops. Managed APIGW gets expensive at high request volume and constrains you (29 s integration timeout, payload limits); self-hosted costs you the fleet's ops burden.
- **AWS API Gateway configuration model** (HTTP API flavor):
  → Routes: `ANY /orders/{proxy+}` → integration.
  → Integrations: Lambda, ALB/NLB via **VPC Link** (private services), or plain HTTP endpoint.
  → Authorizers: JWT authorizer (issuer + audience config — no code) or Lambda authorizer (custom code).
  → Throttling: stage-level and per-route rate/burst; usage plans + API keys (REST API flavor).
  → All of it deployable as Terraform/CloudFormation/OpenAPI — the "route table" is your IaC.

### 1.3 Where gateway state lives — and why the route table is "state"

Key distinction: **config state vs runtime state vs request state**.

| State                      | Kind             | Storage                                                                                                                    | Why there                                                |
| -------------------------- | ---------------- | -------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| Route table, policies      | Config state     | Process **memory**, pushed by control plane (Envoy xDS, SCG `application.yml`/config server, AWS's internal control plane) | Read on every request → must be local, zero network hops |
| JWT public keys (JWKS)     | Config-ish cache | In-memory, TTL refresh                                                                                                     | Signature check becomes CPU-only                         |
| API keys / client metadata | Runtime state    | Redis or DynamoDB, fronted by local cache                                                                                  | Too many to ship as config; needs fast revocation        |
| Rate-limit counters        | Runtime state    | **Redis** (or local buckets + async sync)                                                                                  | Atomic increments shared across gateway replicas         |
| Per-request data           | Request state    | None persisted                                                                                                             | Gateway is stateless per request                         |

- **Why call the route table "state" at all?** Because it is data the process holds that determines behavior, changes at runtime, and must converge across replicas.
  → It is _configuration_ state, not _data_ state: versioned, pushed top-down, identical on every node. No replica ever writes to it.
  → The practical consequence: during a config rollout, two gateway replicas can briefly hold different route tables → a request can route differently depending on which replica the L4 LB picked. Control planes version configs and roll them out gradually for exactly this reason.
  → How it's configured: SCG via YAML route definitions or a `RouteDefinitionLocator` (can be backed by a DB/config server, refreshable via actuator); Envoy via xDS APIs from a control plane (Istio, AWS App Mesh); AWS APIGW via your IaC → AWS's own control plane distributes it to their edge fleet.
- Defeater on rate limiting: exact global counting needs a shared Redis hop per request; most large systems accept **approximate** limiting (local buckets, async sync). If Redis dies: **fail-open** on rate limiting (availability > perfect quotas), **fail-closed** on authN.

### 1.4 The gateway is itself a replicated, load-balanced fleet

```
            DNS
             │
        [ NLB (L4) ]            [control plane]
        /    |    \                   │ pushes config
   [GW-1] [GW-2] [GW-3]  ◄────────────┘
   (stateless replicas, multi-AZ, autoscaled)
```

- Yes — all those functions live in **one service binary**, and that service runs as **N identical stateless replicas** behind an L4 load balancer, spread across AZs, autoscaled on CPU/RPS.
  → This works _because_ the gateway externalizes everything: config is pushed in, counters live in Redis, no request state is kept. Any replica can serve any request.
  → It is not "crazy" — it's the same shape as any stateless microservice fleet. The gateway is special only in that _everything_ flows through it, so it's sized generously and treated as tier-0.
  → For managed AWS APIGW, this fleet exists too — AWS just runs it, multi-tenant, invisible to you.
- Defeater: "stateless" holds only if you keep it so. Teams that sneak per-session data or in-process-only rate buckets into the gateway break replica interchangeability and get inconsistent behavior across nodes.

### 1.5 Build-vs-configure matrix per function

For a Spring Cloud Gateway deployment vs managed AWS API Gateway:

| Function                | Spring Cloud Gateway                                               | AWS API Gateway                                   | Manual code ever?         |
| ----------------------- | ------------------------------------------------------------------ | ------------------------------------------------- | ------------------------- |
| TLS termination         | Config (Netty SSL) — or offload to ALB/NLB + ACM cert              | Managed (ACM cert attach)                         | No                        |
| Routing / route table   | Config: route predicates (`Path=/orders/**`, `Host=...`) + filters | Config: routes + integrations (Terraform/OpenAPI) | No                        |
| AuthN (JWT)             | Spring Security OAuth2 Resource Server — config + issuer URI       | JWT authorizer — config                           | Custom claim rules only   |
| AuthN (opaque/API key)  | Filter + Redis lookup — small custom filter                        | API keys + usage plans — config                   | Sometimes                 |
| AuthZ (fine-grained)    | Not here — in the service                                          | Lambda authorizer — **code**                      | Yes, by design            |
| Rate limiting           | `RequestRateLimiter` filter + Redis — config                       | Stage/route throttling — config                   | Custom key-resolvers only |
| Circuit breaker / retry | Resilience4j filter, Retry filter — config                         | Not built in — handle in client/service           | —                         |
| Request transform       | Built-in + custom `GatewayFilter`                                  | Mapping templates (VTL) / parameter mapping       | Occasionally              |
| Observability           | Micrometer + tracing — config                                      | CloudWatch built-in                               | No                        |

🗣 Bottom line: in 2026 you **configure** a gateway; you almost never hand-write TLS, routing, or rate limiting. Custom code appears only at authZ logic and exotic transforms.

---

## 2. Routing Hierarchy

### 2.1 The five routing decisions

```
DNS / Anycast          [global]   → which region/POP        (by geography/latency)
   │
L4 LB (NLB/Maglev)     [edge]     → which GATEWAY instance  (by connection)
   │
API Gateway / L7       [routing]  → which SERVICE           (by host + path)
   │
Mesh / client-side LB  [cluster]  → which INSTANCE          (by load)
   │
App-level dispatch     [data]     → which SHARD/PARTITION   (by key)
```

🗣 "Routing decides _which service_; load balancing decides _which instance_; sharding decides _which partition_. Three different decisions, all called 'load balancing' loosely."

- Instance selection at Google/Meta scale is usually **client-side** (gRPC + xDS, Meta ServiceRouter): the calling service's RPC library gets the endpoint list from discovery and balances itself — removes a proxy hop from the hot path.
  → Defeater on least-request at cluster level: with thousands of clients each seeing a sliver of traffic, naive least-request degrades toward random — hence **power-of-two-choices** as the standard.
- The last layer (key-based dispatch: Kafka partition, DynamoDB partition, cache shard) balances by **data key, not load** — that's where hot-partition problems live, a different failure mode from instance LB entirely.

### 2.2 DNS knows hostnames, never paths

```
DNS:   maps.google.com  → A/AAAA records → edge IPs     ✔ hostname granularity
DNS:   google.com/maps  →  ✘ impossible — DNS has no concept of a path
```

- **Paths are not registered in DNS. Ever.** DNS resolves a hostname to IPs; the path is inside the HTTP request, which DNS never sees.
  → Different **subdomains** (`maps.google.com` vs `www.google.com`) _are_ different DNS entries and _can_ point at completely different edge fleets. That's **host-based** splitting, done at DNS + edge.
  → Different **paths** under one hostname (`google.com/maps` vs `google.com/search`) are invisible until the L7 gateway reads the request line. That's **path-based** splitting, done at the gateway.
- **Prefix routes, not per-endpoint entries:** one route entry `/api/orders/**` → orders service. It is **one entry** covering all child paths, whatever their depth.
  → All endpoints under that prefix are handlers **inside that one service** (its controllers). You don't enumerate children in the route table; the service's own framework routing (Spring `@RequestMapping`) does the final endpoint dispatch.
  → Yes — "1 path prefix → 1 service" is the exact operational grain. Longest-prefix-match resolves overlaps (`/api/orders/reports/**` can override `/api/orders/**` to a different service if needed).

### 2.3 Host-based vs path-based routing (pattern names)

- The umbrella pattern is the **Gateway Routing pattern** (single entry point routing to multiple backends). Its two mechanisms:
  → **Host-based routing** — route by `Host` header / subdomain. Split happens as early as DNS.
  → **Path-based routing** (a.k.a. prefix routing) — route by URL path at the L7 layer.
  ◆ Related names you'll hear: "single-domain, path-routed microservices," and it's the enabling mechanism for the **Strangler Fig** migration pattern (carve paths off a monolith one prefix at a time).
- Deciding variable between them: host-based lets you split _infrastructure_ early (different certs, different edge, different scaling) but costs you CORS/cookie-scope friction across subdomains; path-based keeps one origin (simpler browser semantics) but everything shares the same edge fleet. Default: path-based within a product, host-based between products.

### 2.4 How google.com / maps.google.com actually resolve

- Your instinct ("completely different gateway per subdomain") is _possible_ but not what Google does. Both hostnames resolve to the **same shared edge fleet — GFE (Google Front End)**.
  → GFE terminates TLS, does DDoS protection, then its routing config maps (host, path) → the correct backend service fleet on Borg. The fan-out to totally different product backends happens _inside_ GFE config, not by giving each product its own edge.
  → Why shared edge: TLS termination, DDoS absorption, and global anycast presence are expensive to build — you build them once and multiplex every product through them.
- So the accurate model: **shared domain(s) + shared edge + per-product backend fleets, wired by routing config.** Not "one server per endpoint" — the unit is a _service fleet_ per bounded capability (hundreds of identical autoscaled containers). A new fleet appears when scaling profile, ownership, or data domain diverges — standard microservice boundary logic.

### 2.5 Request lifecycle end-to-end (numbered)

1. **Client resolves DNS** — geo/latency-based DNS (or anycast) returns edge IPs for the nearest region/POP. Waits on: nothing (cached by TTL). Failure: stale TTL sends you to a dead region → GSLB health-aware DNS pulls the record.
2. **L4 LB accepts the TCP/TLS connection** and picks a gateway replica (consistent hashing so connections survive LB restarts). Knows nothing about HTTP. Failure: replica unhealthy → health check has already evicted it.
3. **Gateway terminates TLS**, reads the request line + headers.
4. **Gateway authenticates** — reads `Authorization: Bearer <jwt>`, validates the signature against the cached JWKS public key (CPU-only, no network hop). Opaque token/API key instead → lookup in local cache, miss → Redis/identity-service call, cache result. Invalid → `401` returned immediately; nothing is proxied.
5. **Gateway authorizes coarsely + rate-limits** — route-level policy, token bucket check (Redis or local). Over limit → `429`.
6. **Gateway routes** — longest-prefix match on (host, path) in the in-memory route table → target service. No match → `404` from the gateway itself.
7. **Gateway proxies the request** to the chosen service's instance (picked by mesh/client-side LB, e.g. power-of-two-choices), typically injecting identity claims as headers (`X-User-Id`) and a trace ID. Waits on: per-hop timeout. Failure: timeout/5xx → retry per budget → circuit breaker opens → degraded response.
8. **Service executes the endpoint** — framework routing (Spring `@RequestMapping`) dispatches to the handler; **fine-grained authZ happens here**, against domain objects.
9. **Response streams back** through the gateway (response filters, access log, metrics) → client.

So your summary — DNS → region, NLB → gateway instance, gateway routes by path to service, then instance selection — is correct; the one correction is step 7–8: the gateway never "owns" or implements the endpoint, it proxies to the internal service that does.

---

## 3. Load Balancer Fundamentals

_(Condensed and restructured from the GeeksforGeeks load-balancer interview page + standard references; kept to the claims that survive scrutiny.)_

### 3.1 What it is, and what breaks without it

```
Without LB:  clients ──► [ single server ]      ✘ SPOF, ✘ ceiling
With LB:     clients ──► [ LB ] ──► S1/S2/S3    ✔ spread, ✔ failover
```

- A load balancer distributes incoming requests across a pool of servers so no single node is a bottleneck or a single point of failure.
  → Mechanism: it receives every request, applies an algorithm (3.3) filtered by health state (3.4), and forwards to a chosen backend.
  → Without one, a single server is both a **SPOF** (crash = total outage) and a **hard throughput ceiling** (overload = latency collapse, then failures).
- Placement is layered, not singular: client→web tier, web→app tier, app→cache tier, cache/app→DB tier can each have their own balancing hop. Every request from outside goes through the edge LB; internal service-to-service traffic often bypasses proxies via client-side LB (see 2.1).
- Do LBs cache? Distribution is the job; but software L7 proxies (NGINX) can double as reverse-proxy caches for static content. Reverse proxy vs LB: overlapping boxes — reverse proxy emphasizes security/caching/TLS/hiding backends and works fine with one backend; LB emphasizes distribution and implies a pool. Modern L7 products are both.
- Why not chain LBs in series (LB1 → LB2 → server)? Each hop adds latency and a failure domain with no distribution benefit. Redundancy is built **in parallel** (3.6), and _different-purpose_ layers (L4 edge → L7 gateway) are fine — that's layering, not redundancy chaining.

### 3.2 Types: by deployment and by layer

| Axis       | Type     | What it means                                                                       | Example / choose when                                                                            |
| ---------- | -------- | ----------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| Deployment | Software | Process on commodity VMs                                                            | NGINX, HAProxy — default in cloud                                                                |
|            | Hardware | Dedicated appliance                                                                 | F5 BIG-IP — legacy DC, extreme throughput                                                        |
|            | Virtual  | Appliance image on a hypervisor                                                     | VMware environments                                                                              |
| Layer      | **L4**   | Balances by IP/port/protocol; no payload inspection; TCP **and UDP**                | Cheap, fast, protocol-agnostic (games, raw TCP) — AWS NLB                                        |
|            | **L7**   | Reads HTTP: path, host, headers, cookies; enables content routing + TLS termination | Path/host routing, sticky-by-cookie — AWS ALB, NGINX                                             |
|            | **GSLB** | Balances across data centers by geography, latency, and DC health                   | Multi-region: users hit nearest healthy region; DC failure → traffic re-routed to another region |

- Defeater: L4's speed comes precisely from _not_ reading the payload — the moment you need path routing or cookie stickiness, you're forced up to L7 and pay the inspection cost.

### 3.3 Algorithms

| Algorithm            | Mechanism                                 | Choose when                                        | Defeater                                                                                                   |
| -------------------- | ----------------------------------------- | -------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Round robin          | Sequential rotation                       | Identical servers, uniform requests                | Ignores actual load — a node stuck on slow requests keeps receiving equal share                            |
| Weighted RR          | Rotation proportional to assigned weights | Heterogeneous server capacity                      | Static weights go stale as real load shifts                                                                |
| Source IP hash       | hash(client IP) → server                  | Cheap stickiness without cookies                   | NAT'd populations hash to one node → hot server; pool resize reshuffles mappings (fix: consistent hashing) |
| Least connections    | Pick fewest active connections            | Variable request durations, long-lived connections | Connection count ≠ cost; needs shared view of counts                                                       |
| Least response time  | Pick fastest current responder            | Latency-sensitive, mixed workloads                 | Feedback loops: everyone piles onto the briefly-fast node                                                  |
| Power of two choices | Sample 2 random, pick less loaded         | Distributed/client-side LB at scale                | Near-optimal with almost no coordination — the modern default                                              |

- Choosing: uniform fleet + uniform work → round robin; variable durations → least connections; heterogeneous capacity → weighted; need stickiness → IP hash (or cookie at L7); distributed clients → power-of-two.

### 3.4 Health checking

```
LB ── GET /health ──► S1: 200 ✔    S2: timeout ✘ (evicted)    S3: 200 ✔
```

- **Active checks**: LB probes each backend every few seconds (HTTP `GET /health`, TCP connect, ping). Success (e.g. 200) = healthy; failures past a threshold = evicted from the pool.
  → Checks are periodic, **not** per-request — per-request checking would double traffic and add latency for marginal freshness. The cost: a few seconds of blindness between a crash and detection.
- **Passive checks**: LB watches real traffic — timeouts, connection resets, 5xx spikes — and marks nodes unhealthy from observed behavior. Typically combined with active checks (passive catches what a shallow `/health` misses).
- **Recovery is conservative**: a returning server is not trusted on its first successful probe; the LB requires N consecutive passes before re-admitting it — prevents flapping nodes from oscillating in and out.
- **In-flight requests on a crash die.** Health checks only stop _new_ traffic to the dead node; requests it was processing fail or time out. Client-side retries + idempotency keys are what make that invisible to users — the LB alone doesn't save those requests.

### 3.5 Sticky sessions (session persistence)

- All requests from one client pinned to one backend, so server-local session data (login, cart) stays reachable.
  → Mechanism: cookie-based (L7 inserts/reads a cookie) or source-IP hash (L4).
  → Defeater: stickiness fights balancing — hot clients create hot servers, and a pinned server's crash loses those sessions anyway. Modern default: **externalize session state (Redis) and stay stateless**; use stickiness only when you can't.

### 3.6 The LB as its own SPOF: active-active vs active-passive

```
Active-Active:   DNS ──► LB1 + LB2  (both serving)
Active-Passive:  DNS ──► LB1 (VIP) ─╌ LB2 standby, takes VIP on failure
```

- One LB in front of everything just moves the SPOF forward. Fix: multiple LBs **in parallel**.

|             | Active-Active                                     | Active-Passive                                |
| ----------- | ------------------------------------------------- | --------------------------------------------- |
| Traffic     | Split across all LBs (DNS multi-record / anycast) | Primary only; standby idles                   |
| Utilization | Full                                              | Standby wasted                                |
| Failover    | Survivors absorb load instantly                   | VIP/DNS flips to standby on failure detection |
| Complexity  | Higher (shared state sync — e.g. rate counters)   | Lower                                         |
| Choose when | Scale + HA both needed (default at scale)         | Simplicity, compliance-style setups           |

- Managed cloud LBs (AWS ELB/ALB/NLB, GCP LB) are internally redundant fleets already — this whole section is what the provider does under the DNS name they hand you.
- **Failover** generally: health detection → traffic redirected to surviving capacity automatically, no human in loop. At GSLB level the same logic applies to whole data centers: region down → DNS/anycast shifts users to the next region.

### 3.7 Connection draining & autoscaling integration

- **Connection draining (graceful shutdown)**: to remove a server (deploy, maintenance), the LB stops sending it _new_ requests but lets in-flight requests finish (bounded by a drain timeout), then removes it. Prevents user-visible errors on every deploy — this is why rolling deploys work.
- **Autoscaling loop**: traffic ↑ → autoscaler launches instances → they register with the LB → pass health checks → start receiving traffic. Traffic ↓ → instances drain → deregister → terminate. The LB is the integration point that makes elastic capacity invisible to clients.
- **Adding a server** is the same admission path: register → pass N health checks → enter pool. (Watch for cold-start thundering herd: some LBs support slow-start ramping for new nodes.)

### 3.8 Interview pop-ups

- **"Why do you need both an API Gateway and a load balancer?"** Different jobs at different grains: the gateway does API policy (authN, rate limits, routing-by-path); LBs do distribution — L4 in front of the gateway fleet, instance-level LB behind it. In practice: NLB → gateway replicas → (mesh LB) → service instances.
- **"Why is round robin not always best?"** It's load-blind — equal distribution to unequal servers/requests overloads the slow node. Least-connections or least-response-time when durations vary.
- **"Can an LB handle UDP?"** L4 yes (transport layer); L7 is HTTP(S)-centric.
- **"LB fails — then what?"** Parallel redundancy (3.6); with managed cloud LBs the provider owns this.
- **"Server crashes mid-request?"** Those requests fail; health checks stop new traffic; retries + idempotency make it invisible (3.4).
- **"How many LBs does Netflix/Amazon use?"** Layered: GSLB across regions → edge L4/L7 per region → service-level balancing inside — dozens of logical LBs, not one.

---

## 4. References

1. Envoy architecture docs (routing, xDS, rate limiting) — https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/arch_overview
2. Spring Cloud Gateway reference (predicates, filters, RequestRateLimiter) — https://docs.spring.io/spring-cloud-gateway/reference/
3. AWS API Gateway HTTP APIs (routes, JWT authorizers, VPC Link) — https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api.html
4. Maglev paper (Google L4 LB, consistent hashing) — https://research.google/pubs/pub44824/
5. Meta ServiceRouter (OSDI '23, client-side LB at scale) — https://www.usenix.org/conference/osdi23/presentation/saokar
6. GeeksforGeeks — Load Balancer interview question set (source for §3) — https://www.geeksforgeeks.org/system-design/load-balancer-system-design-interview-question/
