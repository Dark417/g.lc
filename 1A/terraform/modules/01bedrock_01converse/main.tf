# modules/01bedrock_01converse — least-privilege access to Bedrock inference for the app role,
# plus one application inference profile for cost attribution.
#
# Creates
#   - aws_iam_role_policy.converse on the app role (base_iam)          → iam.tf
#   - aws_bedrock_inference_profile.app  "a-<env>-app-profile" (copy of the text model's system profile, tagged)
# Used by
#   - Python app/{api,service,infra}/_01bedrock_01converse (and 01bedrock_05prompt_engineering, which reuses these permissions)
#   - Python app/infra/_02rag_01embeddings (InvokeModel on the embedding models in var.embed_model_ids)
#   - Java   com.lc.a.{api,service,infra}._01bedrock_01converse
# Lectures: AIP-C01 #7–#10, #22
#
# IAM facts this policy relies on (Bedrock User Guide, "Converse API" + "Cross-Region inference", read 2026-11):
#   - Converse        is authorized by bedrock:InvokeModel                  (there is no bedrock:Converse action)
#   - ConverseStream  is authorized by bedrock:InvokeModelWithResponseStream (no bedrock:ConverseStream action)
#   - A cross-Region (system) inference profile like "us.anthropic..." needs BOTH
#       the inference-profile ARN in the calling Region, AND
#       the foundation-model ARN in every Region the profile may route to (hence region "*").
#   - An application inference profile needs its own ARN plus the underlying foundation models.

# ---------------------------------------------------------------- locals

locals {
  converse_foundation_model_arns = [
    # "*" Region on purpose: a cross-Region profile may route to any Region in its set.
    for id in var.converse_model_ids : "arn:aws:bedrock:*::foundation-model/${id}"
  ]
  # Embedding models are called in-Region by bare model ID (no inference profile) ⇒ this Region only.
  embed_foundation_model_arns = [
    for id in var.embed_model_ids : "arn:aws:bedrock:${var.region}::foundation-model/${id}"
  ]
  converse_system_profile_arns = [
    for id in var.converse_model_ids :
    "arn:aws:bedrock:${var.region}:${var.account_id}:inference-profile/${var.converse_profile_prefix}.${id}"
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
  name        = "${var.prefix}-app-profile"
  description = "Cost-tagged profile for the 1A app's text model"

  model_source {
    copy_from = local.converse_system_profile_arns[0] # first model = the text model
  }

  tags = {
    Component   = "01bedrock_01converse"
    CostCenter  = "ai-platform" # activate as a cost allocation tag in Billing to see spend per profile
    Application = "${var.prefix}-app"
  }
}
