# comprehend Tradeoffs

> When Comprehend beats a Large Language Model (LLM), the knobs that keep it cheap and correct, how it compares, and how it fails.

## Index

- [1. When To Use / Not](#1-when-to-use--not)
- [2. Knobs And Best Practices](#2-knobs-and-best-practices)
- [3. Comparison](#3-comparison)
- [4. Failure Modes](#4-failure-modes)

## 1. When To Use / Not

Comprehend fits narrow, high-volume tasks with fixed labels.

- **Use**
  - High-volume, narrow tasks with fixed labels
  - You need deterministic output, tight latency, predictable cost
  - Pre-filter before an LLM
- **Don't use**
  - Open-ended understanding, new labels each week ⇒ LLM
  - Sarcasm, domain slang, long-context reasoning ⇒ LLM
  - Training endpoints for low volume ⇒ idle cost

## 2. Knobs And Best Practices

Each rule names the failure it prevents.

- **Pass `LanguageCode` when known**
  - Otherwise detect first (one cheap call)
- **Batch up to 25 per call**
  - Split larger lists
  - Read `ErrorList`, retry only failed indexes
- **Cut text to the limit on sentence boundaries**
  - Sentiment of a truncated text is partial
- **Cache results by text hash** for repeated inputs
- **Threshold on `Score`**
  - For entities, ~0.8 is a common start; tune on your data
- **Delete custom endpoints when idle**
  - Use async batch for offline classification
- **Don't log raw text** (sensitive)
  - The Software Development Kit (SDK) marks inputs as sensitive

## 3. Comparison

The deciding variable is volume × label stability.

| Option | What it is | Strength | Weakness | Choose when |
|---|---|---|---|---|
| Comprehend | Task-specific Natural Language Processing (NLP) Application Programming Interfaces (APIs) | Cheap, fast, deterministic, no prompts | Fixed tasks; custom models cost | High volume, fixed labels, pre-filter |
| Prompt an LLM | General model with instructions | Any task, any label, nuance | Per-token cost, latency, non-determinism | Low volume, open-ended, rapid change |
| Comprehend then LLM | Detect, route, then generate | Cost control + explainable routing | Two systems to run | Mixed traffic where cheap signal decides spend |
| Hugging Face on SageMaker | Open model endpoints | Control, fine-tuning | You operate it | Special languages/domains at scale |

Pick: an LLM for flexibility at low volume, unless volume, latency or determinism dominates (Comprehend) or traffic is mixed (Comprehend as router in front of the LLM).

## 4. Failure Modes

API errors fail loudly; partial batches, idle endpoints and misrouting fail quietly.

**Loud failures**

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| `TextSizeLimitExceededException` | Text over the sync limit | API error | Chunk text |
| `UnsupportedLanguageException` | Language not supported for the API | API error | Detect language first; fall back to the LLM |
| Throttling | Burst of calls | `ThrottlingException` | Adaptive retries (shared client), backoff, batch |

**Quiet failures**

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Silent partial batch failure | Reading only `ResultList` | Missing indexes | Check `ErrorList`, retry those |
| Idle cost | Custom endpoint left running | Cost report | Delete endpoint; use async jobs |
| Wrong routing | Sentiment of a truncated message | Review samples | Use full text; thresholds on score |
| Protected Health Information (PHI) in logs | Raw clinical text logged | Log review | Never log inputs |
