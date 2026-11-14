# prod — production account. Multi-AZ, standby replicas, long key deletion window, strict alarms. Mock values.
#   terraform init -backend-config=envs/prod.backend.hcl

env            = "prod"
region         = "us-east-1"
project_prefix = "a"
aws_account_id = "333333333333"
use_localstack = false
alert_email    = "alerts-prod@example.com"

# base
vpc_cidr                            = "10.40.0.0/16"
az_count                            = 3
kms_deletion_window_days            = 30 # maximum: a deleted key can be cancelled for a month
billing_threshold_usd               = 1000
data_bucket_noncurrent_version_days = 90

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
customization_base_model_id = "amazon.nova-lite-v1:0:300k"
prompt_model_id             = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
flow_model_id               = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

# 02rag
opensearch_standby_replicas = "ENABLED" # standby AZ: production availability, about 2x the OCU floor
kb_index_name               = "a-kb-index"
kb_embed_model_id           = "amazon.titan-embed-text-v2:0"
kb_generator_profile        = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"

# 04safety
guardrail_tier          = "STANDARD"
guardrail_profile_id    = "us.guardrail.v1:0"
eval_create_example_job = false # evals run in uat, not against prod

# 05ops
obs_model_id           = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
obs_latency_p90_ms     = 8000
obs_throttle_threshold = 0 # any throttle alarms
obs_log_retention_days = 90
