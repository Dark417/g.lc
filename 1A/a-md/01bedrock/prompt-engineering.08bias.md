# prompt-engineering Bias

> Where bias enters a prompted system, how to reduce it, and why prompting cannot remove it.

## Index

- [1. Sources](#1-sources)
- [2. Mitigations](#2-mitigations)
- [3. Limit](#3-limit)

Back to [00index](prompt-engineering.00index.md).

---

## 1. Sources

- Training data
- Prompt wording
- Example selection
- Label order

## 2. Mitigations

Reduce bias at each source, then measure it.

- Balanced few-shot examples across classes and groups
- Neutral wording
  - Don't name protected attributes unless needed
- Shuffle answer options
  - Test for order effects
- Evaluate on sliced datasets
  - See [evaluations](../04safety/evaluations.00index.md)
  - SageMaker Clarify for bias metrics
- Guardrails denied topics / content filters for harmful outputs

```python
# illustrative: shuffle options per call to expose order bias
import random

def options_block(options: list[str], seed: int) -> str:
    shuffled = options[:]
    random.Random(seed).shuffle(shuffled)  # different seeds ⇒ compare answer distributions
    return "\n".join(f"- {o}" for o in shuffled)
```

- Catch: shuffling detects order bias; it does not fix other sources.
- Bias evaluation is not coded here (see the [00index gaps](prompt-engineering.00index.md#5-gaps)).

## 3. Limit

- Prompting reduces visible bias
- It does not remove bias in the model
