# guardrails.08automated-reasoning Automated Reasoning Checks

> Formal-logic checks of an answer against rules extracted from a policy document (lecture 24).

## Index

- [1. Plain Idea](#1-plain-idea)
- [2. Findings](#2-findings)
- [3. Config As Code](#3-config-as-code)
- [4. Limits](#4-limits)

Back to [00index](guardrails.00index.md).

## 1. Plain Idea

Turn written rules into logic, then check each answer mathematically.

→ You upload a policy document (Human Resources (HR) rules, insurance eligibility).  
→ Bedrock extracts variables and logical rules (SMT-style formal logic) into an Automated Reasoning policy.  
→ At runtime the guardrail translates the Question and Answer (Q&A) into the same logic and checks it mathematically.

## 2. Findings

Assessment `automatedReasoningPolicy.findings[]` returns one kind per finding.

- `valid`: claims follow from the rules
- `invalid`: claims contradict the rules
  - returns `contradictingRules`
- `satisfiable`: true under some assumptions, false under others
- `impossible`: premises contradict each other
- `translationAmbiguous`, `tooComplex`, `noTranslations`: could not decide
- Behavior: findings only, no blocking
  - your code decides: rewrite, refuse, or ask a clarifying question

```python
# app/infra/_04safety_01guardrails.py  (inside _assessment_hits)
for finding in a.get("automatedReasoningPolicy", {}).get("findings", []):
    kind = next(iter(finding), "unknown")  # valid | invalid | satisfiable | impossible | translationAmbiguous ...
    hits.append(PolicyHit("automated_reasoning", kind, "NONE", True))  # action NONE: AR never blocks
```

## 3. Config As Code

The policy has its own lifecycle; the guardrail only attaches a version Amazon Resource Name (ARN).

→ `create_automated_reasoning_policy`  
→ build workflow  
→ test cases  
→ `create_automated_reasoning_policy_version`

- Attach on create/update guardrail
  - `automatedReasoningPolicyConfig = {policies: [<policy version ARN>], confidenceThreshold: 0–1}`
- Terraform 6.73: not supported on `aws_bedrock_guardrail`
  - Software Development Kit (SDK) only
  - the Python builder adds it when `A_GUARDRAILS_AR_POLICY_ARN` is set

```python
# app/infra/_04safety_01guardrails.py
def automated_reasoning_policy(policy_arns: tuple[str, ...], confidence_threshold: float) -> Json | None:
    """Attach Automated Reasoning policy VERSION ARNs (SDK only, not in Terraform)."""
    if not policy_arns:
        return None
    return {"policies": list(policy_arns), "confidenceThreshold": confidence_threshold}
```

```python
# app/config/_04safety_01guardrails.py
# Automated Reasoning: ARN of an AR policy VERSION; empty = policy not attached (Terraform can't attach it).
ar_policy_arn: str = ""
ar_confidence_threshold: float = 1.0  # 0..1; findings below it are reported as translationAmbiguous
```

- Catch
  - The policy build workflow (create, build, tests) is not coded; SDK operations only

## 4. Limits

- Only as good as the extracted rules
  - review rules and test cases by hand
- Narrow domains with crisp rules
  - poor fit for open-ended chat
- Region and language availability is limited (check the docs)
- Versus contextual grounding
  - grounding = statistical "is this supported by the passage"
  - Automated Reasoning (AR) = logical "does this follow from the rules"
