# 03data.04comprehend Amazon Comprehend

> Cheap, fast, deterministic Natural Language Processing (NLP) signals that enrich, filter or route text before an expensive Large Language Model (LLM) call.

## Index

- [1. Source And Scope](#1-source-and-scope)
- [2. One-Minute Version](#2-one-minute-version)
- [3. Component Map](#3-component-map)
  - Concepts
    - [01 Why And Application Programming Interfaces (APIs)](03data.04comprehend.01why-and-apis.md): pain, use cases, Detect* APIs
    - [02 Batch And Async](03data.04comprehend.02batch-and-async.md): `BatchDetect*`, `ErrorList`, async jobs, size limits
    - [03 Custom Models](03data.04comprehend.03custom-models.md): custom classifier, entity recognizer, cost
    - [04 Comprehend Medical](03data.04comprehend.04medical.md): clinical entities, Protected Health Information (PHI), code linking
    - [05 Routing Pattern](03data.04comprehend.05routing-pattern.md): Comprehend + Lambda + Bedrock
  - Decide and defend
    - [98 Tradeoffs](03data.04comprehend.98tradeoffs.md): when to use, knobs, comparison, failure modes
    - [99 Interview](03data.04comprehend.99interview.md): Level 4 (L4) + Level 5 (L5) questions
- [4. Code Map](#4-code-map)
- [References](#references)

## 1. Source And Scope

Lectures AIP-C01 #49–#52 (slides p.114–119).

- **Scope**: Python + Terraform
- **Terraform**: [modules/03data_04comprehend](../../terraform/modules/03data_04comprehend/main.tf)
  - App policy only
  - No custom models (cost)
- **Code**: Python layers `app/*/_03data_04comprehend.py` (slice `comprehend`)
- Personally Identifiable Information (PII) detection and redaction live in [04safety.02pii-redaction](../04safety/04safety.02pii-redaction.00index.md)
  - This component covers the general NLP APIs
- **Numbers**: Amazon Comprehend / Comprehend Medical Developer Guides, read 2026-11
  - "Check the quota page" where unsure

## 2. One-Minute Version

Comprehend answers narrow NLP questions at fixed cost and latency; the LLM does the rest.

- **What**
  - Managed NLP: entities, key phrases, sentiment, language, syntax, classification
  - Comprehend Medical
    - Clinical entities
    - International Classification of Diseases, 10th Revision, Clinical Modification (ICD-10-CM) / RxNorm / Systematized Nomenclature of Medicine (SNOMED) linking
    - PHI
- **Why**
  - Cheap, fast, deterministic signals about text
  - Use them to enrich, filter or route before an expensive LLM call
- **How**
  - Sync `Detect*` for one text
  - `BatchDetect*` for up to 25 documents per call (check the quota page)
  - Async `Start*DetectionJob` for large Simple Storage Service (S3) corpora
  - Custom classifier / entity recognizer: you train, then call through an endpoint
- **Catch**
  - Per-unit pricing: 100 characters per unit, minimum charge per request
    - Check the pricing page
  - Custom models cost training + hourly endpoint
    - Idle endpoints bill
  - Sync text size limits ⇒ chunk long text
  - Batch calls return partial failures in `ErrorList`
  - Language support varies per API
- 🗣 "Comprehend answers narrow NLP questions at fixed cost and latency; the LLM does the rest."
- 🗣 "Detect, then decide: sentiment and key phrases choose the prompt and the model tier."
- 🗣 "Batch APIs fail per item: always read `ErrorList`."

## 3. Component Map

The files go from single calls to scale, customization, a vertical, then the routing pattern.

```text
 01 why-and-apis ─► 02 batch-and-async ─► 03 custom-models
                                              │
               05 routing-pattern ◄── 04 medical
 98 tradeoffs · 99 interview  (decide and defend)
```

The routing pattern in 05 is where Comprehend earns its place next to an LLM.

## 4. Code Map

Every concept file maps to one Python function in the new layer-first layout.

| Concept file | Python path | Function |
|---|---|---|
| 01 one function per Detect* API | `app/infra/_03data_04comprehend.py` | `detect_entities`, `detect_key_phrases`, `detect_sentiment` |
| 01 more Detect* APIs | `app/infra/_03data_04comprehend.py` | `detect_targeted_sentiment`, `detect_dominant_language`, `detect_syntax` |
| 02 batch (25 per call) + `ErrorList` | `app/infra/_03data_04comprehend.py` | `batch_detect_entities`, `_trim` |
| 04 Comprehend Medical | `app/infra/_03data_04comprehend.py` | `detect_entities_v2`, `detect_phi`, `infer_icd10cm` |
| 05 route decision (lecture 51) | `app/domain/_03data_04comprehend.py` | `choose_route`, `Signals`, `Route` |

| Concept file | Python path | Function |
|---|---|---|
| 05 enrich, route, generate | `app/service/_03data_04comprehend.py` | `gather_signals`, `route_and_answer` |
| 01/02/05 Representational State Transfer (REST) (`/comprehend`) | `app/api/_03data_04comprehend.py` | `analyze`, `entities_batch`, `route` |
| 02 settings (`A_COMPREHEND_`) | `app/config/_03data_04comprehend.py` | `ComprehendSettings` |

- **Gaps** (no repo code)
  - Async jobs
  - Custom classifier/recognizer training and endpoints, `ClassifyDocument`
  - Toxicity detection, flywheels, events detection

## References

- [aws-samples/amazon-comprehend-examples](https://github.com/aws-samples/amazon-comprehend-examples)
- [Amazon Comprehend Developer Guide](https://docs.aws.amazon.com/comprehend/latest/dg/what-is.html)
- [Amazon Comprehend Medical Developer Guide](https://docs.aws.amazon.com/comprehend-medical/latest/dev/comprehendmedical-welcome.html)
- [Amazon Web Services (AWS) Machine Learning (ML) blog: Comprehend](https://aws.amazon.com/blogs/machine-learning/)
