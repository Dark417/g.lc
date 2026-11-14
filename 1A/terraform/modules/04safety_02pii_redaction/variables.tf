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
  description = "Shared CMK (base_kms)"
  type        = string
}

variable "data_bucket_arn" {
  description = "Shared data bucket ARN (base_data_bucket); comprehend/ prefixes"
  type        = string
}

variable "data_bucket_name" {
  description = "Shared data bucket name (base_data_bucket)"
  type        = string
}
