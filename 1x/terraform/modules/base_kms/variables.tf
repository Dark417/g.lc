variable "prefix" {
  description = "Name prefix, <project>-<env>"
  type        = string
}

variable "deletion_window_days" {
  description = "Days before a deleted key is gone for good (7-30)"
  type        = number
  default     = 7
}

variable "app_role_id" {
  description = "App role name (from base_iam) that gets kms:Decrypt/GenerateDataKey"
  type        = string
}
