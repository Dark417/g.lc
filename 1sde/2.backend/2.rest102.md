# REST 102 — API Design + Data Models for Oracle System Design

## Index

- [Shared API and schema conventions](#shared)
- [1infra](#infra)
  - [1.1 Rate limiter](#infra-1)
  - [1.2 Load balancer](#infra-2)
  - [1.3 Thread-safe and distributed cache](#infra-3)
  - [1.4 Edge-device health monitoring](#infra-4)
  - [1.5 Metrics ingestion](#infra-5)
  - [1.6 Remote browser isolation](#infra-6)
  - [1.7 Logging service](#infra-7)
  - [1.8 Monolith scaling](#infra-8)
  - [1.9 Resumable file upload](#infra-9)
- [1infra-pki](#pki)
  - [2.1 Certificate issuance](#pki-1)
  - [2.2 Certificate and trust distribution](#pki-2)
  - [2.3 Revocation](#pki-3)
  - [2.4 Key management and signing](#pki-4)
  - [2.5 Authorization policy](#pki-5)
  - [2.6 PKI disaster recovery](#pki-6)
- [1infra+](#platform)
  - [3.1 Work-request API](#platform-1)
  - [3.2 Job scheduler](#platform-2)
  - [3.3 Configuration distribution](#platform-3)
  - [3.4 Consistent metadata/KV store](#platform-4)
  - [3.5 Leases, locks, and election](#platform-5)
  - [3.6 Distributed event log](#platform-6)
- [2business](#business)
  - [4.1 Healthcare ingestion](#business-1)
  - [4.2 Chat](#business-2)
  - [4.3 Uber](#business-3)
  - [4.4 Video streaming](#business-4)
  - [4.5 URL shortener](#business-5)
  - [4.6 Recommendations](#business-6)
- [References](#references)

- **Coverage:** all 27 questions in [the ranked Oracle bank](../../1o/2.sd/2.sd.md), preserving its four groups and within-group order.
- **Scope:** interview-ready API contracts and data models, with L4 foundations, L5 extras, and trap points.
- **Design status:** proposed contracts, not Oracle's actual API specification; use official SDKs/specifications when implementing OCI integrations.
- **Companion:** [REST 101](2.rest101.md) explains HTTP semantics and common mechanisms.
- **Schema status:** PostgreSQL-style DDL for bounded metadata and domain state; explicitly labeled KV/log layouts for native data planes.
- **Composition:** each question is an independent service design. Repeated business concepts across examples are not one global database.

<a id="shared"></a>

## Shared API and schema conventions

### L4 — request, response, and ownership

- Prefix proposed JSON API paths with `/v1`; tables below omit that prefix for readability.
- Resolve `tenant_id` and caller identity from authenticated context, not an untrusted body field.
- Every identifier lookup, list filter, signed URL, and replay response must enforce tenant/object authorization.
- `I` in an API table means require `Idempotency-Key` for that logical command.
  - Scope by tenant, caller, and operation.
  - Bind the key to a canonical request fingerprint.
  - Replay the original response after completion; reject changed input with `409 KEY_REUSED`.
  - Keep ambiguous retries on the same key; a genuinely new intent gets a new key.
- `V` means a strong `If-Match` validator for the resource targeted by the request.
  - Missing required validator: `428`.
  - Failed comparison: `412`.
  - A version of a different resource belongs in the command body as a domain precondition; failure is `409`.
  - When PUT creates a previously absent named resource, use `If-None-Match: *` instead; the creation path cannot require an ETag for a resource that does not yet exist.
- Collections default to a bounded page size and return `{items,nextCursor}`.
  - Document limits; bind opaque cursors to tenant, filter, and sort.
  - Use a unique tiebreaker; snapshots are explicit when exact traversal is required.
- Common errors: `400` malformed input, `401` authentication, `403/404` permission/visibility policy, `409` state conflict, `413` size limit, `415` media type, `422` semantic validation, `429` throttling, `503` unavailable.
- JSON failures use RFC 9457 Problem Details with stable `type`, bounded `detail`, and `traceId`.
- `202` means durably accepted work, not completed work.
  - Return `{operationId,resourceId?}` and `Location: /v1/operations/{operationId}`.
  - Operation states: `ACCEPTED → RUNNING → SUCCEEDED / FAILED`; cancellation is separately tracked.
  - The actual OCI contract varies by service and can identify work through `opc-work-request-id`.
- Units are explicit: timestamps with offsets, durations in named units, byte sizes as integers, monetary amounts as minor units plus currency.
- SQL `id` values are application-generated opaque identifiers; tenant/principal registries belong to the identity service and are omitted from each independent schema.
- Database constraints express local invariants; cross-service references require authorization, existence checks, and reconciliation rather than cross-database foreign keys.

```json
{
  "type": "https://errors.example.test/version-conflict",
  "title": "Resource changed",
  "status": 409,
  "detail": "The expected source version is no longer current.",
  "traceId": "trace-example"
}
```

### L5 extra — shared write boundary

```text
Authenticate -> authorize target -> validate bounded input
  -> claim/replay intent -> check domain preconditions
  -> transaction: business state + response/operation + audit/outbox
  -> commit -> response
                 |
                 +-> outbox relay -> idempotent/fenced downstream worker
```

```sql
CREATE TABLE api_intents (
  tenant_id text NOT NULL, caller_id text NOT NULL, operation text NOT NULL,
  intent_key text NOT NULL, request_hash text NOT NULL,
  response_status integer, response_body jsonb, response_headers jsonb,
  created_at timestamptz NOT NULL, expires_at timestamptz NOT NULL,
  PRIMARY KEY (tenant_id, caller_id, operation, intent_key),
  CHECK (expires_at > created_at)
);
CREATE INDEX intents_expiry ON api_intents (expires_at);
CREATE TABLE outbox_events (
  tenant_id text NOT NULL, event_id text NOT NULL, aggregate_id text NOT NULL,
  aggregate_version bigint NOT NULL, event_type text NOT NULL, payload jsonb NOT NULL,
  created_at timestamptz NOT NULL, published_at timestamptz,
  PRIMARY KEY (tenant_id, event_id)
);
CREATE INDEX outbox_pending ON outbox_events (created_at, event_id)
  WHERE published_at IS NULL;
CREATE TABLE audit_events (
  tenant_id text NOT NULL, event_id text NOT NULL, actor_id text NOT NULL,
  action text NOT NULL, resource_id text NOT NULL, outcome text NOT NULL,
  at timestamptz NOT NULL, trace_id text NOT NULL, redacted_details jsonb NOT NULL,
  PRIMARY KEY (tenant_id, event_id)
);
CREATE INDEX audit_resource ON audit_events (tenant_id, resource_id, at, event_id);
```

- Use these shared tables per owning service where applicable; lifecycle records and messages can provide their own durable intent identity.
- Claim intents with `INSERT ... ON CONFLICT DO NOTHING`; do not keep querying inside a PostgreSQL transaction aborted by a uniqueness error.
- In a single transaction, competing claims can wait on uniqueness arbitration; an uncommitted row is not a visible durable in-progress lease.
- External effects cannot join an ordinary local SQL transaction.
  - Use durable workflow state and effect-specific deduplication/reconciliation.
  - Store the operation response atomically at acceptance; workers separately own execution recovery.
- Append-only audit requires restricted database roles and retention/tamper controls; a table name does not provide immutability.
- Retention and capacity values are design parameters, not universal defaults.

| Option | What it is | Strength | Weakness | Choose when |
|---|---|---|---|---|
| Relational metadata | Constraints and transactional state transitions | Local multi-row invariants | Hot rows and cross-region writes need care | Control plane, ownership, business state |
| Replicated KV state machine | Ordered commands applied by a consensus group | Linearizable revision/lease operations | Quorum latency and unavailable minority | Coordination and authoritative metadata |
| Partitioned log / TSDB | Append records by partition and time | Sequential writes and bounded scans | Cross-partition ordering is extra work | Events, metrics, history |
| Object storage | Immutable large blobs plus manifests | Large payloads outside database rows | Metadata/blob publication needs reconciliation | Files, video, CRLs, snapshots |
| Volatile cache | Rebuildable entries and runtime indexes | Low per-access cost | Eviction, stale data, and memory limits | Cache entries, health projections, geo candidates |

- **Default:** choose ownership and hot access patterns first; persist only the state whose loss violates the contract.

<a id="infra"></a>

## 1infra

<a id="infra-1"></a>

### 1.1 Distributed rate limiter — P0

- **Bank:** [1infra #1](../../1o/2.sd/2.sd.md#1infra); **source:** 1p3a ×2 + recruiter; **type:** HLD + algorithm.

- **L4 model:** durable tenant policies plus ephemeral token buckets; gateway decisions protect a bounded downstream capacity.

#### API design — L4

| Operation | Request | Result | Contract |
|---|---|---|---|
| `PUT /limit-policies/{scope}` | `{ratePerSecond,burst,mode}` | `201` create / `200` update, `{scope,version}` | V for update; `If-None-Match: *` for create; tenant administrator |
| `GET /limit-policies/{scope}` | — | `200 policy`, ETag | Return configuration version |
| `DELETE /limit-policies/{scope}` | — | `204` | V; gateway falls back to an explicit parent/default policy |
| Internal `CheckAndConsume(scope,cost,requestId)` | Positive cost; trusted tenant context | `{allowed,remaining,retryAfterMs,policyVersion}` | Atomic refill/check/decrement; not GET |
| Protected business endpoint | Normal user request | Original response or `429` | Reject before expensive work; send Retry-After when known |
| `POST /limit-policies/{scope}/resets` | `{reason}` | `201 reset record` | I; privileged and audited; deliberate quota bypass |

#### Data model — L4

```sql
CREATE TABLE limit_policies (
  tenant_id text NOT NULL, scope text NOT NULL,
  rate_per_second numeric NOT NULL CHECK (rate_per_second > 0),
  burst numeric NOT NULL CHECK (burst > 0),
  mode text NOT NULL CHECK (mode IN ('ENFORCE','SHADOW')),
  version bigint NOT NULL, updated_at timestamptz NOT NULL,
  PRIMARY KEY (tenant_id, scope)
);
```

```text
Redis key: rl:{tenant:scope}:bucket
Value: tokens, last_refill_ms, policy_version
Expiry: no earlier than the time an idle depleted bucket becomes fully refilled
Optional replay key: rl:{tenant:scope}:request:{request_id} -> decision
Replay TTL: documented decision-retry window; memory is bounded by admitted request volume
```

- **Access:** policy lookup by `(tenant,scope)`; bucket placement by the same scope.
- **Invariant:** refill, charge, and optional request deduplication execute in one atomic operation.

#### L5 extra

- Local quota allocations reduce central calls; their sum and expiry policy determine maximum overshoot.
- Hash-tag only the keys that must share atomic execution; putting every tenant key in one slot can create a hot shard.
- During storage failure, choose fail-open, fail-closed, or bounded local allowance by endpoint risk.

#### Trap points

- A check-only GET followed by a decrement races with other callers.
- Expiring a depleted bucket too early silently grants fresh quota.
- A retry of the limiter RPC can charge twice unless its request identity is deduplicated or that policy is explicitly accepted.

<a id="infra-2"></a>

### 1.2 Software load balancer — P0

- **Bank:** [1infra #2](../../1o/2.sd/2.sd.md#1infra); **source:** 1p3a; **type:** HLD.

- **L4 model:** a versioned listener routes to a backend pool; observed health is separate from desired configuration.

#### API design — L4

| Operation | Request | Result | Contract |
|---|---|---|---|
| `POST /load-balancers` | `{name,networkRef}` | `202 operation` | I; create control-plane resource |
| `PUT /load-balancers/{id}/listeners/{name}` | `{port,protocol,poolId,certificateRef?}` | `202 operation` | V; validate port/protocol and tenant ownership |
| `PUT /load-balancers/{id}/pools/{pool}/backends/{backend}` | `{address,port,weight,adminState}` | `202 operation` | V; `DRAINING` stops new traffic without claiming connections ended |
| `GET /load-balancers/{id}` | — | `{desiredVersion,appliedVersion,listeners}` | Distinguish accepted configuration from fleet convergence |
| `GET /load-balancers/{id}/backend-health` | Bounded pool filter | `{items,observedAt}` | Observations can differ by proxy/zone |
| `DELETE /load-balancers/{id}` | — | `202 operation` | V; drain and release network resources |
| Native data plane | TCP/UDP flows or proxied HTTP | Routed traffic | L4 flow forwarding is not a REST endpoint |

#### Data model — L4

```sql
CREATE TABLE lb_pools (
  tenant_id text NOT NULL, lb_id text NOT NULL, pool_id text NOT NULL,
  policy text NOT NULL, health_check jsonb NOT NULL, version bigint NOT NULL,
  PRIMARY KEY (tenant_id, lb_id, pool_id)
);
CREATE TABLE lb_backends (
  tenant_id text NOT NULL, lb_id text NOT NULL, pool_id text NOT NULL,
  backend_id text NOT NULL, address text NOT NULL,
  port integer NOT NULL CHECK (port BETWEEN 1 AND 65535),
  weight integer NOT NULL CHECK (weight > 0), admin_state text NOT NULL,
  PRIMARY KEY (tenant_id, lb_id, pool_id, backend_id),
  FOREIGN KEY (tenant_id, lb_id, pool_id) REFERENCES lb_pools
);
CREATE TABLE lb_listeners (
  tenant_id text NOT NULL, lb_id text NOT NULL, listener_name text NOT NULL,
  port integer NOT NULL CHECK (port BETWEEN 1 AND 65535), protocol text NOT NULL,
  pool_id text NOT NULL, certificate_ref text, version bigint NOT NULL,
  PRIMARY KEY (tenant_id, lb_id, listener_name),
  UNIQUE (tenant_id, lb_id, port, protocol),
  FOREIGN KEY (tenant_id, lb_id, pool_id) REFERENCES lb_pools
);
```

- **Relationships:** listener → one pool; pool → many backends; certificate reference belongs to the PKI service.
- **Runtime layout:** `(proxyId,backendId) → health,observedAt,activeConnections`; connection table keyed by flow tuple and bounded by idle timeout.
- **Lifecycle:** parent LB resource and its desired/applied versions use the generic [resource model](#platform-1).

#### L5 extra

- Distribute immutable configuration generations and atomically swap the proxy's active snapshot.
- Keep last-known-good configuration through control-plane outages, subject to certificate expiry and explicit revocation policy.

#### Trap points

- Control-plane `202` does not mean every proxy applied the change.
- Storing one global health bit discards observer-specific network failures.
- Draining a backend is different from deleting its active connections.

<a id="infra-3"></a>

### 1.3 Thread-safe LRU → distributed cache — P0

- **Bank:** [1infra #3](../../1o/2.sd/2.sd.md#1infra); **source:** 1p3a ×2; **type:** LLD → HLD.

- **L4 model:** a key map and recency list share one synchronization boundary; TTL and capacity eviction are independent.

#### API design — L4

| Operation | Request | Result | Contract |
|---|---|---|---|
| Local `get(key)` | Key | Hit `{value,version}` or miss | Expired entries behave as absent; updates recency |
| Local `put(key,value,ttl)` | Bounded bytes, duration | Stored version | Eviction and map/list update are atomic |
| `GET /caches/{namespace}/entries/{key}` | Escaped opaque key | `200 value` or `404` | Proposed HTTP facade; use a native cache protocol on hot paths |
| `PUT /caches/{namespace}/entries/{key}` | `{value,expiresAt}` | `200 {version}` | Optional CAS with V; absolute expiry avoids extending TTL on a retry |
| `DELETE /caches/{namespace}/entries/{key}` | — | `204` | Define idempotent absence handling |
| `POST /caches/{namespace}/batch-gets` | `{keys:[...]}` | Per-key hit/miss | Bounded key count and byte budget |
| `PUT /cache-namespaces/{namespace}` | `{maxBytes,maxEntryBytes,defaultTtl}` | `200 policy` | Administrator; V |

#### Data model — L4

```text
Local map: (tenant, namespace, key) -> Node(value, version, expires_at, prev, next, bytes)
LRU list: sentinel_head <-> nodes <-> sentinel_tail
Counters: current_bytes, entry_count; protected with the same lock as mutation
Optional expiry heap: (expires_at, entry_version, key); stale heap entries are discarded
Distributed key: cache:{tenant:namespace:key_hash}:entry
Value: bytes, source_version, expires_at
Routing metadata: ring_version -> [(token, node_id, endpoint)]
```

- **Ownership:** entries are disposable; the source database owns durable truth.
- **Access:** O(1) expected map/list operations locally; heap-based expiry adds logarithmic maintenance.
- **Partition:** hash the full scoped key; cache nodes report capacity and ring-generation observations.
- **Retention:** TTL removes stale entries; byte limits prevent a few large values exhausting memory.

#### L5 extra

- Use per-key load coalescing; validate source versions so a slow old load cannot overwrite a newer fill.
- Read-your-writes may bypass a stale cache; cache TTL is not an end-to-end source freshness guarantee.
- Define CAS scope during node loss; a disposable cache without durable coordination cannot promise durable global versions.

#### Trap points

- Locking the map while leaving list surgery unlocked corrupts LRU structure.
- A cache miss does not prove that the source object is absent.
- An entry-count limit alone does not bound memory.

<a id="infra-4"></a>

### 1.4 Edge-device health monitoring — P0

- **Bank:** [1infra #4](../../1o/2.sd/2.sd.md#1infra); **source:** 1p3a; **type:** HLD.

- **L4 model:** enrolled devices send ordered heartbeats; health is an inferred projection, not ground truth.

#### API design — L4

| Operation | Request | Result | Contract |
|---|---|---|---|
| `POST /devices` | `{externalId,site,capabilities}` | `201 {deviceId,enrollmentRef}` | I; administrator enrolls device identity |
| `POST /devices/{id}/heartbeats` | `{bootId,seq,sentAt,signals}` | `202 {acceptedSeq}` | Device mTLS identity; acknowledge durable ingestion |
| `GET /devices/{id}/health` | — | `{state,lastReceivedAt,lastSeq,reason}` | Server receive time drives timeout inference |
| `GET /devices?state=&site=&after=` | Bounded filters | Page of devices | State index is a projection with freshness metadata |
| `POST /devices/{id}/probes` | `{reason}` | `202 operation` | I; bounded active probe for corroboration |
| `GET /devices/{id}/health-events?after=` | Time/cursor | Event page | Ordered by server event sequence |
| `DELETE /devices/{id}` | — | `202 operation` | V; decommission credentials and stop expected-heartbeat alarms |

#### Data model — L4

```sql
CREATE TABLE devices (
  tenant_id text NOT NULL, device_id text NOT NULL, external_id text NOT NULL,
  site text NOT NULL, state text NOT NULL, version bigint NOT NULL,
  credential_ref text NOT NULL,
  PRIMARY KEY (tenant_id, device_id), UNIQUE (tenant_id, external_id)
);
CREATE INDEX devices_site_state ON devices (tenant_id, site, state, device_id);
CREATE TABLE device_health_events (
  tenant_id text NOT NULL, device_id text NOT NULL, event_seq bigint NOT NULL,
  state text NOT NULL, received_at timestamptz NOT NULL, reason text NOT NULL,
  PRIMARY KEY (tenant_id, device_id, event_seq),
  FOREIGN KEY (tenant_id, device_id) REFERENCES devices
);
```

```text
Latest projection: health:{tenant:device} -> boot_generation, seq, last_received_at, state
Expiry scheduler: shard -> ordered(deadline, tenant, device, generation)
Heartbeat log key: (tenant, device); value includes boot_id, seq, receive_time, bounded signals
```

- **Access:** point health read; site/state listing; per-device transition history.
- **Invariant:** accept sequence advancement only for the enrolled current boot/session generation; late events must not revive an obsolete session.

#### L5 extra

- Separate `UNKNOWN` from `UNHEALTHY`; an ingestion outage can make a fleet appear dead.
- Preserve raw heartbeats briefly and transition history longer; tune retention independently.
- Require new boot identities to establish a new authenticated session rather than trusting arbitrary client timestamps.

#### Trap points

- Client wall clocks cannot reliably establish fleet-wide ordering.
- Missing heartbeat means missing evidence, not proof of hardware failure.
- Deleting an expired projection before recording the transition loses the evidence needed for alerts.

<a id="infra-5"></a>

### 1.5 Internal metrics ingestion — P0

- **Bank:** [1infra #5](../../1o/2.sd/2.sd.md#1infra); **source:** 1p3a; **type:** HLD.

- **L4 model:** producers append bounded batches; a series catalog identifies dimensions while time partitions serve range queries.

#### API design — L4

| Operation | Request | Result | Contract |
|---|---|---|---|
| `POST /metric-batches` | `{producerId,batchId,series:[{name,labels,points}]}` | `202 {batchId}` | Producer identity; whole-batch validation before acceptance |
| `GET /metric-batches/{producer}/{batch}` | — | `{state,accepted,rejected}` | Query acceptance/processing outcome within retention |
| `POST /metric-queries` | `{metric,filters,from,to,step,aggregation}` | `200 {series,points,nextCursor}` | Bounded time range and cost; read-only POST facade |
| `GET /metric-series?metric=&after=` | — | Catalog page | Limit label discovery by tenant |
| `PUT /metric-policies/{namespace}` | `{retentionSeconds,maxSeries,maxLabels}` | `200 policy` | V; administrator |
| `POST /metric-replays` | `{sourceRange,reason}` | `202 operation` | I; authorized replay retains original event identities |

#### Data model — L4

```sql
CREATE TABLE metric_series (
  tenant_id text NOT NULL, series_id text NOT NULL, name text NOT NULL,
  canonical_labels text NOT NULL, labels jsonb NOT NULL,
  PRIMARY KEY (tenant_id, series_id), UNIQUE (tenant_id, name, canonical_labels)
);
CREATE INDEX metric_name_lookup ON metric_series (tenant_id, name, series_id);
CREATE TABLE metric_batches (
  tenant_id text NOT NULL, producer_id text NOT NULL, batch_id text NOT NULL,
  payload_hash text NOT NULL, state text NOT NULL, accepted_at timestamptz NOT NULL,
  PRIMARY KEY (tenant_id, producer_id, batch_id)
);
```

```text
TSDB partition: (tenant, series_id, time_bucket)
Sample key: (event_time, sample_id)
Sample value: metric_kind, numeric_value OR histogram_buckets, producer_id
Rollup key: (tenant, series_id, resolution, window_start)
Rollup value: count, sum, min, max; histogram bins when needed
Log partition key: hash(tenant, series_id); retain ingestion identity through replay
```

- **Access:** catalog lookup by metric and bounded labels; point scans by series and time bucket.
- **Invariant:** batch deduplication alone is insufficient if the same sample appears in different batches; define sample identity or overwrite semantics per metric kind.
- **Lifecycle:** accepted log → indexed samples → rollup → expiration; late-arrival policy is explicit.

#### L5 extra

- Canonicalize labels and verify collisions if series IDs are hashes; hash equality alone does not establish identity.
- Reject or isolate cardinality explosions before allocating unbounded series state.
- Exact percentile merging needs compatible sketches/histograms, not an average of percentile values.

#### Trap points

- Deduplicating only by `(series,timestamp)` can silently discard valid same-timestamp samples.
- Acknowledging an in-memory queue does not promise durable ingestion.
- User IDs or arbitrary URLs as labels can exhaust cardinality budgets.

<a id="infra-6"></a>

### 1.6 Remote browser isolation — P1

- **Bank:** [1infra #6](../../1o/2.sd/2.sd.md#1infra); **source:** 1p3a; **type:** HLD.

- **L4 model:** a user owns a short-lived isolated browser session; gateways authorize access to its streaming channel.

#### API design — L4

| Operation | Request | Result | Contract |
|---|---|---|---|
| `POST /browser-sessions` | `{initialUrl,policyId}` | `202 {sessionId,operationId}` | I; validate egress and tenant quota |
| `GET /browser-sessions/{id}` | — | `{state,expiresAt,policyVersion}` | Session owner or administrator |
| `POST /browser-sessions/{id}/connection-tickets` | `{clientCapabilities}` | `201 {ticket,expiresAt}` | Short-lived, one-use ticket; no reusable bearer credential in URL logs |
| Native WebRTC/WebSocket stream | Ticket exchange; input sequence | Frames + acknowledged input sequence | Bounded backpressure; authenticate stream before browser access |
| `POST /browser-sessions/{id}/downloads` | `{downloadRef}` | `202 scan operation` | Policy approval and malware scan before release |
| `DELETE /browser-sessions/{id}` | — | `202 teardown operation` | Idempotent request; completion means sandbox destroyed |

#### Data model — L4

```sql
CREATE TABLE browser_sessions (
  tenant_id text NOT NULL, session_id text NOT NULL, user_id text NOT NULL,
  sandbox_ref text, policy_id text NOT NULL, policy_version bigint NOT NULL,
  state text NOT NULL, expires_at timestamptz NOT NULL, version bigint NOT NULL,
  PRIMARY KEY (tenant_id, session_id)
);
CREATE INDEX browser_user_sessions ON browser_sessions (tenant_id, user_id, state, session_id);
CREATE INDEX browser_expiry ON browser_sessions (expires_at) WHERE state = 'READY';
CREATE TABLE browser_tickets (
  tenant_id text NOT NULL, ticket_hash text NOT NULL, session_id text NOT NULL,
  expires_at timestamptz NOT NULL, consumed_at timestamptz,
  PRIMARY KEY (tenant_id, ticket_hash),
  FOREIGN KEY (tenant_id, session_id) REFERENCES browser_sessions
);
```

- **State:** `PROVISIONING → READY → TERMINATING → TERMINATED`; provisioning can fail.
- **Runtime:** `(session,connectionGeneration) → encoder state,inputSeq,frameQueue`; bounded memory, not durable SQL blobs.
- **Storage:** approved downloads and policy-permitted recordings use protected object references and retention; transient cookies die with the sandbox.

#### L5 extra

- Place sessions by regional latency and isolation capacity; pin a connection to its generation to reject stale input after reconnect.
- Separate URL/navigation policy from network egress enforcement to defend against redirects and DNS changes.

#### Trap points

- A shared browser process can violate tenant/session isolation.
- Session deletion acknowledged before cleanup is not proof that cookies, disks, or processes are gone.
- The requested URL can target internal services; a browser farm is an SSRF-capable system without egress controls.

<a id="infra-7"></a>

### 1.7 Logging service / log-file layer — P1

- **Bank:** [1infra #7](../../1o/2.sd/2.sd.md#1infra); **source:** 1p3a; **type:** LLD + HLD.

- **L4 model:** ordered append streams write immutable segments; metadata locates time ranges and ingestion checkpoints.

#### API design — L4

| Operation | Request | Result | Contract |
|---|---|---|---|
| `POST /log-streams` | `{name,retentionSeconds}` | `201 stream` | I; scoped producer/read permissions |
| `POST /log-streams/{id}/batches` | `{producerEpoch,firstSeq,events}` | `{lastAcceptedSeq,offset}` | Durable append acknowledgment; bounded batch |
| `POST /log-queries` | `{streams,from,to,filters}` | `200 {events,nextCursor}` | Tenant-scoped query; use 202 for expensive export |
| `GET /log-streams/{id}/tail?after=` | Offset cursor | SSE/native event stream | Heartbeats and resume; no implicit delivery guarantee beyond retention |
| `GET /log-streams/{id}/segments?after=` | — | Metadata page | Internal/operator view |
| `DELETE /log-streams/{id}` | — | `202 operation` | V; enforce retention/legal hold before deletion |

#### Data model — L4

```sql
CREATE TABLE log_streams (
  tenant_id text NOT NULL, stream_id text NOT NULL, name text NOT NULL,
  retention_seconds bigint NOT NULL CHECK (retention_seconds > 0), version bigint NOT NULL,
  PRIMARY KEY (tenant_id, stream_id), UNIQUE (tenant_id, name)
);
CREATE TABLE log_segments (
  tenant_id text NOT NULL, stream_id text NOT NULL, partition_id integer NOT NULL,
  base_offset bigint NOT NULL, end_offset bigint NOT NULL,
  min_time timestamptz NOT NULL, max_time timestamptz NOT NULL,
  object_ref text NOT NULL, checksum text NOT NULL,
  PRIMARY KEY (tenant_id, stream_id, partition_id, base_offset),
  FOREIGN KEY (tenant_id, stream_id) REFERENCES log_streams,
  CHECK (end_offset >= base_offset)
);
CREATE INDEX log_time_range ON log_segments (tenant_id, stream_id, min_time);
```

```text
Segment record: length | offset | producer_id | producer_epoch | seq | timestamp | payload | CRC
Sparse index: offset -> byte_position
Producer checkpoint: (tenant, stream, partition, producer_id) -> epoch, last_seq, last_offset
Search index: tenant + stream + time_bucket -> indexed fields and segment positions
```

- **Relationships:** stream → partitioned segments; query matches index entries then fetches records.
- **Invariant:** a producer acknowledgment is recoverable from the durable log/checkpoint after a crash.

#### L5 extra

- Indexing can lag append acknowledgment; return ingestion and searchable watermarks separately.
- Retention deletes whole segments only after reader/hold policy permits; archive metadata must survive blob cleanup retries.

#### Trap points

- Buffered write success is not fsync/replication durability.
- Client event time is not a globally ordered append offset.
- A tamper-evident audit stream requires stronger permissions and retention than an ordinary debug-log service.

<a id="infra-8"></a>

### 1.8 Scale a monolithic service — P1

- **Bank:** [1infra #8](../../1o/2.sd/2.sd.md#1infra); **source:** 1p3a; **type:** HLD discussion.

- **L4 assumption:** use order management as the concrete domain; the original prompt does not specify one.
- **Model:** preserve public business contracts while moving ownership one bounded context at a time.

#### API design — L4

| Operation | Request | Result | Contract |
|---|---|---|---|
| `POST /orders` | `{items,addressRef}` | `201 order` or `202 operation` | I; server owns prices and totals |
| `GET /orders/{id}` | — | Order view + ETag | Gateway routes by migration assignment |
| `POST /orders/{id}/cancellations` | `{reason,expectedOrderVersion}` | `202 operation` | I; domain conflict is 409 |
| Internal `POST /inventory-reservations` | `{orderId,items,expiresAt}` | Reservation result | Stable order-based intent; explicit compensation |
| Operator `POST /migrations` | `{context,cohort,target}` | `202 migration` | I; controlled ownership transfer |
| Operator `POST /migrations/{id}/rollbacks` | `{reason}` | `202 operation` | I; data compatibility determines whether rollback is possible |

#### Data model — L4

```sql
CREATE TABLE orders (
  tenant_id text NOT NULL, order_id text NOT NULL, customer_id text NOT NULL,
  state text NOT NULL, currency char(3) NOT NULL, total_minor bigint NOT NULL,
  version bigint NOT NULL, created_at timestamptz NOT NULL,
  PRIMARY KEY (tenant_id, order_id), CHECK (total_minor >= 0)
);
CREATE INDEX orders_customer ON orders (tenant_id, customer_id, created_at, order_id);
CREATE TABLE order_lines (
  tenant_id text NOT NULL, order_id text NOT NULL, line_no integer NOT NULL,
  sku text NOT NULL, quantity integer NOT NULL CHECK (quantity > 0),
  unit_price_minor bigint NOT NULL CHECK (unit_price_minor >= 0),
  PRIMARY KEY (tenant_id, order_id, line_no),
  FOREIGN KEY (tenant_id, order_id) REFERENCES orders
);
CREATE TABLE ownership_routes (
  tenant_id text NOT NULL, context text NOT NULL, cohort text NOT NULL,
  owner_service text NOT NULL, routing_epoch bigint NOT NULL, migration_state text NOT NULL,
  PRIMARY KEY (tenant_id, context, cohort)
);
```

- **Ownership:** one writer per aggregate/routing epoch; customer and inventory references become service-level relationships after extraction.
- **Events:** `OrderCreated/OrderCanceled {tenant,eventId,orderId,aggregateVersion,...}` from the shared outbox.
- **Read model:** materialized order details join events by aggregate version; expose freshness when asynchronous.

#### L5 extra

- Shadow reads compare old/new results before routing users; suppress side effects in the shadow path.
- Expand schemas, backfill, reconcile, switch ownership, then retire old writes.
- Use sagas for inventory/payment effects once the original transaction boundary is split.

#### Trap points

- Moving code without moving data ownership leaves a distributed monolith.
- Dual writing two databases without recovery can diverge after the first commit.
- Scaling the application tier does not remove a hot database row or an unbounded query.

<a id="infra-9"></a>

### 1.9 Fault-tolerant resumable file upload — P1

- **Bank:** [1infra #9](../../1o/2.sd/2.sd.md#1infra); **source:** 1p3a; **type:** HLD component.

- **L4 model:** an upload session owns numbered immutable part identities; finalization atomically publishes one object manifest.

#### API design — L4

| Operation | Request | Result | Contract |
|---|---|---|---|
| `POST /uploads` | `{objectKey,sizeBytes,sha256,mediaType}` | `201 {uploadId,partSize,expiresAt}` | I; quota check and scoped destination |
| `POST /uploads/{id}/part-tickets` | `{partNumbers}` | Scoped expiring upload URLs | Bounded list; ticket binds part number and maximum bytes |
| `PUT /uploads/{id}/parts/{n}` | Binary bytes + explicit checksum | `200 {partNo,checksum,etag}` | Same part/content replays; different content requires explicit replacement policy |
| `GET /uploads/{id}/parts?after=` | — | Part page | Authoritative resume source |
| `POST /uploads/{id}/completions` | `{parts:[{partNo,checksum}],sha256}` | `202 operation` | I; freeze part set before verification/publication |
| `DELETE /uploads/{id}` | — | `202 cleanup operation` | Abort only if finalization has not committed |
| `GET /objects/{id}` | — | Metadata or authorized download redirect | Object visible only after successful commit |

#### Data model — L4

```sql
CREATE TABLE uploads (
  tenant_id text NOT NULL, upload_id text NOT NULL, object_key text NOT NULL,
  declared_bytes bigint NOT NULL CHECK (declared_bytes >= 0), declared_sha256 text NOT NULL,
  state text NOT NULL CHECK (state IN ('OPEN','FINALIZING','COMMITTED','ABORTED','FAILED')),
  version bigint NOT NULL, expires_at timestamptz NOT NULL, object_version text,
  PRIMARY KEY (tenant_id, upload_id)
);
CREATE INDEX uploads_cleanup ON uploads (expires_at) WHERE state IN ('OPEN','ABORTED','FAILED');
CREATE TABLE upload_parts (
  tenant_id text NOT NULL, upload_id text NOT NULL, part_no integer NOT NULL CHECK (part_no > 0),
  object_ref text NOT NULL, size_bytes bigint NOT NULL CHECK (size_bytes >= 0),
  sha256 text NOT NULL, etag text NOT NULL,
  PRIMARY KEY (tenant_id, upload_id, part_no),
  FOREIGN KEY (tenant_id, upload_id) REFERENCES uploads
);
```

```text
Temporary blob: uploads/{tenant}/{upload_id}/{part_no}/{content_hash}
Published manifest: objects/{tenant}/{object_key}/{object_version}
Manifest: ordered parts, total_bytes, verified_file_sha256, media_type, created_at
```

- **Invariant:** `OPEN → FINALIZING` freezes mutation; publication and `COMMITTED` are recoverable across SQL/blob-store crashes.
- **Access:** resume by ordered `(upload,part_no)`; cleanup by expiry; downloads by committed object manifest.

#### L5 extra

- Concurrent uploads to one destination need conditional object-generation publication or an explicit overwrite policy.
- Reconcile orphan blobs and manifests with grace periods so garbage collection cannot delete a live finalize attempt.
- The source's older “ETag equals MD5” simplification is not assumed here; provider ETags are opaque validators.

#### Trap points

- Hashing concatenated part hashes does not generally produce the file's SHA-256.
- Client-declared checksums require server/storage verification.
- Deleting the SQL upload row is not equivalent to deleting its staged bytes.

<a id="pki"></a>

## 1infra-pki

<a id="pki-1"></a>

### 2.1 Multi-tenant CA and certificate issuance — P0

- **Bank:** [1infra-pki #1](../../1o/2.sd/2.sd.md#1infra-pki); **source:** JD fit + OCI Certificates docs; **type:** HLD.

- **L4 model:** a logical CA has signing versions; a logical certificate has immutable issued versions.
- **Key ownership:** CA keys remain inside HSM-backed storage; a CSR flow keeps the leaf private key with the requester.

#### API design — L4

| Operation | Request | Result | Contract |
|---|---|---|---|
| `POST /certificate-authorities` | `{name,parentCaId?,keySpec,profile}` | `202 {caId,operationId}` | I; root creation requires separate administrative policy |
| `GET /certificate-authorities/{id}` | — | `{state,activeIssuerVersion,publicChain}` | No private material |
| `POST /certificates` | `{caId,csrPem,profileId,requestedValidity}` | `202 {certificateId,operationId}` | I; parse CSR and verify proof of possession |
| `GET /certificates/{id}` | — | `{currentVersion,issuer,status,notAfter}` | Resource visibility and tenant authorization |
| `GET /certificates/{id}/versions/{v}/bundle` | — | Public certificate + issuer chain; ETag | PEM/DER content negotiation; immutable version |
| `GET /certificates?expiringBefore=&after=` | — | Metadata page | Indexed operational sweep |
| `PATCH /certificate-authorities/{id}` | `{issuanceEnabled:false}` | `200 CA`, ETag | V; disabling issuance is not revoking existing certificates |

#### Data model — L4

```sql
CREATE TABLE certificate_authorities (
  tenant_id text NOT NULL, ca_id text NOT NULL, name text NOT NULL,
  parent_ca_id text, state text NOT NULL, active_issuer_version integer,
  profile jsonb NOT NULL, version bigint NOT NULL,
  PRIMARY KEY (tenant_id, ca_id), UNIQUE (tenant_id, name),
  FOREIGN KEY (tenant_id, parent_ca_id) REFERENCES certificate_authorities
);
CREATE TABLE signing_issuers (
  tenant_id text NOT NULL, ca_id text NOT NULL, issuer_version integer NOT NULL,
  key_ref text NOT NULL, public_chain_ref text NOT NULL, state text NOT NULL,
  not_before timestamptz NOT NULL, not_after timestamptz NOT NULL,
  PRIMARY KEY (tenant_id, ca_id, issuer_version),
  FOREIGN KEY (tenant_id, ca_id) REFERENCES certificate_authorities,
  CHECK (not_after > not_before)
);
CREATE TABLE certificates (
  tenant_id text NOT NULL, certificate_id text NOT NULL, owner_id text NOT NULL,
  name text NOT NULL, current_version integer, auto_renew boolean NOT NULL,
  version bigint NOT NULL,
  PRIMARY KEY (tenant_id, certificate_id)
);
CREATE TABLE certificate_versions (
  tenant_id text NOT NULL, certificate_id text NOT NULL, cert_version integer NOT NULL,
  ca_id text NOT NULL, issuer_version integer NOT NULL, serial numeric(49,0) NOT NULL,
  csr_hash text NOT NULL, sans jsonb NOT NULL, public_bundle_ref text,
  state text NOT NULL, not_before timestamptz NOT NULL, not_after timestamptz NOT NULL,
  PRIMARY KEY (tenant_id, certificate_id, cert_version),
  UNIQUE (tenant_id, ca_id, serial),
  FOREIGN KEY (tenant_id, certificate_id) REFERENCES certificates,
  FOREIGN KEY (tenant_id, ca_id, issuer_version) REFERENCES signing_issuers,
  CHECK (serial > 0), CHECK (not_after > not_before)
);
CREATE INDEX cert_expiry ON certificate_versions (tenant_id, not_after, certificate_id)
  WHERE state = 'ISSUED';
```

- **Relationships:** CA 1:N signing versions; certificate 1:N issued versions; each issued version names exactly one signing issuer version.
- **States:** `PENDING → SIGNING → ISSUED / FAILED`; actual revocation is maintained by the revocation service.
- **Serial invariant:** unique across all signing versions of the same logical issuing authority; rotating the key does not reset its serial namespace.
  - If operational CA records represent the same issuing authority, resolve them to one shared serial-allocation namespace before signing.
  - Enforce the X.509 positive, at-most-20-octet encoding rule in the issuer; SQL precision alone is insufficient.
- **Issuance boundary:** persist intent, chosen issuer, serial, validity, and to-be-signed bytes/hash before HSM work; publish one completed bundle for that intent.

#### L5 extra

- A database transaction cannot atomically roll back an HSM signature; recover the durable issuance intent and reconcile the signed artifact.
- Authorize SANs, key usage, CA constraints, algorithms, and validity independently of CSR signature validity.
- Recheck the issuer's authorization/state at the signing boundary; a disable request racing issuance needs a documented cutoff.
- Avoid locking one CA metadata row for every issuance; allocate safe serial identities without turning the CA into a global hot row.

#### Trap points

- Possessing a key does not prove authorization to obtain a certificate for an arbitrary DNS name.
- A logical certificate ID is not its serial number; renewal creates another issued version.
- Deleting a certificate record does not revoke its already-distributed public certificate.

<a id="pki-2"></a>

### 2.2 Renewal, trust distribution, and CA rollover — P0

- **Bank:** [1infra-pki #2](../../1o/2.sd/2.sd.md#1infra-pki); **source:** JD fit + OCI Certificates docs; **type:** HLD.

- **L4 model:** issuance creates immutable artifacts; deployments track desired and observed versions for each consumer.

#### API design — L4

| Operation | Request | Result | Contract |
|---|---|---|---|
| `POST /certificates/{id}/renewals` | `{baseVersion,csrPem?}` | `202 {newVersion,operationId}` | I; prevent concurrent duplicate renewal of the same base version |
| `POST /trust-bundles/{id}/versions` | `{issuerRefs,reason}` | `201 {bundleVersion,sha256}` | I; authorized trust change, immutable contents |
| `POST /certificate-deployments` | `{certificateVersion,trustBundleVersion,targetGroup,rolloutPolicy}` | `202 deployment` | I; references must be explicit immutable versions |
| `GET /certificate-deployments/{id}` | — | `{state,desired,applied,failed,pending}` | Convergence is based on consumer evidence |
| Agent `GET /certificate-assignments/{target}` | If-None-Match | `200 signed manifest` or `304` | Agent identity maps to target; returns public artifacts and authorized key-delivery reference only |
| Agent `PUT /certificate-deployments/{id}/acks/{target}` | `{generation,loadedVersion,validatedAt,error?}` | `200 ack` | Reject obsolete deployment generations |
| `POST /certificate-deployments/{id}/rollbacks` | `{targetVersion,reason}` | `202 operation` | I; rollback cannot revive a revoked/expired trust state |

#### Data model — L4

```sql
CREATE TABLE trust_bundle_versions (
  tenant_id text NOT NULL, bundle_id text NOT NULL, bundle_version bigint NOT NULL,
  manifest_ref text NOT NULL, sha256 text NOT NULL, created_at timestamptz NOT NULL,
  PRIMARY KEY (tenant_id, bundle_id, bundle_version)
);
CREATE TABLE certificate_deployments (
  tenant_id text NOT NULL, deployment_id text NOT NULL,
  certificate_version_ref text NOT NULL, bundle_id text NOT NULL, bundle_version bigint NOT NULL,
  target_group text NOT NULL, generation bigint NOT NULL, state text NOT NULL,
  policy jsonb NOT NULL, created_at timestamptz NOT NULL,
  PRIMARY KEY (tenant_id, deployment_id),
  FOREIGN KEY (tenant_id, bundle_id, bundle_version) REFERENCES trust_bundle_versions
);
CREATE TABLE certificate_target_acks (
  tenant_id text NOT NULL, deployment_id text NOT NULL, target_id text NOT NULL,
  generation bigint NOT NULL, loaded_version_ref text, state text NOT NULL,
  observed_at timestamptz NOT NULL, error_code text,
  PRIMARY KEY (tenant_id, deployment_id, target_id),
  FOREIGN KEY (tenant_id, deployment_id) REFERENCES certificate_deployments
);
CREATE INDEX deployment_targets ON certificate_target_acks
  (tenant_id, deployment_id, state, target_id);
```

- **Relationships:** trust version → many deployments; deployment → many target acknowledgments.
- **Access:** agent assignment by authenticated target; rollout progress by deployment/state; artifacts by immutable hash/version.
- **Rollover states:** `PUBLISH_TRUST → VERIFY_TRUST → SWITCH_LEAVES → VERIFY_SERVING → RETIRE_OLD_TRUST`.
- **Manifest:** `{generation,certificateVersionRef,chainHash,trustBundleRef,notBefore,notAfter,signature}`; cached with explicit freshness and rollback rules.

#### L5 extra

- Require readiness evidence across the intended consumer cohort, including offline/slow targets, before removing old trust.
- Distinguish “downloaded,” “loaded,” and “serving successful handshakes”; only the final observation proves traffic is using the new certificate.
- For customer-held keys, renewal requires a fresh authenticated CSR workflow; the service cannot recreate the private key from a certificate.

#### Trap points

- Successful issuance does not prove successful rotation at the load balancer.
- Switching leaf certificates before distributing issuer trust breaks handshakes.
- Last-known-good caching does not let an expired certificate remain valid.

<a id="pki-3"></a>

### 2.3 Certificate revocation and status distribution — P0

- **Bank:** [1infra-pki #3](../../1o/2.sd/2.sd.md#1infra-pki); **source:** JD fit; prep addition; **type:** HLD.

- **L4 model:** authoritative revocation events feed signed CRL snapshots and/or OCSP status responses.

#### API design — L4

| Operation | Request | Result | Contract |
|---|---|---|---|
| `POST /issuers/{issuer}/revocations` | `{serial,reason,invalidityDate?}` | `202 {revocationId,operationId}` | I; authorize issuer operation; cutoff/publication state visible |
| `GET /issuers/{issuer}/revocations/{serial}` | — | `{revokedAt,reason,publicationGeneration}` | Administrative metadata API, not a replacement for OCSP |
| `GET /issuers/{issuer}/crl` | Conditional request | Signed DER CRL, `application/pkix-crl` | Freshness bounded by signed thisUpdate/nextUpdate and cache policy |
| `POST /ocsp` | DER `application/ocsp-request` | DER `application/ocsp-response` | RFC OCSP protocol; status encoded in signed response, not JSON HTTP codes |
| `GET /ocsp/{encodedRequest}` | Protocol-defined encoded request | OCSP response | Optional supported profile; validate request size and encoding |
| `POST /issuers/{issuer}/crl-publications` | `{reason}` | `202 operation` | I; operator-triggered publish uses ordered revocation generation |

#### Data model — L4

```sql
CREATE TABLE issuer_status (
  tenant_id text NOT NULL, issuer_id text NOT NULL, next_generation bigint NOT NULL,
  responder_key_ref text NOT NULL, published_generation bigint NOT NULL,
  PRIMARY KEY (tenant_id, issuer_id)
);
CREATE TABLE revocations (
  tenant_id text NOT NULL, issuer_id text NOT NULL, serial numeric(49,0) NOT NULL,
  generation bigint NOT NULL, revoked_at timestamptz NOT NULL,
  reason text NOT NULL, invalidity_date timestamptz,
  PRIMARY KEY (tenant_id, issuer_id, serial),
  UNIQUE (tenant_id, issuer_id, generation),
  FOREIGN KEY (tenant_id, issuer_id) REFERENCES issuer_status
);
CREATE TABLE crl_snapshots (
  tenant_id text NOT NULL, issuer_id text NOT NULL, crl_number bigint NOT NULL,
  through_generation bigint NOT NULL, this_update timestamptz NOT NULL,
  next_update timestamptz NOT NULL, object_ref text NOT NULL, sha256 text NOT NULL,
  PRIMARY KEY (tenant_id, issuer_id, crl_number),
  FOREIGN KEY (tenant_id, issuer_id) REFERENCES issuer_status,
  CHECK (next_update > this_update)
);
```

- **Access:** `(issuer,serial)` status lookup; `(issuer,generation)` publication scan; latest published CRL pointer.
- **OCSP lookup:** protocol CertID contains issuer name/key hashes plus serial; route to the corresponding issuer identity without trusting an arbitrary tenant parameter.
- **Retention:** retain revocations as long as certificates/status evidence require; dropping a row must never turn revoked into good.
- **Invariant:** publish a signed snapshot of an explicit generation before advancing the public pointer.

#### L5 extra

- OCSP `good` does not replace path validation, validity checks, hostname validation, or proof that a certificate was issued.
- Bound emergency revocation propagation through generation lag, response validity, and consumer cache behavior.
- Nonce policy affects precomputed-response caching; use the current OCSP profile and applicable updates when implementing.

#### Trap points

- Removing a revoked row or returning `404` from a JSON endpoint is not certificate revocation enforcement.
- A database outage is not evidence for a signed `good` response.
- Fail-open versus fail-closed on unavailable status belongs to the relying-party policy and must be discussed explicitly.

<a id="pki-4"></a>

### 2.4 HSM-backed key management and signing — P0

- **Bank:** [1infra-pki #4](../../1o/2.sd/2.sd.md#1infra-pki); **source:** JD fit; prep addition; **type:** HLD.

- **L4 model:** logical keys have immutable HSM-backed versions; aliases choose versions, while signatures identify the actual version used.

#### API design — L4

| Operation | Request | Result | Contract |
|---|---|---|---|
| `POST /keys` | `{name,algorithm,purpose,protection:'HSM'}` | `202 {keyId,operationId}` | I; supported algorithm/purpose policy |
| `POST /keys/{id}/versions` | `{reason}` | `202 {keyVersion,operationId}` | I; rotation creates new material without deleting old verification keys |
| `GET /keys/{id}/versions/{v}/public-key` | — | SPKI public key + fingerprint | Asymmetric keys only; no private-key export |
| `POST /keys/{id}/signatures` | `{keyVersion,messageType:'DIGEST',hashAlgorithm,digestBase64,signingAlgorithm}` | `200 {signatureBase64,keyVersion,algorithm}` | I where exact replay is required; verify purpose and digest length |
| `PUT /key-aliases/{alias}` | `{keyId,keyVersion}` | `200 alias`, ETag | V; alias update does not change existing signatures |
| `PATCH /keys/{id}/versions/{v}` | `{state:'DISABLED'}` | `200 version`, ETag | V; fence new signing while allowing public verification |
| `POST /keys/{id}/versions/{v}/deletion-requests` | `{deleteAfter,reason}` | `202 operation` | I; policy hold, dependency checks, and auditable approval |

#### Data model — L4

```sql
CREATE TABLE crypto_keys (
  tenant_id text NOT NULL, key_id text NOT NULL, name text NOT NULL,
  purpose text NOT NULL, algorithm text NOT NULL, version bigint NOT NULL,
  PRIMARY KEY (tenant_id, key_id), UNIQUE (tenant_id, name)
);
CREATE TABLE crypto_key_versions (
  tenant_id text NOT NULL, key_id text NOT NULL, key_version bigint NOT NULL,
  hsm_handle text NOT NULL, public_key_ref text, fingerprint text,
  state text NOT NULL, created_at timestamptz NOT NULL, delete_after timestamptz,
  PRIMARY KEY (tenant_id, key_id, key_version),
  FOREIGN KEY (tenant_id, key_id) REFERENCES crypto_keys
);
CREATE TABLE key_aliases (
  tenant_id text NOT NULL, alias text NOT NULL, key_id text NOT NULL,
  key_version bigint NOT NULL, version bigint NOT NULL,
  PRIMARY KEY (tenant_id, alias),
  FOREIGN KEY (tenant_id, key_id, key_version) REFERENCES crypto_key_versions
);
```

- **Access:** key lookup; exact version lookup; alias-to-version resolution; disabled/deletion sweeps.
- **State:** `CREATING → ENABLED → DISABLED → PENDING_DELETION → DELETED`; recovery transitions obey policy.
- **Operation/audit records:** shared intent and audit model; retain key version, operation identity, policy decision, and outcome without logging sensitive message contents.
- **Invariant:** the signing request pins one key version before HSM execution; retries cannot silently resolve an alias to a newer version.

#### L5 extra

- A signature can be produced before the caller times out; deterministic signatures must not be assumed for every algorithm.
- Reconcile uncertain key-creation/signing operations using durable operation identity and HSM capabilities; never claim SQL rollback erased HSM effects.
- Key backup/replication uses vendor-supported protected mechanisms and separate authorization; metadata copies do not reproduce private keys.

#### Trap points

- Hashing a digest again changes the signed message; distinguish RAW and DIGEST modes.
- The database stores handles, not plaintext private-key bytes.
- Deleting an old key can invalidate future decryption or destroy recovery capability even after rotation succeeds.

<a id="pki-5"></a>

### 2.5 Authorization policy for certificate and key operations — P1

- **Bank:** [1infra-pki #5](../../1o/2.sd/2.sd.md#1infra-pki); **source:** JD fit; prep addition; **type:** HLD.

- **L4 model:** immutable policies and bindings are compiled into a tenant generation; decisions evaluate subject, action, resource, and trusted attributes.

#### API design — L4

| Operation | Request | Result | Contract |
|---|---|---|---|
| `POST /authorization-policies` | `{name,rules}` | `201 policy` | I; privileged authoring with validated action/resource vocabulary |
| `POST /authorization-policies/{id}/versions` | `{rules}` | `201 {version,contentHash}` | I; compile and validate before publication |
| `PUT /policy-bindings/{id}` | `{subjectRef,policyVersionRef,scope}` | `200 binding` | V; delegated administration cannot grant beyond its authority |
| `POST /policy-publications` | `{expectedGeneration,bindings}` | `202 publication` | I; atomic generation switch; domain mismatch 409 |
| Internal `POST /authorization-decisions` | `{subjectRef,action,resourceRef,context}` | `200 {allowed,decisionId,generation,reasonCode}` | Trusted service identity; target attributes resolved/verified server-side |
| `GET /policy-generations/{generation}` | — | Signed compiled bundle | Authorized enforcement agents; immutable version |
| `DELETE /policy-bindings/{id}` | — | `202 publication` | V; removal becomes effective under documented propagation bounds |

#### Data model — L4

```sql
CREATE TABLE policy_versions (
  tenant_id text NOT NULL, policy_id text NOT NULL, policy_version bigint NOT NULL,
  rules jsonb NOT NULL, compiled_ref text NOT NULL, content_hash text NOT NULL,
  PRIMARY KEY (tenant_id, policy_id, policy_version)
);
CREATE TABLE policy_bindings (
  tenant_id text NOT NULL, binding_id text NOT NULL, subject_ref text NOT NULL,
  resource_scope text NOT NULL, policy_id text NOT NULL, policy_version bigint NOT NULL,
  version bigint NOT NULL,
  PRIMARY KEY (tenant_id, binding_id),
  FOREIGN KEY (tenant_id, policy_id, policy_version) REFERENCES policy_versions
);
CREATE INDEX policy_subject ON policy_bindings (tenant_id, subject_ref, resource_scope);
CREATE TABLE policy_generations (
  tenant_id text NOT NULL, generation bigint NOT NULL,
  manifest_ref text NOT NULL, content_hash text NOT NULL, published_at timestamptz NOT NULL,
  PRIMARY KEY (tenant_id, generation)
);
```

- **Relationships:** policy version → many bindings; generation manifest freezes a complete effective binding set.
- **Decision cache key:** `(tenant,subject,action,resource,policyGeneration,subjectAttributeVersion,resourceAttributeVersion)` with bounded expiry.
- **Access:** subject/scope bindings; exact generation fetch; audit by decision/resource ID.
- **Invariant:** default deny; any deny/allow precedence and scope inheritance are defined by the policy language, not ad hoc caller code.

#### L5 extra

- Separate control-plane policy authoring from enforcement; enforcement can cache a signed generation under an explicit revocation/failure policy.
- A policy edit, identity-group removal, or resource attribute change can independently invalidate decisions.
- For sensitive signing/deletion operations, choose a freshness requirement that can reject stale policy decisions.

#### Trap points

- Letting a client supply arbitrary trusted subject/resource attributes creates privilege escalation.
- Caching by role alone misses tenant, resource, and policy-version boundaries.
- `200 {allowed:false}` is appropriate for a successful internal decision evaluation; the protected business API still returns its authorization failure status.

<a id="pki-6"></a>

### 2.6 Regional PKI disaster recovery — P1

- **Bank:** [1infra-pki #6](../../1o/2.sd/2.sd.md#1infra-pki); **source:** JD resilience requirements; prep addition; **type:** HLD.

- **L4 model:** a recovery point combines metadata position, artifact manifests, and recoverable key references; a fenced promotion selects the active writer.

#### API design — L4

| Operation | Request | Result | Contract |
|---|---|---|---|
| `POST /recovery-policies` | `{resourceScope,rpoTarget,rtoTarget,targetRegion}` | `201 policy` | I; targets are requirements to validate, not guarantees from one setting |
| `POST /recovery-points` | `{policyId}` | `202 operation` | I; capture coordinated recovery metadata |
| `GET /recovery-points/{id}` | — | `{state,throughPosition,keyInventory,artifactManifest}` | Publish READY only after verification |
| `POST /restore-tests` | `{recoveryPointId,isolatedTarget}` | `202 operation` | I; no production signing/traffic authority |
| `POST /regional-promotions` | `{targetRegion,recoveryPointId,expectedWriterEpoch}` | `202 operation` | I; independently fence the previous writer |
| `GET /regional-promotions/{id}` | — | `{state,newEpoch,checks,errors}` | Expose verification before enabling issuance |
| `POST /regional-failbacks` | `{targetRegion,expectedWriterEpoch}` | `202 operation` | I; reconcile divergence, then perform another fenced promotion |

#### Data model — L4

```sql
CREATE TABLE recovery_points (
  tenant_id text NOT NULL, point_id text NOT NULL, source_region text NOT NULL,
  db_position text NOT NULL, artifact_manifest_ref text NOT NULL,
  key_inventory_ref text NOT NULL, revoked_through_generation bigint NOT NULL,
  state text NOT NULL, created_at timestamptz NOT NULL, verified_at timestamptz,
  PRIMARY KEY (tenant_id, point_id)
);
CREATE INDEX recovery_latest ON recovery_points (tenant_id, created_at DESC, point_id);
CREATE TABLE regional_promotions (
  tenant_id text NOT NULL, promotion_id text NOT NULL, target_region text NOT NULL,
  point_id text NOT NULL, old_epoch bigint NOT NULL, new_epoch bigint NOT NULL,
  state text NOT NULL, checks jsonb NOT NULL,
  PRIMARY KEY (tenant_id, promotion_id),
  FOREIGN KEY (tenant_id, point_id) REFERENCES recovery_points,
  CHECK (new_epoch > old_epoch)
);
```

```text
Independent fencing authority: (service_scope) -> writer_region, monotonic_epoch, authority_lease
Recovery manifest: database replay position, immutable blob hashes, issuer/key versions,
  revocation publication watermarks, serial-allocation high-water marks, audit checkpoints
Consumer cache: valid certificate chain + signed trust/policy generation + freshness limits
```

- **Access:** newest verified point within the recovery policy; promotion state by operation ID.
- **Invariant:** recovery cannot restore an old fencing epoch and enable two writers; epoch authority must survive independently of the restored snapshot.
- **Retention:** versioned backups and protected key inventories follow coordinated retention; the oldest retained dependent data determines which keys remain necessary.

#### L5 extra

- Existing handshakes can continue from valid local certificates during a control-plane outage; new issuance and emergency revocation have different availability requirements.
- Validate HSM/key recoverability, serial uniqueness, and revocation freshness before enabling the recovered CA.
- Measure actual replay time, key availability, and traffic convergence in isolated restore exercises.

#### Trap points

- A metadata backup with missing HSM keys is not a usable CA recovery point.
- Restoring old revocation state can falsely resurrect a revoked certificate.
- DNS failover alone does not fence the former issuer or repair split-brain state.

<a id="platform"></a>

## 1infra+

<a id="platform-1"></a>

### 3.1 Asynchronous control-plane resource API — P0

- **Bank:** [1infra+ #1](../../1o/2.sd/2.sd.md#1infra-plus); **source:** Recruiter control-plane focus + OCI work-request docs; **type:** HLD + API.

- **L4 model:** a durable resource records desired state; a durable operation records progress toward it.

#### API design — L4

| Operation | Request | Result | Contract |
|---|---|---|---|
| `POST /resources` | `{kind,name,spec}` | `202 {resourceId,operationId}` | I; state + operation + outbox commit before response |
| `GET /resources/{id}` | — | `{desiredSpec,observedState,generation,observedGeneration}` | ETag refers to desired resource version |
| `PATCH /resources/{id}` | Defined merge/patch document | `202 operation` | V; reject incompatible overlapping lifecycle commands |
| `DELETE /resources/{id}` | — | `202 operation` | V; tombstone until downstream cleanup finishes |
| `GET /operations/{id}` | — | `{state,progress,resources,errors,acceptedAt,finishedAt}` | Authorized caller; progress is advisory |
| `GET /operations?resourceId=&state=&after=` | — | Operation page | Indexed by tenant/resource/time |
| `POST /operations/{id}/cancellations` | `{reason}` | `202 cancellation request` | I; best-effort until the point of no return |
| `GET /operations/{id}/events?after=` | — | Ordered events | Bounded history and documented retention |

#### Data model — L4

```sql
CREATE TABLE cloud_resources (
  tenant_id text NOT NULL, resource_id text NOT NULL, kind text NOT NULL,
  name text NOT NULL, desired_spec jsonb NOT NULL, observed_state jsonb NOT NULL,
  generation bigint NOT NULL, observed_generation bigint NOT NULL,
  lifecycle_state text NOT NULL, created_at timestamptz NOT NULL,
  PRIMARY KEY (tenant_id, resource_id), UNIQUE (tenant_id, kind, name)
);
CREATE TABLE operations (
  tenant_id text NOT NULL, operation_id text NOT NULL, resource_id text NOT NULL,
  verb text NOT NULL, target_generation bigint NOT NULL, state text NOT NULL,
  accepted_at timestamptz NOT NULL, finished_at timestamptz,
  worker_id text, worker_fence bigint NOT NULL DEFAULT 0, lease_until timestamptz,
  cancellation_requested boolean NOT NULL DEFAULT false,
  PRIMARY KEY (tenant_id, operation_id),
  FOREIGN KEY (tenant_id, resource_id) REFERENCES cloud_resources
);
CREATE INDEX operations_resource ON operations
  (tenant_id, resource_id, accepted_at DESC, operation_id);
CREATE INDEX operations_recovery ON operations (lease_until)
  WHERE state = 'RUNNING';
CREATE TABLE operation_events (
  tenant_id text NOT NULL, operation_id text NOT NULL, seq bigint NOT NULL,
  at timestamptz NOT NULL, event_type text NOT NULL, code text, details jsonb NOT NULL,
  PRIMARY KEY (tenant_id, operation_id, seq),
  FOREIGN KEY (tenant_id, operation_id) REFERENCES operations
);
```

- **Relationships:** resource 1:N operations; operation 1:N progress/error events.
- **State:** `ACCEPTED → RUNNING → SUCCEEDED / FAILED / CANCELED`; cancellation requests do not force immediate `CANCELED`.
- **Invariant:** mark success only when the requested generation's effects and observed state are verified.
- **Intent:** store the original `202` response using the shared intent table; it remains stable while the operation resource evolves.

#### L5 extra

- Reconciliation workers compare desired versus observed state and resume idempotent steps after crashes.
- Fence stale workers on every shared-state transition; downstream resources must also reject obsolete generations where concurrent effects matter.
- Preserve failed operation history while allowing a new explicit retry/reconcile operation with its own identity.

#### Trap points

- `percentComplete:100` alone is not a correctness condition.
- Returning `202` before an in-memory queue is persisted can lose accepted work.
- Canceling a workflow does not undo already-committed external effects.

<a id="platform-2"></a>

### 3.2 Distributed job scheduler / orchestrator — P0

- **Bank:** [1infra+ #2](../../1o/2.sd/2.sd.md#1infra-plus); **source:** Prior supplemental bank; platform preparation; **type:** HLD + concurrency.

- **L4 model:** job definitions generate logical occurrences; occurrences own runs and retry attempts.

#### API design — L4

| Operation | Request | Result | Contract |
|---|---|---|---|
| `POST /jobs` | `{schedule,timeZone,targetRef,retryPolicy,timeoutSeconds,overlapPolicy}` | `201 {jobId,nextRunAt}` | I; cron/one-shot syntax and target authorization |
| `GET /jobs/{id}` | — | Definition + ETag | Explicit schedule generation |
| `PATCH /jobs/{id}` | `{schedule?,state:'PAUSED'?,overlapPolicy?}` | `200 job` | V; define effects on already-materialized occurrences |
| `POST /jobs/{id}/runs` | `{payloadOverride?}` | `202 {runId}` | I; manual occurrence separate from scheduled occurrence |
| `GET /jobs/{id}/runs?after=` | — | Run history | Order by due time and run ID |
| `POST /runs/{id}/cancellations` | `{reason}` | `202 operation` | I; cooperative cancellation with final result |
| `DELETE /jobs/{id}` | — | `204` | V; stops future scheduling; running-task policy explicit |
| Internal target invocation | `{runId,attempt,fence,payload}` | Acknowledged outcome | Authenticated target request; stable runId across retries |

#### Data model — L4

```sql
CREATE TABLE scheduled_jobs (
  tenant_id text NOT NULL, job_id text NOT NULL, shard integer NOT NULL,
  schedule jsonb NOT NULL, time_zone text NOT NULL, target_ref text NOT NULL,
  retry_policy jsonb NOT NULL, overlap_policy text NOT NULL,
  next_run_at timestamptz, state text NOT NULL, generation bigint NOT NULL,
  PRIMARY KEY (tenant_id, job_id)
);
CREATE INDEX jobs_due ON scheduled_jobs (shard, next_run_at, tenant_id, job_id)
  WHERE state = 'ACTIVE';
CREATE TABLE job_runs (
  tenant_id text NOT NULL, run_id text NOT NULL, job_id text NOT NULL,
  occurrence_id text NOT NULL, due_at timestamptz NOT NULL,
  state text NOT NULL, attempt integer NOT NULL DEFAULT 0,
  fence bigint NOT NULL DEFAULT 0, worker_id text, lease_until timestamptz,
  next_attempt_at timestamptz, result_ref text,
  PRIMARY KEY (tenant_id, run_id), UNIQUE (tenant_id, job_id, occurrence_id),
  FOREIGN KEY (tenant_id, job_id) REFERENCES scheduled_jobs
);
CREATE INDEX runs_by_job ON job_runs (tenant_id, job_id, due_at DESC, run_id);
CREATE INDEX runs_retry ON job_runs (next_attempt_at) WHERE state = 'RETRY_WAIT';
CREATE INDEX runs_expired_worker ON job_runs (lease_until) WHERE state = 'RUNNING';
```

- **Occurrence identity:** scheduled `(scheduleGeneration,nominalDueTime)` or manual `(intentId)`; unique insertion prevents two scanners creating the same run.
- **State:** `READY → RUNNING → SUCCEEDED / FAILED / RETRY_WAIT / CANCELED`; every retry increments attempt and fencing generation.
- **Transaction:** create run, advance job's next due time, and write dispatch outbox atomically.
- **Retention:** keep logical run identity through the supported target deduplication window; archive older results separately.

#### L5 extra

- Define daylight-saving ambiguity, missed-run catch-up, and overlap behavior explicitly; they affect occurrence identity.
- Target execution must couple run-ID deduplication with its business effect, not merely insert a “seen” row before unrelated work.
- Authenticate and constrain callback targets; retry policy must obey tenant and dependency budgets.

#### Trap points

- A worker lease expiring does not stop the old process from sending requests.
- Exactly-once scheduling of a run record does not imply exactly-once execution of its external effect.
- Changing a cron expression without a schedule generation can duplicate or silently skip occurrences.

<a id="platform-3"></a>

### 3.3 Versioned configuration distribution — P1

- **Bank:** [1infra+ #3](../../1o/2.sd/2.sd.md#1infra-plus); **source:** JD fit; prep addition; **type:** HLD.

- **L4 model:** immutable validated configuration versions are deployed through a monotonically increasing rollout generation.

#### API design — L4

| Operation | Request | Result | Contract |
|---|---|---|---|
| `POST /configurations` | `{name,schemaRef}` | `201 configuration` | I; owner and namespace permissions |
| `POST /configurations/{id}/versions` | `{content,baseVersion}` | `201 {version,sha256}` | I; validate schema and bounded size |
| `POST /configurations/{id}/rollouts` | `{version,targetGroup,stages,healthGates}` | `202 rollout` | I; immutable target version |
| `GET /configurations/{id}/versions/{v}` | If-None-Match | `200 content` or `304` | Immutable payload; integrity hash |
| Agent `GET /configuration-assignments?afterGeneration=` | Resume generation | Snapshot or change stream | Compacted cursor returns `410 SNAPSHOT_REQUIRED` |
| Agent `PUT /configuration-rollouts/{id}/acks/{target}` | `{generation,appliedVersion,status}` | `200 ack` | Target identity; reject obsolete generations |
| `POST /configuration-rollouts/{id}/rollbacks` | `{knownGoodVersion,reason}` | `202 rollout` | I; new rollout generation points to old content |

#### Data model — L4

```sql
CREATE TABLE configuration_versions (
  tenant_id text NOT NULL, config_id text NOT NULL, config_version bigint NOT NULL,
  schema_ref text NOT NULL, content_ref text NOT NULL, sha256 text NOT NULL,
  created_at timestamptz NOT NULL,
  PRIMARY KEY (tenant_id, config_id, config_version)
);
CREATE TABLE configuration_rollouts (
  tenant_id text NOT NULL, rollout_id text NOT NULL, config_id text NOT NULL,
  config_version bigint NOT NULL, generation bigint NOT NULL,
  target_group text NOT NULL, stages jsonb NOT NULL, state text NOT NULL,
  PRIMARY KEY (tenant_id, rollout_id), UNIQUE (tenant_id, config_id, generation),
  FOREIGN KEY (tenant_id, config_id, config_version) REFERENCES configuration_versions
);
CREATE TABLE configuration_acks (
  tenant_id text NOT NULL, rollout_id text NOT NULL, target_id text NOT NULL,
  generation bigint NOT NULL, state text NOT NULL, observed_at timestamptz NOT NULL,
  PRIMARY KEY (tenant_id, rollout_id, target_id),
  FOREIGN KEY (tenant_id, rollout_id) REFERENCES configuration_rollouts
);
CREATE INDEX configuration_rollout_targets ON configuration_acks
  (tenant_id, rollout_id, state, target_id);
```

- **Access:** exact content version; latest assignment by config/target; rollout progress by state.
- **State:** `VALIDATED → CANARY → EXPANDING → COMPLETE`; failure can yield `PAUSED` or trigger another rollback rollout.
- **Runtime:** an agent validates the complete new snapshot before swapping one pointer; it keeps the previous usable generation for recovery.
- **Invariant:** generation orders deployment intent; content version identifies bytes. Rollback changes the former monotonically and can decrease the latter.

#### L5 extra

- Define atomic configuration bundles when several keys must change together; per-key delivery can expose an invalid combination.
- Gate expansion on traffic/error evidence, not just download counts.
- Distribute secret references through configuration; deliver secret material through a separately authorized channel.

#### Trap points

- Watch streams are not an infinite durable history; clients need snapshot recovery.
- Acknowledging download is not acknowledging successful application.
- Overwriting a version's bytes defeats hashes, rollback, and reproducibility.

<a id="platform-4"></a>

### 3.4 Strongly consistent metadata / KV store — P1

- **Bank:** [1infra+ #4](../../1o/2.sd/2.sd.md#1infra-plus); **source:** Prior supplemental bank; control-plane adaptation; **type:** HLD.

- **L4 model:** sharded replicated state machines assign revisions; each transaction has one declared atomicity boundary.

#### API design — L4

| Operation | Request | Result | Contract |
|---|---|---|---|
| `PUT /namespaces/{ns}/keys/{key}` | `{value,leaseId?}` | `{createRevision,modRevision}` | V for CAS; default quorum write |
| `GET /namespaces/{ns}/keys/{key}` | `consistency=linearizable` | Value + revision or 404 | Minority cannot serve an authoritative linearizable read |
| `DELETE /namespaces/{ns}/keys/{key}` | — | `204` + deletion revision | V when conditional; create tombstone/event |
| `POST /namespaces/{ns}/transactions` | `{compare:[...],success:[...],failure:[...]}` | `{succeeded,revision,results}` | I; bounded transaction within supported shard/group |
| `GET /namespaces/{ns}/ranges?prefix=&after=` | Snapshot revision | Ordered page + revision | Continue at same revision or fail explicitly if compacted |
| `GET /namespaces/{ns}/watch?fromRevision=` | Resume revision | Ordered events per supported range | 410 when retention no longer supports resume |
| `POST /namespaces` | `{name,quota,replicationPolicy}` | `202 operation` | I; administrative placement and capacity |

#### Data model — L4

```text
Namespace catalog:
  PK (tenant, namespace) -> quota, placement_group, configuration_epoch
Replicated log:
  PK (group_id, log_index) -> term, command_id, compare_set, mutation_set
MVCC record:
  PK (tenant, namespace, key_bytes, revision) -> value_bytes, tombstone,
    create_revision, mod_revision, lease_id
Current-key index:
  (tenant, namespace, key_bytes) -> newest committed revision
Command replay:
  (tenant, caller, command_id) -> request_hash, committed_revision, response
Watch history:
  (group_id, revision, event_ordinal) -> key, event_type, value_ref
Snapshot:
  group_id, applied_index, term, membership_epoch, compacted_revision, checksum
```

- **Relationships:** namespace → one or more placement groups; key → ordered MVCC versions; command → one committed result.
- **Access:** point lookup by current index; prefix scan in key order at a fixed revision; watch by revision.
- **Invariant:** apply a log entry once to the state machine; acknowledge only according to the chosen consensus commit rule.
- **Revision scope:** revisions are group-local unless a global sequencer or coordinated transaction layer is explicitly added.
- **Retention:** compaction keeps versions needed by supported snapshots/watch retention; return a typed error when an old revision is gone.

#### L5 extra

- Leader-local memory reads need a validated leadership/read-index mechanism to claim linearizability.
- Cross-shard transactions require coordination; do not imply a bounded single-group transaction provides them.
- Resharding must preserve key ownership epochs and invalidate or translate affected cursors.

#### Trap points

- `R + W > N` alone is not a complete linearizability design.
- An eventual cache in front of the store breaks an unqualified linearizable-read contract.
- A watch reports retained changes; it is not a perpetual snapshot or proof every consumer applied them.

<a id="platform-5"></a>

### 3.5 Distributed leases, locks, and leader election — P1

- **Bank:** [1infra+ #5](../../1o/2.sd/2.sd.md#1infra-plus); **source:** Prior supplemental bank + recruiter concepts; **type:** LLD + HLD.

- **L4 model:** one scoped lock has a durable increasing fence and a time-bounded authenticated holder.

#### API design — L4

| Operation | Request | Result | Contract |
|---|---|---|---|
| `POST /locks/{resource}/acquisitions` | `{leaseSeconds,waitMs}` | `201 {leaseId,fence,expiresAt}` or `409 LOCKED` | I; bound waiting; server/consensus time determines expiry |
| `PUT /leases/{id}/renewal` | `{fence,renewalSeq,leaseSeconds}` | `200 {expiresAt}` | Verify owner, current fence, unexpired lease; sequence deduplicates renewal |
| `DELETE /leases/{id}` | `X-Fencing-Token: <fence>` | `204` | Proposed header; verify ownership; stale release cannot remove a new holder |
| `GET /locks/{resource}` | — | Redacted holder status + fence | Observation is not a grant |
| `GET /locks/{resource}/events?afterRevision=` | Resume revision | Release/change stream | Wake-up hint; callers still acquire atomically |
| Internal protected write | `{resource,fence,operationId,value}` | Committed result or `409 STALE_FENCE` | Target atomically checks accepted fencing high-water mark |

#### Data model — L4

```sql
CREATE TABLE distributed_locks (
  tenant_id text NOT NULL, resource text NOT NULL, fence bigint NOT NULL DEFAULT 0,
  lease_id text, holder_id text, lease_until timestamptz, renewal_seq bigint NOT NULL DEFAULT 0,
  PRIMARY KEY (tenant_id, resource), UNIQUE (tenant_id, lease_id)
);
CREATE INDEX lock_expiry ON distributed_locks (lease_until) WHERE holder_id IS NOT NULL;
CREATE TABLE protected_records (
  tenant_id text NOT NULL, resource text NOT NULL, last_fence bigint NOT NULL,
  value jsonb NOT NULL, version bigint NOT NULL,
  PRIMARY KEY (tenant_id, resource)
);
```

- **SQL variant:** acquisition atomically checks absent/expired holder, increments `fence`, sets owner and expiry, and returns the grant.
- **Consensus variant:** encode the same ownership transitions as commands in a replicated state machine.
- **Access:** lock lookup by scoped resource; renew/release by tenant + lease ID; expiry sweep by deadline.
- **Invariant:** do not delete/reset a lock's fencing counter when releasing it; retain a tombstone/high-water mark through recreation and recovery.
- **Target write:** compare fence and mutate protected state in one target-side transaction; equal fences permit multiple operations from the same holder, each deduplicated by operation ID as needed.

#### L5 extra

- The target rejects an old fence after it has observed a newer one; a fencing token alone does not prove an otherwise-current holder has not expired.
- If expiry must immediately prohibit all writes, the target needs a lease/authority check or synchronized epoch barrier in addition to its high-water mark.
- Leader election grants authority over a specific protected scope; loss of majority/lease must stop new authoritative work.

#### Trap points

- A timed-out or paused process can continue after its lease expires.
- Replaying an acquisition result after expiry does not renew its authority; return/check the original expiry and use a new intent to reacquire.
- A release event does not reserve the lock for the watcher that saw it first.

<a id="platform-6"></a>

### 3.6 Durable distributed event log — P1

- **Bank:** [1infra+ #6](../../1o/2.sd/2.sd.md#1infra-plus); **source:** Prior supplemental bank; prep addition; **type:** HLD.

- **L4 model:** topic partitions own append order; consumer groups track assignment generations and committed offsets.
- **Protocol:** the following is a proposed API vocabulary; production Kafka normally uses its native binary protocol, not these REST paths.

#### API design — L4

| Operation | Request | Result | Contract |
|---|---|---|---|
| `POST /topics` | `{name,partitions,replication,retention}` | `202 operation` | I; administrative quotas |
| `POST /topics/{id}/partitions/{p}/records` | `{producerId,epoch,firstSeq,records}` | `{baseOffset,lastOffset,leaderEpoch}` | Durable acknowledgment policy and producer deduplication |
| `GET /topics/{id}/partitions/{p}/records?offset=&maxBytes=` | Bounded read | `{records,nextOffset,highWatermark}` | `410 OFFSET_EXPIRED` or equivalent typed native error |
| `POST /consumer-groups/{id}/memberships` | `{memberId,subscriptions}` | `{generation,assignment,heartbeatDeadline}` | Group coordinator owns assignment |
| `PUT /consumer-groups/{id}/members/{member}/heartbeat` | `{generation}` | Liveness acknowledgment | Reject stale generation |
| `PUT /consumer-groups/{id}/offsets` | `{generation,offsets:[...]}` | Commit result | Check current member's partition ownership |
| `PATCH /topics/{id}` | `{retention,partitionCount?}` | `202 operation` | V; partition changes affect routing/ordering scope |

#### Data model — L4

```text
Controller metadata:
  PK (tenant, topic_id, partition) -> leader, replicas, in_sync_replicas, leader_epoch
Partition segment:
  file identity (topic_id, partition, base_offset)
  batch = base_offset, length, CRC, producer_id, producer_epoch, first_sequence, records[]
  record = relative_offset, timestamp, key_bytes, value_bytes, bounded_headers
Sparse indexes:
  offset -> byte_position; event_time -> approximate_offset
Producer state:
  PK (partition, producer_id) -> epoch, last_sequence, last_acknowledged_offset
Consumer group:
  PK (tenant, group_id) -> generation, protocol, members, assignment
Offset state:
  PK (tenant, group_id, topic_id, partition) -> next_offset, group_generation
Transaction state, if supported:
  transaction_id -> producer_epoch, involved_partitions, status, commit_markers
```

- **Access:** append/fetch one partition; replay by offset; group offsets by partition; management metadata by topic.
- **Durability:** acknowledge according to replication/commit policy; controller epochs fence stale leaders.
- **Retention:** segment deletion expires offsets; compaction preserves latest keyed state under a separate tombstone-retention policy.
- **Invariant:** consumer offset is the next record to process, not the last fetched record; commit only after the defined processing boundary.

#### L5 extra

- Record order is partition-local; increasing partition count can remap keys and requires an ordering migration policy.
- Broker idempotent production does not deduplicate an arbitrary producer application that invents a new logical event ID.
- Atomic consume-transform-produce is limited to a supported transaction domain; external database effects need their own atomic offset/effect or deduplication design.

#### Trap points

- Advancing offsets before effects commit loses work after a crash.
- Advancing offsets after effects commit can repeat effects; define deduplication.
- Committing with a stale consumer generation can overwrite the new owner's progress unless fenced.

<a id="business"></a>

## 2business

<a id="business-1"></a>

### 4.1 Healthcare data ingestion — P1

- **Bank:** [2business #1](../../1o/2.sd/2.sd.md#2business); **source:** 1p3a; **type:** HLD.

- **L4 model:** a source submits immutable input batches; processing results preserve source identity, schema version, lineage, and replay state.
- **Boundary:** these are proposed ingestion APIs, not claims of FHIR-compatible endpoint semantics.

#### API design — L4

| Operation | Request | Result | Contract |
|---|---|---|---|
| `POST /ingest-sources` | `{name,schemaRef,credentialRef}` | `201 source` | I; administrator authorizes source namespace |
| `POST /ingest-runs` | `{sourceId,sourceBatchId,schemaVersion,objectRef,sha256}` | `202 {runId,operationId}` | I; verify blob ownership, completeness, and checksum |
| `POST /ingest-sources/{id}/record-batches` | `{batchId,schemaVersion,records}` | `202 run` | Alternate bounded streaming input; source event identities retained |
| `GET /ingest-runs/{id}` | — | `{state,received,validated,applied,failed,watermark}` | Counters distinguish acceptance from domain application |
| `GET /ingest-runs/{id}/errors?after=` | — | Redacted per-record errors | Restricted role; no unnecessary sensitive values |
| `POST /ingest-runs/{id}/replays` | `{recordIds?,transformVersion,reason}` | `202 replay run` | I; parent lineage and original record identities retained |
| `GET /clinical-records?subjectId=&after=` | Authorized subject/time filters | Normalized record page | Fine-grained access and audit; no bulk export by ordinary reader |

#### Data model — L4

```sql
CREATE TABLE ingest_sources (
  tenant_id text NOT NULL, source_id text NOT NULL, name text NOT NULL,
  schema_ref text NOT NULL, credential_ref text NOT NULL,
  PRIMARY KEY (tenant_id, source_id), UNIQUE (tenant_id, name)
);
CREATE TABLE ingest_runs (
  tenant_id text NOT NULL, run_id text NOT NULL, source_id text NOT NULL,
  source_batch_id text NOT NULL, transform_version text NOT NULL,
  schema_version text NOT NULL, raw_object_ref text NOT NULL, payload_hash text NOT NULL,
  parent_run_id text, state text NOT NULL, accepted_at timestamptz NOT NULL,
  PRIMARY KEY (tenant_id, run_id),
  UNIQUE (tenant_id, source_id, source_batch_id, transform_version),
  FOREIGN KEY (tenant_id, source_id) REFERENCES ingest_sources
);
CREATE TABLE ingest_record_results (
  tenant_id text NOT NULL, run_id text NOT NULL, record_id text NOT NULL,
  state text NOT NULL, error_code text, output_ref text,
  PRIMARY KEY (tenant_id, run_id, record_id),
  FOREIGN KEY (tenant_id, run_id) REFERENCES ingest_runs
);
CREATE INDEX ingest_failed_records ON ingest_record_results (tenant_id, run_id, record_id)
  WHERE state = 'FAILED';
CREATE TABLE clinical_records (
  tenant_id text NOT NULL, source_id text NOT NULL, source_record_id text NOT NULL,
  source_version bigint NOT NULL, transform_version text NOT NULL,
  subject_token text NOT NULL, observed_at timestamptz NOT NULL,
  encrypted_payload_ref text NOT NULL, lineage_run_id text NOT NULL,
  PRIMARY KEY (tenant_id, source_id, source_record_id, source_version, transform_version)
);
CREATE INDEX clinical_subject ON clinical_records
  (tenant_id, subject_token, observed_at, source_record_id);
```

- **Relationships:** source → many runs; run → many record results; normalized versions retain source and transformation lineage.
- **Storage:** raw/encrypted payloads in object storage; operational SQL stores bounded metadata and redacted errors.
- **Subject identity:** trusted tokenization/mapping service supplies stable subject tokens; an unsalted hash of an identifier is not sufficient privacy protection.
- **Invariant:** replaying one source version with one transformation version must not append duplicate domain effects; “current” projections advance only under explicit source-version rules.
- **Partition/retention:** partition results by run/time when needed; raw records, errors, and normalized history have independent policy-driven retention.

#### L5 extra

- Source ordering, clinical event time, and ingestion time are different; preserve all required timestamps instead of choosing last-arrival-wins.
- Quarantine invalid records and continue independent valid ones only when the domain permits partial application.
- Track deletion/correction requests through raw, normalized, indexed, and archived copies using lineage.

#### Trap points

- Replaying a DLQ with new identities can duplicate clinical observations.
- A successful HTTP batch response does not mean all records became queryable.
- Error messages and metrics labels can leak the same sensitive data that the main store encrypts.

<a id="business-2"></a>

### 4.2 Chat with durable delivery and offline users — P1

- **Bank:** [2business #2](../../1o/2.sd/2.sd.md#2business); **source:** 1p3a; **type:** HLD.

- **L4 model:** conversations own ordered messages; membership controls access; per-device cursors track replay and delivery.

#### API design — L4

| Operation | Request | Result | Contract |
|---|---|---|---|
| `POST /conversations` | `{type,members}` | `201 conversation` | I; creator permissions and direct/group policy |
| `POST /conversations/{id}/messages` | `{clientMessageId,body,attachmentRefs}` | `201 {messageId,sequence}` | Sender inferred from auth; acknowledgment after durable commit |
| `GET /conversations/{id}/messages?afterSeq=&limit=` | — | `{items,nextSeq}` | Membership and history-visibility policy |
| `PUT /conversations/{id}/receipts/{device}` | `{deliveredThrough,readThrough}` | `200 receipt` | Device owner; monotonically advance valid contiguous cursors |
| `PUT /conversations/{id}/members/{user}` | `{role}` | `200 membership` | V; administrator and tenant boundary |
| `DELETE /conversations/{id}/members/{user}` | — | `204` | V; removal invalidates future delivery authorization |
| Native WebSocket | `{resumeCursors}`; send/ack/presence events | Server message sequence + ack | Same send deduplication as REST; reconnect through durable history |

#### Data model — L4

```sql
CREATE TABLE conversations (
  tenant_id text NOT NULL, conversation_id text NOT NULL, kind text NOT NULL,
  last_sequence bigint NOT NULL DEFAULT 0, membership_version bigint NOT NULL,
  PRIMARY KEY (tenant_id, conversation_id)
);
CREATE TABLE conversation_members (
  tenant_id text NOT NULL, conversation_id text NOT NULL, user_id text NOT NULL,
  role text NOT NULL, joined_sequence bigint NOT NULL, left_sequence bigint,
  version bigint NOT NULL,
  PRIMARY KEY (tenant_id, conversation_id, user_id),
  FOREIGN KEY (tenant_id, conversation_id) REFERENCES conversations
);
CREATE TABLE chat_messages (
  tenant_id text NOT NULL, conversation_id text NOT NULL, sequence bigint NOT NULL,
  message_id text NOT NULL, sender_id text NOT NULL, client_message_id text NOT NULL,
  payload_ref text NOT NULL, created_at timestamptz NOT NULL, tombstone boolean NOT NULL DEFAULT false,
  PRIMARY KEY (tenant_id, conversation_id, sequence),
  UNIQUE (tenant_id, conversation_id, sender_id, client_message_id),
  UNIQUE (tenant_id, conversation_id, message_id),
  FOREIGN KEY (tenant_id, conversation_id) REFERENCES conversations
);
CREATE TABLE chat_receipts (
  tenant_id text NOT NULL, conversation_id text NOT NULL, user_id text NOT NULL,
  device_id text NOT NULL, delivered_through bigint NOT NULL, read_through bigint NOT NULL,
  PRIMARY KEY (tenant_id, conversation_id, user_id, device_id),
  FOREIGN KEY (tenant_id, conversation_id, user_id) REFERENCES conversation_members,
  CHECK (read_through <= delivered_through)
);
CREATE INDEX memberships_user ON conversation_members (tenant_id, user_id, conversation_id);
```

- **Transaction:** check membership, deduplicate sender intent, allocate conversation sequence, append message, and emit delivery outbox.
- **Access:** partition messages by conversation; ascending sequence handles catch-up; membership index builds a user's conversation list.
- **Runtime:** `presence:{tenant:user:device} → connectionRoute,expiresAt`; presence is approximate and does not own message durability.
- **Attachments:** upload using [resumable upload](#infra-9); authorize references before message publication.
- **Retention:** preserve tombstone/sequence semantics so deletion does not confuse contiguous-delivery cursors.

#### L5 extra

- A very large conversation makes one SQL sequence row hot; move sequence ownership to a partition leader without changing the per-conversation contract.
- Fanout-on-write helps small groups; large groups may fan out read pointers rather than duplicate full payloads.
- Membership changes and reconnects require generation-aware delivery checks; cached authorization can leak post-removal messages.

#### Trap points

- WebSocket transmission is not durable recipient delivery.
- Client timestamps do not establish message order.
- At-least-once transport plus a new clientMessageId on every retry still creates duplicate messages.

<a id="business-3"></a>

### 4.3 Uber — matching, live locations, and trips — P1

- **Bank:** [2business #3](../../1o/2.sd/2.sd.md#2business); **source:** 1p3a ×2; **type:** HLD.

- **L4 model:** geo state supplies candidates; a transactional trip/driver state machine makes the final assignment authoritative.

#### API design — L4

| Operation | Request | Result | Contract |
|---|---|---|---|
| `POST /ride-quotes` | `{pickup,dropoff,rideType}` | `201 {quoteId,amountMinor,currency,expiresAt}` | Server-priced, bounded lifetime |
| `POST /ride-requests` | `{quoteId,pickup,dropoff}` | `202 {tripId,state:'MATCHING'}` | I; rider identity from auth; validate quote and scope |
| Driver `PUT /drivers/{id}/location` | `{sessionEpoch,seq,lat,lon,capturedAt}` | `200 {acceptedSeq}` | Authenticated driver; latest projection, not a durability promise for full history |
| Driver `PUT /drivers/{id}/availability` | `{state}` | `200 driver` | V; cannot advertise AVAILABLE while an active trip owns the driver |
| Driver `POST /trip-offers/{id}/acceptances` | `{expectedTripVersion}` | `200 trip` or `409 OFFER_LOST` | I; atomically claim both trip and driver |
| `POST /trips/{id}/transitions` | `{expectedVersion,event}` | `200 trip` | I; actor-specific valid transitions only |
| `GET /trips/{id}` | — | Authorized trip view | Rider/assigned driver only; hide unrelated live locations |
| `POST /trips/{id}/cancellations` | `{reason,expectedVersion}` | `200/202 cancellation` | I; state and fee rules explicit |

#### Data model — L4

```sql
CREATE TABLE ride_quotes (
  tenant_id text NOT NULL, quote_id text NOT NULL, rider_id text NOT NULL,
  amount_minor bigint NOT NULL CHECK (amount_minor >= 0), currency char(3) NOT NULL,
  route_hash text NOT NULL, expires_at timestamptz NOT NULL,
  PRIMARY KEY (tenant_id, quote_id)
);
CREATE TABLE ride_drivers (
  tenant_id text NOT NULL, driver_id text NOT NULL, state text NOT NULL, version bigint NOT NULL,
  PRIMARY KEY (tenant_id, driver_id)
);
CREATE TABLE trips (
  tenant_id text NOT NULL, trip_id text NOT NULL, rider_id text NOT NULL,
  driver_id text, quote_id text NOT NULL, state text NOT NULL, version bigint NOT NULL,
  pickup jsonb NOT NULL, dropoff jsonb NOT NULL, created_at timestamptz NOT NULL,
  PRIMARY KEY (tenant_id, trip_id),
  FOREIGN KEY (tenant_id, quote_id) REFERENCES ride_quotes,
  FOREIGN KEY (tenant_id, driver_id) REFERENCES ride_drivers
);
CREATE UNIQUE INDEX driver_one_trip ON trips (tenant_id, driver_id)
  WHERE state IN ('ASSIGNED','ARRIVING','IN_PROGRESS');
CREATE INDEX trips_rider ON trips (tenant_id, rider_id, created_at DESC, trip_id);
CREATE TABLE trip_offers (
  tenant_id text NOT NULL, offer_id text NOT NULL, trip_id text NOT NULL,
  driver_id text NOT NULL, expires_at timestamptz NOT NULL, state text NOT NULL,
  PRIMARY KEY (tenant_id, offer_id),
  FOREIGN KEY (tenant_id, trip_id) REFERENCES trips,
  FOREIGN KEY (tenant_id, driver_id) REFERENCES ride_drivers
);
```

```text
Latest location: (tenant, driver) -> session_epoch, seq, lat, lon, received_at; short freshness TTL
Geo candidate index: (region, cell) -> driver IDs with freshness/session metadata
Location history: partition by driver/time bucket; append asynchronously under explicit retention
```

- **State:** `MATCHING → ASSIGNED → ARRIVING → IN_PROGRESS → COMPLETED`; cancellation rules depend on current state.
- **Assignment transaction:** verify offer expiry and trip version; claim AVAILABLE driver; attach it to the trip; emit outbox event.
- **Access:** geo query returns candidates, followed by exact distance/freshness filtering and authoritative availability check.

#### L5 extra

- Query all cells intersecting the search radius; a fixed neighbor count is not correct for every radius/resolution.
- Scope matching to regions/cells for locality; boundary handoff must preserve authoritative driver ownership.
- Payment uses a separate idempotent settlement operation keyed by trip, with recoverable compensation for failures.

#### Trap points

- “Nearby and available in Redis” is not an atomic assignment.
- Two offers accepted concurrently must not assign one driver to two trips.
- Reordered location updates can move a driver backward unless fenced by session and sequence.

<a id="business-4"></a>

### 4.4 Global video streaming — P2

- **Bank:** [2business #4](../../1o/2.sd/2.sd.md#2business); **source:** 1p3a; **type:** HLD.

- **L4 model:** uploaded source versions generate immutable renditions; one published manifest identifies the ready playback version.

#### API design — L4

| Operation | Request | Result | Contract |
|---|---|---|---|
| `POST /videos` | `{title,visibility}` | `201 {videoId}` | I; creator ownership |
| `POST /videos/{id}/uploads` | `{sizeBytes,sha256}` | Upload session | I; reuse part/resume protocol from [upload](#infra-9) |
| `POST /videos/{id}/processing-runs` | `{sourceObjectVersion,profileSet}` | `202 operation` | I; pin immutable input and transcoding profile version |
| `GET /videos/{id}` | — | `{state,metadata,availableRenditions}` | Only published authorized versions appear playable |
| `POST /videos/{id}/playback-sessions` | `{deviceCapabilities}` | `201 {manifestUrl,expiresAt}` | Entitlement check; short-lived scoped CDN access |
| CDN `GET /media/{video}/{version}/manifest` | Playback authorization | HLS/DASH manifest | Manifest references immutable rendition segments |
| CDN `GET /media/{video}/{version}/{rendition}/{segment}` | Playback authorization | Media bytes | Range support where format/storage permits |
| `DELETE /videos/{id}` | — | `202 removal operation` | V; revoke discoverability/access and schedule CDN/blob cleanup |

#### Data model — L4

```sql
CREATE TABLE videos (
  tenant_id text NOT NULL, video_id text NOT NULL, owner_id text NOT NULL,
  title text NOT NULL, visibility text NOT NULL, state text NOT NULL,
  published_version bigint, version bigint NOT NULL, created_at timestamptz NOT NULL,
  PRIMARY KEY (tenant_id, video_id)
);
CREATE INDEX videos_owner ON videos (tenant_id, owner_id, created_at DESC, video_id);
CREATE TABLE video_versions (
  tenant_id text NOT NULL, video_id text NOT NULL, media_version bigint NOT NULL,
  source_ref text NOT NULL, source_hash text NOT NULL, profile_version text NOT NULL,
  state text NOT NULL, manifest_ref text,
  PRIMARY KEY (tenant_id, video_id, media_version),
  FOREIGN KEY (tenant_id, video_id) REFERENCES videos
);
CREATE TABLE video_renditions (
  tenant_id text NOT NULL, video_id text NOT NULL, media_version bigint NOT NULL,
  rendition_id text NOT NULL, codec text NOT NULL, bitrate_bps bigint NOT NULL,
  width integer NOT NULL, height integer NOT NULL, playlist_ref text NOT NULL,
  state text NOT NULL,
  PRIMARY KEY (tenant_id, video_id, media_version, rendition_id),
  FOREIGN KEY (tenant_id, video_id, media_version) REFERENCES video_versions
);
```

- **Blob layout:** `media/{tenant}/{video}/{mediaVersion}/{rendition}/{segment}`; manifests record segment order/durations and object hashes as needed.
- **Access:** video metadata by ID/owner; immutable manifests and segments through CDN; processing progress through operation records.
- **Invariant:** publish a manifest only after all required referenced artifacts are durable and validated.
- **Retention:** preserve source/previous versions according to product policy; garbage-collect only versions with no live manifest/session/retention reference.

#### L5 extra

- Processing retries deduplicate by source version and profile version; partial renditions do not make the whole video ready.
- A deleted entitlement may remain usable until a signed URL expires unless the CDN performs an online or versioned authorization check.
- Multi-region origin copies must preserve immutable version identity; a replica lagging one rendition cannot safely serve a manifest that references it.

#### Trap points

- A successful upload is not a playable video.
- Long-lived public segment URLs can bypass the authorization check on the metadata API.
- Overwriting segments behind an unchanged manifest URL creates inconsistent CDN cache contents.

<a id="business-5"></a>

### 4.5 URL shortener — P2

- **Bank:** [2business #5](../../1o/2.sd/2.sd.md#2business); **source:** 1p3a; **type:** HLD.

- **L4 model:** globally routable short-code identity maps to an owner-controlled destination; analytics are asynchronous.

#### API design — L4

| Operation | Request | Result | Contract |
|---|---|---|---|
| `POST /links` | `{destination,customCode?,expiresAt?}` | `201 {linkId,shortUrl}` | I; validate allowed URL schemes and custom-code uniqueness |
| Public `GET /s/{code}` | — | `302 Location: destination` | Resolve host+code; 404/410 for missing/expired under policy |
| Public `HEAD /s/{code}` | — | Same redirect headers, no body | Define analytics handling for bots/previews |
| `GET /links/{id}` | — | Management metadata + ETag | Authenticated owner; destination visibility policy |
| `PATCH /links/{id}` | `{destination?,expiresAt?}` | `200 link` | V; mutable destinations require bounded redirect caching |
| `DELETE /links/{id}` | — | `204` | V; tombstone instead of immediate code reuse |
| `GET /links/{id}/analytics?from=&to=` | Bounded range | Aggregated counts + watermark | Owner access; counts need not be exact billing data |

#### Data model — L4

```sql
CREATE TABLE short_links (
  tenant_id text NOT NULL, link_id text NOT NULL, owner_id text NOT NULL,
  domain text NOT NULL, code text NOT NULL, destination text NOT NULL,
  state text NOT NULL, expires_at timestamptz, version bigint NOT NULL,
  created_at timestamptz NOT NULL,
  PRIMARY KEY (tenant_id, link_id), UNIQUE (domain, code)
);
CREATE INDEX short_links_owner ON short_links (tenant_id, owner_id, created_at DESC, link_id);
CREATE TABLE link_click_rollups (
  tenant_id text NOT NULL, link_id text NOT NULL, bucket_start timestamptz NOT NULL,
  coarse_region text NOT NULL, click_count bigint NOT NULL CHECK (click_count >= 0),
  PRIMARY KEY (tenant_id, link_id, bucket_start, coarse_region),
  FOREIGN KEY (tenant_id, link_id) REFERENCES short_links
);
```

- **Global lookup:** `(domain,code)` is unique because a public redirect has no authenticated tenant context to disambiguate it.
- **Cache:** `(domain,code) → destination,state,expiresAt,version`; bounded positive/negative TTL and invalidation.
- **Analytics log:** `{eventId,linkId,timeBucket,coarseRegion}`; avoid retaining raw sensitive request information unnecessarily.
- **Invariant:** commit code uniqueness before returning the short URL; generated-code collisions retry allocation without changing user intent.

#### L5 extra

- Choose 301/308 only for a genuinely permanent redirect contract; those cache semantics make later destination edits difficult.
- Random codes need a uniqueness constraint; block-allocated IDs need durable allocation and predictable-enumeration consideration.
- Deduplicate analytics by event identity if exact event counts matter; separate human clicks from previews where feasible.

#### Trap points

- Tenant-scoped code uniqueness is insufficient on a shared public hostname.
- Immediately reusing deleted codes can redirect old bookmarks to a new owner's site.
- GET logging is an incidental effect; it must not make redirect success depend on the analytics pipeline.

<a id="business-6"></a>

### 4.6 E-commerce recommendations from browsing history — P2

- **Bank:** [2business #6](../../1o/2.sd/2.sd.md#2business); **source:** 1p3a; **type:** HLD.

- **L4 model:** immutable behavior events feed versioned features/models; recommendation responses log what was actually shown.

#### API design — L4

| Operation | Request | Result | Contract |
|---|---|---|---|
| `POST /behavior-events` | `{events:[{eventId,itemId,eventType,occurredAt,impressionId?}]}` | `202 {acceptedIds}` | Authenticated subject; bounded batch and event deduplication |
| `POST /recommendation-queries` | `{surface,limit,context}` | `200 {requestId,modelVersion,items:[{itemId,reasonCode}]}` | Subject from auth; server-capped candidates and latency budget |
| `POST /recommendation-impressions` | `{requestId,items:[{itemId,position}]}` | `202` | Record displayed items, not every generated candidate |
| `POST /recommendation-models` | `{artifactRef,featureSchemaVersion,trainingCutoff}` | `201 model` | I; operator-only immutable registry entry |
| `POST /recommendation-rollouts` | `{modelVersion,cohort,healthGates}` | `202 operation` | I; canary and fallback policy |
| `GET /recommendation-rollouts/{id}` | — | `{state,metrics,activeVersions}` | Operator view |
| `POST /recommendation-profile-deletions` | `{subjectRef,reason}` | `202 operation` | I; authorized privacy workflow across event/feature stores |

#### Data model — L4

```sql
CREATE TABLE recommendation_models (
  tenant_id text NOT NULL, model_id text NOT NULL, model_version bigint NOT NULL,
  artifact_ref text NOT NULL, feature_schema_version text NOT NULL,
  training_cutoff timestamptz NOT NULL, state text NOT NULL,
  PRIMARY KEY (tenant_id, model_id, model_version)
);
CREATE TABLE recommendation_impressions (
  tenant_id text NOT NULL, impression_id text NOT NULL, request_id text NOT NULL,
  subject_token text NOT NULL, item_id text NOT NULL, position integer NOT NULL,
  model_id text NOT NULL, model_version bigint NOT NULL, at timestamptz NOT NULL,
  PRIMARY KEY (tenant_id, impression_id),
  UNIQUE (tenant_id, request_id, item_id, position),
  FOREIGN KEY (tenant_id, model_id, model_version) REFERENCES recommendation_models
);
CREATE INDEX recommendation_attribution ON recommendation_impressions
  (tenant_id, subject_token, at, impression_id);
```

```text
Event log:
  key (tenant, subject_token); event_id, event_type, item_id, event_time,
  receive_time, impression_id, schema_version
Dedup store:
  (tenant, event_id) -> payload_hash, accepted_offset; TTL = supported retry/replay window
Online feature KV:
  (tenant, subject_token, feature_schema_version) -> features, event_watermark, updated_at
Item candidate index:
  (tenant, index_generation, item_id) -> embedding, category, eligibility_version
Serving pointer:
  (tenant, surface, cohort) -> model_version, feature_schema_version, index_generation
```

- **Relationships:** impressions join later clicks/purchases for attribution; model, feature schema, and candidate index versions form one compatible serving configuration.
- **Access:** recent subject history/features; candidate retrieval by compatible index; item eligibility against current catalog rules.
- **Retention:** behavior, impressions, and features have separate retention; deletion workflows require lineage through derived stores.
- **Invariant:** pin the serving versions for a request; log the version used, even when a fallback served the result.

#### L5 extra

- Fresh item availability and access restrictions filter model candidates; a good score does not authorize or make an item purchasable.
- Handle cold start and unavailable features with bounded fallback candidates; distinguish fallback traffic in metrics.
- Event-time watermarks and training cutoffs prevent future information leaking into offline evaluation.

#### Trap points

- Logging every generated recommendation as an impression corrupts feedback labels.
- Unversioned feature changes can silently feed incompatible input to a model.
- Online training on every HTTP request is not necessary to provide fresh recommendations and couples serving latency to training failures.

## References

- [Oracle question bank and provenance](../../1o/2.sd/2.sd.md).
- [Existing full-design packets](../../1o/2.sd/): vocabulary and domain context; the contracts here resolve shortcuts such as ETag-as-MD5, cross-resource If-Match, and unrestricted exactly-once claims.
- [RFC 9110 — HTTP semantics](https://httpwg.org/specs/rfc9110.html): methods, statuses, validators, and redirects.
- [RFC 9457 — Problem Details](https://www.rfc-editor.org/rfc/rfc9457): JSON error contract.
- [PostgreSQL constraints](https://www.postgresql.org/docs/current/ddl-constraints.html): keys, uniqueness, checks, and foreign keys.
- [PostgreSQL INSERT / ON CONFLICT](https://www.postgresql.org/docs/current/sql-insert.html): atomic uniqueness arbitration.
- [OCI Certificates overview](https://docs.oracle.com/en-us/iaas/Content/certificates/overview.htm): certificate/CA/bundle lifecycle context.
- [OCI asynchronous work requests](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/workrequests.htm): actual OCI operation-tracking conventions.
- [RFC 5280 — X.509 certificates and CRLs](https://www.rfc-editor.org/rfc/rfc5280): certificate identity, issuer constraints, serials, and CRL validation.
- [RFC 6960 — OCSP](https://www.rfc-editor.org/rfc/rfc6960): wire formats and status semantics; consult its listed updates for a concrete nonce/profile implementation.
- [etcd 3.6 API guarantees](https://etcd.io/docs/v3.6/learning/api_guarantees/): consistency, revisions, and watch boundaries.
- [Apache Kafka 4.1 design](https://kafka.apache.org/41/design/design/): partitioned logs, replication, and delivery semantics.
- **Reviewed:** 2026-09-08. Endpoint names, schemas, state machines, and defaults are interview design proposals; reference products define their own exact protocols.
