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
  description = "Shared CMK (base_kms) that encrypts the prompt text"
  type        = string
}

variable "prompt_model_id" {
  description = "Model the prompt's variant runs on. Inference profile IDs are accepted (check per model)."
  type        = string
}
