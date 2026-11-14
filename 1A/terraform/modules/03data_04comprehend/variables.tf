variable "region" {
  type = string
}

variable "account_id" {
  type = string
}

variable "app_role_id" {
  description = "App role (base_iam) the policy attaches to"
  type        = string
}
