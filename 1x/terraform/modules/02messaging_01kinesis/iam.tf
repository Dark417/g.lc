# 02messaging.01kinesis IAM — the Firehose service role (stream -> lake bucket) and app-role produce/consume access.

# ---------------------------------------------------------------- Firehose role

data "aws_iam_policy_document" "firehose_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["firehose.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "firehose" {
  name               = "${var.prefix}-firehose"
  assume_role_policy = data.aws_iam_policy_document.firehose_assume.json
  tags               = { Component = local.component }
}

data "aws_iam_policy_document" "firehose" {
  statement {
    actions   = ["kinesis:DescribeStream", "kinesis:GetShardIterator", "kinesis:GetRecords", "kinesis:ListShards"]
    resources = [aws_kinesis_stream.clicks.arn]
  }
  statement {
    actions   = ["s3:PutObject", "s3:AbortMultipartUpload", "s3:GetBucketLocation", "s3:ListBucket"]
    resources = [var.lake_bucket_arn, "${var.lake_bucket_arn}/*"]
  }
  statement {
    actions   = ["kms:Decrypt", "kms:GenerateDataKey"]
    resources = [var.kms_key_arn]
  }
}

resource "aws_iam_role_policy" "firehose" {
  name   = "firehose"
  role   = aws_iam_role.firehose.id
  policy = data.aws_iam_policy_document.firehose.json
}

# ---------------------------------------------------------------- app access

data "aws_iam_policy_document" "app_kinesis" {
  statement {
    sid = "Stream"
    actions = [
      "kinesis:PutRecord", "kinesis:PutRecords", "kinesis:DescribeStreamSummary", "kinesis:ListShards",
      "kinesis:GetShardIterator", "kinesis:GetRecords", "kinesis:SubscribeToShard", "kinesis:RegisterStreamConsumer",
      "kinesis:DescribeStreamConsumer",
    ]
    resources = [aws_kinesis_stream.clicks.arn, "${aws_kinesis_stream.clicks.arn}/consumer/*"]
  }
  statement {
    sid       = "Firehose"
    actions   = ["firehose:PutRecord", "firehose:PutRecordBatch"]
    resources = [aws_kinesis_firehose_delivery_stream.events_direct.arn]
  }
}

resource "aws_iam_role_policy" "app_kinesis" {
  name   = "kinesis"
  role   = var.app_role_id
  policy = data.aws_iam_policy_document.app_kinesis.json
}
