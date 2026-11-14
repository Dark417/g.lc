# 04safety.03evaluations.05llm-judge Large Language Model (LLM)-as-a-Judge

> How a judge model scores answers, the biases it brings, and how to choose and calibrate it.

## Index

- [1. Mechanism](#1-mechanism)
- [2. Biases](#2-biases)
- [3. Mitigations](#3-mitigations)
- [4. Model Choice](#4-model-choice)

Back to [00index](04safety.03evaluations.00index.md).

## 1. Mechanism

A second model grades each answer against a rubric.

→ Judge gets the rubric, the prompt, the candidate response, and the reference.  
→ Returns a score on the rating scale plus an explanation.  
→ Bedrock normalizes built-in metric scores to 0–1.

## 2. Biases

Documented in the Large Language Model (LLM)-judge literature, e.g. Zheng et al. 2023 "MT-Bench".

- **Self-preference**: a judge favors outputs from its own model family
- **Verbosity**: longer answers score higher
- **Position**: in pairwise comparisons, the first (or second) answer wins more often
- Also: judge cost and non-determinism

## 3. Mitigations

- Judge from a different family than the generator
- Rubrics with explicit criteria and anchored scale definitions
- Calibrate: judge vs humans on 50–200 items (order of magnitude)
  - report agreement
- Pin the judge model version
  - a judge upgrade changes every score
- Pairwise comparisons: swap order and average

## 4. Model Choice

- Must be on the supported evaluator list
  - check the docs; it changes
- Stronger judge = better agreement, higher cost
- Cheaper judge for smoke tests

```python
# app/config/_04safety_03evaluations.py
# Generator = model under test; judge = evaluator. Different families reduce self-preference bias.
# The judge must be on the supported evaluator list (check the docs; it changes).
generator_model_id: str = ""  # empty = app.shared.config fast_model_id
judge_model_id: str = "us.amazon.nova-pro-v1:0"
```

- Catch
  - Never trust a judge you have never compared with humans
