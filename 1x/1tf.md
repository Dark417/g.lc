# 1tf — Terraform guide

- Root: `terraform/` — one flat root, one component per file, never applied
- Rules: [terraform/AGENTS.md](terraform/AGENTS.md)

## Index
- [1. Checks](#1-checks)
- [2. Files](#2-files)

## 1. Checks
- `cd 1x/terraform && terraform fmt -check && terraform init -backend=false && terraform validate`
- Never `plan` / `apply`

## 2. Files
| File | Creates | Status |
|---|---|---|
| `00.00.providers.tf` | provider, variables, locals | ✅ |
| `00.01.network.tf` | VPC, private subnets, app SG, gateway endpoints | ✅ |
| `00.02.kms.tf` | CMK `alias/x-data` | ✅ |
| `00.03.iam.tf` | app role `x-app` | ✅ |
| `03.01.aurora-postgres.tf` | Aurora PG cluster, writer + reader | ✅ |
| `03.02.dynamodb.tf` | `x-orders`, `x-idempotency` | ✅ |
| `03.03.s3.tf` | lake + Athena results buckets | ✅ |
| `04.01.athena.tf` | Glue db/table, workgroup `x-wg` | ✅ |
| `04.02.redshift.tf` | Serverless namespace + workgroup `x-dw` | ✅ |
| `05.01.kinesis.tf` | stream `x-clicks`, 2 Firehose streams | ✅ |
| `05.02.kafka-msk.tf` | MSK cluster, IAM auth | ✅ |

- Validated 2026-11-13 with Terraform 1.9.8, aws provider ~> 5.80
