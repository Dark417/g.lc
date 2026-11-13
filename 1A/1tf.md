# 1tf — Terraform guide (1A)

- Root: `terraform/` — one flat root, one component per file, never applied
- Rules: [terraform/AGENTS.md](terraform/AGENTS.md)

## Index
- [1. Checks](#1-checks)
- [2. Files](#2-files)

## 1. Checks
- `cd 1A/terraform && terraform fmt -check && terraform init -backend=false && terraform validate`
- Never `plan` / `apply`
- Apply order if ever applied: `00.*` → `02.02` collection → vector index (Python `create_kb_index`) → `02.04` knowledge base

## 2. Files
| File | Creates | Status |
|---|---|---|
| `00.00.providers.tf` | provider (aws ~> 6.70), variables, locals | ✅ |
| `00.01.network.tf` | VPC, private subnets, app SG, gateway endpoints, `bedrock-runtime` endpoint | ✅ |
| `00.02.kms.tf` | CMK `alias/a-data` | ✅ |
| `00.03.iam.tf` | app role `a-app` | ✅ |
| `00.04.billing-alarm.tf` | SNS `a-alerts`, billing alarm | ✅ |
| `00.05.data-bucket.tf` | shared bucket `a-ai-data-<account>` | ✅ |
| `01.01.bedrock-converse.tf` | model invoke policy | 🔧 |
| `01.02.model-customization.tf` | customization service role | 🔧 |
| `01.03.prompt-management.tf` | managed prompt | 🔧 |
| `01.04.prompt-flows.tf` | flow + execution role | 🔧 |
| `02.02.opensearch-serverless.tf` | AOSS collection + policies, KB role | 🔧 |
| `02.04.knowledge-bases.tf` | knowledge base + S3 data source | 🔧 |
| `03.01.data-automation.tf` | BDA blueprint + project | 🔧 |
| `03.02.glue-data-quality.tf` | catalog table + DQ ruleset | 🔧 |
| `03.03.transcribe.tf` | vocabulary + filter | 🔧 |
| `03.04.comprehend.tf` | Comprehend policy | 🔧 |
| `04.01.guardrails.tf` | guardrail + version | 🔧 |
| `04.02.pii-redaction.tf` | Comprehend async role (if needed) | 🔧 |
| `04.03.evaluations.tf` | evaluation service role | 🔧 |
| `05.01.observability.tf` | invocation logging, log group, alarms | 🔧 |

- Foundation validated 2026-11-13 with Terraform 1.9.8, aws provider 6.73.0
