# 01core.01principles.11ioc-di-pojo Inversion of Control (IoC), Dependency Injection (DI) And Plain Old Java Object (POJO)

> Spring owns the object graph; classes only declare what they need and never import the framework.

## Index

- [1. Inversion Of Control](#1-inversion-of-control)
  - [1.1 Idea](#11-idea) · [1.2 Code](#12-code) · [1.3 Catch](#13-catch)
- [2. Dependency Injection](#2-dependency-injection)
  - [2.1 Idea](#21-idea) · [2.2 Code](#22-code) · [2.3 DI Styles Compared](#23-di-styles-compared) · [2.4 Catch](#24-catch)
- [3. Non-Invasive POJO Programming](#3-non-invasive-pojo-programming)
  - [3.1 Idea](#31-idea) · [3.2 Code](#32-code) · [3.3 Catch](#33-catch)

Part C, Spring principles (Java only). Back to [00index](00index.md).

- Spring principles are SOLID and SoC built into a framework
- Container internals (bean lifecycle, scopes, `BeanPostProcessor` deep dive) → future doc **06framework.01spring-ioc**

## 1. Inversion Of Control

The framework calls your code; the container creates and wires objects.

### 1.1 Idea

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

### 1.2 Code

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

### 1.3 Catch

Business code must never call `ApplicationContext.getBean`.

→ Business code calls `applicationContext.getBean(...)`.  
⇒ Service-locator: hidden dependencies, container coupling, untestable without Spring.  
→ Only the composition root (config classes) knows about the container.

→ Wiring errors appear only at startup.  
⇒ That is fail fast (good), but stack traces can be long and indirect.  
→ Keep wiring explicit and small per slice; read the "Parameter 0 of constructor..." line first.

- 🗣 "Spring owns the object graph; my code owns the business rules."

## 2. Dependency Injection

An object receives its dependencies instead of creating them.

### 2.1 Idea

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
- Dependency Injection (DI) is how the object arrives; [Dependency Inversion Principle (DIP)](05dip.md) is who owns the interface

### 2.2 Code

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

### 2.3 DI Styles Compared

Constructor injection is the default; the other two exist for narrow cases.

| Option | What it is | Strength | Weakness | Choose when |
|---|---|---|---|---|
| Constructor | Deps as constructor args | Immutable, explicit, testable with `new`, cycles fail fast | Long arg lists visible | Required dependencies (default) |
| Setter | Deps via setters | Optional / reconfigurable | Object can be half-built | Optional dependency with a sane default |
| Field | `@Autowired` on fields | Shortest | Hidden deps, no `final`, needs container in tests | Never in production code; maybe test classes |

Pick: constructor injection, unless the dependency is genuinely optional (setter or `ObjectProvider`).

### 2.4 Catch

A 9-arg constructor is an SRP alarm; don't silence it.

→ Switching to field injection because the constructor has 9 parameters.  
⇒ The SRP smell is hidden, not fixed.  
→ Split the class.

→ A cycle "fixed" with `@Lazy` or `allow-circular-references=true`.  
⇒ Startup passes; the design flaw and a runtime proxy remain.  
→ Extract the shared logic into a third bean.

- 🗣 "Constructor injection makes dependencies visible, final and testable with `new`."

## 3. Non-Invasive POJO Programming

Business classes don't extend or import the framework.

### 3.1 Idea

- Business classes don't extend or import the framework
- Origin: Spring reacted to Enterprise JavaBeans (EJB) 2, which forced container interfaces on every bean (Rod Johnson, 2002)
- Example (`IocDi.Fix.OrderService`)
  - No Spring imports
  - Built by a `@Bean` method
  - Unit-tested with `new`
- **Mechanism**
  - Domain logic survives framework upgrades
  - Runs in tests, batch jobs, Lambdas

### 3.2 Code

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

### 3.3 Catch

Annotations are still coupling, and proxies need non-final classes.

→ Annotations are still coupling (`@Transactional`, `@Entity` on domain types).  
⇒ Pure POJO domain costs mapping layers.  
→ Pragmatic line: framework annotations on adapters and services, none in core rules.

→ Proxies need non-final classes.  
⇒ Records and final classes cannot be Code Generation Library (CGLIB)-proxied; advice on them fails at startup.  
→ Keep advised beans as ordinary classes; records for data.

- 🗣 "My domain compiles without Spring; Spring only wires it."
