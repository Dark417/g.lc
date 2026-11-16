# customization Why Customize, Picture

> Why move behavior from prompts into weights, and how the Amazon Web Services (AWS) pieces connect.

## Index

- [1. Why Customize](#1-why-customize)
  - [1.1 Prompting Limits](#11-prompting-limits)
  - [1.2 What Customization Changes](#12-what-customization-changes)
  - [1.3 Limit](#13-limit)
- [2. Picture](#2-picture)
- [3. Three AWS Clients](#3-three-aws-clients)

Back to [00index](customization.00index.md).

---

## 1. Why Customize

Prompting has a per-call cost and a consistency ceiling.

### 1.1 Prompting Limits

- Long instructions and many examples on every call cost tokens and latency
- Some styles or formats stay inconsistent even with good prompts

### 1.2 What Customization Changes

- Customization moves that behavior into weights
  - Shorter prompts
  - More consistent output
  - Sometimes a smaller model

### 1.3 Limit

- Weights freeze at training time

⇒ facts that change weekly belong in retrieval  
→ see [embeddings](../02rag/embeddings.00index.md) and [knowledge-bases](../02rag/knowledge-bases.00index.md)

## 2. Picture

Data in Simple Storage Service (S3), a training job, a custom model, then one of two serving paths.

```text
S3 a-ai-data-<acct>/customization/
   train/train.jsonl ───┐
   validation/val.jsonl ┤
                        ▼
CreateModelCustomizationJob ── role a-customization-role (reads train/, writes output/, KMS)
   base model + hyperparameters
                        │  hours (order of magnitude)
                        ▼
custom model  arn:...:custom-model/...          + metrics in customization/output/
                        │
   ┌────────────────────┴─────────────────────┐
   ▼                                          ▼
CreateProvisionedModelThroughput      CreateCustomModelDeployment (on-demand, some models)
   arn:...:provisioned-model/...          arn:...:custom-model-deployment/...
                        │
                        ▼
Converse(modelId = provisioned/deployment ARN)
```

- Notice: training ends at a custom model Amazon Resource Name (ARN), which is not yet callable.

## 3. Three AWS Clients

- `bedrock` (control plane): jobs, custom models, provisioned throughput
- `s3`: training and validation data, output metrics
- `bedrock-runtime`: calling the served model
- Nothing runs at import time.
  - The Application Programming Interface (API) exposes only read/validate routes.

```python
# app/infra/_01bedrock_02customization.py
class CustomizationShowcase:
    def __init__(self, settings: CustomizationSettings | None = None) -> None:
        self.settings = settings or get_customization_settings()

    @property
    def control(self) -> Any:
        return aws.client("bedrock")          # jobs, custom models, provisioned throughput

    @property
    def s3(self) -> Any:
        return aws.client("s3")               # datasets and metrics

    @property
    def runtime(self) -> Any:
        return aws.client("bedrock-runtime")  # Converse against the served model

    def _uri(self, key: str) -> str:
        return f"s3://{self.settings.bucket}/{self.settings.prefix}/{key}"
```

```python
# app/config/_01bedrock_02customization.py
class CustomizationSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="A_CUSTOMIZATION_", env_file=".env", extra="ignore")

    base_model_id: str = "amazon.nova-micro-v1:0:128k"  # terraform var customization_base_model_id
    role_arn: str = "arn:aws:iam::ACCOUNT_ID:role/a-customization-role"  # terraform output customization_role_arn
    bucket: str = "a-ai-data-ACCOUNT_ID"  # terraform output data_bucket (base_data_bucket)
    prefix: str = "customization"         # train/, validation/, output/ under it
    kms_key_arn: str = ""                 # encrypts the custom model artifacts
```

- Catch: training bills per token processed.
- Catch: provisioned throughput bills per model unit per hour.
  - From creation until deletion.
