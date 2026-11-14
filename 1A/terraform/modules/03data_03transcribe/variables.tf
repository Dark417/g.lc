variable "prefix" {
  description = "Name prefix <project>-<env>, e.g. a-dev; transcription job names must start with it"
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
