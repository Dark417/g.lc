# 01bedrock_02customization IAM — the job's service role + the app-role policy.

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
      values   = [var.account_id]
    }
    condition {
      test     = "ArnLike"
      variable = "aws:SourceArn"
      values   = ["arn:aws:bedrock:${var.region}:${var.account_id}:model-customization-job/*"]
    }
  }
}

resource "aws_iam_role" "customization" {
  name               = "${var.prefix}-customization-role"
  assume_role_policy = data.aws_iam_policy_document.customization_assume.json
  tags               = { Component = "01bedrock_02customization" }
}

data "aws_iam_policy_document" "customization_data" {
  statement {
    sid       = "ListCustomizationPrefix"
    actions   = ["s3:ListBucket"]
    resources = [var.data_bucket_arn]
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
      "${var.data_bucket_arn}/${local.customization_prefix}/train/*",
      "${var.data_bucket_arn}/${local.customization_prefix}/validation/*",
    ]
  }
  statement {
    sid       = "WriteJobOutput"
    actions   = ["s3:PutObject"]
    resources = ["${var.data_bucket_arn}/${local.customization_prefix}/output/*"]
  }
  # Bucket is SSE-KMS with the shared CMK (base_data_bucket): read needs Decrypt, write needs GenerateDataKey.
  statement {
    sid       = "UseDataKey"
    actions   = ["kms:Decrypt", "kms:GenerateDataKey"]
    resources = [var.kms_key_arn]
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
      "arn:aws:bedrock:${var.region}:${var.account_id}:model-customization-job/*",
      "arn:aws:bedrock:${var.region}:${var.account_id}:custom-model/*",
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
      "arn:aws:bedrock:${var.region}:${var.account_id}:model-customization-job/*",
      "arn:aws:bedrock:${var.region}:${var.account_id}:custom-model/*",
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
      "arn:aws:bedrock:${var.region}:${var.account_id}:custom-model/*",
      "arn:aws:bedrock:${var.region}:${var.account_id}:provisioned-model/*",
      "arn:aws:bedrock:${var.region}:${var.account_id}:custom-model-deployment/*",
    ]
  }

  statement {
    sid     = "InvokeCustomModels"
    actions = ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"] # Converse / ConverseStream
    resources = [
      "arn:aws:bedrock:${var.region}:${var.account_id}:provisioned-model/*",
      "arn:aws:bedrock:${var.region}:${var.account_id}:custom-model-deployment/*",
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
  role   = var.app_role_id
  policy = data.aws_iam_policy_document.customization.json
}
