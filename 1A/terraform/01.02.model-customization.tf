# 01.02 model-customization — the service role a customization job runs as, and the app permissions to
# start jobs, read results, and (deliberately, by hand) buy provisioned throughput to serve the result.
#
# Creates
#   - aws_iam_role.customization "a-customization-role" (assumed by bedrock.amazonaws.com during training)
#   - aws_iam_role_policy.customization on aws_iam_role.app (00.03)
# Does NOT create (they train or bill by the hour): aws_bedrock_custom_model, aws_bedrock_provisioned_model_throughput.
#   Commented examples are at the bottom. The Python slice shows the same calls with explicit warnings.
# Data: shared bucket a-ai-data-<account> (00.05), prefixes customization/train/, customization/validation/,
#   customization/output/.
# Used by: Python app/a01_02_customization
# Lectures: AIP-C01 #11–#12

variable "customization_base_model_id" {
  description = "Base model to customize. Find candidates with ListFoundationModels(byCustomizationType=FINE_TUNING)."
  type        = string
  default     = "amazon.nova-micro-v1:0:128k" # customizable IDs often carry a context suffix (":128k"); check per Region
}

locals {
  customization_prefix = "customization"
  customization_base   = "arn:aws:bedrock:${var.region}::foundation-model/${var.customization_base_model_id}"
}

# ---------------------------------------------------------------- service role (the job runs as this)

data "aws_iam_policy_document" "customization_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["bedrock.amazonaws.com"]
    }
    # Confused-deputy protection: only customization jobs in this account.
    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [local.account_id]
    }
    condition {
      test     = "ArnLike"
      variable = "aws:SourceArn"
      values   = ["arn:aws:bedrock:${var.region}:${local.account_id}:model-customization-job/*"]
    }
  }
}

resource "aws_iam_role" "customization" {
  name               = "${local.prefix}-customization-role"
  assume_role_policy = data.aws_iam_policy_document.customization_assume.json
  tags               = { Component = "01.02" }
}

data "aws_iam_policy_document" "customization_data" {
  statement {
    sid       = "ListCustomizationPrefix"
    actions   = ["s3:ListBucket"]
    resources = [aws_s3_bucket.data.arn]
    condition {
      test     = "StringLike"
      variable = "s3:prefix"
      values   = ["${local.customization_prefix}/*"]
    }
  }
  statement {
    sid     = "ReadTrainingData"
    actions = ["s3:GetObject"]
    resources = [
      "${aws_s3_bucket.data.arn}/${local.customization_prefix}/train/*",
      "${aws_s3_bucket.data.arn}/${local.customization_prefix}/validation/*",
    ]
  }
  statement {
    sid       = "WriteJobOutput"
    actions   = ["s3:PutObject"]
    resources = ["${aws_s3_bucket.data.arn}/${local.customization_prefix}/output/*"]
  }
  # Bucket is SSE-KMS with the shared CMK (00.05): read needs Decrypt, write needs GenerateDataKey.
  statement {
    sid       = "UseDataKey"
    actions   = ["kms:Decrypt", "kms:GenerateDataKey"]
    resources = [aws_kms_key.main.arn]
  }
}

resource "aws_iam_role_policy" "customization_role" {
  name   = "customization-data"
  role   = aws_iam_role.customization.id
  policy = data.aws_iam_policy_document.customization_data.json
}

# ---------------------------------------------------------------- IAM for the app role

