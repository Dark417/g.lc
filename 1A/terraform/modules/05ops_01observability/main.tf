# modules/05ops_01observability — GenAI observability on CloudWatch, lecture 46 (+ preview of 195-206).
# Creates: KMS key + log group for Bedrock model invocation logs, role Bedrock assumes to write them (→ iam.tf),
#          the account-level invocation logging configuration, two alarms (throttles, p90 latency) -> SNS alerts
#          (base_billing_alarm topic), app policy for custom metrics and Logs Insights queries (→ iam.tf).
# Used by: python app/{api,service,infra}/_05ops_01observability (slice "observability").
#
# Catch:
#   - The invocation logging configuration is ONE per account and Region: applying it replaces whatever exists.
#   - Prompts and completions land in the log group in clear text (encrypted at rest only). Treat the log group
#     like the PII store it can be: tight IAM, short retention, no wide read access.
#   - Built-in AWS/Bedrock metrics need no setup; this module only adds logs and alarms on top of them.

locals {
  obs_log_group = "/aws/bedrock/${var.prefix}-invocations"
  obs_namespace = "A/GenAI" # custom metric namespace; the app policy pins PutMetricData to it
}

# ---------------------------------------------------------------- encryption for the log group

# A log group can only use a CMK whose key policy grants the Logs service. The shared key in base_kms keeps the
# default policy (IAM-only), so this component owns a small key instead of editing the foundation.
data "aws_iam_policy_document" "obs_logs_key" {
  statement {
    sid       = "AccountAdmin"
    actions   = ["kms:*"]
    resources = ["*"]
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${var.account_id}:root"]
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
      values   = ["arn:aws:logs:${var.region}:${var.account_id}:log-group:${local.obs_log_group}"]
    }
  }
}

resource "aws_kms_key" "obs_logs" {
  description             = "${var.prefix} bedrock invocation logs"
  enable_key_rotation     = true
  deletion_window_in_days = var.kms_deletion_window_days
  policy                  = data.aws_iam_policy_document.obs_logs_key.json
  tags                    = { Component = "05ops_01observability" }
}

# ---------------------------------------------------------------- log group

resource "aws_cloudwatch_log_group" "invocations" {
  name              = local.obs_log_group
  retention_in_days = var.log_retention_days # never "forever" for a log group that holds prompts
  kms_key_id        = aws_kms_key.obs_logs.arn
  tags              = { Component = "05ops_01observability" }
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
        bucket_name = var.data_bucket_name
        key_prefix  = "invocation-logs"
      }
    }
    # An s3_config {} block would also copy every record to S3 (cheap, Athena-friendly); it needs a bucket
    # policy for bedrock.amazonaws.com on the prefix, so it is left out here.
  }
}

# ---------------------------------------------------------------- alarms on built-in AWS/Bedrock metrics

resource "aws_cloudwatch_metric_alarm" "throttles" {
  alarm_name          = "${var.prefix}-bedrock-throttles"
  namespace           = "AWS/Bedrock"
  metric_name         = "InvocationThrottles"
  dimensions          = { ModelId = var.model_id }
  statistic           = "Sum"
  period              = 300
  evaluation_periods  = 1
  threshold           = var.throttle_threshold # 0 in prod = any throttle alarms; looser in dev
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching" # no traffic is not an incident
  alarm_description   = "Bedrock throttled requests: raise quota, add retries/backoff, or move to a cross-region profile"
  alarm_actions       = [var.alerts_topic_arn]
  tags                = { Component = "05ops_01observability" }
}

resource "aws_cloudwatch_metric_alarm" "latency_p90" {
  alarm_name          = "${var.prefix}-bedrock-latency-p90"
  namespace           = "AWS/Bedrock"
  metric_name         = "InvocationLatency"
  dimensions          = { ModelId = var.model_id }
  extended_statistic  = "p90" # percentile, not average: averages hide the slow tail users feel
  period              = 300
  evaluation_periods  = 3 # 3 x 5 min windows ...
  datapoints_to_alarm = 2 # ... 2 of which must breach: ignores one slow generation
  threshold           = var.latency_p90_ms
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching"
  alarm_description   = "p90 invocation latency (ms) above threshold; long outputs also raise it, so compare with OutputTokenCount"
  alarm_actions       = [var.alerts_topic_arn]
  tags                = { Component = "05ops_01observability" }
}
