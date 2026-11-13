"""Use case: extract invoice fields from an uploaded file."""

from typing import Any

from app.a03_01_data_automation.config import get_bda_settings
from app.a03_01_data_automation.domain import JobStatus
from app.a03_01_data_automation.infra import invoke_async, read_job_result, wait_for_job
from app.shared.config import get_settings


def extract_invoice(key: str, run_id: str | None = None) -> dict[str, Any]:
    """Submit, wait, read, and return the custom-output fields of the first result.

    Catch: returns an error dict instead of raising for ClientError so the caller can route it to review.
    """
    uri = f"s3://{get_settings().data_bucket}/{get_bda_settings().input_prefix}{key}"
    job = invoke_async(uri, run_id)
    status, resp = wait_for_job(job)
    result = read_job_result(status, resp)
    if result.status is not JobStatus.SUCCESS:
        return {"status": result.status.value, "error": result.error}
    fields = result.custom_output[0].get("inference_result", {}) if result.custom_output else {}
    return {"status": "Success", "invocation_arn": job.invocation_arn, "fields": fields}
