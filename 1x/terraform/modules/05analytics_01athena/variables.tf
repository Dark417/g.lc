# ---------------------------------------------------------------- wiring

variable "prefix" {
  description = "Name prefix, <project>-<env>"
  type        = string
}

variable "region" {
  description = "Region, used in Glue ARNs"
  type        = string
}

variable "account_id" {
  description = "Account id, used in Glue ARNs"
  type        = string
}

variable "lake_bucket" {
  description = "Lake bucket name (from 03db_03s3); the clicks table points at raw/clicks/"
  type        = string
}

variable "athena_results_bucket" {
  description = "Results bucket name (from 03db_03s3)"
  type        = string
}

variable "kms_key_arn" {
  type = string
}

variable "app_role_id" {
  description = "App role name that gets Athena + Glue access"
  type        = string
}

# ---------------------------------------------------------------- knobs

variable "bytes_scanned_cutoff" {
  description = "Per-query scan limit in bytes"
  type        = number
  default     = 10737418240
}
