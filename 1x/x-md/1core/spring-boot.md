# Spring Boot

- **In plain words:** Spring Boot is Spring with sensible defaults. It looks at your dependencies and config and sets up the usual beans, so a service starts with almost no setup code.
- Auto-configuration, what Boot does at startup, externalized configuration, starters, embedded server and Actuator; Java only
- Siblings: [Spring](spring.md) · [SOLID](solid.md) · [Design principles](design-principles.md) · [Design patterns](1design-patterns.md)

## Index

- [1. One-Minute Version](#1-one-minute-version)
- [2. Cheat Sheet](#2-cheat-sheet)
- [3. Convention Over Configuration And Auto-Configuration](#3-convention-over-configuration-and-auto-configuration)
  - [3.1 Idea](#31-idea)
  - [3.2 What Spring Boot Does At Startup](#32-what-spring-boot-does-at-startup)
  - [3.3 Code](#33-code)
  - [3.4 Debug](#34-debug)
  - [3.5 Catch](#35-catch)
- [4. Externalized Configuration](#4-externalized-configuration)
  - [4.1 Idea](#41-idea)
  - [4.2 Code](#42-code)
  - [4.3 Config Binding Compared](#43-config-binding-compared)
  - [4.4 Catch](#44-catch)
- [5. Starters, Embedded Server And Actuator](#5-starters-embedded-server-and-actuator)
  - [5.1 Starters](#51-starters)
  - [5.2 Embedded server and fat jar](#52-embedded-server-and-fat-jar)
  - [5.3 Actuator](#53-actuator)
- [6. Knobs](#6-knobs)
- [7. Failure Modes](#7-failure-modes)
- [8. Interview Questions](#8-interview-questions)
- [9. Code Map And Local Checks](#9-code-map-and-local-checks)

---

## 1. One-Minute Version

- **What:** Spring plus starters, auto-configuration, an embedded server and externalized config
- **Why:** classic Spring needed a lot of XML / Java config before the first request
- **How**
  - Starters pull a tested set of dependencies
  - Auto-config registers `@Conditional` beans that back off when you define your own
  - Config comes from files, env vars and args, bound to typed `@ConfigurationProperties`
- **Catch:** adding a jar can switch on a feature you didn't ask for; `--debug` shows why
- 🗣 "Auto-config is `@Conditional` beans that back off when I define my own."

## 2. Cheat Sheet

| Principle | One line | Smell when violated | 🗣 line to say aloud |
|---|---|---|---|
| [Auto-Configuration](#3-convention-over-configuration-and-auto-configuration) | Sensible beans by default, your bean wins | Mystery beans; startup fails after adding a jar | "Auto-config is `@Conditional` beans that back off when I define my own." |
| [Externalized Configuration](#4-externalized-configuration) | Same artifact, config from the environment | `@Value` strings scattered; env checks in code | "Typed, validated `@ConfigurationProperties`; profiles only for environment differences." |

## 3. Convention Over Configuration And Auto-Configuration

- **In plain words:** Boot looks at what is on the classpath (say, a Postgres driver) and creates the usual beans automatically, but steps aside the moment you define your own.
- **One line:** Sensible beans by default from the classpath and config, backing off when you define your own.

### 3.1 Idea

Defaults come from what is on the classpath and in config; your own bean wins.

- Auto-config = `@Conditional` beans that back off when you define your own
- Example (`AutoConfig.NotifierAutoConfiguration`)
  - `@ConditionalOnProperty(x.principles.notifier=sms)` → Short Message Service (SMS) notifier
  - Else `@ConditionalOnMissingBean(Notifier.class)` → default log notifier
- Use for library/starter code that must offer defaults yet yield to the application

### 3.2 What Spring Boot Does At Startup

Boot builds the environment, parses your config first, then filters auto-config candidates by condition.

→ `SpringApplication.run` builds the `Environment` (command line, env vars, `application-{profile}.yml`, `application.yml`)  
→ `@SpringBootApplication` = `@Configuration` + `@ComponentScan` + `@EnableAutoConfiguration`  
→ User configuration classes are parsed first  
→ `AutoConfigurationImportSelector` loads candidates from `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` (Boot ≥ 2.7; `spring.factories` before)  
→ Each candidate is filtered by `@ConditionalOnClass`, `@ConditionalOnMissingBean`, `@ConditionalOnProperty`, `@ConditionalOnWebApplication`  
→ Survivors register beans; singletons are created; the embedded web server starts  
→ `ApplicationReadyEvent`

### 3.3 Code

Conditions decide which `Notifier` exists, guarded by the slice flag.

```java
// concept/_01core_01principles/spring/AutoConfig.java
// Real auto-config is listed in META-INF/spring/...AutoConfiguration.imports and processed after user config.
// Here both beans sit in one class, so declaration order (sms first) keeps it deterministic.
@Configuration(proxyBeanMethods = false)
@ConditionalOnProperty(name = "x.principles.enabled", havingValue = "true")
public static class NotifierAutoConfiguration {

    @Bean
    @ConditionalOnProperty(name = "x.principles.notifier", havingValue = "sms")
    public IocDi.Fix.Notifier principlesSmsNotifier() {
        return new SmsNotifier();
    }

    @Bean
    @ConditionalOnMissingBean(IocDi.Fix.Notifier.class)   // backs off if any Notifier already exists
    public IocDi.Fix.Notifier principlesLogNotifier() {
        return new LogNotifier();
    }
}
```

```java
// concept/_01core_01principles/spring/SpringPrinciplesDemo.java
// Use to explain back-off: define your own Notifier bean and the default disappears.
public String autoconfig() {
    return "x.principles.notifier=" + env.getProperty("x.principles.notifier", "(unset)")
            + " -> Notifier bean=" + notifier.getClass().getSimpleName();
}
```

- Verified locally: `x.principles.notifier=sms` switched the bean to `SmsNotifier`

### 3.4 Debug

Two ways to see why a bean is or isn't there.

- `--debug` (or `debug=true`) prints the condition evaluation report
- Actuator `/actuator/conditions` shows it at runtime

### 3.5 Catch

`@ConditionalOnMissingBean` in ordinary `@Configuration` depends on parse order.

→ A jar on the classpath activates a feature.  
⇒ Adding `spring-jdbc` makes Boot want a DataSource Uniform Resource Locator (URL) at startup.  
→ Exclude it explicitly — `XApplication` excludes `DataSourceAutoConfiguration` for exactly this reason.

→ `@ConditionalOnMissingBean` in an ordinary `@Configuration`.  
⇒ Result depends on parse order; it is only reliable in real auto-configuration classes (processed after user config).  
→ Use it in auto-config registered in `AutoConfiguration.imports`; in app code, wire explicitly.

- Gap in this repo: real `AutoConfiguration.imports` registration not added, to keep shared `resources/` untouched; the class shows the conditions
- 🗣 "Auto-config is `@Conditional` beans that back off when I define my own."

## 4. Externalized Configuration

- **In plain words:** build one jar and change its behavior per environment through config files and environment variables, not through code changes.
- **One line:** One artifact everywhere; behavior differs per environment via typed, validated config, not code.

### 4.1 Idea

The same build runs in every environment; only the configuration changes.

- One artifact; behavior differs per environment via config, not code
- Property sources in precedence order (high → low)
  1. command line
  2. env vars
  3. profile files
  4. `application.yml`
- **Relaxed binding**: env `X_PRINCIPLES_ENABLED` → `x.principles.enabled`
- **`@ConfigurationProperties` vs `@Value`** (`PrinciplesProperties`, `ExternalConfig`)
  - `@ConfigurationProperties`: typed, grouped, immutable record, Java Specification Request (JSR) 380 validated at startup
  - `@Value("${key:default}")`: one value, supports Spring Expression Language (SpEL), no validation, key strings scattered
- **Profiles**
  - `@Profile("prod")` beans
  - `application-prod.yml`
  - Activated by `spring.profiles.active`
- Encapsulate what varies per environment ([Encapsulate What Varies](design-principles.md#11-encapsulate-what-varies)); fail fast on bad config ([Fail Fast](design-principles.md#15-fail-fast))

### 4.2 Code

`@Value` strings vs a validated `@ConfigurationProperties` record.

#### 4.2.1 Violation

```java
// concept/_01core_01principles/spring/ExternalConfig.java
/**
 * Note the deliberate typo "max-attemps": no error, the default 3 is used forever.
 * Also no range check: X_PRINCIPLES_MAX_ATTEMPTS=0 would be accepted.
 */
@Component
@ConditionalOnProperty(name = "x.principles.enabled", havingValue = "true")
public static class ValueSettings {                // ExternalConfig.Violation.ValueSettings
    private final int maxAttempts;
    private final String taxRate;                  // stringly typed

    public ValueSettings(@Value("${x.principles.max-attemps:3}") int maxAttempts,
                         @Value("${x.principles.tax-rate:0.08}") String taxRate) {
        this.maxAttempts = maxAttempts;
        this.taxRate = taxRate;
    }
}
```

#### 4.2.2 Fix

```java
// config/_01core_01principles/PrinciplesProperties.java
// Bound from x.principles.* (yml, env X_PRINCIPLES_MAX_ATTEMPTS, command line), relaxed binding.
// Registered by @EnableConfigurationProperties in PrinciplesConfig, so only when the slice is on.
// Catch: unknown yml keys are ignored by default; a misspelled key silently keeps the default.
@Validated
@ConfigurationProperties(prefix = "x.principles")
public record PrinciplesProperties(
        boolean enabled,
        @DefaultValue("log") @NotNull @Pattern(regexp = "log|sms") String notifier,
        @DefaultValue("3") @Min(1) @Max(10) int maxAttempts,          // 0 fails startup
        @DefaultValue("2s") @NotNull Duration timeout,
        @DefaultValue("0.08") @NotNull @DecimalMin("0") @DecimalMax("0.5") BigDecimal taxRate) {
}
```

- Demo: `SpringPrinciplesDemo.config()` → `ExternalConfig.describe` prints both styles plus active profiles
- `TemplateMethod.demo(props.maxAttempts())` reads the typed value ([Template-Style Boilerplate Removal](spring.md#7-template-style-boilerplate-removal))
- Verified locally: `x.principles.max-attempts=0` failed startup with "must be greater than or equal to 1"

### 4.3 Config Binding Compared

Three ways to read config in Spring.

| Option | What it is | Strength | Weakness | Choose when |
|---|---|---|---|---|
| `@ConfigurationProperties` record | Typed group bound by prefix | Validation, relaxed binding, Integrated Development Environment (IDE) metadata, immutable | One more class | ≥2 related keys, anything required |
| `@Value("${k:d}")` | Single injected value | Quick; SpEL | No validation; keys scattered as strings | One isolated value or a SpEL expression |
| `Environment.getProperty` | Programmatic lookup | Dynamic keys | Stringly typed, late failure | Framework/infra code with computed keys |

Pick: `@ConfigurationProperties` + `@Validated`, unless it is a single isolated value.

### 4.4 Catch

Profiles are for environment wiring only; secrets never go in `application.yml`.

→ Profiles used as feature flags or `if (env.equals("prod"))` in code.  
⇒ Prod-only paths never run in tests.  
→ Profiles only for environment wiring; feature flags for features.

→ Secrets in `application.yml`.  
⇒ Secrets in git and in every artifact.  
→ Inject from a secrets manager or env at runtime; Identity and Access Management (IAM) auth where possible.

- Gap in this repo: `@Profile` beans described only (one runnable profile set would change base app wiring)
- 🗣 "Typed, validated `@ConfigurationProperties`; profiles only for environment differences."

## 5. Starters, Embedded Server And Actuator

- **In plain words:** starters are curated dependency bundles, the web server ships inside your jar, and Actuator adds ready-made health and metrics endpoints.

### 5.1 Starters
- One dependency (`spring-boot-starter-web`) pulls a tested, version-aligned set: Spring MVC, Jackson, embedded Tomcat
- The Boot parent / BOM pins versions, so you rarely write a version number
- Catch: a starter can bring auto-config you didn't want (a JDBC starter wants a DataSource); exclude it explicitly

### 5.2 Embedded server and fat jar
- The server (Tomcat by default; Jetty or Undertow as swaps) runs inside the app, started by `SpringApplication.run`
- `java -jar app.jar` runs anywhere with a JVM; no app server to install, which suits containers
- Knobs: `server.port`, `server.tomcat.threads.max` (request threads), `server.shutdown=graceful` with `spring.lifecycle.timeout-per-shutdown-phase`

### 5.3 Actuator
- `spring-boot-starter-actuator` adds `/actuator/health`, `/metrics`, `/info`, `/conditions`, `/env`
- Liveness vs readiness probes: liveness says "restart me", readiness says "don't send me traffic yet"
- Metrics go through Micrometer to Prometheus, CloudWatch or others
- Catch: `/env` and `/heapdump` leak secrets; expose only `health` and `info` publicly (`management.endpoints.web.exposure.include`)
- 🗣 "Readiness gates traffic, liveness gates restarts; mixing them up turns a slow dependency into a restart loop."

## 6. Knobs

| Knob | Default | What it trades | Change when |
|---|---|---|---|
| `debug=true` / `--debug` | off | Prints auto-config condition report | Diagnosing "why is/isn't this bean here" |
| `@Validated` on `@ConfigurationProperties` | off | Startup fails on bad config | Always for required config |

## 7. Failure Modes

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Mystery beans / startup failure | Auto-config triggered by a new jar | `--debug` condition report | Exclude auto-config or define your own bean |
| Bad config reaches runtime | `@Value` without validation | Failure on first use, not at startup | `@ConfigurationProperties` + `@Validated` |
| Prod-only path untested | Profile-specific code branches | Bugs only in prod | Profiles for wiring only; test each profile's context |

## 8. Interview Questions

### Q1 Boot Startup

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

### Q2 Properties vs Value

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

## 9. Code Map And Local Checks

- Java `1x/java/src/main/java/com/lc/x/concept/_01core_01principles/spring/` and `config/_01core_01principles/PrinciplesProperties`

| File | Java | Python |
|---|---|---|
| [Convention Over Configuration And Auto-Configuration](#3-convention-over-configuration-and-auto-configuration) | `spring/AutoConfig.NotifierAutoConfiguration`, `SpringPrinciplesDemo.autoconfig` | — |
| [Externalized Configuration](#4-externalized-configuration) | `config/_01core_01principles/PrinciplesProperties` (record + `@Validated`), `spring/ExternalConfig.Violation.ValueSettings`, `SpringPrinciplesDemo.config` | — |
| REST | `api/_01core_01principles/PrinciplesController.show` → GET `/principles/{name}` | `app/api/_01core_01principles.py` `show` → GET `/principles/{name}` |

- Verified locally (2026-11-13)
  - `x.principles.notifier=sms` switched the bean to `SmsNotifier`
  - `x.principles.max-attempts=0` failed startup: "must be greater than or equal to 1"
  - Slice off: `/principles` returned 404
- Gaps
  - `@Profile` beans: described only
  - Real `AutoConfiguration.imports` registration: not added; the class shows the conditions

## References

- [spring-projects/spring-boot — autoconfigure module](https://github.com/spring-projects/spring-boot/tree/main/spring-boot-project/spring-boot-autoconfigure) — real `@Conditional` auto-config classes
- [Spring Boot reference — Externalized configuration](https://docs.spring.io/spring-boot/reference/features/external-config.html) — property source order, `@ConfigurationProperties` vs `@Value`
- [Spring Boot reference — Actuator endpoints](https://docs.spring.io/spring-boot/reference/actuator/endpoints.html) — exposure, health groups, probes
