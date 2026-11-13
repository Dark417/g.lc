# 01.04 prompt-flows — one Bedrock Flow (a-flow: Input -> Prompt (inline) -> Output), its execution role,
# and the app permissions to build, deploy (version + alias), and invoke flows.
#
# Creates
#   - aws_iam_role.flow               "a-flow-role" (assumed by bedrock.amazonaws.com to run the flow's nodes)
#   - aws_bedrockagent_flow.main      "a-flow" (DRAFT definition)
#   - aws_iam_role_policy.flows on aws_iam_role.app (00.03)
# Not created here: prepare / versions / aliases (no Terraform resources in provider 6.73) ⇒ the Python
# slice calls PrepareFlow, CreateFlowVersion, CreateFlowAlias; config then holds the alias ID.
# Used by: Python app/a01_04_prompt_flows (which also builds the same definition via CreateFlow)
# Lectures: AIP-C01 #28

variable "flow_model_id" {
  description = "Model for the flow's prompt node (inference profile ID accepted; check per model)."
  type        = string
  default     = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
}

locals {
  flow_foundation_model_id = replace(var.flow_model_id, "/^(us|eu|apac|global)\\./", "")
}

# ---------------------------------------------------------------- execution role

data "aws_iam_policy_document" "flow_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["bedrock.amazonaws.com"]
    }
    # Confused-deputy protection: only flows in this account may assume the role.
    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [local.account_id]
    }
    condition {
      test     = "ArnLike"
      variable = "aws:SourceArn"
      values   = ["arn:aws:bedrock:${var.region}:${local.account_id}:flow/*"]
    }
  }
}

resource "aws_iam_role" "flow" {
  name               = "${local.prefix}-flow-role"
  assume_role_policy = data.aws_iam_policy_document.flow_assume.json
  tags               = { Component = "01.04" }
}

data "aws_iam_policy_document" "flow_permissions" {
  # Prompt node: invoke its model (profile + foundation model in every Region the profile routes to).
  statement {
    sid     = "PromptNodeModel"
    actions = ["bedrock:InvokeModel"]
    resources = [
      "arn:aws:bedrock:${var.region}:${local.account_id}:inference-profile/${var.flow_model_id}",
      "arn:aws:bedrock:*::foundation-model/${local.flow_foundation_model_id}",
    ]
  }
  # Encrypted flow definition (customer_encryption_key_arn below).
  statement {
    sid       = "FlowKms"
    actions   = ["kms:Decrypt", "kms:GenerateDataKey"]
    resources = [aws_kms_key.main.arn]
  }
  # Add per node type when used: bedrock:Retrieve/RetrieveAndGenerate (KB node), lambda:InvokeFunction
  # (Lambda node), bedrock:GetPrompt + bedrock:RenderPrompt (managed-prompt node), s3:GetObject/PutObject (S3 nodes).
}

resource "aws_iam_role_policy" "flow" {
  name   = "flow-nodes"
  role   = aws_iam_role.flow.id
  policy = data.aws_iam_policy_document.flow_permissions.json
}

# ---------------------------------------------------------------- flow

