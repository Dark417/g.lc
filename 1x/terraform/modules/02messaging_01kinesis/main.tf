# 02messaging.01kinesis — Kinesis Data Stream "x-<env>-clicks" + Firehose that lands it in S3 (raw/clicks/dt=.../),
# plus a direct-PUT Firehose "x-<env>-events" for producers that skip the stream.
# Used by: java/python _02messaging_01kinesis. Downstream: Athena table clicks (05analytics_01athena).
# Lake bucket comes in from 03db_03s3. Per-env knobs: stream mode, shard count, retention hours.

locals {
  component = "02messaging.01kinesis"
}

resource "aws_kinesis_stream" "clicks" {
  name             = "${var.prefix}-clicks"
  retention_period = var.retention_hours # hours (24 default, up to 8760): replay window for consumers that fall behind

  # ON_DEMAND: AWS adds/removes shards from traffic. PROVISIONED: you pick shards
  # (each shard = 1 MB/s or 1,000 records/s in, 2 MB/s out; AWS Kinesis quotas page, 2026).
  shard_count = var.stream_mode == "PROVISIONED" ? var.shard_count : null
  stream_mode_details {
    stream_mode = var.stream_mode
  }

  encryption_type = "KMS"
  kms_key_id      = var.kms_key_arn

  shard_level_metrics = ["IncomingBytes", "WriteProvisionedThroughputExceeded", "IteratorAgeMilliseconds"]

  tags = { Component = local.component }
}

# ---------------------------------------------------------------- Firehose: stream -> S3

resource "aws_kinesis_firehose_delivery_stream" "clicks_to_s3" {
  name        = "${var.prefix}-clicks-to-s3"
  destination = "extended_s3"

  kinesis_source_configuration {
    kinesis_stream_arn = aws_kinesis_stream.clicks.arn
    role_arn           = aws_iam_role.firehose.arn
  }

  extended_s3_configuration {
    role_arn   = aws_iam_role.firehose.arn
    bucket_arn = var.lake_bucket_arn

    # Hive-style folders so Athena partition projection (05analytics_01athena) finds them.
    prefix              = "raw/clicks/dt=!{timestamp:yyyy-MM-dd}/"
    error_output_prefix = "errors/clicks/!{firehose:error-output-type}/dt=!{timestamp:yyyy-MM-dd}/"

    # Flush when 64 MB OR 60 s, whichever first. Bigger/longer = fewer, larger files (better for Athena),
    # but more delivery latency. Small-file problem appears when buffers are tiny.
    buffering_size     = 64
    buffering_interval = 60
    compression_format = "GZIP"
    kms_key_arn        = var.kms_key_arn
  }

  tags = { Component = local.component }
}

# ---------------------------------------------------------------- Firehose: direct PUT -> S3

resource "aws_kinesis_firehose_delivery_stream" "events_direct" {
  name        = "${var.prefix}-events"
  destination = "extended_s3"

  server_side_encryption {
    enabled  = true
    key_type = "CUSTOMER_MANAGED_CMK"
    key_arn  = var.kms_key_arn
  }

  extended_s3_configuration {
    role_arn            = aws_iam_role.firehose.arn
    bucket_arn          = var.lake_bucket_arn
    prefix              = "raw/events/dt=!{timestamp:yyyy-MM-dd}/"
    error_output_prefix = "errors/events/!{firehose:error-output-type}/"
    buffering_size      = 5
    buffering_interval  = 60
    compression_format  = "GZIP"
  }

  tags = { Component = local.component }
}
