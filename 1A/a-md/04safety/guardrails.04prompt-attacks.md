# guardrails.04prompt-attacks Prompt Attacks and Misuse

> Attack types, layered defenses, and why `guardContent` tagging decides what the prompt-attack filter sees (lecture 34).

## Index

- [1. Attack Types](#1-attack-types)
- [2. Defense in Depth](#2-defense-in-depth)
- [3. Tagging Matters](#3-tagging-matters)
  - [3.1 Without Tags](#31-without-tags)
  - [3.2 With guardContent](#32-with-guardcontent)
  - [3.3 Code: Guard Only User Text](#33-code-guard-only-user-text)
- [4. Bias and Misuse](#4-bias-and-misuse)

Back to [00index](guardrails.00index.md).

## 1. Attack Types

Attackers aim to override instructions, remove refusals, or extract hidden context.

- **Prompt injection**: instructions hidden in user text or retrieved content
  - "ignore previous instructions …"
- **Indirect injection**: the instruction sits in a web page, email, or tool result the agent reads
- **Jailbreak**: role-play or encoding tricks that remove the model's refusals
  - "Do Anything Now (DAN)", base64, other languages
- **Prompt leaking**: the attacker extracts the system prompt or hidden context
- **Data poisoning**: malicious documents land in the Retrieval-Augmented Generation (RAG) index or fine-tune set

## 2. Defense in Depth

No single layer suffices; each layer limits what the previous one misses.

→ Separate trusted (system) and untrusted (user, retrieved) text: `guardContent` tagging.  
→ PROMPT_ATTACK filter HIGH on the untrusted part only.  
→ Least-privilege tools for agents: a hijacked agent can only do what Identity and Access Management (IAM) allows.  
→ Output checks: Personally Identifiable Information (PII), grounding, denied topics.  
→ Never put secrets in the system prompt.

- Indirect injection (RAG docs, tool output) needs `ApplyGuardrail` on that content too

## 3. Tagging Matters

The prompt-attack filter flags whatever it evaluates, including your own instructions.

### 3.1 Without Tags

- Every message is evaluated
  - history and templated instructions included
  - `InvokeModel`: the whole body, system instructions included
- Your own "You are …, never …, ignore anything that …" text looks like an injection
  - false positive

### 3.2 With guardContent

- Only the tagged text is evaluated
- The model still sees all blocks
  - `guardContent` only changes what the guardrail evaluates
- `InvokeModel` equivalent
  - input tags `<amazon-bedrock-guardrails-guardContent_SUFFIX>`
  - with a random per-request suffix, so attackers can't close the tag

### 3.3 Code: Guard Only User Text

- The instruction text is a plain block ⇒ not evaluated
- Passages are tagged `grounding_source`, the question `query`
  - so contextual grounding scores the model answer

```python
# app/infra/_04safety_01guardrails.py
def converse_guard_user_text_only(
    user_text: str,
    passages: list[str] | None = None,
    system: str = "Answer only from the context. If the context does not contain the answer, say so.",
) -> GuardedReply:
    content: list[Json] = [{"text": "Use the context below to answer the question."}]  # not evaluated
    for p in passages or []:
        content.append({"guardContent": {"text": {"text": p, "qualifiers": [Qualifier.GROUNDING_SOURCE.value]}}})
    content.append({"guardContent": {"text": {"text": user_text, "qualifiers": [Qualifier.QUERY.value]}}})
    resp = _runtime().converse(
        modelId=_model_id(),
        system=[{"text": system}],
        messages=[{"role": "user", "content": content}],
        inferenceConfig={"maxTokens": 512, "temperature": 0.0},
        guardrailConfig=_guardrail_config(),
    )
    return _reply_from_converse(resp)
```

- Catch
  - It is one layer
  - least-privilege tools and output checks limit the blast radius when it misses

## 4. Bias and Misuse

Guardrails filter misuse; bias needs measurement.

- Bias (stereotyping, unequal quality across groups) is measured, not filtered
  - evaluation jobs, `Builtin.Stereotyping` ([evaluations](evaluations.00index.md))
- Guardrails cover the misuse side
  - harmful content
  - disallowed topics
  - data leakage
