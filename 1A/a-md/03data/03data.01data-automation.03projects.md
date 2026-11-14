# 03data.01data-automation Projects

> A project is the reusable config you invoke: standard output, blueprints, Personally Identifiable Information (PII) detection, and stage.

## Index

- [1. What A Project Holds](#1-what-a-project-holds)
- [2. Creating A Project](#2-creating-a-project)
- [3. Settings](#3-settings)

## 1. What A Project Holds

A project bundles everything an invoke needs except the input and output locations.

- **Standard-output settings**: per modality
- **Custom blueprints**: one or more
  - A document may carry several blueprints
  - Bedrock Data Automation (BDA) picks the matching one
  - A fallback blueprint is available
- **Sensitive-data detection** (optional): PII detect or redact
  - See [04safety.02pii-redaction](../04safety/04safety.02pii-redaction.00index.md)
- **Stage**: DEVELOPMENT or LIVE
  - Pass the stage at invoke time
- **Override configuration**
  - Modality routing
  - Document splitter
  - Audio language settings

## 2. Creating A Project

The project pins the blueprint stage, so the invoke cannot drift to an unreviewed edit.

```python
# app/infra/_03data_01data_automation.py
def create_data_automation_project(blueprint_arn: str, name: str | None = None) -> str:
    name = name or get_bda_settings().project_name
    resp = _control().create_data_automation_project(
        projectName=name,
        projectDescription="Document extraction",
        projectStage="LIVE",  # DEVELOPMENT | LIVE
        projectType="ASYNC",  # ASYNC | SYNC
        standardOutputConfiguration={...},  # see 02 standard output
        customOutputConfiguration={
            # blueprint stage is pinned here (LIVE), not at invoke time
            "blueprints": [{"blueprintArn": blueprint_arn, "blueprintStage": "LIVE"}]
        },
        clientToken=str(uuid.uuid5(uuid.NAMESPACE_URL, f"project/{name}")),
    )
    return resp["projectArn"]
```

- **Catch**: the project is what you invoke
  - Pinning DEVELOPMENT ⇒ output changes after any blueprint edit

## 3. Settings

Slice settings mirror the Terraform names; Amazon Resource Names (ARNs) come from Terraform outputs.

```python
# app/config/_03data_01data_automation.py
class BdaSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="A_BDA_", env_file=".env", extra="ignore")

    project_name: str = "a-docs"
    blueprint_name: str = "a-invoice"
    project_arn: str = ""  # terraform output bda_project_arn
    blueprint_arn: str = ""  # terraform output bda_blueprint_arn
    # Cross-region inference profile BDA requires. Verify the exact id/Region for your account.
    profile_arn: str = ""  # arn:aws:bedrock:<region>:<account>:data-automation-profile/us.data-automation-v1
    input_prefix: str = "bda/input/"
    output_prefix: str = "bda/output/"
    stage: str = "LIVE"  # LIVE | DEVELOPMENT: which project stage to run
    poll_deadline_s: float = 600.0
```

- **Catch**: `profile_arn` is a cross-region inference profile
  - Data may be processed elsewhere in the geography
  - Confirm residency rules first
