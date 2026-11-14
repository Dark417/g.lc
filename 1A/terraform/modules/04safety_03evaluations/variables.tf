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
  description = "Shared CMK (base_kms)"
  type        = string
}

variable "data_bucket_arn" {
  description = "Shared data bucket ARN (base_data_bucket); evals/ prefixes"
  type        = string
}

variable "data_bucket_name" {
  description = "Shared data bucket name (base_data_bucket)"
  type        = string
}

variable "knowledge_base_id" {
  description = "Knowledge base id for the example RAG eval job (from 02rag_04knowledge_bases)"
  type        = string
}

variable "create_example_job" {
  description = "Create the example RAG evaluation job. A job is a one-shot run: re-applying does not re-run it"
  type        = bool
}
