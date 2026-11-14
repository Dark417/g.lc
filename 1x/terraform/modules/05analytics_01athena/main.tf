# 05analytics.01athena — Glue Data Catalog table over the lake + an Athena workgroup with cost guardrails.
# Used by: java/python _05analytics_01athena. Data arrives from Firehose (02messaging_01kinesis) under
# s3://<lake>/raw/clicks/dt=YYYY-MM-DD/. Lake + results buckets come in from 03db_03s3.
# Per-env knob: bytes scanned cutoff per query.

locals {
  component = "05analytics.01athena"
  glue_name = replace(var.prefix, "-", "_") # x-dev -> x_dev
}

resource "aws_glue_catalog_database" "lake" {
  name = "${local.glue_name}_lake" # Glue names: lowercase + underscores
}

# External table: Athena reads files in place; dropping the table never deletes data.
resource "aws_glue_catalog_table" "clicks" {
  name          = "clicks"
  database_name = aws_glue_catalog_database.lake.name
  table_type    = "EXTERNAL_TABLE"

  # Partition projection: Athena computes partition paths from these rules instead of asking the catalog.
  # No MSCK REPAIR / crawler needed when new dt= folders appear; partition pruning still works.
  parameters = {
    "classification"              = "json"
    "projection.enabled"          = "true"
    "projection.dt.type"          = "date"
    "projection.dt.format"        = "yyyy-MM-dd"
    "projection.dt.range"         = "2026-01-01,NOW"
    "projection.dt.interval"      = "1"
    "projection.dt.interval.unit" = "DAYS"
    "storage.location.template"   = "s3://${var.lake_bucket}/raw/clicks/dt=$${dt}/"
  }

  partition_keys {
    name = "dt"
    type = "string"
  }

  storage_descriptor {
    location      = "s3://${var.lake_bucket}/raw/clicks/"
    input_format  = "org.apache.hadoop.mapred.TextInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat"

    ser_de_info {
      serialization_library = "org.openx.data.jsonserde.JsonSerDe"
    }

    columns {
      name = "click_id"
      type = "string"
    }
    columns {
      name = "ad_id"
      type = "string"
    }
    columns {
      name = "user_id"
      type = "string"
    }
    columns {
      name = "ts"
      type = "bigint" # epoch millis
    }
    columns {
      name = "country"
      type = "string"
    }
  }
}

resource "aws_athena_workgroup" "x" {
  name          = "${var.prefix}-wg"
  force_destroy = false

  configuration {
    enforce_workgroup_configuration    = true # clients can't override result location / encryption
    publish_cloudwatch_metrics_enabled = true
    bytes_scanned_cutoff_per_query     = var.bytes_scanned_cutoff # 10 GiB default: kill runaway full scans (Athena bills per TB scanned)

    engine_version {
      selected_engine_version = "Athena engine version 3" # Trino-based
    }

    result_configuration {
      output_location = "s3://${var.athena_results_bucket}/results/"
      encryption_configuration {
        encryption_option = "SSE_KMS"
        kms_key_arn       = var.kms_key_arn
      }
    }
  }

  tags = { Component = local.component }
}
