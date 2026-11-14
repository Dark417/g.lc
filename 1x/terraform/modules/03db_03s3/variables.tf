# ---------------------------------------------------------------- wiring

variable "prefix" {
  description = "Name prefix, <project>-<env>"
  type        = string
}

variable "account_id" {
  description = "Suffix that makes bucket names globally unique"
  type        = string
}

variable "kms_key_arn" {
  type = string
}

variable "app_role_id" {
  description = "App role name that gets bucket access"
  type        = string
}

# ---------------------------------------------------------------- knobs

variable "raw_ia_days" {
  description = "raw/ -> STANDARD_IA after N days (>= 30)"
  type        = number
  default     = 30
}

variable "raw_glacier_days" {
  description = "raw/ -> GLACIER_IR after N days (>= raw_ia_days + 30)"
  type        = number
  default     = 180
}

variable "noncurrent_expiration_days" {
  type    = number
  default = 30
}

variable "athena_results_expiration_days" {
  type    = number
  default = 7
}
