# 00.03 iam — the role the Java / Python app runs as (ECS task role shown; Lambda is the same idea).
# Each component file attaches its own least-privilege policy to this role.

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
  name               = "${local.prefix}-app"
  assume_role_policy = data.aws_iam_policy_document.app_assume.json
  tags               = { Component = "00.03" }
}

# Every component encrypts with the shared CMK, so the app needs to use it.
data "aws_iam_policy_document" "app_kms" {
  statement {
    actions   = ["kms:Decrypt", "kms:GenerateDataKey", "kms:DescribeKey"]
    resources = [aws_kms_key.main.arn]
  }
}

resource "aws_iam_role_policy" "app_kms" {
  name   = "kms"
  role   = aws_iam_role.app.id
  policy = data.aws_iam_policy_document.app_kms.json
}

output "app_role_arn" {
  value = aws_iam_role.app.arn
}
