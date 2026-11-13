# 05.01 observability — GenAI observability on CloudWatch, lecture 46 (+ preview of 195-206).
# Creates: KMS key + log group for Bedrock model invocation logs, role Bedrock assumes to write them,
#          the account-level invocation logging configuration, two alarms (throttles, p90 latency) -> SNS alerts,
#          app policy for custom metrics and Logs Insights queries.
# Used by: python app/a05_01_observability (slice "observability").
#
# Catch:
#   - The invocation logging configuration is ONE per account and Region: applying it replaces whatever exists.
#   - Prompts and completions land in the log group in clear text (encrypted at rest only). Treat the log group
#     like the PII store it can be: tight IAM, short retention, no wide read access.
#   - Built-in AWS/Bedrock metrics need no setup; this file only adds logs and alarms on top of them.

locals {
  obs_log_group = "/aws/bedrock/${local.prefix}-invocations"
  obs_namespace = "A/GenAI" # custom metric namespace; the app policy pins PutMetricData to it
}

variable "obs_model_id" {
  description = "ModelId dimension value the alarms watch (the model or inference profile id the app calls)"
  type        = string
  default     = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
}

variable "obs_latency_p90_ms" {
  description = "Alarm when p90 InvocationLatency exceeds this many milliseconds"
  type        = number
  default     = 10000
}

variable "obs_log_retention_days" {
  description = "Invocation logs hold prompts: keep them only as long as debugging and audit need"
  type        = number
  default     = 30
}

# ---------------------------------------------------------------- encryption for the log group

# A log group can only use a CMK whose key policy grants the Logs service. The shared key in 00.02 keeps the
# default policy (IAM-only), so this component owns a small key instead of editing the foundation.
data "aws_iam_policy_document" "obs_logs_key" {
  statement {
    sid       = "AccountAdmin"
    actions   = ["kms:*"]
    resources = ["*"]
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${local.account_id}:root"]
    }
  }
  statement {
    sid       = "AllowLogsService"
    actions   = ["kms:Encrypt*", "kms:Decrypt*", "kms:ReEncrypt*", "kms:GenerateDataKey*", "kms:Describe*"]
    resources = ["*"]
    principals {
      type        = "Service"
      identifiers = ["logs.${var.region}.amazonaws.com"]
    }
    condition {
      test     = "ArnEquals" # only this log group, not every log group in the account
      variable = "kms:EncryptionContext:aws:logs:arn"
      values   = ["arn:aws:logs:${var.region}:${local.account_id}:log-group:${local.obs_log_group}"]
    }
  }
}

resource "aws_kms_key" "obs_logs" {
  description             = "${local.prefix} bedrock invocation logs"
  enable_key_rotation     = true
  deletion_window_in_days = 7
  policy                  = data.aws_iam_policy_document.obs_logs_key.json
  tags                    = { Component = "05.01" }
}

# ---------------------------------------------------------------- log group + Bedrock write role

resource "aws_cloudwatch_log_group" "invocations" {
  name              = local.obs_log_group
  retention_in_days = var.obs_log_retention_days # never "forever" for a log group that holds prompts
  kms_key_id        = aws_kms_key.obs_logs.arn
  tags              = { Component = "05.01" }
}

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
      values   = [local.account_id]
    }
    condition {
      test     = "ArnLike"
      variable = "aws:SourceArn"
      values   = ["arn:aws:bedrock:${var.region}:${local.account_id}:*"]
    }
  }
}

resource "aws_iam_role" "bedrock_logging" {
  name               = "${local.prefix}-bedrock-logging"
  assume_role_policy = data.aws_iam_policy_document.bedrock_logging_assume.json
  tags               = { Component = "05.01" }
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
    resources = ["${aws_s3_bucket.data.arn}/invocation-logs/*"]
  }
  statement {
    sid       = "BucketKey" # the data bucket is SSE-KMS with the shared key (00.05)
    actions   = ["kms:GenerateDataKey", "kms:Decrypt"]
    resources = [aws_kms_key.main.arn]
  }
}

resource "aws_iam_role_policy" "bedrock_logging" {
  name   = "write-invocation-logs"
  role   = aws_iam_role.bedrock_logging.id
  policy = data.aws_iam_policy_document.bedrock_logging.json
}

# ---------------------------------------------------------------- invocation logging configuration

resource "aws_bedrock_model_invocation_logging_configuration" "main" {
  logging_config {
    # Delivery flags decide which payloads are logged at all. Each = privacy exposure + storage cost.
    text_data_delivery_enabled      = true  # prompts + completions of Converse / InvokeModel text models
    embedding_data_delivery_enabled = true  # embedding inputs (outputs are vectors: noisy and large)
    image_data_delivery_enabled     = false # generated images: large; leave off unless audited
    video_data_delivery_enabled     = false

    cloudwatch_config {
      log_group_name = aws_cloudwatch_log_group.invocations.name
      role_arn       = aws_iam_role.bedrock_logging.arn

      # Payloads over the CloudWatch event size limit (check the CloudWatch Logs quota page) go to S3;
      # the log event keeps a pointer. Without this block those bodies are dropped from the log.
      large_data_delivery_s3_config {
        bucket_name = aws_s3_bucket.data.bucket
        key_prefix  = "invocation-logs"
      }
    }
    # An s3_config {} block would also copy every record to S3 (cheap, Athena-friendly); it needs a bucket
    # policy for bedrock.amazonaws.com on the prefix, so it is left out here.
  }
}

# ---------------------------------------------------------------- alarms on built-in AWS/Bedrock metrics

resource "aws_cloudwatch_metric_alarm" "throttles" {
  alarm_name          = "${local.prefix}-bedrock-throttles"
  namespace           = "AWS/Bedrock"
  metric_name         = "InvocationThrottles"
  dimensions          = { ModelId = var.obs_model_id }
  statistic           = "Sum"
  period              = 300
  evaluation_periods  = 1
  threshold           = 0
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching" # no traffic is not an incident
  alarm_description   = "Bedrock throttled requests: raise quota, add retries/backoff, or move to a cross-region profile"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  tags                = { Component = "05.01" }
}

resource "aws_cloudwatch_metric_alarm" "latency_p90" {
  alarm_name          = "${local.prefix}-bedrock-latency-p90"
  namespace           = "AWS/Bedrock"
  metric_name         = "InvocationLatency"
  dimensions          = { ModelId = var.obs_model_id }
  extended_statistic  = "p90" # percentile, not average: averages hide the slow tail users feel
  period              = 300
  evaluation_periods  = 3 # 3 x 5 min windows ...
  datapoints_to_alarm = 2 # ... 2 of which must breach: ignores one slow generation
  threshold           = var.obs_latency_p90_ms
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching"
  alarm_description   = "p90 invocation latency (ms) above threshold; long outputs also raise it, so compare with OutputTokenCount"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  tags                = { Component = "05.01" }
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
  role   = aws_iam_role.app.id
  policy = data.aws_iam_policy_document.app_observability.json
}

output "invocation_log_group" {
  value = aws_cloudwatch_log_group.invocations.name
}

output "obs_metric_namespace" {
  value = local.obs_namespace
}
