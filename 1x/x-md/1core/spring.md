# Spring

- **In plain words:** Spring creates and connects your objects for you and wraps them with extra behavior (transactions, logging), so your classes can focus on business rules.
- The container (IoC, DI, POJO), proxies and AOP, and template callbacks; Java only
- Siblings: [Spring Boot](spring-boot.md) · [SOLID](solid.md) · [Design principles](design-principles.md) · [Design patterns](1design-patterns.md)

## Index

- [1. One-Minute Version](#1-one-minute-version)
- [2. Cheat Sheet](#2-cheat-sheet)
- [3. Inversion Of Control](#3-inversion-of-control)
  - [3.1 Idea](#31-idea)
  - [3.2 Code](#32-code)
  - [3.3 Catch](#33-catch)
- [4. Dependency Injection](#4-dependency-injection)
  - [4.1 Idea](#41-idea)
  - [4.2 Code](#42-code)
  - [4.3 DI Styles Compared](#43-di-styles-compared)
  - [4.4 Catch](#44-catch)
- [5. Non-Invasive POJO Programming](#5-non-invasive-pojo-programming)
  - [5.1 Idea](#51-idea)
  - [5.2 Code](#52-code)
  - [5.3 Catch](#53-catch)
- [6. Aspect-Oriented Programming (AOP) And Proxies](#6-aspect-oriented-programming-aop-and-proxies)
  - [6.1 Idea](#61-idea)
  - [6.2 Java Development Kit (JDK) Dynamic Proxy Vs Code Generation Library (CGLIB)](#62-java-development-kit-jdk-dynamic-proxy-vs-code-generation-library-cglib)
  - [6.3 Self-Invocation Trap](#63-self-invocation-trap)
  - [6.4 Code](#64-code)
  - [6.5 Proxy Mechanisms Compared](#65-proxy-mechanisms-compared)
  - [6.6 Catch](#66-catch)
- [7. Template-Style Boilerplate Removal](#7-template-style-boilerplate-removal)
  - [7.1 Idea](#71-idea)
  - [7.2 Mechanism](#72-mechanism)
  - [7.3 Code](#73-code)
  - [7.4 Catch](#74-catch)
- [8. Knobs](#8-knobs)
- [9. Best Practices](#9-best-practices)
- [10. Failure Modes](#10-failure-modes)
- [11. Interview Questions](#11-interview-questions)
- [12. Code Map And Local Checks](#12-code-map-and-local-checks)

---

## 1. One-Minute Version

- **What:** a container that builds the object graph, plus proxies that add cross-cutting behavior
- **Why:** business code stops doing `new` on infrastructure and stops repeating transaction, logging and resource code
- **How**
  - IoC/DI: you declare dependencies in constructors; the container wires them
  - AOP: a proxy around a bean runs advice before and after the call
  - Templates: the framework owns a resource's lifecycle; you pass a callback
- **Catch:** proxies only see calls that go through the proxy; `this.method()` skips transactions silently
- 🗣 "Spring owns the object graph; my code owns the business rules."

## 2. Cheat Sheet

| Principle | One line | Smell when violated | 🗣 line to say aloud |
|---|---|---|---|
| [Inversion of Control (IoC)](#3-inversion-of-control) | The framework calls your code and owns wiring | `new` of infrastructure inside business code | "Spring owns the object graph; my code owns the business rules." |
| [Dependency Injection (DI)](#4-dependency-injection) | Dependencies come in through the constructor | `@Autowired` private fields | "Constructor injection makes dependencies visible, final and testable with `new`." |
| [Plain Old Java Object (POJO)](#5-non-invasive-pojo-programming) | Business classes don't import the framework | Domain extends framework base classes | "My domain compiles without Spring; Spring only wires it." |
| [Aspect-Oriented Programming (AOP)](#6-aspect-oriented-programming-aop-and-proxies) | Cross-cutting code applied by proxies | Copy-pasted timing/tx code; `@Transactional` silently ignored | "Spring AOP is a proxy: calls through `this` never see it." |
| [Template Callbacks](#7-template-style-boilerplate-removal) | Framework owns the resource lifecycle, you pass a callback | try/finally/close copied around every query | "`JdbcTemplate` is inversion of control for a connection's lifecycle." |

## 3. Inversion Of Control

- **In plain words:** instead of your code creating and connecting everything, the framework does it and calls your code when needed: "don't call us, we'll call you."

The framework calls your code; the container creates and wires objects.

### 3.1 Idea

- "Hollywood principle": don't call us, we call you
- The container creates and wires objects
- **Mechanism**

  → Read bean definitions (component scan, `@Bean` methods, auto-config)  
  → Build the dependency graph and instantiate singletons in dependency order  
  → Inject dependencies, run post-processors (which may wrap beans in proxies)  
  → Context ready; your code runs only when called

- Example (`PrinciplesConfig`)
  - `@Bean` methods wire the Plain Old Java Object (POJO) `OrderService` with a repository and notifier
  - It is the composition root: the only place that knows how the slice's objects are wired

### 3.2 Code

Every bean exists only when `x.principles.enabled=true`, so the base app is unaffected.

```java
// config/_01core_01principles/PrinciplesConfig.java
@Configuration(proxyBeanMethods = false)
@ConditionalOnProperty(name = "x.principles.enabled", havingValue = "true")
@EnableConfigurationProperties(PrinciplesProperties.class)
public class PrinciplesConfig {

    @Bean
    public IocDi.Fix.OrderRepository principlesOrderRepository() {
        return new IocDi.Fix.InMemoryOrderRepository();
    }

    // Notifier comes from AutoConfig.NotifierAutoConfiguration (log or sms, by condition).
    @Bean
    public IocDi.Fix.OrderService principlesOrderService(IocDi.Fix.OrderRepository repo, IocDi.Fix.Notifier notifier) {
        return new IocDi.Fix.OrderService(repo, notifier);   // POJO built with its constructor
    }
    // ... aspect and checkout beans for 12aop-proxy, demo facade for the controller
}
```

```java
// concept/_01core_01principles/spring/SpringPrinciplesDemo.java
// Shows the container-built graph: OrderService arrived wired, and wrapped in a proxy by a post-processor.
// Catch: the bean you hold is a proxy subclass, not your class (see getClass()).
public String ioc() {
    return "OrderService bean class=" + orderService.getClass().getSimpleName()
            + " aopProxy=" + AopUtils.isAopProxy(orderService)
            + "\nplace -> " + orderService.place("o-ioc");
}
```

### 3.3 Catch

Business code must never call `ApplicationContext.getBean`.

→ Business code calls `applicationContext.getBean(...)`.  
⇒ Service-locator: hidden dependencies, container coupling, untestable without Spring.  
→ Only the composition root (config classes) knows about the container.

→ Wiring errors appear only at startup.  
⇒ That is fail fast (good), but stack traces can be long and indirect.  
→ Keep wiring explicit and small per slice; read the "Parameter 0 of constructor..." line first.

- 🗣 "Spring owns the object graph; my code owns the business rules."

## 4. Dependency Injection

- **In plain words:** a class lists what it needs in its constructor, and Spring hands those objects in, so the class never builds its own dependencies.

An object receives its dependencies instead of creating them.

### 4.1 Idea

- **Styles** (`IocDi`)
  - Constructor: required deps, `final` fields, testable with `new`
  - Setter: optional deps that may be reconfigured
  - Field (`@Autowired private`): concise, but hidden and container-only
- **Why constructor**
  - Object is complete and immutable after construction
  - Unit tests need no container: `new OrderService(fakeRepo, fakeNotifier)`
  - A circular dependency fails at startup
    - Spring Boot ≥ 2.6 forbids cycles by default (2.6 release notes, Nov 2021)
  - Single constructor needs no `@Autowired` (Spring ≥ 4.3)
  - Long parameter lists stay visible — a free Single Responsibility Principle (SRP) alarm
- Dependency Injection (DI) is how the object arrives; [Dependency Inversion Principle (DIP)](solid.md#7-dependency-inversion-principle-dip) is who owns the interface

### 4.2 Code

Field injection fails outside the container; the constructor-injected POJO works with `new`.

```java
// concept/_01core_01principles/spring/IocDi.java
/** Violation: hidden dependency, not final, null when built with new (unit tests NPE far from the cause). */
public static class FieldInjected {                // IocDi.Violation.FieldInjected
    @Autowired
    private Fix.OrderRepository repo;

    public String place(String orderId) {
        repo.save(orderId);                        // NPE when built with new
        return "placed " + orderId;
    }
}

/**
 * Fix: non-invasive POJO, no Spring imports, final fields, testable with new.
 * Not final so Spring can CGLIB-proxy it for the TimingAspect (bean-name pointcut).
 */
public static class OrderService {                 // IocDi.Fix.OrderService
    private final OrderRepository repo;
    private final Notifier notifier;

    public OrderService(OrderRepository repo, Notifier notifier) {
        this.repo = repo;
        this.notifier = notifier;
    }

    public String place(String orderId) {
        repo.save(orderId);
        return notifier.notify(orderId) + " stored=" + repo.count();
    }
}

/** Setter injection: only for optional deps with a sane default; object may be half-configured. */
public static class SetterInjected {               // IocDi.Fix.SetterInjected
    private Notifier notifier = id -> "default-notifier " + id;

    @Autowired(required = false)
    public void setNotifier(Notifier notifier) { this.notifier = notifier; }
}
```

- Demo: `IocDi.demo()` (via `SpringPrinciplesDemo.di`)
  - `new FieldInjected().place` → `NullPointerException (repo was never injected)`
  - `new OrderService(fakeRepo, fakeNotifier).place` works

### 4.3 DI Styles Compared

Constructor injection is the default; the other two exist for narrow cases.

| Option | What it is | Strength | Weakness | Choose when |
|---|---|---|---|---|
| Constructor | Deps as constructor args | Immutable, explicit, testable with `new`, cycles fail fast | Long arg lists visible | Required dependencies (default) |
| Setter | Deps via setters | Optional / reconfigurable | Object can be half-built | Optional dependency with a sane default |
| Field | `@Autowired` on fields | Shortest | Hidden deps, no `final`, needs container in tests | Never in production code; maybe test classes |

Pick: constructor injection, unless the dependency is genuinely optional (setter or `ObjectProvider`).

### 4.4 Catch

A 9-arg constructor is an SRP alarm; don't silence it.

→ Switching to field injection because the constructor has 9 parameters.  
⇒ The SRP smell is hidden, not fixed.  
→ Split the class.

→ A cycle "fixed" with `@Lazy` or `allow-circular-references=true`.  
⇒ Startup passes; the design flaw and a runtime proxy remain.  
→ Extract the shared logic into a third bean.

- 🗣 "Constructor injection makes dependencies visible, final and testable with `new`."

## 5. Non-Invasive POJO Programming

- **In plain words:** business classes are plain Java with no framework imports, so they can be tested and reused without Spring.

Business classes don't extend or import the framework.

### 5.1 Idea

- Business classes don't extend or import the framework
- Origin: Spring reacted to Enterprise JavaBeans (EJB) 2, which forced container interfaces on every bean (Rod Johnson, 2002)
- Example (`IocDi.Fix.OrderService`)
  - No Spring imports
  - Built by a `@Bean` method
  - Unit-tested with `new`
- **Mechanism**
  - Domain logic survives framework upgrades
  - Runs in tests, batch jobs, Lambdas

### 5.2 Code

The same POJO class used with and without Spring.

```java
// concept/_01core_01principles/spring/SpringPrinciplesDemo.java
// Use to argue domain code survives framework changes.
// Catch: proxies need non-final classes; records can't be advised.
public String pojo() {
    IocDi.Fix.OrderService plain = new IocDi.Fix.OrderService(new IocDi.Fix.InMemoryOrderRepository(), id -> "plain " + id);
    return "without Spring: " + plain.place("o-plain")
            + "\nwith Spring:    " + orderService.place("o-spring");   // container-built, proxied bean
}
```

### 5.3 Catch

Annotations are still coupling, and proxies need non-final classes.

→ Annotations are still coupling (`@Transactional`, `@Entity` on domain types).  
⇒ Pure POJO domain costs mapping layers.  
→ Pragmatic line: framework annotations on adapters and services, none in core rules.

→ Proxies need non-final classes.  
⇒ Records and final classes cannot be Code Generation Library (CGLIB)-proxied; advice on them fails at startup.  
→ Keep advised beans as ordinary classes; records for data.

- 🗣 "My domain compiles without Spring; Spring only wires it."

## 6. Aspect-Oriented Programming (AOP) And Proxies

- **In plain words:** Spring wraps a bean in a stand-in object (a proxy) that runs extra code, like starting a transaction, before and after your method, so you don't copy that code everywhere.
- **One line:** Cross-cutting code applied by proxies around Spring beans, and why calls through `this` never see it.

### 6.1 Idea

Transactions, security, metrics, retries and caching are applied around methods without editing them.

- Aspect-Oriented Programming (AOP) is Separation of Concerns (SoC) for cross-cutting concerns ([Catch](design-principles.md#73-catch))
- Spring AOP is **proxy-based**
  - Only method calls on Spring beans are advised
  - Only calls made *through the proxy*
- Example (`Aop`)
  - `TimingAspect` times the Plain Old Java Object (POJO) `OrderService` by bean name (no annotation on the POJO)
  - `TxAspect` + `@DemoTransactional` mimic `@Transactional`
  - So the trap is observable without a database

### 6.2 Java Development Kit (JDK) Dynamic Proxy Vs Code Generation Library (CGLIB)

Spring builds one of two proxy kinds; each limits what can be advised.

- **JDK proxy**
  - Implements the bean's interfaces
  - Only interface methods advised
  - Casting to the class fails
- **CGLIB**
  - Runtime subclass
  - Advises public/protected/package methods
  - Never `final` or `private` methods
- Spring Boot defaults to CGLIB (`spring.aop.proxy-target-class=true`, since Boot 2.0)
- CGLIB proxies are created without calling the constructor (Objenesis)
  - ⇒ A `final` method running on the proxy sees `null` fields

### 6.3 Self-Invocation Trap

An internal call skips the proxy, so its advice silently does nothing.

→ Caller → proxy.`checkout()` → target.`checkout()`  
→ Target calls `this.writeLedger()` directly — the proxy is not in the path  
⇒ `@Transactional`, `@Async`, `@Cacheable`, `@Retryable` on `writeLedger` are silently ignored

- **Fixes** (best first)
  1. Move the advised method to a separate bean (`Aop.Fix.SplitCheckout` + `Aop.Fix.LedgerWriter`)
  2. Inject yourself lazily via `ObjectProvider<Self>` and call through it (`Aop.Fix.SelfInjectedCheckout`)
  3. `AopContext.currentProxy()` with `exposeProxy=true` (couples code to Spring)
  4. AspectJ compile/load-time weaving (advises self-calls; heavier build)
- Calling `writeLedger` directly on the proxy works; only `this.writeLedger()` is skipped

### 6.4 Code

The aspects, the trap, both fixes, and the two proxy kinds without a container.

#### 6.4.1 Aspects

```java
// concept/_01core_01principles/spring/Aop.java
/** Stand-in for @Transactional: same proxy mechanics, no DataSource needed. */
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
public @interface DemoTransactional { }
// TxContext: thread-bound "transaction" via ThreadLocal, like TransactionSynchronizationManager.

/** Outer aspect (lower @Order = runs first): timing wraps the transaction, so it measures the whole call. */
@Aspect
@Order(0)
public static class TimingAspect {
    @Around("bean(principlesOrderService)")       // by bean name: the POJO carries no annotation
    public Object time(ProceedingJoinPoint pjp) throws Throwable {
        long start = System.nanoTime();
        try {
            return pjp.proceed();
        } finally {
            calls.incrementAndGet();
            lastMicros.put(pjp.getSignature().toShortString(), (System.nanoTime() - start) / 1_000);
        }
    }
}

/** Joins an existing "transaction" (like REQUIRED) or opens one around the annotated method. */
@Aspect
@Order(1)
public static class TxAspect {
    @Around("@annotation(tx)")
    public Object inTransaction(ProceedingJoinPoint pjp, DemoTransactional tx) throws Throwable {
        if (TxContext.active()) {
            return pjp.proceed();
        }
        TxContext.begin(pjp.getSignature().toShortString());
        try {
            return pjp.proceed();
        } finally {
            TxContext.end();
        }
    }
}
```

#### 6.4.2 Violation And Fixes

```java
// concept/_01core_01principles/spring/Aop.java
/** Violation: checkout() calls this.writeLedger(); the call never reaches the proxy, so no transaction. */
public static class Checkout {                     // Aop.Violation.Checkout
    public String checkout(String orderId) {
        return "checkout -> " + writeLedger(orderId);          // this.writeLedger: proxy skipped
    }
    @DemoTransactional
    public String writeLedger(String orderId) {
        return "ledger(" + orderId + ") inTx=" + TxContext.active();
    }
}

/** Fix 1: inject yourself lazily; getObject() returns the proxy, so advice applies. */
public static class SelfInjectedCheckout {         // Aop.Fix.SelfInjectedCheckout
    private final ObjectProvider<SelfInjectedCheckout> self;
    public String checkout(String orderId) {
        return "checkout -> " + self.getObject().writeLedger(orderId);
    }
    @DemoTransactional
    public String writeLedger(String orderId) { /* same as above */ }
}

/** Fix 2 (preferred): the advised method lives in another bean. */
public static class LedgerWriter {                 // Aop.Fix.LedgerWriter
    @DemoTransactional
    public String write(String orderId) {
        return "ledger(" + orderId + ") inTx=" + TxContext.active();
    }
}
public static class SplitCheckout {                // Aop.Fix.SplitCheckout
    private final LedgerWriter ledger;
    public String checkout(String orderId) { return "checkout -> " + ledger.write(orderId); }
}
```

- Demo: `SpringPrinciplesDemo.aop()`
  - Self-invocation prints `inTx=false`
  - Direct call via proxy and both fixes print `inTx=true`
  - Plus the `TimingAspect` report and `Aop.proxyKinds()`

#### 6.4.3 Proxy Kinds

```java
// concept/_01core_01principles/spring/Aop.java
public static class PlainGreeter implements Greeter {
    private final String name;
    public String greet() { return "hello " + name; }
    /** final: CGLIB cannot override it, so it runs on the proxy instance whose fields were never set. */
    public final String finalGreet() { return "final hello " + name; }
}

// Catch: CGLIB proxies are built via Objenesis without running the constructor.
public static String proxyKinds() {
    MethodInterceptor advice = inv -> "[advised] " + inv.proceed();

    ProxyFactory jdkFactory = new ProxyFactory(new PlainGreeter("ada"));
    jdkFactory.addInterface(Greeter.class);
    jdkFactory.setProxyTargetClass(false);         // JDK proxy: interface only
    jdkFactory.addAdvice(advice);
    Object jdk = jdkFactory.getProxy();            // jdk instanceof PlainGreeter == false

    ProxyFactory cglibFactory = new ProxyFactory(new PlainGreeter("ada"));
    cglibFactory.setProxyTargetClass(true);        // CGLIB: runtime subclass
    cglibFactory.addAdvice(advice);
    PlainGreeter cglib = (PlainGreeter) cglibFactory.getProxy();
    // cglib.greet() is advised; cglib.finalGreet() prints "final hello null"
    ...
}
```

### 6.5 Proxy Mechanisms Compared

Three ways to apply advice, from lightest to heaviest.

| Option | What it is | Strength | Weakness | Choose when |
|---|---|---|---|---|
| JDK dynamic proxy | `java.lang.reflect.Proxy` implementing interfaces | No bytecode generation; target class untouched | Interface methods only; cast to class fails | Interface-only design, `proxy-target-class=false` |
| CGLIB (Spring) | Runtime subclass of the bean class | Works without interfaces; Boot default | No `final`/`private` methods; final classes and records impossible | Default in Spring Boot |
| AspectJ weaving | Compile/load-time bytecode weaving | Advises self-calls, fields, constructors | Build/agent complexity | Self-invocation or non-bean objects must be advised |

Pick: Spring's CGLIB proxies, unless self-calls or non-Spring objects must be advised (AspectJ).

### 6.6 Catch

Rollback rules and aspect order are the two other silent traps.

→ `@Transactional` on a method that throws a checked exception.  
⇒ Default rollback is only for `RuntimeException` and `Error` (Spring Framework docs).  
→ Set `rollbackFor`, or throw unchecked domain exceptions.

→ Several aspects on one method without explicit order.  
⇒ Retry inside a transaction retries on a doomed transaction; metrics may count attempts, not requests.  
→ `@Order` aspects explicitly (retry outside tx).

- Knobs (`proxy-target-class`, `exposeProxy`, `@Order`): see [Knobs](#8-knobs)
- 🗣 "Spring AOP is a proxy: calls through `this` never see it."

## 7. Template-Style Boilerplate Removal

- **In plain words:** the framework does the fixed, boring steps (open the connection, handle errors, close it) and you supply only the part that differs, like the SQL and how to read a row.
- **One line:** The framework owns a resource's fixed lifecycle steps; you pass only the variable part as a callback.

### 7.1 Idea

Inversion of control for a connection's lifecycle.

- The framework owns the fixed steps of a resource's lifecycle
- You pass only the variable part as a callback
- Examples
  - `JdbcTemplate`
  - `TransactionTemplate`
  - `RestClient`
  - `KafkaTemplate`
- Don't Repeat Yourself (DRY) for resource handling ([Don't Repeat Yourself (DRY)](design-principles.md#4-dont-repeat-yourself-dry))
- Example (`TemplateMethod`)
  - Violation: every call copies open/retry/close/translate
  - Fix: `MiniTemplate.execute(callback)` owns retry, close and error translation once

### 7.2 Mechanism

`JdbcTemplate.query(sql, rowMapper)` runs the same skeleton around your callback.

→ Get connection (bound to the current transaction if any)  
→ Prepare statement, execute, iterate rows → your `RowMapper`  
→ Translate `SQLException` into the `DataAccessException` hierarchy  
→ Close everything in `finally`

- Template method + callbacks (lambdas), not Gang of Four (GoF) inheritance

### 7.3 Code

A fake resource (`FakeDataSource`, `FakeConnection`, `TransientDbError`) lets the demo run without a `DataSource`.

#### 7.3.1 Violation

```java
// concept/_01core_01principles/spring/TemplateMethod.java
/** Skeleton copy #1; copy #2 (loadCustomer) would repeat it, and one copy will forget close(). */
public static String loadOrder(FakeDataSource ds, String id) {   // TemplateMethod.Violation.loadOrder
    for (int attempt = 1; ; attempt++) {
        FakeConnection c = ds.getConnection();
        try {
            return c.query("SELECT * FROM orders WHERE id = ?", id);
        } catch (TransientDbError e) {             // like SQLState 40001 serialization failure
            if (attempt == 3) {
                throw new DataAccessFailure("loadOrder failed", e);
            }
        } finally {
            c.close();
        }
    }
}
```

#### 7.3.2 Fix

```java
// concept/_01core_01principles/spring/TemplateMethod.java
@FunctionalInterface
public interface ConnectionCallback<T> { T doInConnection(FakeConnection c); }

/** Owns the fixed steps once; reuses the shared full-jitter Retry for transient errors only. */
public static final class MiniTemplate {           // TemplateMethod.Fix.MiniTemplate
    private final FakeDataSource ds;
    private final Retry retry;

    // The template method: open -> callback -> close always -> translate driver errors.
    // Catch: retry is only safe because the callback here is a read; writes need idempotency.
    public <T> T execute(ConnectionCallback<T> callback) {
        try {
            return retry.call(() -> {
                try (FakeConnection c = ds.getConnection()) {
                    return callback.doInConnection(c);
                }
            }, e -> e instanceof TransientDbError);
        } catch (TransientDbError e) {
            throw new DataAccessFailure("query failed after retries", e);   // callers never see driver types
        }
    }

    public String loadOrder(String id) {
        return execute(c -> c.query("SELECT * FROM orders WHERE id = ?", id));
    }
    public String loadCustomer(String id) {
        return execute(c -> c.query("SELECT * FROM customers WHERE id = ?", id));
    }
}
```

- Demo: `TemplateMethod.demo(maxAttempts)` via `SpringPrinciplesDemo.template()`
  - A transient failure is retried by the template
  - Every connection is closed (`open=0`)
  - Attempts come from typed config ([Externalized Configuration](spring-boot.md#4-externalized-configuration))

#### 7.3.3 The Real JdbcTemplate

```java
// concept/_01core_01principles/spring/TemplateMethod.java
// JdbcTemplate does the same steps around a RowMapper callback.
// Use when a DataSource exists (the Aurora slice); not called here, so no DataSource bean is needed.
public static List<String> findOrderIds(JdbcTemplate jdbc, String customerId) {
    return jdbc.query("SELECT id FROM orders WHERE customer_id = ?", (rs, rowNum) -> rs.getString("id"), customerId);
}
```

### 7.4 Catch

One-line template calls hide cost and vendor detail.

→ The template hides cost.  
⇒ `jdbc.query` inside a loop is N+1 queries that look like one line each.  
→ Batch (`batchUpdate`, `IN` lists) and watch query counts.

→ Exception translation hides vendor detail.  
⇒ Retry logic can't see the Structured Query Language (SQL) state it needs.  
→ Inspect `getCause()` / `SQLException.getSQLState()` where retry depends on it.

- 🗣 "`JdbcTemplate` is inversion of control for a connection's lifecycle."

## 8. Knobs

**Proxy and AOP knobs**

| Knob | Default | What it trades | Change when |
|---|---|---|---|
| `spring.aop.proxy-target-class` | `true` (Boot) | Code Generation Library (CGLIB) everywhere vs Java Development Kit (JDK) proxies on interfaces | Almost never; set `false` only to enforce interface-only proxies |
| `@EnableAspectJAutoProxy(exposeProxy=true)` | `false` | Enables `AopContext.currentProxy()` | Legacy code that can't split beans |
| `@Order` on aspects | undefined order | Deterministic advice nesting | Any method with 2+ aspects |

**Container knobs**

| Knob | Default | What it trades | Change when |
|---|---|---|---|
| `spring.main.allow-circular-references` | `false` (Boot ≥ 2.6) | Startup passes with cycles | Temporary migration only |
| `spring.main.lazy-initialization` | `false` | Faster startup vs late wiring errors | Dev loops; avoid in prod (defeats fail fast) |

## 9. Best Practices

Five habits that avoid most Spring traps.

- Constructor injection, `final` fields, no `@Autowired` on single constructors
- Advised methods public, non-final, called from another bean
- `@ConfigurationProperties` records + `@Validated` for any group of ≥2 related keys
- `@ConditionalOnMissingBean` only in auto-config classes
- Guard optional features with `@ConditionalOnProperty` (every 1x slice does)

## 10. Failure Modes

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| `@Transactional` ignored | Self-invocation, `private`/`final` method | No tx in logs; partial writes on error | Separate bean, `ObjectProvider` self, AspectJ |
| No rollback | Checked exception from `@Transactional` | Data committed after an error | `rollbackFor` or unchecked exceptions |
| `null` fields in bean | `final` method called on CGLIB proxy | NullPointerException (NPE) only when proxied | Remove `final`; don't call through proxy internals |

## 11. Interview Questions

### Q1 Constructor Injection

**Q:** Why does Spring recommend constructor injection?

**L4 answer**

- Required deps explicit, fields `final`, object complete after construction
- Unit tests use `new` without a container

**L5 extra**

- Cycles fail at startup (Boot ≥ 2.6 forbids them by default); field injection hid them
- Long constructors expose SRP violations that field injection hides

### Q2 Transactional Ignored

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

### Q3 JDK Proxy vs Code Generation Library (CGLIB)

**Q:** JDK dynamic proxy vs CGLIB?

**L4 answer**

- JDK: implements interfaces, advises interface methods only
- CGLIB: subclasses the class; cannot advise `final`/`private` methods; Boot's default

**L5 extra**

- CGLIB instantiates via Objenesis without running the constructor
  - A `final` method on the proxy sees `null` fields
- Records and final classes cannot be class-proxied at all

## 12. Code Map And Local Checks

- Java `1x/java/src/main/java/com/lc/x/concept/_01core_01principles/spring/`; wiring `config/_01core_01principles/`; enable `x.principles.enabled=true`

| File | Java | Python |
|---|---|---|
| [Inversion Of Control](#3-inversion-of-control) | `config/_01core_01principles/PrinciplesConfig` (`@Bean` wiring), `SpringPrinciplesDemo.ioc` | — (Java only) |
| [Dependency Injection](#4-dependency-injection) | `IocDi.Violation.FieldInjected`, `IocDi.Fix.OrderService`, `IocDi.demo` | — |
| [Non-Invasive POJO Programming](#5-non-invasive-pojo-programming) | `IocDi.Fix.OrderService` (no Spring imports), `SpringPrinciplesDemo.pojo` | — |
| [Aspect-Oriented Programming (AOP) And Proxies](#6-aspect-oriented-programming-aop-and-proxies) | `Aop.TimingAspect`, `Aop.TxAspect`, `Aop.Violation.Checkout`, `Aop.Fix.{SelfInjectedCheckout,SplitCheckout,LedgerWriter}`, `Aop.proxyKinds`, `SpringPrinciplesDemo.aop` | — |
| [Template-Style Boilerplate Removal](#7-template-style-boilerplate-removal) | `spring/TemplateMethod.Violation.loadOrder`, `TemplateMethod.Fix.MiniTemplate.execute`, `TemplateMethod.findOrderIds(JdbcTemplate)`, `TemplateMethod.demo` | — |

- Verified locally (2026-11-13)
  - Self-invocation printed `inTx=false`; both fixes printed `inTx=true`
  - CGLIB `finalGreet()` printed `final hello null` (Objenesis, constructor skipped)
- Gap: real `@Transactional` is mimicked by `@DemoTransactional`; the base app has no `DataSource` or transaction manager

## References

- [Spring Framework reference — Proxying mechanisms](https://docs.spring.io/spring-framework/reference/core/aop/proxying.html) — JDK vs CGLIB, self-invocation
