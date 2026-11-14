# ---------------------------------------------------------------- wiring

variable "prefix" {
  description = "Name prefix, <project>-<env>"
  type        = string
}

variable "region" {
  description = "Region, used in kafka-cluster ARNs"
  type        = string
}

variable "account_id" {
  description = "Account id, used in kafka-cluster ARNs"
  type        = string
}

variable "vpc_id" {
  type = string
}

variable "subnet_ids" {
  description = "Private subnets, one per AZ; brokers spread evenly across them"
  type        = list(string)
}

variable "app_security_group_id" {
  description = "App SG allowed to reach brokers on 9098"
  type        = string
}

variable "kms_key_arn" {
  type = string
}

variable "app_role_id" {
  description = "App role name that gets kafka-cluster:* data access"
  type        = string
}

# ---------------------------------------------------------------- knobs

variable "broker_instance_type" {
  type    = string
  default = "kafka.m7g.large"
}

variable "broker_count" {
  description = "Brokers; multiple of the subnet count"
  type        = number
  default     = 3
}

variable "volume_size_gib" {
  description = "EBS GiB per broker"
  type        = number
  default     = 500
}

variable "log_retention_hours" {
  description = "Kafka log.retention.hours"
  type        = number
  default     = 168
}
