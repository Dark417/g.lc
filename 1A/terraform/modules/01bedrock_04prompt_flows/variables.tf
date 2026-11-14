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

variable "app_role_id" {
  description = "App role (base_iam) the policy attaches to"
  type        = string
}

variable "kms_key_arn" {
  description = "Shared CMK (base_kms) that encrypts the flow definition"
  type        = string
}

variable "flow_model_id" {
  description = "Model for the flow's prompt node (inference profile ID accepted; check per model)."
  type        = string
}
