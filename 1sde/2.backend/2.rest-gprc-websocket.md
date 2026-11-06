# REST, GraphQL, gRPC, WebSocket — Servers in Java & Python, Clients in React & Angular

Grouped by protocol. Each topic shows the servers first — **raw Java** (the actual mechanism), **Spring Boot**, **Python Flask**, **Python FastAPI** — then the frontend clients — **React** and **Angular** — with a multiplex matrix showing the same client code pointed at every server. Every snippet covers the full request anatomy: path, path variable, query param, header, body, versioning.

## Index

- [Core concepts](#concepts)
- [Where every component lives (cross-protocol map)](#map)
- **REST**
  - [How it works](#rest-wire)
  - [Raw Java](#rest-raw-java)
  - [Spring Boot](#rest-spring)
  - [Python Flask](#rest-flask)
  - [Python FastAPI](#rest-fastapi)
  - [React client](#rest-react)
  - [Angular client](#rest-angular)
  - [Multiplex matrix](#rest-matrix)
  - [Pagination & lazy loading](#rest-paging)
- **GraphQL**
  - [How it works](#gql-wire)
  - [Schema (the contract)](#gql-schema)
  - [Raw Java (graphql-java)](#gql-raw-java)
  - [Spring Boot](#gql-spring)
  - [Python Flask (Ariadne)](#gql-flask)
  - [Python FastAPI (Strawberry)](#gql-fastapi)
  - [React client (Apollo)](#gql-react)
  - [Angular client (Apollo Angular)](#gql-angular)
  - [Multiplex matrix](#gql-matrix)
  - [Pagination & lazy loading](#gql-paging)
- **gRPC**
  - [How it works](#grpc-wire)
  - [Proto contract](#grpc-proto)
  - [Raw Java](#grpc-raw-java)
  - [Spring Boot](#grpc-spring)
  - [Python (grpcio)](#grpc-python)
  - [React client (grpc-web)](#grpc-react)
  - [Angular client (grpc-web)](#grpc-angular)
  - [Multiplex matrix](#grpc-matrix)
  - [Pagination & lazy loading](#grpc-paging)
- **WebSocket**
  - [How it works](#ws-wire)
  - [Raw Java](#ws-raw-java)
  - [Spring Boot (raw + STOMP)](#ws-spring)
  - [Python Flask](#ws-flask)
  - [Python FastAPI](#ws-fastapi)
  - [React client](#ws-react)
  - [Angular client](#ws-angular)
  - [Multiplex matrix](#ws-matrix)
  - [Pagination & lazy loading](#ws-paging)
- [Popular frameworks](#frameworks)
- [Interview pitfalls](#pitfalls)

---

<a id="concepts"></a>
## Core Concepts

- **Interaction model.** REST is request/response over HTTP: client asks, server answers, stateless. GraphQL is also request/response over HTTP, but through **one endpoint** where the client declares the shape it wants; subscriptions add server push over WebSocket. gRPC is RPC over HTTP/2: you call a *method* on a remote service, in four shapes (unary, server-streaming, client-streaming, bidirectional). WebSocket is a persistent full-duplex TCP pipe: after one HTTP handshake, either side sends frames at any time — no request/response pairing unless you build it.

- **Wire format.** REST and GraphQL carry JSON (text, self-describing, ~2–10× larger than binary). gRPC carries Protocol Buffers (binary, schema-required, parse cost roughly 5–10× lower than JSON). WebSocket carries opaque frames — text or binary; the payload format is entirely your choice.

- **Transport framing.** HTTP/1.1 is text-delimited: headers cost ~500–2000 bytes per request, one request at a time per connection (head-of-line blocking → browsers open ~6 connections/host). HTTP/2 is binary-framed: one TCP connection multiplexes ~100 concurrent streams, HPACK-compressed headers. gRPC *requires* HTTP/2. A WebSocket frame header is 2–14 bytes — the whole per-message overhead, which is why it wins for chat-frequency messaging.

- **Contract.** REST: conventions + optional OpenAPI — nothing enforced at compile time (FastAPI regains some of this via Pydantic types). GraphQL: the SDL schema — introspectable, codegen-friendly, and validated per request. gRPC: the `.proto` file — codegen on both ends, and field *numbers* (not names) are the wire contract. WebSocket: **no contract at all** — you define and version your own message envelope.

- **Statefulness and scaling.** REST/GraphQL queries/gRPC unary are stateless → any instance serves any request. WebSocket (and GraphQL subscriptions, which ride on it) pin a connection to one server: per-connection memory (~20–50 KB), pub/sub backplane for cross-node broadcast, reconnect + missed-message design for every deploy.

- **Load balancing difference that bites.** L4 balancers balance *connections*. REST/GraphQL over HTTP/1.1: connections ≈ requests → L4 works. gRPC and WebSocket hold one long-lived connection → L4 pins all traffic to one backend. gRPC needs L7 (Envoy, ALB gRPC mode) or client-side LB; WebSocket needs connection-count-aware balancing and drain-on-deploy.

---

<a id="map"></a>
## Where Every Component Lives (cross-protocol map)

The interview money-table — the same logical components exist in all four, but live in different places:

| Component | REST | GraphQL | gRPC | WebSocket |
|---|---|---|---|---|
| **Route / path** | URL path: `GET /v1/users/42` | One fixed endpoint: `POST /graphql`; the *operation* selects behavior | HTTP/2 `:path` = `/user.v1.UserService/GetUser` (generated) | Handshake URL only: `ws://host/ws/chat/{room}` |
| **Path variable** | Path segment, parsed by router | A **field argument**: `user(id: 42)` | A **request-message field** (`GetUserRequest.id`) | `@PathParam` on the endpoint URI template |
| **Query param** | `?page=2&sort=name` | Also a field argument: `users(first: 20, after: "…")` | Doesn't exist — everything is a message field | Exists **only at handshake** (`?token=…`) |
| **Headers** | HTTP headers, both ways | HTTP headers on the POST (auth lives here) | `Metadata` (initial + trailing) | Handshake headers only — **browsers can't set custom ones** |
| **Body** | JSON on POST/PUT/PATCH | `{"query": "...", "variables": {...}}` | Length-prefixed protobuf messages | Frames — text or binary, schema is yours |
| **Version** | URI (`/v1/`), header, or media type | **None** — additive evolution + `@deprecated` fields | Proto **package** (`package user.v1;`) → part of the path | URL path (`/ws/v1/…`) or `Sec-WebSocket-Protocol` subprotocol |
| **Status / errors** | Status codes 2xx/4xx/5xx + body | Always HTTP 200; `errors` array in the body | `Status` code in **trailers**; HTTP status ~always 200 | Close codes (1000 normal, 1008 policy, 1011 error) + your envelope |
| **Server push** | No (SSE is the HTTP answer) | Subscriptions (over WebSocket, `graphql-ws`) | Server-streaming RPC | Native — that's the point |
| **Pagination** | Query params: `?size=20&after=<cursor>` | Connection args: `users(first: 20, after: "…")` | Request fields: `page_size` / `page_token` (AIP-158) | Your envelope: `{"type":"history.request","before":…}` |

---

# Topic 1 — REST

<a id="rest-wire"></a>
## REST — How It Works

A REST call is just text over TCP. The client writes:

```
GET /v1/users/42?verbose=true&fields=name,email HTTP/1.1
Host: api.example.com
Accept: application/json
X-Request-Id: 7f3a…

```

`GET` = method (verb), `/v1/users/42` = path (identity: version `v1`, collection `users`, path variable `42`), `?verbose=true&fields=name,email` = query string (optional modifiers). The server writes back a status line, headers, blank line, body. Every framework below is automation of parsing and routing this text.

<a id="rest-raw-java"></a>
## REST — Raw Java (JDK `HttpServer`, all parsing by hand)

No dependencies; this is what every framework automates.

```java
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpServer;

import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.Executors;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class RawRestServer {

    // Path template "/v1/users/{id}" — the version prefix and the path
    // variable are both just conventions inside one string we must parse.
    private static final Pattern USER_BY_ID = Pattern.compile("^/v1/users/(\\d+)$");

    public static void main(String[] args) throws IOException {
        HttpServer server = HttpServer.create(new InetSocketAddress(8080), 0);

        // A "context" is only a path-prefix hook; method + exact-path
        // dispatch (the router) is on us.
        server.createContext("/v1/users", RawRestServer::route);

        // Default executor runs handlers on the accept thread — always set one.
        server.setExecutor(Executors.newFixedThreadPool(16));
        server.start();
    }

    static void route(HttpExchange ex) throws IOException {
        String method = ex.getRequestMethod();          // "GET", "POST", ...
        String path   = ex.getRequestURI().getPath();   // "/v1/users/42"  (query excluded)
        String query  = ex.getRequestURI().getQuery();  // "verbose=true&fields=name,email"

        Matcher m = USER_BY_ID.matcher(path);

        if (method.equals("GET") && m.matches()) {
            // ── path variable: captured group from the path regex
            long id = Long.parseLong(m.group(1));

            // ── query params: split & URL-decode by hand
            Map<String, String> q = parseQuery(query);
            boolean verbose = Boolean.parseBoolean(q.getOrDefault("verbose", "false"));
            String fields   = q.get("fields");                       // may be null

            // ── request header
            String requestId = ex.getRequestHeaders().getFirst("X-Request-Id");

            respond(ex, 200, """
                {"id": %d, "name": "Ada", "verbose": %b, "fields": "%s"}"""
                .formatted(id, verbose, fields));

        } else if (method.equals("POST") && path.equals("/v1/users")) {
            // ── request body: raw bytes off the stream (real code: Jackson)
            String body = new String(ex.getRequestBody().readAllBytes(),
                                     StandardCharsets.UTF_8);
            long newId = 43; // pretend insert

            // ── response header + 201 Created
            ex.getResponseHeaders().add("Location", "/v1/users/" + newId);
            respond(ex, 201, "{\"id\": %d}".formatted(newId));

        } else if (m.matches() || path.equals("/v1/users")) {
            respond(ex, 405, "{\"error\": \"method not allowed\"}");
        } else {
            respond(ex, 404, "{\"error\": \"not found\"}");
        }
    }

    static Map<String, String> parseQuery(String query) {
        Map<String, String> out = new HashMap<>();
        if (query == null) return out;
        for (String pair : query.split("&")) {
            String[] kv = pair.split("=", 2);
            out.put(URLDecoder.decode(kv[0], StandardCharsets.UTF_8),
                    kv.length > 1 ? URLDecoder.decode(kv[1], StandardCharsets.UTF_8) : "");
        }
        return out;
    }

    static void respond(HttpExchange ex, int status, String json) throws IOException {
        byte[] bytes = json.getBytes(StandardCharsets.UTF_8);
        ex.getResponseHeaders().add("Content-Type", "application/json");
        // Browser clients need CORS — by hand here: also answer OPTIONS preflight
        ex.getResponseHeaders().add("Access-Control-Allow-Origin", "http://localhost:5173");
        ex.sendResponseHeaders(status, bytes.length);
        try (OutputStream os = ex.getResponseBody()) { os.write(bytes); }
    }
}
```

What the exercise teaches: routing is string matching, path variables are regex groups, query parsing needs URL-decoding (`%20`, `+`), CORS is just response headers plus an OPTIONS handler, and thread-per-request is a choice you make explicitly.

<a id="rest-spring"></a>
## REST — Spring Boot

`spring-boot-starter-web` (Tomcat + Spring MVC + Jackson). Every manual step becomes an annotation.

```java
@RestController
@RequestMapping("/api/v1/users")          // ── URI VERSIONING: prefix on the class
public class UserController {

    // GET /api/v1/users/42?verbose=true      ── path variable + query params + header
    @GetMapping("/{id}")
    public ResponseEntity<UserDto> get(
            @PathVariable long id,                                   // path variable, auto-converted
            @RequestParam(defaultValue = "false") boolean verbose,   // optional query param w/ default
            @RequestParam(required = false) String fields,           // optional, null if absent
            @RequestHeader(value = "X-Request-Id", required = false) String requestId) {

        return ResponseEntity.ok()
                .eTag("\"v7\"")                                      // response header
                .body(new UserDto(id, "Ada", "ada@example.com"));
    }

    // GET /api/v1/users?status=ACTIVE&page=0&size=20&sort=name,asc   ── list + pagination
    @GetMapping
    public Page<UserDto> list(
            @RequestParam(required = false) Status status,           // enum bound automatically
            @PageableDefault(size = 20, sort = "name") Pageable pageable) {
        return service.find(status, pageable);
    }

    // POST /api/v1/users                     ── body + validation + 201 Location
    @PostMapping
    public ResponseEntity<UserDto> create(@Valid @RequestBody CreateUserRequest body,
                                          UriComponentsBuilder uri) {
        UserDto created = service.create(body);
        return ResponseEntity
                .created(uri.path("/api/v1/users/{id}").build(created.id()))
                .body(created);
    }

    // PUT = full replace (idempotent), PATCH = partial, DELETE = 204
    @PutMapping("/{id}")
    public UserDto replace(@PathVariable long id, @Valid @RequestBody CreateUserRequest body) {
        return service.replace(id, body);
    }

    @PatchMapping("/{id}")
    public UserDto patch(@PathVariable long id, @RequestBody Map<String, Object> changes) {
        return service.patch(id, changes);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(@PathVariable long id) { service.delete(id); }
}
```

DTOs, validation, centralized errors:

```java
public record UserDto(long id, String name, String email) {}
public record CreateUserRequest(
        @NotBlank String name,
        @Email @NotBlank String email,
        @Min(13) int age) {}

@RestControllerAdvice          // one place enforces the error taxonomy
class ApiErrorHandler {

    @ExceptionHandler(MethodArgumentNotValidException.class)   // @Valid failures
    ProblemDetail invalidBody(MethodArgumentNotValidException e) {
        ProblemDetail pd = ProblemDetail.forStatus(HttpStatus.UNPROCESSABLE_ENTITY);
        pd.setDetail(e.getFieldErrors().stream()
                .map(f -> f.getField() + ": " + f.getDefaultMessage())
                .collect(Collectors.joining("; ")));
        return pd;                                             // RFC 9457 Problem Details
    }

    @ExceptionHandler(UserNotFoundException.class)
    ProblemDetail notFound(UserNotFoundException e) {
        return ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, e.getMessage());
    }
}

@Configuration                 // CORS for the React/Angular dev servers
class CorsConfig implements WebMvcConfigurer {
    @Override public void addCorsMappings(CorsRegistry r) {
        r.addMapping("/api/**")
         .allowedOrigins("http://localhost:5173", "http://localhost:4200")
         .allowedMethods("GET", "POST", "PUT", "PATCH", "DELETE");
    }
}
```

The three versioning mechanisms, side by side:

```java
// 1. URI versioning (default choice: visible, routable, cache-friendly)
@RequestMapping("/api/v1/users")   // v2 = a separate controller class

// 2. Header versioning (clean URLs; invisible to caches unless Vary is set)
@GetMapping(value = "/{id}", headers = "X-API-Version=2")
public UserDtoV2 getV2(@PathVariable long id) { ... }

// 3. Media-type (content-negotiation) versioning — "the REST-pure one"
@GetMapping(value = "/{id}", produces = "application/vnd.acme.user-v2+json")
public UserDtoV2 getV2Negotiated(@PathVariable long id) { ... }
```

Interview position: URI versioning as pragmatic default, but versioning is a failure mode — invest in additive-only evolution and expand/contract migration.

<a id="rest-flask"></a>
## REST — Python Flask

WSGI, synchronous, thread-per-request under gunicorn (`workers × threads` = your concurrency ceiling). Validation is manual (or marshmallow/pydantic bolted on) — the contrast with FastAPI is the interview point.

```python
from flask import Flask, Blueprint, request, jsonify, abort, url_for

app = Flask(__name__)

# ── VERSIONING: a Blueprint per version; /api/v2 = second blueprint
v1 = Blueprint("v1", __name__, url_prefix="/api/v1")

@v1.get("/users/<int:user_id>")            # ── path variable, typed by the converter:
def get_user(user_id: int):                #    <int:…> 404s on "abc" before your code runs
    # ── query params: request.args (MultiDict), typed + defaulted by hand
    verbose = request.args.get("verbose", default="false") == "true"
    fields  = request.args.get("fields")                    # None if absent
    # ── header
    request_id = request.headers.get("X-Request-Id")
    return jsonify(id=user_id, name="Ada", verbose=verbose, fields=fields)

@v1.get("/users")
def list_users():
    page   = request.args.get("page", default=0, type=int)   # type= coerces or None
    size   = min(request.args.get("size", default=20, type=int), 100)
    status = request.args.get("status")
    return jsonify(items=[], page=page, size=size)

@v1.post("/users")
def create_user():
    body = request.get_json()               # ── body; 415 if Content-Type wrong
    if not body or not body.get("name"):    # validation is YOUR job in Flask
        abort(422, description="name is required")
    new_id = 43
    resp = jsonify(id=new_id)
    resp.status_code = 201                  # ── status + Location header
    resp.headers["Location"] = url_for("v1.get_user", user_id=new_id)
    return resp

@app.errorhandler(422)                      # centralized error shape
def unprocessable(e):
    return jsonify(error=str(e.description)), 422

app.register_blueprint(v1)

# CORS for browser clients: pip install flask-cors
from flask_cors import CORS
CORS(app, origins=["http://localhost:5173", "http://localhost:4200"])

# dev: flask run --port 5000   prod: gunicorn -w 4 --threads 8 app:app
```

<a id="rest-fastapi"></a>
## REST — Python FastAPI

ASGI + async event loop (uvicorn). Type hints *are* the parsing, validation, and OpenAPI docs — a junk path variable or invalid body returns 422 before your code runs. Free interactive docs at `/docs`.

```python
from fastapi import FastAPI, APIRouter, Query, Header, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field

app = FastAPI(title="Users API")
app.add_middleware(CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4200"],
    allow_methods=["*"], allow_headers=["*"])

# ── VERSIONING: router prefix; mount a v2 router beside it
v1 = APIRouter(prefix="/api/v1/users", tags=["users"])

class CreateUser(BaseModel):                       # ── body schema = validation = docs
    name: str = Field(min_length=1)
    email: EmailStr
    age: int = Field(ge=13)

class UserOut(BaseModel):
    id: int
    name: str
    email: str | None = None

@v1.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: int,                                  # ── path variable: typed → 422 on junk
    verbose: bool = False,                         # ── query param with default
    fields: str | None = Query(None, max_length=100),   # optional, validated
    x_request_id: str | None = Header(None),       # ── header (snake_case → X-Request-Id)
):
    if user_id <= 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "no such user")
    return UserOut(id=user_id, name="Ada")

@v1.get("", response_model=list[UserOut])
async def list_users(
    page: int = Query(0, ge=0),                    # constraints in the signature
    size: int = Query(20, le=100),
    status_filter: str | None = Query(None, alias="status"),
):
    return []

@v1.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(body: CreateUser, response: Response):
    new_id = 43                                    # body already validated & typed
    response.headers["Location"] = f"/api/v1/users/{new_id}"
    return UserOut(id=new_id, name=body.name, email=body.email)

app.include_router(v1)
# run: uvicorn app:app --port 8000    prod: uvicorn --workers 4
```

Flask vs FastAPI in one line for interviews: Flask = sync WSGI, ceiling set by worker threads (~hundreds of concurrent requests), validation manual; FastAPI = async ASGI, one event loop handles thousands of concurrent I/O-bound requests, validation and docs generated from types — but blocking code (a sync DB driver) in an `async def` stalls the whole loop.

<a id="rest-react"></a>
## REST — React Client

The client speaks the *protocol*, not the framework — one client works against all four servers; only the base URL changes (that IS the interview point about contracts). See the [multiplex matrix](#rest-matrix).

```jsx
// api.js — the base URL is the only server-specific knowledge
const BASE = import.meta.env.VITE_API_BASE;   // e.g. "http://localhost:8000/api/v1"

export async function getUser(id, { verbose = false, fields } = {}) {
  const q = new URLSearchParams({ verbose });          // ── query params
  if (fields) q.set("fields", fields);
  const res = await fetch(`${BASE}/users/${id}?${q}`, { // ── path variable in the URL
    headers: { "X-Request-Id": crypto.randomUUID() },   // ── header
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);   // fetch does NOT reject on 4xx/5xx
  return res.json();
}

export async function createUser(body) {
  const res = await fetch(`${BASE}/users`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),                         // ── body
  });
  if (res.status === 422) throw new Error((await res.json()).detail);
  return res.json();                                    // Location header: res.headers.get("Location")
}
```

```jsx
// UserView.jsx — data fetching with cancellation (the part juniors skip)
function UserView({ id }) {
  const [user, setUser] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const ctrl = new AbortController();                 // cancel on unmount/id change
    fetch(`${BASE}/users/${id}?verbose=true`, { signal: ctrl.signal })
      .then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(setUser)
      .catch(e => e.name !== "AbortError" && setError(e));
    return () => ctrl.abort();
  }, [id]);

  if (error) return <p>failed: {String(error)}</p>;
  return user ? <p>{user.name}</p> : <p>loading…</p>;
}
// Production apps wrap this in TanStack Query (useQuery) for caching/retries/dedupe.
```

<a id="rest-angular"></a>
## REST — Angular Client

`HttpClient` returns Observables; `HttpParams`/`HttpHeaders` are immutable (every `.set` returns a new object — mutating in place is the classic bug).

```typescript
// user-api.service.ts
export interface User { id: number; name: string; email?: string; }
export interface CreateUser { name: string; email: string; age: number; }

@Injectable({ providedIn: "root" })
export class UserApi {
  private base = environment.apiBase;          // ← the multiplex point, per environment
  constructor(private http: HttpClient) {}

  getUser(id: number, verbose = false, fields?: string): Observable<User> {
    let params = new HttpParams().set("verbose", verbose);       // ── query params
    if (fields) params = params.set("fields", fields);           // immutable: reassign!
    const headers = new HttpHeaders({ "X-Request-Id": crypto.randomUUID() }); // ── header
    return this.http.get<User>(`${this.base}/users/${id}`, { params, headers });
  }

  list(page = 0, size = 20): Observable<User[]> {
    return this.http.get<User[]>(`${this.base}/users`,
        { params: new HttpParams().set("page", page).set("size", size) });
  }

  create(body: CreateUser): Observable<HttpResponse<User>> {
    return this.http.post<User>(`${this.base}/users`, body,     // ── body
        { observe: "response" });   // observe:"response" → read status + Location header
  }
}
```

```typescript
// Cross-cutting headers (auth, request id) belong in an interceptor, not per call:
export const authInterceptor: HttpInterceptorFn = (req, next) =>
  next(req.clone({ setHeaders: { Authorization: `Bearer ${token()}` } }));

// component usage — async pipe handles subscribe/unsubscribe
@Component({
  selector: "user-view",
  template: `@if (user$ | async; as user) { <p>{{ user.name }}</p> }`,
})
export class UserViewComponent {
  user$ = this.api.getUser(42, true).pipe(
    catchError(err => { console.error(err.status); return EMPTY; }));  // HttpErrorResponse
  constructor(private api: UserApi) {}
}
```

<a id="rest-matrix"></a>
## REST — Multiplex Matrix (same client → every server)

| Client → Server | Base URL to configure | Endpoint shape | Notes |
|---|---|---|---|
| React/Angular → **Raw Java** | `http://localhost:8080/v1` | `/users/{id}` | CORS headers + OPTIONS handled by hand server-side |
| React/Angular → **Spring Boot** | `http://localhost:8080/api/v1` | `/users/{id}` | CORS via `WebMvcConfigurer` |
| React/Angular → **Flask** | `http://localhost:5000/api/v1` | `/users/{id}` | CORS via `flask-cors` |
| React/Angular → **FastAPI** | `http://localhost:8000/api/v1` | `/users/{id}` | CORS via `CORSMiddleware`; 422 bodies differ (`detail` array) |

Client code is byte-identical across rows — swap `VITE_API_BASE` / `environment.apiBase`. That's the value of a protocol contract: the server stack is invisible. The one leak: each framework's *error body shape* differs (Problem Details vs Flask's HTML-ish aborts vs FastAPI's `{"detail": [...]}`) — normalize errors in one place client-side.

<a id="rest-paging"></a>
## REST — Pagination & Lazy Loading

"Lazy loading" means two different things — keep them separate in an interview:

- **Data lazy loading**: fetch the next slice only when the user needs it (infinite scroll, load-more). This is pagination driven from the client — the subject of this section.
- **Code lazy loading**: ship the JS bundle in chunks — `React.lazy(() => import("./AdminPanel"))` + `<Suspense>`, Angular `loadChildren: () => import("./admin/routes")` and `@defer (on viewport) { <heavy-cmp/> }`. Orthogonal to the API; mention it and move on.

**Server side — offset vs keyset (cursor):**

| | Offset (`?page=2&size=20`) | Keyset (`?after=<cursor>&size=20`) |
|---|---|---|
| SQL | `LIMIT 20 OFFSET 40` | `WHERE (created_at, id) < (:c_ts, :c_id) ORDER BY created_at DESC, id DESC LIMIT 21` |
| Cost at depth | DB reads+discards the offset — depth-linear | O(page) at any depth |
| Under concurrent inserts | Pages shift — rows skipped/duplicated | Stable |
| Random page jump | ✓ (page 17 directly) | ✗ — forward/backward only |
| Use for | Admin tables with page numbers | Feeds, infinite scroll, exports |

Keyset endpoint, Spring Boot — the `n+1` fetch trick gives `hasNext` without a COUNT:

```java
public record PageDto<T>(List<T> items, String nextCursor) {}   // cursor = opaque base64

@GetMapping
public PageDto<UserDto> list(
        @RequestParam(defaultValue = "20") @Max(100) int size,   // ALWAYS clamp size
        @RequestParam(required = false) String after) {          // opaque cursor
    Cursor c = Cursor.decode(after);                 // base64({createdAt, id}) — id is the
    List<UserDto> rows = repo.pageAfter(c, size + 1);// tiebreaker; without it rows at equal
    boolean hasNext = rows.size() > size;            // timestamps get skipped at boundaries
    List<UserDto> page = hasNext ? rows.subList(0, size) : rows;
    return new PageDto<>(page,
            hasNext ? Cursor.encode(page.getLast()) : null);     // null = client stops
}
```

Same shape in FastAPI (Flask and raw Java: identical mechanics via `request.args` / `parseQuery`):

```python
class Page(BaseModel):
    items: list[UserOut]
    next_cursor: str | None = None

@v1.get("", response_model=Page)
async def list_users(size: int = Query(20, le=100), after: str | None = None):
    rows = await repo.page_after(decode_cursor(after), size + 1)
    has_next = len(rows) > size
    page = rows[:size]
    return Page(items=page,
                next_cursor=encode_cursor(page[-1]) if has_next else None)
```

**React — infinite scroll (IntersectionObserver on a sentinel):**

```jsx
function useInfiniteUsers() {
  const [items, setItems] = useState([]);
  const [cursor, setCursor] = useState(null);
  const [done, setDone] = useState(false);
  const inFlight = useRef(false);                  // guard: observer fires in bursts

  const loadMore = useCallback(async () => {
    if (inFlight.current || done) return;
    inFlight.current = true;
    const q = new URLSearchParams({ size: 20 });
    if (cursor) q.set("after", cursor);
    const page = await fetch(`${BASE}/users?${q}`).then(r => r.json());
    setItems(prev => [...prev, ...page.items]);    // append, never replace
    setCursor(page.nextCursor);
    if (!page.nextCursor) setDone(true);
    inFlight.current = false;
  }, [cursor, done]);

  return { items, loadMore, done };
}

function UserList() {
  const { items, loadMore, done } = useInfiniteUsers();
  const sentinel = useRef(null);

  useEffect(() => {
    const obs = new IntersectionObserver(
      ([e]) => e.isIntersecting && loadMore(),
      { rootMargin: "200px" });                    // prefetch before the edge is visible
    if (sentinel.current) obs.observe(sentinel.current);
    return () => obs.disconnect();
  }, [loadMore]);

  return (<>
    {items.map(u => <p key={u.id}>{u.name}</p>)}
    {!done && <div ref={sentinel}>loading…</div>}
  </>);
}
```

**Angular — the pager service owns the cursor; the component appends:**

```typescript
@Injectable({ providedIn: "root" })
export class UserPager {
  private cursor: string | null = null;
  done = false;
  constructor(private http: HttpClient) {}

  nextPage(): Observable<User[]> {
    if (this.done) return of([]);
    let params = new HttpParams().set("size", 20);
    if (this.cursor) params = params.set("after", this.cursor);
    return this.http.get<PageDto<User>>(`${environment.apiBase}/users`, { params })
      .pipe(map(p => {
        this.cursor = p.nextCursor;
        this.done = !p.nextCursor;
        return p.items;
      }));
  }
}

@Component({ /* … */ })
export class UserListComponent {
  users: User[] = [];
  private loading = false;
  constructor(private pager: UserPager) { this.more(); }

  more() {
    if (this.loading || this.pager.done) return;
    this.loading = true;
    this.pager.nextPage().subscribe(p => { this.users.push(...p); this.loading = false; });
  }

  @HostListener("window:scroll")
  onScroll() {                                     // 200px early, same idea as rootMargin
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 200)
      this.more();
  }
}
```

For thousand-row lists, pair this with CDK Virtual Scroll (`<cdk-virtual-scroll-viewport>`) or a React window library — infinite *fetching* without list *virtualization* eventually makes the DOM itself the bottleneck.

---

# Topic 2 — GraphQL

<a id="gql-wire"></a>
## GraphQL — How It Works

One endpoint, `POST /graphql`. The body carries the operation; the *client* declares the response shape:

```
POST /graphql HTTP/1.1
Content-Type: application/json
Authorization: Bearer …            ← auth stays in HTTP headers

{
  "query": "query GetUser($id: ID!) { user(id: $id) { id name email } }",
  "variables": { "id": "42" },
  "operationName": "GetUser"
}

← HTTP 200 always; success and failure both look like:
{ "data": { "user": { … } }, "errors": [ { "message": "…", "path": ["user"] } ] }
```

- **Query** = read, **Mutation** = write (top-level mutation fields run *serially* per spec), **Subscription** = server push — carried over WebSocket using the `graphql-ws` subprotocol (`Sec-WebSocket-Protocol: graphql-transport-ws`), because HTTP request/response can't push.
- REST's path variables and query params both collapse into **field arguments**; there is no versioning — the schema evolves additively and old fields get `@deprecated`.
- Because everything is HTTP 200 POST: no HTTP caching, and your monitoring must read the `errors` array, not status codes.

<a id="gql-schema"></a>
## GraphQL — Schema (the contract, shared by every server below)

```graphql
type Query {
  user(id: ID!): User                    # id ≈ REST path variable → argument
  users(status: Status, first: Int! = 20, after: String): [User!]!  # ≈ query params
}

type Mutation {
  createUser(input: CreateUserInput!): User!
}

type Subscription {
  userCreated: User!                     # server push — rides on WebSocket
}

type User {
  id: ID!
  name: String!
  email: String                          # nullable = allowed to degrade
}

input CreateUserInput {
  name: String!
  email: String!
  age: Int!
}

enum Status { ACTIVE INACTIVE }
```

<a id="gql-raw-java"></a>
## GraphQL — Raw Java (graphql-java, no Spring)

graphql-java is the execution engine everything JVM-side (including Spring for GraphQL) sits on. You wire a `DataFetcher` per field; transport is your problem.

```java
TypeDefinitionRegistry types = new SchemaParser().parse(sdlString);

RuntimeWiring wiring = RuntimeWiring.newRuntimeWiring()
    .type("Query", t -> t
        .dataFetcher("user", env -> {
            String id = env.getArgument("id");            // ── argument ≈ path var
            return Map.of("id", id, "name", "Ada");
        })
        .dataFetcher("users", env -> {
            int first = env.getArgument("first");         // ── argument ≈ query param
            return List.of();
        }))
    .type("Mutation", t -> t
        .dataFetcher("createUser", env -> {
            Map<String, Object> input = env.getArgument("input");
            Map<String, Object> user = Map.of("id", "43", "name", input.get("name"));
            userSink.tryEmitNext(user);                   // feed subscribers
            return user;
        }))
    .type("Subscription", t -> t
        // Subscription fetchers return a Reactive-Streams Publisher —
        // the engine emits one ExecutionResult per published element
        .dataFetcher("userCreated", env -> userSink.asFlux()))
    .build();

GraphQLSchema schema = new SchemaGenerator().makeExecutableSchema(types, wiring);
GraphQL graphql = GraphQL.newGraphQL(schema).build();

// Transport is on you: parse {"query","variables"} from POST /graphql and:
ExecutionResult result = graphql.execute(ExecutionInput.newExecutionInput()
        .query(query).variables(variables).build());
Map<String, Object> body = result.toSpecification();   // {"data":…,"errors":…} → JSON
// Subscriptions additionally need a WebSocket endpoint speaking graphql-ws —
// this is exactly what Spring for GraphQL provides out of the box.
```

<a id="gql-spring"></a>
## GraphQL — Spring Boot (Spring for GraphQL)

`spring-boot-starter-graphql`. Schema file in `src/main/resources/graphql/schema.graphqls`; HTTP endpoint `/graphql`; enable the WebSocket transport for subscriptions with `spring.graphql.websocket.path=/graphql`.

```java
@Controller                      // note: not @RestController — schema routes, not URLs
public class UserGraphqlController {

    // one multicast sink feeds all subscription clients
    private final Sinks.Many<UserDto> created =
            Sinks.many().multicast().onBackpressureBuffer();

    @QueryMapping                                 // matches Query.user by method name
    public UserDto user(@Argument long id) {      // ── @Argument binds "id"
        return new UserDto(id, "Ada", "ada@example.com");
    }

    @QueryMapping
    public List<UserDto> users(@Argument Status status, @Argument int first) {
        return service.find(status, first);
    }

    @MutationMapping
    public UserDto createUser(@Argument CreateUserInput input) {   // input type → record
        UserDto u = service.create(input);
        created.tryEmitNext(u);                   // push to subscribers
        return u;
    }

    @SubscriptionMapping                          // must return a Publisher (Flux)
    public Flux<UserDto> userCreated() {
        return created.asFlux();
    }

    // Relation field with the N+1 answer built in: called ONCE per query
    // with all parent users — not once per user.
    @BatchMapping
    public Map<UserDto, Team> team(List<UserDto> users) {
        return teamService.teamsFor(users);
    }
}

public record CreateUserInput(@NotBlank String name, @Email String email, @Min(13) int age) {}
```

<a id="gql-flask"></a>
## GraphQL — Python Flask (Ariadne)

Ariadne is schema-first: the same SDL string, resolvers registered per field. **Flask is WSGI, so subscriptions are impossible here** — no WebSocket in the worker model. Queries and mutations only; that limitation is a legitimate interview talking point.

```python
from ariadne import QueryType, MutationType, make_executable_schema
from ariadne import graphql_sync
from flask import Flask, request, jsonify

app = Flask(__name__)
query = QueryType()
mutation = MutationType()

@query.field("user")
def resolve_user(_, info, id):                 # ── arguments arrive as kwargs
    # headers still HTTP: info.context["request"].headers.get("Authorization")
    return {"id": id, "name": "Ada", "email": "ada@example.com"}

@query.field("users")
def resolve_users(_, info, first=20, status=None, after=None):
    return []

@mutation.field("createUser")
def resolve_create_user(_, info, input):       # input dict, validated against SDL types
    return {"id": "43", "name": input["name"], "email": input["email"]}

schema = make_executable_schema(sdl_string, query, mutation)

@app.post("/graphql")                          # the single endpoint
def graphql_endpoint():
    ok, result = graphql_sync(                 # validates + executes against schema
        schema, request.get_json(),
        context_value={"request": request})
    return jsonify(result), 200                # always 200 — errors are in the body

# Subscriptions need ASGI: either ariadne.asgi.GraphQL under uvicorn, or FastAPI below.
```

<a id="gql-fastapi"></a>
## GraphQL — Python FastAPI (Strawberry)

Strawberry is code-first: Python types *are* the schema. `GraphQLRouter` serves queries/mutations on `POST /graphql` **and** the `graphql-ws` WebSocket on the same path — subscriptions work because ASGI speaks WebSocket natively.

```python
import asyncio
import strawberry
from typing import AsyncGenerator
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

@strawberry.type
class User:
    id: strawberry.ID
    name: str
    email: str | None = None

@strawberry.input
class CreateUserInput:
    name: str
    email: str
    age: int

listeners: set[asyncio.Queue] = set()          # naive in-process pub/sub

@strawberry.type
class Query:
    @strawberry.field
    async def user(self, id: strawberry.ID) -> User:        # ── argument ≈ path var
        return User(id=id, name="Ada")

    @strawberry.field
    async def users(self, first: int = 20, status: str | None = None) -> list[User]:
        return []

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_user(self, input: CreateUserInput) -> User:
        u = User(id="43", name=input.name, email=input.email)
        for q in listeners:                    # push to every subscriber
            q.put_nowait(u)
        return u

@strawberry.type
class Subscription:
    @strawberry.subscription                    # an async generator IS the stream
    async def user_created(self) -> AsyncGenerator[User, None]:
        q: asyncio.Queue = asyncio.Queue()
        listeners.add(q)
        try:
            while True:
                yield await q.get()            # each yield → one push to the client
        finally:
            listeners.discard(q)               # cleanup on disconnect

schema = strawberry.Schema(query=Query, mutation=Mutation, subscription=Subscription)
app = FastAPI()
app.include_router(GraphQLRouter(schema), prefix="/graphql")
# uvicorn app:app --port 8000  → POST /graphql + WS /graphql (graphql-ws)
```

Multi-instance note: the in-process `listeners` set only reaches subscribers on *this* node — production fan-out needs Redis pub/sub or a broker behind the async generator.

<a id="gql-react"></a>
## GraphQL — React Client (Apollo Client)

One Apollo setup serves every GraphQL server; the `split` link routes subscriptions to WebSocket and everything else to HTTP.

```jsx
import { ApolloClient, InMemoryCache, HttpLink, split, gql } from "@apollo/client";
import { GraphQLWsLink } from "@apollo/client/link/subscriptions";
import { createClient } from "graphql-ws";
import { getMainDefinition } from "@apollo/client/utilities";

const httpLink = new HttpLink({
  uri: `${import.meta.env.VITE_GQL_HTTP}`,        // http://localhost:8080/graphql
  headers: { Authorization: `Bearer ${token}` },  // auth = plain HTTP header
});
const wsLink = new GraphQLWsLink(createClient({
  url: `${import.meta.env.VITE_GQL_WS}`,          // ws://localhost:8080/graphql
  connectionParams: { token },                    // WS can't send headers → params
}));

// subscriptions → wsLink; queries & mutations → httpLink
const link = split(({ query }) => {
  const def = getMainDefinition(query);
  return def.kind === "OperationDefinition" && def.operation === "subscription";
}, wsLink, httpLink);

export const client = new ApolloClient({ link, cache: new InMemoryCache() });
```

```jsx
const GET_USER = gql`query GetUser($id: ID!) { user(id: $id) { id name email } }`;
const CREATE_USER = gql`
  mutation CreateUser($input: CreateUserInput!) {
    createUser(input: $input) { id name }
  }`;
const USER_CREATED = gql`subscription { userCreated { id name } }`;

function UserView({ id }) {
  const { data, loading, error } = useQuery(GET_USER, { variables: { id } });
  if (loading) return <p>loading…</p>;
  if (error) return <p>{error.message}</p>;        // GraphQL errors ≠ HTTP errors
  return <p>{data.user.name}</p>;
}

function CreateUserForm() {
  const [createUser, { loading }] = useMutation(CREATE_USER, {
    refetchQueries: ["GetUser"],                   // or update the cache directly
  });
  return <button disabled={loading}
    onClick={() => createUser({ variables: { input: { name: "Bo", email: "b@x.io", age: 30 } } })}>
    create</button>;
}

function NewUserToast() {
  const { data } = useSubscription(USER_CREATED);  // live over graphql-ws
  return data ? <p>new user: {data.userCreated.name}</p> : null;
}
```

<a id="gql-angular"></a>
## GraphQL — Angular Client (Apollo Angular)

Same link architecture, Angular DI flavor (`ng add apollo-angular`).

```typescript
// app.config.ts
export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(),
    provideApollo(() => {
      const httpLink = inject(HttpLink);
      const http = httpLink.create({ uri: environment.gqlHttp });
      const ws = new GraphQLWsLink(createClient({
        url: environment.gqlWs,
        connectionParams: { token: token() },
      }));
      const link = split(({ query }) => {
        const def = getMainDefinition(query);
        return def.kind === "OperationDefinition" && def.operation === "subscription";
      }, ws, http);
      return { link, cache: new InMemoryCache() };
    }),
  ],
};
```

```typescript
@Injectable({ providedIn: "root" })
export class UserGql {
  constructor(private apollo: Apollo) {}

  user(id: string): Observable<User> {
    return this.apollo
      .watchQuery<{ user: User }>({ query: GET_USER, variables: { id } })
      .valueChanges.pipe(map(r => r.data.user));
  }

  createUser(input: CreateUserInput) {
    return this.apollo.mutate<{ createUser: User }>({
      query: CREATE_USER, variables: { input },   // errors surface in result.errors
    });
  }

  userCreated(): Observable<User> {
    return this.apollo
      .subscribe<{ userCreated: User }>({ query: USER_CREATED })
      .pipe(map(r => r.data!.userCreated));
  }
}
```

<a id="gql-matrix"></a>
## GraphQL — Multiplex Matrix (same client → every server)

| Client → Server | HTTP URL | WS URL (subscriptions) | Subscriptions? |
|---|---|---|---|
| Apollo → **Raw Java (graphql-java)** | `http://localhost:8080/graphql` | — unless you build a graphql-ws transport | ✗ (DIY) |
| Apollo → **Spring Boot** | `http://localhost:8080/graphql` | `ws://localhost:8080/graphql` | ✓ |
| Apollo → **Flask + Ariadne** | `http://localhost:5000/graphql` | — (WSGI has no WebSocket) | ✗ |
| Apollo → **FastAPI + Strawberry** | `http://localhost:8000/graphql` | `ws://localhost:8000/graphql` | ✓ |

Queries and mutations are identical against all four — the schema is the contract, and Apollo doesn't care what executes it. The split-link only helps where a `graphql-ws` endpoint exists; against Flask/raw-Java you'd poll (`pollInterval`) instead of subscribing.

<a id="gql-paging"></a>
## GraphQL — Pagination & Lazy Loading

GraphQL has lazy loading **built into execution**: a field's resolver only runs if the query asks for that field. The `@BatchMapping team` resolver earlier never executes unless the client selects `team` — that's per-field laziness REST can't express. Two more layers on top:

**1. Relay connections — the standard cursor pagination envelope:**

```graphql
type Query {
  users(first: Int! = 20, after: String): UserConnection!   # first REQUIRED + clamped:
}                                                           # schema can't say "max 100" —
type UserConnection {                                       # clamp in the resolver
  edges: [UserEdge!]!
  pageInfo: PageInfo!
}
type UserEdge { node: User! cursor: String! }               # per-edge cursor → resume anywhere
type PageInfo { endCursor: String hasNextPage: Boolean! }
```

Resolver (Spring for GraphQL) — same keyset SQL and n+1 trick as REST, different envelope:

```java
@QueryMapping
public UserConnection users(@Argument int first, @Argument String after) {
    int size = Math.min(first, 100);                          // the clamp
    var rows = repo.pageAfter(Cursor.decode(after), size + 1);
    boolean hasNext = rows.size() > size;
    var page = hasNext ? rows.subList(0, size) : rows;
    var edges = page.stream()
            .map(u -> new UserEdge(u, Cursor.encode(u)))
            .toList();
    return new UserConnection(edges, new PageInfo(
            edges.isEmpty() ? null : edges.getLast().cursor(), hasNext));
}
```

(Strawberry/Ariadne: identical shape — a `UserConnection` type returned from the `users` resolver; Strawberry also ships `strawberry.relay` helpers.)

**2. Client-side lazy loading — Apollo `fetchMore` + a merge policy.** The cache must know pages of `users` belong together; `relayStylePagination()` does the merging:

```jsx
// once, at client setup — without this, page 2 REPLACES page 1 in the cache
new ApolloClient({
  link,
  cache: new InMemoryCache({
    typePolicies: { Query: { fields: { users: relayStylePagination() } } },
  }),
});

const USERS = gql`query Users($first: Int!, $after: String) {
  users(first: $first, after: $after) {
    edges { node { id name } cursor }
    pageInfo { endCursor hasNextPage }
  }
}`;

function UserList() {
  const { data, fetchMore, loading } = useQuery(USERS, { variables: { first: 20 } });
  const info = data?.users.pageInfo;
  return (<>
    {data?.users.edges.map(e => <p key={e.node.id}>{e.node.name}</p>)}
    {info?.hasNextPage && (
      <button disabled={loading}
              onClick={() => fetchMore({ variables: { after: info.endCursor } })}>
        load more
      </button>)}     {/* swap the button for the IntersectionObserver sentinel
                          from the REST section for infinite scroll */}
  </>);
}
```

Angular (apollo-angular) — `watchQuery` + the same `fetchMore`; the cache policy does the appending, so the template just renders `valueChanges`:

```typescript
export class UserListComponent {
  usersQuery = this.apollo.watchQuery<UsersResult>({
    query: USERS, variables: { first: 20 },
  });
  users$ = this.usersQuery.valueChanges.pipe(map(r => r.data.users));

  constructor(private apollo: Apollo) {}

  more(endCursor: string | null) {
    this.usersQuery.fetchMore({ variables: { after: endCursor } });
  }
}
```

**Interview notes:** `totalCount` on a connection is opt-in and approximate — a COUNT can cost more than the page. And `@defer`/`@stream` directives are the emerging spec-level lazy loading (server flushes the cheap fields first, deferred fragments arrive incrementally over the same response) — name-drop, don't design around them.

---

# Topic 3 — gRPC

<a id="grpc-wire"></a>
## gRPC — How It Works

gRPC is HTTP/2 POSTs with a fixed shape. One call `GetUser(id=42)` becomes:

```
:method: POST
:path: /user.v1.UserService/GetUser     ← package.Service/Method IS the route
content-type: application/grpc+proto
grpc-timeout: 2S                        ← deadline travels as a header
authorization: Bearer …                 ← "headers" = Metadata

DATA frame: [compressed-flag:1B][length:4B][protobuf bytes]   ← the "body"

← response DATA frames, then TRAILERS:
grpc-status: 0        ← the real status lives in trailers, not the HTTP status
grpc-message: …
```

What's *missing*: no query params, no path variables. **Everything that varies goes in the request message.** The path is fixed per method and generated from the proto — versioning therefore lives in the proto `package`.

<a id="grpc-proto"></a>
## gRPC — The Proto Contract (shared by all servers and clients)

```protobuf
syntax = "proto3";

package user.v1;                          // ── VERSION: baked into every RPC path
option java_multiple_files = true;
option java_package = "com.example.user.v1";

service UserService {
  // Unary — the REST-equivalent shape
  rpc GetUser(GetUserRequest) returns (User);

  // Server streaming — one request, many responses (feeds, watch APIs)
  rpc ListUsers(ListUsersRequest) returns (stream User);

  // Bidirectional streaming — both sides send freely (chat, sync)
  rpc Chat(stream ChatMessage) returns (stream ChatMessage);
}

message GetUserRequest {
  int64 id = 1;            // ── would be a PATH VARIABLE in REST
  bool  verbose = 2;       // ── would be a QUERY PARAM in REST
}

message ListUsersRequest {
  int32  page_size = 1;    // pagination = plain fields, not ?page=…
  string page_token = 2;
  string status_filter = 3;
}

message User {
  int64  id = 1;           // field NUMBERS are the wire contract —
  string name = 2;         // renaming a field is safe, renumbering breaks
  string email = 3;        // every deployed client
}

message ChatMessage {
  string room = 1;
  string text = 2;
}
```

A breaking change (`user.v2`) is a **new package** → new paths → both versions served side by side by registering both services.

<a id="grpc-raw-java"></a>
## gRPC — Raw Java (grpc-java, no Spring)

```java
import io.grpc.*;
import io.grpc.stub.StreamObserver;
import com.example.user.v1.*;

public class UserServiceImpl extends UserServiceGrpc.UserServiceImplBase {

    @Override
    public void getUser(GetUserRequest req, StreamObserver<User> out) {
        if (req.getId() <= 0) {
            // Errors are Status codes delivered in trailers — never throw raw
            out.onError(Status.INVALID_ARGUMENT
                    .withDescription("id must be positive")
                    .asRuntimeException());
            return;
        }
        out.onNext(User.newBuilder()
                .setId(req.getId()).setName("Ada").setEmail("ada@example.com")
                .build());
        out.onCompleted();          // forgetting this hangs the client until deadline
    }

    @Override
    public void listUsers(ListUsersRequest req, StreamObserver<User> out) {
        for (long id = 1; id <= req.getPageSize(); id++) {   // server streaming:
            out.onNext(User.newBuilder().setId(id).build()); // N onNext calls
        }
        out.onCompleted();
    }

    @Override
    public StreamObserver<ChatMessage> chat(StreamObserver<ChatMessage> out) {
        // Bidi: return an observer for inbound; write outbound whenever you like
        return new StreamObserver<>() {
            @Override public void onNext(ChatMessage msg)  { out.onNext(msg); } // echo
            @Override public void onError(Throwable t)     { }
            @Override public void onCompleted()            { out.onCompleted(); }
        };
    }
}
```

```java
// Bootstrap + a Metadata ("header") interceptor for auth
public class GrpcMain {
    public static void main(String[] args) throws Exception {
        ServerInterceptor auth = new ServerInterceptor() {
            static final Metadata.Key<String> AUTH =
                Metadata.Key.of("authorization", Metadata.ASCII_STRING_MARSHALLER);

            @Override
            public <ReqT, RespT> ServerCall.Listener<ReqT> interceptCall(
                    ServerCall<ReqT, RespT> call, Metadata headers,
                    ServerCallHandler<ReqT, RespT> next) {
                if (headers.get(AUTH) == null) {
                    call.close(Status.UNAUTHENTICATED.withDescription("missing token"),
                               new Metadata());
                    return new ServerCall.Listener<>() {};
                }
                return next.startCall(call, headers);
            }
        };

        Server server = ServerBuilder.forPort(9090)
                .addService(ServerInterceptors.intercept(new UserServiceImpl(), auth))
                .maxInboundMessageSize(4 * 1024 * 1024)   // 4 MB default — know it exists
                .build()
                .start();
        server.awaitTermination();
    }
}
```

Java client (service-to-service):

```java
ManagedChannel channel = ManagedChannelBuilder
        .forAddress("localhost", 9090)
        .usePlaintext()                       // prod: TLS
        .defaultLoadBalancingPolicy("round_robin")  // client-side LB across resolved IPs
        .build();

UserServiceGrpc.UserServiceBlockingStub stub =
        UserServiceGrpc.newBlockingStub(channel)
                .withDeadlineAfter(2, TimeUnit.SECONDS);   // ALWAYS set a deadline

try {
    User u = stub.getUser(GetUserRequest.newBuilder().setId(42).build()); // unary
    stub.listUsers(ListUsersRequest.newBuilder().setPageSize(10).build())
        .forEachRemaining(user -> System.out.println(user.getName()));    // server stream
} catch (StatusRuntimeException e) {
    // e.getStatus().getCode(): NOT_FOUND, DEADLINE_EXCEEDED, UNAVAILABLE (retryable)…
}
```

Say out loud: channels are expensive (create once, share); deadlines propagate to downstream gRPC calls automatically (a shrinking budget, unlike REST timeouts which reset per hop); `UNAVAILABLE`/`DEADLINE_EXCEEDED` are retryable, `INVALID_ARGUMENT` is not.

<a id="grpc-spring"></a>
## gRPC — Spring Boot

Proto and generated code identical — Spring replaces only bootstrap and wiring. Two starters: `net.devh:grpc-spring-boot-starter` (mature community one, shown) and the Spring team's official `spring-grpc` (same shape).

```yaml
# application.yml — replaces ServerBuilder/ManagedChannelBuilder code
grpc:
  server:
    port: 9090
    max-inbound-message-size: 4MB
  client:
    user-service:
      address: 'discovery:///user-service'   # or static://localhost:9090
      negotiation-type: plaintext            # prod: TLS
      default-load-balancing-policy: round_robin
```

```java
// Server: @GrpcService replaces ServerBuilder.addService(...).start()
@GrpcService
public class UserGrpcService extends UserServiceGrpc.UserServiceImplBase {

    private final UserRepository repo;      // full Spring DI, unlike raw grpc-java
    public UserGrpcService(UserRepository repo) { this.repo = repo; }

    @Override
    public void getUser(GetUserRequest req, StreamObserver<User> out) {
        repo.findById(req.getId())
            .map(u -> User.newBuilder().setId(u.id()).setName(u.name()).build())
            .ifPresentOrElse(
                u -> { out.onNext(u); out.onCompleted(); },
                () -> out.onError(Status.NOT_FOUND
                        .withDescription("user " + req.getId())
                        .asRuntimeException()));
    }
}

@GrpcGlobalServerInterceptor                // global auth/logging interceptor
class AuthInterceptor implements ServerInterceptor { /* same code as raw version */ }
```

```java
// Client: @GrpcClient injects a stub built from the yml channel config
@Service
public class UserClient {

    @GrpcClient("user-service")             // name matches grpc.client.<name> in yml
    private UserServiceGrpc.UserServiceBlockingStub stub;

    public UserDto fetch(long id) {
        try {
            User u = stub.withDeadlineAfter(2, TimeUnit.SECONDS)   // deadline still YOUR job
                         .getUser(GetUserRequest.newBuilder().setId(id).build());
            return new UserDto(u.getId(), u.getName(), u.getEmail());
        } catch (StatusRuntimeException e) {
            if (e.getStatus().getCode() == Status.Code.NOT_FOUND)
                throw new UserNotFoundException(id);
            throw e;
        }
    }
}
```

Note: gRPC runs on a second port (9090) beside HTTP (8080) — two ports to secure, health-check, and expose in k8s.

<a id="grpc-python"></a>
## gRPC — Python (grpcio)

gRPC in Python is framework-independent — **Flask and FastAPI don't host it**; the gRPC server is its own process/port beside the web app. Codegen:

```bash
python -m grpc_tools.protoc -I proto \
    --python_out=. --grpc_python_out=. proto/user.proto
# → user_pb2.py (messages), user_pb2_grpc.py (stubs + servicer base)
```

```python
import grpc
from concurrent import futures
import user_pb2, user_pb2_grpc

class UserService(user_pb2_grpc.UserServiceServicer):

    def GetUser(self, request, context):
        if request.id <= 0:                     # abort = Status in trailers
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "id must be positive")
        md = dict(context.invocation_metadata())        # ── "headers" = metadata
        return user_pb2.User(id=request.id, name="Ada", email="ada@example.com")

    def ListUsers(self, request, context):      # server streaming = a generator
        for i in range(request.page_size):
            yield user_pb2.User(id=i + 1, name=f"user-{i + 1}")

    def Chat(self, request_iterator, context):  # bidi = iterate in, yield out
        for msg in request_iterator:
            yield msg                           # echo

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()
```

```python
# Client — sync stub with deadline + metadata
with grpc.insecure_channel("localhost:50051") as channel:
    stub = user_pb2_grpc.UserServiceStub(channel)
    try:
        user = stub.GetUser(
            user_pb2.GetUserRequest(id=42),
            timeout=2.0,                                     # ── deadline
            metadata=[("authorization", "Bearer …")])        # ── headers
        for u in stub.ListUsers(user_pb2.ListUsersRequest(page_size=10)):
            print(u.name)                                    # server stream
    except grpc.RpcError as e:
        e.code()      # StatusCode.NOT_FOUND / DEADLINE_EXCEEDED / UNAVAILABLE
```

In an async (FastAPI-style) codebase use `grpc.aio`: `server = grpc.aio.server()`, `async def GetUser`, `async for` on streams — same generated code, event-loop friendly. Python servers also suffer the GIL for CPU-bound work — scale with multiple processes, not `max_workers`.

<a id="grpc-react"></a>
## gRPC — React Client (grpc-web)

Browsers **cannot speak native gRPC** — no access to HTTP/2 frames or trailers from JS. The bridge is the **grpc-web** protocol plus a translating proxy (Envoy, or Connect servers speaking it natively). Limits: unary + server-streaming only — no client/bidi streaming from browsers.

```yaml
# envoy snippet: browser (grpc-web, :8081) → backend (native gRPC)
# The SAME proxy multiplexes to the Java or Python server — clients never know.
route_config:
  virtual_hosts:
    - domains: ["*"]
      routes:
        - match: { prefix: "/user.v1.UserService" }
          route: { cluster: grpc_backend }     # cluster → java:9090 or python:50051
http_filters:
  - name: envoy.filters.http.grpc_web          # translates grpc-web ↔ grpc
  - name: envoy.filters.http.cors              # browser calls still need CORS
```

```bash
protoc -I proto user.proto \
  --js_out=import_style=commonjs:./src/gen \
  --grpc-web_out=import_style=typescript,mode=grpcwebtext:./src/gen
```

```jsx
import { UserServiceClient } from "./gen/UserServiceClientPb";
import { GetUserRequest, ListUsersRequest } from "./gen/user_pb";

// Points at ENVOY, not the gRPC server
const client = new UserServiceClient(import.meta.env.VITE_GRPC_WEB); // http://localhost:8081

function UserView({ id }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const req = new GetUserRequest();
    req.setId(id);                                  // fields, not URL parts
    client.getUser(req, { authorization: `Bearer ${token}` }, (err, resp) => {
      if (err) return console.error(err.code, err.message);  // grpc Status, not HTTP
      setUser(resp.toObject());                     // protobuf → plain JS object
    });
  }, [id]);

  return user ? <p>{user.name}</p> : <p>loading…</p>;
}

// Server streaming works in browsers:
const stream = client.listUsers(new ListUsersRequest().setPageSize(10), {});
stream.on("data", u => console.log(u.getName()));
stream.on("error", e => console.error(e.code));
stream.on("end", () => console.log("done"));
```

Modern alternative worth naming: **Connect** (`@connectrpc/connect-web`) — same protos, promise-based generated clients, no Envoy needed if the server speaks the Connect protocol.

<a id="grpc-angular"></a>
## gRPC — Angular Client (grpc-web)

Same generated client — wrap it in an injectable service and adapt callbacks to RxJS.

```typescript
@Injectable({ providedIn: "root" })
export class UserGrpcService {
  // Envoy endpoint from environment — the multiplex point
  private client = new UserServiceClient(environment.grpcWeb);

  getUser(id: number): Observable<User.AsObject> {
    const req = new GetUserRequest();
    req.setId(id);
    return new Observable(sub => {
      this.client.getUser(req, { authorization: `Bearer ${token()}` },
        (err, resp) => {
          if (err) { sub.error(err); return; }       // err.code = grpc StatusCode
          sub.next(resp.toObject());
          sub.complete();
        });
    });
  }

  listUsers(pageSize: number): Observable<User.AsObject> {
    const req = new ListUsersRequest();
    req.setPageSize(pageSize);
    return new Observable(sub => {
      const stream = this.client.listUsers(req, {});
      stream.on("data", u => sub.next(u.toObject())); // one next per streamed message
      stream.on("error", e => sub.error(e));
      stream.on("end", () => sub.complete());
      return () => stream.cancel();                   // teardown cancels the RPC
    });
  }
}
```

<a id="grpc-matrix"></a>
## gRPC — Multiplex Matrix (same client → every server)

| Client → Server | Route | What changes in the client |
|---|---|---|
| Java/Python stub → **Raw Java server** | direct `localhost:9090` | nothing — native gRPC |
| Java/Python stub → **Spring Boot server** | direct `localhost:9090` | nothing — same wire protocol |
| Java/Python stub → **Python server** | direct `localhost:50051` | nothing — proto is the contract |
| React/Angular → **any of the above** | browser → Envoy `:8081` → backend | **nothing** — Envoy's cluster config picks the backend; the generated client is identical |

The strongest multiplex story of the four protocols: the proto file generates *both* sides in *every* language, so swapping Java ↔ Python backends is an Envoy config edit, invisible to every client.

<a id="grpc-paging"></a>
## gRPC — Pagination & Lazy Loading

gRPC offers **two lazy shapes** — pick per use case, and be ready to defend the choice:

| | Page tokens (unary, AIP-158) | Server streaming (`stream User`) |
|---|---|---|
| Laziness | Pull — client asks for each page | Push with backpressure — HTTP/2 flow control paces the server |
| Resumable | ✓ — token survives disconnect/retry | ✗ — a dropped stream restarts from zero |
| Retry-friendly | ✓ — each page is an idempotent unary call | Partial results on failure |
| Browser (grpc-web) | ✓ | ✓ (server-streaming is supported) |
| Use for | UI lists, resumable exports | Live feeds, unbounded result sets consumed once |

**Page tokens** — the Google API standard (AIP-158): `page_size`/`page_token` in the request, `next_page_token` in the response, empty token = last page:

```protobuf
service UserService {
  rpc ListUsersPage(ListUsersRequest) returns (ListUsersResponse);  // unary + tokens
}
message ListUsersResponse {
  repeated User users = 1;
  string next_page_token = 2;   // "" = last page — proto3 has no null
}
```

```java
@Override
public void listUsersPage(ListUsersRequest req, StreamObserver<ListUsersResponse> out) {
    int size = req.getPageSize() == 0 ? 20 : Math.min(req.getPageSize(), 100); // clamp
    var rows = repo.pageAfter(Cursor.decode(req.getPageToken()), size + 1);    // same
    boolean hasNext = rows.size() > size;                                      // keyset SQL
    var page = hasNext ? rows.subList(0, size) : rows;
    out.onNext(ListUsersResponse.newBuilder()
            .addAllUsers(page.stream().map(this::toProto).toList())
            .setNextPageToken(hasNext ? Cursor.encode(page.getLast()) : "")
            .build());
    out.onCompleted();
}
```

```java
// Java client — drain all pages (each page an independent, retryable unary call)
String token = "";
do {
    ListUsersResponse resp = stub.withDeadlineAfter(2, TimeUnit.SECONDS)
            .listUsersPage(ListUsersRequest.newBuilder()
                    .setPageSize(100).setPageToken(token).build());
    resp.getUsersList().forEach(this::process);
    token = resp.getNextPageToken();
} while (!token.isEmpty());
```

Python mirrors it exactly (`request.page_token`, `response.next_page_token`); note the streaming variant is *already* lazy in Python — a servicer generator `yield`s one message at a time and pauses when HTTP/2 flow control fills the window.

**Browser lazy loading (grpc-web)** — same page-token loop, wired to the REST section's IntersectionObserver sentinel:

```jsx
const loadMore = useCallback(() => {
  const req = new ListUsersRequest();
  req.setPageSize(20);
  req.setPageToken(token.current);           // "" on first call
  client.listUsersPage(req, {}, (err, resp) => {
    if (err) return;
    setItems(prev => [...prev, ...resp.getUsersList().map(u => u.toObject())]);
    token.current = resp.getNextPageToken();
    if (!token.current) setDone(true);       // empty token = stop observing
  });
}, []);
```

Angular: the same `Observable`-wrapped call from the [gRPC Angular section](#grpc-angular), with the service holding `token` exactly like the REST `UserPager`.

---

# Topic 4 — WebSocket

<a id="ws-wire"></a>
## WebSocket — How It Works

A WebSocket starts life as an HTTP GET — which is why it traverses proxies and shares port 443:

```
GET /ws/chat/general?token=abc123 HTTP/1.1        ← path variable & query param
Host: example.com                                    exist ONLY here
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==       ← random 16 bytes, base64
Sec-WebSocket-Protocol: chat.v2                   ← subprotocol = a versioning surface
Sec-WebSocket-Version: 13

HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

After the `101`, HTTP is over: the same TCP connection carries frames (2–14 byte header + payload; client→server frames XOR-masked per RFC 6455). The accept key is SHA-1 of the client key plus a fixed GUID:

```java
// The entire cryptographic content of the handshake:
String acceptKey = Base64.getEncoder().encodeToString(
        MessageDigest.getInstance("SHA-1").digest(
                (clientKey + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11")
                        .getBytes(StandardCharsets.US_ASCII)));
```

Because frames have no request/response semantics, message types, correlation, and errors must live in **your own envelope**, e.g. `{"type":"chat.send","v":2,"corrId":"…","payload":{…}}` — you are rebuilding what HTTP methods/paths/status codes gave you for free.

<a id="ws-raw-java"></a>
## WebSocket — Raw Java (Jakarta `@ServerEndpoint`)

Runs on any Jakarta container (Tomcat, Jetty) or standalone Tyrus.

```java
import jakarta.websocket.*;
import jakarta.websocket.server.PathParam;
import jakarta.websocket.server.ServerEndpoint;

import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

// URI template: path variable {room}; version could live here: /ws/v1/chat/{room}
@ServerEndpoint("/ws/chat/{room}")
public class ChatEndpoint {

    // The server HOLDS state per connection — the defining difference from REST
    private static final Map<String, Set<Session>> rooms = new ConcurrentHashMap<>();

    @OnOpen
    public void onOpen(Session session, @PathParam("room") String room) throws Exception {
        // ── query params: available ONLY at handshake time
        List<String> token = session.getRequestParameterMap().get("token"); // ?token=…
        if (token == null || !valid(token.get(0))) {
            session.close(new CloseReason(
                    CloseReason.CloseCodes.VIOLATED_POLICY, "bad token")); // close code 1008
            return;
        }
        session.getUserProperties().put("room", room);   // per-connection storage
        rooms.computeIfAbsent(room, r -> ConcurrentHashMap.newKeySet()).add(session);
    }

    @OnMessage   // fires per inbound frame — no URL, no verb, just the payload
    public void onMessage(String message, Session session,
                          @PathParam("room") String room) {
        for (Session s : rooms.getOrDefault(room, Set.of())) {
            if (s.isOpen()) s.getAsyncRemote().sendText(message);  // async: no slow-client block
        }
    }

    @OnClose
    public void onClose(Session session, @PathParam("room") String room) {
        rooms.getOrDefault(room, Set.of()).remove(session);   // leak if you forget
    }

    @OnError
    public void onError(Session session, Throwable t) { /* log; container closes */ }

    private boolean valid(String token) { return !token.isBlank(); }
}
```

JDK 11+ Java *client* (service-to-service or tests):

```java
WebSocket ws = HttpClient.newHttpClient()
        .newWebSocketBuilder()
        .subprotocols("chat.v2")                       // version negotiation
        .buildAsync(URI.create("ws://localhost:8080/ws/chat/general?token=abc123"),
                    new WebSocket.Listener() {
                        @Override
                        public CompletionStage<?> onText(WebSocket w, CharSequence data,
                                                         boolean last) {
                            System.out.println("received: " + data);
                            return WebSocket.Listener.super.onText(w, data, last);
                        }
                    })
        .join();
ws.sendText("hello room", true);
ws.sendClose(WebSocket.NORMAL_CLOSURE, "done");
```

<a id="ws-spring"></a>
## WebSocket — Spring Boot (raw handler + STOMP)

`spring-boot-starter-websocket`. Two levels — know both and when each applies.

**Level 1 — raw `WebSocketHandler` (you own the message protocol):**

```java
@Configuration
@EnableWebSocket
public class WsConfig implements WebSocketConfigurer {

    @Override
    public void registerWebSocketHandlers(WebSocketHandlerRegistry registry) {
        registry.addHandler(new ChatHandler(), "/ws/v1/chat")   // version in the path
                .setAllowedOrigins("http://localhost:5173", "http://localhost:4200")
                .addInterceptors(new AuthHandshakeInterceptor());
    }
}

// Query params & headers exist only at handshake → capture them here into attributes
class AuthHandshakeInterceptor implements HandshakeInterceptor {
    @Override
    public boolean beforeHandshake(ServerHttpRequest request, ServerHttpResponse response,
                                   WebSocketHandler handler, Map<String, Object> attrs) {
        String token = UriComponentsBuilder.fromUri(request.getURI())
                .build().getQueryParams().getFirst("token");     // ?token=…
        if (token == null) return false;                         // rejects with 403, no upgrade
        attrs.put("userId", resolveUser(token));                 // → session.getAttributes()
        return true;
    }
    @Override
    public void afterHandshake(ServerHttpRequest req, ServerHttpResponse res,
                               WebSocketHandler h, Exception ex) {}
    private String resolveUser(String token) { return "u-42"; }
}

class ChatHandler extends TextWebSocketHandler {
    private final Set<WebSocketSession> sessions = ConcurrentHashMap.newKeySet();

    @Override
    public void afterConnectionEstablished(WebSocketSession session) {
        sessions.add(session);   // session.getAttributes().get("userId") from interceptor
    }

    @Override
    protected void handleTextMessage(WebSocketSession session, TextMessage message)
            throws Exception {
        for (WebSocketSession s : sessions)
            if (s.isOpen()) s.sendMessage(message);              // broadcast (single node!)
    }

    @Override
    public void afterConnectionClosed(WebSocketSession session, CloseStatus status) {
        sessions.remove(session);
    }
}
```

**Level 2 — STOMP (Spring supplies routing, pub/sub, cluster fan-out):**

STOMP adds a frame protocol *on top of* WebSocket (destinations, subscriptions) — it restores the "path + routing" layer raw WebSocket lacks, so Spring can route messages like it routes HTTP.

```java
@Configuration
@EnableWebSocketMessageBroker
public class StompConfig implements WebSocketMessageBrokerConfigurer {

    @Override
    public void registerStompEndpoints(StompEndpointRegistry registry) {
        registry.addEndpoint("/ws")                 // the one HTTP handshake URL
                .setAllowedOrigins("http://localhost:5173", "http://localhost:4200")
                .withSockJS();                      // long-polling fallback for old proxies
    }

    @Override
    public void configureMessageBroker(MessageBrokerRegistry config) {
        config.setApplicationDestinationPrefixes("/app");   // client → @MessageMapping
        config.enableSimpleBroker("/topic", "/queue");      // broker → subscribers
        // Multi-node: replace with a real broker relay so broadcasts cross instances:
        // config.enableStompBrokerRelay("/topic").setRelayHost("rabbitmq")…
    }
}

@Controller   // note: NOT @RestController — these are message endpoints
public class ChatStompController {

    private final SimpMessagingTemplate template;
    public ChatStompController(SimpMessagingTemplate template) { this.template = template; }

    // Client SENDs to /app/chat/general → routed here, like @GetMapping for messages
    @MessageMapping("/chat/{room}")
    @SendTo("/topic/chat/{room}")                    // return value → all subscribers
    public ChatMessage relay(@DestinationVariable String room,   // ── the WS "path variable"
                             @Payload ChatMessage msg,           // ── the "body"
                             @Header("simpSessionId") String sessionId,  // ── STOMP headers
                             Principal principal) {              // authenticated user
        return new ChatMessage(room, principal.getName(), msg.text());
    }

    // Server-initiated push from anywhere in the app (the thing REST can't do):
    public void notifyUser(String username, Notification n) {
        template.convertAndSendToUser(username, "/queue/notifications", n);
    }
}
```

Decision rule: raw handler for custom or binary protocols (games, CRDT collab editing); STOMP for subscribe/broadcast semantics and a path to a clustered broker without building the fan-out backplane yourself.

<a id="ws-flask"></a>
## WebSocket — Python Flask (flask-sock)

WSGI's request/response model doesn't fit WebSocket; `flask-sock` (via `simple-websocket`) holds the worker thread for the connection's lifetime — **one thread per connection**, so a few thousand connections is the practical ceiling. Note: Flask-**SocketIO** is a different beast — Socket.IO is its own protocol with fallbacks, *not* raw WebSocket, and browser `new WebSocket()` cannot talk to it.

```python
from collections import defaultdict
from flask import Flask, request
from flask_sock import Sock

app = Flask(__name__)
sock = Sock(app)

rooms: dict[str, set] = defaultdict(set)

@sock.route("/ws/chat/<room>")              # ── path variable, Flask-style
def chat(ws, room):
    token = request.args.get("token")       # ── query param: handshake only
    if not token:
        ws.close(1008, "missing token")     # close code 1008 = policy violation
        return
    rooms[room].add(ws)
    try:
        while True:
            msg = ws.receive()              # blocks THIS thread until a frame arrives
            for peer in set(rooms[room]):
                peer.send(msg)              # broadcast (single node, single process!)
    finally:
        rooms[room].discard(ws)             # leak if you forget

# gunicorn needs a threaded/gevent worker: gunicorn -k gevent app:app
```

<a id="ws-fastapi"></a>
## WebSocket — Python FastAPI

Native support — ASGI speaks WebSocket. Async: one event loop holds 10k+ connections; path variables and query params bind in the signature exactly like REST routes.

```python
from collections import defaultdict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

class RoomManager:
    def __init__(self):
        self.rooms: dict[str, set[WebSocket]] = defaultdict(set)

    async def broadcast(self, room: str, msg: str):
        for ws in set(self.rooms[room]):
            await ws.send_text(msg)         # per-socket try/except in real code

manager = RoomManager()

@app.websocket("/ws/chat/{room}")
async def chat(ws: WebSocket,
               room: str,                   # ── path variable, typed like REST
               token: str | None = None):   # ── query param (?token=…), handshake-only
    if not token:
        await ws.close(code=1008)           # reject before accept
        return
    await ws.accept()                       # completes the 101 upgrade
    manager.rooms[room].add(ws)
    try:
        while True:
            msg = await ws.receive_text()   # yields the event loop while waiting
            await manager.broadcast(room, msg)
    except WebSocketDisconnect:
        manager.rooms[room].discard(ws)
```

Cross-instance fan-out still needs Redis pub/sub — `manager` only knows this process's sockets.

<a id="ws-react"></a>
## WebSocket — React Client

The browser's native `WebSocket` speaks to **every raw-WS server** below (raw Java, Spring raw handler, flask-sock, FastAPI) — only the URL changes. The hook packages the three things production needs: reconnect with jittered backoff, cleanup on unmount, and a send guard.

```jsx
function useChat(room, token) {
  const [messages, setMessages] = useState([]);
  const wsRef = useRef(null);

  useEffect(() => {
    let closed = false, retry = 0;

    function connect() {
      // path variable in the URL; token as query param — browsers CANNOT
      // set an Authorization header on the handshake
      const ws = new WebSocket(
        `${import.meta.env.VITE_WS_BASE}/ws/chat/${room}?token=${token}`);
      ws.onopen = () => { retry = 0; };
      ws.onmessage = e => setMessages(m => [...m, e.data]);
      ws.onclose = () => {                    // fires on server restart, LB drain, wifi blip
        if (closed) return;
        const delay = Math.min(1000 * 2 ** retry++, 15000) * (0.5 + Math.random() / 2);
        setTimeout(connect, delay);           // exponential backoff + jitter
      };
      wsRef.current = ws;
    }
    connect();
    return () => { closed = true; wsRef.current?.close(1000); };  // normal closure
  }, [room, token]);

  const send = text => {
    if (wsRef.current?.readyState === WebSocket.OPEN) wsRef.current.send(text);
  };
  return { messages, send };
}
```

**STOMP variant** — required for the Spring STOMP broker (a raw `WebSocket` connects but speaks the wrong frame protocol):

```jsx
import { Client } from "@stomp/stompjs";

const client = new Client({
  brokerURL: "ws://localhost:8080/ws",
  connectHeaders: { Authorization: `Bearer ${token}` },  // STOMP CONNECT frame headers —
  reconnectDelay: 5000,                                  // this works where WS headers can't
});
client.onConnect = () => {
  client.subscribe(`/topic/chat/${room}`, m => show(JSON.parse(m.body)));
  client.publish({ destination: `/app/chat/${room}`,
                   body: JSON.stringify({ text: "hi" }) });
};
client.activate();   // …and client.deactivate() on unmount
```

<a id="ws-angular"></a>
## WebSocket — Angular Client

RxJS ships a WebSocket wrapper — `webSocket()` returns a Subject: subscribe = receive, `.next()` = send, and `retry` gives reconnection for free.

```typescript
import { webSocket, WebSocketSubject } from "rxjs/webSocket";

export interface ChatMessage { room?: string; from?: string; text: string; }

@Injectable({ providedIn: "root" })
export class ChatSocketService {
  connect(room: string, token: string): WebSocketSubject<ChatMessage> {
    return webSocket<ChatMessage>({
      url: `${environment.wsBase}/ws/chat/${room}?token=${token}`,
      // default (de)serializer is JSON.parse/stringify — override for plain text
    });
  }
}
```

```typescript
@Component({
  selector: "chat-room",
  template: `
    @for (m of messages; track $index) { <p>{{ m.text }}</p> }
    <input #box (keyup.enter)="send(box.value); box.value = ''" />`,
})
export class ChatRoomComponent implements OnInit, OnDestroy {
  private socket$!: WebSocketSubject<ChatMessage>;
  messages: ChatMessage[] = [];

  constructor(private chat: ChatSocketService) {}

  ngOnInit() {
    this.socket$ = this.chat.connect("general", token());
    this.socket$
      .pipe(retry({ delay: 3000 }))          // auto-reconnect on close/error
      .subscribe(m => this.messages.push(m));
  }
  send(text: string) { this.socket$.next({ text }); }   // next() = send a frame
  ngOnDestroy() { this.socket$.complete(); }            // closes the socket
}
```

**STOMP variant** for the Spring broker — `@stomp/rx-stomp` wraps the same STOMP client in Observables:

```typescript
const rxStomp = new RxStomp();
rxStomp.configure({ brokerURL: "ws://localhost:8080/ws", reconnectDelay: 5000 });
rxStomp.activate();
rxStomp.watch(`/topic/chat/${room}`)                   // subscribe as Observable
       .subscribe(m => this.messages.push(JSON.parse(m.body)));
rxStomp.publish({ destination: `/app/chat/${room}`, body: JSON.stringify({ text }) });
```

<a id="ws-matrix"></a>
## WebSocket — Multiplex Matrix (same client → every server)

| Client → Server | URL | Client code | Notes |
|---|---|---|---|
| native WS / rxjs → **Raw Java (Jakarta)** | `ws://localhost:8080/ws/chat/{room}?token=…` | identical | |
| native WS / rxjs → **Spring raw handler** | `ws://localhost:8080/ws/v1/chat?token=…` | identical | room via envelope (no path var in this handler) |
| native WS / rxjs → **Flask (flask-sock)** | `ws://localhost:5000/ws/chat/{room}?token=…` | identical | thread-per-connection ceiling server-side |
| native WS / rxjs → **FastAPI** | `ws://localhost:8000/ws/chat/{room}?token=…` | identical | |
| @stomp/stompjs / rx-stomp → **Spring STOMP** | `ws://localhost:8080/ws` | **different** — STOMP frames | the only row needing a different client library |

The contract for raw WebSocket is just "URL + your message envelope," so clients multiplex freely — until a *sub-protocol* (STOMP, Socket.IO, graphql-ws) enters: then both ends must speak it, and mixing raw and sub-protocol clients/servers fails at the first frame.

<a id="ws-paging"></a>
## WebSocket — Pagination & Lazy Loading

WebSocket has **no pagination primitive** — frames are just frames. Pagination becomes message types in your envelope, and the canonical case is chat history: live messages stream in, older history loads lazily on scroll-**up**.

**The envelope — a request/response pair you define:**

```json
→ {"type": "history.request", "room": "general", "before": "msg-1041", "limit": 50}
← {"type": "history.page", "items": [ … ], "nextBefore": "msg-991"}
← {"type": "chat.message", "id": "msg-1042", "text": "hi"}      ← live traffic interleaves!
```

`nextBefore` is the same keyset cursor as everywhere else; `null` means history is exhausted. Because live frames interleave with history pages on one pipe, the `type` field does the demultiplexing that HTTP paths did for free.

**Server — inside the FastAPI receive loop (same dict-dispatch in every server above):**

```python
while True:
    msg = json.loads(await ws.receive_text())
    if msg["type"] == "history.request":
        rows = await repo.messages_before(room, msg.get("before"), msg["limit"] + 1)
        has_more = len(rows) > msg["limit"]
        page = rows[:msg["limit"]]
        await ws.send_json({"type": "history.page", "items": page,
                            "nextBefore": page[-1]["id"] if has_more else None})
    elif msg["type"] == "chat.send":
        await manager.broadcast(room, msg["text"])
```

**React — scroll-up triggers the next history page; one handler demuxes by type:**

```jsx
function ChatRoom({ room }) {
  // useChat from the WS React section, extended to expose onFrame(cb):
  // a listener registry called from ws.onmessage instead of setMessages
  const { send, onFrame } = useChat(room, token);
  const [history, setHistory] = useState([]);
  const oldest = useRef(null);        // nextBefore cursor
  const [ended, setEnded] = useState(false);

  useEffect(() => onFrame(frame => {
    const m = JSON.parse(frame);
    if (m.type === "history.page") {                   // prepend older messages
      setHistory(h => [...m.items, ...h]);
      oldest.current = m.nextBefore;
      if (!m.nextBefore) setEnded(true);
    } else if (m.type === "chat.message") {            // append live messages
      setHistory(h => [...h, m]);
    }
  }), [onFrame]);

  const onScroll = e => {
    if (e.target.scrollTop === 0 && !ended)            // hit the top → load older
      send(JSON.stringify({ type: "history.request", room,
                            before: oldest.current, limit: 50 }));
  };
  return <div onScroll={onScroll} style={{ overflowY: "auto" }}>…</div>;
}
```

Angular: identical protocol — the `WebSocketSubject` from the [Angular WS section](#ws-angular) already JSON-(de)serializes, so the component filters `m.type` in `subscribe` and calls `socket$.next({type: "history.request", …})` from its scroll handler.

**The senior detail — reconnect ordering (ties to the reconnect pitfall):** on (re)connect, *subscribe live first, then backfill lazily* — request history `before: <oldest you have>` and, for the gap after a drop, `since: <newest you have>`. Both windows can overlap live traffic, so **dedupe by message id** when merging. Fetch-then-subscribe has a hole between the fetch and the subscription; subscribe-then-backfill only has overlap, and overlap is fixable client-side.

**Two cheaper lazy patterns worth naming:** lazy *connection* — don't open the socket until the user enters a live view (idle sockets cost server memory and LB slots); lazy *subscription* — one socket, channel subscribe/unsubscribe messages as the user navigates, which is exactly what STOMP destinations and graphql-ws subscriptions give you for free.

---

<a id="frameworks"></a>
## Popular Frameworks

**grpc-java + protobuf (the canonical gRPC stack):**
- **What it is:** Google's official Java implementation; Netty-based async core with blocking, async, and future stub flavors generated per service.
- **When to use:** internal service-to-service APIs, polyglot shops (one proto, 10+ language codegens), streaming APIs.
- **How it works:** channels manage HTTP/2 connections + name resolution + LB policy; interceptors wrap both directions. Server threading: `directExecutor()` vs pooled — CPU-bound work on the transport thread stalls the event loop.
- **Gotchas:** 4 MB default max message; channel creation is expensive (share one); browsers need grpc-web + Envoy or Connect.

**Netty (the engine under most of this):**
- **What it is:** async event-loop NIO framework — beneath grpc-java, Spring WebFlux (Reactor Netty), Vert.x, many WS servers.
- **When to use (directly):** custom binary protocols, extreme connection counts (100k+/node realistic; thread-per-request dies ~10k threads).
- **How it works:** few event-loop threads each owning many channels; handler pipeline (codec → business). Never block an event-loop thread.

**Spring MVC vs Spring WebFlux:**
- **MVC:** thread-per-request on Tomcat (default 200 threads). Simple mental model. With Java 21 virtual threads (`spring.threads.virtual.enabled=true`) the thread ceiling largely disappears for I/O-bound work.
- **WebFlux:** event loop + Reactor (`Mono`/`Flux`) — massive concurrency on few threads, required for reactive streaming at scale. Cost: contagious reactive types, harder debugging.

**FastAPI (Starlette + Uvicorn + Pydantic):**
- **What it is:** ASGI framework where type hints generate parsing, validation (422s), and OpenAPI docs; Starlette supplies routing/WebSocket, uvicorn the event loop.
- **When to use:** Python REST/GraphQL/WebSocket services; the async answer to Flask's WSGI model.
- **How it works:** one event loop per worker; `async def` handlers yield on I/O — thousands of concurrent requests per process vs Flask's `workers × threads`.
- **Gotchas:** a *sync* call (blocking DB driver) inside `async def` stalls every request on the loop — use async drivers or `def` handlers (run in a threadpool); CPU-bound work still needs processes (GIL).

**graphql-java / Spring for GraphQL — and Strawberry / Ariadne (Python):**
- **What they are:** the JVM execution engine + Spring's transport/annotation layer (`@QueryMapping`, `@BatchMapping`, graphql-ws WebSocket transport); Python's code-first (Strawberry, types→schema) and schema-first (Ariadne, SDL→resolvers) equivalents.
- **When to use:** Spring for GraphQL for JVM services; Strawberry with FastAPI when you want subscriptions; Ariadne when the SDL is the source of truth.
- **Gotchas:** subscriptions need an ASGI/WebSocket-capable host — WSGI Flask can't; `@BatchMapping`/DataLoader is the N+1 answer and interviewers will ask.

**Apollo Client (React / Angular):**
- **What it is:** the de-facto GraphQL client: normalized cache (objects merged by `__typename:id`), hooks (`useQuery`/`useMutation`/`useSubscription`) or Observables (apollo-angular), link chain for transport.
- **How it works:** every response is normalized into one cache; a mutation returning changed objects updates every query on screen automatically — the feature REST clients rebuild by hand.
- **Gotchas:** cache updates only merge objects with `id`; list additions need `refetchQueries` or manual `cache.modify`; the split-link (http vs graphql-ws) is boilerplate you must get right for subscriptions.

**STOMP + SockJS (Spring messaging layer):**
- **What it is:** STOMP = text frame protocol with SUBSCRIBE/SEND/destinations over WebSocket; SockJS = transport fallback for proxies that kill upgrades.
- **When to use:** app-style pub/sub (notifications, dashboards, chat) on Spring; skip for custom binary protocols.
- **Key config:** `enableStompBrokerRelay` to RabbitMQ for multi-instance fan-out — the simple broker is in-memory and single-node only.
- **Clients:** `@stomp/stompjs` (React/vanilla), `@stomp/rx-stomp` (Angular).

**grpc-web + Envoy (browser bridge):**
- **What it is:** a wire-compatible gRPC variant browsers can produce (base64/text or binary framing, trailers folded into the body), translated to native gRPC by Envoy's `grpc_web` filter.
- **When to use:** browser frontends against an existing gRPC backend without adding a REST/GraphQL facade.
- **Limits:** unary + server-streaming only — no client/bidi streaming from browsers; CORS still applies; Connect (`connect-es`) is the modern alternative that can skip the proxy.

---

<a id="pitfalls"></a>
## Interview Pitfalls

1. **"gRPC is faster because it's binary" — incomplete, sounds junior.** The wins: protobuf encode/parse (~5–10× cheaper than JSON), HPACK header compression, HTTP/2 multiplexing over a warm connection. Then volunteer the costs: L4 LBs pin the long-lived connection (need L7 or client-side LB), browsers need grpc-web/Connect + proxy, humans can't `curl` it. Tradeoff, not free lunch.

2. **Choosing WebSocket without a reconnect and missed-message story.** Every deploy, LB drain, and network blip drops connections. Design out loud: client reconnects with exponential backoff + jitter (see the React hook), sends `lastSeenMessageId`, server replays from a buffer/log. No recovery story = the design fails the first follow-up.

3. **Forgetting browsers can't set headers on the WebSocket handshake.** `Authorization: Bearer …` is impossible from the browser API. Real options: short-lived one-time token in the query string (keep it out of access logs), cookie auth, or first-message auth with a server-side timeout. STOMP and graphql-ws dodge this with headers in their own CONNECT/init frame — sent *after* the upgrade.

4. **No deadline on gRPC calls.** Default is effectively infinite: a hung downstream pins caller threads and cascades. Always `withDeadlineAfter(...)` / `timeout=`; mention that gRPC propagates the *remaining* deadline downstream automatically — an advantage over REST timeouts, which reset at every hop.

5. **Scaling WebSocket (and GraphQL subscriptions) like REST.** "Add instances" doesn't work alone: connections are stateful and pinned, broadcasts must cross nodes (Redis pub/sub, broker relay), per-connection memory (~20–50 KB) bounds a node. The in-process `listeners`/`rooms` sets in every snippet above are the single-node version — name the backplane unprompted.

6. **Wrong versioning surface.** REST: path/header/media type — never a query param. gRPC: the proto package (`user.v1` → `user.v2`), both served side by side. GraphQL: **no versions** — additive schema evolution + `@deprecated`, and saying "/v2/graphql" signals you haven't used it. WebSocket: URL path or subprotocol + a version field in your envelope.

7. **Reaching for WebSocket when SSE or polling suffices.** One-directional push (notifications, dashboards, live scores) fits Server-Sent Events: plain HTTP, auto-reconnect with `Last-Event-ID` built in, proxy-friendly. WebSocket earns its cost only for genuine bidirectionality or sub-second client→server frequency.

8. **Treating a WSGI stack as protocol-neutral.** Flask can serve REST and GraphQL queries/mutations, but *not* GraphQL subscriptions and only thread-pinned WebSockets — the worker model, not the library, is the constraint. Saying "subscriptions need an ASGI server (or a separate push service)" is a cheap senior signal.

9. **Ignoring CORS and error-shape drift in browser clients.** Every cross-origin fetch/Apollo/grpc-web call needs server-side CORS (and POST-with-JSON triggers preflight OPTIONS). And each backend framework emits a different error body (Problem Details vs `{"detail": […]}` vs GraphQL `errors` array vs grpc Status) — normalize once in the client (interceptor / Apollo error link), not per call site.

10. **Streaming with no flow-control awareness.** Blindly pushing to a slow consumer buffers unboundedly → OOM. Name the fix per protocol: gRPC `ServerCallStreamObserver.isReady()` + `setOnReadyHandler`; WebSocket `getAsyncRemote()` with send timeouts and a drop/queue policy; Reactor's backpressure in `Flux`-based subscriptions. Knowing backpressure exists here is a strong senior signal.
