# 01bedrock_01converse IAM — Bedrock inference policy on the app role.

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

  # Embeddings (02rag_01embeddings): InvokeModel only; embedding models have no streaming or Converse support.
  statement {
    sid       = "InvokeEmbeddingModels"
    actions   = ["bedrock:InvokeModel"]
    resources = local.embed_foundation_model_arns
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
  role   = var.app_role_id
  policy = data.aws_iam_policy_document.converse.json
}
