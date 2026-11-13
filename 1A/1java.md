# 1java — Java project guide (1A)

- Project: `java/` — one Maven project, Spring Boot 3.5.x, Java 17
- Scope: the backend call path only (a Spring service calling Bedrock); everything else is Python
- Rules: [AGENTS.md §1, §8–§9](AGENTS.md#9-java-rules)

## Index
- [1. Build and run](#1-build-and-run)
- [2. Layout](#2-layout)
- [3. Slices](#3-slices)

## 1. Build and run
- Compile: `cd 1A/java && mvn -q -DskipTests compile`
- Run (all slices off): `mvn spring-boot:run` (port 8081)
- Enable a slice: `--a.guardrails.enabled=true` (or env `A_GUARDRAILS_ENABLED=true`)

## 2. Layout
```
java/src/main/java/com/lc/a/
  AApplication.java
  shared/                     AwsConfig, Retry
  a01_01_converse/{api,service,domain,infra}
  a04_01_guardrails/{api,service,domain,infra}
```

## 3. Slices
| Number | Package | Status |
|---|---|---|
| 01.01 | `a01_01_converse` | 🔧 A-010 |
| 04.01 | `a04_01_guardrails` | 🔧 A-040 |
