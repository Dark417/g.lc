# 01bedrock.01converse InvokeModel vs Converse

> The native-JSON Application Programming Interface (API) versus the typed, model-agnostic chat API, and the escape hatches between them.

## Index

- [1. InvokeModel](#1-invokemodel)
- [2. Converse](#2-converse)
- [3. Escape Hatches](#3-escape-hatches)
- [4. Limit](#4-limit)

Back to [00index](01bedrock.01converse.00index.md).

---

## 1. InvokeModel

InvokeModel passes provider-native JavaScript Object Notation (JSON) bytes in both directions.

- Body = provider-native JSON bytes
  - Anthropic: `{"anthropic_version": "bedrock-2023-05-31", "max_tokens": ..., "system": ..., "messages": [...]}`
  - Nova, Llama, Titan: each different
- Response = provider-native JSON bytes
  - Usage in the body or in Hypertext Transfer Protocol (HTTP) headers
- Needed for
  - embeddings
  - image generation
  - provider features Converse does not expose yet

```python
# app/infra/_01bedrock_01converse.py
ANTHROPIC_BEDROCK_VERSION = "bedrock-2023-05-31"  # required "anthropic_version" in native Claude bodies

def invoke_model_anthropic(self, prompt: str, system: str = "You are concise.") -> dict[str, Any]:
    body = {
        "anthropic_version": ANTHROPIC_BEDROCK_VERSION,
        "max_tokens": self.settings.max_tokens,  # snake_case: native field, not maxTokens
        "system": system,
        "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
    }
    resp = self.runtime.invoke_model(
        modelId=self.settings.text_model(),
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json",
    )
    native = json.loads(resp["body"].read())  # StreamingBody: read once
    return {
        "text": "".join(c.get("text", "") for c in native.get("content", [])),
        "stop_reason": native.get("stop_reason"),  # end_turn | max_tokens | stop_sequence | tool_use
        "usage": native.get("usage", {}),          # {"input_tokens", "output_tokens", ...}
        # Token counts are also returned as HTTP headers on InvokeModel:
        "header_input_tokens": resp["ResponseMetadata"]["HTTPHeaders"].get("x-amzn-bedrock-input-token-count"),
    }
```

- Catch: field names differ from Converse.
  - `max_tokens` vs `maxTokens`
  - `stop_reason` vs `stopReason`
- Catch: swapping to Nova means rewriting this method.

## 2. Converse

Converse wraps the same call in a typed, fixed shape.

- Typed request fields
  - `modelId`, `messages`, `system`
  - `inferenceConfig`, `toolConfig`, `guardrailConfig`
  - `additionalModelRequestFields`, `promptVariables`, `requestMetadata`
  - `performanceConfig`, `serviceTier`, `outputConfig`
- Typed response fields
  - `output.message`, `stopReason`, `usage`, `metrics`
  - `additionalModelResponseFields`, `trace`
- Same Identity and Access Management (IAM) action as InvokeModel
  - See [09 errors and retries](01bedrock.01converse.09errors-retries.md) and the Terraform header
- Request and response detail: [04 request and response](01bedrock.01converse.04request-response.md)

## 3. Escape Hatches

Converse lets you reach provider-only keys without leaving its envelope.

- **`additionalModelRequestFields`**: provider-specific request keys
  - `top_k`, reasoning settings
- **`additionalModelResponseFieldPaths`**: JSON pointers into the native response
  - e.g. `/stop_sequence`

```python
# app/infra/_01bedrock_01converse.py  (inside converse_basic)
resp = self.runtime.converse(
    modelId=model_id or self.settings.text_model(),
    system=[{"text": system}],
    messages=[user_text(prompt)],
    inferenceConfig=self.inference_config(max_tokens, stop_sequences),
    # Provider-specific keys Converse does not model (Anthropic example): top_k sampling cutoff.
    # additionalModelRequestFields={"top_k": 250},
    # JSON pointers into the native response, returned in additionalModelResponseFields:
    # additionalModelResponseFieldPaths=["/stop_sequence"],
)
```

- Catch: these keys are provider-specific again.
  - Using them re-couples that call to one provider.

## 4. Limit

- A feature exposed only by the native API lands in Converse later, if at all

  ⇒ check the "Supported models and model features" table before choosing