data "aws_iam_policy_document" "customization" {
  statement {
    sid     = "StartCustomizationJobs"
    actions = ["bedrock:CreateModelCustomizationJob"]
    # Authorized against the job, the output custom model, and the base model.
    resources = [
      "arn:aws:bedrock:${var.region}:${local.account_id}:model-customization-job/*",
      "arn:aws:bedrock:${var.region}:${local.account_id}:custom-model/*",
      local.customization_base,
    ]
  }

  statement {
    sid = "ReadCustomizationResults"
    actions = [
      "bedrock:GetModelCustomizationJob",
      "bedrock:StopModelCustomizationJob",
      "bedrock:GetCustomModel",
    ]
    resources = [
      "arn:aws:bedrock:${var.region}:${local.account_id}:model-customization-job/*",
      "arn:aws:bedrock:${var.region}:${local.account_id}:custom-model/*",
    ]
  }

  statement {
    sid       = "ListCustomization"
    actions   = ["bedrock:ListModelCustomizationJobs", "bedrock:ListCustomModels", "bedrock:ListFoundationModels"]
    resources = ["*"] # list operations: no resource-level permissions
  }

  # COST WARNING: CreateProvisionedModelThroughput starts hourly billing immediately (even with no traffic),
  # and a 1- or 6-month commitment cannot be cancelled. Kept here only so the showcase is complete; in a real
  # account gate it behind a separate, human-assumed role.
  statement {
    sid = "ServeCustomModels"
    actions = [
      "bedrock:CreateProvisionedModelThroughput",
      "bedrock:GetProvisionedModelThroughput",
      "bedrock:DeleteProvisionedModelThroughput",
      "bedrock:CreateCustomModelDeployment", # on-demand serving for supported custom models
      "bedrock:GetCustomModelDeployment",
    ]
    resources = [
      "arn:aws:bedrock:${var.region}:${local.account_id}:custom-model/*",
      "arn:aws:bedrock:${var.region}:${local.account_id}:provisioned-model/*",
      "arn:aws:bedrock:${var.region}:${local.account_id}:custom-model-deployment/*",
    ]
  }

  statement {
    sid     = "InvokeCustomModels"
    actions = ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"] # Converse / ConverseStream
    resources = [
      "arn:aws:bedrock:${var.region}:${local.account_id}:provisioned-model/*",
      "arn:aws:bedrock:${var.region}:${local.account_id}:custom-model-deployment/*",
    ]
  }

  statement {
    sid       = "PassCustomizationRole"
    actions   = ["iam:PassRole"]
    resources = [aws_iam_role.customization.arn]
    condition {
      test     = "StringEquals"
      variable = "iam:PassedToService"
      values   = ["bedrock.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy" "customization" {
  name   = "bedrock-customization"
  role   = aws_iam_role.app.id
  policy = data.aws_iam_policy_document.customization.json
}

# ---------------------------------------------------------------- commented examples (NOT live resources)

# Training job as a Terraform resource: `apply` would start a paid, hours-long training run, and a later
# change to any argument replaces (re-trains) the model. Kept as a reference for the argument names (6.73).
#
# resource "aws_bedrock_custom_model" "summary" {
#   custom_model_name     = "${local.prefix}-summary-model"
#   job_name              = "${local.prefix}-summary-job-1"
#   base_model_identifier = local.customization_base
#   role_arn              = aws_iam_role.customization.arn
#   customization_type    = "FINE_TUNING"          # FINE_TUNING | CONTINUED_PRE_TRAINING | DISTILLATION
#   custom_model_kms_key_id = aws_kms_key.main.arn
#   hyperparameters = {                              # string map; names and ranges are per base model
#     epochCount   = "2"
#     batchSize    = "1"
#     learningRate = "0.00001"
#   }
#   training_data_config   { s3_uri = "s3://${aws_s3_bucket.data.bucket}/customization/train/train.jsonl" }
#   validation_data_config { validator { s3_uri = "s3://${aws_s3_bucket.data.bucket}/customization/validation/validation.jsonl" } }
#   output_data_config     { s3_uri = "s3://${aws_s3_bucket.data.bucket}/customization/output/" }
# }
#
# Provisioned throughput: bills per model unit per hour from creation until deletion.
# resource "aws_bedrock_provisioned_model_throughput" "summary" {
#   provisioned_model_name = "${local.prefix}-summary-pt"
#   model_arn              = aws_bedrock_custom_model.summary.custom_model_arn
#   model_units            = 1
#   # commitment_duration  = "OneMonth"   # OneMonth | SixMonths; omit = no commitment (hourly, deletable)
# }

# ---------------------------------------------------------------- outputs

output "customization_role_arn" {
  description = "A_CUSTOMIZATION_ROLE_ARN"
  value       = aws_iam_role.customization.arn
}

output "customization_s3_prefix" {
  description = "A_CUSTOMIZATION_S3_PREFIX"
  value       = "s3://${aws_s3_bucket.data.bucket}/${local.customization_prefix}/"
}
