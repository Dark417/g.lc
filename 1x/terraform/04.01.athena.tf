# 04.01 athena — Glue Data Catalog table over the lake + an Athena workgroup with cost guardrails.
# Used by: java/python x04_01_athena. Data arrives from Firehose (05.01) under s3://<lake>/raw/clicks/dt=YYYY-MM-DD/.

resource "aws_glue_catalog_database" "lake" {
  name = "${local.prefix}_lake" # Glue names: lowercase + underscores
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
    "storage.location.template"   = "s3://${aws_s3_bucket.lake.bucket}/raw/clicks/dt=$${dt}/"
  }

  partition_keys {
    name = "dt"
    type = "string"
  }

  storage_descriptor {
    location      = "s3://${aws_s3_bucket.lake.bucket}/raw/clicks/"
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
  name          = "${local.prefix}-wg"
  force_destroy = false

  configuration {
    enforce_workgroup_configuration    = true # clients can't override result location / encryption
    publish_cloudwatch_metrics_enabled = true
    bytes_scanned_cutoff_per_query     = 10737418240 # 10 GiB: kill runaway full scans (Athena bills per TB scanned)

    engine_version {
      selected_engine_version = "Athena engine version 3" # Trino-based
    }

    result_configuration {
      output_location = "s3://${aws_s3_bucket.athena_results.bucket}/results/"
      encryption_configuration {
        encryption_option = "SSE_KMS"
        kms_key_arn       = aws_kms_key.main.arn
      }
    }
  }

  tags = { Component = "04.01" }
}

# ---------------------------------------------------------------- app access

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
      "arn:aws:glue:${var.region}:${local.account_id}:catalog",
      "arn:aws:glue:${var.region}:${local.account_id}:database/${aws_glue_catalog_database.lake.name}",
      "arn:aws:glue:${var.region}:${local.account_id}:table/${aws_glue_catalog_database.lake.name}/*",
    ]
  }
}

resource "aws_iam_role_policy" "app_athena" {
  name   = "athena"
  role   = aws_iam_role.app.id
  policy = data.aws_iam_policy_document.app_athena.json
}

output "athena_workgroup" {
  value = aws_athena_workgroup.x.name
}

output "glue_database" {
  value = aws_glue_catalog_database.lake.name
}
