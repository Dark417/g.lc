# 03data_01data_automation IAM — app policy (least privilege). No service role: BDA runs as the caller.

data "aws_iam_policy_document" "app_bda" {
  statement {
    sid     = "InvokeAsync"
    actions = ["bedrock:InvokeDataAutomationAsync"]
    resources = [
      aws_bedrockdataautomation_project.docs.arn,
      # Cross-region inference profile; the exact ARN shape is documented in the BDA IAM guide - verify.
      "arn:aws:bedrock:*:${var.account_id}:data-automation-profile/*",
    ]
  }
  statement {
    sid       = "PollStatus"
    actions   = ["bedrock:GetDataAutomationStatus"]
    resources = ["arn:aws:bedrock:${var.region}:${var.account_id}:data-automation-invocation/*"]
  }
  statement {
    sid     = "ReadConfig"
    actions = ["bedrock:GetBlueprint", "bedrock:GetDataAutomationProject", "bedrock:ListBlueprints", "bedrock:ListDataAutomationProjects"]
    resources = [
      aws_bedrockdataautomation_blueprint.invoice.arn,
      aws_bedrockdataautomation_project.docs.arn,
      "arn:aws:bedrock:${var.region}:${var.account_id}:blueprint/*",
    ]
  }
  statement {
    # Needed only by the config-as-code showcase in python (create_*). Drop in production: Terraform owns these.
    sid       = "ConfigAsCodeShowcase"
    actions   = ["bedrock:CreateBlueprint", "bedrock:CreateDataAutomationProject"]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "app_bda" {
  name   = "bda"
  role   = var.app_role_id
  policy = data.aws_iam_policy_document.app_bda.json
}
