# 05.01 kinesis — Kinesis Data Stream "x-clicks" + Firehose that lands it in S3 (raw/clicks/dt=.../),
# plus a direct-PUT Firehose "x-events" for producers that skip the stream.
# Used by: java/python x05_01_kinesis. Downstream: Athena table clicks (04.01).

resource "aws_kinesis_stream" "clicks" {
  name             = "${local.prefix}-clicks"
  retention_period = 48 # hours (24 default, up to 8760): replay window for consumers that fall behind

  # ON_DEMAND: AWS adds/removes shards from traffic. PROVISIONED: you pick shards
  # (each shard = 1 MB/s or 1,000 records/s in, 2 MB/s out; AWS Kinesis quotas page, 2026).
  stream_mode_details {
    stream_mode = "ON_DEMAND"
  }

  encryption_type = "KMS"
  kms_key_id      = aws_kms_key.main.arn

  shard_level_metrics = ["IncomingBytes", "WriteProvisionedThroughputExceeded", "IteratorAgeMilliseconds"]

  tags = { Component = "05.01" }
}

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
  name               = "${local.prefix}-firehose"
  assume_role_policy = data.aws_iam_policy_document.firehose_assume.json
  tags               = { Component = "05.01" }
}

data "aws_iam_policy_document" "firehose" {
  statement {
    actions   = ["kinesis:DescribeStream", "kinesis:GetShardIterator", "kinesis:GetRecords", "kinesis:ListShards"]
    resources = [aws_kinesis_stream.clicks.arn]
  }
  statement {
    actions   = ["s3:PutObject", "s3:AbortMultipartUpload", "s3:GetBucketLocation", "s3:ListBucket"]
    resources = [aws_s3_bucket.lake.arn, "${aws_s3_bucket.lake.arn}/*"]
  }
  statement {
    actions   = ["kms:Decrypt", "kms:GenerateDataKey"]
    resources = [aws_kms_key.main.arn]
  }
}

resource "aws_iam_role_policy" "firehose" {
  name   = "firehose"
  role   = aws_iam_role.firehose.id
  policy = data.aws_iam_policy_document.firehose.json
}

# ---------------------------------------------------------------- Firehose: stream -> S3

resource "aws_kinesis_firehose_delivery_stream" "clicks_to_s3" {
  name        = "${local.prefix}-clicks-to-s3"
  destination = "extended_s3"

  kinesis_source_configuration {
    kinesis_stream_arn = aws_kinesis_stream.clicks.arn
    role_arn           = aws_iam_role.firehose.arn
  }

  extended_s3_configuration {
    role_arn   = aws_iam_role.firehose.arn
    bucket_arn = aws_s3_bucket.lake.arn

    # Hive-style folders so Athena partition projection (04.01) finds them.
    prefix              = "raw/clicks/dt=!{timestamp:yyyy-MM-dd}/"
    error_output_prefix = "errors/clicks/!{firehose:error-output-type}/dt=!{timestamp:yyyy-MM-dd}/"

    # Flush when 64 MB OR 60 s, whichever first. Bigger/longer = fewer, larger files (better for Athena),
    # but more delivery latency. Small-file problem appears when buffers are tiny.
    buffering_size     = 64
    buffering_interval = 60
    compression_format = "GZIP"
    kms_key_arn        = aws_kms_key.main.arn
  }

  tags = { Component = "05.01" }
}

# ---------------------------------------------------------------- Firehose: direct PUT -> S3

resource "aws_kinesis_firehose_delivery_stream" "events_direct" {
  name        = "${local.prefix}-events"
  destination = "extended_s3"

  server_side_encryption {
    enabled  = true
    key_type = "CUSTOMER_MANAGED_CMK"
    key_arn  = aws_kms_key.main.arn
  }

  extended_s3_configuration {
    role_arn            = aws_iam_role.firehose.arn
    bucket_arn          = aws_s3_bucket.lake.arn
    prefix              = "raw/events/dt=!{timestamp:yyyy-MM-dd}/"
    error_output_prefix = "errors/events/!{firehose:error-output-type}/"
    buffering_size      = 5
    buffering_interval  = 60
    compression_format  = "GZIP"
  }

  tags = { Component = "05.01" }
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
  role   = aws_iam_role.app.id
  policy = data.aws_iam_policy_document.app_kinesis.json
}

output "kinesis_stream" {
  value = aws_kinesis_stream.clicks.name
}

output "firehose_direct" {
  value = aws_kinesis_firehose_delivery_stream.events_direct.name
}
