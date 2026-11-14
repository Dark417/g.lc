# main — one module block per 1A component (spec §1.2 code names), wired through module outputs.
# Foundation (base_*) first; every component takes the app role, the CMK, and the data bucket from it.
# Component-to-component links (all explicit here, never by resource address across modules):
#   02rag_02opensearch → 02rag_04knowledge_bases   collection ARN + KB service role
#   02rag_04knowledge_bases → 04safety_03evaluations  knowledge base id for the example RAG eval job
#   base_billing_alarm → 05ops_01observability   alerts topic for the Bedrock alarms
# Never applied (see AGENTS.md).

# ================================================================ base foundation

module "base_network" {
  source = "./modules/base_network"

  prefix   = local.prefix
  region   = var.region
  vpc_cidr = var.vpc_cidr
  az_count = var.az_count
}

module "base_kms" {
  source = "./modules/base_kms"

  prefix                  = local.prefix
  deletion_window_in_days = var.kms_deletion_window_days
}

module "base_iam" {
  source = "./modules/base_iam"

  prefix      = local.prefix
  kms_key_arn = module.base_kms.kms_key_arn
}

module "base_billing_alarm" {
  source = "./modules/base_billing_alarm"

  prefix                = local.prefix
  alert_email           = var.alert_email
  billing_threshold_usd = var.billing_threshold_usd
}

module "base_data_bucket" {
  source = "./modules/base_data_bucket"

  prefix                  = local.prefix
  account_id              = local.account_id
  kms_key_arn             = module.base_kms.kms_key_arn
  app_role_id             = module.base_iam.app_role_id
  noncurrent_version_days = var.data_bucket_noncurrent_version_days
}

# ================================================================ 01bedrock

module "_01bedrock_01converse" {
  source = "./modules/01bedrock_01converse"

  prefix                  = local.prefix
  region                  = var.region
  account_id              = local.account_id
  app_role_id             = module.base_iam.app_role_id
  converse_model_ids      = var.converse_model_ids
  embed_model_ids         = var.embed_model_ids
  converse_profile_prefix = var.converse_profile_prefix
}

module "_01bedrock_02customization" {
  source = "./modules/01bedrock_02customization"

  prefix                      = local.prefix
  region                      = var.region
  account_id                  = local.account_id
  app_role_id                 = module.base_iam.app_role_id
  kms_key_arn                 = module.base_kms.kms_key_arn
  data_bucket_arn             = module.base_data_bucket.bucket_arn
  data_bucket_name            = module.base_data_bucket.bucket
  customization_base_model_id = var.customization_base_model_id
}

module "_01bedrock_03prompt_management" {
  source = "./modules/01bedrock_03prompt_management"

  prefix          = local.prefix
  region          = var.region
  account_id      = local.account_id
  app_role_id     = module.base_iam.app_role_id
  kms_key_arn     = module.base_kms.kms_key_arn
  prompt_model_id = var.prompt_model_id
}

module "_01bedrock_04prompt_flows" {
  source = "./modules/01bedrock_04prompt_flows"

  prefix        = local.prefix
  region        = var.region
  account_id    = local.account_id
  app_role_id   = module.base_iam.app_role_id
  kms_key_arn   = module.base_kms.kms_key_arn
  flow_model_id = var.flow_model_id
}

# ================================================================ 02rag

module "_02rag_02opensearch" {
  source = "./modules/02rag_02opensearch"

  prefix                      = local.prefix
  region                      = var.region
  account_id                  = local.account_id
  app_role_arn                = module.base_iam.app_role_arn
  app_role_id                 = module.base_iam.app_role_id
  kms_key_arn                 = module.base_kms.kms_key_arn
  vpc_id                      = module.base_network.vpc_id
  private_subnet_ids          = module.base_network.private_subnet_ids
  endpoints_security_group_id = module.base_network.endpoints_security_group_id
  standby_replicas            = var.opensearch_standby_replicas
}

module "_02rag_04knowledge_bases" {
  source = "./modules/02rag_04knowledge_bases"

