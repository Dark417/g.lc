"""Model customization showcase (boto3): dataset -> job -> metrics -> serving -> Converse.

- Control plane "bedrock" for jobs, custom models, provisioned throughput; "s3" for data; "bedrock-runtime" to call.
- COST: training jobs bill per token processed; provisioned throughput bills per model unit per HOUR from
  creation until deletion. Nothing here runs at import time, and the API exposes only read/validate routes.
"""

import time
import uuid
from typing import Any

from app.a01_02_customization.config import CustomizationSettings, get_customization_settings
from app.a01_02_customization.domain import (
    DatasetFormat,
    TrainingExample,
    ValidationReport,
    validate_jsonl,
    write_jsonl,
)
from app.shared import aws
from app.shared.retry import backoff

TERMINAL_JOB = {"Completed", "Failed", "Stopped"}


class CustomizationError(Exception):
    pass


class CustomizationShowcase:
    def __init__(self, settings: CustomizationSettings | None = None) -> None:
        self.settings = settings or get_customization_settings()

    @property
    def control(self) -> Any:
        return aws.client("bedrock")

    @property
    def s3(self) -> Any:
        return aws.client("s3")

    @property
    def runtime(self) -> Any:
        return aws.client("bedrock-runtime")

    def _uri(self, key: str) -> str:
        return f"s3://{self.settings.bucket}/{self.settings.prefix}/{key}"

    # ================================================================ 1.3 which models

    def list_customizable_models(self, customization: str = "FINE_TUNING") -> list[dict[str, Any]]:
        """Shows: ListFoundationModels(byCustomizationType=...) = which base models support which type here.
        Values: FINE_TUNING | CONTINUED_PRE_TRAINING | DISTILLATION. Catch: per Region; customizable IDs
        often carry a context suffix (":128k") that differs from the on-demand model ID.
        """
        resp = self.control.list_foundation_models(byCustomizationType=customization)
        return [
            {"model_id": m["modelId"], "provider": m.get("providerName"), "customizations": m.get("customizationsSupported", [])}
            for m in resp["modelSummaries"]
        ]

    # ================================================================ 1.5 dataset

    def upload_dataset(
        self, train: list[TrainingExample], validation: list[TrainingExample]
    ) -> tuple[str, str, ValidationReport]:
        """Shows: write JSONL in the base model's format, validate locally, upload to customization/train|validation.
        Catch: validation must not overlap training (we check exact duplicates across both); bucket is SSE-KMS.
        """
        fmt = DatasetFormat(self.settings.dataset_format)
        train_bytes, val_bytes = write_jsonl(train, fmt), write_jsonl(validation, fmt)
        report = validate_jsonl(train_bytes, fmt, self.settings.max_record_chars)
        val_report = validate_jsonl(val_bytes, fmt, self.settings.max_record_chars)
        report.errors += [f"validation {e}" for e in val_report.errors]
        overlap = {(e.prompt, e.completion) for e in train} & {(e.prompt, e.completion) for e in validation}
        if overlap:
            report.errors.append(f"{len(overlap)} examples appear in both train and validation")
        if not report.ok:
            raise CustomizationError("; ".join(report.errors[:20]))
        train_key = f"{self.settings.prefix}/train/train.jsonl"
        val_key = f"{self.settings.prefix}/validation/validation.jsonl"
        for key, body in ((train_key, train_bytes), (val_key, val_bytes)):
            self.s3.put_object(Bucket=self.settings.bucket, Key=key, Body=body, ContentType="application/jsonl")
        return self._uri("train/train.jsonl"), self._uri("validation/validation.jsonl"), report

    # ================================================================ 1.6 job

    def create_customization_job(self, job_name: str, custom_model_name: str, train_uri: str, validation_uri: str) -> str:
        """Shows: CreateModelCustomizationJob with every important field. Returns the job ARN.
        Use once per training run. Catch: starts paid training; clientRequestToken (from job_name) makes a
        retried call return the same job instead of training twice; job and model names must be unique.
        """
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
                "epochCount": self.settings.epoch_count,  # passes over the data; more -> overfitting risk
                "batchSize": self.settings.batch_size,  # examples per update; some models fix it
                "learningRate": self.settings.learning_rate,  # step size; too high -> unstable loss
                # "learningRateWarmupSteps": "10",  # some models
            },
            "clientRequestToken": str(uuid.uuid5(uuid.NAMESPACE_URL, f"customization/{job_name}")),
            "jobTags": [{"key": "Component", "value": "01.02"}],
            "customModelTags": [{"key": "Component", "value": "01.02"}],
            # "vpcConfig": {"subnetIds": [...], "securityGroupIds": [...]},  # keep data access inside the VPC
            # Distillation instead: customizationType="DISTILLATION" +
            # "customizationConfig": {"distillationConfig": {"teacherModelConfig": {"teacherModelIdentifier": "..."}}}
        }
        if self.settings.kms_key_arn:
            kwargs["customModelKmsKeyId"] = self.settings.kms_key_arn  # encrypt the model artifacts with the CMK
        return self.control.create_model_customization_job(**kwargs)["jobArn"]

    def wait_for_job(self, job_arn: str, poll_cap_s: float = 300.0) -> dict[str, Any]:
        """Shows: poll GetModelCustomizationJob with capped exponential backoff until a terminal status.
        Status: InProgress | Completed | Failed | Stopping | Stopped. Catch: hours long ⇒ in production use an
        EventBridge rule on the job state change instead of a polling process.
        """
        deadline = time.monotonic() + self.settings.job_poll_timeout_s
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

    def metrics_location(self, job_arn: str) -> dict[str, str]:
        """Shows: where step-wise training and validation metrics (CSV) are written.
        Catch: the exact sub-folder and file names are per job/model; list the prefix rather than hard-coding files.
        """
        job_id = job_arn.rsplit("/", 1)[-1]
        prefix = f"{self.settings.prefix}/output/model-customization-job-{job_id}/"
        resp = self.s3.list_objects_v2(Bucket=self.settings.bucket, Prefix=prefix)
        return {"prefix": f"s3://{self.settings.bucket}/{prefix}", "files": ",".join(o["Key"] for o in resp.get("Contents", []))}

    def list_custom_models(self) -> list[dict[str, str]]:
        """Shows: ListCustomModels with the boto3 paginator, newest first."""
        out: list[dict[str, str]] = []
        pages = self.control.get_paginator("list_custom_models").paginate(sortBy="CreationTime", sortOrder="Descending")
        for page in pages:
            out += [
                {"arn": m["modelArn"], "name": m["modelName"], "base": m.get("baseModelName", ""), "status": m.get("modelStatus", "")}
                for m in page.get("modelSummaries", [])
            ]
        return out

    # ================================================================ 1.7 serving

    def create_provisioned_throughput(self, custom_model_arn: str, name: str) -> str:
        """Shows: CreateProvisionedModelThroughput for a custom model (1 model unit, no commitment).

        !!! COST WARNING: hourly billing starts now and runs until delete_provisioned_throughput, with or
        without traffic. commitmentDuration "OneMonth" | "SixMonths" is cheaper per hour but cannot be cancelled.
        """
        return self.control.create_provisioned_model_throughput(
            provisionedModelName=name,
            modelId=custom_model_arn,
            modelUnits=1,  # throughput scales with units; size from measured tokens/min
            # commitmentDuration="OneMonth",  # omit = no commitment (hourly, deletable any time)
            clientRequestToken=str(uuid.uuid5(uuid.NAMESPACE_URL, f"pt/{name}")),
            tags=[{"key": "Component", "value": "01.02"}, {"key": "DeleteAfterTest", "value": "true"}],
        )["provisionedModelArn"]

    def wait_for_provisioned(self, provisioned_arn: str, timeout_s: int = 3600) -> str:
        """Shows: poll until InService (Creating | InService | Updating | Failed); provisioning takes minutes."""
        deadline = time.monotonic() + timeout_s
        attempt = 0
        while time.monotonic() < deadline:
            pt = self.control.get_provisioned_model_throughput(provisionedModelId=provisioned_arn)
            if pt["status"] == "InService":
                return pt["status"]
            if pt["status"] == "Failed":
                raise CustomizationError(pt.get("failureMessage", "provisioning failed"))
            time.sleep(max(15.0, backoff(attempt, base=15.0, cap=120.0)))
            attempt += 1
        raise CustomizationError("provisioned throughput not InService in time")

    def delete_provisioned_throughput(self, provisioned_arn: str) -> None:
        """Shows: the call that stops the bill. Run it right after tests (not possible during a commitment term)."""
        self.control.delete_provisioned_model_throughput(provisionedModelId=provisioned_arn)

    def create_on_demand_deployment(self, custom_model_arn: str, name: str) -> str:
        """Shows: CreateCustomModelDeployment = on-demand (per-token) serving for SUPPORTED custom models.
        Catch: check model support; unsupported models still need provisioned throughput.
        """
        return self.control.create_custom_model_deployment(
            modelDeploymentName=name,
            modelArn=custom_model_arn,
            clientRequestToken=str(uuid.uuid5(uuid.NAMESPACE_URL, f"deploy/{name}")),
            tags=[{"key": "Component", "value": "01.02"}],
        )["customModelDeploymentArn"]

    def converse_custom(self, prompt: str, model_arn: str | None = None) -> dict[str, Any]:
        """Shows: Converse against the custom model: modelId = provisioned model ARN (or deployment ARN).
        Catch: the tuned model expects prompts shaped like its training data (same system text, same format).
        """
        arn = model_arn or self.settings.provisioned_model_arn
        if not arn:
            raise CustomizationError("no provisioned/deployment ARN configured (A_CUSTOMIZATION_PROVISIONED_MODEL_ARN)")
        resp = self.runtime.converse(
            modelId=arn,
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": 512, "temperature": 0.0},
        )
        return {
            "text": "".join(b.get("text", "") for b in resp["output"]["message"]["content"]),
            "stop_reason": resp["stopReason"],
            "usage": resp.get("usage", {}),
        }
