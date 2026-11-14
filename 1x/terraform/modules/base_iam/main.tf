# base_iam — the role the Java / Python app runs as (ECS task role shown; Lambda is the same idea).
# Each component module attaches its own least-privilege policy to this role in its iam.tf
# (including base_kms, which grants the app use of the shared CMK).

locals {
  component = "base_iam"
}

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
  tags               = { Component = local.component }
}
