# 01bedrock_04prompt_flows IAM — the flow execution role + the app-role policy.

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
      values   = [var.account_id]
    }
    condition {
      test     = "ArnLike"
      variable = "aws:SourceArn"
      values   = ["arn:aws:bedrock:${var.region}:${var.account_id}:flow/*"]
    }
  }
}

resource "aws_iam_role" "flow" {
  name               = "${var.prefix}-flow-role"
  assume_role_policy = data.aws_iam_policy_document.flow_assume.json
  tags               = { Component = "01bedrock_04prompt_flows" }
}

data "aws_iam_policy_document" "flow_permissions" {
  # Prompt node: invoke its model (profile + foundation model in every Region the profile routes to).
  statement {
    sid     = "PromptNodeModel"
    actions = ["bedrock:InvokeModel"]
    resources = [
      "arn:aws:bedrock:${var.region}:${var.account_id}:inference-profile/${var.flow_model_id}",
      "arn:aws:bedrock:*::foundation-model/${local.flow_foundation_model_id}",
    ]
  }
  # Encrypted flow definition (customer_encryption_key_arn in main.tf).
  statement {
    sid       = "FlowKms"
    actions   = ["kms:Decrypt", "kms:GenerateDataKey"]
    resources = [var.kms_key_arn]
  }
  # Add per node type when used: bedrock:Retrieve/RetrieveAndGenerate (KB node), lambda:InvokeFunction
  # (Lambda node), bedrock:GetPrompt + bedrock:RenderPrompt (managed-prompt node), s3:GetObject/PutObject (S3 nodes).
}

resource "aws_iam_role_policy" "flow" {
  name   = "flow-nodes"
  role   = aws_iam_role.flow.id
  policy = data.aws_iam_policy_document.flow_permissions.json
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
    # flow/* (not only a-<env>-flow) because the Python showcase also creates a flow; narrow in production.
    resources = [
      "arn:aws:bedrock:${var.region}:${var.account_id}:flow/*",
      "arn:aws:bedrock:${var.region}:${var.account_id}:flow/*/alias/*",
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
    resources = ["arn:aws:bedrock:${var.region}:${var.account_id}:flow/*/alias/*"]
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
  role   = var.app_role_id
  policy = data.aws_iam_policy_document.flows.json
}
