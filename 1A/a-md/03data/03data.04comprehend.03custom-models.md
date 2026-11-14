# 03data.04comprehend Custom Models

> Train your own classifier or entity recognizer: when it beats a few-shot Large Language Model (LLM), and what it costs.

## Index

- [1. Custom Classification And Entities](#1-custom-classification-and-entities)
- [2. Cost And Alternatives](#2-cost-and-alternatives)

## 1. Custom Classification And Entities

Custom models extend the fixed label sets with your own labels and entity types.

- **Custom classification**
  → Labeled Comma-Separated Values (CSV) in Simple Storage Service (S3)  
  → `CreateDocumentClassifier`  
  → Model → real-time endpoint or async batch
- **Custom entity recognition**
  - Annotations or an entity list
  - `CreateEntityRecognizer`
- Real-time inference via `ClassifyDocument` / `DetectEntities` with `EndpointArn`
- Terraform has `aws_comprehend_document_classifier`
  - A commented example is in the `.tf`, not declared (cost)

```python
# illustrative (no repo code): train a classifier, then serve it
clf = client("comprehend").create_document_classifier(
    DocumentClassifierName="a-tickets",
    DataAccessRoleArn=role_arn,
    InputDataConfig={"S3Uri": "s3://bucket/comprehend/train.csv"},  # label,text rows
    LanguageCode="en",
)
client("comprehend").create_endpoint(
    EndpointName="a-tickets",
    ModelArn=clf["DocumentClassifierArn"],
    DesiredInferenceUnits=1,  # billed per inference-unit-hour, even when idle
)
```

- **Catch**: retraining is needed whenever labels change

## 2. Cost And Alternatives

Custom models pay off only with stable labels, volume, and labeled data.

- **Costs**
  - Training time
  - Model management
  - Endpoint per inference-unit-hour (check the pricing page)
- **Alternative today**: few-shot an LLM classifier
  - Custom models win at high volume and stable labels
- Start with an LLM labeler to produce the training set, then distill
- Delete custom endpoints when idle
  - Use async batch for offline classification

→ Endpoint left running with low traffic  
⇒ Idle cost dominates the bill.  
→ Delete the endpoint; use async jobs.
