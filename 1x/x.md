# x — Knowledge Map (1x manifest)

- Master index of everything in `1x/`
- Mirror: claude.ai Project `1D/X/XMap.md` (keep identical; this file is master — [AGENTS.md §4](AGENTS.md#4-manifest-xmd-and-the-project-xmap))
- `[C]` = has code (Java + Python, + Terraform for cloud components)
- Status: ⬜ planned · 🔧 wip · ✅ gen (done) · ▶ ran · 🎓 reviewed
- Last updated: 2026-11-13

## Index
- [00 Foundation](#00-foundation)
- [01 Language core](#01-language-core)
- [02 Design principles and patterns](#02-design-principles-and-patterns)
- [03 Databases and storage](#03-databases-and-storage)
- [04 Analytics and warehouses](#04-analytics-and-warehouses)
- [05 Streaming and messaging](#05-streaming-and-messaging)
- [06 Frameworks](#06-frameworks)
- [07 Distributed systems concepts](#07-distributed-systems-concepts)
- [08 AI and agents](#08-ai-and-agents)
- [Change log](#change-log)

### Catalog
- 00 Foundation
  - ✅ 00.00–00.03 Providers, network, KMS, IAM (Terraform only)
- 01 Language core
  - (empty)
- 02 Design principles and patterns
  - ⬜ [C] 02.01 SOLID — X-020
  - ⬜ [C] 02.02 GoF design patterns — X-021
- 03 Databases and storage
  - ⬜ [C] 03.01 Aurora PostgreSQL — X-010
  - ⬜ [C] 03.02 DynamoDB — X-011
  - ⬜ [C] 03.03 S3 — X-012
- 04 Analytics and warehouses
  - ⬜ [C] 04.01 Athena — X-013
  - ⬜ [C] 04.02 Redshift — X-014
- 05 Streaming and messaging
  - ⬜ [C] 05.01 Kinesis + Firehose to S3 — X-015
  - ⬜ [C] 05.02 Kafka (MSK) — X-016
  - ⬜ [C] 05.03 Flink windows — X-024
  - ⬜ [C] 05.04 SQS / SNS — X-025
- 06 Frameworks
  - ⬜ [C] 06.01 Spring IoC — X-022
  - ⬜ [C] 06.02 FastAPI DI — X-023
- 07 Distributed systems concepts
  - ⬜ 07.01 Tech-choice guide (DB / stream by requirement) — X-026
- 08 AI and agents
  - ⬜ [C] 08.01 Bedrock basics — X-027
  - ⬜ [C] 08.02 Step Functions + Bedrock — X-028
  - ⬜ [C] 08.03 Agent SDKs side by side — X-029

---

## 00 Foundation
- ✅ 00.00–00.03 (Terraform only)
  - `terraform/00.00.providers.tf` — provider, variables, `local.prefix = "x"`, default tags
  - `terraform/00.01.network.tf` — VPC, 3 private subnets, app SG, S3/DynamoDB gateway endpoints
  - `terraform/00.02.kms.tf` — one CMK `alias/x-data` for all data at rest
  - `terraform/00.03.iam.tf` — app role `x-app`; components attach their own policies
  - 2026-11-13 · Claude · `terraform validate` passed

## 01 Language core
- (empty — add Java / Python core items here)

## 02 Design principles and patterns
- ⬜ [C] 02.01 SOLID — task X-020
- ⬜ [C] 02.02 GoF design patterns — task X-021

## 03 Databases and storage
- ⬜ [C] 03.01 Aurora PostgreSQL — task X-010
  - Doc `docs/03.01.aurora-postgres.md` · Java `com.lc.x.x03_01_aurora` · Python `app/x03_01_aurora/`
  - Terraform ✅ `terraform/03.01.aurora-postgres.tf` (writer + reader, Serverless v2, IAM auth)
- ⬜ [C] 03.02 DynamoDB — task X-011
  - Doc `docs/03.02.dynamodb.md` · Java `x03_02_dynamodb` · Python `app/x03_02_dynamodb/`
  - Terraform ✅ `terraform/03.02.dynamodb.tf` (`x-orders` PK/SK + GSI1, TTL, streams; `x-idempotency`)
- ⬜ [C] 03.03 S3 — task X-012
  - Doc `docs/03.03.s3.md` · Java `x03_03_s3` · Python `app/x03_03_s3/`
  - Terraform ✅ `terraform/03.03.s3.tf` (lake bucket with lifecycle; Athena results bucket)

## 04 Analytics and warehouses
- ⬜ [C] 04.01 Athena — task X-013
  - Doc `docs/04.01.athena.md` · Java `x04_01_athena` · Python `app/x04_01_athena/`
  - Terraform ✅ `terraform/04.01.athena.tf` (Glue table `clicks`, partition projection, workgroup `x-wg`)
- ⬜ [C] 04.02 Redshift — task X-014
  - Doc `docs/04.02.redshift.md` · Java `x04_02_redshift` · Python `app/x04_02_redshift/`
  - Terraform ✅ `terraform/04.02.redshift.tf` (Serverless `x-ns` / `x-dw`, COPY role)

## 05 Streaming and messaging
- ⬜ [C] 05.01 Kinesis + Firehose to S3 — task X-015
  - Doc `docs/05.01.kinesis.md` · Java `x05_01_kinesis` · Python `app/x05_01_kinesis/`
  - Terraform ✅ `terraform/05.01.kinesis.tf` (stream `x-clicks`, Firehose to `raw/clicks/dt=`)
- ⬜ [C] 05.02 Kafka (MSK) — task X-016
  - Doc `docs/05.02.kafka.md` · Java `x05_02_kafka` · Python `app/x05_02_kafka/`
  - Terraform ✅ `terraform/05.02.kafka-msk.tf` (3 brokers, IAM auth, RF 3, min.insync 2)
- ⬜ [C] 05.03 Flink windows — task X-024
- ⬜ [C] 05.04 SQS / SNS — task X-025

## 06 Frameworks
- ⬜ [C] 06.01 Spring IoC — task X-022
- ⬜ [C] 06.02 FastAPI DI — task X-023

## 07 Distributed systems concepts
- ⬜ 07.01 Tech-choice guide — task X-026

## 08 AI and agents
- ⬜ [C] 08.01 Bedrock basics — task X-027
- ⬜ [C] 08.02 Step Functions + Bedrock — task X-028
- ⬜ [C] 08.03 Agent SDKs side by side — task X-029

## Change log
- 2026-11-13 · Created: rules, manifest, task queue, Terraform foundation + 7 component files
