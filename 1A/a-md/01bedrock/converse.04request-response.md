# converse Converse Request And Response

> The fields you send, the fields you get back, and two cost levers: prompt caching and request metadata.

## Index

- [1. Request](#1-request)
  - [1.1 Messages](#11-messages)
  - [1.2 System](#12-system)
  - [1.3 inferenceConfig](#13-inferenceconfig)
  - [1.4 A Basic Call](#14-a-basic-call)
- [2. Response](#2-response)
  - [2.1 Fields](#21-fields)
  - [2.2 Parsing](#22-parsing)
- [3. Prompt Caching](#3-prompt-caching)
- [4. requestMetadata](#4-requestmetadata)

Back to [00index](converse.00index.md).

---

## 1. Request

A Converse request is messages plus a system prompt plus sampling settings.

### 1.1 Messages

- `messages`: list of `{role: user|assistant, content: [blocks]}`
- Must start with `user` and alternate roles
- Content blocks
  - `text`, `image`, `document`, `video`
  - `toolUse`, `toolResult`
  - `guardContent`, `cachePoint`, `reasoningContent`, ...

```python
# app/infra/_01bedrock_01converse.py
def user_text(text: str) -> Message:
    return {"role": "user", "content": [{"text": text}]}
```

```python
# app/domain/_01bedrock_01converse.py
Message = dict[str, Any]  # one Converse message (role + content blocks), plain wire-shape dict
```

### 1.2 System

- `system`: list of blocks
  - `text`, `guardContent`, `cachePoint`
- Not every model supports a system prompt
  - Check the feature table

### 1.3 inferenceConfig

- **`maxTokens`**: output cap
  - Hitting it ⇒ `stopReason = max_tokens`
- **`temperature`**: 0 = most deterministic, higher = more varied
- **`topP`**: nucleus sampling
  - Tune temperature or topP, not both
- **`stopSequences`**: strings that end generation
  - Hitting one ⇒ `stopReason = stop_sequence`
- Some newer models reject sampling knobs
  - e.g. recent Claude models reject `temperature` / `topP` (Anthropic docs 2026-11)

  ⇒ keep them configurable per model

```python
# app/infra/_01bedrock_01converse.py
def inference_config(self, max_tokens: int | None = None, stop: list[str] | None = None) -> dict[str, Any]:
    cfg: dict[str, Any] = {"maxTokens": max_tokens or self.settings.max_tokens}
    if self.settings.send_sampling:  # False for models that reject temperature/topP
        cfg["temperature"] = self.settings.temperature
        cfg["topP"] = self.settings.top_p
    if stop:
        cfg["stopSequences"] = stop  # max 4 on many models
    return cfg
```

```python
# app/config/_01bedrock_01converse.py
max_tokens: int = 1024       # also reserves tokens-per-minute quota on some models: keep it tight
temperature: float = 0.2     # 0..1; low for extraction/tools, higher for creative text
top_p: float = 0.9           # nucleus sampling; tune temperature OR top_p, not both
send_sampling: bool = True   # False for models that reject temperature/topP (some newer Claude models)
```

### 1.4 A Basic Call

```python
# app/infra/_01bedrock_01converse.py
def converse_basic(self, prompt: str, system: str = "You are a concise assistant for backend engineers.",
                   model_id: str | None = None, max_tokens: int | None = None,
                   stop_sequences: list[str] | None = None) -> ConverseResult:
    resp = self.runtime.converse(
        modelId=model_id or self.settings.text_model(),  # model ID, profile ID, or profile/provisioned ARN
        system=[{"text": system}],  # list of blocks; some models don't support system prompts
        messages=[user_text(prompt)],
        inferenceConfig=self.inference_config(max_tokens, stop_sequences),
        requestMetadata={"feature": "converse-basic"},  # lands in invocation logs (observability)
    )
    return parse_converse_response(resp)
```

- Catch: check `stop_reason == max_tokens` before trusting the text.

## 2. Response

The response carries the message, why it stopped, tokens, and latency.

### 2.1 Fields

- **`output.message`**: the assistant message
  - Append it as-is to history
- **`stopReason`**
  - `end_turn`, `tool_use`, `max_tokens`, `stop_sequence`
  - `guardrail_intervened`, `content_filtered`
  - `malformed_model_output`, `malformed_tool_use`
  - `model_context_window_exceeded`
- **`usage`**
  - `inputTokens`, `outputTokens`, `totalTokens`
  - `cacheReadInputTokens`, `cacheWriteInputTokens`
- **`metrics.latencyMs`**: server-side time for the whole call

```python
# app/domain/_01bedrock_01converse.py
class StopReason(StrEnum):
    """Every stopReason Converse can return (botocore bedrock-runtime model, 2026-11)."""
    END_TURN = "end_turn"                  # model finished
    TOOL_USE = "tool_use"                  # model wants tool results before it continues
    MAX_TOKENS = "max_tokens"              # truncated by inferenceConfig.maxTokens
    STOP_SEQUENCE = "stop_sequence"        # hit one of inferenceConfig.stopSequences
    GUARDRAIL_INTERVENED = "guardrail_intervened"  # guardrail blocked/masked (guardrails)
    CONTENT_FILTERED = "content_filtered"  # provider-side filter
    MALFORMED_MODEL_OUTPUT = "malformed_model_output"
    MALFORMED_TOOL_USE = "malformed_tool_use"
    MODEL_CONTEXT_WINDOW_EXCEEDED = "model_context_window_exceeded"
```

### 2.2 Parsing

- One parser turns every response into a `ConverseResult`.
- Text = all `text` blocks joined; tool calls = all `toolUse` blocks.

```python
# app/infra/_01bedrock_01converse.py
def parse_converse_response(resp: dict[str, Any], rounds: int = 1) -> ConverseResult:
    message: Message = resp["output"]["message"]
    blocks = message.get("content", [])
    return ConverseResult(
        text="".join(b["text"] for b in blocks if "text" in b),
        stop_reason=resp["stopReason"],
        usage=parse_usage(resp.get("usage")),
        latency_ms=resp.get("metrics", {}).get("latencyMs", 0),
        message=message,  # appended unchanged to history
        tool_calls=[b["toolUse"] for b in blocks if "toolUse" in b],
        rounds=rounds,
    )
```

- Catch: `latencyMs` is server time only.
  - Compare with client time to separate network and retries.

## 3. Prompt Caching

A `cachePoint` lets repeated long prefixes bill and run cheaper.

- A `cachePoint` block marks the end of a reusable prefix
  - System prompt, long document
- Later calls with the same prefix
  - bill cached tokens at a discount
  - start faster

```python
# app/infra/_01bedrock_01converse.py
def converse_cached_system(self, long_system: str, prompt: str) -> ConverseResult:
    resp = self.runtime.converse(
        modelId=self.settings.text_model(),
        system=[{"text": long_system}, {"cachePoint": {"type": "default"}}],  # everything above is cacheable
        messages=[user_text(prompt)],
        inferenceConfig=self.inference_config(),
    )
    return parse_converse_response(resp)
```

```python
# app/domain/_01bedrock_01converse.py
@dataclass(frozen=True)
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cache_read_input_tokens: int = 0  # > 0 proves a cachePoint prefix was reused
    cache_write_input_tokens: int = 0
```

- Limit: minimum prefix length and Time to Live (TTL) are per model.
  - Below the minimum nothing is cached.
  - Verify with `cacheReadInputTokens > 0` on the second call.

## 4. requestMetadata

- **`requestMetadata`**: key-value tags written to invocation logs
  - See [observability](../05ops/observability.00index.md)

  ⇒ filter logs per tenant or feature

- Code: the `requestMetadata` line in [1.4](#14-a-basic-call).
