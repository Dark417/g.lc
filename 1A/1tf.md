# 1tf — Terraform Guide (1A)

> Checks, environments, and module index for the 1A Terraform project.

- Project: `terraform/` — base files + `envs/` + `modules/`, never applied
- Rules: [terraform/AGENTS.md](terraform/AGENTS.md)

## Index

- [1. Checks](#1-checks)
- [2. Environments](#2-environments)
- [3. Modules](#3-modules)

## 1. Checks

The project must format and validate cleanly; it is never planned or applied.

- `cd 1A/terraform && terraform fmt -check -recursive && terraform init -backend=false && terraform validate`
- Never `plan` / `apply`
- Apply order if ever applied

→ `base_*`  
→ `02rag_02opensearch` collection  
→ vector index (Python `create_kb_index`)  
→ `02rag_04knowledge_bases`

## 2. Environments

All values are mock; envs differ only through `envs/<env>.tfvars`.

| Env | Account | VPC / AZs | Shape |
| --- | --- | --- | --- |
| `local` | `000000000000` | `10.10.0.0/16` / 1 | LocalStack; Bedrock + AOSS only validate |
| `dev` | `111111111111` | `10.20.0.0/16` / 2 | haiku models, $20 alarm, 7-day logs |
| `uat` | `222222222222` | `10.30.0.0/16` / 2 | sonnet generator, eval job on |
| `prod` | `333333333333` | `10.40.0.0/16` / 3 | standby replicas, $1000 alarm, 90-day logs |

- AWS names carry the env: `a-<env>-guardrail`, `a-<env>-ai-data-<account>`, Glue db `a_<env>_ai_data`

## 3. Modules

One module per component; `iam.tf` holds that component's IAM.

| Module | Creates | Status |
| --- | --- | --- |
| `base_network` | VPC, private subnets, app SG, gateway + `bedrock-runtime` endpoints | ✅ |
| `base_kms` | CMK `alias/a-<env>-data` | ✅ |
| `base_iam` | shared app role `a-<env>-app` | ✅ |
| `base_billing_alarm` | SNS alerts + EstimatedCharges alarm | ✅ |
| `base_data_bucket` | shared data bucket, one prefix per component, lifecycle | ✅ |

| Module | Creates | Status |
| --- | --- | --- |
| `01bedrock_01converse` | application inference profile, model invoke policy | ✅ |
| `01bedrock_02customization` | customization job role + policies | ✅ |
| `01bedrock_03prompt_management` | managed prompt, app policy | ✅ |
| `01bedrock_04prompt_flows` | flow, flow execution role | ✅ |
| `02rag_02opensearch` | Serverless vector collection, policies, VPC endpoint, KB role | ✅ |
| `02rag_04knowledge_bases` | knowledge base, S3 data source, app policy | ✅ |

| Module | Creates | Status |
| --- | --- | --- |
| `03data_01data_automation` | BDA project + blueprint, app policy | ✅ |
| `03data_02glue_data_quality` | Glue db/table, DQ ruleset, DQ role | ✅ |
| `03data_03transcribe` | custom vocabulary + vocabulary filter, app policy | ✅ |
| `03data_04comprehend` | app policy | ✅ |
| `04safety_01guardrails` | guardrail + version, app policy | ✅ |
| `04safety_02pii_redaction` | Comprehend PII async job role | ✅ |

| Module | Creates | Status |
| --- | --- | --- |
| `04safety_03evaluations` | eval role, optional example evaluation job | ✅ |
| `05ops_01observability` | invocation logging (log group + KMS key), latency + throttle alarms | ✅ |

- Restructured 2026-11-13 (A-090); validated with Terraform 1.10.4
