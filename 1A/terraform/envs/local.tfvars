# local — LocalStack on the laptop. Smallest everything, fake account, mock values.
#   terraform init -backend-config=envs/local.backend.hcl
#   terraform validate   (plan / apply are never run in this repo)
#
# NOT EMULATED BY LOCALSTACK: Bedrock (runtime, agent prompts/flows, knowledge bases, guardrails, evaluations,
# inference profiles, Data Automation, invocation logging) and OpenSearch Serverless. Those modules still
# validate here, but only S3 / KMS / IAM / SNS / CloudWatch / Logs / EC2 (VPC) / Glue / Transcribe / Comprehend
# would actually be created locally. Exercise the Bedrock + AOSS modules against the dev account.

env            = "local"
region         = "us-east-1"
project_prefix = "a"
aws_account_id = "000000000000" # LocalStack's default account; allowed_account_ids is skipped when use_localstack
use_localstack = true
alert_email    = "alerts-local@example.com"

# base
vpc_cidr                            = "10.10.0.0/16"
az_count                            = 1
kms_deletion_window_days            = 7
billing_threshold_usd               = 5 # LocalStack never bills; kept tiny so a misrouted apply alarms fast
data_bucket_noncurrent_version_days = 1

# 01bedrock (Bedrock not in LocalStack: values only shape the IAM policies)
converse_model_ids = [
  "anthropic.claude-haiku-4-5-20251001-v1:0", # text = fast model locally
]
embed_model_ids             = ["amazon.titan-embed-text-v2:0"]
converse_profile_prefix     = "us"
customization_base_model_id = "amazon.nova-micro-v1:0:128k"
prompt_model_id             = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
flow_model_id               = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

# 02rag (OpenSearch Serverless not in LocalStack)
opensearch_standby_replicas = "DISABLED"
kb_index_name               = "a-kb-index"
kb_embed_model_id           = "amazon.titan-embed-text-v2:0"
kb_generator_profile        = "us.anthropic.claude-haiku-4-5-20251001-v1:0"

# 04safety
guardrail_tier          = "CLASSIC" # no cross-Region profile needed
guardrail_profile_id    = "us.guardrail.v1:0"
eval_create_example_job = false

# 05ops
obs_model_id           = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
obs_latency_p90_ms     = 30000
obs_throttle_threshold = 50
obs_log_retention_days = 1
