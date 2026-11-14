# ---------------------------------------------------------------- wiring

variable "prefix" {
  description = "Name prefix, <project>-<env>"
  type        = string
}

variable "vpc_id" {
  type = string
}

variable "subnet_ids" {
  description = "Private subnets for the workgroup (3 AZs recommended)"
  type        = list(string)
}

variable "app_security_group_id" {
  description = "App SG allowed to reach Redshift on 5439"
  type        = string
}

variable "lake_bucket_arn" {
  description = "Lake bucket ARN (from 03db_03s3) for COPY / UNLOAD"
  type        = string
}

variable "kms_key_arn" {
  type = string
}

variable "app_role_id" {
  description = "App role name that gets Data API access"
  type        = string
}

# ---------------------------------------------------------------- knobs

variable "base_rpu" {
  description = "Base capacity in RPUs (8 minimum, steps of 8)"
  type        = number
  default     = 8
}

variable "max_rpu" {
  description = "Max capacity in RPUs (cost ceiling)"
  type        = number
  default     = 64
}
