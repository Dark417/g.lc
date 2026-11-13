# 01.01 bedrock-converse — least-privilege access to Bedrock inference for the app role,
# plus one application inference profile for cost attribution.
#
# Creates
#   - aws_iam_role_policy.converse on aws_iam_role.app (00.03)
#   - aws_bedrock_inference_profile.app  "a-app-profile" (copy of the text model's system profile, tagged)
# Used by
#   - Python app/a01_01_converse (and 01.05 prompting, which reuses these permissions)
#   - Java   com.lc.a.a01_01_converse
# Lectures: AIP-C01 #7–#10, #22
#
# IAM facts this policy relies on (Bedrock User Guide, "Converse API" + "Cross-Region inference", read 2026-11):
#   - Converse        is authorized by bedrock:InvokeModel                  (there is no bedrock:Converse action)
#   - ConverseStream  is authorized by bedrock:InvokeModelWithResponseStream (no bedrock:ConverseStream action)
#   - A cross-Region (system) inference profile like "us.anthropic..." needs BOTH
#       the inference-profile ARN in the calling Region, AND
#       the foundation-model ARN in every Region the profile may route to (hence region "*").
#   - An application inference profile needs its own ARN plus the underlying foundation models.

# ---------------------------------------------------------------- variables

variable "converse_model_ids" {
  description = "Base foundation-model IDs the app may call (no Region prefix). Must match the Python/Java config."
  type        = list(string)
  default = [
    "anthropic.claude-sonnet-4-5-20250929-v1:0", # a.models.text / A_TEXT_MODEL_ID (via us. profile)
    "anthropic.claude-haiku-4-5-20251001-v1:0",  # a.models.fast / A_FAST_MODEL_ID (via us. profile)
  ]
}

variable "converse_profile_prefix" {
  description = "System inference profile geography prefix: us, eu, apac, or global (where offered)."
  type        = string
  default     = "us" # us = routes across US Regions only; data stays in the US geography
}

# ---------------------------------------------------------------- locals

locals {
  converse_foundation_model_arns = [
    # "*" Region on purpose: a cross-Region profile may route to any Region in its set.
    for id in var.converse_model_ids : "arn:aws:bedrock:*::foundation-model/${id}"
  ]
  converse_system_profile_arns = [
    for id in var.converse_model_ids :
    "arn:aws:bedrock:${var.region}:${local.account_id}:inference-profile/${var.converse_profile_prefix}.${id}"
  ]
}

# ---------------------------------------------------------------- application inference profile

# Application inference profile = your own profile, copied from a system profile (or a model ARN).
# Trade-off:
#   + carries tags (cost allocation per app/tenant) and has its own CloudWatch dimension
#   + same price and routing as the profile it copies
#   - callers must use its ARN as modelId (an extra config value), and IAM must allow that ARN too
#   - one profile per model: changing the model means a new profile (ARN changes)
resource "aws_bedrock_inference_profile" "app" {
  name        = "${local.prefix}-app-profile"
  description = "Cost-tagged profile for the 1A app's text model"

  model_source {
    copy_from = local.converse_system_profile_arns[0] # first model = the text model
  }

  tags = {
    Component   = "01.01"
    CostCenter  = "ai-platform" # activate as a cost allocation tag in Billing to see spend per profile
    Application = "${local.prefix}-app"
  }
}

# ---------------------------------------------------------------- IAM for the app role

data "aws_iam_policy_document" "converse" {
  # Inference on the system cross-Region profiles (us.<model>) and the app profile.
  statement {
    sid = "InvokeViaProfiles"
    actions = [
      "bedrock:InvokeModel",                   # InvokeModel + Converse
      "bedrock:InvokeModelWithResponseStream", # InvokeModelWithResponseStream + ConverseStream
    ]
    resources = concat(local.converse_system_profile_arns, [aws_bedrock_inference_profile.app.arn])
  }

  # Inference on the foundation models themselves: direct in-Region calls with a bare model ID,
  # and the destination-Region hop of a profile call.
  statement {
    sid = "InvokeFoundationModels"
    actions = [
      "bedrock:InvokeModel",
      "bedrock:InvokeModelWithResponseStream",
    ]
    resources = local.converse_foundation_model_arns
  }

  # Read-only model discovery (control plane).
  # ListFoundationModels / ListInferenceProfiles do not support resource-level permissions ⇒ "*".
  statement {
    sid       = "DiscoverModels"
    actions   = ["bedrock:ListFoundationModels", "bedrock:ListInferenceProfiles"]
    resources = ["*"]
  }

  statement {
    sid       = "DescribeModels"
    actions   = ["bedrock:GetFoundationModel", "bedrock:GetInferenceProfile"]
    resources = concat(local.converse_foundation_model_arns, local.converse_system_profile_arns, [aws_bedrock_inference_profile.app.arn])
  }
}

resource "aws_iam_role_policy" "converse" {
  name   = "bedrock-converse"
  role   = aws_iam_role.app.id
  policy = data.aws_iam_policy_document.converse.json
}

# ---------------------------------------------------------------- outputs

output "converse_app_profile_arn" {
  description = "modelId for cost-tagged calls (A_CONVERSE_APP_PROFILE_ARN)"
  value       = aws_bedrock_inference_profile.app.arn
}

output "converse_system_profile_ids" {
  description = "Cross-Region inference profile IDs the app may call (A_TEXT_MODEL_ID / A_FAST_MODEL_ID)"
  value       = [for id in var.converse_model_ids : "${var.converse_profile_prefix}.${id}"]
}
