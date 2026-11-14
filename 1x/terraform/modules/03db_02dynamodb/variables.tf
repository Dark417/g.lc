# ---------------------------------------------------------------- wiring

variable "prefix" {
  description = "Name prefix, <project>-<env>"
  type        = string
}

variable "kms_key_arn" {
  type = string
}

variable "app_role_id" {
  description = "App role name that gets table access"
  type        = string
}

# ---------------------------------------------------------------- knobs

variable "billing_mode" {
  description = "PAY_PER_REQUEST or PROVISIONED (orders table)"
  type        = string
  default     = "PAY_PER_REQUEST"
}

variable "read_capacity" {
  description = "RCUs for table + GSI1 when PROVISIONED"
  type        = number
  default     = 5
}

variable "write_capacity" {
  description = "WCUs for table + GSI1 when PROVISIONED"
  type        = number
  default     = 5
}

variable "deletion_protection" {
  type    = bool
  default = true
}
