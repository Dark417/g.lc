# base_iam IAM — the shared app role + its KMS grant.
# Each component module attaches its own least-privilege policy to this role.

data "aws_iam_policy_document" "app_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com", "lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "app" {
  name               = "${var.prefix}-app"
  assume_role_policy = data.aws_iam_policy_document.app_assume.json
  tags               = { Component = "base_iam" }
}

# Every component encrypts with the shared CMK, so the app needs to use it.
data "aws_iam_policy_document" "app_kms" {
  statement {
    actions   = ["kms:Decrypt", "kms:GenerateDataKey", "kms:DescribeKey"]
    resources = [var.kms_key_arn]
  }
}

resource "aws_iam_role_policy" "app_kms" {
  name   = "kms"
  role   = aws_iam_role.app.id
  policy = data.aws_iam_policy_document.app_kms.json
}
