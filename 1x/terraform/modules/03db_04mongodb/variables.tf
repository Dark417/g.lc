# ---------------------------------------------------------------- wiring

variable "prefix" {
  description = "Name prefix, <project>-<env>"
  type        = string
}

variable "vpc_id" {
  type = string
}

variable "subnet_ids" {
  description = "Private subnets for the DocumentDB subnet group (2+ AZs)"
  type        = list(string)
}

variable "app_security_group_id" {
  description = "App SG allowed to reach DocumentDB on 27017"
  type        = string
}

variable "kms_key_arn" {
  description = "Shared CMK for storage, logs, and Performance Insights"
  type        = string
}

variable "app_role_id" {
  description = "App role name that gets the docdb policy"
  type        = string
}

# ---------------------------------------------------------------- knobs

variable "instance_class" {
  description = "DocumentDB instance class; memory decides whether the working set (docs + indexes) stays cached"
  type        = string
  default     = "db.r6g.large"
}

variable "instance_count" {
  description = "1 primary + (n-1) replicas; replicas are failover targets and read scale-out"
  type        = number
  default     = 2

  validation {
    condition     = var.instance_count >= 1 && var.instance_count <= 16
    error_message = "instance_count must be 1-16 (1 primary + up to 15 replicas)."
  }
}

variable "deletion_protection" {
  type    = bool
  default = true
}

variable "backup_retention_days" {
  description = "Point-in-time restore window (1-35 days)"
  type        = number
  default     = 7
}

variable "log_retention_days" {
  description = "CloudWatch retention for exported audit + profiler logs"
  type        = number
  default     = 30
}

variable "change_stream_retention_hours" {
  description = "Change-stream history kept (1-168 h); a consumer down longer than this must reconcile"
  type        = number
  default     = 24
}

variable "storage_type" {
  description = "standard (pay per I/O) or iopt1 (I/O-optimized)"
  type        = string
  default     = "standard"

  validation {
    condition     = contains(["standard", "iopt1"], var.storage_type)
    error_message = "storage_type must be standard or iopt1."
  }
}

variable "performance_insights" {
  description = "Enable Performance Insights on every instance"
  type        = bool
  default     = true
}
