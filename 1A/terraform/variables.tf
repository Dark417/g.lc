# variables — every per-env knob. Defaults = the old flat-stack values; envs/<env>.tfvars override them.
# Grouped by the module that consumes them (spec §1.2 code names).

# ---------------------------------------------------------------- environment

variable "env" {
  description = "Environment name; part of every AWS name (a-<env>-<thing>)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["local", "dev", "uat", "prod"], var.env)
    error_message = "The env value must be one of local, dev, uat, prod."
  }
}

variable "region" {
  description = "AWS region for every resource"
  type        = string
  default     = "us-east-1"
}

variable "project_prefix" {
  description = "Project part of the name prefix; local.prefix = <project_prefix>-<env> (e.g. a-dev-guardrail, a-dev-kb)"
  type        = string
  default     = "a"
}

variable "aws_account_id" {
  description = "Account this env deploys to; the provider refuses any other (ignored when use_localstack)"
  type        = string
  default     = "111111111111"
}

variable "use_localstack" {
  description = "Point the AWS provider at LocalStack (env = local only)"
  type        = bool
  default     = false
}

variable "localstack_endpoint" {
  description = "LocalStack edge endpoint used for every emulated service"
  type        = string
  default     = "http://localhost:4566"
}

variable "alert_email" {
  description = "Email that receives cost and GenAI alarms (SNS subscription must be confirmed by hand)"
  type        = string
  default     = "alerts@example.com"
}

# ---------------------------------------------------------------- base_network

variable "vpc_cidr" {
  description = "VPC CIDR; one private /20 per AZ is carved from it"
  type        = string
  default     = "10.40.0.0/16"
}

variable "az_count" {
  description = "Number of AZs for private subnets; 2 is enough for endpoints + OpenSearch standby"
  type        = number
  default     = 2
}

# ---------------------------------------------------------------- base_kms

variable "kms_deletion_window_days" {
  description = "Waiting period before a deleted CMK is gone for good (7-30). Longer in prod = more time to undo"
  type        = number
  default     = 7
}

# ---------------------------------------------------------------- base_billing_alarm

variable "billing_threshold_usd" {
  description = "Alarm when month-to-date estimated charges exceed this many USD"
  type        = number
  default     = 20
}

# ---------------------------------------------------------------- base_data_bucket

variable "data_bucket_noncurrent_version_days" {
  description = "Days an overwritten or deleted object version is kept before S3 expires it (versioning is on)"
  type        = number
  default     = 30
}

# ---------------------------------------------------------------- 01bedrock_01converse

variable "converse_model_ids" {
  description = "Base foundation-model IDs the app may call (no Region prefix). Must match the Python/Java config."
  type        = list(string)
  default = [
    "anthropic.claude-sonnet-4-5-20250929-v1:0", # a.models.text / A_TEXT_MODEL_ID (via us. profile)
    "anthropic.claude-haiku-4-5-20251001-v1:0",  # a.models.fast / A_FAST_MODEL_ID (via us. profile)
  ]
}

variable "embed_model_ids" {
  description = "Embedding models the app may call with InvokeModel (02rag_01embeddings slice). In-Region, on-demand."
  type        = list(string)
  default = [
    "amazon.titan-embed-text-v2:0", # A_EMBED_MODEL_ID (shared default)
    "cohere.embed-english-v3",      # 02rag_01embeddings comparison function
  ]
}

variable "converse_profile_prefix" {
  description = "System inference profile geography prefix: us, eu, apac, or global (where offered)."
  type        = string
  default     = "us" # us = routes across US Regions only; data stays in the US geography
}

# ---------------------------------------------------------------- 01bedrock_02customization

variable "customization_base_model_id" {
  description = "Base model to customize. Find candidates with ListFoundationModels(byCustomizationType=FINE_TUNING)."
  type        = string
  default     = "amazon.nova-micro-v1:0:128k" # customizable IDs often carry a context suffix (":128k"); check per Region
}

# ---------------------------------------------------------------- 01bedrock_03prompt_management

variable "prompt_model_id" {
  description = "Model the prompt's variant runs on. Inference profile IDs are accepted (check per model)."
  type        = string
  default     = "us.anthropic.claude-haiku-4-5-20251001-v1:0" # fast model: summaries don't need the large one
}

# ---------------------------------------------------------------- 01bedrock_04prompt_flows

variable "flow_model_id" {
  description = "Model for the flow's prompt node (inference profile ID accepted; check per model)."
  type        = string
  default     = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
}

# ---------------------------------------------------------------- 02rag_02opensearch

variable "opensearch_standby_replicas" {
  description = "ENABLED = standby-AZ replicas (prod availability, about 2x the OCU floor); DISABLED = single-AZ (dev). Immutable"
  type        = string
  default     = "DISABLED"

  validation {
    condition     = contains(["ENABLED", "DISABLED"], var.opensearch_standby_replicas)
    error_message = "The opensearch_standby_replicas value must be ENABLED or DISABLED."
  }
}

# ---------------------------------------------------------------- 02rag_04knowledge_bases

variable "kb_index_name" {
  description = "Vector index the KB writes to; created by Python (= A_OPENSEARCH_INDEX_NAME)"
  type        = string
  default     = "a-kb-index"
}

variable "kb_embed_model_id" {
  description = "Embedding model of the KB; its dimension must equal the index knn_vector dimension (1024)"
  type        = string
  default     = "amazon.titan-embed-text-v2:0"
}

variable "kb_generator_profile" {
  description = "Generator for RetrieveAndGenerate: a cross-region inference profile (= app.shared.config text_model_id)"
  type        = string
  default     = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
}

# ---------------------------------------------------------------- 04safety_01guardrails

variable "guardrail_tier" {
  description = "CLASSIC or STANDARD. STANDARD = more languages, typo/obfuscation robustness, prompt-leakage detection; needs a cross-Region guardrail profile"
  type        = string
  default     = "STANDARD"
}

variable "guardrail_profile_id" {
  description = "System guardrail profile for the STANDARD tier; geography prefix must match the Region (us. / eu. / apac.)"
  type        = string
  default     = "us.guardrail.v1:0"
}

# ---------------------------------------------------------------- 04safety_03evaluations

variable "eval_create_example_job" {
  description = "Create the example RAG evaluation job. A job is a one-shot run: re-applying does not re-run it"
  type        = bool
  default     = false
}

# ---------------------------------------------------------------- 05ops_01observability

variable "obs_model_id" {
  description = "ModelId dimension value the alarms watch (the model or inference profile id the app calls)"
  type        = string
  default     = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
}

variable "obs_latency_p90_ms" {
  description = "Alarm when p90 InvocationLatency exceeds this many milliseconds"
  type        = number
  default     = 10000
}

variable "obs_throttle_threshold" {
  description = "Alarm when InvocationThrottles in 5 min exceed this count (0 = any throttle alarms)"
  type        = number
  default     = 0
}

variable "obs_log_retention_days" {
  description = "Invocation logs hold prompts: keep them only as long as debugging and audit need"
  type        = number
  default     = 30
}
