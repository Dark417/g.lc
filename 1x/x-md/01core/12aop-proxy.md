# 01core.01principles.12aop-proxy Aspect-Oriented Programming (AOP) And Proxies

> Cross-cutting code applied by proxies around Spring beans, and why calls through `this` never see it.

## Index

- [1. Idea](#1-idea)
- [2. Java Development Kit (JDK) Dynamic Proxy Vs Code Generation Library (CGLIB)](#2-java-development-kit-jdk-dynamic-proxy-vs-code-generation-library-cglib)
- [3. Self-Invocation Trap](#3-self-invocation-trap)
- [4. Code](#4-code)
  - [4.1 Aspects](#41-aspects)
  - [4.2 Violation And Fixes](#42-violation-and-fixes)
  - [4.3 Proxy Kinds](#43-proxy-kinds)
- [5. Proxy Mechanisms Compared](#5-proxy-mechanisms-compared)
- [6. Catch](#6-catch)
- [References](#references)

Part C, Spring principles (Java only). Back to [00index](00index.md).

## 1. Idea

Transactions, security, metrics, retries and caching are applied around methods without editing them.

- Aspect-Oriented Programming (AOP) is Separation of Concerns (SoC) for cross-cutting concerns ([07soc-cohesion](07soc-cohesion.md#13-catch))
- Spring AOP is **proxy-based**
  - Only method calls on Spring beans are advised
  - Only calls made *through the proxy*
- Example (`Aop`)
  - `TimingAspect` times the Plain Old Java Object (POJO) `OrderService` by bean name (no annotation on the POJO)
  - `TxAspect` + `@DemoTransactional` mimic `@Transactional`
  - So the trap is observable without a database

## 2. Java Development Kit (JDK) Dynamic Proxy Vs Code Generation Library (CGLIB)

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

## 3. Self-Invocation Trap

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

## 4. Code

The aspects, the trap, both fixes, and the two proxy kinds without a container.

### 4.1 Aspects

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

### 4.2 Violation And Fixes

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

### 4.3 Proxy Kinds

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

## 5. Proxy Mechanisms Compared

Three ways to apply advice, from lightest to heaviest.

| Option | What it is | Strength | Weakness | Choose when |
|---|---|---|---|---|
| JDK dynamic proxy | `java.lang.reflect.Proxy` implementing interfaces | No bytecode generation; target class untouched | Interface methods only; cast to class fails | Interface-only design, `proxy-target-class=false` |
| CGLIB (Spring) | Runtime subclass of the bean class | Works without interfaces; Boot default | No `final`/`private` methods; final classes and records impossible | Default in Spring Boot |
| AspectJ weaving | Compile/load-time bytecode weaving | Advises self-calls, fields, constructors | Build/agent complexity | Self-invocation or non-bean objects must be advised |

Pick: Spring's CGLIB proxies, unless self-calls or non-Spring objects must be advised (AspectJ).

## 6. Catch

Rollback rules and aspect order are the two other silent traps.

→ `@Transactional` on a method that throws a checked exception.  
⇒ Default rollback is only for `RuntimeException` and `Error` (Spring Framework docs).  
→ Set `rollbackFor`, or throw unchecked domain exceptions.

→ Several aspects on one method without explicit order.  
⇒ Retry inside a transaction retries on a doomed transaction; metrics may count attempts, not requests.  
→ `@Order` aspects explicitly (retry outside tx).

- Knobs (`proxy-target-class`, `exposeProxy`, `@Order`): see [98tradeoffs](98tradeoffs.md#3-spring-knobs)
- 🗣 "Spring AOP is a proxy: calls through `this` never see it."

## References

- [Spring Framework reference — Proxying mechanisms](https://docs.spring.io/spring-framework/reference/core/aop/proxying.html) — JDK vs CGLIB, self-invocation