resource "aws_bedrockagent_flow" "main" {
  name                        = "${local.prefix}-flow"
  description                 = "Input -> inline Prompt -> Output (01.04 showcase)"
  execution_role_arn          = aws_iam_role.flow.arn
  customer_encryption_key_arn = aws_kms_key.main.arn # omit for an AWS-owned key

  definition {
    # Entry node: exactly one output named "document". Type = what callers send (String here).
    node {
      name = "FlowInput"
      type = "Input"
      configuration {
        input {}
      }
      output {
        name = "document"
        type = "String"
      }
    }

    # Prompt node with an inline prompt. A managed prompt (01.03) would use source_configuration.resource.prompt_arn.
    node {
      name = "Summarize"
      type = "Prompt"
      configuration {
        prompt {
          source_configuration {
            inline {
              model_id      = var.flow_model_id
              template_type = "TEXT"
              inference_configuration {
                text {
                  max_tokens  = 300
                  temperature = 0.2 # low: consistent summaries
                  top_p       = 0.9
                }
              }
              template_configuration {
                text {
                  text = "Summarize the following for an on-call engineer in at most 3 bullets:\n<input>{{topic}}</input>"
                  input_variable {
                    name = "topic" # must match the node input name below
                  }
                }
              }
            }
          }
          # guardrail_configuration { guardrail_identifier = ... guardrail_version = ... }  # 04.01, for user input
        }
      }
      input {
        name       = "topic"
        type       = "String"
        expression = "$.data" # the whole incoming value; $.data.field selects inside an Object
      }
      output {
        name = "modelCompletion" # fixed output name of Prompt nodes
        type = "String"
      }
    }

    # Exit node: exactly one input named "document"; each Output node emits one flowOutputEvent.
    node {
      name = "FlowOutput"
      type = "Output"
      configuration {
        output {}
      }
      input {
        name       = "document"
        type       = "String"
        expression = "$.data"
      }
    }

    connection {
      name   = "InputToSummarize"
      source = "FlowInput"
      target = "Summarize"
      type   = "Data" # Data = output -> input; Conditional = from a Condition node's named condition
      configuration {
        data {
          source_output = "document"
          target_input  = "topic"
        }
      }
    }

    connection {
      name   = "SummarizeToOutput"
      source = "Summarize"
      target = "FlowOutput"
      type   = "Data"
      configuration {
        data {
          source_output = "modelCompletion"
          target_input  = "document"
        }
      }
    }
  }

  tags = { Component = "01.04" }
}

# ---------------------------------------------------------------- IAM for the app role

data "aws_iam_policy_document" "flows" {
  statement {
    sid = "BuildAndDeployFlows"
    actions = [
      "bedrock:CreateFlow",
      "bedrock:UpdateFlow",
      "bedrock:GetFlow",
      "bedrock:PrepareFlow",
      "bedrock:CreateFlowVersion",
      "bedrock:ListFlowVersions",
      "bedrock:CreateFlowAlias",
      "bedrock:UpdateFlowAlias",
      "bedrock:GetFlowAlias",
      "bedrock:ListFlowAliases",
    ]
    # flow/* (not only a-flow) because the Python showcase also creates a flow; narrow in production.
    resources = [
      "arn:aws:bedrock:${var.region}:${local.account_id}:flow/*",
      "arn:aws:bedrock:${var.region}:${local.account_id}:flow/*/alias/*",
    ]
  }

  statement {
    sid       = "ListAndValidate"
    actions   = ["bedrock:ListFlows", "bedrock:ValidateFlowDefinition"] # no resource-level permissions
    resources = ["*"]
  }

  # Runtime: InvokeFlow is authorized on the alias ARN (invoke aliases, never the DRAFT).
  statement {
    sid       = "InvokeFlowAliases"
    actions   = ["bedrock:InvokeFlow"]
    resources = ["arn:aws:bedrock:${var.region}:${local.account_id}:flow/*/alias/*"]
  }

  # Creating/updating a flow hands the execution role to Bedrock.
  statement {
    sid       = "PassFlowRole"
    actions   = ["iam:PassRole"]
    resources = [aws_iam_role.flow.arn]
    condition {
      test     = "StringEquals"
      variable = "iam:PassedToService"
      values   = ["bedrock.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy" "flows" {
  name   = "bedrock-flows"
  role   = aws_iam_role.app.id
  policy = data.aws_iam_policy_document.flows.json
}

# ---------------------------------------------------------------- outputs

output "flow_id" {
  description = "A_FLOWS_FLOW_ID"
  value       = aws_bedrockagent_flow.main.id
}

output "flow_arn" {
  value = aws_bedrockagent_flow.main.arn
}

output "flow_role_arn" {
  description = "A_FLOWS_EXECUTION_ROLE_ARN (CreateFlow from Python)"
  value       = aws_iam_role.flow.arn
}
