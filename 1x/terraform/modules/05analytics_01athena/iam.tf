# 05analytics.01athena IAM — app-role access to the workgroup and the Glue catalog entries.
# S3 access to the lake/results buckets is granted by 03db_03s3/iam.tf.

data "aws_iam_policy_document" "app_athena" {
  statement {
    actions = [
      "athena:StartQueryExecution", "athena:GetQueryExecution", "athena:GetQueryResults",
      "athena:StopQueryExecution", "athena:GetWorkGroup", "athena:ListQueryExecutions",
    ]
    resources = [aws_athena_workgroup.x.arn]
  }
  statement {
    actions = ["glue:GetDatabase", "glue:GetTable", "glue:GetPartitions", "glue:CreateTable", "glue:DeleteTable"]
    resources = [
      "arn:aws:glue:${var.region}:${var.account_id}:catalog",
      "arn:aws:glue:${var.region}:${var.account_id}:database/${aws_glue_catalog_database.lake.name}",
      "arn:aws:glue:${var.region}:${var.account_id}:table/${aws_glue_catalog_database.lake.name}/*",
    ]
  }
}

resource "aws_iam_role_policy" "app_athena" {
  name   = "athena"
  role   = var.app_role_id
  policy = data.aws_iam_policy_document.app_athena.json
}
