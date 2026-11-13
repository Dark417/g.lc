# 1java — Java project guide

- Project: `java/` — one Maven project, Spring Boot 3.5.x, Java 17 (task X-001)
- Rules: [AGENTS.md §8–§9](AGENTS.md#9-java-rules)

## Index
- [1. Build and run](#1-build-and-run)
- [2. Layout](#2-layout)
- [3. Slices](#3-slices)

## 1. Build and run
- Compile: `cd 1x/java && mvn -q -DskipTests compile`
- Run (all slices off): `mvn spring-boot:run`
- Enable a slice: `--x.aurora.enabled=true` (or env `X_AURORA_ENABLED=true`)

## 2. Layout
```
java/src/main/java/com/lc/x/
  XApplication.java
  shared/                 AwsConfig, Retry
  x03_01_aurora/{api,service,domain,infra}
  x03_02_dynamodb/...
```

## 3. Slices
| Number | Package | Status |
|---|---|---|
| 03.01 | `x03_01_aurora` | ⬜ X-010 |
| 03.02 | `x03_02_dynamodb` | ⬜ X-011 |
| 03.03 | `x03_03_s3` | ⬜ X-012 |
| 04.01 | `x04_01_athena` | ⬜ X-013 |
| 04.02 | `x04_02_redshift` | ⬜ X-014 |
| 05.01 | `x05_01_kinesis` | ⬜ X-015 |
| 05.02 | `x05_02_kafka` | ⬜ X-016 |
