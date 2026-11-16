# prompt-flows Security: The Execution Role

> The flow acts as its own Identity and Access Management (IAM) role, so three principals need three different permissions.

## Index

- [1. The Flow Runs As Its Role](#1-the-flow-runs-as-its-role)
  - [1.1 Trust](#11-trust)
  - [1.2 Permissions Per Node](#12-permissions-per-node)
- [2. The Caller](#2-the-caller)
- [3. The Creator](#3-the-creator)

Back to [00index](prompt-flows.00index.md).

---

## 1. The Flow Runs As Its Role

The flow runs as its execution role, not as the caller.

### 1.1 Trust

- Trusted principal: `bedrock.amazonaws.com`
- Conditions
  - `aws:SourceAccount` = this account
  - `aws:SourceArn` = this account's flows
- Purpose: confused-deputy protection

### 1.2 Permissions Per Node

| Node | Action the role needs |
|---|---|
| Prompt | `bedrock:InvokeModel` |
| KnowledgeBase | `bedrock:Retrieve` / `RetrieveAndGenerate` |
| Lambda | `lambda:InvokeFunction` |
| Managed-prompt | `bedrock:GetPrompt` / `RenderPrompt` |
| Encrypted flow | Key Management Service (KMS) |

- Least-privilege execution role per flow
- Missing action ⇒ `dependencyFailedException` / `accessDeniedException` events

```python
# app/config/_01bedrock_04prompt_flows.py
flow_id: str = "FLOW_ID"  # terraform output flow_id (a-flow)
execution_role_arn: str = "arn:aws:iam::ACCOUNT_ID:role/a-flow-role"  # terraform output flow_role_arn
kms_key_arn: str = ""  # terraform output kms_key_arn; empty -> AWS-owned key for flows created in code
```

- Catch: the role itself lives in Terraform (`aws_iam_role.flow`).
  - Python only references its Amazon Resource Name (ARN).

## 2. The Caller

- The caller needs `bedrock:InvokeFlow` on the alias ARN

## 3. The Creator

- Whoever creates or updates a flow needs `iam:PassRole` on the execution role
- Restrict PassRole
  - to that role
  - to `bedrock` only
- Missing ⇒ `AccessDeniedException` on create/update
