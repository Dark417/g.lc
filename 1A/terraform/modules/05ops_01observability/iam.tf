# 05ops_01observability IAM — the role Bedrock assumes to write invocation logs + the app-role policy.

# ---------------------------------------------------------------- Bedrock write role

data "aws_iam_policy_document" "bedrock_logging_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["bedrock.amazonaws.com"]
    }
    condition {
      test     = "StringEquals" # confused-deputy guard: only this account's Bedrock may assume the role
      variable = "aws:SourceAccount"
      values   = [var.account_id]
    }
    condition {
      test     = "ArnLike"
      variable = "aws:SourceArn"
      values   = ["arn:aws:bedrock:${var.region}:${var.account_id}:*"]
    }
  }
}

resource "aws_iam_role" "bedrock_logging" {
  name               = "${var.prefix}-bedrock-logging"
  assume_role_policy = data.aws_iam_policy_document.bedrock_logging_assume.json
  tags               = { Component = "05ops_01observability" }
}

data "aws_iam_policy_document" "bedrock_logging" {
  statement {
    sid       = "WriteLogs"
    actions   = ["logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["${aws_cloudwatch_log_group.invocations.arn}:*"]
  }
  statement {
    sid       = "LargePayloads" # bodies too big for a log event are offloaded to S3
    actions   = ["s3:PutObject"]
    resources = ["${var.data_bucket_arn}/invocation-logs/*"]
  }
  statement {
    sid       = "BucketKey" # the data bucket is SSE-KMS with the shared key (base_data_bucket)
    actions   = ["kms:GenerateDataKey", "kms:Decrypt"]
    resources = [var.kms_key_arn]
  }
}

resource "aws_iam_role_policy" "bedrock_logging" {
  name   = "write-invocation-logs"
  role   = aws_iam_role.bedrock_logging.id
  policy = data.aws_iam_policy_document.bedrock_logging.json
}

# ---------------------------------------------------------------- app policy (least privilege)

data "aws_iam_policy_document" "app_observability" {
  statement {
    sid       = "CustomMetrics"
    actions   = ["cloudwatch:PutMetricData"]
    resources = ["*"] # PutMetricData has no resource ARN; the namespace condition is the scope
    condition {
      test     = "StringEquals"
      variable = "cloudwatch:namespace"
      values   = [local.obs_namespace]
    }
  }
  statement {
    sid       = "ReadMetrics"
    actions   = ["cloudwatch:GetMetricData", "cloudwatch:ListMetrics"]
    resources = ["*"] # read APIs cannot be scoped by resource
  }
  statement {
    sid       = "InsightsStart"
    actions   = ["logs:StartQuery"]
    resources = ["${aws_cloudwatch_log_group.invocations.arn}:*"]
  }
  statement {
    sid       = "InsightsResults" # query ids are not resources; GetQueryResults cannot be scoped
    actions   = ["logs:GetQueryResults", "logs:StopQuery"]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "app_observability" {
  name   = "observability"
  role   = var.app_role_id
  policy = data.aws_iam_policy_document.app_observability.json
}
