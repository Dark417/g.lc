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

variable "converse_model_ids" {
  description = "Base foundation-model IDs the app may call (no Region prefix). Must match the Python/Java config. First = text model"
  type        = list(string)
}

variable "embed_model_ids" {
  description = "Embedding models the app may call with InvokeModel (02rag_01embeddings slice). In-Region, on-demand."
  type        = list(string)
}

variable "converse_profile_prefix" {
  description = "System inference profile geography prefix: us, eu, apac, or global (where offered)."
  type        = string
}
