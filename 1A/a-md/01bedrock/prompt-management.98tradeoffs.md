# prompt-management Trade-Offs

> When to use Prompt Management, the knobs that keep it safe, how it compares, and how it fails.

## Index

- [1. When To Use / Not](#1-when-to-use--not)
- [2. Knobs And Best Practices](#2-knobs-and-best-practices)
- [3. Comparison](#3-comparison)
- [4. Failure Modes](#4-failure-modes)

Back to [00index](prompt-management.00index.md).

---

## 1. When To Use / Not

Use it when prompt ownership and change rate outgrow code deploys.

- Use when
  - Several teams or non-developers edit prompts
  - You need version history, rollback, and Identity and Access Management (IAM) on prompts
  - You already run on Bedrock (Converse, Flows, Agents)
- Avoid when
  - One small service, prompts change with code anyway

  ⇒ git is enough

  - Multi-cloud or multi-vendor model routing

  ⇒ a vendor-neutral prompt store

  - You need built-in A/B traffic splitting and analytics

  ⇒ a Large Language Model (LLM)-ops platform

## 2. Knobs And Best Practices

Each rule names the failure it prevents.

- Pin version Amazon Resource Names (ARNs) in config
  - Prevents: DRAFT edits changing production behavior
- One owner per prompt
- Tags for team and cost
- Name variables clearly
- Declare every variable used in the template
  - Prevents: unfilled `{{var}}` reaching the model
- Keep the template in git too (Terraform or a seed script)
  - Prevents: console-only changes with no review
- Evaluate each new version on a golden set before promotion
  - See [evaluations](../04safety/evaluations.00index.md)
- Encrypt with the Customer Managed Key (CMK) (`customerEncryptionKeyArn`)
- Cache `GetPrompt` per version when rendering locally
- Use `clientToken` on create calls
  - Prevents: duplicate prompts or versions on retries

## 3. Comparison

Three ways to store and serve prompts.

| Option | What it is | Strength | Weakness | Choose when |
|---|---|---|---|---|
| Bedrock Prompt Management | Amazon Web Services (AWS) resource: variants, versions, IAM; runs in Converse/Flows/Agents | Native to Bedrock; immutable versions; no extra vendor; console compare | Bedrock-only; no built-in traffic split or analytics; default-variant only in Converse | AWS-native stack, Bedrock models |
| Prompts in git (files + code) | Templates in the repo, rendered by the app | Pull Request (PR) review, Continuous Integration (CI) evals, zero extra service | Change = deploy; non-devs blocked; no runtime lookup | Small team, prompts change with code |
| LangSmith / Langfuse prompt hub | LLM-ops platform prompt registry with labels | Labels (production/staging), tracing linked to prompt versions, A/B analytics, vendor-neutral | Another vendor or self-hosted service; data leaves AWS (Software as a Service (SaaS)) | Multi-model, heavy experimentation, need tracing + evals together |

- Deciding variable
  - Who edits prompts and how often
  - Whether you need analytics tied to versions

Pick: Bedrock Prompt Management for Bedrock-only apps (templates mirrored in git), unless you need cross-vendor experimentation and tracing → Langfuse / LangSmith.

## 4. Failure Modes

Most failures come from unpinned versions, variables, or field rules.

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Production uses DRAFT | Config holds the base ARN, not `:N` | Behavior changes without deploy | Pin version ARN; alarm on base-ARN use |
| Missing variable | Template uses `{{x}}` not passed | Literal `{{x}}` in model input / `ValidationException` | Declare `inputVariables`; validate before calling |
| Rejected fields | Sending `system` or `inferenceConfig` with a prompt ARN | `ValidationException` | Move them into the prompt variant |
| Access denied | Missing `RenderPrompt` / `InvokeModel` on the variant model | `AccessDeniedException` | Grant both (and Key Management Service (KMS) on the CMK) |

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Variant ignored | Expecting Converse to run a non-default variant | Output matches default | Render locally (`GetPrompt`) or change `defaultVariant` + new version |
| Untracked console edits | Edits outside git | Drift between Terraform and service | Terraform owns prompts; `plan` shows drift |
| Model retired | Variant pinned to a legacy model | `ValidationException` / lifecycle alarm | New version with new model; eval first |
