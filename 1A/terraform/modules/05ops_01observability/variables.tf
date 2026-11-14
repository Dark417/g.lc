variable "prefix" {
  description = "Name prefix <project>-<env>, e.g. a-dev"
  type        = string
}

variable "region" {
  type = string
}

variable "account_id" {
  type = string
}

variable "app_role_id" {
  description = "App role (base_iam) the policy attaches to"
  type        = string
}

variable "kms_key_arn" {
  description = "Shared CMK (base_kms); the data bucket's SSE-KMS key"
  type        = string
}

variable "kms_deletion_window_days" {
  description = "Deletion window of this module's own log-group key (7-30)"
  type        = number
}

variable "data_bucket_arn" {
  description = "Shared data bucket ARN (base_data_bucket); invocation-logs/ prefix"
  type        = string
}

variable "data_bucket_name" {
  description = "Shared data bucket name (base_data_bucket)"
  type        = string
}

variable "alerts_topic_arn" {
  description = "SNS alerts topic (base_billing_alarm)"
  type        = string
}

variable "model_id" {
  description = "ModelId dimension value the alarms watch (the model or inference profile id the app calls)"
  type        = string
}

variable "latency_p90_ms" {
  description = "Alarm when p90 InvocationLatency exceeds this many milliseconds"
  type        = number
}

variable "throttle_threshold" {
  description = "Alarm when InvocationThrottles in 5 min exceed this count"
  type        = number
}

variable "log_retention_days" {
  description = "Invocation logs hold prompts: keep them only as long as debugging and audit need"
  type        = number
}
