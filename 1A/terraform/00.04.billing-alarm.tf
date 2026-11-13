# 00.04 billing-alarm — lecture 5 "Setting Up an AWS Billing Alarm".
# Creates: SNS topic + email subscription, CloudWatch alarm on AWS/Billing EstimatedCharges.
# Why first: OpenSearch Serverless and provisioned throughput bill per hour even when idle (lectures 17, 101).
#
# Catch:
#   - Billing metrics exist only in us-east-1 and only after "Receive Billing Alerts" is enabled in the
#     Billing console preferences (one-time, account-level; not exposed as a Terraform resource here).
#   - EstimatedCharges is month-to-date and updates a few times a day: it is a tripwire, not a real-time meter.
#   - AWS Budgets is the alternative with forecasts and per-service filters (aws_budgets_budget).

variable "billing_threshold_usd" {
  description = "Alarm when month-to-date estimated charges exceed this many USD"
  type        = number
  default     = 20
}

resource "aws_sns_topic" "alerts" {
  name = "${local.prefix}-alerts"
  # Not KMS-encrypted on purpose: CloudWatch alarms can only publish to an encrypted topic when the CMK
  # key policy grants cloudwatch.amazonaws.com kms:GenerateDataKey + kms:Decrypt. Add that grant to
  # 00.02 before turning on kms_master_key_id here.
  tags = { Component = "00.04" }
}

resource "aws_sns_topic_subscription" "alerts_email" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email # stays "pending confirmation" until the recipient clicks the link
}

resource "aws_cloudwatch_metric_alarm" "billing" {
  alarm_name          = "${local.prefix}-billing-over-${var.billing_threshold_usd}usd"
  namespace           = "AWS/Billing"
  metric_name         = "EstimatedCharges"
  dimensions          = { Currency = "USD" }
  statistic           = "Maximum"
  period              = 21600 # 6 h: the metric only updates a few times a day
  evaluation_periods  = 1
  comparison_operator = "GreaterThanThreshold"
  threshold           = var.billing_threshold_usd
  alarm_actions       = [aws_sns_topic.alerts.arn]
  treat_missing_data  = "notBreaching"
  tags                = { Component = "00.04" }
}

output "alerts_topic_arn" {
  value = aws_sns_topic.alerts.arn
}
