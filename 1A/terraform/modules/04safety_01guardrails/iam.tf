# 04safety_01guardrails IAM — app policy (least privilege).

data "aws_iam_policy_document" "app_guardrails" {
  # Runtime: standalone checks + Converse guardrailConfig both need ApplyGuardrail on the guardrail.
  statement {
    sid     = "UseGuardrail"
    actions = ["bedrock:ApplyGuardrail", "bedrock:GetGuardrail"]
    resources = [
      aws_bedrock_guardrail.main.guardrail_arn,
      "${aws_bedrock_guardrail.main.guardrail_arn}:*", # versioned form
    ]
  }

  # STANDARD tier: the call is routed through the system guardrail profile in the geography's Regions.
  statement {
    sid       = "UseGuardrailProfile"
    actions   = ["bedrock:ApplyGuardrail"]
    resources = ["arn:aws:bedrock:*:${var.account_id}:guardrail-profile/${local.guardrail_profile_id}"]
  }

  # Converse / ConverseStream with a guardrail still need model invoke rights (cross-Region profiles -> Region *).
  statement {
    sid     = "InvokeModels"
    actions = ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"]
    resources = [
      "arn:aws:bedrock:*::foundation-model/*",
      "arn:aws:bedrock:*:${var.account_id}:inference-profile/*",
    ]
  }

  # Configuration-as-code scenario (infra.create_guardrail / update / version). Scoped to guardrails in this
  # account + Region. In prod, give this to a CI role, not the app role.
  statement {
    sid = "ManageGuardrailsFromSdk"
    actions = [
      "bedrock:CreateGuardrail",
      "bedrock:UpdateGuardrail",
      "bedrock:CreateGuardrailVersion",
      "bedrock:GetGuardrail",
      "bedrock:TagResource", # tags passed on CreateGuardrail
    ]
    resources = ["arn:aws:bedrock:${var.region}:${var.account_id}:guardrail/*"]
  }

  # List APIs cannot be scoped to a resource. InvokeGuardrailChecks (inline checks, no guardrail resource) is new;
  # action name assumed to match the operation - verify in the Service Authorization Reference.
  statement {
    sid       = "ListAndInlineChecks"
    actions   = ["bedrock:ListGuardrails", "bedrock:InvokeGuardrailChecks"]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "app_guardrails" {
  name   = "guardrails"
  role   = var.app_role_id
  policy = data.aws_iam_policy_document.app_guardrails.json
}
