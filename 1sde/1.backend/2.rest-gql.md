# GraphQL + REST Comparison — Interview Depth

## Index

- [REST vs GraphQL](#rest-vs-graphql)
- [2.1 Flow, schema, resolvers](#21-flow-schema-resolvers)
- [2.2 Filtering & pagination](#22-filtering--pagination)
- [2.3 Errors & exceptions](#23-errors--exceptions)
- [2.4 N+1 & DataLoader](#24-n1--dataloader)
- [2.5 Caching](#25-caching)
- [2.6 Concurrency & async](#26-concurrency--async)
- [2.7 Query safety & performance](#27-query-safety--performance)
- [2.8 Retries](#28-retries)
- [2.9 vs REST, federation, evolution](#29-vs-rest-federation-evolution)
- [2.10 GraphQL security](#210-graphql-security)
- [2.11 Testing (they ask "what tests did you implement")](#211-testing-they-ask-what-tests-did-you-implement)
- [2.x L5-only](#2x-l5-only)
- [Part 2 — GraphQL](#part-2--graphql)
- [References](#references)

- **REST knowledge and questions:** moved to [REST 101](2.rest101#interview-questions).
- **Coverage retained here:** GraphQL mechanics, GraphQL interview answers, and REST/GraphQL comparisons.
- **Example context:** Java/Spring instrument services over Aurora, a document store, and search.
- **Evidence boundary:** first-person platform stories are rehearsal material to adapt only to experience you can substantiate.

<a id="rest-vs-graphql"></a>

## REST vs GraphQL

**L4**

| Dimension | REST | GraphQL |
|---|---|---|
| Contract | Resource endpoints and representations | Typed schema and client-selected fields |
| Read shape | Server-defined; projections or aggregates can be added | Client selects fields within schema and cost limits |
| Caching | GET responses can use ordinary HTTP policies | Entity/client caches; GET or persisted operations can enable HTTP caching |
| Errors | HTTP status plus a structured error body | Transport status plus GraphQL data/errors and null propagation |
| N+1 | Chatty clients or backend ORM/resolver fan-out | Nested resolvers can create backend fan-out |
| Writes | HTTP methods plus domain contracts | Mutation fields plus domain contracts |
| Retries | Method semantics plus deduplication and failure policy | Operation semantics plus deduplication and failure policy |
| Evolution | Compatible changes, consumer coordination, versions when needed | Compatible schema changes, deprecation, consumer coordination |

**L5 extra**

| Option | What it is | Strength | Weakness | Choose when |
|---|---|---|---|---|
| REST | Resource-oriented HTTP API | Familiar infrastructure and stable integration contracts | Divergent client views may need new aggregates | Few stable consumer shapes or public integration endpoints |
| GraphQL | Typed query and mutation layer | Flexible consumer views over shared services | Requires batching, cost controls, field authorization, and operation metrics | Many consumer shapes justify schema governance |
| Both | Two API faces over shared application services | Fits UI and integrator requirements independently | Two contracts and transport test surfaces | Consumer needs justify the extra operating cost |

- **Deciding variables:** diversity of consumer views, acceptable query freedom, cacheability, and team capacity for schema governance.
- **Default:** REST for stable bounded contracts; add GraphQL when client composition needs justify its controls and operational cost.
- Backend N+1 can occur under either API style; measure downstream work per operation.
- GraphQL execution errors can coexist with HTTP success; status-only monitoring is insufficient.
- Neither style provides cross-system transactions or exactly-once effects automatically.
- Detailed comparisons remain in Q47, Q54–Q58, Q65–Q68, and the compact GraphQL answers below.

# 2. GraphQL

## 2.1 Flow, schema, resolvers

**Q39: Explain your GraphQL flow end-to-end.**

**L4**

- Client POSTs `{query, variables, operationName}` to one `/graphql` endpoint.
- **Parse:** convert the query string to an AST.
- **Validate:** check fields, argument types, fragments, and schema rules.
- **Execute:** resolve fields using parent results and the execution context.
- **Respond:** return the selected shape in `data`, with `errors` when applicable.
- My stack: Spring for GraphQL over graphql-java, schema-first SDL in `src/main/resources/graphql/`, `@QueryMapping`/`@SchemaMapping` controllers delegating to the same application services the REST controllers use — one service layer, two protocol faces.

**L5**

- Sibling fields and list items can resolve independently, subject to execution dependencies and implementation scheduling.
- This permits concurrency and can create N+1 backend work (§2.4, §2.6).
- Carry auth and loader state in request context; resolver execution may move across threads.
- **Request failure:** parse/validation errors return `errors` without `data`; fix the document or inputs before retrying.
- **Execution failure:** nullable-field errors can return partial `data` plus `errors` (§2.3).
- Around it: schema SDL is the reviewed contract artifact (schema diff in CI — GraphQL's `oasdiff` equivalent, e.g., graphql-inspector), depth/complexity instrumentation in front of execution (§2.7), and per-operation-name metrics out the back (Datadog tag: `operationName`) — anonymous queries need a normalized operation identity for useful metrics.

**Q40: What is a resolver, exactly?**

**L4**

- A function per schema field: `(parent, args, context, info) → value | CompletableFuture<value>`. graphql-java default resolver = property/getter lookup on the parent — so plain fields on a fetched object cost nothing extra.
- You write explicit resolvers where a field needs its own fetch or shaping.
- Root `Query`/`Mutation` field resolvers are the entry points.

**L5**

- The schema is a _promise that any legal field combination is cheap_
- resolvers are where the promise is kept.
- So L5 resolver design is batching-topology design, decided per field:
- resolves off the parent row → free, default resolver
- needs another entity → DataLoader, always, no exceptions in list positions
- cost can't be bounded → _don't expose it as a nested field_ — we exposed `documents(first: Int!)` with a required, capped limit instead of a bare `documents` list.
- That third category is the one candidates miss: the cheapest guardrail is the field you refuse to add.
- Also: resolvers must be authz-aware or delegated to services that are — a resolver is a new door to the same room (§2.10).

**Q41: Schema design for your domain?**

**L4**

- Types mirror the _read model consumers need_, not DB tables: `Instrument`, `Offering`, `Document`, `Correction`.
- `!` non-null only where absence is impossible
- enums for closed sets
- input types for mutation args
- `interface Node { id: ID! }` for shared identity
- connections on all lists.

```graphql
type Instrument implements Node {
  id: ID!
  isin: String
  status: InstrumentStatus!
  issuer: Issuer # nullable: partner-service sourced
  documents(first: Int!, after: String): DocumentConnection!
  corrections(first: Int!, after: String): CorrectionConnection!
}
type Query {
  instrument(id: ID!): Instrument
  instruments(
    filter: InstrumentFilter
    first: Int!
    after: String
  ): InstrumentConnection!
}
```

**L5**

- Two decisions with defeaters.
- **Nullability is an availability decision**: per spec, a null in a non-null position propagates up to the nearest nullable ancestor — one failed `issuer!` inside a list can null the entire list or the whole `data`.
- Rule we ran: fields backed by _other services_ stay nullable (degrade to holes), fields from our own row are non-null (absence = bug, want the explosion).
- That's error-blast-radius design expressed in the type system.
- **Demand-driven surface**: expose fields consumers asked for, not columns you have — under no-versioning (§2.9) every field is a permanent liability
- the failure prevented is the 200-field God type where nobody can prove which 12 are live.
- Extra L5 morsel: model _identity_ deliberately — global `ID` should be opaque and stable (we base64'd `type:pk`), because Apollo client normalization and federation `@key` both stand on it
- leaking raw numeric PKs as IDs is a migration trap.

**Q42: Schema-first vs code-first?**

**L4**

- Schema-first: SDL files are the source of truth
- resolvers bind to them (Spring for GraphQL's default).
- Code-first: schema generated from annotated code (Netflix DGS supports both; code-first common in JS/Python — Nexus, Strawberry).

**L5**

- Deciding variable: _who reviews the contract_.
- Schema-first makes the SDL a language-neutral artifact product owners and consumer teams can read and diff in PRs — the contract review happens on the contract, not on Java.
- Code-first optimizes single-team velocity and type-safety-by-construction but buries contract changes inside implementation diffs, where a resolver refactor can silently reshape the schema.
- With multiple consumer teams (our case, and Vanguard's), schema-first + CI schema-diff is the defensible default
- say code-first is fine for one-team internal graphs and you've shown judgment, not allegiance.

**Q43: Your actual wiring (be ready to draw it).**

**L4/L5 fused (this one is "prove you built it")**

- `@Controller` classes: `@QueryMapping instrument(@Argument String id)` → application service → repository
- nested `@SchemaMapping(typeName="Instrument") issuer(...)` returning `CompletableFuture` via DataLoader
- `BatchLoaderRegistry` registers mapped batch loaders at startup
- `DataFetcherExceptionResolverAdapter` for the error taxonomy
- `WebGraphQlInterceptor` pulls auth principal + trace id into `GraphQLContext`
- instrumentation beans for depth/complexity caps
- Datadog metrics tagged by operation name
- GraphiQL enabled non-prod only.
- Being able to rattle the _bean names_ is what makes "I used Spring for GraphQL" credible under cross-examination.

## 2.2 Filtering & pagination

**Q44: Filtering?**

**L4**

- Typed filter inputs: `instruments(filter: InstrumentFilter)` with `InstrumentFilter { types: [InstrumentType!], issuedAfter: Date, text: String }`
- resolver compiles it to SQL predicates / OpenSearch query.
- No raw query strings, no generic string DSLs.

**L5**

- The fork is **closed vocabulary vs. generic filter DSL** (`{field, op, value}` trees, and-or nesting).
- The DSL demos beautifully and is a footgun: it is a slow-query construction kit handed to clients — every expressible combination must be index- or mapping-backed or someone will find the seq scan for you in prod
- and it's unvalidatable at the type level (field names as strings).
- Doctrine: _a filter field is a capacity commitment_ — adding one means committing an index/OpenSearch mapping and gets reviewed as such.
- That's also the real answer to "how do you prevent expensive queries": prevention at schema-design time is static and unbypassable
- runtime cost analysis (§2.7) is the fuse behind it.
- Text search: route `text:` to OpenSearch, ids back to Aurora for hydration — say the two-store split out loud, it matches your resume's architecture and invites a question you want.

**Q45: Connections — mechanics + code.**

**L4**

- Relay Connection spec: `(first: Int!, after: String)` → `{ edges { node cursor } pageInfo { hasNextPage endCursor } }`.
- Cursor = keyset position ([REST §1.9](2.rest101#rest-performance) mechanics), opaque base64.
- Standardized envelope: every client, tool, and cache handles paging identically.

```java
@SchemaMapping(typeName = "Instrument")
public CompletableFuture<Connection<Document>> documents(Instrument parent,
    @Argument int first, @Argument String after, DataFetchingEnvironment env) {
  int limit = Math.min(first, 100);                       // hard cap, schema promise kept
  var cursor = Cursor.decode(after);                      // (createdAt, id) tuple
  return env.<DocKey, List<Document>>getDataLoader("docsPage")
            .load(new DocKey(parent.id(), cursor, limit + 1))   // n+1 rows
            .thenApply(rows -> Connections.from(rows, limit));  // 101st row => hasNextPage
}
```

**L5**

- Why the ceremony beats `{items, nextCursor}`: per-edge cursors allow resume-from-any-item
- `pageInfo` carries hasNext without sentinel hacks (the fetch-n+1 mechanism — name it)
- and the uniform shape is what lets Apollo's normalized cache and federation handle paged data generically — the envelope is infrastructure, not bureaucracy.
- Defeaters: `totalCount` is not free — a `COUNT(*)` can cost more than the page (Postgres counts by scanning; order of magnitude: full-index scan on millions of rows)
- we made it opt-in and approximate (OpenSearch `track_total_hits` bounded) — "exact counts on demand" is a requirement to push back on, with the alternative of "≈10,000+" UX.
- And `first` is non-null with a server-side clamp: the schema says required, the resolver enforces the ceiling — belt and suspenders because schema can't express max values.

**Q46: totalCount / page-jumping pushback?**

**L5**

- When product insists on page numbers + exact totals: offset pagination _bounded_ (cap max page × size so the O(offset) cost has a ceiling), count served from a maintained counter or search-engine estimate, and honesty that deep-linking page 4,000 is a non-goal.
- Naming the bounded-offset compromise beats both purist refusal and naive compliance.

## 2.3 Errors & exceptions

**Q47: How does GraphQL error handling differ from REST?**

**L4**

- Transport is (almost always) HTTP 200
- errors ride in the body's `errors[]`: `message`, `path`, `locations`, `extensions`.
- Three classes: **request errors** (parse/validate — `errors` only, no `data`), **field errors** (resolver threw — that field becomes null per nullability rules, siblings survive → _partial results_), **transport errors** (genuine non-200: gateway auth, 429, 5xx).
- Client must check both channels.

**Q48: Built-in vs custom — what did you use?**

**L4**

- Custom taxonomy on top of the built-in shape: `DataFetcherExceptionResolverAdapter` mapping domain exceptions → `GraphQLError` with stable `extensions.code` + graphql-java `ErrorClassification`
- unknown exceptions → sanitized `INTERNAL_ERROR` (default-deny: never leak internal messages into `errors[].message`).

```java
@Component
class GqlExceptions extends DataFetcherExceptionResolverAdapter {
  @Override protected GraphQLError resolveToSingleError(Throwable ex, DataFetchingEnvironment env) {
    return switch (ex) {
      case CorrectionConflictException c -> GraphqlErrorBuilder.newError(env)
          .errorType(ErrorType.BAD_REQUEST)
          .message("Correction conflicts with a newer version")
          .extensions(Map.of("code", "CORRECTION_CONFLICT",
                             "instrumentId", c.instrumentId(),
                             "traceId", MDC.get("traceId")))
          .build();
      case AccessDeniedException a -> GraphqlErrorBuilder.newError(env)
          .errorType(ErrorType.FORBIDDEN)
          .message("Not permitted").extensions(Map.of("code", "FORBIDDEN")).build();
      default -> null;   // falls through to sanitized INTERNAL_ERROR
    };
  }
}
```

**Q49: Errors-as-data — the design fork.**

**L5**

- The spec's `errors[]` is for _exceptional_ failures
- **expected, business-meaningful outcomes belong in the schema** as union result types:

```graphql
union CorrectInstrumentResult =
  | CorrectionSuccess
  | FieldLockedError
  | StaleVersionError
type FieldLockedError {
  field: String!
  lockedBy: String!
  message: String!
}
type Mutation {
  correctInstrument(input: CorrectInput!): CorrectInstrumentResult!
}
```

- Why unions win for these: they're _introspectable_ (codegen forces clients to handle each case — the compiler is your contract test), _extensible when consumers tolerate new variants_ (add a union member = additive), and _typed_ (structured data per error kind, not string codes by convention).
- Costs: schema surface + client match boilerplate → doctrine: unions for mutations and expected read failures
- `errors[]` for genuine faults (bugs, outages, authz).
- Two operational defeaters worth volunteering:
- HTTP-200-always **blinds generic monitoring** — your dashboards say 200s while every body carries errors
- you must emit an error-rate metric from the `errors[]` array tagged by `extensions.code` (`Canonical failure pattern`: the "healthy" GraphQL API that had been failing for hours)
- the exception resolver is the _only_ leak barrier — a missed mapping means a raw Hibernate message in a client-visible error
- default-deny with an allowlist, and alert on INTERNAL_ERROR rate.

**Q50: Partial results — client contract.**

**L5**

- A `data`+`errors` response is a transport _success_
- blanket retry re-executes the parts that worked (and re-runs any committed mutation prefix — §2.8).
- Correct client behavior: render what resolved, per-field fallback for what didn't, targeted refetch of the failed subtree if needed (Apollo `errorPolicy: all` exists for exactly this).
- Server-side you _choose_ blast radius via nullability (§2.1): nullable field = hole in the page
- non-null = amputate the subtree.
- Saying "partial results are a feature I configure with nullability, not an accident" is the L5 sentence.

## 2.4 N+1 & DataLoader

**Q51: What is N+1?**

**L4**

- List of N parents + a child field: 1 fetch for parents, then the child resolver runs once per parent → N more calls.
- `instruments(first: 50) { issuer { name } }` = 1 + 50 issuer lookups.
- Structural, not a bug: execution resolves list items independently (§2.1), so any per-entity fetch in a list position amplifies.

**Q52: DataLoader — mechanism + code.**

**L4**

- Per-request batch + cache.
- Resolvers call `load(key)` → future
- DataLoader accumulates keys during the execution step, dispatches one `batchLoadFn(keys)` (`WHERE id IN (...)`), completes all futures, caches key→value for the request. 51 queries → 2.

```java
@Configuration
class Loaders {
  @Bean BatchLoaderRegistry registry(IssuerRepository repo, Executor gqlExecutor) {
    var registry = new DefaultBatchLoaderRegistry();
    registry.forTypePair(String.class, Issuer.class)
        .withName("issuers")
        .registerMappedBatchLoader((Set<String> ids, BatchLoaderEnvironment env) ->
            Mono.fromCallable(() -> repo.findByIds(ids))     // one IN-query
                .subscribeOn(Schedulers.fromExecutor(gqlExecutor)));
    return registry;
  }
}

@SchemaMapping(typeName = "Instrument")
CompletableFuture<Issuer> issuer(Instrument i, DataLoader<String, Issuer> issuers) {
  return issuers.load(i.issuerId());     // Spring injects the named loader
}
```

**L5 (mechanism)**

- Why batching works at all: graphql-java's execution strategy tracks field-resolution _levels_ and dispatches registered loaders when a level's demands are gathered (`as of` graphql-java's per-level dispatching instrumentation) — batching is a property of cooperative scheduling between executor and loaders, not magic.

**Q53: DataLoader defeaters (this is where they sort levels).**

**L5**

- **Blocking kills it**: `.join()` on a loader future inside a resolver stalls the very thread that would trigger dispatch → deadlock or one-key "batches"
- loaders demand end-to-end async resolvers.
- **Per-request scope is a correctness rule**: a shared/global loader cache serves user A's authz-filtered issuer to user B and stale rows forever — cache lifetime = request lifetime, and any real cache goes _under_ the batch fn, consciously.
- **Batch-fn contract**: results must map to input keys incl. misses (mapped loader sidesteps ordering bugs; list loader with misaligned order = silent wrong-data, worst failure class).
- **Batching flattens breadth, not depth**: 4 nested levels = ≥4 sequential dispatch rounds minimum
- deep schemas need denormalized read models, not more loaders.
- **The relocated N+1**: your batch fn calls `repo.findByIds` which lazy-loads a collection per row → N+1 reborn one layer down, invisible from the GraphQL layer
- the guard is mechanical — assert query counts in an integration test (§2.11).
- IN-list limits: thousands of keys per batch → split batches (`maxBatchSize`) or hit parameter/plan limits.

**Q54: N+1 in REST?**

**L4**

- Client-side: GET list then GET-per-item — the chatty client.
- REST fixes: `?expand=issuer` compound docs, purpose-built aggregate endpoints, BFF.

**L5**

- Sharpest framing: GraphQL doesn't create N+1, it _relocates_ it.
- REST can expose client-side N+1 across HTTP calls, and can also have server-side ORM N+1.
- GraphQL's lives server→DB behind one request: invisible in access logs, paid in DB connections — beneficial when batching reduces measured backend work without excessive coordination cost
- unbatched, you've hidden a fan-out where ops tooling can't see it.
- One paragraph, and it answers "GraphQL vs REST performance" better than any benchmark.

## 2.5 Caching

**Q55: Why is caching harder?**

**L4**

- REST commonly uses URL-based HTTP caching when response policy and authorization permit reuse.
- GraphQL: one endpoint, POST bodies, unbounded query shapes → HTTP caches blind.
- Caching relocates: client normalized caches (Apollo, keyed `__typename:id`), per-request DataLoader dedupe, application caches under resolvers.

**Q56: The four layers, with deciding variables.**

**L5**

- Ordered by ROI for an authed internal API:
- **Entity cache under resolvers** (Caffeine/Redis, `instrument:{id}:v{n}`): shape-agnostic, shared with REST, invalidation via version bump — where ours lived
- highest leverage because every query shape hits it.
- **DataLoader per-request dedupe**: correct by construction, zero staleness risk, free.
- **Whole-response caching** only via persisted queries / GET-with-hash: restores URL-keyability — worth it for public read-heavy graphs
- for authed APIs `Vary: Authorization` fragments it to uselessness, skip.
- **Client normalized cache**: powerful, but a correctness footgun — needs globally stable unique IDs and consistent selections, staleness invisible to the server
- you _design for it_ (opaque global IDs, §2.1) even if you don't operate it.
- Governing defeater: **field-level authz makes unpartitioned response caching unsafe** — same query, different viewer, different data
- cache reusable raw entities with authorization enforced on every response
- partition any response cache by all relevant viewer permissions.

**Q57: APQ mechanics (know it even unused).**

**L4/L5**

- Automatic Persisted Queries: client sends SHA-256 of the query
- server cache-misses → client sends full text once → thereafter hash-only, and queries can go over **GET** → CDN-cacheable, infra-retryable (`as of` Apollo APQ docs).
- Distinguish from the _allowlist_ flavor: build-time registration where unknown hashes are rejected — that one is a security control (§2.7)
- APQ alone is bandwidth + GET restoration, not protection (any client can register any query).
- Conflating them is a common candidate error — drawing the line is free L5 signal.

**Q58: What did you actually run?**

- Entity cache with version-bump invalidation (60s TTL bound), DataLoader per request, no whole-response cache (internal, authed), required-and-clamped `first` so the uncached worst case stays bounded, read-your-writes for the correcting session.
- Defensible, boring, true.

## 2.6 Concurrency & async

**Q59: Are resolvers concurrent?**

**L4**

- Query fields: yes — siblings and list elements may resolve concurrently
- returning `CompletableFuture` makes it explicit and graphql-java composes them.
- **Mutations: spec mandates serial execution of top-level mutation fields in document order** — `{ debit credit }` is deterministic
- that asymmetry is _the_ exam favorite.

**Q60: Executors, pools, virtual threads.**

**L5**

- Parallelism is determined by _where futures complete_, not by the framework: blocking JDBC on the transport thread serializes everything (and starves a reactive transport entirely).
- Blocking work goes to a bounded executor sized to the true constraint — which is the **Hikari pool, not CPU**: 50 concurrent resolvers vs 20 connections = 30 parked threads and a tail-latency cliff
- the concurrency limit belongs at the executor/loader (bulkhead) and must be ≤ pool.
- **Virtual threads** (Java 21 — bridges their other question): `spring.threads.virtual.enabled=true` (Boot 3.2+) makes thread-per-task free for blocking code and deletes pool-sizing guesswork for _threads_ — but VTs mint no DB connections
- the queue moves from thread pool to connection pool, and the fix for connection scarcity is still capacity/limits/replicas.
- Caveat if pushed: VT pinning inside `synchronized` around JDBC was the known trap
- JDK 24 (JEP 491) largely removed it — knowing the JEP number is cheap credibility.

**Q61: When does async pay?**

**L5**

- Only when one query fans out to _independent_ sources — our instrument + OpenSearch text hits + partner doc-service metadata overlapped three backends in one round trip
- that's real latency subtraction.
- Single-DB queries: async buys nothing and costs stack-trace legibility.
- Naming the boundary — "async where there's fan-out, sync where there isn't" — outranks enthusiasm in either direction.

## 2.7 Query safety & performance

**Q62: Defending against expensive queries — ordered by leverage.**

**L4**

- Depth limit (~10), complexity budget (cost/field × list multipliers, reject pre-execution via instrumentation), required + capped `first` everywhere, per-request and per-loader timeouts, persisted-query allowlist for known clients, gateway rate limits.

**L5**

- Rank and admit weaknesses: **schema-level guardrails first** (capped `first`, no unbounded lists, closed filters) — _static_, unbypassable, free at runtime
- **complexity analysis is a fuse, not a firewall** — multipliers are estimates and one mis-costed field is a bypass
- **the allowlist is the only complete defense** (arbitrary-query risk → 0), right for a fixed internal consumer set, at the cost of a registration step and ad-hoc queries (keep GraphiQL+introspection non-prod).
- Pair prevention with **detection**: per-operation-name p95/cost in Datadog — a cost regression surfaces as a _named_ trend, not anonymous noise.
- Depth limits double as the cycle defense (`instrument → issuer → instruments → …` via recursive fragments).
- Aliasing defeater: `a: instruments(first:100) b: instruments(first:100) …` ×50 multiplies cost inside legal depth — complexity budgets must count aliases (naive depth checks don't; this is the known bypass).

**Q63: Overfetch/underfetch — the honest version.**

**L4**

- REST fixed payloads: 40 fields fetched, 4 used (overfetch)
- 3 calls per screen (underfetch).
- GraphQL: field selection solves both at the wire contract — the founding pitch (Facebook mobile, public history 2012→2015 open-sourcing).

**L5**

- Two catches to volunteer.
- Selection trims the _wire_, not the _backend_: `SELECT *` into a full entity moves waste from network to DB/heap
- end-to-end demand-driven needs projection push-down (Q64) — done selectively or not at all.
- The counter-cost: exact selection makes every client query shape a distinct performance profile — REST's rigidity is also its _predictability_ (capacity-plan 5 endpoints vs an open query space)
- persisted queries are how you claw predictability back.
- Closing line: **"GraphQL trades payload efficiency for load predictability — then you spend tooling to buy the predictability back."**

**Q64: Projection push-down.**

**L5**

- `env.getSelectionSet()` → requested field names → column list / OpenSearch `_source` filter.
- Real gains on wide types (our instrument row: 150+ attributes; fetching 6 vs 150 columns matters — TOAST'd wide columns especially)
- cost: couples resolvers to storage layout and breaks the "service layer returns whole entities" simplicity, so we did it for the two widest types only, behind the service interface. "Selective, measured, behind the boundary" is the defensible posture.

## 2.8 Retries

**Q65: Retry semantics — queries vs mutations.**

**L4**

- Queries are reads → semantically retryable, but travel as POSTs, so no infra auto-retry: client-library logic, on transport errors/5xx/429 only — classify in-body errors too: parse/validation failures are deterministic, while resolver dependency failures may be transient.
- Mutations: unsafe by default
- idempotency exactly as REST POST ([REST §1.6](2.rest101#rest-idempotency)) — key as mutation input or header + server-side key store.

**L5**

- Subtleties:
- partial-result responses are transport successes — blanket retry re-executes what worked
- per-field fallback or targeted subtree refetch instead.
- **Serial mutation execution means a multi-field mutation document that dies midway has committed a prefix** — whole-document retry re-runs committed fields → client convention: one mutation field per document
- multi-step ops become one server-side transactional mutation.
- APQ's GET restores infra-level retry/caching for reads — the fix, not the default.
- This trio is a fully-armored answer to a question most candidates fumble with "queries yes, mutations no."

## 2.9 vs REST, federation, evolution

**Q66: When do you pick which?**

**L4**

- GraphQL: many client types with divergent needs, aggregation across backends, fast-iterating frontends, one flexible contract over N bespoke endpoints.
- REST: few stable-shape consumers, HTTP-cache leverage, files/binary, webhooks, operational simplicity, public surfaces where arbitrary queries are unacceptable.
- They coexist: our GraphQL faced product UIs, REST faced system integrators, one service layer beneath both.

**L5**

- Decide on _organizational_ variables: GraphQL moves integration cost from server team (bespoke endpoints per consumer) into schema design + governance tooling — a win iff consumer-team count is high and you'll actually run the governance.
- State the price plainly: GraphQL replaces commodity HTTP infrastructure — caching (§2.5), retries (§2.8), monitoring semantics (§2.3) — with bespoke application-layer equivalents you now own and staff.
- One backend + one consumer + CRUD = REST, full stop
- proposing GraphQL there is résumé-driven architecture.
- Saying that last sentence, in a GraphQL interview, is the strongest single credibility move available.

**Q67: Supergraph / federation — what, why, how it actually executes.**

**L4**

- Supergraph = one composed schema over multiple **subgraphs**, each owned and deployed by a domain team
- a router (Apollo Router) plans each operation across subgraphs and joins entities.
- Subgraphs declare entities with `@key(fields: "id")`
- other subgraphs contribute fields to them.
- Why: one graph for clients + independent team ownership — vs monolithic schema (single deploy bottleneck, merge contention) and vs schema stitching (the predecessor: manual gateway-side merging, brittle — what federation replaced).

```graphql
# instruments-subgraph
type Instrument @key(fields: "id") {
  id: ID!
  isin: String
  status: InstrumentStatus!
}
# pricing-subgraph
extend type Instrument @key(fields: "id") {
  id: ID! @external
  price: Price
}
```

**L5**

- Name the router's **query plan**: the operation decomposes into per-subgraph fetches sequenced by key dependencies
- downstream subgraphs are called via `_entities(representations: [...])` — so an innocent client query becomes a _sequential multi-hop fan-out_, and **cross-subgraph joins are N+1 at the service tier**: entity resolvers must batch representations exactly as DataLoader batches ids, one layer up.
- The real product is **governance**: composition checks in CI reject a subgraph change that breaks the supergraph _before deploy_ — the org-scale mechanism behind no-versioning.
- When it's wrong: federation earns its router + registry + composition pipeline at roughly 3+ teams owning distinct domains (order of magnitude, not doctrine)
- one team = monolithic schema, say so. (`as of` Apollo Federation v2 docs.; Vanguard asked "what/why supergraph" — this buys/costs/mechanism triple is the expected shape.)

**Q68: Evolution without versions.**

**L4**

- Additive freely
- breaking = add-new-alongside + `@deprecated(reason:)` + migrate consumers + remove at ~zero usage.
- No `/v2` graphs.

**L5**

- The load-bearing mechanism is **field-level usage telemetry per client** (router/gateway metrics): without it deprecation is a prayer
- with it, contraction is a query ("which clients still read `cusipId`?") and removal is a dated, gated ticket.
- This native per-field observability is _why_ the no-versioning stance is credible in GraphQL and aspirational in REST ([REST §1.3](2.rest101#rest-versioning)) — drawing that contrast across protocols is a cross-cutting L5 move interviewers remember.

## 2.10 GraphQL security

**Q69: Where does authz live?**

**L4**

- AuthN at the gateway/interceptor (JWT → principal into `GraphQLContext`).
- AuthZ in the _service layer_ — object- and field-level checks where domain context exists — not sprinkled per-resolver.
- `@PreAuthorize` on `@SchemaMapping` methods works but delegating to centrally-enforced services means a new resolver can't forget the check (correct-by-construction, same doctrine as [REST §1.10](2.rest101#rest-security) BOLA).

**L5**

- GraphQL-specific surfaces:
- **introspection off in prod** for external-facing graphs (schema = free recon map; keep it on internally where DX wins)
- **the resolver-is-a-new-door problem** — REST endpoint audited, GraphQL exposes the same entity via a nested path nobody threat-modeled
- the fix is authz at the service/entity layer so _every_ door hits the same lock
- **batching/alias abuse** as brute-force amplifier (50 aliased login mutations in one request defeats per-request rate limits — count operations/aliases, not HTTP requests, in the limiter)
- CSRF: GraphQL-over-GET (APQ) needs the same CSRF posture as any GET-with-effects — keep mutations POST-only
- field-level redaction beats field-level errors for confidential-but-present data (return null, don't advertise existence via FORBIDDEN — the 404-vs-403 concealment logic, GraphQL edition).

## 2.11 Testing (they ask "what tests did you implement")

**Q71: Testing GraphQL?**

**L4**

- Slice tests with `@GraphQlTest` + `GraphQlTester`: execute documents against the schema with mocked services — validates schema-resolver binding, arg coercion, error mapping.
- Integration: full context + Testcontainers Postgres, real queries through HTTP.
- Contract: schema diff in CI (breaking-change detection) + codegen'd client types failing compilation on drift.

```java
@GraphQlTest(InstrumentController.class)
class InstrumentControllerTest {
  @Autowired GraphQlTester tester;
  @MockBean InstrumentService svc;

  @Test void fetchesIssuerBatched() {
    tester.document("""
        { instruments(first: 2) { edges { node { issuer { name } } } } }""")
      .execute()
      .path("instruments.edges[*].node.issuer.name")
      .entityList(String.class).hasSize(2);
  }
}
```

**Q73: The query-count regression gate (your signature move — say it).**

**L5**

- The N+1 fix that isn't tested regresses on the next innocent field addition.
- Mechanical ratchet: integration test wraps the datasource (e.g., datasource-proxy / p6spy), executes the representative query, asserts `queryCount ≤ 2`.
- Now un-batching a resolver _fails CI_ instead of paging on-call — external verification over self-review, the same principle as your Terraform grep gates and Liquibase drift tests, and you should draw that line explicitly in the interview: it presents a coherent engineering philosophy, not a bag of tricks.
- REST testing moved to [Q72 in REST 101](2.rest101#rest-q72).

## 2.x L5-only

**Q74: The 5,000 RPS consumer on GraphQL + Aurora Serverless (their Scenario 2 — internalize the skeleton, don't script it).**

- **(1) Evaluate**: baseline QPS and per-operation cost profile — persisted queries make the new load _enumerable_ (a finite set of shapes to plan for, versus an open query space; this is §2.7's predictability point becoming a capacity tool)
- Aurora Serverless capacity model is the trap to name — ACU autoscaling reacts in tens of seconds (order of magnitude; `as of` Aurora Serverless v2 docs) which chases a step-function of sustained 5k RPS badly → provisioned instances + read replicas
- connection math: pods × Hikari pool vs Postgres `max_connections` → RDS Proxy/pgbouncer multiplexing.
- **(2) Design for isolation first, speed second** ("cannot impact existing consumers" is a _structural_ requirement): dedicated read replicas or a dedicated deployment cell for the new consumer behind the same schema (bulkhead), per-consumer token-bucket at the gateway so their 5k cannot cannibalize the neighbors, entity-cache layer sized for their (narrow, persisted) query set, allowlist so nothing off-plan executes.
- **(3) Test**: load-test the named operations at 1.5–2× target against production-shaped data volumes, soak for pool/leak behavior, game-day a replica failover mid-load.
- **(4) Rollout**: percentage ramp gated on SLOs (p99, `errors[]`-derived error rate, replica lag), automatic rollback thresholds, per-consumer dashboards.
- Differentiator sentence: _"zero-downtime tolerance means I protect existing consumers structurally — cells and limits — before I optimize anything."_

**Q75: Mutation design doctrine.**

- One mutation field per document (§2.8's committed-prefix hazard)
- verb-specific mutations (`correctInstrument`, `lockField`) over generic `updateInstrument` (audit + authz granularity — the REST custom-action logic, GraphQL edition)
- input types with idempotency key
- union results (§2.3)
- mutations return the mutated entity so client caches update in one round trip.

**Q76: One graph over Aurora + MongoDB + OpenSearch (your actual system as a design question).**

- Entity residency: canonical instruments in Aurora
- documents in Mongo behind the broker
- text search in OpenSearch returning ids hydrated from Aurora (hydration uses canonical-store values subject to its replica/cache freshness; search lag can still affect membership and ordering).
- DataLoaders per backend
- nullable cross-store fields so one degraded store degrades fields, not pages (§2.1 nullability-as-availability, applied)
- the graph is the place cross-store consistency semantics become _visible_ to consumers — which is the argument for GraphQL in this architecture, stated as a conclusion rather than a preference.

---

# Compact GraphQL Interviewer Q&A

## Part 2 — GraphQL

**Q: Now design the GraphQL layer. Where do you start?**

- Same service layer, different contract philosophy.
- The schema is a promise that any legal field combination is cheap — so schema design is batching-topology design.
- Per field: resolves off the parent row, free
- needs another entity, DataLoader, no exceptions in list positions
- cost can't be bounded, I don't expose the field — `documents(first: Int!)` with a required capped limit, never a bare list.
- The cheapest guardrail is the field you refuse to add.

**Q: How do you decide nullability?**

- It's an availability decision, not data modeling.
- Per spec, a null in a non-null position cascades to the nearest nullable ancestor — one failed non-null field inside a list can null the whole page.
- So: fields backed by other services stay nullable and degrade to holes
- fields from my own row are non-null because absence there is a bug I want loud.
- That's blast-radius design in the type system.

**Q: Explain N+1 and your fix.**

- Fifty instruments with `issuer` is one query plus fifty lookups, because execution resolves list items independently — structural, not a bug.
- DataLoader batches per request: resolvers return futures, the engine gathers keys per level, dispatches one `WHERE id IN`, caches per request.
- Three defeaters I watch: blocking on a loader future stalls dispatch — deadlock
- a shared loader cache leaks data across users — scope is per-request, always
- and if the batch function lazy-loads per row, N+1 is reborn one layer down — so an integration test asserts query count ≤ 2, and un-batching fails CI instead of paging on-call.

**Q: Doesn't GraphQL just have worse performance than REST here?**

- GraphQL relocates N+1, it doesn't create it.
- REST's version is the chatty client — visible in access logs, paid in round trips.
- GraphQL moves it server-side behind one request — invisible in logs, paid in DB connections.
- Batching can reduce backend work; compare measured end-to-end cost
- unbatched, you've hidden a fan-out where ops tooling can't see it.

**Q: Error handling — built-in or custom?**

- Both, split by kind.
- Genuine faults go through the built-in `errors` array via an exception resolver — stable code in extensions, trace id, default-deny so internal messages never leak.
- Expected business outcomes go in the schema as union results — `CorrectInstrumentResult = Success | FieldLocked | StaleVersion` — because unions are introspectable, codegen forces clients to handle each case, and adding a variant still requires compatibility checks for exhaustive clients.
- And since execution failures can still return HTTP 200, I emit my own error-rate metric from the errors array — otherwise dashboards say healthy while every response carries failures.

**Q: Pagination?**

- Relay connections — edges, cursors, pageInfo — keyset underneath, same n+1-row trick for hasNext.
- The envelope earns its ceremony: per-edge resume, and clients and caches handle paging generically.
- `totalCount` is the trap — a count can cost more than the page — so it's opt-in and approximate.
- `first` is required in schema and clamped in the resolver, because schema can't express a maximum.

**Q: How do you protect against expensive queries?**

- Ordered by leverage: schema guardrails first — capped `first`, closed filter vocabulary where every filter field is a committed index — static and unbypassable.
- Then depth limits and a complexity budget as a fuse, not a firewall — multipliers are estimates, and naive depth checks miss alias abuse: fifty aliased copies of the same query inside legal depth.
- For a fixed consumer set, a persisted-query allowlist bounds admitted query shapes, alongside variable limits, authorization, and capacity controls.
- Detection alongside: per-operation-name latency in Datadog, so a regression is a named trend.

**Q: Caching?**

- Where cacheable REST reads fit ordinary URL-based caches, GraphQL makes me choose layers.
- Highest ROI: entity cache under the resolvers, version-keyed, shared with REST, shape-agnostic.
- DataLoader gives per-request dedupe free and correct.
- Whole-response caching only via persisted queries over GET — pointless on an authed internal API where authorization fragments the cache.
- Governing rule: field-level authz breaks response caching — cache reusable raw entities with authorization enforced on every response
- partition any response cache by all relevant viewer permissions.

**Q: Can clients retry GraphQL?**

- Queries: semantically read-only; let the client classify transport and in-body errors before retrying
- resolver failures may be transient.
- Mutations need idempotency keys, same as REST POST.
- The subtle one: the spec runs top-level mutation fields _serially_, so a multi-mutation document that dies midway has committed a prefix — whole-document retry re-runs committed work.
- Convention: one mutation per document.

**Q: GraphQL vs REST — when each?**

- Organizational variables, not taste.
- GraphQL moves integration cost from building bespoke endpoints into schema governance — worth it with many consumer teams, and only with the discipline to run governance.
- The price stated plainly: you replace commodity HTTP infrastructure — caching, retries, monitoring semantics — with application-layer equivalents you now own.
- One backend, one consumer, CRUD shapes: REST, full stop.
- We ran both off one service layer — GraphQL for product UIs, REST for integrators.

**Q: What's a supergraph, and why?**

- One composed schema over subgraphs each team owns and deploys
- a router plans queries across them, joining entities declared with `@key`.
- It replaced stitching, which was manual gateway merging.
- Two things worth knowing: the router's query plan makes cross-subgraph joins the new N+1 — entity resolvers must batch representations, DataLoader logic one layer up
- and the real product is governance — composition checks in CI reject a subgraph change that breaks the graph before deploy.
- Worth the machinery at roughly three-plus domain teams
- below that, monolithic schema, and I'd say so.

---

- _Drill order: N+1, nullability, expensive-query defense, idempotency, supergraph — those five carry the most cross-examination weight for Vanguard._

## References

- graphql-java — batching/DataLoader & instrumentation: https://www.graphql-java.com/documentation/batching · execution: https://www.graphql-java.com/documentation/execution
- Spring for GraphQL reference (controllers, BatchLoaderRegistry, exception resolvers, GraphQlTester): https://docs.spring.io/spring-graphql/reference/
- GraphQL spec (Oct 2021 — execution order, serial mutations, error format, null propagation): https://spec.graphql.org/October2021/
- Relay Connection spec: https://relay.dev/graphql/connections.htm
- RFC 9457 Problem Details: https://www.rfc-editor.org/rfc/rfc9457 · Spring error responses: https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-ann-rest-exceptions.html
- AWS Architecture Blog, "Exponential Backoff and Jitter" (2015): https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
- Stripe idempotent requests: https://docs.stripe.com/api/idempotent_requests
- Apollo Federation v2 (entities, query plans, composition): https://www.apollographql.com/docs/federation/ · APQ: https://www.apollographql.com/docs/apollo-server/performance/apq/
- OWASP API Security Top 10 (2023): https://owasp.org/API-Security/
- Envoy retry budgets: https://www.envoyproxy.io/docs/envoy/latest/faq/load_balancing/transient_failures
