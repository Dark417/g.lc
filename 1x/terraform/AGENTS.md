# 1x/terraform — Agent Rules

> Declares every AWS resource the 1x code talks to, as one root stack of per-component modules.

- Scope: `1x/terraform/`
- **Never run** `terraform plan` or `apply`
  - Allowed: `terraform fmt`, `terraform init -backend=false`, `terraform validate`

## Index

- [1. Layout](#1-layout)
- [2. Naming](#2-naming)
- [3. Env Model](#3-env-model)
- [4. Module File Roles](#4-module-file-roles)
- [5. Wiring](#5-wiring)
- [6. Security Defaults](#6-security-defaults)
- [7. Checks](#7-checks)

## 1. Layout

One root module at `terraform/`; each component is a child module under `modules/`.

```text
terraform/
  versions.tf   backend.tf   providers.tf   variables.tf
  locals.tf     main.tf      outputs.tf
  envs/         <env>.tfvars + <env>.backend.hcl  (local dev uat prod)
  modules/      base_network  base_kms  base_iam
                03db_01aurora  03db_02dynamodb  03db_03s3
                05analytics_01athena  05analytics_02redshift
                02messaging_01kinesis  02messaging_02kafka
```

| Root file | Holds |
| --- | --- |
| `versions.tf` | `required_version`, AWS provider pin |
| `backend.tf` | Empty `backend "s3" {}`; values from `envs/<env>.backend.hcl` |
| `providers.tf` | AWS provider, `default_tags`, LocalStack endpoints when `use_localstack` |
| `variables.tf` / `locals.tf` | Env identity, per-component knobs / prefix, tags, shared data sources |
| `main.tf` / `outputs.tf` | One module block per component / names + ARNs the code needs |

## 2. Naming

Names follow the repo spec: group + component, two digits each.

- **Module dir**: `modules/<GG><group>_<CC><name>/`
  - `modules/03db_01aurora/`, `modules/02messaging_02kafka/`
- **Module block label**: leading underscore, since labels can't start with a digit
  - `module "_03db_01aurora"`
- **Component tag**: md name, `Component = "03db.01aurora"`
  - Set once as `local.component` in each module's `main.tf`
- **Terraform address**: `aws_<type>.<short_role>` in snake_case
  - `aws_rds_cluster.aurora`, `aws_dynamodb_table.orders`
- **AWS name**: `${var.prefix}-<thing>`, with `prefix = "<project_prefix>-<env>"`
  - `x-dev-orders`, `x-prod-clicks`, `x-uat-aurora`
  - Java / Python config must use the env-qualified names from `outputs.tf`
  - Glue names swap hyphens for underscores: `x_dev_lake`

## 3. Env Model

Four envs share one code path; only `envs/<env>.tfvars` differs.

| Env | Account (mock) | VPC CIDR | Shape |
| --- | --- | --- | --- |
| `local` | `000000000000` | `10.10.0.0/16` | Smallest, LocalStack, no deletion protection |
| `dev` | `111111111111` | `10.20.0.0/16` | Small, 2 AZs, no deletion protection |
| `uat` | `222222222222` | `10.30.0.0/16` | Prod-like, 3 AZs, protected |
| `prod` | `333333333333` | `10.40.0.0/16` | Biggest, longest retention, multi-AZ, protected |

- Every value in `envs/` is fake; never put real account ids or secrets there
- Add a knob in three places
  1. Root `variables.tf`, default = the safe original value
  2. Module `variables.tf`, passed through in root `main.tf`
  3. All four `envs/*.tfvars`
- `allowed_account_ids = [var.aws_account_id]` stops a wrong-account run

## 4. Module File Roles

Each module keeps the same files with fixed jobs.

- `main.tf`
  - Header comment: what it creates, which code uses it, per-env knobs
  - `locals` (component tag, derived values), then resources, core first
- `iam.tf`
  - All IAM for that component in one file
  - App-role policy (least privilege, this component's ARNs only)
  - Service roles the component needs (Firehose, Redshift COPY/UNLOAD)
  - No `iam.tf` when the component grants nothing (`base_network`)
- `variables.tf`: wiring inputs first, then knobs with safe defaults
- `outputs.tf`: names, ARNs, endpoints other modules or the code need
- Comment every non-default knob: what it trades, when to change it

## 5. Wiring

Modules never reference each other directly; root `main.tf` passes outputs to inputs.

- Foundation first, consumed by every component
  - `base_network`: VPC, private subnets, app security group
  - `base_iam`: the app role; others attach policies via `app_role_id`
  - `base_kms`: the shared CMK, plus the app's `kms:*` policy
- Component-to-component links also go through root
  - `03db_03s3` lake bucket → Athena table, Redshift COPY role, Firehose
- Dependency outside this repo (an existing VPC, a shared key)
  - Pretend it exists: `data` source or variable, comment `# assumed to exist`

## 6. Security Defaults

Every component keeps these, in every env.

- Encrypt at rest with the shared CMK (`var.kms_key_arn`)
- No public access; private subnets only
- Secrets managed by AWS (`manage_master_user_password = true`)
  - Never in variables, tfvars, or code
- IAM: one app policy per component, scoped to that component's ARNs
- Deletion protection and long retention are on for `uat` and `prod`

## 7. Checks

Run inside `1x/terraform/`.

→ `terraform fmt -recursive`  
→ `terraform init -backend=false`  
→ `terraform validate`  
⇒ If terraform is not installed, say so; don't claim it passed

- `.terraform/` stays untracked (root `.gitignore`); `.terraform.lock.hcl` is committed
