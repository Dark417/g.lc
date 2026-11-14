# 01core.01principles.14external-config Externalized Configuration

> One artifact everywhere; behavior differs per environment via typed, validated config, not code.

## Index

- [1. Idea](#1-idea)
- [2. Code](#2-code)
  - [2.1 Violation](#21-violation)
  - [2.2 Fix](#22-fix)
- [3. Config Binding Compared](#3-config-binding-compared)
- [4. Catch](#4-catch)
- [References](#references)

Part C, Spring principles (Java only). Back to [00index](00index.md).

## 1. Idea

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
- Encapsulate what varies per environment ([08](08composition-interface-encapsulate.md#3-encapsulate-what-varies)); fail fast on bad config ([10](10cqs-failfast-pola.md#2-fail-fast))

## 2. Code

`@Value` strings vs a validated `@ConfigurationProperties` record.

### 2.1 Violation

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

### 2.2 Fix

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
- `TemplateMethod.demo(props.maxAttempts())` reads the typed value ([15template](15template.md))
- Verified locally: `x.principles.max-attempts=0` failed startup with "must be greater than or equal to 1"

## 3. Config Binding Compared

Three ways to read config in Spring.

| Option | What it is | Strength | Weakness | Choose when |
|---|---|---|---|---|
| `@ConfigurationProperties` record | Typed group bound by prefix | Validation, relaxed binding, Integrated Development Environment (IDE) metadata, immutable | One more class | ≥2 related keys, anything required |
| `@Value("${k:d}")` | Single injected value | Quick; SpEL | No validation; keys scattered as strings | One isolated value or a SpEL expression |
| `Environment.getProperty` | Programmatic lookup | Dynamic keys | Stringly typed, late failure | Framework/infra code with computed keys |

Pick: `@ConfigurationProperties` + `@Validated`, unless it is a single isolated value.

## 4. Catch

Profiles are for environment wiring only; secrets never go in `application.yml`.

→ Profiles used as feature flags or `if (env.equals("prod"))` in code.  
⇒ Prod-only paths never run in tests.  
→ Profiles only for environment wiring; feature flags for features.

→ Secrets in `application.yml`.  
⇒ Secrets in git and in every artifact.  
→ Inject from a secrets manager or env at runtime; Identity and Access Management (IAM) auth where possible.

- Gap in this repo: `@Profile` beans described only (one runnable profile set would change base app wiring)
- 🗣 "Typed, validated `@ConfigurationProperties`; profiles only for environment differences."

## References

- [Spring Boot reference — Externalized configuration](https://docs.spring.io/spring-boot/reference/features/external-config.html) — property source order, `@ConfigurationProperties` vs `@Value`
