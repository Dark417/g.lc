# variables — env identity + per-component knobs. Values per env live in envs/<env>.tfvars.
# Defaults are the original single-stack values, so a bare `terraform validate` still works.

# ---------------------------------------------------------------- env identity

variable "env" {
  description = "Environment name; part of every AWS name (x-<env>-orders)"
  type        = string

  validation {
    condition     = contains(["local", "dev", "uat", "prod"], var.env)
    error_message = "env must be one of local, dev, uat, prod."
  }
}

variable "aws_account_id" {
  description = "Account this env may touch (provider allowed_account_ids). LocalStack uses 000000000000"
  type        = string
}

variable "region" {
  description = "AWS region for every resource"
  type        = string
  default     = "us-east-1"
}

variable "project_prefix" {
  description = "Project part of the name prefix; local.prefix = <project_prefix>-<env>"
  type        = string
  default     = "x"
}

variable "use_localstack" {
  description = "Point the AWS provider at LocalStack (local env only)"
  type        = bool
  default     = false
}

variable "localstack_endpoint" {
  description = "LocalStack edge URL, used only when use_localstack = true"
  type        = string
  default     = "http://localhost:4566"
}

# ---------------------------------------------------------------- base

variable "vpc_cidr" {
  description = "VPC CIDR; one private /20 per AZ is carved out of it"
  type        = string
  default     = "10.40.0.0/16"
}

variable "az_count" {
  description = "Number of AZs for private subnets; 3 lets Aurora/MSK survive one AZ loss"
  type        = number
  default     = 3
}

variable "kms_deletion_window_days" {
  description = "Days a deleted CMK waits before it is gone for good (7-30)"
  type        = number
  default     = 7
}

variable "log_retention_days" {
  description = "CloudWatch Logs retention for exported service logs (Aurora postgresql log)"
  type        = number
  default     = 30
}

# ---------------------------------------------------------------- 03db

variable "aurora_min_acu" {
  description = "Aurora Serverless v2 floor in ACUs (1 ACU ~ 2 GiB RAM)"
  type        = number
  default     = 0.5
}

variable "aurora_max_acu" {
  description = "Aurora Serverless v2 ceiling in ACUs (cost cap)"
  type        = number
  default     = 8
}

variable "aurora_instance_count" {
  description = "Aurora instances: 1 writer + (n-1) readers / failover targets"
  type        = number
  default     = 2
}

variable "aurora_deletion_protection" {
  description = "Block cluster deletion until this is turned off"
  type        = bool
  default     = true
}

variable "aurora_backup_retention_days" {
  description = "Aurora point-in-time restore window (1-35 days)"
  type        = number
  default     = 7
}

variable "dynamodb_billing_mode" {
  description = "PAY_PER_REQUEST (on-demand) or PROVISIONED for the orders table"
  type        = string
  default     = "PAY_PER_REQUEST"

  validation {
    condition     = contains(["PAY_PER_REQUEST", "PROVISIONED"], var.dynamodb_billing_mode)
    error_message = "dynamodb_billing_mode must be PAY_PER_REQUEST or PROVISIONED."
  }
}

variable "dynamodb_read_capacity" {
  description = "RCUs for the orders table and GSI1 when PROVISIONED"
  type        = number
  default     = 5
}

variable "dynamodb_write_capacity" {
  description = "WCUs for the orders table and GSI1 when PROVISIONED"
  type        = number
  default     = 5
}

variable "dynamodb_deletion_protection" {
  description = "Block deletion of the orders table"
  type        = bool
  default     = true
}

variable "s3_raw_ia_days" {
  description = "Days before raw/ objects move to STANDARD_IA (>= 30)"
  type        = number
  default     = 30
}

variable "s3_raw_glacier_days" {
  description = "Days before raw/ objects move to GLACIER_IR (>= s3_raw_ia_days + 30)"
  type        = number
  default     = 180
}

variable "s3_noncurrent_expiration_days" {
  description = "Days old object versions in raw/ are kept"
  type        = number
  default     = 30
}

variable "s3_athena_results_expiration_days" {
  description = "Days Athena query results are kept"
  type        = number
  default     = 7
}

variable "docdb_instance_class" {
  description = "DocumentDB instance class (memory = cached working set of docs + indexes)"
  type        = string
  default     = "db.r6g.large"
}

variable "docdb_instance_count" {
  description = "DocumentDB instances: 1 primary + (n-1) replicas / failover targets"
  type        = number
  default     = 2
}

variable "docdb_deletion_protection" {
  description = "Block DocumentDB cluster deletion until this is turned off"
  type        = bool
  default     = true
}

variable "docdb_backup_retention_days" {
  description = "DocumentDB point-in-time restore window (1-35 days)"
  type        = number
  default     = 7
}

# ---------------------------------------------------------------- 05analytics

variable "athena_bytes_scanned_cutoff" {
  description = "Per-query scan limit in bytes for the Athena workgroup (min 10 MB)"
  type        = number
  default     = 10737418240
}

variable "redshift_base_rpu" {
  description = "Redshift Serverless base capacity in RPUs (8 minimum, steps of 8)"
  type        = number
  default     = 8
}

variable "redshift_max_rpu" {
  description = "Redshift Serverless max capacity in RPUs (cost guardrail)"
  type        = number
  default     = 64
}

# ---------------------------------------------------------------- 02messaging

variable "kinesis_stream_mode" {
  description = "ON_DEMAND or PROVISIONED for the clicks stream"
  type        = string
  default     = "ON_DEMAND"

  validation {
    condition     = contains(["ON_DEMAND", "PROVISIONED"], var.kinesis_stream_mode)
    error_message = "kinesis_stream_mode must be ON_DEMAND or PROVISIONED."
  }
}

variable "kinesis_shard_count" {
  description = "Shards when kinesis_stream_mode = PROVISIONED (ignored for ON_DEMAND)"
  type        = number
  default     = 1
}

variable "kinesis_retention_hours" {
  description = "Stream retention / replay window in hours (24-8760)"
  type        = number
  default     = 48
}

variable "msk_broker_instance_type" {
  description = "MSK broker instance type"
  type        = string
  default     = "kafka.m7g.large"
}

variable "msk_broker_count" {
  description = "MSK brokers; must be a multiple of az_count"
  type        = number
  default     = 3
}

variable "msk_volume_size_gib" {
  description = "EBS GiB per broker"
  type        = number
  default     = 500
}

variable "msk_log_retention_hours" {
  description = "Kafka log.retention.hours (topic data retention)"
  type        = number
  default     = 168
}
