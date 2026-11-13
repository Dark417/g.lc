# 04.02 pii-redaction — Comprehend PII detection/redaction, lectures 26, 49-51 (47 Transcribe, 225 Macie: doc only).
# Creates: the Comprehend data-access role a-comprehend-pii (async StartPiiEntitiesDetectionJob reads
#          comprehend/input/ and writes comprehend/output/ in the shared bucket, KMS-encrypted) and the app policy
#          for the sync + async PII APIs and iam:PassRole on that role.
# Used by: python app/a04_02_pii_redaction (slice "pii").
# Not here: the general NLP Comprehend component (03.04) and the guardrail used as the output net (04.01).
#
# Why a service role: async Comprehend jobs run as the Comprehend service, not as the caller. The caller passes
# DataAccessRoleArn, which needs iam:PassRole; the role must trust comprehend.amazonaws.com.

locals {
  pii_input_prefix  = "comprehend/input/"
  pii_output_prefix = "comprehend/output/"
}

# ================================================================ Comprehend data-access role

data "aws_iam_policy_document" "comprehend_pii_trust" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["comprehend.amazonaws.com"]
    }
    # Confused-deputy guard: only Comprehend jobs started in this account may assume the role.
    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [local.account_id]
    }
    condition {
      test     = "ArnLike"
      variable = "aws:SourceArn"
      values   = ["arn:aws:comprehend:${var.region}:${local.account_id}:*"]
    }
  }
}

resource "aws_iam_role" "comprehend_pii" {
  name               = "${local.prefix}-comprehend-pii"
  assume_role_policy = data.aws_iam_policy_document.comprehend_pii_trust.json
  tags               = { Component = "04.02" }
}

data "aws_iam_policy_document" "comprehend_pii_access" {
  statement {
    sid       = "ListInputOutputPrefixes"
    actions   = ["s3:ListBucket"]
    resources = [aws_s3_bucket.data.arn]
    condition {
      test     = "StringLike"
      variable = "s3:prefix"
      values   = ["${local.pii_input_prefix}*", "${local.pii_output_prefix}*"]
    }
  }
  statement {
    sid       = "ReadInput"
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.data.arn}/${local.pii_input_prefix}*"]
  }
  statement {
    sid       = "WriteOutput"
    actions   = ["s3:PutObject"]
    resources = ["${aws_s3_bucket.data.arn}/${local.pii_output_prefix}*"]
  }
  # Bucket is SSE-KMS (00.05) and the job encrypts output with OutputDataConfig.KmsKeyId = the same CMK.
  statement {
    sid       = "UseDataKey"
    actions   = ["kms:Decrypt", "kms:GenerateDataKey", "kms:DescribeKey"]
    resources = [aws_kms_key.main.arn]
  }
}

resource "aws_iam_role_policy" "comprehend_pii_access" {
  name   = "s3-kms"
  role   = aws_iam_role.comprehend_pii.id
  policy = data.aws_iam_policy_document.comprehend_pii_access.json
}

# ================================================================ app IAM (least privilege)

data "aws_iam_policy_document" "app_pii" {
  # Comprehend sync PII APIs are not resource-scoped (no ARN for a text call).
  statement {
    sid       = "DetectPii"
    actions   = ["comprehend:DetectPiiEntities", "comprehend:ContainsPiiEntities"]
    resources = ["*"]
  }

  # Async jobs: start / describe / list. Job ARNs only exist after start, so the resource is "*".
  statement {
    sid = "PiiJobs"
    actions = [
      "comprehend:StartPiiEntitiesDetectionJob",
      "comprehend:DescribePiiEntitiesDetectionJob",
      "comprehend:ListPiiEntitiesDetectionJobs",
    ]
    resources = ["*"] # tighter option: tag jobs on start and condition on aws:RequestTag / aws:ResourceTag
  }

  # Hand the data-access role to Comprehend, and only to Comprehend.
  statement {
    sid       = "PassComprehendRole"
    actions   = ["iam:PassRole"]
    resources = [aws_iam_role.comprehend_pii.arn]
    condition {
      test     = "StringEquals"
      variable = "iam:PassedToService"
      values   = ["comprehend.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy" "app_pii" {
  name   = "pii-redaction"
  role   = aws_iam_role.app.id
  policy = data.aws_iam_policy_document.app_pii.json
}

# The pipeline (service.redact_converse_guard) also calls bedrock-runtime Converse + ApplyGuardrail; those grants
# come from 04.01 (app_guardrails policy) on the same app role.

# ================================================================ outputs

output "comprehend_pii_role_arn" {
  value = aws_iam_role.comprehend_pii.arn # A_PII_DATA_ACCESS_ROLE_ARN
}

output "pii_input_s3_uri" {
  value = "s3://${aws_s3_bucket.data.bucket}/${local.pii_input_prefix}"
}

output "pii_output_s3_uri" {
  value = "s3://${aws_s3_bucket.data.bucket}/${local.pii_output_prefix}"
}