  prefix               = local.prefix
  region               = var.region
  account_id           = local.account_id
  app_role_id          = module.base_iam.app_role_id
  kms_key_arn          = module.base_kms.kms_key_arn
  data_bucket_arn      = module.base_data_bucket.bucket_arn
  kb_role_arn          = module._02rag_02opensearch.kb_role_arn
  kb_role_id           = module._02rag_02opensearch.kb_role_id
  aoss_collection_arn  = module._02rag_02opensearch.aoss_collection_arn
  kb_index_name        = var.kb_index_name
  kb_embed_model_id    = var.kb_embed_model_id
  kb_generator_profile = var.kb_generator_profile

  # The KB validates its index at create time: the AOSS data-access policy must exist first.
  depends_on = [module._02rag_02opensearch]
}

# ================================================================ 03data

module "_03data_01data_automation" {
  source = "./modules/03data_01data_automation"

  prefix      = local.prefix
  region      = var.region
  account_id  = local.account_id
  app_role_id = module.base_iam.app_role_id
  kms_key_arn = module.base_kms.kms_key_arn
}

module "_03data_02glue_data_quality" {
  source = "./modules/03data_02glue_data_quality"

  prefix           = local.prefix
  region           = var.region
  account_id       = local.account_id
  app_role_id      = module.base_iam.app_role_id
  kms_key_arn      = module.base_kms.kms_key_arn
  data_bucket_arn  = module.base_data_bucket.bucket_arn
  data_bucket_name = module.base_data_bucket.bucket
}

module "_03data_03transcribe" {
  source = "./modules/03data_03transcribe"

  prefix      = local.prefix
  region      = var.region
  account_id  = local.account_id
  app_role_id = module.base_iam.app_role_id
}

module "_03data_04comprehend" {
  source = "./modules/03data_04comprehend"

  region      = var.region
  account_id  = local.account_id
  app_role_id = module.base_iam.app_role_id
}

# ================================================================ 04safety

module "_04safety_01guardrails" {
  source = "./modules/04safety_01guardrails"

  prefix               = local.prefix
  region               = var.region
  account_id           = local.account_id
  app_role_id          = module.base_iam.app_role_id
  kms_key_arn          = module.base_kms.kms_key_arn
  guardrail_tier       = var.guardrail_tier
  guardrail_profile_id = var.guardrail_profile_id
}

module "_04safety_02pii_redaction" {
  source = "./modules/04safety_02pii_redaction"

  prefix           = local.prefix
  region           = var.region
  account_id       = local.account_id
  app_role_id      = module.base_iam.app_role_id
  kms_key_arn      = module.base_kms.kms_key_arn
  data_bucket_arn  = module.base_data_bucket.bucket_arn
  data_bucket_name = module.base_data_bucket.bucket
}

module "_04safety_03evaluations" {
  source = "./modules/04safety_03evaluations"

  prefix             = local.prefix
  region             = var.region
  account_id         = local.account_id
  app_role_id        = module.base_iam.app_role_id
  kms_key_arn        = module.base_kms.kms_key_arn
  data_bucket_arn    = module.base_data_bucket.bucket_arn
  data_bucket_name   = module.base_data_bucket.bucket
  knowledge_base_id  = module._02rag_04knowledge_bases.kb_id
  create_example_job = var.eval_create_example_job
}

# ================================================================ 05ops

module "_05ops_01observability" {
  source = "./modules/05ops_01observability"

  prefix                   = local.prefix
  region                   = var.region
  account_id               = local.account_id
  app_role_id              = module.base_iam.app_role_id
  kms_key_arn              = module.base_kms.kms_key_arn
  kms_deletion_window_days = var.kms_deletion_window_days
  data_bucket_arn          = module.base_data_bucket.bucket_arn
  data_bucket_name         = module.base_data_bucket.bucket
  alerts_topic_arn         = module.base_billing_alarm.alerts_topic_arn
  model_id                 = var.obs_model_id
  latency_p90_ms           = var.obs_latency_p90_ms
  throttle_threshold       = var.obs_throttle_threshold
  log_retention_days       = var.obs_log_retention_days
}
