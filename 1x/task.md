# 1x — Task Queue

- Agents pick from here (Claude Code cloud, Codex, phone)
- Protocol: [AGENTS.md §6](AGENTS.md#6-taskmd-protocol)
  - Default pick = top `todo` in Queue, unless the user names an ID
  - Branch `x/X-NNN-<slug>`, PR title `X-NNN: <title>`
  - Same PR: task → `done`, `x.md` status, the three guides (`1java.md`, `1python.md`, `1tf.md`)
- Rules for every slice: [AGENTS.md §7–§11](AGENTS.md#7-knowledge-doc-rules)

## Index
- [Queue](#queue)
  - [X-013 [C] 04.01 Athena](#x-013-c-0401-athena)
  - [X-014 [C] 04.02 Redshift](#x-014-c-0402-redshift)
  - [X-015 [C] 05.01 Kinesis + Firehose to S3](#x-015-c-0501-kinesis--firehose-to-s3)
  - [X-016 [C] 05.02 Kafka (MSK)](#x-016-c-0502-kafka-msk)
- [Backlog](#backlog)
- [Done](#done)

---

## Queue

### X-013 [C] 04.01 Athena
- Status: `todo` · Terraform: `terraform/04.01.athena.tf` (exists: Glue db `x_lake`, table `clicks` with partition projection, workgroup `x-wg`)
- Files: `docs/04.01.athena.md`, Java `x04_01_athena`, Python `app/x04_01_athena/`
- Scenarios
  - Start → poll with backoff → paginate results (async query lifecycle)
  - Parameterized query (`ExecutionParameters`), workgroup enforcement
  - Partition pruning on `dt` (bytes scanned with vs without the filter)
  - CTAS to Parquet + partitioned output; `UNLOAD`
  - Cancel (StopQueryExecution), failure reasons, bytes-scanned cutoff
  - Result reuse (query result caching)
- Done when: checks pass; Code map complete

### X-014 [C] 04.02 Redshift
- Status: `todo` · Terraform: `terraform/04.02.redshift.tf` (exists: Serverless namespace `x-ns`, workgroup `x-dw`, COPY role)
- Files: `docs/04.02.redshift.md`, Java `x04_02_redshift`, Python `app/x04_02_redshift/`
- Scenarios (Redshift Data API)
  - ExecuteStatement → DescribeStatement poll → GetStatementResult pagination
  - Named parameters, BatchExecuteStatement (multi-statement transaction)
  - DDL with DISTKEY / SORTKEY choices explained in comments
  - COPY from S3 (`IAM_ROLE default`), UNLOAD to Parquet
  - Staging table + MERGE upsert pattern
  - Cancel; JDBC path mentioned in doc only
- Done when: checks pass; Code map complete

### X-015 [C] 05.01 Kinesis + Firehose to S3
- Status: `todo` · Terraform: `terraform/05.01.kinesis.tf` (exists: stream `x-clicks` on-demand, Firehose `x-clicks-to-s3`, direct-put `x-events`)
- Files: `docs/05.01.kinesis.md`, Java `x05_01_kinesis`, Python `app/x05_01_kinesis/`
- Scenarios
  - PutRecord (partition key → shard), PutRecords with `FailedRecordCount` retry of only failed entries
  - Hot shard: key choice + random suffix
  - Simple consumer: ListShards → GetShardIterator (TRIM_HORIZON / LATEST / AT_TIMESTAMP) → GetRecords loop, checkpoint by sequence number
  - Enhanced fan-out (SubscribeToShard) — Java async client; doc notes KCL as the production consumer
  - Firehose PutRecordBatch with per-record failure retry; buffering → S3 file layout → Athena
  - Idempotent consumer (dedupe on click_id)
- Done when: checks pass; Code map complete

### X-016 [C] 05.02 Kafka (MSK)
- Status: `todo` · Terraform: `terraform/05.02.kafka-msk.tf` (exists: 3 brokers, IAM auth, RF 3, min.insync 2)
- Files: `docs/05.02.kafka.md`, Java `x05_02_kafka` (Spring Kafka), Python `app/x05_02_kafka/` (confluent-kafka)
- Scenarios
  - Admin: create topic (partitions, RF, retention, `cleanup.policy=compact`)
  - Producer: idempotent, `acks=all`, keys → partition order, headers, batching knobs (`linger.ms`, `batch.size`, compression)
  - Transactions: transactional producer, read-process-write with `sendOffsetsToTransaction`
  - Consumer: group, manual commit after processing, rebalance listener, `max.poll.interval.ms`
  - Spring: `@KafkaListener`, `DefaultErrorHandler` + backoff + dead-letter topic
  - Python: poll loop, commit, DLQ produce
  - MSK IAM auth config for both languages; local mode via `localhost:9092`
- Done when: checks pass; Code map complete

---

## Backlog
> Ideas from chats; promote to Queue with full spec when picked.

- X-021 [C] 02.02 GoF design patterns — link to `1sde/1.core/design-patterns/`, add code here
- X-022 [C] 06.01 Spring IoC — container, bean lifecycle, scopes, proxies (@Transactional self-invocation trap)
- X-023 [C] 06.02 FastAPI DI — `Depends`, lifespan, async vs sync endpoints
- X-024 [C] 05.03 Flink windows — tumbling / sliding / session, watermarks (ad-click aggregator pattern)
- X-025 [C] 05.04 SQS / SNS — visibility timeout, DLQ, FIFO groups, fan-out
- X-026 07.01 Tech-choice guide — which DB / stream for which requirement, mapped to the hiNN questions
- X-027..X-029 (Bedrock, Step Functions + Bedrock, agent SDKs) → moved to `1A/task.md`
- X-030 Obsidian view of `x.md` + docs (wikilinks / MOC)

## Done
- 2026-11-13 · X-000 Skeleton: `AGENTS.md`, `terraform/AGENTS.md`, `x.md`, `task.md`, guides
- 2026-11-13 · X-001 Java base project: Spring Boot 3.5.16, Java 17, AWS SDK BOM 2.59.0, `AwsConfig`, `Retry`, `application.yml` (all slices off); `mvn compile` passed
- 2026-11-13 · X-002 Python base project: FastAPI, `X_ENABLED` slice mounting, `config.py`, `aws.py` (adaptive retries), `retry.py`; `compileall` + import smoke test passed
- 2026-11-13 · X-003 Terraform foundation + 7 component files (`00.00`–`00.03`, `03.01`–`05.02`); `terraform validate` passed (v1.9.8, aws ~> 5.80)
- 2026-11-13 · X-020 [C] 02.01 Core principles: SOLID + 13 general (Java + Python) + 7 Spring (Java only) in one doc
- 2026-11-13 · X-010 [C] 03.01 Aurora PostgreSQL: doc + Java (4 layers) + Python
- 2026-11-13 · X-011 [C] 03.02 DynamoDB: doc + Java (low-level + Enhanced) + Python (client + resource)
- 2026-11-13 · X-012 [C] 03.03 S3: doc + Java + Python; app IAM policy gains version reads
- 2026-11-13 · Full checks: `mvn compile`, `compileall` + 29-route import check, `terraform validate` passed
