# 03data.01data-automation Tradeoffs

> When Bedrock Data Automation (BDA) is the right extractor, the knobs that keep it safe, how it compares, and how it fails.

## Index

- [1. When To Use / Not](#1-when-to-use--not)
- [2. Knobs And Best Practices](#2-knobs-and-best-practices)
- [3. Comparison](#3-comparison)
- [4. Failure Modes](#4-failure-modes)

## 1. When To Use / Not

BDA pays off when modalities are mixed or layouts vary.

- **Use**
  - Mixed modalities with one pipeline
  - Documents with variable layouts where template Optical Character Recognition (OCR) breaks
  - You want typed JavaScript Object Notation (JSON) and don't want to manage prompts
- **Don't use**
  - Plain OCR of clean text ⇒ Textract is cheaper
  - Tiny volume, bespoke logic ⇒ prompt a multimodal model directly
  - Data cannot leave the Region geography ⇒ check the inference profile Regions first
  - Need deterministic field coordinates in a fixed form ⇒ Textract Queries / forms

## 2. Knobs And Best Practices

Each rule names the failure it prevents.

- **Pin the LIVE stage** of blueprints in the project
  - Prevents: a DEVELOPMENT edit changing production output
- **Write instructions like prompts**
  - Unit, format, where to look
  - What to return when absent
- **Set `clientToken` on invoke**
  - Prevents: a retried submit starting a second billed job
- **Poll with exponential backoff and a deadline**
  - Use EventBridge for high volume
- **Encrypt output with the shared Customer Managed Key (CMK)** (`encryptionConfiguration`)
  - The caller needs `kms:GenerateDataKey`
- **Keep the output prefix per run**
  - Keeps listing and cleanup cheap
- **Validate result JSON** against a Pydantic model
  - Keep BDA's `confidence` per field
  - Route low confidence to humans
- **Sensitive-data detection** in the project for Personally Identifiable Information (PII)
  - Runs before the data reaches the Large Language Model (LLM)
  - See [04safety.02pii-redaction](../04safety/04safety.02pii-redaction.00index.md)

## 3. Comparison

The deciding variable is how many modalities and how variable the layouts are.

| Option | What it is | Strength | Weakness | Choose when |
|---|---|---|---|---|
| Bedrock Data Automation | Multimodal extraction, standard + blueprints | One Application Programming Interface (API) for 4 modalities; typed JSON; Knowledge Base (KB) parser | Region/profile constraints; per-unit price | Mixed files, variable layouts, Retrieval-Augmented Generation (RAG) ingestion |
| Textract | OCR, forms, tables, queries, invoice/Identity Document (ID) APIs | Cheap for pure OCR; bounding boxes | Documents only; no field inference | Clean scans, known forms, coordinates |
| Comprehend | Natural Language Processing (NLP) on text you already have | Fast, cheap, deterministic | No OCR, no custom field schema | Entities / sentiment on extracted text |
| Prompt a multimodal LLM | You send the image/Portable Document Format (PDF) and a schema | Most flexible; any logic | You own prompts, retries, cost, drift | Low volume, bespoke schema |

Pick: BDA for multi-modality or variable-layout extraction, unless the input is clean OCR (Textract) or volume is tiny (prompt the model).

## 4. Failure Modes

Access and input errors dominate; drift and duplicates are the silent ones.

**Access and input**

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| `AccessDenied` on invoke | Policy lacks the profile Amazon Resource Name (ARN) or project ARN | Error names the resource | Allow `data-automation-profile/*` and the project |
| Job `ClientError` | Unsupported format, file over limits | `get_data_automation_status` errorType + errorMessage | Check formats / size quotas, split input |
| Job never finishes in your timeout | Large video | Status stays `InProgress` | Longer deadline or EventBridge |
| Output unreadable | Key Management Service (KMS) grant missing for the caller | Simple Storage Service (S3) `AccessDenied` / KMS error | Grant `kms:Decrypt` on the CMK |

**Quality and cost**

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Field returned null | Instruction ambiguous or value absent | Compare with sample | Tighten instruction; add `inferenceType` |
| Duplicate billed jobs | Retried submit without token | Two invocation ARNs | Pass `clientToken` |
| Drift after blueprint edit | Project pinned to DEVELOPMENT | Output changes | Promote to LIVE, pin version |
