# 01bedrock.03prompt-management Interview Questions

> Prompt Management interview questions with L4 answers and L5 extras.

## Index

- [1. Core Questions](#1-core-questions)
  - [1.1 Why Manage Prompts Outside Code](#11-why-manage-prompts-outside-code)
  - [1.2 Calling A Managed Prompt](#12-calling-a-managed-prompt)
  - [1.3 Variant vs Version](#13-variant-vs-version)
  - [1.4 Safe Rollout](#14-safe-rollout)
- [2. L5-Only Questions](#2-l5-only-questions)
  - [2.1 Prompt Management vs Langfuse](#21-prompt-management-vs-langfuse)

Back to [00index](01bedrock.03prompt-management.00index.md).

---

## 1. Core Questions

Most-asked first.

### 1.1 Why Manage Prompts Outside Code

**Q1:** Why manage prompts outside the code?

**L4 answer**

- Prompts change more often than code
- Versions give history and rollback
- Identity and Access Management (IAM) controls who edits

**L5 extra**

- The version Amazon Resource Name (ARN) becomes a deploy artifact referenced from config
- Pair it with an eval gate
- Keep the source in git for review
- Trade-off: one more runtime dependency vs faster, safer iteration

### 1.2 Calling A Managed Prompt

**Q2:** How do you call a managed prompt from code?

**L4 answer**

- Converse with `modelId` = prompt version ARN and `promptVariables`

**L5 extra**

- The prompt supplies model, system, and inference config
  - You cannot override them in that call
- Only the default variant runs

  ⇒ local rendering for A/B

- IAM: render permission on the prompt plus invoke on the underlying model

### 1.3 Variant vs Version

**Q3:** What is the difference between a variant and a version?

**L4 answer**

- **Variant**: an alternative template/model inside one prompt
- **Version**: immutable snapshot of the whole prompt (all variants)

**L5 extra**

- Variants are for comparison during design
- Versions are for release
- Changing the default variant needs a new version to reach production

### 1.4 Safe Rollout

**Q4:** How would you roll out a prompt change safely?

**L4 answer**

→ edit DRAFT, test  
→ create a version  
→ update config to the new ARN  
→ roll back by restoring the old ARN

**L5 extra**

- Eval the new version on a golden set before promotion
- Canary: route a share of traffic to the new version in code
  - Compare metrics
- Log the prompt ARN with each invocation (`requestMetadata`)
  - Attributes regressions to a version

## 2. L5-Only Questions

Depth, scale, and design ownership.

### 2.1 Prompt Management vs Langfuse

**L5-only Q5:** Bedrock Prompt Management vs Langfuse for a 20-team platform?

**L5 answer**

- Bedrock-only models + strict Amazon Web Services (AWS) data boundary
  - → Prompt Management
  - Plus an internal wrapper for A/B and logging
- Several model vendors + heavy experimentation
  - → Langfuse
  - Self-hosted on AWS keeps data in the account
- Either way
  - git as source of truth
  - eval gate
  - version pinned per service
- Trade-off: native IAM and no extra service vs labels, analytics, tracing linked to prompt versions
