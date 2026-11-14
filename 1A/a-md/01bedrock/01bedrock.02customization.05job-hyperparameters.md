# 01bedrock.02customization Training Job And Hyperparameters

> Create the paid job safely, tune its hyperparameters, and read the loss curves.

## Index

- [1. Hyperparameters](#1-hyperparameters)
  - [1.1 The Knobs](#11-the-knobs)
  - [1.2 Reading Loss](#12-reading-loss)
- [2. Creating The Job](#2-creating-the-job)
- [3. Waiting For The Job](#3-waiting-for-the-job)
- [4. Metrics And Custom Models](#4-metrics-and-custom-models)

Back to [00index](01bedrock.02customization.00index.md).

---

## 1. Hyperparameters

Hyperparameters are a string map; names and ranges are per model.

### 1.1 The Knobs

- Passed as a string map in `hyperParameters`
- **`epochCount`**: passes over the data
  - More = fits better, until it memorizes (overfits)
- **`batchSize`**: examples per update
  - Larger = smoother updates, more memory
  - Some models fix it
- **`learningRate`**: update step size
  - Too high = unstable loss
  - Too low = no change
- **`learningRateWarmupSteps`** (some models): ramp-up steps

```python
# app/config/_01bedrock_02customization.py
# Hyperparameters: strings, names and ranges per base model (check the model's customization page).
epoch_count: str = "2"
batch_size: str = "1"
learning_rate: str = "0.00001"
```

### 1.2 Reading Loss

Compare training and validation loss per epoch.

- Both falling ⇒ learning
- Validation rising while training falls

⇒ overfitting  
→ fewer epochs or more data

## 2. Creating The Job

`CreateModelCustomizationJob` starts paid training and returns the job Amazon Resource Name (ARN).

- Every important field
  - service role, base model, type
  - training, validation, output Simple Storage Service (S3) Uniform Resource Identifiers (URIs)
  - hyperparameters
  - idempotency token, tags, optional Key Management Service (KMS) and Virtual Private Cloud (VPC)

```python
# app/infra/_01bedrock_02customization.py
def create_customization_job(self, job_name, custom_model_name, train_uri, validation_uri) -> str:
    kwargs: dict[str, Any] = {
        "jobName": job_name,
        "customModelName": custom_model_name,
        "roleArn": self.settings.role_arn,  # a-customization-role: reads train/validation, writes output
        "baseModelIdentifier": self.settings.base_model_id,
        "customizationType": "FINE_TUNING",  # | CONTINUED_PRE_TRAINING | DISTILLATION | REINFORCEMENT_FINE_TUNING
        "trainingDataConfig": {"s3Uri": train_uri},
        "validationDataConfig": {"validators": [{"s3Uri": validation_uri}]},  # validation loss per epoch
        "outputDataConfig": {"s3Uri": self._uri("output/")},  # metrics land here
        "hyperParameters": {  # string map; names/ranges per base model
            "epochCount": self.settings.epoch_count,
            "batchSize": self.settings.batch_size,
            "learningRate": self.settings.learning_rate,
            # "learningRateWarmupSteps": "10",  # some models
        },
        # same job_name -> same token -> a retried call returns the same job, not a second paid run
        "clientRequestToken": str(uuid.uuid5(uuid.NAMESPACE_URL, f"customization/{job_name}")),
        "jobTags": [{"key": "Component", "value": "01.02"}],
        "customModelTags": [{"key": "Component", "value": "01.02"}],
        # "vpcConfig": {"subnetIds": [...], "securityGroupIds": [...]},  # keep data access inside the VPC
    }
    if self.settings.kms_key_arn:
        kwargs["customModelKmsKeyId"] = self.settings.kms_key_arn  # encrypt the model artifacts with the CMK
    return self.control.create_model_customization_job(**kwargs)["jobArn"]
```

- Catch: the call starts paid training.
- Catch: job and model names must be unique.

## 3. Waiting For The Job

- Status: `InProgress` | `Completed` | `Failed` | `Stopping` | `Stopped`
- Poll with capped exponential backoff until a terminal status.

```python
# app/infra/_01bedrock_02customization.py
TERMINAL_JOB = {"Completed", "Failed", "Stopped"}

def wait_for_job(self, job_arn: str, poll_cap_s: float = 300.0) -> dict[str, Any]:
    deadline = time.monotonic() + self.settings.job_poll_timeout_s  # 6 h default: jobs take hours
    attempt = 0
    while time.monotonic() < deadline:
        job = self.control.get_model_customization_job(jobIdentifier=job_arn)
        if job["status"] in TERMINAL_JOB:
            if job["status"] != "Completed":
                raise CustomizationError(f"job {job['status']}: {job.get('failureMessage', '')}")
            return {
                "status": job["status"],
                "custom_model_arn": job.get("outputModelArn"),
                "training_loss": job.get("trainingMetrics", {}).get("trainingLoss"),
                "validation_loss": [v.get("validationLoss") for v in job.get("validationMetrics", [])],
            }
        time.sleep(max(10.0, backoff(attempt, base=10.0, cap=poll_cap_s)))
        attempt += 1
    raise CustomizationError(f"job not finished after {self.settings.job_poll_timeout_s}s")
```

- Catch: jobs run for hours (order of magnitude).
  - In production use an EventBridge rule on the job state change.
  - Not a polling process.

## 4. Metrics And Custom Models

- Step-wise training and validation metrics (Comma-Separated Values (CSV)) land under `customization/output/`.
- `ListCustomModels` lists finished models, newest first.

```python
# app/infra/_01bedrock_02customization.py
def metrics_location(self, job_arn: str) -> dict[str, str]:
    job_id = job_arn.rsplit("/", 1)[-1]
    prefix = f"{self.settings.prefix}/output/model-customization-job-{job_id}/"
    resp = self.s3.list_objects_v2(Bucket=self.settings.bucket, Prefix=prefix)  # list, don't hard-code
    return {"prefix": f"s3://{self.settings.bucket}/{prefix}",
            "files": ",".join(o["Key"] for o in resp.get("Contents", []))}

def list_custom_models(self) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    pages = self.control.get_paginator("list_custom_models").paginate(sortBy="CreationTime", sortOrder="Descending")
    for page in pages:
        out += [{"arn": m["modelArn"], "name": m["modelName"],
                 "base": m.get("baseModelName", ""), "status": m.get("modelStatus", "")}
                for m in page.get("modelSummaries", [])]
    return out
```

- Catch: the exact sub-folder and file names are per job and model.
  - List the prefix rather than hard-coding files.
