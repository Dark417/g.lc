# prompt-management Prompt, Variant, Template, Variables

> What a prompt resource contains: variants that each fully describe one way to run it.

## Index

- [1. Prompt](#1-prompt)
- [2. Variant](#2-variant)
  - [2.1 Variant Fields](#21-variant-fields)
  - [2.2 TEXT And CHAT](#22-text-and-chat)
- [3. Variables](#3-variables)
- [4. Creating A Prompt In Code](#4-creating-a-prompt-in-code)
- [5. The Domain Model](#5-the-domain-model)

Back to [00index](prompt-management.00index.md).

---

## 1. Prompt

The prompt is the resource that owns everything else.

- **Prompt**: the resource
  - name
  - description
  - Key Management Service (KMS) key
  - tags
  - `defaultVariant`
- `defaultVariant` = the variant Converse runs with a prompt Amazon Resource Name (ARN)

## 2. Variant

A variant is one complete way to run the prompt.

### 2.1 Variant Fields

- **`templateType`**: `TEXT` (single string) or `CHAT`
  - CHAT = system + messages + optional tool config
- **`templateConfiguration`**: the template text or chat messages
  - Plus `inputVariables`
- **`modelId`**: model or inference profile the variant runs on
- **`inferenceConfiguration.text`**
  - `maxTokens`, `temperature`, `topP`, `stopSequences`
- **`additionalModelRequestFields`**: provider-specific keys
- **`metadata`**: key-value pairs (owner, ticket)
- Limit: a few variants per prompt
  - Order of magnitude: 3 in the console; check the quota page

### 2.2 TEXT And CHAT

- TEXT: one template string rendered into one user message
- CHAT: system text + Converse-shaped messages
  - Can carry `cachePoint` blocks
  - Can carry a tool configuration

## 3. Variables

Variables are named placeholders filled at run time.

- `{{name}}` placeholders, declared in `inputVariables`
- Filled at run time via `promptVariables = {name: {text: value}}`
- Values are inserted verbatim

  ⇒ fence untrusted text ([prompt-engineering](prompt-engineering.00index.md))

## 4. Creating A Prompt In Code

- Terraform owns `a-prompt` in this repo.
- `create_prompt` shows every console field as code (configuration as code).
- Two variants: TEXT `default` and CHAT `chat-concise`.

```python
# app/infra/_01bedrock_03prompt_management.py
SUMMARY_TEXT = "<task>Summarize {{topic}} for {{audience}}.</task>\n<format>At most 5 bullets.</format>"

def create_prompt(self, name: str, description: str = "") -> ManagedPrompt:
    model = self.settings.model()
    inference = {"text": {"maxTokens": 400, "temperature": 0.2, "topP": 0.9, "stopSequences": []}}
    kwargs: dict[str, Any] = {
        "name": name,                  # unique per account+Region; ([0-9a-zA-Z][_-]?){1,100}
        "defaultVariant": "default",   # the variant Converse(modelId=prompt ARN) runs
        "variants": [
            {
                "name": "default",
                "templateType": "TEXT",  # TEXT | CHAT
                "templateConfiguration": {"text": {
                    "text": SUMMARY_TEXT,
                    "inputVariables": [{"name": "topic"}, {"name": "audience"}],
                    # "cachePoint": {"type": "default"},  # cache the template prefix (supported models)
                }},
                "modelId": model,      # model ID or inference profile
                "inferenceConfiguration": inference,
                "metadata": [{"key": "owner", "value": "ai-platform"}],
            },
            {
                "name": "chat-concise",
                "templateType": "CHAT",
                "templateConfiguration": {"chat": {
                    "system": [{"text": "You write for busy {{audience}}. Three bullets, no preamble."}],
                    "messages": [{"role": "user", "content": [{"text": "Summarize {{topic}}."}]}],
                    "inputVariables": [{"name": "topic"}, {"name": "audience"}],
                    # "toolConfiguration": {"tools": [...], "toolChoice": {"auto": {}}},  # CHAT only
                }},
                "modelId": model,
                "inferenceConfiguration": inference,
                # "additionalModelRequestFields": {"top_k": 50},  # provider-specific keys
            },
        ],
        "clientToken": str(uuid.uuid5(uuid.NAMESPACE_URL, f"prompt/{name}")),  # stable per name ⇒ idempotent
        "tags": {"Component": "01.03"},
    }
    if description:  # optional, but min length 1 when sent
        kwargs["description"] = description
    if self.settings.kms_key_arn:
        kwargs["customerEncryptionKeyArn"] = self.settings.kms_key_arn  # CMK; caller needs KMS permissions
    return self._to_prompt(self.agent.create_prompt(**kwargs))
```

```python
# app/config/_01bedrock_03prompt_management.py
class PromptsSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="A_PROMPTS_", env_file=".env", extra="ignore")

    prompt_name: str = "a-prompt"
    prompt_id: str = "PROMPT_ID"  # terraform output prompt_id
    prompt_version_arn: str = ""  # "<prompt_arn>:<n>" after CreatePromptVersion. Never DRAFT.
    kms_key_arn: str = ""         # empty -> AWS-owned key for prompts created in code
    model_id: str = ""            # empty -> shared fast_model_id

    def model(self) -> str:
        return self.model_id or get_settings().fast_model_id
```

- Catch: `CreatePrompt` creates DRAFT only.
  - Production needs a version ([03 draft and versions](prompt-management.03draft-versions.md)).
- Catch: `clientToken` makes a retried create return the same prompt.
  - Without it, retries create duplicates.

## 5. The Domain Model

- The Application Programming Interface (API) response maps to two frozen dataclasses.
- `ManagedPrompt.variant()` falls back to the default variant.

```python
# app/domain/_01bedrock_03prompt_management.py
@dataclass(frozen=True)
class PromptVariant:
    name: str
    template_type: str  # TEXT | CHAT
    model_id: str
    text: str = ""      # TEXT template
    system: str = ""    # CHAT template: system text
    messages: list[dict[str, Any]] = field(default_factory=list)  # CHAT: Converse-shaped messages
    input_variables: list[str] = field(default_factory=list)
    inference: dict[str, Any] = field(default_factory=dict)  # maxTokens, temperature, topP, stopSequences


@dataclass(frozen=True)
class ManagedPrompt:
    prompt_id: str
    arn: str
    version: str  # "DRAFT" or "1", "2", ...
    default_variant: str
    variants: list[PromptVariant]

    def variant(self, name: str | None = None) -> PromptVariant:
        wanted = name or self.default_variant
        for v in self.variants:
            if v.name == wanted:
                return v
        raise KeyError(f"variant {wanted} not in prompt {self.prompt_id}")
```

- Catch: an unknown variant name raises `KeyError`.
  - The Representational State Transfer (REST) adapter maps it to Hypertext Transfer Protocol (HTTP) 422.
