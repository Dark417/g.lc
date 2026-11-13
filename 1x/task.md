# 1x — Task Queue

- Agents pick from here (Claude Code cloud, Codex, phone)
- Protocol: [AGENTS.md §6](AGENTS.md#6-taskmd-protocol)
  - Default pick = top `todo` in Queue, unless the user names an ID
  - Branch `x/X-NNN-<slug>`, PR title `X-NNN: <title>`
  - Same PR: task → `done`, `x.md` status, the three guides (`1java.md`, `1python.md`, `1tf.md`)
- Rules for every slice: [AGENTS.md §7–§11](AGENTS.md#7-knowledge-doc-rules)

## Index
- [Queue](#queue)
  - [X-001 Java base project](#x-001-java-base-project)
  - [X-002 Python base project](#x-002-python-base-project)
  - [X-010 [C] 03.01 Aurora PostgreSQL](#x-010-c-0301-aurora-postgresql)
  - [X-011 [C] 03.02 DynamoDB](#x-011-c-0302-dynamodb)
  - [X-012 [C] 03.03 S3](#x-012-c-0303-s3)
  - [X-013 [C] 04.01 Athena](#x-013-c-0401-athena)
  - [X-014 [C] 04.02 Redshift](#x-014-c-0402-redshift)
  - [X-015 [C] 05.01 Kinesis + Firehose to S3](#x-015-c-0501-kinesis--firehose-to-s3)
  - [X-016 [C] 05.02 Kafka (MSK)](#x-016-c-0502-kafka-msk)
- [Backlog](#backlog)
- [Done](#done)

---

## Queue

### X-001 Java base project
- Status: `todo`
- Spec
  - `java/pom.xml`: Spring Boot 3.5.x parent, Java 17, group `com.lc`, artifact `x`
  - Deps: web, jdbc, postgresql, spring-kafka, AWS SDK v2 BOM (dynamodb, dynamodb-enhanced, s3, athena, redshiftdata, kinesis, firehose, rds), `software.amazon.msk:aws-msk-iam-auth`
  - `com.lc.x.XApplication`; exclude `DataSourceAutoConfiguration` (Aurora slice builds its own Hikari pool)
  - `com.lc.x.shared`: `AwsConfig` (region + credentials provider beans), `Retry` helper (exponential backoff + full jitter)
  - `application.yml`: every `x.<slice>.enabled: false`, resource names matching Terraform outputs (`x-orders`, `x-clicks`, ...)
- Done when
  - `mvn -q -DskipTests compile` passes
  - App starts with no AWS access (all slices off)

### X-002 Python base project
- Status: `todo`
- Spec
  - `python/pyproject.toml` (Python 3.11+): fastapi, uvicorn, boto3, psycopg[binary,pool], confluent-kafka, pydantic-settings
  - `app/main.py`: mounts a slice router only when listed in `X_ENABLED` (comma list)
  - `app/shared/config.py` (settings from env), `app/shared/aws.py` (one boto3 Session, client factory with retry config `mode="adaptive"`)
  - `README` section in `1python.md`: venv create, install, run
- Done when
  - `python -m compileall -q app` passes
  - `uvicorn app.main:app` starts with `X_ENABLED` empty

### X-010 [C] 03.01 Aurora PostgreSQL
- Status: `todo` · Needs X-001, X-002 · Terraform: `terraform/03.01.aurora-postgres.tf` (exists)
- Files
  - `docs/03.01.aurora-postgres.md`
  - Java `com.lc.x.x03_01_aurora.{domain,service,infra,api}` (full reference slice: all 4 layers)
  - Python `app/x03_01_aurora/{domain,service,infra,api}.py`
- Scenarios the infra showcase must cover
  - Connection: Hikari pool knobs (max size, timeouts, max lifetime < failover DNS TTL), writer vs reader endpoint routing
  - IAM auth token (RDS utilities generateAuthenticationToken), TLS required
  - CRUD, batch insert (JDBC batch / `executemany`), upsert `INSERT ... ON CONFLICT DO UPDATE`
  - Keyset pagination vs OFFSET (show why OFFSET degrades)
  - Optimistic lock (version column, 0 rows updated = conflict)
  - Pessimistic lock `SELECT ... FOR UPDATE`, job queue `FOR UPDATE SKIP LOCKED`
  - Transactions: `@Transactional` propagation + isolation levels; Python `with conn.transaction()`
  - JSONB column + GIN index query
  - Retry on failover / serialization failure (SQLSTATE 40001, 08xxx) with idempotent writes
  - Read-after-write caveat on the reader endpoint (replica lag)
- Done when: AGENTS §11 checks pass; doc §7 Code map lists every scenario

### X-011 [C] 03.02 DynamoDB
- Status: `todo` · Terraform: `terraform/03.02.dynamodb.tf` (exists: `x-orders` PK/SK + GSI1, `x-idempotency`)
- Files: `docs/03.02.dynamodb.md`, Java `x03_02_dynamodb`, Python `app/x03_02_dynamodb/`
- Scenarios
  - Single-table key design (keys documented in the .tf header)
  - PutItem with `attribute_not_exists` (create-only), GetItem strong vs eventual
  - UpdateItem expressions: SET / ADD atomic counter / REMOVE, `ReturnValues`
  - Optimistic lock with a `version` condition
  - Query by PK + `begins_with` / `between` on SK, GSI query (eventual only)
  - Pagination with `LastEvaluatedKey` → opaque cursor
  - Scan + parallel scan (and why to avoid)
  - BatchWrite / BatchGet with `UnprocessedItems` retry + backoff
  - TransactWriteItems (order + idempotency record together), cancellation reasons
  - TTL, Streams record shape (NEW_AND_OLD_IMAGES)
  - Hot partition: write sharding suffix demo
  - Java: both low-level client and Enhanced Client; Python: client + resource
- Done when: checks pass; Code map complete

### X-012 [C] 03.03 S3
- Status: `todo` · Terraform: `terraform/03.03.s3.tf` (exists: lake + athena-results buckets)
- Files: `docs/03.03.s3.md`, Java `x03_03_s3`, Python `app/x03_03_s3/`
- Scenarios
  - Put / get / head / delete, metadata, SSE-KMS
  - List with pagination (prefix + delimiter = "folders")
  - Presigned GET and PUT URLs (expiry, who signs)
  - Multipart upload (initiate, parts, complete, abort) + Transfer Manager / `upload_file`
  - Conditional writes (`If-None-Match: *`), versioning, ranged GET
  - Consistency note: strong read-after-write (since Dec 2020)
- Done when: checks pass; Code map complete

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

- X-020 [C] 02.01 SOLID — each principle: violation vs fix, Java + Python
- X-021 [C] 02.02 GoF design patterns — link to `1sde/1.core/design-patterns/`, add code here
- X-022 [C] 06.01 Spring IoC — container, bean lifecycle, scopes, proxies (@Transactional self-invocation trap)
- X-023 [C] 06.02 FastAPI DI — `Depends`, lifespan, async vs sync endpoints
- X-024 [C] 05.03 Flink windows — tumbling / sliding / session, watermarks (ad-click aggregator pattern)
- X-025 [C] 05.04 SQS / SNS — visibility timeout, DLQ, FIFO groups, fan-out
- X-026 07.01 Tech-choice guide — which DB / stream for which requirement, mapped to the hiNN questions
- X-027 [C] 08.01 Bedrock — Terraform + basic calls (Converse API), Java + Python
- X-028 [C] 08.02 Step Functions orchestration of Bedrock calls
- X-029 [C] 08.03 Agent SDKs side by side — ADK/Vertex, Strands, AgentCore, LangChain, Python SDK
- X-030 Obsidian view of `x.md` + docs (wikilinks / MOC)

## Done
- 2026-11-13 · X-000 Skeleton: `AGENTS.md`, `terraform/AGENTS.md`, `x.md`, `task.md`, guides
- 2026-11-13 · X-003 Terraform foundation + 7 component files (`00.00`–`00.03`, `03.01`–`05.02`); `terraform validate` passed (v1.9.8, aws ~> 5.80)
