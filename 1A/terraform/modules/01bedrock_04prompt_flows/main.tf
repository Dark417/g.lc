# modules/01bedrock_04prompt_flows — one Bedrock Flow (a-<env>-flow: Input -> Prompt (inline) -> Output), its execution
# role, and the app permissions to build, deploy (version + alias), and invoke flows.
#
# Creates
#   - aws_iam_role.flow               "a-<env>-flow-role" (assumed by bedrock.amazonaws.com to run the flow's nodes) → iam.tf
#   - aws_bedrockagent_flow.main      "a-<env>-flow" (DRAFT definition)
#   - aws_iam_role_policy.flows on the app role (base_iam)                                                  → iam.tf
# Not created here: prepare / versions / aliases (no Terraform resources in provider 6.73) ⇒ the Python
# slice calls PrepareFlow, CreateFlowVersion, CreateFlowAlias; config then holds the alias ID.
# Used by: Python app/{api,service,infra}/_01bedrock_04prompt_flows (which also builds the same definition via CreateFlow)
# Lectures: AIP-C01 #28

locals {
  flow_foundation_model_id = replace(var.flow_model_id, "/^(us|eu|apac|global)\\./", "")
}

# ---------------------------------------------------------------- flow

resource "aws_bedrockagent_flow" "main" {
  name                        = "${var.prefix}-flow"
  description                 = "Input -> inline Prompt -> Output (01bedrock_04prompt_flows showcase)"
  execution_role_arn          = aws_iam_role.flow.arn
  customer_encryption_key_arn = var.kms_key_arn # omit for an AWS-owned key

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

    # Prompt node with an inline prompt. A managed prompt (01bedrock_03prompt_management) would use
    # source_configuration.resource.prompt_arn.
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
          # guardrail_configuration { guardrail_identifier = ... guardrail_version = ... }  # 04safety_01guardrails, for user input
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

  tags = { Component = "01bedrock_04prompt_flows" }
}
