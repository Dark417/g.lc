# 01bedrock.05prompt-engineering Chain-Of-Thought

> Ask the model to reason before answering, parse only the answer, and know when it is redundant.

## Index

- [1. What It Does](#1-what-it-does)
- [2. Structured CoT](#2-structured-cot)
- [3. Cost](#3-cost)
- [4. Reasoning Models](#4-reasoning-models)
- [5. Limit](#5-limit)

Back to [00index](01bedrock.05prompt-engineering.00index.md).

---

## 1. What It Does

- Ask the model to reason step by step before answering
- Improves on non-reasoning models
  - multi-step math
  - logic
  - planning

## 2. Structured CoT

Reasoning and answer go in separate tags.

- Reasoning in `<thinking>`
- Final answer in `<answer>`

⇒ parse only `<answer>`  
⇒ log or drop the reasoning

```python
# app/infra/_01bedrock_05prompt_engineering.py
def chain_of_thought(self, question: str) -> dict[str, str | None]:
    prompt = (
        f"<question>\n{question}\n</question>\n\n"
        "Think step by step inside <thinking></thinking>. "
        "Then give only the final answer inside <answer></answer>."
    )
    text = self._text(self._converse([{"role": "user", "content": [{"text": prompt}]}], "You solve problems carefully."))
    return {"answer": extract_tag(text, "answer"), "reasoning": extract_tag(text, "thinking")}
```

```python
# app/domain/_01bedrock_05prompt_engineering.py
def extract_tag(text: str, tag: str) -> str | None:
    """Content of the LAST <tag>...</tag>; keeps only <answer> from a CoT reply."""
    found = re.findall(rf"<{tag}>(.*?)</{tag}>", text, flags=re.DOTALL)
    return found[-1].strip() if found else None
```

- Catch: a missing `<answer>` returns `None`; treat it as a failed call.

## 3. Cost

- More output tokens

⇒ more latency and money

- Use Chain-of-Thought (CoT) only where accuracy needs it

## 4. Reasoning Models

- Reasoning models think internally
  - Claude with extended/adaptive thinking, Nova reasoning, ...

⇒ explicit "think step by step" is mostly redundant there  
⇒ control depth with the model's reasoning or effort setting instead (`additionalModelRequestFields`)

- Effort settings are not coded here (see the [00index gaps](01bedrock.05prompt-engineering.00index.md#5-gaps)).

## 5. Limit

- Visible reasoning is not guaranteed to be the real cause of the answer

⇒ don't use it as an audit trail
