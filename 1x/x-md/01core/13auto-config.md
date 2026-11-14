# 01core.01principles.13auto-config Convention Over Configuration And Auto-Configuration

> Sensible beans by default from the classpath and config, backing off when you define your own.

## Index

- [1. Idea](#1-idea)
- [2. What Spring Boot Does At Startup](#2-what-spring-boot-does-at-startup)
- [3. Code](#3-code)
- [4. Debug](#4-debug)
- [5. Catch](#5-catch)
- [References](#references)

Part C, Spring principles (Java only). Back to [00index](00index.md).

## 1. Idea

Defaults come from what is on the classpath and in config; your own bean wins.

- Auto-config = `@Conditional` beans that back off when you define your own
- Example (`AutoConfig.NotifierAutoConfiguration`)
  - `@ConditionalOnProperty(x.principles.notifier=sms)` → Short Message Service (SMS) notifier
  - Else `@ConditionalOnMissingBean(Notifier.class)` → default log notifier
- Use for library/starter code that must offer defaults yet yield to the application

## 2. What Spring Boot Does At Startup

Boot builds the environment, parses your config first, then filters auto-config candidates by condition.

→ `SpringApplication.run` builds the `Environment` (command line, env vars, `application-{profile}.yml`, `application.yml`)  
→ `@SpringBootApplication` = `@Configuration` + `@ComponentScan` + `@EnableAutoConfiguration`  
→ User configuration classes are parsed first  
→ `AutoConfigurationImportSelector` loads candidates from `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` (Boot ≥ 2.7; `spring.factories` before)  
→ Each candidate is filtered by `@ConditionalOnClass`, `@ConditionalOnMissingBean`, `@ConditionalOnProperty`, `@ConditionalOnWebApplication`  
→ Survivors register beans; singletons are created; the embedded web server starts  
→ `ApplicationReadyEvent`

## 3. Code

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

## 4. Debug

Two ways to see why a bean is or isn't there.

- `--debug` (or `debug=true`) prints the condition evaluation report
- Actuator `/actuator/conditions` shows it at runtime

## 5. Catch

`@ConditionalOnMissingBean` in ordinary `@Configuration` depends on parse order.

→ A jar on the classpath activates a feature.  
⇒ Adding `spring-jdbc` makes Boot want a DataSource Uniform Resource Locator (URL) at startup.  
→ Exclude it explicitly — `XApplication` excludes `DataSourceAutoConfiguration` for exactly this reason.

→ `@ConditionalOnMissingBean` in an ordinary `@Configuration`.  
⇒ Result depends on parse order; it is only reliable in real auto-configuration classes (processed after user config).  
→ Use it in auto-config registered in `AutoConfiguration.imports`; in app code, wire explicitly.

- Gap in this repo: real `AutoConfiguration.imports` registration not added, to keep shared `resources/` untouched; the class shows the conditions
- 🗣 "Auto-config is `@Conditional` beans that back off when I define my own."

## References

- [spring-projects/spring-boot — autoconfigure module](https://github.com/spring-projects/spring-boot/tree/main/spring-boot-project/spring-boot-autoconfigure) — real `@Conditional` auto-config classes
