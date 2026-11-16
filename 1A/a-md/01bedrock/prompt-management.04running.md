# prompt-management Running A Managed Prompt

> Three ways to run a prompt: Converse with its Amazon Resource Name (ARN), render locally, or inside a Flow or Agent.

## Index

- [1. Three Options](#1-three-options)
- [2. Option A: Converse With The Prompt ARN](#2-option-a-converse-with-the-prompt-arn)
- [3. Option B: Render Locally](#3-option-b-render-locally)
  - [3.1 Strict Rendering](#31-strict-rendering)
  - [3.2 Calling The Chosen Variant](#32-calling-the-chosen-variant)
- [4. Option C: Flows And Agents](#4-option-c-flows-and-agents)

Back to [00index](prompt-management.00index.md).

---

## 1. Three Options

Pick by whether you need the prompt's settings or your own control.

| Option | How | Variants | Your system / guardrails |
|---|---|---|---|
| A | Converse, `modelId` = prompt ARN | Default only | Not allowed |
| B | `GetPrompt` → render → Converse | Any (A/B) | Yes |
| C | Flow prompt node / Agent override | Per node | Per resource |

Pick: A for the production default path, unless you need A/B or extra guardrails → B.

## 2. Option A: Converse With The Prompt ARN

Bedrock renders the default variant and uses its model and settings.

- `modelId` = prompt ARN
  - Version ARN in production
- Pass `promptVariables`
- `messages` are appended after the prompt's own messages (CHAT) where allowed
- You cannot also send these fields (Converse Application Programming Interface (API) reference: they come from the prompt)
  - `system`
  - `inferenceConfig`
  - `toolConfig`
  - `additionalModelRequestFields`
- Runs the default variant
- Identity and Access Management (IAM)
  - `bedrock:RenderPrompt` on the prompt
  - `bedrock:InvokeModel` on the variant's model
  - See the Terraform comment on uncertainty

```python
# app/infra/_01bedrock_03prompt_management.py
def converse_managed_prompt(self, prompt_version_arn: str, variables: dict[str, str]) -> dict[str, Any]:
    if ":" not in prompt_version_arn.rsplit("/", 1)[-1]:  # base ARN = DRAFT
        raise ValueError("pin a version ARN (<prompt_arn>:<n>); DRAFT is not for production")
    resp = self.runtime.converse(
        modelId=prompt_version_arn,
        promptVariables={k: {"text": v} for k, v in variables.items()},  # PromptVariableValues = {"text": ...}
        # no system / inferenceConfig / toolConfig: they come from the prompt
    )
    return {
        "text": "".join(b.get("text", "") for b in resp["output"]["message"]["content"]),
        "stop_reason": resp["stopReason"],
        "usage": resp.get("usage", {}),
    }
```

```python
# app/api/_01bedrock_03prompt_management.py
@router.post("/run")
def run(body: RunRequest, showcase: Showcase) -> dict[str, Any]:
    arn = body.prompt_version_arn or showcase.settings.prompt_version_arn  # production path
    try:
        return showcase.converse_managed_prompt(arn, body.variables)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
```

- Catch: a DRAFT ARN (no `:n`) is for testing only.
- Catch: sending `system` or `inferenceConfig` here ⇒ `ValidationException`.

## 3. Option B: Render Locally

`GetPrompt`, render any variant yourself, then call its model.

- Any variant (A/B)
- Your own system prompt and guardrails
- Extra messages
- Cache `GetPrompt` results
  - They are immutable per version

### 3.1 Strict Rendering

- A missing value raises instead of sending a literal `{{name}}` to the model.
- An undeclared value raises too.
- Values are inserted verbatim.

```python
# app/domain/_01bedrock_03prompt_management.py
_VAR = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}")

def render_text(template: str, values: dict[str, str]) -> str:
    missing = set(_VAR.findall(template)) - values.keys()
    if missing:  # never send a literal {{name}} to the model
        raise MissingVariableError(f"missing variables: {sorted(missing)}")
    return _VAR.sub(lambda m: values[m.group(1)], template)


def render_variant(variant: PromptVariant, values: dict[str, str]) -> tuple[str, list[dict[str, Any]]]:
    """TEXT or CHAT variant -> (system text, Converse messages)."""
    undeclared = set(values) - set(variant.input_variables)
    if undeclared:
        raise MissingVariableError(f"not declared in variant {variant.name}: {sorted(undeclared)}")
    if variant.template_type == "TEXT":
        return "", [{"role": "user", "content": [{"text": render_text(variant.text, values)}]}]
    messages = [
        {"role": m["role"], "content": [{"text": render_text(b["text"], values)} for b in m["content"] if "text" in b]}
        for m in variant.messages
    ]
    return render_text(variant.system, values), messages
```

- Catch: values are inserted verbatim.
  - Fence untrusted text first (`fence_untrusted` in [prompt-engineering](prompt-engineering.00index.md)).

### 3.2 Calling The Chosen Variant

```python
# app/infra/_01bedrock_03prompt_management.py
def converse_rendered_variant(self, prompt_id: str, version: str, variant: str,
                              variables: dict[str, str]) -> dict[str, Any]:
    chosen = self.get_prompt(prompt_id, version).variant(variant)  # any variant, not only the default
    system, messages = render_variant(chosen, variables)
    inf = chosen.inference
    kwargs: dict[str, Any] = {
        "modelId": chosen.model_id,  # the variant's own model
        "messages": messages,
        "inferenceConfig": {k: inf[k] for k in ("maxTokens", "temperature", "topP", "stopSequences")
                            if inf.get(k) not in (None, [])},
    }
    if system:
        kwargs["system"] = [{"text": system}]  # you may add your own guardrail text here
    resp = self.runtime.converse(**kwargs)
    return {"variant": chosen.name,
            "text": "".join(b.get("text", "") for b in resp["output"]["message"]["content"]),
            "stop_reason": resp["stopReason"]}
```

- Catch: you now own rendering rules (strict variables).
- Catch: cache `GetPrompt` per version, or each call adds a control-plane round trip.

## 4. Option C: Flows And Agents

- Prompt node in a Flow
  - See [prompt-flows](prompt-flows.00index.md)
- An Agent's prompt override
  - Agents live in 06agents
