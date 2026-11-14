# 03data.01data-automation Interview

> Interview questions on Bedrock Data Automation, with Level 4 (L4) answers and Level 5 (L5) extras.

## Index

- [1. Core Questions](#1-core-questions)
  - [Q1 Standard Vs Custom Output](#q1-standard-vs-custom-output)
  - [Q2 Running Bedrock Data Automation (BDA) At Scale](#q2-running-bedrock-data-automation-bda-at-scale)
  - [Q3 BDA Vs Textract](#q3-bda-vs-textract)
  - [Q4 BDA In A Retrieval-Augmented Generation (RAG) Pipeline](#q4-bda-in-a-retrieval-augmented-generation-rag-pipeline)
  - [Q5 Data Automation Profile Amazon Resource Name (ARN)](#q5-data-automation-profile-amazon-resource-name-arn)
- [2. L5-Only Questions](#2-l5-only-questions)
  - [Q6 Invoice-Processing Pipeline](#q6-invoice-processing-pipeline)
  - [Q7 Output Differs Between Runs](#q7-output-differs-between-runs)

## 1. Core Questions

Each answer gives the L4 baseline, then what L5 adds.

### Q1 Standard Vs Custom Output

**Q:** What is the difference between standard and custom output?

**L4 answer**

- Standard = modality defaults (text, summary, transcript)
- Custom = a blueprint with the fields you want and instructions per field
- Projects combine both

**L5 extra**

- Blueprint fields are inferred by a model ⇒ confidence + validation needed
- Stages (DEVELOPMENT / LIVE) are the change-management lever

### Q2 Running Bedrock Data Automation (BDA) At Scale

**Q:** How do you run BDA at scale?

**L4 answer**

- Async invoke with Simple Storage Service (S3) in/out
- Poll status or use EventBridge
- Put S3 events → Lambda/Step Functions to submit

**L5 extra**

- Throttle submissions to the quota
- Idempotent `clientToken`
- Per-run output prefix
- Retry only on `ServiceError`, not `ClientError`

### Q3 BDA Vs Textract

**Q:** BDA vs Textract?

**L4 answer**

- Textract = Optical Character Recognition (OCR) and structure for documents
- BDA = multimodal + field inference

**L5 extra**

- Combine them
  - Textract for coordinates and cheap bulk OCR
  - BDA for the hard minority
- Price per page decides; benchmark on your own documents

### Q4 BDA In A Retrieval-Augmented Generation (RAG) Pipeline

**Q:** How would BDA improve a RAG pipeline?

**L4 answer**

- As the Knowledge Base (KB) parser
  - Tables, charts and layout become text/Markdown before chunking

**L5 extra**

- Trade-off: ingestion cost vs retrieval quality
  - Measure with RAG evals (see [04safety.03evaluations](../04safety/04safety.03evaluations.00index.md))
- Re-ingest is needed when you change the parser

### Q5 Data Automation Profile Amazon Resource Name (ARN)

**Q:** Why does BDA need a data automation profile ARN?

**L4 answer**

- It is a cross-region inference profile
- BDA routes work across Regions

**L5 extra**

- Governance: data may leave the Region
  - Confirm the geography fits residency rules

## 2. L5-Only Questions

These test design ownership and ambiguity.

### Q6 Invoice-Processing Pipeline

**Q:** Design an invoice-processing pipeline with BDA.

**L5 answer**

→ S3 upload → event → submit job (`clientToken` = object version id)  
→ EventBridge on completion → validate JavaScript Object Notation (JSON) → write to DynamoDB  
→ Low-confidence or schema failure → human review queue

- Idempotent by object version
- Dead-Letter Queue (DLQ) for `ServiceError`
- Cost guard: reject files over the page cap before submit

### Q7 Output Differs Between Runs

**Q:** BDA output differs between runs. What do you do?

**L5 answer**

- Pin the blueprint LIVE version
- Keep a golden set with expected fields
- Regression test on every blueprint edit
  - Compare field-level accuracy
- Move deterministic fields to Textract queries or regex post-checks
