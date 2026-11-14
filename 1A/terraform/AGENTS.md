# 1A/terraform — Agent Rules

> Scoped rules for the 1A Terraform project: one root, one module per component, four envs.

- Scope: `1A/terraform/`
- Purpose: declare every AWS resource the 1A code talks to
  - The code gets a real shape to point at
- **Never run** `terraform plan` or `apply`
  - Allowed: `terraform fmt`, `terraform init -backend=false`, `terraform validate`

## Index

- [1. Layout](#1-layout)
- [2. Naming](#2-naming)
- [3. Env Model](#3-env-model)
- [4. Root Files](#4-root-files)
- [5. Module Files](#5-module-files)
- [6. Wiring And Dependencies](#6-wiring-and-dependencies)
- [7. Security Defaults](#7-security-defaults)
- [8. Checks](#8-checks)

## 1. Layout

One root module calls one child module per component.

```text
terraform/
  versions.tf backend.tf providers.tf variables.tf locals.tf main.tf outputs.tf
  envs/      local|dev|uat|prod .tfvars + .backend.hcl
  modules/   base_network/ ... 05ops_01observability/
             each: main.tf iam.tf variables.tf outputs.tf
  .terraform.lock.hcl   committed; keep it
```

- One module = one component of `1A/AGENTS.md` numbering
  - Same group + component as the doc and the code
- Foundation modules `base_*` hold anything two or more components need

## 2. Naming

Names follow the shared spec: dots in Markdown, underscores in code.

| Thing | Pattern | Example |
|---|---|---|
| Module dir | `modules/<group>_<component>/` | `modules/04safety_01guardrails/` |
| Module block label | `_<dir name>` (labels can't start with a digit) | `module "_04safety_01guardrails"` |
| Resource address | `aws_<type>.<short_role>`, snake_case | `aws_bedrock_guardrail.main` |
| AWS name | `${var.prefix}-<thing>` | `a-dev-guardrail`, `a-prod-kb` |
| Component tag | `Component = "<dir name>"` | `Component = "02rag_02opensearch"` |

- Multi-word component names use underscores in dirs
  - `01bedrock_03prompt_management`, `04safety_02pii_redaction`
- `local.prefix = "<project_prefix>-<env>"`
  - The old flat stack used `a-<thing>`; names now carry the env
  - The Java / Python config reads names from outputs, per env
- Every resource gets `default_tags` (Project, Env, Managed) from the provider

## 3. Env Model

Four envs share one code path; only tfvars and backend config differ.

| Env | Account (mock) | VPC CIDR | AZs | Notes |
|---|---|---|---|---|
| `local` | `000000000000` | `10.10.0.0/16` | 1 | LocalStack, smallest, `use_localstack = true` |
| `dev` | `111111111111` | `10.20.0.0/16` | 2 | cheap models, short retention |
| `uat` | `222222222222` | `10.30.0.0/16` | 2 | prod-like thresholds, example eval job |
| `prod` | `333333333333` | `10.40.0.0/16` | 3 | standby replicas, 30-day key window, strict alarms |

→ `terraform init -backend-config=envs/<env>.backend.hcl`  
→ `terraform validate` (plan / apply with `-var-file=envs/<env>.tfvars` stay off in this repo)

- All env values are realistic but fake
- `local`: Bedrock and OpenSearch Serverless are not in LocalStack
  - Those modules validate but cannot be created locally
- `providers.tf` sets `allowed_account_ids` for real envs
  - A dev tfvars can never touch the prod account
- New knob ⇒ root `variables.tf` default + a value in all four tfvars

## 4. Root Files

Each root file has one job.

- `versions.tf`: `required_version` + AWS provider pin (`~> 6.70`)
- `backend.tf`: empty `backend "s3" {}`; values come from `envs/*.backend.hcl`
- `providers.tf`: AWS provider, `default_tags`, LocalStack endpoints when `use_localstack`
- `variables.tf`: env, region, prefix, and every per-component knob
  - Grouped under a banner per module
- `locals.tf`: `prefix`, `account_id`, `common_tags`, shared data sources
- `main.tf`: one module block per component, foundation first
- `outputs.tf`: names / ARNs / endpoints the code needs
  - Re-exported from modules; output names unchanged from the flat stack

## 5. Module Files

Every module has the same four files.

- `main.tf`: header comment, locals, component resources (core first, extras after)
  - Header: what it creates, which code uses it, catches, cost
  - Commented-out examples of billing-heavy resources live here
- `iam.tf`: every IAM role and policy of this component, all in one file
  - Service roles (trust + permissions) the AWS service assumes
  - The least-privilege policy attached to the shared app role (`var.app_role_id`)
  - Modules without IAM keep an `iam.tf` with a one-line "none" comment
- `variables.tf`: inputs only, no defaults
  - Foundation ids (`app_role_id`, `kms_key_arn`, `data_bucket_arn`, ...)
  - Per-env knobs passed down from the root
- `outputs.tf`: what the root or other modules need
- Comment every non-default knob: what it trades, when to change it

## 6. Wiring And Dependencies

Modules never reference each other's resources directly; the root wires outputs to inputs.

- Foundation → every component
  - `base_kms` → `kms_key_arn`
  - `base_iam` → `app_role_id` / `app_role_arn`
  - `base_data_bucket` → `bucket` / `bucket_arn`
- Component → component links in `main.tf`
  - `02rag_02opensearch` → `02rag_04knowledge_bases`: collection ARN + KB role
  - `02rag_04knowledge_bases` → `04safety_03evaluations`: knowledge base id
  - `base_billing_alarm` → `05ops_01observability`: alerts topic
- Ordering that data flow can't express ⇒ module-level `depends_on`
  - Example: the KB module waits for the AOSS data-access policy
- Dependency outside this repo (existing VPC, shared key)
  - Use a `data` source or a variable with `# assumed to exist`
- `count` / `for_each` only on known values (flags), never on another module's ids

## 7. Security Defaults

These defaults carry over from the flat stack.

- Encrypt at rest with the shared CMK from `base_kms`
  - Exception: a service that needs a key-policy grant gets its own small key
  - Example: the `05ops_01observability` log-group key
- No public access
  - Private subnets only
  - S3 public access block + `BucketOwnerEnforced`
- Secrets: managed by AWS (`manage_master_user_password = true`)
  - Never in variables, tfvars, or code
- IAM: one policy per component, scoped to that component's ARNs
  - Service roles carry confused-deputy conditions (`aws:SourceAccount`, `aws:SourceArn`)
  - `iam:PassRole` is limited with `iam:PassedToService`
  - `"*"` only for APIs without resource-level permissions, with a comment saying so
- Billing-heavy resources (training, provisioned throughput, endpoints) stay commented out

## 8. Checks

Run inside `1A/terraform/` before finishing any change.

→ `terraform fmt -recursive`  
→ `terraform init -backend=false`  
→ `terraform validate`  
⇒ If terraform is not installed, say so; don't claim it passed

- Never `plan` or `apply`, in any env
- Keep `.terraform.lock.hcl`; never commit `.terraform/`
