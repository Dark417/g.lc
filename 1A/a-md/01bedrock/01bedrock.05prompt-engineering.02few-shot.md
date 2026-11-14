# 01bedrock.05prompt-engineering Zero-, One-, Few-Shot

> How many examples to show, how to pass them, and how to pick them per input.

## Index

- [1. Shot Counts](#1-shot-counts)
  - [1.1 Zero-Shot](#11-zero-shot)
  - [1.2 One-Shot And Few-Shot](#12-one-shot-and-few-shot)
- [2. Two Ways To Pass Examples](#2-two-ways-to-pass-examples)
  - [2.1 Inline Example Blocks](#21-inline-example-blocks)
  - [2.2 Fake Prior Turns](#22-fake-prior-turns)
- [3. Dynamic Few-Shot](#3-dynamic-few-shot)

Back to [00index](01bedrock.05prompt-engineering.00index.md).

---

## 1. Shot Counts

More examples teach more, at a token cost on every call.

### 1.1 Zero-Shot

- **Zero-shot**: instruction only
- Works for common tasks on strong models

```python
# app/infra/_01bedrock_05prompt_engineering.py
def classify_zero_shot(self, text: str) -> str:
    sections = PromptSections(
        role="You classify engineering status updates.",
        task="Classify the sentiment of the input.",
        output_format="One word: positive, negative, neutral, or mixed.",
    )
    resp = self._converse([{"role": "user", "content": [{"text": sections.render(text)}]}], sections.system())
    return self._text(resp).strip().lower()
```

- Catch: the label set and edge cases ("mixed") are underspecified.

  ⇒ format drift

### 1.2 One-Shot And Few-Shot

- **One-shot**: one example
  - Fixes the output format
- **Few-shot**: 3–5 examples (order of magnitude)
  - Teaches labels, edge cases, tone
  - Cover each class
  - Include a hard negative

```python
# app/domain/_01bedrock_05prompt_engineering.py
SENTIMENT_EXAMPLES = [
    FewShotExample("The deploy went smoothly, zero downtime.", "positive"),
    FewShotExample("Pager went off three times last night.", "negative"),
    FewShotExample("We migrated the table to on-demand.", "neutral"),
    FewShotExample("Latency improved, but the bill doubled.", "mixed"),  # hard case: both signals
]
```

- Catch: the model copies surface features (length, wording, label order)

  ⇒ vary examples

- Catch: examples cost tokens on every call.

## 2. Two Ways To Pass Examples

Same idea, two Converse shapes.

- Inline `<example>` blocks inside one user message
- Fake prior turns (user/assistant pairs) in `messages`

```python
# app/infra/_01bedrock_05prompt_engineering.py
def classify_few_shot(self, text: str, as_messages: bool = False) -> str:
    sections = PromptSections(
        role="You classify engineering status updates.",
        task="Classify the sentiment of the input.",
        output_format="One word: positive, negative, neutral, or mixed.",
        examples="" if as_messages else build_few_shot_block(SENTIMENT_EXAMPLES),
    )
    if as_messages:
        messages = few_shot_messages(SENTIMENT_EXAMPLES, text)  # examples as fake turns
    else:
        messages = [{"role": "user", "content": [{"text": sections.render(text)}]}]
    return self._text(self._converse(messages, sections.system())).strip().lower()
```

### 2.1 Inline Example Blocks

```python
# app/domain/_01bedrock_05prompt_engineering.py
def build_few_shot_block(examples: list[FewShotExample]) -> str:
    rendered = "\n".join(
        f'<example index="{i}">\n<input>{e.input}</input>\n<output>{e.output}</output>\n</example>'
        for i, e in enumerate(examples, 1)
    )
    return f"<examples>\n{rendered}\n</examples>"
```

### 2.2 Fake Prior Turns

```python
# app/domain/_01bedrock_05prompt_engineering.py
def few_shot_messages(examples: list[FewShotExample], final_input: str) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = []
    for e in examples:
        messages.append({"role": "user", "content": [{"text": e.input}]})
        messages.append({"role": "assistant", "content": [{"text": e.output}]})
    messages.append({"role": "user", "content": [{"text": final_input}]})  # the real input, last
    return messages
```

- Catch: fake turns must still alternate roles and start with `user`.
  - Converse rejects other orders ([01bedrock.01converse](01bedrock.01converse.04request-response.md)).

## 3. Dynamic Few-Shot

- Retrieve the k most similar examples per input
  - Uses embeddings ([02rag.01embeddings](../02rag/02rag.01embeddings.00index.md))

⇒ better accuracy with a fixed token budget

- Not coded here (see the [00index gaps](01bedrock.05prompt-engineering.00index.md#5-gaps)).
