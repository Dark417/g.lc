# 1A/terraform — Agent Rules

- Scope: `1A/terraform/`
- Purpose: declare every AWS resource the 1A code talks to, so the code has a real shape to point at
- **Never run** `terraform plan` or `apply`
  - Allowed: `terraform fmt`, `terraform init -backend=false`, `terraform validate`

## Index
- [1. Layout](#1-layout)
- [2. File naming](#2-file-naming)
- [3. Dependencies and the 00 foundation](#3-dependencies-and-the-00-foundation)
- [4. Resource naming](#4-resource-naming)
- [5. Inside one file](#5-inside-one-file)
- [6. Security defaults](#6-security-defaults)
- [7. Checks](#7-checks)

## 1. Layout
- One Terraform root module, flat
  - Terraform loads every `*.tf` in the folder, so one component per file still forms one stack
- One file = one component (the user's "one module one file")
  - Not Terraform child modules: a flat root is simpler to read and to diff
  - Switch to `modules/<name>/` only if a component must be instantiated twice

## 2. File naming
- `GG.CC.<name>.tf`, same number as the doc and the code (`1A/AGENTS.md` §3)
  - `00.00.providers.tf`, `04.01.guardrails.tf`, `02.02.opensearch-serverless.tf`
- Lowercase, hyphens

## 3. Dependencies and the 00 foundation
- Plain idea: anything two or more components need is created first, in `00.*`
  - `00.00.providers.tf`: terraform block, AWS provider, variables, locals, default tags
  - `00.01.network.tf`: VPC, private subnets, security groups
  - `00.02.kms.tf`: one customer-managed key for all data at rest
  - `00.03.iam.tf`: the app role that Java / Python assume
- A component file references foundation by name
  - `aws_kms_key.main.arn`, `aws_subnet.private[*].id`, `aws_iam_role.app.name`
- Dependency outside this repo (an existing VPC, a shared KMS key)
  - Pretend it exists: use a `data` source or a variable, with a comment `# assumed to exist`
- Component-to-component links are allowed (the knowledge base in `02.04` uses the collection in `02.02`)

## 4. Resource naming
- Terraform address: `aws_<type>.<short_role>` in snake_case
  - `aws_bedrock_guardrail.main`, `aws_opensearchserverless_collection.vectors`
- AWS name: `${local.prefix}-<thing>`, where `local.prefix = "a"` by default
  - `a-guardrail`, `a-kb`, `a-vectors`
  - The Java / Python config uses these exact names
- Every resource gets tags through provider `default_tags`; add `Component = "GG.CC"` per resource

## 5. Inside one file
- Order, with banner comments
  1. Header comment: what it creates, which code uses it
  2. Locals for the component
  3. Resources, core first, extras after
  4. IAM policy for the app role (least privilege, this component only)
  5. Outputs: names, ARNs, endpoints the code needs
- Comment every non-default knob: what it trades, when to change it

## 6. Security defaults
- Encrypt at rest with `aws_kms_key.main`
- No public access; private subnets only
- Secrets: managed by AWS (`manage_master_user_password = true`), never in variables or code
- IAM: one policy per component, scoped to that component's ARNs

## 7. Checks
→ `terraform fmt -recursive`  
→ `terraform init -backend=false`  
→ `terraform validate`  
⇒ If terraform is not installed in the environment, say so; don't claim it passed
