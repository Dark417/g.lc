# 03db.02dynamodb — single table "x-<env>-orders" (PK/SK), one GSI, TTL, streams, PITR.
# Used by: java _03db_02dynamodb, python _03db_02dynamodb.
# Per-env knobs: billing mode (+ capacity when PROVISIONED), deletion protection.
#
# Key design (single-table):
#   PK = CUSTOMER#<customerId>   SK = ORDER#<createdAtIso>#<orderId>   -> list a customer's orders by time
#   PK = CUSTOMER#<customerId>   SK = PROFILE                          -> the customer item
#   GSI1PK = STATUS#<status>     GSI1SK = <createdAtIso>               -> "all PENDING orders, oldest first"

locals {
  component   = "03db.02dynamodb"
  provisioned = var.billing_mode == "PROVISIONED"
}

resource "aws_dynamodb_table" "orders" {
  name = "${var.prefix}-orders"

  # On-demand: pay per request, no capacity planning. Switch to PROVISIONED + autoscaling when traffic is
  # steady and high (cheaper per request at sustained load; order of magnitude, check the pricing page).
  billing_mode   = var.billing_mode
  read_capacity  = local.provisioned ? var.read_capacity : null
  write_capacity = local.provisioned ? var.write_capacity : null

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
    read_capacity      = local.provisioned ? var.read_capacity : null
    write_capacity     = local.provisioned ? var.write_capacity : null
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
    kms_key_arn = var.kms_key_arn
  }

  deletion_protection_enabled = var.deletion_protection

  tags = { Component = local.component }
}

# Idempotency table: one item per request key, auto-expired. Shown by the "idempotent create" scenario.
resource "aws_dynamodb_table" "idempotency" {
  name         = "${var.prefix}-idempotency"
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
    kms_key_arn = var.kms_key_arn
  }

  tags = { Component = local.component }
}
