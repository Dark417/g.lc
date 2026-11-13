"""BDA SDK calls: config as code (create_*), async invoke, polling, reading results from S3."""

import json
import time
import uuid
from typing import Any

from botocore.exceptions import ClientError

from app.a03_01_data_automation.config import get_bda_settings
from app.a03_01_data_automation.domain import (
    TERMINAL,
    JobRef,
    JobResult,
    JobStatus,
    invoice_blueprint_schema,
)
from app.shared.aws import client
from app.shared.config import get_settings
from app.shared.retry import backoff


def _control() -> Any:
    return client("bedrock-data-automation")  # control plane: blueprints, projects


def _runtime() -> Any:
    return client("bedrock-data-automation-runtime")  # invoke + status


def _s3() -> Any:
    return client("s3")


# ---------------------------------------------------------------- 1.3 blueprint (custom output)


def create_blueprint(name: str | None = None) -> str:
    """Create the invoice blueprint; return its ARN. Use when Terraform does not own it (experiments).

    Catch: names are unique per account, so a rerun hits ConflictException; we look the ARN up instead.
    """
    name = name or get_bda_settings().blueprint_name
    try:
        resp = _control().create_blueprint(
            blueprintName=name,
            type="DOCUMENT",  # DOCUMENT | IMAGE | AUDIO | VIDEO
            blueprintStage="LIVE",  # DEVELOPMENT | LIVE (default LIVE)
            schema=invoice_blueprint_schema(),
            clientToken=str(uuid.uuid5(uuid.NAMESPACE_URL, f"blueprint/{name}")),  # idempotent retry
            # encryptionConfiguration={"kmsKeyId": "<cmk arn>"},  # optional CMK for the blueprint
        )
        return resp["blueprint"]["blueprintArn"]
    except ClientError as e:
        if e.response["Error"]["Code"] != "ConflictException":
            raise
        for page in _control().get_paginator("list_blueprints").paginate(resourceOwner="ACCOUNT"):
            for bp in page["blueprints"]:
                if bp.get("blueprintName") == name:
                    return bp["blueprintArn"]
        raise


# ---------------------------------------------------------------- 1.4 project


def create_data_automation_project(blueprint_arn: str, name: str | None = None) -> str:
    """Create a project with document standard output + one blueprint; return its ARN.

    Catch: the project is what you invoke; blueprint stage is pinned here (LIVE), not at invoke time.
    """
    name = name or get_bda_settings().project_name
    resp = _control().create_data_automation_project(
        projectName=name,
        projectDescription="Document extraction",
        projectStage="LIVE",  # DEVELOPMENT | LIVE
        projectType="ASYNC",  # ASYNC | SYNC
        standardOutputConfiguration={
            "document": {
                "extraction": {
                    "granularity": {"types": ["DOCUMENT", "PAGE"]},  # + ELEMENT | WORD | LINE
                    "boundingBox": {"state": "DISABLED"},  # ENABLED adds coordinates
                },
                "generativeField": {"state": "DISABLED"},  # ENABLED adds a model summary (extra cost)
                "outputFormat": {
                    "textFormat": {"types": ["MARKDOWN"]},  # PLAIN_TEXT | MARKDOWN | HTML | CSV
                    "additionalFileFormat": {"state": "DISABLED"},
                },
            }
        },
        customOutputConfiguration={
            "blueprints": [{"blueprintArn": blueprint_arn, "blueprintStage": "LIVE"}]
        },
        clientToken=str(uuid.uuid5(uuid.NAMESPACE_URL, f"project/{name}")),
    )
    return resp["projectArn"]


# ---------------------------------------------------------------- 1.5 async invoke


def invoke_async(input_s3_uri: str, run_id: str | None = None) -> JobRef:
    """Submit one async job; the same run_id always maps to the same clientToken (no double billing).

    Catch: dataAutomationProfileArn is required; output s3Uri is a prefix, BDA adds <invocation-id>/.
    """
    cfg = get_bda_settings()
    bucket = get_settings().data_bucket
    run_id = run_id or uuid.uuid4().hex
    output_uri = f"s3://{bucket}/{cfg.output_prefix}{run_id}/"
    resp = _runtime().invoke_data_automation_async(
        clientToken=run_id,  # idempotency: a retry with the same token returns the same invocation
        inputConfiguration={"s3Uri": input_s3_uri},
        outputConfiguration={"s3Uri": output_uri},
        dataAutomationConfiguration={
            "dataAutomationProjectArn": cfg.project_arn,
            "stage": cfg.stage,  # LIVE | DEVELOPMENT
        },
        dataAutomationProfileArn=cfg.profile_arn,
        # encryptionConfiguration={"kmsKeyId": "..."}  # optional: CMK for the output
        # notificationConfiguration={"eventBridgeConfiguration": {"eventBridgeEnabled": True}}  # push, no polling
    )
    return JobRef(invocation_arn=resp["invocationArn"], output_s3_uri=output_uri)


def wait_for_job(job: JobRef, deadline_s: float | None = None) -> tuple[JobStatus, dict[str, Any]]:
    """Poll GetDataAutomationStatus with full-jitter backoff until terminal or deadline.

    Use for demos and low volume; at volume use EventBridge. Catch: ServiceError may be retried, ClientError not.
    """
    end = time.monotonic() + (deadline_s or get_bda_settings().poll_deadline_s)
    attempt = 0
    while True:
        resp = _runtime().get_data_automation_status(invocationArn=job.invocation_arn)
        status = JobStatus(resp["status"])
        if status in TERMINAL:
            return status, resp
        if time.monotonic() >= end:
            raise TimeoutError(f"{job.invocation_arn} still {status} after deadline")
        time.sleep(backoff(attempt, base=1.0, cap=15.0))
        attempt += 1


# ---------------------------------------------------------------- 1.2 read results


def _read_json(s3_uri: str) -> dict[str, Any]:
    bucket, _, key = s3_uri.removeprefix("s3://").partition("/")
    body = _s3().get_object(Bucket=bucket, Key=key)["Body"].read()
    return json.loads(body)


def read_job_result(status: JobStatus, status_resp: dict[str, Any]) -> JobResult:
    """Read job_metadata.json, then every result.json it points to (standard + custom output).

    Catch: the status response gives the metadata file URI; the result paths come from the metadata.
    """
    if status is not JobStatus.SUCCESS:
        return JobResult(status=status, error=f"{status_resp.get('errorType')}: {status_resp.get('errorMessage')}")
    metadata = _read_json(status_resp["outputConfiguration"]["s3Uri"])
    result = JobResult(status=status, metadata=metadata)
    # Metadata shape (verify against a real run): output_metadata[] -> segment_metadata[] with
    # standard_output_path and custom_output_path.
    for asset in metadata.get("output_metadata", []):
        for seg in asset.get("segment_metadata", []):
            if seg.get("standard_output_path"):
                result.standard_output.append(_read_json(seg["standard_output_path"]))
            if seg.get("custom_output_path"):
                result.custom_output.append(_read_json(seg["custom_output_path"]))
    return result
