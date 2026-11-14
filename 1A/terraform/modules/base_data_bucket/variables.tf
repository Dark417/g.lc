variable "prefix" {
  description = "Name prefix <project>-<env>, e.g. a-dev"
  type        = string
}

variable "account_id" {
  description = "AWS account id; suffixes the globally unique bucket name"
  type        = string
}

variable "kms_key_arn" {
  description = "Shared CMK (base_kms) for SSE-KMS"
  type        = string
}

variable "app_role_id" {
  description = "App role (base_iam) that gets read/write on the bucket"
  type        = string
}

variable "noncurrent_version_days" {
  description = "Days an overwritten or deleted object version is kept before S3 expires it"
  type        = number
}
