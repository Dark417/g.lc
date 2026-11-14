# 03db.01aurora IAM — app-role access: IAM database auth for the x_app DB user.

data "aws_iam_policy_document" "app_aurora" {
  statement {
    sid       = "IamDbAuth"
    actions   = ["rds-db:connect"]
    resources = ["arn:aws:rds-db:${var.region}:${var.account_id}:dbuser:${aws_rds_cluster.aurora.cluster_resource_id}/${local.aurora_app_user}"]
  }
}

resource "aws_iam_role_policy" "app_aurora" {
  name   = "aurora"
  role   = var.app_role_id
  policy = data.aws_iam_policy_document.app_aurora.json
}
