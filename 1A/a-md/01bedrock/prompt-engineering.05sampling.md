# prompt-engineering Temperature And Top-P

> Two sampling knobs that trade repeatability for variety; tune one, and keep both per-model config.

## Index

- [1. Temperature](#1-temperature)
- [2. Top-P](#2-top-p)
- [3. Picking Values](#3-picking-values)
- [4. Models That Reject The Knobs](#4-models-that-reject-the-knobs)

Back to [00index](prompt-engineering.00index.md).

---

## 1. Temperature

- **Temperature** scales the logits before sampling
  - 0 ⇒ near-greedy, most repeatable
    - Not bit-exact across calls
  - 0.7–1.0 ⇒ more varied wording and ideas

## 2. Top-P

- **Top-p** keeps the smallest token set whose probability sums to p
  - 0.9 cuts the long tail of unlikely tokens
- Tune one of them, not both (vendor guidance)

## 3. Picking Values

- Extraction, classification, tools: temperature 0–0.3
- Brainstorming, marketing copy: 0.7+

```python
# app/infra/_01bedrock_05prompt_engineering.py
def sample_at_temperatures(self, prompt: str, temperatures: list[float]) -> dict[str, str]:
    out: dict[str, str] = {}
    for t in temperatures:  # same prompt; low = repeatable, high = varied
        resp = self._converse([{"role": "user", "content": [{"text": prompt}]}], "Answer in one sentence.", temperature=t)
        out[str(t)] = self._text(resp)
    return out
```

- The Representational State Transfer (REST) adapter calls it with `[0.0, 0.5, 1.0]` (`/temperatures`).

## 4. Models That Reject The Knobs

- Some newer models reject these knobs
  - Recent Claude models (Anthropic docs 2026-11)

⇒ keep them per-model config (`A_PROMPTING_SEND_SAMPLING`)

```python
# app/infra/_01bedrock_05prompt_engineering.py
def _converse(self, messages, system: str, temperature: float | None = 0.0, **extra: Any) -> dict[str, Any]:
    cfg: dict[str, Any] = {"maxTokens": self.settings.max_tokens}
    if self.settings.send_sampling and temperature is not None:  # drop the knob for models that reject it
        cfg["temperature"] = temperature
    return self.runtime.converse(
        modelId=self.settings.model(),
        system=[{"text": system}],
        messages=messages,
        inferenceConfig=cfg,
        **extra,  # toolConfig / outputConfig for structured output
    )
```

```python
# app/config/_01bedrock_05prompt_engineering.py
send_sampling: bool = True  # False for models that reject temperature/topP
```

- Catch: with `send_sampling=False` every temperature uses the model default.
  - The temperature demo then shows no difference.
