# modules/01bedrock_03prompt_management — one managed prompt (a-<env>-prompt) + the app permissions to manage and run prompts.
#
# Creates
#   - aws_bedrockagent_prompt.main  "a-<env>-prompt": DRAFT with one TEXT variant, two input variables, inference config
#   - aws_iam_role_policy.prompts on the app role (base_iam)          → iam.tf
# Not created here: prompt versions (no Terraform resource in provider 6.73) ⇒ the Python slice calls
# CreatePromptVersion; config then pins the version ARN (<prompt_arn>:<n>).
# Used by: Python app/{api,service,infra}/_01bedrock_03prompt_management
# Lectures: AIP-C01 #27

# ---------------------------------------------------------------- prompt

resource "aws_bedrockagent_prompt" "main" {
  name            = "${var.prefix}-prompt"
  description     = "Summarize a topic for an audience (01bedrock_03prompt_management showcase)"
  default_variant = "default" # the variant Converse runs when modelId = this prompt's ARN

  # CMK: prompt text is encrypted with the shared key. The caller (app role) already has
  # kms:Decrypt/GenerateDataKey on it (base_iam). Omit to use an AWS-owned key (no KMS cost, less control).
  customer_encryption_key_arn = var.kms_key_arn

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

  tags = { Component = "01bedrock_03prompt_management" }
}
