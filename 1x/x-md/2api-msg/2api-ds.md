# 2api-ds — API Design And Contracts

- **In plain words:** an API is a written promise between a server and its callers: which requests exist, what they carry, what comes back, and how it fails. Good design lets both sides change without breaking each other.
- `-ds` = design file. Merged 2026-11-15 from `2api-design.md` (moved from `1sd/00.base`), `2api.md` (API design + estimation toolkit) and `2rest-ds.md` (contract design)
- Protocol mechanics: [2rest101.md](2rest101.md), [2rest-gql.md](2rest-gql.md), [2rest-grpc-websocket.md](2rest-grpc-websocket.md); messaging payloads: [3messaging.md](3messaging.md)

## Index

- [0. One-Minute Version](#b0)
- [1. Core Concepts](#a1)
- [2. Designing An API Surface](#b-surface)
- [3. HTTP Methods](#a2)
- [4. How Servers Run Requests: Threads](#a3)
- [5. Resource Paths, Variables And Params](#a4)
- [6. POST vs PUT vs PATCH](#a5)
- [7. Request And Response Samples](#a6)
- [8. Field And Payload Rules](#b-fields)
- [9. Status Codes And Errors](#a7)
- [10. Pagination](#a8)
- [11. Idempotency, Concurrency And Long-Running Work](#b-safety)
- [12. Authentication And Authorization At The API](#b-auth)
- [13. Rate Limiting And Quotas](#b-rate)
- [14. Batch, Bulk, Files, Streaming](#b-bulk)
- [15. API Styles: REST, GraphQL, gRPC, WebSocket, SSE, Webhooks](#a9)
- [16. Versioning, Evolution And Contract Testing](#a11)
- [17. Serialization](#a12)
- [18. Worked API Surfaces](#b-worked)
- [19. Frameworks And Tools](#a13)
- [20. Failure Modes](#b-fail)
- [21. Interview Questions And Pitfalls](#a14)
- [Part B — Estimation Toolkit](#h-est)
  - [22. Numbers To Memorize](#est22)
  - [23. Formulas](#est23)
  - [24. Worked Estimates](#est24)
- [25. Where This Fits](#b-fits)
- [References](#refs)

---

<a id="b0"></a>
## 0. One-Minute Version

- **Every requirement gets an API, every API maps to a requirement**: check this out loud
- **Default style**: REST + JSON externally, gRPC internally, SSE / WebSocket / webhooks for push
- **Five things every write API needs**: idempotency key, validation, clear status codes, a stable error format, auth
- **Lists use cursor pagination**; long work returns **202 + an operation id**; edits use **ETag / If-Match**
- **Contract-first, evolve additively**: breaking changes get a new version and a deprecation window
- **Estimation** is the other half of the first 10 minutes (Part B)
- 🗣 "I'll map each requirement to an endpoint, design the contract first from the client's use cases, evolve it only additively, then size the system."


---

<a id="a1"></a>
## 1. Core Concepts ★★★

- **In plain words:** an API is a promise: "send me this shape, I'll do this and send back that shape, and fail in these named ways."
- The contract covers: operations, inputs, outputs, errors, side effects
- **Safe:** does not change state (GET, HEAD, OPTIONS)
- **Idempotent:** calling it N times has the same effect as once (GET, PUT, DELETE); makes retries safe
- **Pagination:** never return an unbounded list
- **Versioning:** clients must not break when the API changes; plan it from day one


---

<a id="b-surface"></a>
## 2. Designing An API Surface ★★★

- **In plain words:** list what users need to do, give each action one endpoint, then add the cross-cutting pieces every endpoint needs.

### 2.1 Requirement → Endpoint Mapping

1. Write the functional requirements as user actions
2. One endpoint (or RPC) per action
3. Name the resource and method
4. Define request fields, response fields, errors
5. Add cross-cutting pieces: auth, idempotency, pagination, rate limits
6. Read the list back against the requirements

| Requirement | Endpoint | Notes |
|---|---|---|
| Guest searches listings | `GET /v1/listings?city=&check_in=&check_out=&guests=&cursor=` | Cursor pagination |
| Guest books a listing | `POST /v1/bookings` | Idempotency-Key; 201 or 409 |
| Guest views trips | `GET /v1/users/me/bookings?cursor=` | Read-your-writes |
| Guest cancels | `POST /v1/bookings/{id}:cancel` | Custom method, idempotent |
| Host updates calendar | `PATCH /v1/listings/{id}/calendar` | ETag / If-Match |

- 🗣 "Five requirements, five endpoints; let me check none is missing."

### 2.2 What Interviewers Check

- APIs match requirements (no extra, none missing)
- Correct HTTP semantics and status codes
- Idempotency for anything that creates or charges
- Pagination on every list
- Async work doesn't block the request

### 2.3 Contract-First vs Code-First

| Approach | How | Good at | Bad at |
|---|---|---|---|
| Contract-first | Write OpenAPI / SDL / `.proto`, generate server stubs and clients | Review before code; parallel client work; one source of truth | Extra step; generators can be clunky |
| Code-first | Annotate code (springdoc, FastAPI), generate the spec | Fast for one team | The API drifts toward internal models; leaks entities |

- Default: contract-first for public or cross-team APIs; code-first is fine inside one team, as long as the spec is published and reviewed


---

<a id="a2"></a>
## 3. HTTP Methods ★★★

- **In plain words:** the method is a one-word label on the request that tells everyone (server, caches, proxies, retry logic) what kind of action this is.

| Method | Meaning | Safe | Idempotent | Cacheable | Has body | Typical success |
|---|---|---|---|---|---|---|
| GET | Read a resource or list | Yes | Yes | Yes | No | 200 |
| HEAD | GET without the body (check exists, size, ETag) | Yes | Yes | Yes | No | 200 |
| POST | Create under a collection, or "process this" | No | No (yes with an idempotency key) | Rarely (only with explicit freshness headers; almost never done) | Yes | 201 / 200 / 202 |
| PUT | Replace the whole resource at this URI (or create it there) | No | Yes | No | Yes | 200 / 204 / 201 |
| PATCH | Change some fields | No | Not guaranteed | No | Yes | 200 / 204 |
| DELETE | Remove | No | Yes | No | Usually no | 204 / 200 / 202 |
| OPTIONS | What is allowed here (CORS preflight) | Yes | Yes | No | No | 204 |

- Source: RFC 9110 (HTTP Semantics, 2022) defines safe, idempotent and cacheable per method

### 3.1 How a method works internally

1. The method is just the first word of the request line: `GET /v1/orders/42 HTTP/1.1`
2. The server's router matches **(method, path template)** to one handler, e.g. `GET /orders/{id}` → `getOrder`
3. The handler runs; the method itself does nothing magic
4. The meaning matters to the **infrastructure around** the server
   - Caches and CDNs only store safe responses (GET / HEAD)
   - Browsers and HTTP clients may auto-retry idempotent requests on a dropped connection
   - Proxies and gateways apply rules per method (rate limits, auth scopes)

- Catch: these properties are promises *you* must keep; a `GET /deleteUser?id=1` works technically and gets crawled and cached

### 3.2 Are methods sync or async?

- **In plain words:** every HTTP method is request-then-response; "async" is a choice the server makes about *when the work happens*, not a property of the method.
- **Sync:** the server does the work, then responds (most GET, PUT, small POST)
- **Async:** the server records the job, responds `202 Accepted` with a status URL, and does the work later (exports, video upload processing, bulk DELETE)
- Rule of thumb: anything that can take longer than ~1 s, or depends on a slow third party, goes async (order of magnitude, depends on client timeouts)
- Separate idea: the server's **threading model** can be blocking or non-blocking (section 4); that is invisible to the client

### 3.3 Is GET the only cacheable method?

- In practice yes: GET and HEAD
- POST responses are cacheable by spec only with explicit freshness headers; CDNs and browsers almost never do it
- PUT, PATCH, DELETE are never cached; a successful one **invalidates** cached GETs of the same URI
- Workarounds when reads need a body (complex search): `POST /search` is not cached; cache in the app instead, or use GraphQL persisted queries over GET


---

<a id="a3"></a>
## 4. How Servers Run Requests: Threads ★★

- **In plain words:** either each request gets its own worker thread that waits while I/O happens, or a few threads juggle many requests and never wait.

| Server setup | Model | Default size | What happens on a slow DB call | Choose when |
|---|---|---|---|---|
| Spring Boot MVC on Tomcat | Thread per request (blocking) | 200 worker threads (`server.tomcat.threads.max`), extra connections queue | The thread sits blocked; at 200 slow calls, new requests queue | Default for most CRUD services |
| Spring MVC + virtual threads (Boot 3.2+, Java 21) | Thread per request, but threads are cheap | Thousands of virtual threads on few carrier threads | Virtual thread parks; the carrier thread serves others | Blocking code style with high concurrency |
| Spring WebFlux on Netty | Event loop (non-blocking) | About one loop thread per CPU core | Must use non-blocking drivers (R2DBC, WebClient); a blocking call freezes the loop | Streaming, very high fan-out I/O |
| FastAPI `async def` on Uvicorn | Event loop per worker process | 1 loop thread per process; scale with `--workers` | `await` yields to other requests; a blocking call inside `async def` freezes everything | I/O-heavy Python with async clients (httpx, asyncpg) |
| FastAPI plain `def` | Runs in a thread pool | AnyIO pool, 40 threads by default | Blocks one pool thread | Blocking libraries (requests, psycopg2) |

- How a Spring MVC request flows
  1. Tomcat's acceptor takes the connection
  2. A worker thread from the pool reads the request
  3. `DispatcherServlet` routes on (method, path) to your controller
  4. Your code runs on that thread, including DB calls
  5. Jackson writes the response; the thread returns to the pool
- Little's law sizing: in-flight = RPS × latency; 1,000 RPS × 0.2 s = 200 concurrent, exactly Tomcat's default
- Python catch: the GIL lets only one thread run Python bytecode at a time per process, so CPU-heavy work needs more processes, not more threads
- 🗣 "Spring MVC is thread-per-request with 200 Tomcat threads by default; virtual threads make that cheap. FastAPI runs async endpoints on an event loop and sync ones in a thread pool, so never block inside async def."


---

<a id="a4"></a>
## 5. Resource Paths, Variables And Params ★★★

- **In plain words:** the path names *which thing*, the query string says *how you want it* (filtered, sorted, paged, trimmed), the body carries *the thing itself*, and headers carry *metadata about the call*.

### 5.1 Words that get mixed up

| Term | Meaning | Example |
|---|---|---|
| Parameter | A named slot in a definition | `{orderId}` in the route, `limit` in the docs, `orderId` in the method signature |
| Argument | The actual value filled into a slot on one call | `42`, `20` |
| Path variable (path parameter) | A placeholder inside the path template, in `{}` | `/orders/{orderId}` called as `/orders/42` |
| Query parameter | `key=value` pairs after `?`, joined by `&` | `?status=shipped&limit=20` |
| Header | Metadata line on the request | `Authorization: Bearer …`, `If-None-Match: "v7"` |
| Body | The payload (JSON etc.) | `{"quantity": 2}` |

- `{}` is only documentation / routing syntax (OpenAPI, Spring, FastAPI); the wire just carries `/orders/42`
- In code
  - Spring: `@PathVariable Long orderId`, `@RequestParam int limit`, `@RequestBody OrderDto dto`, `@RequestHeader`
  - FastAPI: `def get(order_id: int, limit: int = 20, body: OrderIn | None = None)`; names in the path become path params, simple types become query params, Pydantic models become the body

### 5.2 Building the hierarchy

```text
/v1/users                          collection of users
/v1/users/{userId}                 one user (an object)
/v1/users/{userId}/orders          that user's orders (child collection)
/v1/users/{userId}/orders/{orderId}   one order of that user
/v1/users/{userId}/settings        singleton child (exactly one per user)
```

- A path segment adds a **resource**, never a field
  - Child path = an owned child collection or singleton with its own lifecycle
  - Field selection = a query param: `?fields=id,status,total` (sparse fieldsets; Google APIs call it a field mask)
- Keep nesting to about two levels; once a child has a global ID, also expose it flat: `/v1/orders/{orderId}`
- Filters belong in the query, not the path: `/orders?status=shipped`, not `/orders/shipped`
- Actions that aren't CRUD: Google's style is a custom method `POST /v1/orders/42:cancel`; others use `POST /v1/orders/42/cancellation`

### 5.3 Sub-resource or top-level, and IDs

- Sub-resource when the child only exists under the parent: `/v1/listings/{id}/reviews`
- Top-level when the child is queried on its own: `/v1/bookings` (by guest, by listing)
- IDs
  - Opaque strings, not auto-increment integers (no enumeration, no leaking volume)
  - Prefixed for readability: `bk_8Hq2...`; OCI uses OCIDs (`ocid1.instance.oc1...`)
- Naming: plural nouns, lowercase, one case style everywhere
- Cancel is a state transition, so it's a custom method on the booking, not a DELETE

### 5.4 How the pieces add up

```http
GET /v1/users/42/orders?status=shipped&fields=id,total&sort=-created_at&limit=20&cursor=eyJpZCI6OTl9 HTTP/1.1
Authorization: Bearer eyJhbGc...
Accept: application/json
```

| Part | Role here |
|---|---|
| `/v1` | API version |
| `/users/42/orders` | Which resource: user 42's order collection |
| `status=shipped` | Filter |
| `fields=id,total` | Which fields to return |
| `sort=-created_at` | Order, newest first |
| `limit`, `cursor` | Pagination (section 10) |
| Headers | Who is calling and what format they accept |

- Each concern is independent and additive: the path stays the same while filters, fields and pages change
- 🗣 "The path identifies the resource, the query shapes the read, the body is the representation, and headers carry auth, format, caching and idempotency."


---

<a id="a5"></a>
## 6. POST vs PUT vs PATCH ★★★

- **In plain words:** PUT means "make the thing at this exact address look like this"; POST means "here's some data, you decide what to do with it"; PATCH means "change just these fields."

| | POST | PUT | PATCH |
|---|---|---|---|
| Who picks the ID | Server | Client (it is in the URL) | Existing resource |
| Body | New item or command | The full representation | Only changed fields |
| Missing fields | N/A | Cleared or set to default | Left alone |
| Repeat the call | Creates a duplicate (unless idempotency key) | Same end state | Depends: `set email` is safe, `add 1 to count` is not |
| Example | `POST /orders` → 201 + `Location: /orders/987` | `PUT /users/42/settings` | `PATCH /users/42 {"email": …}` |

- Why so many teams use POST for everything
  - HTML forms only support GET and POST, and old proxies dropped other methods
  - Actions don't fit CRUD (`cancel`, `approve`, `search`)
  - Searches with large filter bodies can't go in a GET URL
  - RPC habits: GraphQL and many internal APIs are POST-only
- Cost of doing it: lose idempotent retries, caching and clear semantics; you must add idempotency keys yourself
- When to choose PUT: the client already knows the ID (client-generated UUID, a singleton like settings), and sends the whole thing; it doubles as an upsert
- 🗣 "PUT is an idempotent replace at a known URI; POST is server-assigned create or a command, so it needs an idempotency key for safe retries."


---

<a id="a6"></a>
## 7. Request And Response Samples ★★

- **In plain words:** a request is a start line, headers, a blank line, then an optional body; a response is the same with a status line.

**GET with a conditional cache check**
```http
GET /v1/orders/987 HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGc...
Accept: application/json
If-None-Match: "v7"

HTTP/1.1 200 OK
Content-Type: application/json
ETag: "v8"
Cache-Control: private, max-age=60

{"id": "987", "status": "shipped", "total": 4200, "currency": "USD"}
```
- If the ETag still matched, the server replies `304 Not Modified` with no body

**POST create**
```http
POST /v1/orders HTTP/1.1
Content-Type: application/json
Authorization: Bearer eyJhbGc...
Idempotency-Key: 3f1c9a2e-7b4d-4e0a-9f00-2d6c5b1e8a11

{"items": [{"sku": "A12", "qty": 2}], "currency": "USD"}

HTTP/1.1 201 Created
Location: /v1/orders/987
Content-Type: application/json

{"id": "987", "status": "pending", "total": 4200}
```

**PUT replace with optimistic locking**
```http
PUT /v1/users/42/settings HTTP/1.1
Content-Type: application/json
If-Match: "v3"

{"language": "en", "timezone": "America/Chicago", "emails": true}

HTTP/1.1 200 OK
ETag: "v4"
```
- If someone else changed it first: `412 Precondition Failed`

**PATCH and DELETE**
```http
PATCH /v1/users/42 HTTP/1.1
Content-Type: application/merge-patch+json

{"email": "new@example.com"}

HTTP/1.1 200 OK
```
```http
DELETE /v1/orders/987 HTTP/1.1
Authorization: Bearer eyJhbGc...

HTTP/1.1 204 No Content
```

**Error**
```http
HTTP/1.1 422 Unprocessable Content
Content-Type: application/problem+json

{"type": "https://api.example.com/errors/validation", "title": "Invalid email",
 "status": 422, "detail": "email must contain @", "instance": "/v1/users/42",
 "request_id": "req-123"}
```
- `application/problem+json` is the standard error format (RFC 9457)

**GraphQL for comparison** (one endpoint, client picks fields)
```http
POST /graphql HTTP/1.1
Content-Type: application/json

{"query": "query($id: ID!) { order(id: $id) { id status items { sku qty } } }",
 "variables": {"id": "987"}}

HTTP/1.1 200 OK

{"data": {"order": {"id": "987", "status": "shipped", "items": [{"sku": "A12", "qty": 2}]}}}
```
- GraphQL usually returns 200 even with errors, inside an `errors` array; monitoring must read the body

**Headers worth knowing**

| Header | Purpose |
|---|---|
| `Authorization`, `Content-Type`, `Accept` | Who is calling, body format, wanted format |
| `Idempotency-Key` (OCI `opc-retry-token`) | Safe retries of creates |
| `ETag`, `If-Match`, `If-None-Match` | Caching and optimistic concurrency |
| `Location` | URL of the created resource or operation |
| `Retry-After` | When to retry after 429 / 503 |
| `X-Request-Id` (OCI `opc-request-id`), `traceparent` | Correlation and tracing |
| `RateLimit-*` (IETF draft) or `X-RateLimit-*` | Remaining quota |


---

<a id="b-fields"></a>
## 8. Field And Payload Rules ★★

- **In plain words:** small naming and typing choices decide whether clients can trust and evolve against your API.

### 8.1 Rules for every style

1. **Design from use cases, not tables:** one call per screen or job, not one per entity
2. **Never expose persistence models:** request and response DTOs are separate from JPA entities
3. **Names:** consistent case (REST JSON: `camelCase`; protobuf fields: `snake_case`), plural collections, no abbreviations
4. **Types:** money as integer minor units + currency (`amountCents`, `currency`), times as UTC ISO-8601 or epoch with the unit in the name, IDs as opaque strings
5. **Enums:** allow unknown values on the client; add an `UNSPECIFIED` default in protobuf
6. **Errors:** one error shape everywhere, with a machine-readable code
7. **Pagination:** cursor-based for large or changing lists; return `nextCursor`
8. **Idempotency:** an `Idempotency-Key` (or client-generated id) on every create that must not run twice
9. **Concurrency:** a `version` or `ETag` for updates (`If-Match`), to stop lost updates
10. **Security in the contract:** auth scheme declared; never return fields the caller isn't allowed to see

### 8.2 Field details

- Bare resources in responses (no wrapper) unless you need metadata; lists return `{items, next_cursor}`
- Field rules
  - Timestamps: UTC, ISO-8601 (`2026-11-09T07:25:00Z`)
  - Money: integer minor units + currency (`"total_cents": 4599, "currency": "USD"`), never floats
  - Enums: strings (`"CONFIRMED"`), documented, with "unknown" handling on clients
  - IDs as strings
  - Booleans named positively (`is_active`)
- Partial responses: field masks (`?fields=id,title,price`)
- Expansion: `?expand=host` to embed related resources and save round trips
- Validate input at the edge; return all validation errors at once
- 🗣 "Money is integer cents plus currency; floats lose precision."


---

<a id="a7"></a>
## 9. Status Codes And Errors ★★

| Range | Codes that matter |
|---|---|
| 2xx success | 200 OK, 201 Created (+ `Location`), 202 Accepted (async), 204 No Content |
| 3xx | 301 / 308 moved, 304 Not Modified (cache still valid) |
| 4xx client | 400 malformed, 401 not authenticated, 403 not allowed, 404 not found, 409 conflict, 410 gone, 412 precondition failed, 422 semantic error, 429 rate limited (+ `Retry-After`) |
| 5xx server | 500 bug, 502 bad upstream, 503 overloaded / maintenance, 504 upstream timeout |

- Retry rule: retry 429, 503, 504 and timeouts with backoff; never retry 4xx validation errors

### 9.1 Error format

- One format everywhere: RFC 9457 `application/problem+json`

```json
{"type": "https://api.example.com/errors/dates-unavailable",
 "title": "Dates unavailable",
 "status": 409,
 "detail": "Nights 2026-12-20 to 2026-12-22 are already booked",
 "code": "DATES_UNAVAILABLE",
 "request_id": "req_7Fz9"}
```

- Machine-readable `code` + human `detail`
- Say what's retryable: 429 / 503 / 504 yes (with backoff); 400 / 403 / 409 no
- Validation errors list each field
- Don't leak internals (stack traces, SQL)


---

<a id="a8"></a>
## 10. Pagination ★★★

- **In plain words:** return a list in pages so no single response, query or client gets crushed; offset says "skip N," a cursor says "continue after this item."

### 10.1 When to paginate

- Any list that can grow without limit must be paginated from day one; adding it later is a breaking change
- Rough triggers (order of magnitude): the list can exceed ~100 items, or the response would exceed ~1 MB, or the query would scan more than a few thousand rows
- Defaults: page size 20–100, a hard max (e.g. 100 or 1,000), server enforces it even if the client asks for more
- Small fixed lists (countries, a user's 5 addresses) don't need it

### 10.2 Offset vs cursor

| | Offset (`?page=3&size=20` or `?offset=40`) | Cursor / keyset (`?cursor=…&limit=20`) |
|---|---|---|
| SQL | `ORDER BY id LIMIT 20 OFFSET 40` | `WHERE (created_at, id) < (:ts, :id) ORDER BY created_at DESC, id DESC LIMIT 20` |
| Cost of page N | Grows with N: the DB reads and discards all skipped rows | Constant: index seek to the cursor, read 20 |
| Inserts / deletes during paging | Items skipped or shown twice | Stable |
| Jump to page 50 | Yes | No, only next / previous |
| Total count | Easy but `COUNT(*)` is costly on big tables | Usually omitted or estimated |
| Choose when | Small or admin tables (under ~10k rows), page-number UIs | Feeds, large or changing data, infinite scroll, public APIs |

- The cursor is the last row's sort key (e.g. `{created_at, id}`), base64-encoded so clients treat it as opaque; add `id` as a tie-breaker so the order is unique
- Response shape
```json
{"data": [ ... ], "next_cursor": "eyJ0cyI6IjIwMjYtMTEtMTUiLCJpZCI6OTl9", "has_more": true}
```
- Pagination composes with everything else: filters and sort go in the same query string, and the cursor must encode the sort being used
- Filtering: explicit params (`?status=CONFIRMED&check_in_after=...`); validate allowed fields
- Sorting: whitelist sortable fields; the cursor must encode the sort key
- 🗣 "Offset is O(offset) and drifts under writes; keyset cursors seek by index, stay stable, and are the default for anything that grows."


---

<a id="b-safety"></a>
## 11. Idempotency, Concurrency And Long-Running Work ★★★

- **In plain words:** make retries harmless, stop two editors overwriting each other, and never make a client wait minutes on one request.

### 11.1 Idempotency

- Problem: a client times out and retries a payment or booking → double charge
- How
  1. Client generates a key per logical operation (UUID) and sends `Idempotency-Key`
  2. Server stores `(tenant, key) → status, response hash, response body` with a TTL (e.g. 24 h)
  3. First request: mark **in progress**, execute, store the response
  4. Repeat with the same key: return the stored response
  5. Repeat while in progress: return 409 (or wait)
  6. Same key, different body: return 422 / 409 (key misuse)
- Store it with the business write (same DB transaction) when possible, so "done" and "recorded" can't diverge
- PUT and DELETE are idempotent by definition; POST needs the key
- 🗣 "The idempotency key is stored in the same transaction as the booking, so a retry returns the original result instead of booking twice."

### 11.2 Concurrency control

- `GET` returns `ETag: "v7"`
- `PATCH` with `If-Match: "v7"` → 200 if unchanged, **412** if someone else edited
- Create-only-if-absent: `PUT` with `If-None-Match: *`
- Body alternative: a `version` field checked by a conditional update
- 🗣 "Calendar edits use If-Match, so two hosts editing at once get a 412 instead of silently overwriting."

### 11.3 Long-running operations

- Problem: provisioning, transcoding, exports take seconds to hours
- Pattern
  1. `POST /v1/instances` → `202 Accepted`, `Location: /v1/workRequests/wr_123` (OCI returns `opc-work-request-id`)
  2. Client polls `GET /v1/workRequests/wr_123` (`status`, `percent_complete`, `errors`)
  3. Optional: webhook / notification on completion
  4. Optional: `POST /v1/workRequests/wr_123:cancel`
- Operation resource fields: `id, status, resource_id, percent_complete, created_at, updated_at, errors[]`
- The resource itself exists immediately in a transitional state (`PROVISIONING`)
- Server side: outbox + queue + leased workers ([3messaging.md](3messaging.md) section 8.4)
- 🗣 "Create returns 202 with a work request id; the client polls it, and the resource shows PROVISIONING until done."

### 11.4 Partial updates

- PATCH with `application/merge-patch+json` (send changed fields) or `application/json-patch+json` (list of operations)


---

<a id="b-auth"></a>
## 12. Authentication And Authorization At The API ★★★

| Method | How | Good for |
|---|---|---|
| OAuth2 authorization code + PKCE | User logs in, app gets tokens | Browser / mobile apps |
| OAuth2 client credentials | Service gets a token with its secret | Service-to-service via a gateway |
| JWT bearer tokens | Signed claims; validate signature, `exp`, `aud`, `iss` locally | Stateless validation at scale |
| API keys | Static secret per client | Simple server-to-server, low risk |
| mTLS | Client certificate | Internal services, high trust |
| Request signing | Client signs method, path, headers, body hash | Cloud APIs (OCI HTTP signatures, AWS SigV4) |

- Scopes (`bookings:write`) for coarse permissions; resource checks (is this my booking?) in the service
- Short-lived access tokens + refresh tokens; revocation via short TTL + denylist / introspection
- Never put long-lived secrets in URLs
- 🗣 "The gateway validates the JWT and scopes; the booking service still checks that the booking belongs to the caller."


---

<a id="b-rate"></a>
## 13. Rate Limiting And Quotas ★★

- Where: at the gateway, per user / API key / tenant / IP
- Response: `429` + `Retry-After` (+ remaining-quota headers)
- Algorithms: token bucket (bursts allowed), sliding window (smooth); distributed counters in Redis
- Quotas vs rate limits: quota = total per period (billing / fairness), rate limit = per second
- Different limits per endpoint cost (search heavier than get-by-id)


---

<a id="b-bulk"></a>
## 14. Batch, Bulk, Files, Streaming ★

- Batch: `POST /v1/listings:batchGet` with ids; return per-item results and errors
- Bulk writes: async job + operation resource for large batches
- Files: presigned URL flow ([3messaging.md](3messaging.md) section 5.10)
- Streaming responses: SSE / NDJSON for incremental results (LLM tokens, exports)


---

<a id="a9"></a>
## 15. API Styles: REST, GraphQL, gRPC, WebSocket, SSE, Webhooks ★★★

- **In plain words:** REST, GraphQL and gRPC are ways to ask and answer; WebSocket, SSE and webhooks are ways for the server to tell you things without you asking.

| Style | What it is | Transport / format | Direction | Good at | Bad at | Choose when |
|---|---|---|---|---|---|---|
| REST | Resources + HTTP methods | HTTP/1.1 or 2, JSON | Request / response | Simple, cacheable, every tool understands it | Over- / under-fetching; many round trips | Public and CRUD APIs |
| GraphQL | One endpoint, client picks fields from a typed schema | HTTP POST, JSON | Request / response (+ subscriptions over WebSocket) | Many clients needing different shapes, one round trip | HTTP caching, N+1 resolvers, expensive nested queries | Frontend-driven APIs, BFF |
| gRPC | Typed RPC from `.proto` contracts | HTTP/2, protobuf (binary) | Unary + server, client and bidirectional streams | Fast internal calls, codegen, deadlines | Browsers need gRPC-Web; harder to debug | Service-to-service |
| WebSocket | Long-lived full-duplex socket | Upgraded HTTP, any frames | Both ways, anytime | Chat, games, collaborative editing | Stateful connections; scaling and load balancing are harder | Low-latency two-way |
| SSE (server-sent events) | Server streams events on one HTTP response | HTTP, `text/event-stream` | Server → client only | Live feeds, notifications, LLM token streaming; auto-reconnect | No client → server channel (use normal requests) | One-way live updates |
| Webhook | Server calls *your* URL when something happens | HTTP POST, JSON | Server → server | Integrations (payments, Git events) | Receiver must be reachable, verify signatures, dedupe | Cross-company event notifications |

- Default: REST for public, gRPC inside, GraphQL when many clients need different shapes; SSE before WebSocket when only the server pushes
- GraphQL in one line (you use it daily): a schema of types, a resolver per field, DataLoader batching against N+1, depth / cost limits against abuse, persisted queries to allow GET caching
- gRPC in one line: write a `.proto`, generate client and server stubs, call a method like a local function; HTTP/2 multiplexes many calls on one connection; deadlines propagate automatically
- More detail: [2rest-gql.md](2rest-gql.md), [2rest-grpc-websocket.md](2rest-grpc-websocket.md)

**Example proto**
```protobuf
service UserService {
  rpc GetUser(GetUserRequest) returns (User);
  rpc ListUsers(ListUsersRequest) returns (stream User);  // server streaming
}
message GetUserRequest { string user_id = 1; }
message User { string id = 1; string name = 2; string email = 3; }
```
- The numbers are field tags; on the wire only tags and values travel, which is why renaming a field is safe but reusing a tag number breaks clients

### 15.1 REST contract (OpenAPI)

- **In plain words:** OpenAPI is a YAML file listing every URL, method, request body and response, from which docs, mocks and clients are generated.
```yaml
paths:
  /orders:
    post:
      operationId: createOrder
      parameters:
        - { name: Idempotency-Key, in: header, required: true, schema: { type: string } }
      requestBody:
        content: { application/json: { schema: { $ref: '#/components/schemas/CreateOrder' } } }
      responses:
        '201': { description: created, content: { application/json: { schema: { $ref: '#/components/schemas/Order' } } } }
        '409': { $ref: '#/components/responses/Problem' }
components:
  schemas:
    CreateOrder:
      type: object
      required: [items]
      properties:
        items: { type: array, items: { $ref: '#/components/schemas/OrderItem' } }
```
- Resource design: nouns (`/orders/{id}/items`), verbs only for actions that aren't CRUD (`POST /orders/{id}:cancel` or `/orders/{id}/cancellation`)
- Error shape: RFC 9457 problem details (`type`, `title`, `status`, `detail`, plus your `code`)
- List response: `{ "items": [...], "nextCursor": "..." }`; filters and sort as query parameters
- Long-running work: `202 Accepted` + `Location: /operations/{id}`
- Versioning: URL (`/v1/`) is simplest to route and cache; header or media-type versioning is cleaner but harder to see

### 15.2 GraphQL contract (SDL)

- **In plain words:** the GraphQL schema is a typed graph of everything a client may ask for; clients pick fields, and the schema is the contract.
```graphql
type Query {
  order(id: ID!): Order
  orders(first: Int = 20, after: String): OrderConnection!
}
type Mutation {
  createOrder(input: CreateOrderInput!): CreateOrderPayload!
}
type Order { id: ID!  status: OrderStatus!  total: Money!  items: [OrderItem!]! }
type CreateOrderPayload { order: Order  errors: [UserError!]! }
```
- Mutations take one `input` type and return a payload with domain errors (`errors: [UserError]`), keeping transport errors separate
- Pagination: Relay-style connections (`edges`, `node`, `pageInfo`, `cursor`)
- Nullability: non-null (`!`) is a promise; making a field nullable later breaks clients, so be careful with `!` on fields backed by other services
- Evolution: no versions; add fields, `@deprecated(reason: ...)` old ones, track field usage before removal
- Guard the contract: query depth and cost limits, persisted queries for public clients

- More GraphQL rules
  - Schema-first SDL; nullable by default
  - Relay connections for pagination
  - Cost control: depth / complexity limits, persisted queries
  - DataLoader batching to avoid N+1
  - Mutations return the changed object; subscriptions for push

### 15.3 gRPC contract (Protobuf)

- **In plain words:** a `.proto` file defines services and messages with numbered fields; code is generated for every language, and the numbers, not the names, are what travel on the wire.
```protobuf
syntax = "proto3";
package orders.v1;

service OrderService {
  rpc CreateOrder(CreateOrderRequest) returns (Order);
  rpc ListOrders(ListOrdersRequest) returns (ListOrdersResponse);
}
message CreateOrderRequest {
  string request_id = 1;              // idempotency key
  repeated OrderItem items = 2;
}
enum OrderStatus { ORDER_STATUS_UNSPECIFIED = 0; PENDING = 1; PAID = 2; }
message ListOrdersRequest { int32 page_size = 1; string page_token = 2; }
message ListOrdersResponse { repeated Order orders = 1; string next_page_token = 2; }
```
- Field numbers are forever: never reuse one; mark removed ones `reserved`
- One request and one response message per RPC, even if small: room to grow
- Package versioning (`orders.v1`, `orders.v2`) for breaking changes
- Errors: standard gRPC status codes plus `google.rpc.Status` details
- Google's AIP guidelines (aip.dev) are a strong default style guide for resource-oriented gRPC

- More gRPC rules
  - Service per domain; request / response messages per method (never reuse a message for two RPCs)
  - Deadlines on every call, propagated
  - Status codes: `INVALID_ARGUMENT`, `NOT_FOUND`, `ALREADY_EXISTS`, `FAILED_PRECONDITION`, `RESOURCE_EXHAUSTED`, `UNAVAILABLE`
  - Pagination: `page_size`, `page_token`, `next_page_token`
  - Field masks for partial updates
  - Expose to the web via grpc-gateway / transcoding when needed
  - Schema and evolution rules: [3messaging.md](3messaging.md) section 5.1.3

### 15.4 Event contracts (async APIs)

- An event is a contract too: name it in the past tense (`OrderPaid`), version it, and include `eventId`, `occurredAt`, `aggregateId`, `schemaVersion`
- Schema formats: Avro, Protobuf or JSON Schema, checked by a schema registry with a compatibility mode
- Thin event (ids only, consumer calls back) vs fat event (full state): fat avoids callbacks but couples consumers to more fields
- Kafka-specific design (keys, partitions, Avro, Schema Registry): [3kafka.md](3kafka.md) §3.11 and [3kafka-c.md](3kafka-c.md) §1.3
- AsyncAPI documents event-driven APIs the way OpenAPI documents REST


---

<a id="a11"></a>
## 16. Versioning, Evolution And Contract Testing ★★

| Style | Example | Good | Bad |
|---|---|---|---|
| URL | `/v1/users`, `/v2/users` | Visible, easy routing and caching | Version is part of every URL |
| Media type (header) | `Accept: application/vnd.example.v2+json` | Clean URLs; version per representation | Hidden; harder to test in a browser |
| Custom header | `X-API-Version: 2026-11-01` | Date-based versions (Stripe style) | Non-standard |
| Query param | `?api_version=2` | Easy to add | Pollutes the query string |

### 16.1 Reading `application/vnd.example.v2+json`

- A media type is `type/subtype`; here the type is `application`
- `vnd.` = vendor tree: a private, company-specific format (RFC 6838)
- `example` = the vendor or API name; `v2` = the representation version
- `+json` = structured syntax suffix: "underneath, this is JSON," so generic JSON parsers still work
- Flow
  1. Client sends `Accept: application/vnd.example.v2+json`
  2. Server picks the v2 serializer (content negotiation)
  3. Response carries `Content-Type: application/vnd.example.v2+json` and `Vary: Accept` so caches keep v1 and v2 apart
- Real use: GitHub's `application/vnd.github+json` (it now pairs this with an `X-GitHub-Api-Version` date header)

### 16.2 Evolving without a new version

- Safe: add response fields, add optional request fields, add endpoints
- Breaking: remove or rename fields, change types or meaning, make an optional field required
- Clients must ignore unknown fields (tolerant reader)
- Deprecate: announce, add a `Deprecation` / `Sunset` header, track usage, remove after the window (often 6–12 months)

### 16.3 Compatibility by style

| Change | REST / JSON | GraphQL | Protobuf |
|---|---|---|---|
| Add optional field | Safe | Safe | Safe (new number) |
| Add required request field | Breaking | Breaking (non-null arg without default) | Breaking in practice |
| Remove or rename field | Breaking | Breaking (deprecate first) | Rename is wire-safe, removal must `reserve` the number |
| Change type | Breaking | Breaking | Breaking unless wire-compatible |
| Add enum value | Breaking for strict clients | Breaking for exhaustive clients | Safe if clients handle unknown |
| Tighten validation | Breaking | Breaking | Breaking |

- Robustness rule: be strict in what you send, tolerant in what you accept (ignore unknown fields)
- Deprecation: announce, mark in the spec, monitor usage, set a sunset date (`Deprecation` / `Sunset` headers in REST)
- Consumer-driven contract tests (Pact) catch breaking changes before deploy

### 16.4 Documentation, SDKs, contract testing

- OpenAPI / proto as the source of truth; generate SDKs and docs
- Contract tests (Pact) between consumers and providers
- Examples for every endpoint; changelog per version


---

<a id="a12"></a>
## 17. Serialization ★★★

- **In plain words:** objects in memory are pointers and language-specific layouts; to send or store them you flatten them into bytes (serialize), and the other side rebuilds its own objects from those bytes (deserialize).

### 17.1 When it happens

- Every time data **leaves one process's memory**
  - Network: HTTP bodies, gRPC messages, Kafka records
  - Caches: Redis stores bytes, so your object becomes JSON or binary first
  - Files and object storage: Parquet, Avro, JSON lines
  - Databases: yes, but mostly hidden (17.4)
- Not inside one process: passing an object between your own methods needs no serialization

### 17.2 In one HTTP call, step by step

1. Controller returns an `OrderDto` object
2. The framework picks a serializer by the agreed format (`Accept` / `Content-Type`)
   - Spring: an `HttpMessageConverter` using Jackson turns the whole object into JSON text
   - FastAPI: Pydantic's `model_dump_json` does the same
3. Text becomes bytes (UTF-8), optionally gzip-compressed (`Content-Encoding: gzip`)
4. TLS encrypts the bytes; TCP sends them
5. Client reverses it: decrypt, decompress, read `Content-Type: application/json`, parse JSON into its own type (Jackson `ObjectMapper`, Pydantic model, `JSON.parse` in TypeScript)

- You serialize the **whole body object** once, just before sending; not field by field
- The client never needs your class: it only needs the format (JSON) and the contract (OpenAPI, GraphQL schema, `.proto`)
- Headers are plain text lines and are not part of body serialization

### 17.3 Formats

| Format | Text or binary | Schema | Good at | Bad at |
|---|---|---|---|---|
| JSON | Text | Optional (JSON Schema, OpenAPI) | Readable, universal, browsers | Bigger, slower to parse, weak types (no int64 or date) |
| Protobuf | Binary | Required `.proto` | Small, fast, safe evolution by tag numbers | Not human-readable |
| Avro | Binary | Required, often from a schema registry | Kafka and data pipelines, schema evolution | Needs the writer's schema to read |
| MessagePack / CBOR | Binary | None | Compact JSON-like | Less tooling |
| Java `Serializable` | Binary | Java classes | Nothing today | Java-only; deserializing untrusted data is a known remote-code-execution risk |

### 17.4 Is there serialization in the database?

- Yes, at two hops, but drivers do it for you
  - **Driver ↔ DB:** JDBC / psycopg turn your parameters into the database wire protocol (PostgreSQL protocol, MySQL protocol)
  - **DB ↔ disk:** the database stores rows in its own page format
- An ORM (JPA, SQLAlchemy) maps objects to rows; that is mapping, the driver still does the byte encoding
- Where *you* choose a format: a JSON / JSONB column (PostgreSQL JSONB is a parsed binary form), a blob column, Redis values, Kafka messages
- 🗣 "Serialization happens at every process boundary: the framework turns the response object into JSON bytes right before writing the body, and the client parses by Content-Type into its own types; databases and caches do the same through drivers."


---

<a id="b-worked"></a>
## 18. Worked API Surfaces

<a id="s18-1"></a>
### 18.1 Booking (Airbnb) ★★★

| Method | Path | Notes |
|---|---|---|
| GET | `/v1/listings?city=&check_in=&check_out=&guests=&price_max=&cursor=` | Search (derived index) |
| GET | `/v1/listings/{id}` | Cacheable |
| GET | `/v1/listings/{id}/availability?from=&to=` | Fresh from source of truth |
| POST | `/v1/bookings` | Idempotency-Key; 201 HELD / CONFIRMED, 409 dates unavailable |
| GET | `/v1/bookings/{id}` | Owner only |
| POST | `/v1/bookings/{id}:cancel` | Idempotent |
| GET | `/v1/users/me/bookings?cursor=` | Cursor pagination |

<a id="s18-2"></a>
### 18.2 Chat ★★

| Method | Path / message | Notes |
|---|---|---|
| POST | `/v1/realtime/tickets` | One-time connect ticket |
| WS | `message.send`, `message.new`, `receipt.read`, `sync.request` | See 3messaging.md 5.5.1 |
| GET | `/v1/chats?cursor=` | Conversation list |
| GET | `/v1/chats/{id}/messages?after_seq=&limit=` | History / catch-up |
| POST | `/v1/uploads` | Presigned media upload |

<a id="s18-3"></a>
### 18.3 OCI-Style Control Plane ★★★

| Method | Path | Notes |
|---|---|---|
| POST | `/v1/instances` | `opc-retry-token`; 202 + `opc-work-request-id` |
| GET | `/v1/instances/{id}` | `lifecycleState`: PROVISIONING / RUNNING / ... |
| GET | `/v1/instances?compartmentId=&page=` | Paginated, tenant-scoped |
| POST | `/v1/instances/{id}/actions/stop` | Async action |
| DELETE | `/v1/instances/{id}` | 202 + work request |
| GET | `/v1/workRequests/{id}` | Status, percent, errors |


---

<a id="a13"></a>
## 19. Frameworks And Tools ★

| Area | Options |
|---|---|
| Java | Spring Boot MVC (blocking), WebFlux (reactive), grpc-java |
| Python | FastAPI (OpenAPI from code, Pydantic), Flask, Django REST Framework |
| Node | Express, Fastify (schema-based, faster) |
| Gateways | Kong, AWS API Gateway, Envoy, NGINX, OCI API Gateway |
| Contracts | OpenAPI / Swagger UI / Redoc; GraphQL SDL; `.proto` + buf |


---

<a id="b-fail"></a>
## 20. Failure Modes

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Double charge / booking | Client retry without idempotency | Duplicate rows | Idempotency key stored with the write |
| Lost edit | Concurrent PATCH | User complaints | ETag / If-Match |
| Deep pagination meltdown | Offset 1,000,000 | Slow queries | Cursor pagination |
| Retry storm | Clients retry 5xx without backoff | Traffic spike after an incident | `Retry-After`, client backoff + jitter |
| Breaking change | Field rename shipped in place | Client errors after deploy | Additive changes, versioning |
| Token leak | Long-lived token in URL / logs | Security review | Short-lived tokens, headers only |
| Blocking long work | Sync API for multi-minute tasks | Timeouts | 202 + operation resource |
| Entity leak | Returning JPA entities | Lazy-loading errors, exposed internal fields | DTOs mapped at the boundary |
| Enum crash | New enum value | Deserialization errors in old clients | Unknown-tolerant clients, `UNSPECIFIED` default |
| Reused proto field number | Deleting and reusing a number | Garbage values in old clients | `reserved` numbers |


---

<a id="a14"></a>
## 21. Interview Questions And Pitfalls

### 21.1 Questions

**Q1. How do you version an API?**
- L4: URL versioning (`/v1`) for REST, package versions for protobuf, deprecation instead of versions for GraphQL; add fields freely
- L5 extra: versions are a last resort; most changes should be additive, with contract tests and usage tracking deciding when an old field can go

**Q2. What makes a change breaking?**
- L4: removing or renaming fields, changing types, adding required inputs, tightening validation
- L5 extra: semantic changes (same field, new meaning) and new enum values break clients too; consumer-driven contracts catch what schema diffs miss

**Q3. REST vs GraphQL vs gRPC for a new service?**
- L4: REST public, gRPC internal, GraphQL for many varied clients
- L5 extra: the deciding variables are who the clients are, how varied their reads are, latency budget, and whether HTTP caching matters

### 21.2 Pitfalls

- "REST for everything": know when gRPC (internal, streaming) or SSE fits
- No idempotency story for POSTs that create or charge
- Offset pagination on a large or changing list
- 200 with an error in the body for REST (GraphQL is the documented exception)
- Vague errors without code and `request_id`
- No versioning plan
- Verbs in paths (`/getUser`) or fields as path segments
- Blocking calls inside an async handler (FastAPI `async def`, WebFlux)


---

<a id="h-est"></a>
## Part B — Estimation Toolkit

- Kept here from the old `2api.md`; it belongs to the first 10 minutes of a design round alongside the API

<a id="est22"></a>
## 22. Numbers To Memorize ★★★

- All values are order of magnitude; say "roughly" in the interview

<a id="s19-1"></a>
### 22.1 Time And Rates

| Item | Value |
|---|---|
| Seconds per day | 86,400 ≈ 10^5 |
| Seconds per month | ≈ 2.6 × 10^6 |
| 1M per day | ≈ 12 per second |
| 100M per day | ≈ 1,200 per second |
| 1B per day | ≈ 12,000 per second |
| Peak / average | 2–5× (spiky consumer apps up to 10×) |

<a id="s19-2"></a>
### 22.2 Latency

| Operation | Rough latency |
|---|---|
| L1 cache / main memory reference | ~1 ns / ~100 ns |
| Read 1 MB sequentially from memory | ~tens of µs |
| SSD random read | ~100 µs |
| Read 1 MB sequentially from SSD | ~1 ms (order) |
| Round trip in a datacenter | ~0.5 ms |
| Disk seek (HDD) | ~10 ms |
| Round trip cross-continent | ~100–150 ms |

<a id="s19-3"></a>
### 22.3 Sizes

| Item | Size |
|---|---|
| Snowflake / long id | 8 B |
| UUID | 16 B |
| Typical DB row / small JSON event | 0.5–1 KB |
| Chat message with metadata | ~200 B–1 KB |
| Image (compressed) | ~100 KB–2 MB |
| 1 min of video (streaming quality) | ~5–50 MB |

<a id="s19-4"></a>
### 22.4 Per-Node Capacity

| Component | Rough capacity |
|---|---|
| Stateless API server | ~1k–10k requests/s |
| Relational primary | ~thousands to low tens of thousands writes/s |
| Redis node | ~100k ops/s |
| Kafka partition (planning) | ~5–10 MB/s |
| Cassandra node | ~tens of thousands writes/s |
| WebSocket / SSE server | ~50k–100k connections |
| 10 Gbps NIC | ~1.25 GB/s |

<a id="est23"></a>
## 23. Formulas ★★★

| Quantity | Formula |
|---|---|
| Average QPS | DAU × actions per user per day ÷ 86,400 |
| Peak QPS | Average × peak factor (2–5×) |
| Read vs write QPS | Split by ratio (e.g. 100:1 reads) |
| Storage per year | Writes per day × item size × 365 × replication factor |
| Bandwidth | QPS × payload size (ingress and egress separately) |
| Servers | Peak QPS ÷ per-server capacity × 1.3 headroom |
| Cache memory | Hot keys × value size (e.g. 20% of daily reads) |
| Connections | Peak concurrent users (often 10–20% of DAU) |
| Partitions | max(throughput ÷ per-partition rate, consumers needed) × 2 |

- Rule: after every number, say **what it forces**
  - "12k writes/s → past one primary → partition by listing_id"
  - "40 TB/year → object storage for media, DB only for metadata"
  - "2M concurrent connections → ~40 connection servers at 50k each, plus headroom"

<a id="est24"></a>
## 24. Worked Estimates ★★★

<a id="s21-1"></a>
### 24.1 Booking System

- 20M DAU, 1% book per day → 200k bookings/day ≈ 2–3/s average, ~25/s peak → write volume is trivial; **contention per listing** is the real problem
- Searches: 20M × 10 = 200M/day ≈ 2.3k/s, ~10k/s peak → needs a search index + cache
- Storage: 200k × 1 KB × 365 ≈ 73 GB/year bookings → one relational cluster is fine
- Decision: relational source of truth with conditional updates; scale search separately

<a id="s21-2"></a>
### 24.2 Chat

- 100M DAU × 40 messages = 4B/day ≈ 46k/s average, ~150k/s peak
- Storage: 4B × 300 B ≈ 1.2 TB/day, × RF 3 ≈ 3.6 TB/day → wide-column store, time buckets, cold tiering
- Connections: ~20M concurrent → ~400 connection servers at 50k each, plus ~30% headroom
- Decision: Kafka keyed by chat_id, Cassandra for history, stateful connection tier

<a id="s21-3"></a>
### 24.3 URL Shortener

- 100M new links/month ≈ 40/s writes; reads 100:1 → ~4k/s average, ~20k/s peak
- Storage: 100M × 12 months × 500 B ≈ 600 GB over a year
- Key space: base62, 7 characters ≈ 3.5 × 10^12 codes → enough
- Decision: KV store + cache; reads dominate, so CDN / cache hit rate is the lever


---

<a id="b-fits"></a>
## 25. Where This Fits

- Place: the deep doc behind 1sd.md sections 4.2, 4.3, 6.1, 6.3; payloads and schemas in 3messaging.md
- Time: 2 days; then the first 10 minutes of every mock
- I should be able to
  - Map requirements to endpoints in 2–3 minutes with correct verbs and codes
  - Explain idempotency keys, cursors, ETags and 202 operations in one sentence each
  - Do QPS / storage / bandwidth / server math in under 3 minutes and say what each number forces


---

<a id="refs"></a>
## References

- [RFC 9110 — HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110)
- [RFC 9457 — Problem Details for HTTP APIs](https://www.rfc-editor.org/rfc/rfc9457)
- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)
- [Google API Improvement Proposals (AIP)](https://google.aip.dev/)
- [Protocol Buffers — proto3 guide](https://protobuf.dev/programming-guides/proto3/) and [GraphQL best practices](https://graphql.org/learn/best-practices/)
