# 01core.01principles.99interview Interview Questions

> Twelve L4 + L5 questions on Single Responsibility, Open-Closed, Liskov Substitution, Interface Segregation, Dependency Inversion (SOLID), general and Spring principles, plus three L5-only design questions.

## Index

- [1. SOLID](#1-solid)
  - [Q1 SOLID From Your Systems](#q1-solid-from-your-systems) · [Q2 When To Split A Class](#q2-when-to-split-a-class) · [Q3 LSP Violation](#q3-lsp-violation) · [Q4 DIP vs Dependency Injection (DI) vs Inversion of Control (IoC)](#q4-dip-vs-dependency-injection-di-vs-inversion-of-control-ioc)
- [2. General Principles](#2-general-principles)
  - [Q5 Duplication vs Don't Repeat Yourself (DRY)](#q5-duplication-vs-dont-repeat-yourself-dry) · [Q6 You Aren't Gonna Need It (YAGNI) vs OCP](#q6-you-arent-gonna-need-it-yagni-vs-ocp) · [Q7 Composition Or Inheritance](#q7-composition-or-inheritance)
- [3. Spring](#3-spring)
  - [Q8 Constructor Injection](#q8-constructor-injection) · [Q9 Transactional Ignored](#q9-transactional-ignored) · [Q10 JDK Proxy vs Code Generation Library (CGLIB)](#q10-jdk-proxy-vs-code-generation-library-cglib) · [Q11 Boot Startup](#q11-boot-startup) · [Q12 Properties vs Value](#q12-properties-vs-value)
- [4. L5-Only](#4-l5-only)
  - [Q13 Refactor A 5k-Line Class](#q13-refactor-a-5k-line-class) · [Q14 Agent Tool Registry](#q14-agent-tool-registry) · [Q15 Principles In Distributed Systems](#q15-principles-in-distributed-systems)

Back to [00index](00index.md).

## 1. SOLID

Concept files: [01srp](01srp.md) · [02ocp](02ocp.md) · [03lsp](03lsp.md) · [04isp](04isp.md) · [05dip](05dip.md).

### Q1 SOLID From Your Systems

**Q:** Explain SOLID with an example from your own systems.

**L4 answer**

- Single Responsibility Principle (SRP): a data-platform ingestion service split into parse, validate, persist, publish
  - Each owned by a different concern
- Open-Closed Principle (OCP): new file formats added as new `RecordParser` implementations in a registry
- Liskov Substitution Principle (LSP): every parser honors the same contract
  - Same errors on bad input, no extra exceptions
- Interface Segregation Principle (ISP): the reporting job depends on `OrderReader` only, not on writer/admin methods
- Dependency Inversion Principle (DIP): the service depends on a `LakeWriter` port; Simple Storage Service (S3)/Delta adapters implement it

**L5 extra**

- I apply them at boundaries, not everywhere
  - DIP at I/O
  - OCP only where variants exist
- I name the cost: each interface is a file and an indirection
  - I accept it only where a change or a test needs it

### Q2 When To Split A Class

**Q:** How do you decide when to split a class (SRP)?

**L4 answer**

- When two different actors request changes to it independently
- Signals
  - Unrelated field groups
  - Merge conflicts
  - Tests needing unrelated setup

**L5 extra**

- Evidence over taste: `git log` co-change shows which methods change together
- Over-splitting is a real failure
  - If a feature now spans 10 tiny classes, I merge by actor

### Q3 LSP Violation

**Q:** Give an LSP violation and how you would catch it.

**L4 answer**

- `GiftCardPayment.refund()` throws `UnsupportedOperationException`; callers add `instanceof`
- Fix: `Refundable` capability interface implemented only by refundable payments

**L5 extra**

- Compilers check signatures, not behavior
  - I catch LSP with a shared contract test suite run against each implementation
- The Java Development Kit (JDK) accepts LSP breaks in `List.of` ("optional operations")
  - A deliberate trade of fewer interfaces for runtime failures

### Q4 DIP vs Dependency Injection (DI) vs Inversion of Control (IoC)

**Q:** DIP vs DI vs IoC?

**L4 answer**

- IoC: framework controls the flow and calls my code
- DI: dependencies are supplied from outside (constructor)
- DIP: high-level policy owns the abstraction; details implement it

**L5 extra**

- You can do DI without DIP (inject concrete classes)
- You can do DIP without a container (manual wiring in `main`)
- The DIP test: does the domain package import the Software Development Kit (SDK)?
  - If yes, the arrow points the wrong way

## 2. General Principles

Concept files: [06dry-kiss-yagni](06dry-kiss-yagni.md) · [08composition-interface-encapsulate](08composition-interface-encapsulate.md).

### Q5 Duplication vs Don't Repeat Yourself (DRY)

**Q:** When is duplication better than DRY?

**L4 answer**

- When two pieces look alike but represent different knowledge with different reasons to change
- Merging them couples their callers

**L5 extra**

- Example: shared "common utils" across Databricks jobs and online services
  - One upgrade forces both to redeploy
- Share contracts (schemas), not implementation
- Rule of three before extracting

### Q6 You Aren't Gonna Need It (YAGNI) vs OCP

**Q:** YAGNI vs OCP — an agent tool registry has three tools today. Do you add a plugin interface?

**L4 answer**

- Three real tools with the same shape is already the "rule of three"
- A `Tool` interface + registry keyed by name is justified
- Dynamic class loading is not

**L5 extra**

- Close against the variation seen (new tools), not imagined ones (new protocols)
- Retrofit-expensive parts are not YAGNI
  - Tool input schemas
  - Idempotency of side-effecting tools
  - Per-tool timeouts and audit

### Q7 Composition Or Inheritance

**Q:** Composition or inheritance for notifiers with retry and logging?

**L4 answer**

- Composition: `Retrying(Logging(Email))` decorators over a `Notifier` interface
- Inheritance needs a class per combination

**L5 extra**

- Inheritance couples to the base's self-calls (fragile base class); decorators don't
- Decorator order is a contract
  - Metrics outside retry counts requests
  - Inside retry counts attempts

## 3. Spring

Concept files: [11ioc-di-pojo](11ioc-di-pojo.md) · [12aop-proxy](12aop-proxy.md) · [13auto-config](13auto-config.md) · [14external-config](14external-config.md).

### Q8 Constructor Injection

**Q:** Why does Spring recommend constructor injection?

**L4 answer**

- Required deps explicit, fields `final`, object complete after construction
- Unit tests use `new` without a container

**L5 extra**

- Cycles fail at startup (Boot ≥ 2.6 forbids them by default); field injection hid them
- Long constructors expose SRP violations that field injection hides

### Q9 Transactional Ignored

**Q:** Why is `@Transactional` sometimes ignored?

**L4 answer**

- Spring applies it through a proxy; `this.method()` skips the proxy
- Also ignored on `private` and `final` methods

**L5 extra**

- Fixes ranked
  1. Separate bean
  2. `ObjectProvider<Self>`
  3. `AopContext.currentProxy()`
  4. AspectJ weaving
- Also check rollback rules (checked exceptions commit by default)
- Also check aspect order with retries

### Q10 JDK Proxy vs Code Generation Library (CGLIB)

**Q:** JDK dynamic proxy vs CGLIB?

**L4 answer**

- JDK: implements interfaces, advises interface methods only
- CGLIB: subclasses the class; cannot advise `final`/`private` methods; Boot's default

**L5 extra**

- CGLIB instantiates via Objenesis without running the constructor
  - A `final` method on the proxy sees `null` fields
- Records and final classes cannot be class-proxied at all

### Q11 Boot Startup

**Q:** What does Spring Boot actually do at startup? How does auto-config decide?

**L4 answer**

- Builds the `Environment`, scans user config
- Then imports auto-config candidates from `AutoConfiguration.imports`
- Each candidate is kept only if its `@Conditional...` checks pass

**L5 extra**

- User config is processed first, so `@ConditionalOnMissingBean` lets my bean win
  - The same annotation in normal config is order-dependent
- Debug with `--debug` or `/actuator/conditions`
- Exclude unwanted auto-config explicitly

### Q12 Properties vs Value

**Q:** `@ConfigurationProperties` vs `@Value`? How do you use profiles?

**L4 answer**

- `@ConfigurationProperties`: typed, grouped, validated at startup
- `@Value`: single value, no validation
- Profiles switch environment wiring (`application-prod.yml`)

**L5 extra**

- Validation at startup is fail fast for config
  - A typo in `@Value` fails on first use or never
- No `if (prod)` in code
- Feature flags are not profiles
- Secrets never in yml

## 4. L5-Only

Depth, scale, ambiguity and design ownership.

### Q13 Refactor A 5k-Line Class

**Q:** You inherit a 5k-line service class in a JPMorgan Chase (JPMC)-style data platform. Plan the refactor without stopping delivery.

- Characterization tests around current behavior first
- Find seams with co-change history and actors (pricing, persistence, notification)
- Strangle: extract one actor's code behind a port per release; keep the facade stable
- Stop when the remaining class is cohesive — not when it is "small"

### Q14 Agent Tool Registry

**Q:** Design an extensible agent tool registry that is not over-engineered.

- `Tool` interface: name, input schema, `invoke(input)`
  - Registry map
  - Startup validation of duplicate names (fail fast)
- LSP: every tool honors the same timeout, error, and idempotency contract
  - Contract tests per tool
- ISP: the planner sees `ToolCatalog` (describe), the executor sees `ToolInvoker`
- Not built yet: hot reloading, remote plugin loading — until a real need appears

### Q15 Principles In Distributed Systems

**Q:** Where do these principles hurt in distributed systems?

- Law of Demeter (LoD) and fine-grained interfaces → chatty remote calls
  - Remote Application Programming Interfaces (APIs) should be coarse-grained
- DRY across services → shared libraries force lockstep deploys
- Tell-don't-ask across a network → a command needs idempotency keys and retries
- Fail fast at startup on a remote dependency → fleet-wide crash loops
