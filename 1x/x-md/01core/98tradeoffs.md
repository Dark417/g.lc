# 01core.01principles.98tradeoffs Trade-offs Knobs And Failure Modes

> When to apply the principles firmly, the Spring knobs, the tensions between principles, and how each one fails.

## Index

- [1. When To Use Or Not](#1-when-to-use-or-not)
- [2. Design Rules](#2-design-rules)
- [3. Spring Knobs](#3-spring-knobs)
- [4. Spring Best Practices](#4-spring-best-practices)
- [5. Tensions Between Principles](#5-tensions-between-principles)
- [6. Other Comparisons](#6-other-comparisons)
- [7. Failure Modes](#7-failure-modes)
  - [7.1 Design Failures](#71-design-failures)
  - [7.2 Coupling And Runtime Failures](#72-coupling-and-runtime-failures)
  - [7.3 Spring Failures](#73-spring-failures)

Back to [00index](00index.md).

## 1. When To Use Or Not

Apply principles where change is frequent and boundaries are expensive; relax them where code is throwaway.

- **Apply firmly when**
  - Code is long-lived and changes often (core services, shared platform Application Programming Interfaces (APIs))
  - Several teams or many contributors touch it
  - The boundary is public or persisted (APIs, schemas, events) — retrofitting is expensive
  - Testing needs to run without real infrastructure (Dependency Inversion Principle (DIP), Dependency Injection (DI), ports)
- **Relax when**
  - Spikes, notebooks, one-off migrations, throwaway scripts
  - Stable code nobody has touched in a year
  - Only one variant exists and none is on the roadmap (You Aren't Gonna Need It (YAGNI) beats Open-Closed Principle (OCP))
  - Performance-critical inner loops where indirection costs
    - Order of magnitude: virtual calls are cheap on the Java Virtual Machine (JVM) after Just-In-Time compilation (JIT)
    - Allocations and remote calls are not
- **Never relax**
  - Liskov Substitution Principle (LSP) for types you expose to others
  - Fail fast on configuration and on input at trust boundaries
  - Idempotency and observability on networked commands (not covered by YAGNI)

## 2. Design Rules

Each rule names the failure it prevents.

- Rule of three before abstracting → prevents a wrong shared abstraction
- Invert dependencies at I/O and vendor boundaries first → prevents an untestable domain
- One contract test suite per interface with >1 implementation → prevents silent LSP breaks
- Let the consumer own small interfaces (Java role interfaces, Python `Protocol`) → prevents fat interfaces
- Closed set of variants → enum / sealed type + exhaustive `switch`; open set → interface + registry → prevents OCP misuse
- Validate in constructors (compact record constructor, `__post_init__`) → prevents invalid objects travelling far
- Use co-change history to choose seams → prevents cosmetic, not real, cohesion

## 3. Spring Knobs

Defaults and when to change them, split into proxy knobs and container/config knobs.

**Proxy and Aspect-Oriented Programming (AOP) knobs** ([12aop-proxy](12aop-proxy.md))

| Knob | Default | What it trades | Change when |
|---|---|---|---|
| `spring.aop.proxy-target-class` | `true` (Boot) | Code Generation Library (CGLIB) everywhere vs Java Development Kit (JDK) proxies on interfaces | Almost never; set `false` only to enforce interface-only proxies |
| `@EnableAspectJAutoProxy(exposeProxy=true)` | `false` | Enables `AopContext.currentProxy()` | Legacy code that can't split beans |
| `@Order` on aspects | undefined order | Deterministic advice nesting | Any method with 2+ aspects |

**Container and config knobs** ([11ioc-di-pojo](11ioc-di-pojo.md), [13auto-config](13auto-config.md), [14external-config](14external-config.md))

| Knob | Default | What it trades | Change when |
|---|---|---|---|
| `spring.main.allow-circular-references` | `false` (Boot ≥ 2.6) | Startup passes with cycles | Temporary migration only |
| `spring.main.lazy-initialization` | `false` | Faster startup vs late wiring errors | Dev loops; avoid in prod (defeats fail fast) |
| `debug=true` / `--debug` | off | Prints auto-config condition report | Diagnosing "why is/isn't this bean here" |
| `@Validated` on `@ConfigurationProperties` | off | Startup fails on bad config | Always for required config |

## 4. Spring Best Practices

Five habits that avoid most Spring traps.

- Constructor injection, `final` fields, no `@Autowired` on single constructors
- Advised methods public, non-final, called from another bean
- `@ConfigurationProperties` records + `@Validated` for any group of ≥2 related keys
- `@ConditionalOnMissingBean` only in auto-config classes
- Guard optional features with `@ConditionalOnProperty` (every 1x slice does)

## 5. Tensions Between Principles

Principles pull against each other; each row names how to resolve the pull.

**Abstraction tensions**

| Tension | Pulls toward | Pulls against | Resolve by |
|---|---|---|---|
| Don't Repeat Yourself (DRY) vs decoupling | One shared helper / library | Independent deploys and owners | Same reason to change → merge; different owners → duplicate |
| YAGNI vs OCP | Concrete code now | Extension point for future variants | Extract on the 2nd real variant; refactor is cheap inside one repo |
| Keep It Simple (KISS) vs Single Responsibility, Open-Closed, Liskov Substitution, Interface Segregation, Dependency Inversion (SOLID) | Fewer classes | Ports, adapters, role interfaces | SOLID at boundaries, KISS inside a module |
| Composition vs inheritance | Decorators, delegation | Reuse of a designed base class | Inherit only from bases designed for extension |

**Object and runtime tensions**

| Tension | Pulls toward | Pulls against | Resolve by |
|---|---|---|---|
| Law of Demeter (LoD) vs fluent APIs | Wrap every chain | Builders, streams, records | LoD only for behavior-rich objects |
| Tell-don't-ask vs Separation of Concerns (SoC) | Logic inside the entity | Entity free of I/O | Entity guards invariants; service does I/O |
| Command-Query Separation (CQS) vs atomicity | Split read and write | One atomic op | Keep atomic ops combined |
| Fail fast vs availability | Crash on bad state | Keep serving | Reject per request/record; never crash the fleet on optional deps |

Pick: concrete, simple code inside a module; SOLID-style abstractions at I/O, vendor and team boundaries, unless the variation has already appeared twice.

## 6. Other Comparisons

The option tables live next to their concept.

- DI styles (constructor / setter / field) → [11ioc-di-pojo §2.3](11ioc-di-pojo.md#23-di-styles-compared)
- Proxy mechanisms (JDK / CGLIB / AspectJ) → [12aop-proxy §5](12aop-proxy.md#5-proxy-mechanisms-compared)
- Config binding (`@ConfigurationProperties` / `@Value` / `Environment`) → [14external-config §3](14external-config.md#3-config-binding-compared)

## 7. Failure Modes

Every principle over- or under-applied has a recognizable trigger and fix.

### 7.1 Design Failures

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Class explosion | Single Responsibility Principle (SRP) read as "one method per class" | Feature needs 10 files to read; tiny classes with one caller | Merge by actor / co-change; SRP is per stakeholder |
| Wrong abstraction | DRY on look-alike code | Shared helper with boolean flags or `if (caller == X)` | Inline back into callers, re-extract later |
| Speculative generality | OCP / YAGNI ignored | Interfaces with one impl, unused config hooks | Delete; keep concrete until a 2nd variant |
| LSP break | Subtype throws or tightens checks | `instanceof` in callers; contract tests fail on one impl | Split capability interfaces; compose |
| Fat interface | One interface for all clients | Mocks stub many unused methods | Role interfaces per client |
| Leaky port | Port mirrors vendor API | Domain code mentions Software Development Kit (SDK) types/expressions | Reshape port around domain operations |

### 7.2 Coupling And Runtime Failures

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Hidden coupling | "Decoupled" via events/maps | Runtime break after a field rename | Schemas, contract tests, consumer-driven contracts |
| Fragile base class | Subclass relies on base self-calls | Base change breaks subclasses | Composition / decorators; `final` by default |
| Check-then-act race | CQS split of atomic op | Duplicate numbers/identifiers (IDs) under load | Atomic op (`incrementAndGet`, conditional write) |
| Batch killed by one row | Fail fast at system level | Job fails on a single bad record | Validate per record, quarantine / Dead-Letter Queue (DLQ) |

### 7.3 Spring Failures

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| `@Transactional` ignored | Self-invocation, `private`/`final` method | No tx in logs; partial writes on error | Separate bean, `ObjectProvider` self, AspectJ |
| No rollback | Checked exception from `@Transactional` | Data committed after an error | `rollbackFor` or unchecked exceptions |
| `null` fields in bean | `final` method called on CGLIB proxy | NullPointerException (NPE) only when proxied | Remove `final`; don't call through proxy internals |
| Mystery beans / startup failure | Auto-config triggered by a new jar | `--debug` condition report | Exclude auto-config or define your own bean |
| Bad config reaches runtime | `@Value` without validation | Failure on first use, not at startup | `@ConfigurationProperties` + `@Validated` |
| Prod-only path untested | Profile-specific code branches | Bugs only in prod | Profiles for wiring only; test each profile's context |
