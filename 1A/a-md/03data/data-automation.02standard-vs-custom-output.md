# data-automation Standard Vs Custom Output

> Standard output tells you what is in the file; a blueprint tells you the fields you want.

## Index

- [1. Standard Output](#1-standard-output)
- [2. Custom Output (Blueprints)](#2-custom-output-blueprints)
  - [2.1 Schema Shape](#21-schema-shape)
  - [2.2 Creating A Blueprint](#22-creating-a-blueprint)

## 1. Standard Output

Standard output is always on per modality; you only toggle granularity and formats.

- **Document**
  - Text granularity: DOCUMENT / PAGE / ELEMENT / WORD / LINE
  - Text formats: Markdown / Hypertext Markup Language (HTML) / Comma-Separated Values (CSV)
- **Image**: summary, captions, categories (Interactive Advertising Bureau (IAB)), text
- **Audio**: transcript (speaker and channel labels), summary, topics
- **Video**: summary, chapters, transcript, text in frames

```python
# app/infra/_03data_01data_automation.py  (inside create_data_automation_project)
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
```

- **Catch**: finer granularity and generative fields grow output size and cost

## 2. Custom Output (Blueprints)

A blueprint is a typed field list with one prompt-like instruction per field.

### 2.1 Schema Shape

- Schema is JavaScript Object Notation (JSON)-schema-like: `class`, `description`, `properties`
- Each property has three parts
  - `type`: string, number, integer, boolean, array, object
  - `inferenceType`: `explicit` = in the file; `inferred` = derived
  - `instruction`: what to extract, prompt-like
- Blueprint `type` = DOCUMENT, IMAGE, AUDIO or VIDEO
- Stages
  - DEVELOPMENT: editable
  - LIVE: what projects should pin
- Prefer explicit instructions
  - Example: "return the amount in the invoice footer as a number"

```python
# app/domain/_03data_01data_automation.py
def invoice_blueprint_schema() -> str:
    # Same content as the Terraform blueprint; the schema is passed as a string
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
```

- **Catch**: fields are inferred by a model
  - Keep per-field `confidence`
  - Validate against a Pydantic model

### 2.2 Creating A Blueprint

Terraform owns the blueprint in production; the Software Development Kit (SDK) path is for experiments.

- Names are unique per account
  - A rerun hits `ConflictException`
  - The code looks the Amazon Resource Name (ARN) up instead of failing
- `clientToken` is derived from the name ⇒ a retried create is idempotent

```python
# app/infra/_03data_01data_automation.py
def create_blueprint(name: str | None = None) -> str:
    name = name or get_bda_settings().blueprint_name
    try:
        resp = _control().create_blueprint(
            blueprintName=name,
            type="DOCUMENT",  # DOCUMENT | IMAGE | AUDIO | VIDEO
            blueprintStage="LIVE",  # DEVELOPMENT | LIVE (default LIVE)
            schema=invoice_blueprint_schema(),
            clientToken=str(uuid.uuid5(uuid.NAMESPACE_URL, f"blueprint/{name}")),  # idempotent retry
        )
        return resp["blueprint"]["blueprintArn"]
    except ClientError as e:
        if e.response["Error"]["Code"] != "ConflictException":
            raise
        for page in _control().get_paginator("list_blueprints").paginate(resourceOwner="ACCOUNT"):
            for bp in page["blueprints"]:
                if bp.get("blueprintName") == name:
                    return bp["blueprintArn"]  # already exists: reuse it
        raise
```

- **Catch**: an edit in DEVELOPMENT must not reach production
  - Pin LIVE in the project ([03 Projects](data-automation.03projects.md))
