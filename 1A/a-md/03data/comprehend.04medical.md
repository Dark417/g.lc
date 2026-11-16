# comprehend Comprehend Medical

> Clinical Natural Language Processing (NLP): medical entities with traits, Protected Health Information (PHI) detection, and linking text to International Classification of Diseases, 10th Revision, Clinical Modification (ICD-10-CM), RxNorm and Systematized Nomenclature of Medicine (SNOMED) codes.

## Index

- [1. What It Adds](#1-what-it-adds)
- [2. Entities And PHI](#2-entities-and-phi)
- [3. Code Linking](#3-code-linking)

## 1. What It Adds

Comprehend Medical is a separate service (`comprehendmedical`) for clinical text.

- `DetectEntitiesV2`: medications, conditions, tests, anatomy
  - With traits (negation, ...)
- `DetectPHI`: protected health information entities
- `InferICD10CM`, `InferRxNorm`, `InferSNOMEDCT`: link text to codes with scores
- **Limits**: text size per call is small
  - Documented in characters; check the quota page
- HIPAA-eligible
  - Your data governance still applies

## 2. Entities And PHI

Both calls take raw clinical text, so the text itself is PHI.

```python
# app/infra/_03data_04comprehend.py
def detect_entities_v2(text: str) -> list[dict[str, Any]]:
    """Medications, conditions, tests with traits (negation...). Never log the text (PHI)."""
    return client("comprehendmedical").detect_entities_v2(Text=text)["Entities"]


def detect_phi(text: str) -> list[dict[str, Any]]:
    """Protected health information spans (NAME, DATE, ID, ...)."""
    return client("comprehendmedical").detect_phi(Text=text)["Entities"]
```

- **Catch**: raw clinical text in logs ⇒ PHI leak
  - Never log inputs

## 3. Code Linking

Code inference returns ranked candidates, not coding decisions.

```python
# app/infra/_03data_04comprehend.py
def infer_icd10cm(text: str) -> list[dict[str, Any]]:
    """Link conditions to ICD-10-CM codes with scores. Catch: candidates, not coding decisions."""
    return client("comprehendmedical").infer_icd10_cm(Text=text)["Entities"]
```

- **Catch**: scores per code
  - Human review for coding decisions
  - Health Insurance Portability and Accountability Act (HIPAA) scope
