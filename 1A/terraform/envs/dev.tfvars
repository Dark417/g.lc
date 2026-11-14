# dev — shared developer account. Small and cheap, single-AZ vector store, short retention. Mock values.
#   terraform init -backend-config=envs/dev.backend.hcl

env            = "dev"
region         = "us-east-1"
project_prefix = "a"
aws_account_id = "111111111111"
use_localstack = false
alert_email    = "alerts-dev@example.com"

# base
vpc_cidr                            = "10.20.0.0/16"
az_count                            = 2
kms_deletion_window_days            = 7
billing_threshold_usd               = 20
data_bucket_noncurrent_version_days = 14

# 01bedrock
converse_model_ids = [
  "anthropic.claude-sonnet-4-5-20250929-v1:0", # a.models.text / A_TEXT_MODEL_ID
  "anthropic.claude-haiku-4-5-20251001-v1:0",  # a.models.fast / A_FAST_MODEL_ID
]
embed_model_ids = [
  "amazon.titan-embed-text-v2:0",
  "cohere.embed-english-v3",
]
converse_profile_prefix     = "us"
customization_base_model_id = "amazon.nova-micro-v1:0:128k"
prompt_model_id             = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
flow_model_id               = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

# 02rag
opensearch_standby_replicas = "DISABLED" # single-AZ: about half the OCU floor
kb_index_name               = "a-kb-index"
kb_embed_model_id           = "amazon.titan-embed-text-v2:0"
kb_generator_profile        = "us.anthropic.claude-haiku-4-5-20251001-v1:0" # cheaper generator in dev

# 04safety
guardrail_tier          = "STANDARD"
guardrail_profile_id    = "us.guardrail.v1:0"
eval_create_example_job = false

# 05ops
obs_model_id           = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
obs_latency_p90_ms     = 15000
obs_throttle_threshold = 10
obs_log_retention_days = 7
