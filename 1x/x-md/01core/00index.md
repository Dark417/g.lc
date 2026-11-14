# 01core.01principles.00index Core Principles

> Design principles as a cost model for the next change: 5 Single Responsibility, Open-Closed, Liskov Substitution, Interface Segregation, Dependency Inversion (SOLID), 13 general, 7 Spring principles, each with real Java and Python code.

## Index

- [1. Scope And Enable](#1-scope-and-enable)
- [2. One-Minute Version](#2-one-minute-version)
- [3. Principle Cheat Sheet](#3-principle-cheat-sheet)
- [4. Map](#4-map)
- [5. File Index](#5-file-index)
- [6. Code Map](#6-code-map)
- [7. Local Verification And Gaps](#7-local-verification-and-gaps)
- [Where This Fits](#where-this-fits)
- [References](#references)

## 1. Scope And Enable

One component, three sibling parts.

- Part A: SOLID — **Java + Python**
- Part B: general design principles — **Java + Python**
- Part C: Spring principles — **Java only**
- Code
  - Java `com.lc.x.concept._01core_01principles.{solid,general,spring}`
  - Java wiring `com.lc.x.config._01core_01principles`, Representational State Transfer (REST) `com.lc.x.api._01core_01principles`
  - Python `app/concept/_01core_01principles/{solid,general}.py`, REST `app/api/_01core_01principles.py`
- Enable
  - Java: `x.principles.enabled=true`
  - Python: `X_ENABLED=principles`
- Running domain in code: orders → payments → notifications
- Per principle: idea → mechanism → code (Violation, then Fix) → **catch** (where it breaks)

## 2. One-Minute Version

Principles are heuristics for one goal: lower the cost of the next change.

- **What**
  - Principles are heuristics for one goal: lower the cost of the next change
  - They are not laws; each one trades indirection for flexibility
- **Why**
  - Most cost of a long-lived service is change, not first delivery
  - Change is cheap when it touches one place and breaks nothing far away
- **How** (two forces + two brakes)
  - Raise cohesion: keep things that change together, together
    - Single Responsibility Principle (SRP), Separation of Concerns (SoC), Interface Segregation Principle (ISP), encapsulate what varies
  - Lower coupling: depend on stable contracts, not details
    - Dependency Inversion Principle (DIP), Open-Closed Principle (OCP), interfaces, Law of Demeter (LoD), composition
  - Brakes: Keep It Simple (KISS) and You Aren't Gonna Need It (YAGNI) stop you paying for change that never comes
  - Spring = these ideas built into a framework
    - Dependency Injection (DI) = DIP by container
    - Aspect-Oriented Programming (AOP) = SoC for cross-cutting code
- **Catch**
  - Every principle over-applied creates its own smell
  - SRP → class explosion
  - Don't Repeat Yourself (DRY) → wrong shared abstraction
  - OCP → speculative plugin points
- 🗣 "Principles are a cost model, not a checklist: I apply one when I can name the change it makes cheaper."

## 3. Principle Cheat Sheet

One line, the violation smell, and the line to say aloud, per principle.

**SOLID**

| Principle | One line | Smell when violated | 🗣 line to say aloud |
|---|---|---|---|
| [SRP](01srp.md) | One module answers to one actor | God class edited by finance, ops and marketing | "One reason to change means one stakeholder, not one method." |
| [OCP](02ocp.md) | Add behavior by adding code, not editing tested code | `switch` on type repeated in many places | "I close code against the variation I have seen twice, not the one I imagine." |
| [Liskov Substitution Principle (LSP)](03lsp.md) | A subtype keeps the base type's promises | `instanceof` checks, `UnsupportedOperationException` overrides | "Signatures compile; behavior substitutes — LSP is about the second." |
| [ISP](04isp.md) | Clients depend only on methods they use | Stub methods that throw; huge mocks in tests | "Interfaces belong to the client, sized to what it calls." |
| [DIP](05dip.md) | Policy owns the interface; details implement it | Domain imports the Amazon Web Services (AWS) Software Development Kit (SDK) or Java Database Connectivity (JDBC) | "The arrow of source dependency points at the policy, not the database." |

**Brakes and structure**

| Principle | One line | Smell when violated | 🗣 line to say aloud |
|---|---|---|---|
| [DRY](06dry-kiss-yagni.md#1-dont-repeat-yourself-dry) | One authoritative home per piece of knowledge | Same rule edited in 3 places, one forgotten | "DRY is about knowledge, not identical-looking text." |
| [KISS](06dry-kiss-yagni.md#2-keep-it-simple-kiss) | Simplest design that meets real requirements | Generic engine for a 5-line rule | "Simple means fewer moving parts, not fewer requirements handled." |
| [YAGNI](06dry-kiss-yagni.md#3-you-arent-gonna-need-it-yagni) | Do not build what no requirement needs yet | Plugin system with one plugin | "YAGNI covers features, not things that are expensive to retrofit." |
| [SoC](07soc-cohesion.md#1-separation-of-concerns) | Each part handles one concern | Controller that parses, prices, writes Structured Query Language (SQL) and logs | "Separate concerns so each can change and be tested alone." |
| [Cohesion / coupling](07soc-cohesion.md#2-high-cohesion-low-coupling) | Strong inside, thin between | `Utils` grab-bag; edits ripple across modules | "Cohesion is what changes together; coupling is what breaks together." |

**Contracts and objects**

| Principle | One line | Smell when violated | 🗣 line to say aloud |
|---|---|---|---|
| [Composition](08composition-interface-encapsulate.md#1-composition-over-inheritance) | Assemble behavior from parts, not deep subclassing | `LoggingRetryingEmailNotifier` class tree | "Inheritance is the tightest coupling Java offers; I use it only for real is-a." |
| [Program to interface](08composition-interface-encapsulate.md#2-program-to-an-interface) | Depend on the narrowest contract you need | Params typed `ArrayList`, `HashMap` | "Accept the widest type I can handle, return the most useful specific one." |
| [Encapsulate what varies](08composition-interface-encapsulate.md#3-encapsulate-what-varies) | Wall off the axis of change | Region-specific fee logic inside checkout | "Find the part that changes, put a stable interface in front of it." |
| [LoD](09lod-tell-dont-ask.md#1-law-of-demeter) | Talk only to your direct collaborators | `order.getCustomer().getWallet().getBalance()` | "Dots are fine on data and fluent Application Programming Interfaces (APIs); LoD is about behavior-rich objects." |
| [Tell-don't-ask](09lod-tell-dont-ask.md#2-tell-dont-ask) | Tell an object to act; don't pull its state and decide | `if (a.getBalance() >= x) a.setBalance(...)` | "Put the decision next to the data that guards the invariant." |

**Correctness guards**

| Principle | One line | Smell when violated | 🗣 line to say aloud |
|---|---|---|---|
| [Command-Query Separation (CQS)](10cqs-failfast-pola.md#1-command-query-separation) | A method changes state or returns data, not both | Getter that increments a counter | "Queries must be safe to call twice — except atomic ops where splitting causes races." |
| [Fail fast](10cqs-failfast-pola.md#2-fail-fast) | Reject bad input at the first boundary | Null blows up three services later | "Fail fast per record, degrade gracefully per system." |
| [Principle of Least Astonishment (POLA)](10cqs-failfast-pola.md#3-principle-of-least-astonishment) | Behavior matches what name and context suggest | `get` that writes; mutable default args | "If a reader must open the method to know what it does, the name failed." |

**Spring container**

| Principle | One line | Smell when violated | 🗣 line to say aloud |
|---|---|---|---|
| [Inversion of Control (IoC)](11ioc-di-pojo.md#1-inversion-of-control) | The framework calls your code and owns wiring | `new` of infrastructure inside business code | "Spring owns the object graph; my code owns the business rules." |
| [DI](11ioc-di-pojo.md#2-dependency-injection) | Dependencies come in through the constructor | `@Autowired` private fields | "Constructor injection makes dependencies visible, final and testable with `new`." |
| [Plain Old Java Object (POJO)](11ioc-di-pojo.md#3-non-invasive-pojo-programming) | Business classes don't import the framework | Domain extends framework base classes | "My domain compiles without Spring; Spring only wires it." |
| [AOP](12aop-proxy.md) | Cross-cutting code applied by proxies | Copy-pasted timing/tx code; `@Transactional` silently ignored | "Spring AOP is a proxy: calls through `this` never see it." |

**Spring Boot**

| Principle | One line | Smell when violated | 🗣 line to say aloud |
|---|---|---|---|
| [Auto-config](13auto-config.md) | Sensible beans by default, your bean wins | Mystery beans; startup fails after adding a jar | "Auto-config is `@Conditional` beans that back off when I define my own." |
| [External config](14external-config.md) | Same artifact, config from the environment | `@Value` strings scattered; env checks in code | "Typed, validated `@ConfigurationProperties`; profiles only for environment differences." |
| [Templates](15template.md) | Framework owns the resource lifecycle, you pass a callback | try/finally/close copied around every query | "`JdbcTemplate` is inversion of control for a connection's lifecycle." |

## 4. Map

What every principle is really for.

```text
                 cost of the next change
                           |
          +----------------+----------------+
          |                                 |
   raise COHESION                    lower COUPLING
   SRP, SoC, ISP,                    DIP, OCP, program-to-interface,
   encapsulate what varies           LoD, tell-don't-ask, composition
          |                                 |
          +----------------+----------------+
                           |
   correctness guards: LSP, CQS, fail fast, least astonishment
                           |
   brakes on over-design:  KISS, YAGNI  (and DRY used carefully)
                           |
   Spring = the same ideas in a framework:
     IoC/DI ................... DIP done by a container
     AOP ...................... SoC for cross-cutting concerns
     auto-config .............. convention over configuration
     @ConfigurationProperties . encapsulate what varies per env
     JdbcTemplate ............. template method + callbacks (DRY)
```

Two forces (cohesion up, coupling down) do the work; guards keep it correct and brakes keep it cheap.

## 5. File Index

Every file of the component, grouped by part.

- **Part A — SOLID (Java + Python)**
  - [01srp](01srp.md) — Single Responsibility
  - [02ocp](02ocp.md) — Open/Closed (+ closed-set exception)
  - [03lsp](03lsp.md) — Liskov Substitution (+ contract test)
  - [04isp](04isp.md) — Interface Segregation
  - [05dip](05dip.md) — Dependency Inversion
- **Part B — General principles (Java + Python)**
  - Brakes: [06dry-kiss-yagni](06dry-kiss-yagni.md)
    - [DRY](06dry-kiss-yagni.md#1-dont-repeat-yourself-dry) · [KISS](06dry-kiss-yagni.md#2-keep-it-simple-kiss) · [YAGNI](06dry-kiss-yagni.md#3-you-arent-gonna-need-it-yagni)
  - Structure: [07soc-cohesion](07soc-cohesion.md)
    - [SoC](07soc-cohesion.md#1-separation-of-concerns) · [Cohesion / coupling](07soc-cohesion.md#2-high-cohesion-low-coupling)
  - Contracts: [08composition-interface-encapsulate](08composition-interface-encapsulate.md)
    - [Composition](08composition-interface-encapsulate.md#1-composition-over-inheritance) · [Program to interface](08composition-interface-encapsulate.md#2-program-to-an-interface) · [Encapsulate what varies](08composition-interface-encapsulate.md#3-encapsulate-what-varies)
  - Objects: [09lod-tell-dont-ask](09lod-tell-dont-ask.md)
    - [LoD](09lod-tell-dont-ask.md#1-law-of-demeter) · [Tell-don't-ask](09lod-tell-dont-ask.md#2-tell-dont-ask)
  - Correctness guards: [10cqs-failfast-pola](10cqs-failfast-pola.md)
    - [CQS](10cqs-failfast-pola.md#1-command-query-separation) · [Fail fast](10cqs-failfast-pola.md#2-fail-fast) · [POLA](10cqs-failfast-pola.md#3-principle-of-least-astonishment)
- **Part C — Spring principles (Java only)**
  - [11ioc-di-pojo](11ioc-di-pojo.md) — IoC, DI (+ DI styles table), POJO
  - [12aop-proxy](12aop-proxy.md) — AOP, Java Development Kit (JDK) vs Code Generation Library (CGLIB), self-invocation trap
  - [13auto-config](13auto-config.md) — convention over configuration, Boot startup
  - [14external-config](14external-config.md) — `@ConfigurationProperties` vs `@Value`, profiles
  - [15template](15template.md) — template + callback (`JdbcTemplate`)
- **Across parts**
  - [98tradeoffs](98tradeoffs.md) — when to use / not, design rules, Spring knobs, tensions, failure modes
  - [99interview](99interview.md) — Q1–Q12 (L4 + L5 extra), Q13–Q15 L5-only

## 6. Code Map

Concept file → Java class/method → Python function, using the new layer-first paths.

- Java root: `1x/java/src/main/java/com/lc/x/concept/_01core_01principles/`
  - Spring wiring: `1x/java/src/main/java/com/lc/x/config/_01core_01principles/` (`PrinciplesConfig`, `PrinciplesProperties`)
  - Catalog: `concept/_01core_01principles/PrinciplesCatalog.java`
- Python root: `1x/python/app/concept/_01core_01principles/`
- Every Java principle file has nested `Violation` and `Fix` types and a static `demo()`
- Every Python principle has a `<name>_demo()`

**SOLID** (Java `solid/`, Python `solid.py`)

| File | Java | Python |
|---|---|---|
| [01srp](01srp.md) | `Srp.Violation.OrderService.place` vs `Srp.Fix.OrderService.place`, `Srp.demo` | `SrpViolationOrderService.place` vs `SrpOrderService.place`, `srp_demo` |
| [02ocp](02ocp.md) | `Ocp.Violation.PaymentProcessor.pay` vs `Ocp.Fix.PaymentProcessor.pay` (+ closed set `Fix.FeeKind` / `Fix.fee`), `Ocp.demo` | `OcpViolationProcessor.pay` vs `OcpPaymentProcessor.pay`, `ocp_demo` |
| [03lsp](03lsp.md) | `Lsp.Violation.GiftCardPayment.refund` vs `Lsp.Fix.Refundable`, `Lsp.Fix.contractHolds`, `Lsp.demo` | `LspViolationGiftCard.refund` vs `Refundable`, `contract_holds`, `lsp_demo` |
| [04isp](04isp.md) | `Isp.Violation.OrderStore` vs `Isp.Fix.{OrderReader,OrderWriter,OrderAdmin}`, `Isp.Fix.NightlyReport.run`, `Isp.demo` | `IspViolationOrderStore` vs `OrderReader` (Protocol), `nightly_report`, `isp_demo` |
| [05dip](05dip.md) | `Dip.Violation.OrderService` vs `Dip.Fix.OrderService(OrderRepository, Notifier)`, `Dip.demo` | `DipViolationOrderService` vs `DipOrderService`, `dip_demo` |

**General A** (Java `general/`, Python `general.py`)

| File | Java | Python |
|---|---|---|
| [06 DRY](06dry-kiss-yagni.md#1-dont-repeat-yourself-dry) | `Dry.Violation.{Checkout,Invoice}` vs `Dry.Fix.TaxPolicy`, `Dry.demo` | `TaxPolicy`, `dry_demo` |
| [06 KISS](06dry-kiss-yagni.md#2-keep-it-simple-kiss) | `Kiss.Violation.RuleEngine` vs `Kiss.Fix.shippingFee`, `Kiss.demo` | `KissViolationRuleEngine` vs `shipping_fee`, `kiss_demo` |
| [06 YAGNI](06dry-kiss-yagni.md#3-you-arent-gonna-need-it-yagni) | `Yagni.Violation.PluginLoader` vs `Yagni.Fix.CardGateway`, `Yagni.demo` | `YagniViolationPluginLoader` vs `CardGateway`, `yagni_demo` |
| [07 SoC](07soc-cohesion.md#1-separation-of-concerns) | `SeparationOfConcerns.Violation.handle` vs `Fix.OrderHandler.handle`, `SeparationOfConcerns.demo` | `soc_violation_handle` vs `SocOrderHandler.handle`, `soc_demo` |
| [07 Cohesion](07soc-cohesion.md#2-high-cohesion-low-coupling) | `CohesionCoupling.Violation.OrderUtils` vs `Fix.ShippingQuote.quoteFor`, `CohesionCoupling.demo` | `CohesionViolationUtils` vs `ShippingQuote.quote_for`, `cohesion_demo` |

**General B** (Java `general/`, Python `general.py`)

| File | Java | Python |
|---|---|---|
| [08 Composition](08composition-interface-encapsulate.md#1-composition-over-inheritance) | `CompositionOverInheritance.Violation.LoggingRetryingEmailNotifier` vs `Fix.{Retrying,Logging}`, `CompositionOverInheritance.demo` | `RetryingNotifier`, `LoggingNotifier`, `composition_demo` |
| [08 Interface](08composition-interface-encapsulate.md#2-program-to-an-interface) | `ProgramToInterface.Violation.totalOf(ArrayList)` vs `Fix.totalOf(Collection)`, `ProgramToInterface.demo` | `total_of_violation(list)` vs `total_of(Iterable)`, `interface_demo` |
| [08 Encapsulate](08composition-interface-encapsulate.md#3-encapsulate-what-varies) | `EncapsulateWhatVaries.Violation.Checkout.fee` vs `Fix.FeePolicy`, `EncapsulateWhatVaries.demo` | `FeePolicy`, `FEE_POLICIES`, `encapsulate_demo` |
| [09 LoD](09lod-tell-dont-ask.md#1-law-of-demeter) | `LawOfDemeter.Violation.Checkout.canPay` vs `Fix.Order.canPay`, `LawOfDemeter.demo` | `lod_violation_can_pay` vs `LodOrder.can_pay`, `lod_demo` |
| [09 Tell-don't-ask](09lod-tell-dont-ask.md#2-tell-dont-ask) | `TellDontAsk.Violation.PaymentService.charge` vs `Fix.Wallet.debit`, `TellDontAsk.demo` | `tda_violation_charge` vs `Wallet.debit`, `tda_demo` |

**General C** (Java `general/`, Python `general.py`)

| File | Java | Python |
|---|---|---|
| [10 CQS](10cqs-failfast-pola.md#1-command-query-separation) | `Cqs.Violation.OrderNumbers.nextOrderNumber` vs `Fix.OrderNumbers.{reserveNumber,peekNext}`, `Cqs.demo` | `CqsOrderNumbers`, `cqs_demo` |
| [10 Fail fast](10cqs-failfast-pola.md#2-fail-fast) | `FailFast.Violation.Order` vs `Fix.Order` (compact constructor), `Fix.validateBatch` (per-record), `FailFast.demo` | `FailFastOrder.__post_init__`, `validate_batch`, `failfast_demo` |
| [10 POLA](10cqs-failfast-pola.md#3-principle-of-least-astonishment) | `LeastAstonishment.Violation.getDiscount` vs `Fix.recordDiscountAudit`, `LeastAstonishment.demo` (+ `List.remove` trap) | `pola_violation_add` vs `pola_add`, `pola_demo` |

**Spring container** (Java only; `spring/` unless noted)

| File | Java | Python |
|---|---|---|
| [11 IoC](11ioc-di-pojo.md#1-inversion-of-control) | `config/_01core_01principles/PrinciplesConfig` (`@Bean` wiring), `SpringPrinciplesDemo.ioc` | — (Java only) |
| [11 DI](11ioc-di-pojo.md#2-dependency-injection) | `IocDi.Violation.FieldInjected`, `IocDi.Fix.OrderService`, `IocDi.demo` | — |
| [11 POJO](11ioc-di-pojo.md#3-non-invasive-pojo-programming) | `IocDi.Fix.OrderService` (no Spring imports), `SpringPrinciplesDemo.pojo` | — |
| [12 AOP](12aop-proxy.md) | `Aop.TimingAspect`, `Aop.TxAspect`, `Aop.Violation.Checkout`, `Aop.Fix.{SelfInjectedCheckout,SplitCheckout,LedgerWriter}`, `Aop.proxyKinds`, `SpringPrinciplesDemo.aop` | — |

**Spring Boot and REST**

| File | Java | Python |
|---|---|---|
| [13 Auto-config](13auto-config.md) | `spring/AutoConfig.NotifierAutoConfiguration`, `SpringPrinciplesDemo.autoconfig` | — |
| [14 External config](14external-config.md) | `config/_01core_01principles/PrinciplesProperties` (record + `@Validated`), `spring/ExternalConfig.Violation.ValueSettings`, `SpringPrinciplesDemo.config` | — |
| [15 Templates](15template.md) | `spring/TemplateMethod.Violation.loadOrder`, `TemplateMethod.Fix.MiniTemplate.execute`, `TemplateMethod.findOrderIds(JdbcTemplate)`, `TemplateMethod.demo` | — |
| REST | `api/_01core_01principles/PrinciplesController.show` → GET `/principles/{name}` | `app/api/_01core_01principles.py` `show` → GET `/principles/{name}` |

## 7. Local Verification And Gaps

Checked locally on 2026-11-13 (no cloud needed): app booted with `x.principles.enabled=true`.

- **Verified**
  - Self-invocation printed `inTx=false`; both fixes printed `inTx=true`
  - CGLIB `finalGreet()` printed `final hello null` (Objenesis, constructor skipped)
  - `x.principles.notifier=sms` switched the bean to `SmsNotifier`
  - `x.principles.max-attempts=0` failed startup: "must be greater than or equal to 1"
  - Slice off → `/principles` returned 404
- **Gaps**
  - `@Profile` beans: described only (one runnable profile set would change base app wiring)
  - Real `@Transactional`: mimicked by `@DemoTransactional`
    - The base app has no `DataSource` / transaction manager
  - Real auto-config registration (`AutoConfiguration.imports`): not added
    - Keeps shared `resources/` untouched; the class shows the conditions

## Where This Fits

This component is the design vocabulary every other 1x slice uses.

- Every slice uses the `domain` / `infra` split ([DIP](05dip.md)) and a `@ConditionalOnProperty` slice flag ([auto-config](13auto-config.md))
- After reading, you should be able to name the change each principle makes cheaper, and its failure when over-applied
- Next: Spring container internals → future **06framework.01spring-ioc**

## References

- [spring-projects/spring-boot — autoconfigure module](https://github.com/spring-projects/spring-boot/tree/main/spring-boot-project/spring-boot-autoconfigure) — real `@Conditional` auto-config classes
- [Spring Framework reference — Proxying mechanisms](https://docs.spring.io/spring-framework/reference/core/aop/proxying.html) — JDK vs CGLIB, self-invocation
- [Spring Boot reference — Externalized configuration](https://docs.spring.io/spring-boot/reference/features/external-config.html) — property source order, `@ConfigurationProperties` vs `@Value`
- [Robert C. Martin — The Principles of Object-Oriented Design (OOD)](http://butunclebob.com/ArticleS.UncleBob.PrinciplesOfOod) — SOLID papers index
- [Liskov & Wing, "A Behavioral Notion of Subtyping", Association for Computing Machinery (ACM) Transactions on Programming Languages and Systems (TOPLAS) 1994](https://doi.org/10.1145/197320.197383) — formal LSP
