# 03db.02dynamodb IAM — app-role item/query/transaction access to both tables and the GSI.

data "aws_iam_policy_document" "app_dynamodb" {
  statement {
    actions = [
      "dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:UpdateItem", "dynamodb:DeleteItem",
      "dynamodb:Query", "dynamodb:Scan", "dynamodb:BatchGetItem", "dynamodb:BatchWriteItem",
      "dynamodb:TransactWriteItems", "dynamodb:TransactGetItems", "dynamodb:ConditionCheckItem",
    ]
    resources = [
      aws_dynamodb_table.orders.arn,
      "${aws_dynamodb_table.orders.arn}/index/*",
      aws_dynamodb_table.idempotency.arn,
    ]
  }
}

resource "aws_iam_role_policy" "app_dynamodb" {
  name   = "dynamodb"
  role   = var.app_role_id
  policy = data.aws_iam_policy_document.app_dynamodb.json
}
