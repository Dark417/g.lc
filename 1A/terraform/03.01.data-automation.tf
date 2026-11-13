# 03.01 data-automation — Bedrock Data Automation (BDA), lectures 38-39.
# Creates: one custom blueprint (invoice: vendor, total, due_date) + one project that uses it, plus the
#          app policy for async invoke and status polling.
# Used by: python app/a03_01_data_automation (slice "bda").
#
# S3: input bda/input/ and output bda/output/ in the shared bucket. The app role already has s3:Get/Put on
#      the whole bucket from 00.05, so no extra S3 policy here.
# Catch: BDA reads the input and writes the output with the CALLER's permissions (the app role), so no
#      service role is needed. Output is KMS-encrypted via the project encryption_configuration.

resource "aws_bedrockdataautomation_blueprint" "invoice" {
  name = "${local.prefix}-invoice"
  type = "DOCUMENT" # DOCUMENT | IMAGE | AUDIO | VIDEO
  # Each property: type + inferenceType (explicit = read from file, inferred = derived) + instruction.
  schema = jsonencode({
    "$schema"   = "http://json-schema.org/draft-07/schema#"
    description = "Supplier invoice"
    class       = "invoice"
    type        = "object"
    properties = {
      vendor = {
        type          = "string"
        inferenceType = "explicit"
        instruction   = "The legal name of the company that issued the invoice"
      }
      total = {
        type          = "number"
        inferenceType = "explicit"
        instruction   = "The grand total to pay, in the invoice currency, as a number without symbols"
      }
      due_date = {
        type          = "string"
        inferenceType = "explicit"
        instruction   = "Payment due date in ISO 8601 (YYYY-MM-DD); empty if absent"
      }
    }
  })

  encryption_configuration {
    kms_key_id = aws_kms_key.main.arn
  }

  tags = { Component = "03.01" }
}

resource "aws_bedrockdataautomation_project" "docs" {
  name        = "${local.prefix}-docs"
  description = "Document extraction: standard text output + invoice blueprint"

  # Standard output: what BDA returns for every document even without a blueprint.
  standard_output_configuration {
    document {
      extraction {
        bounding_box {
          state = "DISABLED" # ENABLED adds coordinates; larger output
        }
        granularity {
          types = ["DOCUMENT", "PAGE"] # also ELEMENT | WORD | LINE
        }
      }
      generative_field {
        state = "DISABLED" # ENABLED adds a model-written summary (extra cost)
      }
      output_format {
        additional_file_format {
          state = "DISABLED"
        }
        text_format {
          types = ["MARKDOWN"] # PLAIN_TEXT | MARKDOWN | HTML | CSV
        }
      }
    }
  }

  # Custom output: the blueprint above. Pin the stage so a blueprint edit does not change production.
  custom_output_configuration {
    blueprint {
      blueprint_arn   = aws_bedrockdataautomation_blueprint.invoice.arn
      blueprint_stage = "LIVE"
    }
  }

  encryption_configuration {
    kms_key_id = aws_kms_key.main.arn
  }

  tags = { Component = "03.01" }
}

# ---------------------------------------------------------------- app policy (least privilege)

data "aws_iam_policy_document" "app_bda" {
  statement {
    sid     = "InvokeAsync"
    actions = ["bedrock:InvokeDataAutomationAsync"]
    resources = [
      aws_bedrockdataautomation_project.docs.arn,
      # Cross-region inference profile; the exact ARN shape is documented in the BDA IAM guide - verify.
      "arn:aws:bedrock:*:${local.account_id}:data-automation-profile/*",
    ]
  }
  statement {
    sid       = "PollStatus"
    actions   = ["bedrock:GetDataAutomationStatus"]
    resources = ["arn:aws:bedrock:${var.region}:${local.account_id}:data-automation-invocation/*"]
  }
  statement {
    sid     = "ReadConfig"
    actions = ["bedrock:GetBlueprint", "bedrock:GetDataAutomationProject", "bedrock:ListBlueprints", "bedrock:ListDataAutomationProjects"]
    resources = [
      aws_bedrockdataautomation_blueprint.invoice.arn,
      aws_bedrockdataautomation_project.docs.arn,
      "arn:aws:bedrock:${var.region}:${local.account_id}:blueprint/*",
    ]
  }
  statement {
    # Needed only by the config-as-code showcase in python (create_*). Drop in production: Terraform owns these.
    sid       = "ConfigAsCodeShowcase"
    actions   = ["bedrock:CreateBlueprint", "bedrock:CreateDataAutomationProject"]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "app_bda" {
  name   = "bda"
  role   = aws_iam_role.app.id
  policy = data.aws_iam_policy_document.app_bda.json
}

output "bda_project_arn" {
  value = aws_bedrockdataautomation_project.docs.arn
}

output "bda_blueprint_arn" {
  value = aws_bedrockdataautomation_blueprint.invoice.arn
}
