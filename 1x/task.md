# 1x Task Queue

> Work queue for 1x agents (Claude Code, Codex, phone), plus the Java and Python guide.

- Protocol: [AGENTS.md §7](AGENTS.md#7-taskmd-protocol)
  - Default pick = top `todo` in Queue, unless the user names an ID
  - Branch `x/X-NNN-<slug>`, PR title `X-NNN: <title>`
  - ✅ After each round: finished tasks leave Queue → top of Finish, same change updates `x.md`, Guide tables, `1tf.md`
- New text the user drops anywhere here → becomes a Queue task + Index line

## Index

- [Queue](#queue)
  - 02messaging
    - [X-015 02messaging.01kinesis](#x-015-c-02messaging01kinesis)
    - [X-016 02messaging.02kafka](#x-016-c-02messaging02kafka)
  - 05analytics
    - [X-013 05analytics.01athena](#x-013-c-05analytics01athena)
    - [X-014 05analytics.02redshift](#x-014-c-05analytics02redshift)
  - base
    - [X-041 Env-aware resource names in app config](#x-041-env-aware-resource-names-in-app-config)
- [Backlog](#backlog)
  - X-021 01core.02patterns · X-022 06framework.01spring-ioc · X-023 06framework.02fastapi-di
  - X-024 02messaging.03flink · X-025 02messaging.04sqs-sns · X-026 04dissys.01tech-choice · X-030 Obsidian view
- [Finish](#finish)
  - X-017 03db.04mongodb · X-042 Regroup · X-040 Restructure · X-020 01core.01principles · X-010..X-012 03db · X-000..X-003 base
- [Guide](#guide)
  - [Java](#java) · [Python](#python)

---

## Queue

### X-015 [C] 02messaging.01kinesis

- Status: `todo` · Terraform: `modules/02messaging_01kinesis/` (exists: stream `x-clicks` on-demand, Firehose `x-clicks-to-s3`, direct-put `x-events`)
- Files: `x-md/02messaging/02messaging.01kinesis.*`, Java `<layer>._02messaging_01kinesis`, Python `app/<layer>/_02messaging_01kinesis.py`
- Scenarios
  - PutRecord (partition key → shard), PutRecords with `FailedRecordCount` retry of only failed entries
  - Hot shard: key choice + random suffix
  - Simple consumer: ListShards → GetShardIterator (TRIM_HORIZON / LATEST / AT_TIMESTAMP) → GetRecords loop, checkpoint by sequence number
  - Enhanced fan-out (SubscribeToShard) — Java async client; x-md notes KCL as the production consumer
  - Firehose PutRecordBatch with per-record failure retry; buffering → S3 file layout → Athena
  - Idempotent consumer (dedupe on click_id)
- Finish when: checks pass; `00index` Code map complete

### X-016 [C] 02messaging.02kafka

- Status: `todo` · Terraform: `modules/02messaging_02kafka/` (exists: 3 brokers, IAM auth, RF 3, min.insync 2)
- Files: `x-md/02messaging/02messaging.02kafka.*`, Java `<layer>._02messaging_02kafka` (Spring Kafka), Python `app/<layer>/_02messaging_02kafka.py` (confluent-kafka)
- Scenarios
  - Admin: create topic (partitions, RF, retention, `cleanup.policy=compact`)
  - Producer: idempotent, `acks=all`, keys → partition order, headers, batching knobs (`linger.ms`, `batch.size`, compression)
  - Transactions: transactional producer, read-process-write with `sendOffsetsToTransaction`
  - Consumer: group, manual commit after processing, rebalance listener, `max.poll.interval.ms`
  - Spring: `@KafkaListener`, `DefaultErrorHandler` + backoff + dead-letter topic
  - Python: poll loop, commit, DLQ produce
  - MSK IAM auth config for both languages; local mode via `localhost:9092`
- Finish when: checks pass; `00index` Code map complete

---

## Backlog

> Ideas from chats; promote to Queue with a full spec when picked.

- X-021 [C] 01core.02patterns — GoF design patterns; source from the retired `1sde/1.core/design-patterns/` (git history), add code here
- X-022 [C] 06framework.01spring-ioc — container, bean lifecycle, scopes, proxies (@Transactional self-invocation trap)
- X-023 [C] 06framework.02fastapi-di — `Depends`, lifespan, async vs sync endpoints
- X-024 [C] 02messaging.03flink — tumbling / sliding / session windows, watermarks (ad-click aggregator pattern)
- X-025 [C] 02messaging.04sqs-sns — visibility timeout, DLQ, FIFO groups, fan-out
- X-026 04dissys.01tech-choice — which DB / stream for which requirement, mapped to the hiNN questions
- X-027..X-029 (Bedrock, Step Functions + Bedrock, agent SDKs) → moved to `1A/task.md`
- X-030 Obsidian view of `x.md` + x-md (wikilinks / MOC)

## Finish

- 2026-11-13 · X-017 [C] 03db.04mongodb: 17 x-md files (Java + Python blocks), Java sync-driver showcase (config, api, domain, infra, service), pymongo slice `mongodb`, Terraform `modules/03db_04mongodb` (DocumentDB), local replica set in `local/mongodb/`; `2de/mongodb` removed; not compiled or run (example code)
- 2026-11-13 · X-042 Regroup: `00java` `01core` `02messaging` `03db` `04dissys` `05analytics` `06framework`; Terraform foundation → unnumbered `base_network` `base_kms` `base_iam`; `ddd/` (2stripe, 2stripe2) moved in from `2de/`
- 2026-11-13 · X-040 Restructure: group names (`01core`, `03db`, …), layer-first Java + Python with `_GGgroup_CCcomp` packages, `docs/` → `x-md/<group>/` flat concept files with Java + Python blocks, Terraform project (base files, `envs/` local/dev/uat/prod, `modules/`), shared AGENTS.md synced with 1A, `1java.md` + `1python.md` merged into this Guide
- 2026-11-13 · Full checks: `mvn compile`, `compileall` + 29-route import check, `terraform validate` passed
- 2026-11-13 · X-012 [C] 03db.03s3: x-md + Java + Python; app IAM policy gains version reads
- 2026-11-13 · X-011 [C] 03db.02dynamodb: x-md + Java (low-level + Enhanced) + Python (client + resource)
- 2026-11-13 · X-010 [C] 03db.01aurora: x-md + Java (4 layers) + Python
- 2026-11-13 · X-020 [C] 01core.01principles: SOLID + 13 general (Java + Python) + 7 Spring (Java only)
- 2026-11-13 · X-003 Terraform foundation + 7 components; `terraform validate` passed (v1.9.8, aws ~> 5.80)
- 2026-11-13 · X-002 Python base project: FastAPI, `X_ENABLED` slice mounting, `config.py`, `aws.py` (adaptive retries), `retry.py`
- 2026-11-13 · X-001 Java base project: Spring Boot 3.5.16, Java 17, AWS SDK BOM 2.59.0, `AwsConfig`, `Retry`, `application.yml` (all slices off)
- 2026-11-13 · X-000 Skeleton: `AGENTS.md`, `terraform/AGENTS.md`, `x.md`, `task.md`, guides

---

## Guide

Build, run, and slice tables for both code projects (was `1java.md` + `1python.md`).

### Java

- Project: `java/` — one Maven project, Spring Boot 3.5.x, Java 17
- Compile: `cd 1x/java && mvn -q -DskipTests compile`
- Run (all slices off): `mvn spring-boot:run`
- Enable a slice: `--x.aurora.enabled=true` (or env `X_AURORA_ENABLED=true`)

```text
java/src/main/java/com/lc/x/
  XApplication.java
  shared/                       AwsConfig, Retry
  config/_03db_01aurora/        AuroraConfig, AuroraProperties
  api/_03db_01aurora/           AuroraController
  domain/_03db_01aurora/        models, ports, exceptions
  infra/_03db_01aurora/         AuroraJdbcRepository, IamAuthDataSource, ...
  service/_03db_01aurora/       AuroraOrderService, AuroraOrderTx, ...
  concept/_01core_01principles/ {solid,general,spring} + PrinciplesCatalog
java/src/main/resources/_03db_01aurora/schema.sql
```

| Component | Layers | Status |
| --- | --- | --- |
| `_01core_01principles` | concept, config, api | ✅ X-020 |
| `_03db_01aurora` | config, api, domain, infra, service | ✅ X-010 |
| `_03db_02dynamodb` | config, api, domain, infra, service | ✅ X-011 |
| `_03db_03s3` | config, api, domain, infra | ✅ X-012 |
| `_03db_04mongodb` | config, api, domain, infra, service | ✅ X-017 |
| `_05analytics_01athena` · `_05analytics_02redshift` | — | ⬜ X-013 · X-014 |
| `_02messaging_01kinesis` · `_02messaging_02kafka` | — | ⬜ X-015 · X-016 |

### Python

- Project: `python/` — one FastAPI project, Python 3.11+
- Windows: `cd 1x\python; py -m venv .venv; .venv\Scripts\activate; pip install -e .`
- Linux/macOS: `cd 1x/python && python -m venv .venv && . .venv/bin/activate && pip install -e .`
- Check: `python -m compileall -q app` and `X_ENABLED=principles,aurora,dynamodb,s3 python -c "from app.main import app; print(sorted(app.openapi()['paths']))"`
- Run: `uvicorn app.main:app --reload`; enable slices with `X_ENABLED=aurora,dynamodb`

```text
python/app/
  main.py                       SLICES: X_ENABLED name -> module name
  shared/                       config.py, aws.py, retry.py
  api/_03db_01aurora.py         router
  domain/_03db_01aurora.py
  infra/_03db_01aurora.py
  service/_03db_01aurora.py
  concept/_01core_01principles/ solid.py, general.py
```

| Component | `X_ENABLED` | Layers | Status |
| --- | --- | --- | --- |
| `_01core_01principles` | `principles` | concept, api | ✅ X-020 |
| `_03db_01aurora` | `aurora` | api, domain, infra, service | ✅ X-010 |
| `_03db_02dynamodb` | `dynamodb` | api, domain, infra, service | ✅ X-011 |
| `_03db_03s3` | `s3` | api, domain, infra | ✅ X-012 |
| `_03db_04mongodb` | `mongodb` | config, api, domain, infra, service | ✅ X-017 |
| `_05analytics_*` · `_02messaging_*` | `athena` `redshift` `kinesis` `kafka` | — | ⬜ X-013..X-016 |
