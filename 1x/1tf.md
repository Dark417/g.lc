# 1tf — Terraform Guide (1x)

> Checks, environments, and module index for the 1x Terraform project.

- Project: `terraform/` — base files + `envs/` + `modules/`, never applied
- Rules: [terraform/AGENTS.md](terraform/AGENTS.md)

## Index

- [1. Checks](#1-checks)
- [2. Environments](#2-environments)
- [3. Modules](#3-modules)

## 1. Checks

The project must format and validate cleanly; it is never planned or applied.

- `cd 1x/terraform && terraform fmt -check -recursive && terraform init -backend=false && terraform validate`
- Never `plan` / `apply`
- If ever applied: `terraform init -backend-config=envs/<env>.backend.hcl` → `terraform plan -var-file=envs/<env>.tfvars`

## 2. Environments

All values are mock; envs differ only through `envs/<env>.tfvars`.

| Env | Account | VPC | Shape |
| --- | --- | --- | --- |
| `local` | `000000000000` | `10.10.0.0/16` | LocalStack, smallest, no protection |
| `dev` | `111111111111` | `10.20.0.0/16` | small, short retention |
| `uat` | `222222222222` | `10.30.0.0/16` | 3 AZ, deletion protection |
| `prod` | `333333333333` | `10.40.0.0/16` | 3 AZ, largest, 35-day backups, 365-day logs |

- AWS names carry the env: `x-<env>-orders`, `x-<env>-clicks`; Glue db `x_<env>_lake`

## 3. Modules

One module per component; `iam.tf` holds that component's IAM.

| Module | Creates | Status |
| --- | --- | --- |
| `base_network` | VPC, private subnets, app SG, gateway endpoints | ✅ |
| `base_kms` | CMK `alias/x-<env>-data` + app key policy | ✅ |
| `base_iam` | shared app role `x-<env>-app` | ✅ |
| `03db_01aurora` | Aurora PG Serverless v2, writer + readers, log group | ✅ |
| `03db_02dynamodb` | `orders` (PK/SK, GSI1, TTL, streams), `idempotency` | ✅ |

| Module | Creates | Status |
| --- | --- | --- |
| `03db_03s3` | lake + Athena results buckets, lifecycle, app policy | ✅ |
| `03db_04mongodb` | DocumentDB cluster + instances, TLS param group, app access | ✅ |
| `05analytics_01athena` | Glue db/table `clicks`, workgroup `x-<env>-wg` | ✅ |
| `05analytics_02redshift` | Serverless namespace + workgroup, COPY role | ✅ |
| `02messaging_01kinesis` | stream `clicks`, 2 Firehose streams to the lake | ✅ |
| `02messaging_02kafka` | MSK cluster, IAM auth, RF = min(3, brokers) | ✅ |

- Restructured 2026-11-13 (X-040); validated with Terraform 1.10.4, aws provider 5.100.0
