# 01bedrock.02customization Customization Types

> Four ways to train a custom model, what data each needs, and how to find supporting models.

## Index

- [1. The Four Types](#1-the-four-types)
  - [1.1 Fine-Tuning](#11-fine-tuning)
  - [1.2 Continued Pre-Training](#12-continued-pre-training)
  - [1.3 Distillation](#13-distillation)
  - [1.4 Reinforcement Fine-Tuning](#14-reinforcement-fine-tuning)
- [2. Which Models Support Which Type](#2-which-models-support-which-type)

Back to [00index](01bedrock.02customization.00index.md).

---

## 1. The Four Types

The type is set by `customizationType` on the job.

| Type | Data | Teaches |
|---|---|---|
| `FINE_TUNING` | Labeled input → output pairs | Task, style, format |
| `CONTINUED_PRE_TRAINING` | Unlabeled domain text | Vocabulary, domain familiarity |
| `DISTILLATION` | Your prompts; teacher answers | Teacher quality on a student |
| `REINFORCEMENT_FINE_TUNING` | Prompts + a grader | Higher-scoring outputs |

### 1.1 Fine-Tuning

- **Fine-tuning** (`FINE_TUNING`): labeled input → output pairs
- Teaches a task, style, or format
  - classification labels
  - a brand voice
  - a JavaScript Object Notation (JSON) shape

### 1.2 Continued Pre-Training

- **Continued pre-training** (`CONTINUED_PRE_TRAINING`): unlabeled domain text
  - manuals, filings
- Shifts vocabulary and domain familiarity
- Needs far more data
- Supported by fewer models

### 1.3 Distillation

- **Distillation** (`DISTILLATION`)
  - A large teacher model generates answers for your prompts
  - A smaller student learns them
- Can use invocation logs as the prompt source
- Goal: teacher-like quality at student price and latency on your task

```python
# app/infra/_01bedrock_02customization.py  (commented in create_customization_job)
# Distillation instead: customizationType="DISTILLATION" +
# "customizationConfig": {"distillationConfig": {"teacherModelConfig": {"teacherModelIdentifier": "..."}}}
```

- Catch: distillation needs a teacher that already works on your task.

### 1.4 Reinforcement Fine-Tuning

- **Reinforcement fine-tuning** (`REINFORCEMENT_FINE_TUNING`)
  - A grader (Lambda) scores outputs
  - Training rewards higher scores
- Newer; only some models
  - Check model support

## 2. Which Models Support Which Type

- `ListFoundationModels(byCustomizationType=...)` per Region
- Values: `FINE_TUNING` | `CONTINUED_PRE_TRAINING` | `DISTILLATION`

```python
# app/infra/_01bedrock_02customization.py
def list_customizable_models(self, customization: str = "FINE_TUNING") -> list[dict[str, Any]]:
    resp = self.control.list_foundation_models(byCustomizationType=customization)  # this Region only
    return [
        {"model_id": m["modelId"], "provider": m.get("providerName"),
         "customizations": m.get("customizationsSupported", [])}
        for m in resp["modelSummaries"]
    ]
```

- Catch: results are per Region.
- Catch: customizable Identifiers (IDs) often carry a context suffix (`:128k`).
  - It differs from the on-demand model ID.
