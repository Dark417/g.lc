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
  description = "App role (base_iam) the query policy attaches to"
  type        = string
}

variable "kms_key_arn" {
  description = "Shared CMK (base_kms)"
  type        = string
}

variable "data_bucket_arn" {
  description = "Shared data bucket ARN (base_data_bucket); source = kb-docs/ prefix"
  type        = string
}

variable "kb_role_arn" {
  description = "KB service role ARN (02rag_02opensearch)"
  type        = string
}

variable "kb_role_id" {
  description = "KB service role name (02rag_02opensearch); this module attaches its permissions"
  type        = string
}

variable "aoss_collection_arn" {
  description = "Vector collection ARN (02rag_02opensearch)"
  type        = string
}

variable "kb_index_name" {
  description = "Vector index created by Python (= A_OPENSEARCH_INDEX_NAME)"
  type        = string
}

variable "kb_embed_model_id" {
  description = "Embedding model; dimension must equal the index knn_vector dimension (1024)"
  type        = string
}

variable "kb_generator_profile" {
  description = "Cross-region inference profile id used by RetrieveAndGenerate"
  type        = string
}
