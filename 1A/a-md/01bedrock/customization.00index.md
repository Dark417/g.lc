# customization Model Customization

> Train a private copy of a Bedrock base model on your data, then serve and call it.

## Index

- [1. Source And Scope](#1-source-and-scope)
- [2. One-Minute Version](#2-one-minute-version)
- [3. File Index](#3-file-index)
- [4. Code Map](#4-code-map)
- [5. Gaps](#5-gaps)
- [References](#references)

---

## 1. Source And Scope

This component covers the Amazon Web Services (AWS) customization workflow from dataset to serving.

- Lectures: AIP-C01 #11–#12 (slides p.25–28)
- Scope: Python + Terraform
- Terraform: `terraform/modules/01bedrock_02customization/`
  - Service role `a-customization-role`, app policy
  - Custom model and provisioned throughput only as commented examples: they cost money
- Code: Python `app/{config,api,domain,infra}/_01bedrock_02customization.py`
- Depth: a "before the model" topic

  ⇒ high level on training internals, full depth on the AWS workflow

- Numbers: Amazon Bedrock User Guide, "Customize your model", read 2026-11
  - Unless marked "order of magnitude"

## 2. One-Minute Version

Customization moves behavior into weights; serving it is the real cost.

- What
  - **Bedrock model customization**: train a private copy of a base model on your data
  - Types
    - fine-tuning (labeled pairs)
    - continued pre-training (unlabeled text)
    - distillation (teacher → student)
    - reinforcement fine-tuning (grader-driven)
- Why
  - Consistent style, format, or domain behavior
    - That prompting cannot reach at acceptable cost
  - A smaller tuned model can replace a larger general one (cheaper, faster)
- How

→ JavaScript Object Notation (JSON) Lines (JSONL) dataset to Simple Storage Service (S3) (`customization/train/`)  
→ `CreateModelCustomizationJob` (base model, hyperparameters, service role, output S3)  
→ poll until `Completed`; read loss metrics in S3  
→ serve it: provisioned throughput (most models) or on-demand deployment (some models)  
→ Converse with `modelId` = provisioned model Amazon Resource Name (ARN)

- Catch
  - Fine-tuning teaches behavior, not facts that change

  ⇒ Retrieval-Augmented Generation (RAG) for knowledge

  - Serving usually means provisioned throughput
    - Billed per hour while it exists
  - Data quality dominates
    - Hundreds to thousands of clean examples (order of magnitude)
- 🗣 "Prompt first, RAG for knowledge, fine-tune for behavior."
- 🗣 "The training job is cheap compared with the provisioned throughput you forget to delete."

## 3. File Index

Read top to bottom: why, what kinds, then the workflow in order.

- Foundations
  - [01 Why customize, picture](customization.01why-and-picture.md)
  - [02 Customization types](customization.02types.md)
  - [03 Low-Rank Adaptation (LoRA) in brief](customization.03lora.md)
- Workflow
  - [04 Data format and dataset upload](customization.04data-format.md)
  - [05 Training job and hyperparameters](customization.05job-hyperparameters.md)
  - [06 Serving a custom model](customization.06serving.md)
- Decide and defend
  - [98 Trade-offs: when to use, knobs, comparison, failure modes](customization.98tradeoffs.md)
  - [99 Interview questions](customization.99interview.md)

## 4. Code Map

All code is Python; this component has no Java.

| Concept file | Python (`app/`) |
|---|---|
| 02 customizable base models | `infra/…` `CustomizationShowcase.list_customizable_models` |
| 04 JSONL writer | `domain/…` `to_jsonl_line`, `write_jsonl` |
| 04 JSONL validator | `domain/…` `validate_jsonl` |
| 04 upload train/validation | `infra/…` `CustomizationShowcase.upload_dataset` |
| 05 create job | `infra/…` `CustomizationShowcase.create_customization_job` |
| 05 poll job | `infra/…` `CustomizationShowcase.wait_for_job` |

| Concept file | Python (`app/`) |
|---|---|
| 05 metrics in S3 | `infra/…` `CustomizationShowcase.metrics_location` |
| 05 list custom models | `infra/…` `CustomizationShowcase.list_custom_models` |
| 06 provisioned throughput | `infra/…` `create_provisioned_throughput`, `wait_for_provisioned`, `delete_provisioned_throughput` |
| 06 on-demand deployment | `infra/…` `CustomizationShowcase.create_on_demand_deployment` |
| 06 call the custom model | `infra/…` `CustomizationShowcase.converse_custom` |
| Representational State Transfer (REST) (read-only + validate) | `api/_01bedrock_02customization.py` `router` (`/customization`) |

- `…` = the same component module, e.g. `infra/_01bedrock_02customization.py`.

## 5. Gaps

These topics are documented but not coded.

- Distillation and reinforcement fine-tuning job configs (`customizationConfig`)
- Custom Model Import
- Evaluation of the custom model vs baseline → [evaluations](../04safety/evaluations.00index.md)

## References

- [aws-samples/amazon-bedrock-samples: custom-models](https://github.com/aws-samples/amazon-bedrock-samples/tree/main/custom-models)
- [Amazon Bedrock User Guide: Customize your model to improve its performance for your use case](https://docs.aws.amazon.com/bedrock/latest/userguide/custom-models.html)
- [Amazon Bedrock User Guide: Prepare data for fine-tuning](https://docs.aws.amazon.com/bedrock/latest/userguide/model-customization-prepare.html)
- [Amazon Bedrock User Guide: Provisioned Throughput](https://docs.aws.amazon.com/bedrock/latest/userguide/prov-throughput.html)
- [Hu et al., "LoRA: Low-Rank Adaptation of Large Language Models", 2021](https://arxiv.org/abs/2106.09685)
