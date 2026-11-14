# ---------------------------------------------------------------- wiring

variable "prefix" {
  description = "Name prefix, <project>-<env>"
  type        = string
}

variable "lake_bucket_arn" {
  description = "Lake bucket ARN (from 03db_03s3) where Firehose lands records"
  type        = string
}

variable "kms_key_arn" {
  type = string
}

variable "app_role_id" {
  description = "App role name that gets produce/consume access"
  type        = string
}

# ---------------------------------------------------------------- knobs

variable "stream_mode" {
  description = "ON_DEMAND or PROVISIONED"
  type        = string
  default     = "ON_DEMAND"
}

variable "shard_count" {
  description = "Shards when PROVISIONED (ignored for ON_DEMAND)"
  type        = number
  default     = 1
}

variable "retention_hours" {
  description = "Replay window in hours (24-8760)"
  type        = number
  default     = 48
}
