"""Models and the blueprint schema as data. No SDK imports."""

import json
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class JobStatus(StrEnum):
    # GetDataAutomationStatus.status values
    CREATED = "Created"
    IN_PROGRESS = "InProgress"
    SUCCESS = "Success"
    SERVICE_ERROR = "ServiceError"  # BDA side: safe to resubmit
    CLIENT_ERROR = "ClientError"  # your input: resubmitting the same file fails again


TERMINAL = {JobStatus.SUCCESS, JobStatus.SERVICE_ERROR, JobStatus.CLIENT_ERROR}


@dataclass(frozen=True)
class JobRef:
    invocation_arn: str
    output_s3_uri: str  # prefix passed at submit time


@dataclass
class JobResult:
    status: JobStatus
    metadata: dict[str, Any] = field(default_factory=dict)  # job_metadata.json
    standard_output: list[dict[str, Any]] = field(default_factory=list)
    custom_output: list[dict[str, Any]] = field(default_factory=list)
    error: str = ""


def invoice_blueprint_schema() -> str:
    """Blueprint schema JSON, same content as the Terraform blueprint (the schema is passed as a string).

    Per property: type (string | number | integer | boolean | array | object), inferenceType
    (explicit = read from the file | inferred = derived), instruction (prompt-like, be specific).
    """
    return json.dumps(
        {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "description": "Supplier invoice",
            "class": "invoice",
            "type": "object",
            "properties": {
                "vendor": {"type": "string", "inferenceType": "explicit",
                           "instruction": "The legal name of the company that issued the invoice"},
                "total": {"type": "number", "inferenceType": "explicit",
                          "instruction": "The grand total to pay as a number without symbols"},
                "due_date": {"type": "string", "inferenceType": "explicit",
                             "instruction": "Payment due date in ISO 8601 (YYYY-MM-DD); empty if absent"},
            },
        }
    )
