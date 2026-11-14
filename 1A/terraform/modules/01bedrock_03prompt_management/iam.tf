# 01bedrock_03prompt_management IAM — prompt management + run permissions on the app role.

data "aws_iam_policy_document" "prompts" {
  # Manage prompts in this account. Scoped to prompt/* (not only a-<env>-prompt) because the Python showcase
  # also creates prompts; narrow to aws_bedrockagent_prompt.main.arn (+ ":*" for versions) in production.
  statement {
    sid = "ManagePrompts"
    actions = [
      "bedrock:CreatePrompt",
      "bedrock:UpdatePrompt",
      "bedrock:GetPrompt",
      "bedrock:CreatePromptVersion",
    ]
    resources = ["arn:aws:bedrock:${var.region}:${var.account_id}:prompt/*"]
  }

  statement {
    sid       = "ListPrompts"
    actions   = ["bedrock:ListPrompts"] # list operations do not support resource-level permissions
    resources = ["*"]
  }

  # Converse(modelId = prompt ARN): Bedrock renders the prompt, then invokes the variant's model as the caller.
  # Uncertainty (2026-11): the Bedrock service authorization reference lists bedrock:RenderPrompt for this;
  # some docs mention only bedrock:GetPrompt. Both are granted (GetPrompt above) so either reading works.
  statement {
    sid       = "RunPrompts"
    actions   = ["bedrock:RenderPrompt"]
    resources = ["arn:aws:bedrock:${var.region}:${var.account_id}:prompt/*"]
  }

  # The variant's model: profile ARN + foundation model in every Region the profile routes to.
  # (Redundant if prompt_model_id is one of var.converse_model_ids in 01bedrock_01converse; kept so this module stands alone.)
  statement {
    sid     = "InvokePromptModel"
    actions = ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"]
    resources = [
      "arn:aws:bedrock:${var.region}:${var.account_id}:inference-profile/${var.prompt_model_id}",
      "arn:aws:bedrock:*::foundation-model/${replace(var.prompt_model_id, "/^(us|eu|apac|global)\\./", "")}",
    ]
  }
}

resource "aws_iam_role_policy" "prompts" {
  name   = "bedrock-prompts"
  role   = var.app_role_id
  policy = data.aws_iam_policy_document.prompts.json
}
