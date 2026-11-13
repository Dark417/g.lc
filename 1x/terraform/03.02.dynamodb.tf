# 03.02 dynamodb — single table "x-orders" (PK/SK), one GSI, TTL, streams, PITR.
# Used by: java x03_02_dynamodb, python x03_02_dynamodb.
#
# Key design (single-table):
#   PK = CUSTOMER#<customerId>   SK = ORDER#<createdAtIso>#<orderId>   -> list a customer's orders by time
#   PK = CUSTOMER#<customerId>   SK = PROFILE                          -> the customer item
#   GSI1PK = STATUS#<status>     GSI1SK = <createdAtIso>               -> "all PENDING orders, oldest first"

resource "aws_dynamodb_table" "orders" {
  name = "${local.prefix}-orders"

  # On-demand: pay per request, no capacity planning. Switch to PROVISIONED + autoscaling when traffic is
  # steady and high (cheaper per request at sustained load; order of magnitude, check the pricing page).
  billing_mode = "PAY_PER_REQUEST"

  hash_key  = "PK"
  range_key = "SK"

  attribute {
    name = "PK"
    type = "S"
  }
  attribute {
    name = "SK"
    type = "S"
  }
  attribute {
    name = "GSI1PK"
    type = "S"
  }
  attribute {
    name = "GSI1SK"
    type = "S"
  }

  # GSI = a second copy of the data keyed differently; updated asynchronously (reads are eventually consistent).
  global_secondary_index {
    name               = "GSI1"
    hash_key           = "GSI1PK"
    range_key          = "GSI1SK"
    projection_type    = "INCLUDE" # copy only what the status query needs -> smaller index, cheaper writes
    non_key_attributes = ["orderId", "customerId", "amountCents"]
  }

  # Items with an epoch-seconds "expiresAt" are deleted by a background process (typically within days, not exact).
  ttl {
    attribute_name = "expiresAt"
    enabled        = true
  }

  # Change log for CDC consumers (Lambda, Kinesis adapter). NEW_AND_OLD_IMAGES = full before/after.
  stream_enabled   = true
  stream_view_type = "NEW_AND_OLD_IMAGES"

  point_in_time_recovery {
    enabled = true # restore to any second in the last 35 days
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.main.arn
  }

  deletion_protection_enabled = true

  tags = { Component = "03.02" }
}

# Idempotency table: one item per request key, auto-expired. Shown by the "idempotent create" scenario.
resource "aws_dynamodb_table" "idempotency" {
  name         = "${local.prefix}-idempotency"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "idempotencyKey"

  attribute {
    name = "idempotencyKey"
    type = "S"
  }

  ttl {
    attribute_name = "expiresAt"
    enabled        = true
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.main.arn
  }

  tags = { Component = "03.02" }
}

# ---------------------------------------------------------------- app access

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
  role   = aws_iam_role.app.id
  policy = data.aws_iam_policy_document.app_dynamodb.json
}

output "dynamodb_orders_table" {
  value = aws_dynamodb_table.orders.name
}

output "dynamodb_orders_stream_arn" {
  value = aws_dynamodb_table.orders.stream_arn
}
