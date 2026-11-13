# 01.03 prompt-management — one managed prompt (a-prompt) + the app permissions to manage and run prompts.
#
# Creates
#   - aws_bedrockagent_prompt.main  "a-prompt": DRAFT with one TEXT variant, two input variables, inference config
#   - aws_iam_role_policy.prompts on aws_iam_role.app (00.03)
# Not created here: prompt versions (no Terraform resource in provider 6.73) ⇒ the Python slice calls
# CreatePromptVersion; config then pins the version ARN (<prompt_arn>:<n>).
# Used by: Python app/a01_03_prompt_management
# Lectures: AIP-C01 #27

variable "prompt_model_id" {
  description = "Model the prompt's variant runs on. Inference profile IDs are accepted (check per model)."
  type        = string
  default     = "us.anthropic.claude-haiku-4-5-20251001-v1:0" # fast model: summaries don't need the large one
}

# ---------------------------------------------------------------- prompt

resource "aws_bedrockagent_prompt" "main" {
  name            = "${local.prefix}-prompt"
  description     = "Summarize a topic for an audience (01.03 showcase)"
  default_variant = "default" # the variant Converse runs when modelId = this prompt's ARN

  # CMK: prompt text is encrypted with the shared key. The caller (app role) already has
  # kms:Decrypt/GenerateDataKey on it (00.03). Omit to use an AWS-owned key (no KMS cost, less control).
  customer_encryption_key_arn = aws_kms_key.main.arn

  variant {
    name          = "default"
    template_type = "TEXT" # TEXT = one string; CHAT = system + messages (+ tool config, cache points)
    model_id      = var.prompt_model_id

    template_configuration {
      text {
        # {{var}} is Bedrock's placeholder syntax (not HCL interpolation: HCL uses ${...}).
        text = <<-EOT
          <task>Summarize {{topic}} for {{audience}}.</task>
          <format>At most 5 bullets, plain language, no marketing tone.</format>
        EOT

        # Every variable used in the text must be declared, or callers can't fill it.
        input_variable {
          name = "topic"
        }
        input_variable {
          name = "audience"
        }
      }
    }

    inference_configuration {
      text {
        max_tokens     = 400 # summaries are short; a tight cap also saves TPM quota
        temperature    = 0.2 # low = consistent wording across runs
        top_p          = 0.9
        stop_sequences = []
      }
    }

    metadata {
      key   = "owner"
      value = "ai-platform" # who reviews changes to this prompt
    }
  }

  tags = { Component = "01.03" }
}

# ---------------------------------------------------------------- IAM for the app role

data "aws_iam_policy_document" "prompts" {
  # Manage prompts in this account. Scoped to prompt/* (not only a-prompt) because the Python showcase
  # also creates prompts; narrow to aws_bedrockagent_prompt.main.arn (+ ":*" for versions) in production.
  statement {
    sid = "ManagePrompts"
    actions = [
      "bedrock:CreatePrompt",
      "bedrock:UpdatePrompt",
      "bedrock:GetPrompt",
      "bedrock:CreatePromptVersion",
    ]
    resources = ["arn:aws:bedrock:${var.region}:${local.account_id}:prompt/*"]
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
    resources = ["arn:aws:bedrock:${var.region}:${local.account_id}:prompt/*"]
  }

  # The variant's model: profile ARN + foundation model in every Region the profile routes to.
  # (Redundant if prompt_model_id is one of var.converse_model_ids in 01.01; kept so this file stands alone.)
  statement {
    sid     = "InvokePromptModel"
    actions = ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"]
    resources = [
      "arn:aws:bedrock:${var.region}:${local.account_id}:inference-profile/${var.prompt_model_id}",
      "arn:aws:bedrock:*::foundation-model/${replace(var.prompt_model_id, "/^(us|eu|apac|global)\\./", "")}",
    ]
  }
}

resource "aws_iam_role_policy" "prompts" {
  name   = "bedrock-prompts"
  role   = aws_iam_role.app.id
  policy = data.aws_iam_policy_document.prompts.json
}

# ---------------------------------------------------------------- outputs

output "prompt_id" {
  description = "A_PROMPTS_PROMPT_ID"
  value       = aws_bedrockagent_prompt.main.id
}

output "prompt_arn" {
  description = "Base ARN (DRAFT). Production config pins <prompt_arn>:<version> after CreatePromptVersion."
  value       = aws_bedrockagent_prompt.main.arn
}
