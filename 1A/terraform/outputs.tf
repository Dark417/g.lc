# outputs — names / ARNs / endpoints the Java and Python config needs, re-exported from the modules.
# Output names are unchanged from the old flat stack. AWS names now carry the env:
#   a-<env>-guardrail, a-<env>-kb, a-<env>-vectors, a-<env>-ai-data-<account>, ...
# so the app config must read these outputs per env instead of assuming "a-<thing>".

output "name_prefix" {
  description = "Prefix of every AWS name in this env (<project_prefix>-<env>)"
  value       = local.prefix
}

# ---------------------------------------------------------------- base

output "vpc_id" {
  value = module.base_network.vpc_id
}

output "private_subnet_ids" {
  value = module.base_network.private_subnet_ids
}

output "kms_key_arn" {
  value = module.base_kms.kms_key_arn
}

output "app_role_arn" {
  value = module.base_iam.app_role_arn
}

output "alerts_topic_arn" {
  value = module.base_billing_alarm.alerts_topic_arn
}

output "data_bucket" {
  value = module.base_data_bucket.bucket
}

# ---------------------------------------------------------------- 01bedrock

output "converse_app_profile_arn" {
  description = "modelId for cost-tagged calls (A_CONVERSE_APP_PROFILE_ARN)"
  value       = module._01bedrock_01converse.converse_app_profile_arn
}

output "converse_system_profile_ids" {
  description = "Cross-Region inference profile IDs the app may call (A_TEXT_MODEL_ID / A_FAST_MODEL_ID)"
  value       = module._01bedrock_01converse.converse_system_profile_ids
}

output "customization_role_arn" {
  description = "A_CUSTOMIZATION_ROLE_ARN"
  value       = module._01bedrock_02customization.customization_role_arn
}

output "customization_s3_prefix" {
  description = "A_CUSTOMIZATION_S3_PREFIX"
  value       = module._01bedrock_02customization.customization_s3_prefix
}

output "prompt_id" {
  description = "A_PROMPTS_PROMPT_ID"
  value       = module._01bedrock_03prompt_management.prompt_id
}

output "prompt_arn" {
  description = "Base ARN (DRAFT). Production config pins <prompt_arn>:<version> after CreatePromptVersion."
  value       = module._01bedrock_03prompt_management.prompt_arn
}

output "flow_id" {
  description = "A_FLOWS_FLOW_ID"
  value       = module._01bedrock_04prompt_flows.flow_id
}

output "flow_arn" {
  value = module._01bedrock_04prompt_flows.flow_arn
}

output "flow_role_arn" {
  description = "A_FLOWS_EXECUTION_ROLE_ARN (CreateFlow from Python)"
  value       = module._01bedrock_04prompt_flows.flow_role_arn
}

# ---------------------------------------------------------------- 02rag

output "aoss_collection_endpoint" {
  description = "https://<id>.<region>.aoss.amazonaws.com → A_OPENSEARCH_COLLECTION_ENDPOINT (host part)"
  value       = module._02rag_02opensearch.aoss_collection_endpoint
}

output "aoss_collection_arn" {
  value = module._02rag_02opensearch.aoss_collection_arn
}

output "aoss_collection_id" {
  value = module._02rag_02opensearch.aoss_collection_id
}

output "kb_role_arn" {
  value = module._02rag_02opensearch.kb_role_arn
}

output "kb_id" {
  description = "A_KB_KNOWLEDGE_BASE_ID"
  value       = module._02rag_04knowledge_bases.kb_id
}

output "kb_arn" {
  value = module._02rag_04knowledge_bases.kb_arn
}

output "kb_data_source_id" {
  description = "A_KB_DATA_SOURCE_ID"
  value       = module._02rag_04knowledge_bases.kb_data_source_id
}

# ---------------------------------------------------------------- 03data

output "bda_project_arn" {
  value = module._03data_01data_automation.bda_project_arn
}

output "bda_blueprint_arn" {
  value = module._03data_01data_automation.bda_blueprint_arn
}

output "glue_database" {
  value = module._03data_02glue_data_quality.glue_database
}

output "glue_dq_ruleset_name" {
  value = module._03data_02glue_data_quality.glue_dq_ruleset_name
}

output "glue_dq_role_arn" {
  value = module._03data_02glue_data_quality.glue_dq_role_arn
}

output "transcribe_vocabulary_name" {
  value = module._03data_03transcribe.transcribe_vocabulary_name
}

output "transcribe_filter_name" {
  value = module._03data_03transcribe.transcribe_filter_name
}

# ---------------------------------------------------------------- 04safety

output "guardrail_id" {
  description = "A_GUARDRAILS_GUARDRAIL_ID / a.guardrails.guardrail-id"
  value       = module._04safety_01guardrails.guardrail_id
}

output "guardrail_arn" {
  value = module._04safety_01guardrails.guardrail_arn
}

output "guardrail_version" {
  description = "\"1\"; A_GUARDRAILS_GUARDRAIL_VERSION"
  value       = module._04safety_01guardrails.guardrail_version
}

output "guardrail_name" {
  value = module._04safety_01guardrails.guardrail_name
}

output "comprehend_pii_role_arn" {
  description = "A_PII_DATA_ACCESS_ROLE_ARN"
  value       = module._04safety_02pii_redaction.comprehend_pii_role_arn
}

output "pii_input_s3_uri" {
  value = module._04safety_02pii_redaction.pii_input_s3_uri
}

output "pii_output_s3_uri" {
  value = module._04safety_02pii_redaction.pii_output_s3_uri
}

output "bedrock_eval_role_arn" {
  description = "A_EVALS_ROLE_ARN"
  value       = module._04safety_03evaluations.bedrock_eval_role_arn
}

output "eval_datasets_s3_uri" {
  value = module._04safety_03evaluations.eval_datasets_s3_uri
}

output "eval_results_s3_uri" {
  value = module._04safety_03evaluations.eval_results_s3_uri
}

# ---------------------------------------------------------------- 05ops

output "invocation_log_group" {
  value = module._05ops_01observability.invocation_log_group
}

output "obs_metric_namespace" {
  value = module._05ops_01observability.obs_metric_namespace
}
