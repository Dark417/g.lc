variable "prefix" {
  description = "Name prefix <project>-<env>, e.g. a-dev"
  type        = string
}

variable "region" {
  type = string
}

variable "account_id" {
  type = string
}

variable "app_role_arn" {
  description = "App role ARN (base_iam); named in the AOSS data-access policy"
  type        = string
}

variable "app_role_id" {
  description = "App role (base_iam) the IAM policy attaches to"
  type        = string
}

variable "kms_key_arn" {
  description = "Shared CMK (base_kms) for the encryption policy"
  type        = string
}

variable "vpc_id" {
  description = "VPC (base_network) for the AOSS VPC endpoint"
  type        = string
}

variable "private_subnet_ids" {
  description = "Private subnets (base_network) for the AOSS VPC endpoint"
  type        = list(string)
}

variable "endpoints_security_group_id" {
  description = "Interface-endpoint SG (base_network): 443 from the app"
  type        = string
}

variable "standby_replicas" {
  description = "ENABLED (prod: standby AZ, ~2x OCU floor) or DISABLED (dev: single AZ). Immutable after create"
  type        = string
}
