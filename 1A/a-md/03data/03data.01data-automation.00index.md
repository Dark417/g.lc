# 03data.01data-automation Bedrock Data Automation

> Turn unstructured files into typed JavaScript Object Notation (JSON) with one managed Application Programming Interface (API): standard output, blueprints, projects, async invoke.

## Index

- [1. Source And Scope](#1-source-and-scope)
- [2. One-Minute Version](#2-one-minute-version)
- [3. Component Map](#3-component-map)
  - Concepts
    - [01 Why And Flow](03data.01data-automation.01why-and-flow.md): pain, use cases, picture, reading results
    - [02 Standard Vs Custom Output](03data.01data-automation.02standard-vs-custom-output.md): modality defaults, blueprints
    - [03 Projects](03data.01data-automation.03projects.md): reusable config, stages, overrides
    - [04 Invoke And Poll](03data.01data-automation.04invoke-and-poll.md): async vs sync, `clientToken`, polling
    - [05 Knowledge Base Parser](03data.01data-automation.05kb-parser.md): Bedrock Data Automation (BDA) as Knowledge Base (KB) parsing strategy
  - Decide and defend
    - [98 Tradeoffs](03data.01data-automation.98tradeoffs.md): when to use, knobs, comparison, failure modes
    - [99 Interview](03data.01data-automation.99interview.md): Level 4 (L4) + Level 5 (L5) questions
- [4. Code Map](#4-code-map)
- [References](#references)

## 1. Source And Scope

Lectures AIP-C01 #38–#39 (slides p.76–91).

- **Scope**: Python + Terraform
  - Doc-first
  - Java not needed: not on a request path
- **Terraform**: [modules/03data_01data_automation](../../terraform/modules/03data_01data_automation/main.tf)
  - `a-invoice` blueprint
  - `a-docs` project
- **Code**: Python layers `app/*/_03data_01data_automation.py` (slice `bda`)
- **Numbers**: Bedrock Data Automation (BDA) docs, read 2026-11
  - Limits change often
  - "Check the quota page" where unsure

## 2. One-Minute Version

BDA is document-Artificial Intelligence (AI) as a service: point it at Simple Storage Service (S3), get typed JSON back.

- **What**
  - A managed service that turns unstructured files into structured output
  - Inputs: documents, images, audio, video
- **Why**
  - One API replaces Optical Character Recognition (OCR) + layout + Automatic Speech Recognition (ASR) + vision-Large Language Model (LLM) glue
  - Output is JSON (plus optional Markdown)
    - Ready for Retrieval-Augmented Generation (RAG) or downstream systems
- **How**
  - Standard output: modality defaults
    - text, summary, tables, transcript, scenes
  - Custom output: a blueprint lists fields
    - Each field has a type and a natural-language instruction
  - A project bundles standard-output config + blueprints
  - Async invoke returns an invocation Amazon Resource Name (ARN)
    - Inputs: input S3 Uniform Resource Identifier (URI), output S3 URI, project ARN, profile ARN
  - Poll the status
  - Then read `job_metadata.json` and the result JSON from S3
- **Catch**
  - Async only for large files and video ⇒ you own polling or EventBridge
  - Cross-region inference profile required ⇒ data may be processed in another Region of the geography
  - Per-page / per-minute pricing ⇒ cost scales with file size, not with fields
    - Check the pricing page
  - Blueprint fields are LLM-inferred ⇒ validate output, do not trust blindly
- 🗣 "BDA is document-AI as a service: point it at S3, get typed JSON back."
- 🗣 "Standard output tells you what is in the file; a blueprint tells you the fields you want."
- 🗣 "BDA can also be the parser of a knowledge base, so ingestion gets tables and transcripts for free."

## 3. Component Map

The files split the service into the output model, configuration, runtime, and RAG use.

```text
 01 why-and-flow ──► 02 output model ──► 03 projects
                                            │
                       05 kb-parser ◄── 04 invoke-and-poll
 98 tradeoffs · 99 interview  (decide and defend)
```

Read top to bottom: what goes in, what you configure, how you run it.

## 4. Code Map

Every concept file maps to one Python function in the new layer-first layout.

| Concept file | Python path | Function |
|---|---|---|
| 02 blueprint schema as code (invoice) | `app/domain/_03data_01data_automation.py` | `invoice_blueprint_schema` |
| 02 create blueprint (idempotent by name) | `app/infra/_03data_01data_automation.py` | `create_blueprint` |
| 03 create project (standard + custom) | `app/infra/_03data_01data_automation.py` | `create_data_automation_project` |
| 04 async invoke with `clientToken` | `app/infra/_03data_01data_automation.py` | `invoke_async` |
| 04 poll with backoff + deadline | `app/infra/_03data_01data_automation.py` | `wait_for_job` |
| 01 read job metadata + result JSON | `app/infra/_03data_01data_automation.py` | `read_job_result` |

| Concept file | Python path | Function |
|---|---|---|
| 04 end-to-end use case | `app/service/_03data_01data_automation.py` | `extract_invoice` |
| 04 Representational State Transfer (REST) (`/bda`) | `app/api/_03data_01data_automation.py` | `router`, `extract` |
| 03 settings (`A_BDA_`) | `app/config/_03data_01data_automation.py` | `BdaSettings` |
| 01 job status and result models | `app/domain/_03data_01data_automation.py` | `JobStatus`, `JobRef`, `JobResult` |

- **Gaps** (no repo code)
  - Sync `InvokeDataAutomation`
  - EventBridge notification wiring
  - Blueprint creation from sample (console "blueprint prompt")
  - KB parsing config (see [05 KB parser](03data.01data-automation.05kb-parser.md))

## References

- [aws-samples/amazon-bedrock-samples (data automation)](https://github.com/aws-samples/amazon-bedrock-samples)
- [Amazon Bedrock Data Automation user guide](https://docs.aws.amazon.com/bedrock/latest/userguide/bda.html)
- [BDA API: InvokeDataAutomationAsync](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_data-automation-runtime_InvokeDataAutomationAsync.html)
- [Amazon Web Services (AWS) Machine Learning (ML) blog: Bedrock Data Automation](https://aws.amazon.com/blogs/machine-learning/)
