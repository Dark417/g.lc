# ---------------------------------------------------------------- wiring

variable "prefix" {
  description = "Name prefix, <project>-<env>"
  type        = string
}

variable "region" {
  description = "Region, used in the rds-db:connect ARN"
  type        = string
}

variable "account_id" {
  description = "Account id, used in the rds-db:connect ARN"
  type        = string
}

variable "vpc_id" {
  type = string
}

variable "subnet_ids" {
  description = "Private subnets for the DB subnet group (2+ AZs)"
  type        = list(string)
}

variable "app_security_group_id" {
  description = "App SG allowed to reach Postgres on 5432"
  type        = string
}

variable "kms_key_arn" {
  type = string
}

variable "kms_key_id" {
  description = "CMK key id, for the master user secret"
  type        = string
}

variable "app_role_id" {
  description = "App role name that gets rds-db:connect"
  type        = string
}

# ---------------------------------------------------------------- knobs

variable "min_acu" {
  type    = number
  default = 0.5
}

variable "max_acu" {
  type    = number
  default = 8
}

variable "instance_count" {
  description = "1 writer + (n-1) readers"
  type        = number
  default     = 2
}

variable "deletion_protection" {
  type    = bool
  default = true
}

variable "backup_retention_days" {
  type    = number
  default = 7
}

variable "log_retention_days" {
  type    = number
  default = 30
}
