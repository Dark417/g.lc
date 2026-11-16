# x — Knowledge Map (1x manifest)

- Master index of everything in `1x/`
- Mirror: claude.ai Project `1D/X/XMap.md` (keep identical; this file is master — [AGENTS.md §5](AGENTS.md#5-manifest-and-project-mirror))
- `[C]` = has code (Java + Python, + Terraform for cloud components)
- Status: ⬜ planned · 🔧 wip · ✅ gen (done) · ▶ ran · 🎓 reviewed
- Last updated: 2026-11-13

## Index
- [00java Java core](#00java-java-core)
- [01core Design principles and patterns](#01core-design-principles-and-patterns)
- [02messaging Messaging and streaming](#02messaging-messaging-and-streaming)
- [03db Databases and storage](#03db-databases-and-storage)
- [04dissys Distributed systems](#04dissys-distributed-systems)
- [05analytics Analytics and warehouses](#05analytics-analytics-and-warehouses)
- [06framework Frameworks](#06framework-frameworks)
- [ddd Domain-driven design samples](#ddd-domain-driven-design-samples)
- [base Foundation](#base-foundation)
- [AI and agents (moved to 1A)](#ai-and-agents-moved-to-1a)
- [Change log](#change-log)

### Catalog
- 00java Java core
  - (empty)
- 01core Design principles and patterns
  - ✅ [C] 01core.01principles Core principles (SOLID, general, Spring) — X-020
  - ⬜ [C] 01core.02patterns GoF design patterns — X-021
- 02messaging Messaging and streaming
  - ⬜ [C] 02messaging.01kinesis Kinesis + Firehose to S3 — X-015
  - ⬜ [C] 02messaging.02kafka Kafka (MSK) — X-016
  - ⬜ [C] 02messaging.03flink Flink windows — X-024
  - ⬜ [C] 02messaging.04sqs-sns SQS / SNS — X-025
- 03db Databases and storage
  - ✅ [C] 03db.01aurora Aurora PostgreSQL — X-010
  - ✅ [C] 03db.02dynamodb DynamoDB — X-011
  - ✅ [C] 03db.03s3 S3 — X-012
  - ✅ [C] 03db.04mongodb MongoDB — X-017
- 04dissys Distributed systems
  - ⬜ 04dissys.01tech-choice Tech-choice guide (DB / stream by requirement) — X-026
- 05analytics Analytics and warehouses
  - ⬜ [C] 05analytics.01athena Athena — X-013
  - ⬜ [C] 05analytics.02redshift Redshift — X-014
- 06framework Frameworks
  - ⬜ [C] 06framework.01spring-ioc Spring IoC — X-022
  - ⬜ [C] 06framework.02fastapi-di FastAPI DI — X-023
- ddd: `2stripe`, `2stripe2` sample projects
- base Foundation: ✅ `base_network`, `base_kms`, `base_iam` + base files (Terraform only)

---

## 00java Java core
- (empty — add Java language / JVM items here; Python-only items go to the language they demo)

## 01core Design principles and patterns
- ✅ [C] 01core.01principles Core principles — task X-020
  - x-md `x-md/01core/solid.md`, `design-principles.md`, `spring.md`, `spring-boot.md` (merged 2026-11-15 from 18 files) · Java `com.lc.x.concept._01core_01principles.{solid,general,spring}` + `api`/`config` · Python `app/concept/_01core_01principles/`
  - Part A SOLID (Java + Python) · Part B 13 general principles (Java + Python) · Part C 7 Spring principles (Java only)
  - Each principle: `Violation` vs `Fix` + `demo()`; Spring: IoC/DI, proxy AOP + self-invocation trap, conditional beans, validated `@ConfigurationProperties`, template method
  - 2026-11-13 · Claude · javac + context run passed; 25 demos return 200
- 🔧 [C] 01core.02patterns GoF design patterns — task X-021
  - x-md `x-md/01core/1design-patterns.md`: all 23 GoF (plain opener, analogy mapping, when / when not, JDK and Spring uses) + non-GoF map; code not yet in the projects

## 02messaging Messaging and streaming
- ⬜ [C] 02messaging.01kinesis Kinesis + Firehose to S3 — task X-015
  - x-md `x-md/02messaging/02messaging.01kinesis.*` · Java `<layer>._02messaging_01kinesis` · Python `app/<layer>/_02messaging_01kinesis.py`
  - Terraform ✅ `modules/02messaging_01kinesis/` (stream `x-clicks`, Firehose to `raw/clicks/dt=`)
- ⬜ [C] 02messaging.02kafka Kafka (MSK) — task X-016
  - x-md `x-md/02messaging/02messaging.02kafka.*` · Java `<layer>._02messaging_02kafka` · Python `app/<layer>/_02messaging_02kafka.py`
  - Terraform ✅ `modules/02messaging_02kafka/` (3 brokers, IAM auth, RF 3, min.insync 2)
- ⬜ [C] 02messaging.03flink Flink windows — task X-024
- ⬜ [C] 02messaging.04sqs-sns SQS / SNS — task X-025

## 03db Databases and storage
- ✅ [C] 03db.01aurora Aurora PostgreSQL — task X-010
  - x-md `x-md/03db/01aurora.*` (18 files) · Java `com.lc.x.<layer>._03db_01aurora` (config, api, domain, infra, service + `resources/_03db_01aurora/schema.sql`) · Python `app/<layer>/_03db_01aurora.py`
  - Writer/reader Hikari pools, IAM token per new connection, batch, upsert, keyset vs OFFSET, optimistic + pessimistic locks, SKIP LOCKED queue, JSONB/GIN, propagation + isolation, retry on 40001/40P01/08xxx with idempotency keys
  - 2026-11-13 · Claude · javac + Spring context start passed; Python 17 routes
  - Terraform ✅ `modules/03db_01aurora/` (writer + reader, Serverless v2, IAM auth)
- ✅ [C] 03db.02dynamodb DynamoDB — task X-011
  - x-md `x-md/03db/02dynamodb.*` (14 files) · Java `<layer>._03db_02dynamodb` (low-level + Enhanced Client) · Python `app/<layer>/_03db_02dynamodb.py` (client + resource)
  - Conditions, optimistic lock, cursors, batch retry, idempotent TransactWriteItems with cancellation parsing, streams shape, write sharding
  - 2026-11-13 · Claude · javac + offline Stubber tests passed
  - Terraform ✅ `modules/03db_02dynamodb/` (`x-orders` PK/SK + GSI1, TTL, streams; `x-idempotency`)
- ✅ [C] 03db.03s3 S3 — task X-012
  - x-md `x-md/03db/03s3.*` (10 files) · Java `<layer>._03db_03s3` · Python `app/<layer>/_03db_03s3.py`
  - Terraform ✅ `modules/03db_03s3/` (lake bucket with lifecycle; Athena results bucket; app policy now includes version reads)
  - Put/get/head/delete + SSE-KMS, paginated list, presign GET/PUT (+ POST in Python), multipart + Transfer Manager, conditional create, versions, ranged GET
  - 2026-11-13 · Claude · javac + compileall passed
- ✅ [C] 03db.04mongodb MongoDB — task X-017
  - x-md `x-md/03db/04mongodb.*` · Java `<layer>._03db_04mongodb` (sync driver) · Python `app/<layer>/_03db_04mongodb.py` (pymongo) · local `local/mongodb/` (docker replica set)
  - Terraform ✅ `modules/03db_04mongodb/` (Amazon DocumentDB, Mongo-compatible)
  - Validator, extended reference, atomic operators, arrayFilters, pipeline update, queue claim, optimistic lock, bulk upsert, ESR indexes, explain, keyset cursor, `$facet` / window / `$merge`, transactions with retry labels, write skew, change streams with resume token
  - Source: retired `1sde/2.database/1.mongodb*.md` + `2de/mongodb/` (removed)

## 04dissys Distributed systems
- ⬜ 04dissys.01tech-choice Tech-choice guide — task X-026

## 05analytics Analytics and warehouses
- ⬜ [C] 05analytics.01athena Athena — task X-013
  - x-md `x-md/05analytics/05analytics.01athena.*` · Java `<layer>._05analytics_01athena` · Python `app/<layer>/_05analytics_01athena.py`
  - Terraform ✅ `modules/05analytics_01athena/` (Glue table `clicks`, partition projection, workgroup `x-wg`)
- ⬜ [C] 05analytics.02redshift Redshift — task X-014
  - x-md `x-md/05analytics/05analytics.02redshift.*` · Java `<layer>._05analytics_02redshift` · Python `app/<layer>/_05analytics_02redshift.py`
  - Terraform ✅ `modules/05analytics_02redshift/` (Serverless `x-ns` / `x-dw`, COPY role)

## 06framework Frameworks
- ⬜ [C] 06framework.01spring-ioc Spring IoC — task X-022
- ⬜ [C] 06framework.02fastapi-di FastAPI DI — task X-023

## ddd Domain-driven design samples
- Outside numbering; moved from `2de/` on 2026-11-13
  - `ddd/2stripe/` — Spring Boot Stripe payment POC (controller, service, repository, webhook)
  - `ddd/2stripe2/` — second Stripe POC

## base Foundation
- ✅ base_* (3 modules) (Terraform only)
  - Base files `versions.tf` `backend.tf` `providers.tf` `variables.tf` `locals.tf` `main.tf` `outputs.tf`; `local.prefix = "x-<env>"`, default tags; envs `local` `dev` `uat` `prod`
  - `modules/base_network/` — VPC, private subnets, app SG, S3/DynamoDB gateway endpoints
  - `modules/base_kms/` — one CMK `alias/x-<env>-data` for all data at rest
  - `modules/base_iam/` — app role `x-<env>-app`; components attach their own policies
  - 2026-11-13 · Claude · `terraform validate` passed

## AI and agents (moved to 1A)
- Moved to `1A/` (AI knowledge tree): Bedrock basics → `1A` 01.01, Step Functions + Bedrock → `1A` A-072, agent SDKs → `1A` A-062/A-063


## Change log
- 2026-11-15 · `2backend/2api.md` + `2rest-ds.md` merged into `2api-ds.md` (formerly `2api-design`); sources removed
- 2026-11-15 · 1sd/00.base 04–14 moved into `x-md/02backend`: `2api-design`, `3messaging-async`, `4data-modeling` (root) + `4data-rds-ds`, `4data-nosql-ds`, `4data-redis-ds`, `4data-caching`, `4database`, `5performance-capacity`, new `5observability` (L5); consistency → `1dissys` §9.8–9.11, partitioning → `4persistence` §6.6–6.9, reliability → `5cloud-availability` §4, security → `7security` §12.1, 15.1, 19, 20b–20c
- 2026-11-13 · X-042 Regroup: 00java, 01core, 02messaging, 03db, 04dissys, 05analytics, 06framework; Terraform foundation → unnumbered `base_*`; `ddd/` added from `2de/`
- 2026-11-13 · X-040 Restructure: group names, layer-first code (`_GGgroup_CCcomp`), `docs/` → `x-md/` (60 flat files, Java + Python blocks), Terraform project with `envs/` + `modules/`, shared AGENTS.md
- 2026-11-13 · Done: base projects, 02.01 core principles, 03.01 Aurora, 03db.02dynamodb DynamoDB, 03db.03s3 S3; AI group moved to `1A/`
- 2026-11-13 · Created: rules, manifest, task queue, Terraform foundation + 7 component files
