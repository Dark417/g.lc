# 03.02 glue-data-quality — Glue Data Catalog + Data Quality ruleset, lectures 43-45.
# Creates: catalog database a_ai_data, table docs_metadata (parquet under s3 glue/docs_metadata/),
#          DQDL ruleset a-docs-metadata-dq, Glue service role for evaluation runs, app policy.
# Used by: python app/a03_02_glue_data_quality (slice "glue_dq").
# Catch: Data Quality runs are Spark jobs billed per DPU-hour; the code caps workers and timeout.

locals {
  glue_dq_ruleset_name = "${local.prefix}-docs-metadata-dq"
  glue_dq_role_name    = "${local.prefix}-glue-dq"
}

resource "aws_glue_catalog_database" "ai_data" {
  name        = "${replace(local.prefix, "-", "_")}_ai_data" # Glue database names: lowercase + underscore
  description = "Corpus metadata tables checked by Glue Data Quality"
}

resource "aws_glue_catalog_table" "docs_metadata" {
  name          = "docs_metadata"
  database_name = aws_glue_catalog_database.ai_data.name
  table_type    = "EXTERNAL_TABLE"
  parameters = {
    classification = "parquet"
    EXTERNAL       = "TRUE"
  }

  storage_descriptor {
    location      = "s3://${aws_s3_bucket.data.bucket}/glue/docs_metadata/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"

    ser_de_info {
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns {
      name = "doc_id"
      type = "string"
    }
    columns {
      name = "title"
      type = "string"
    }
    columns {
      name = "source"
      type = "string"
    }
    columns {
      name = "language"
      type = "string"
    }
    columns {
      name = "char_count"
      type = "int"
    }
    columns {
      name = "created_at"
      type = "timestamp"
    }
  }
}

# DQDL = Data Quality Definition Language. Thresholds trade false alarms against missed defects.
resource "aws_glue_data_quality_ruleset" "docs_metadata" {
  name        = local.glue_dq_ruleset_name
  description = "Corpus metadata must be unique, complete and sane before embedding"
  ruleset     = <<-DQDL
    Rules = [
      RowCount > 0,
      IsComplete "doc_id",
      IsUnique "doc_id",
      Completeness "title" > 0.95,
      ColumnValues "language" in ["en", "de", "fr"],
      ColumnValues "char_count" between 1 and 1000000,
      CustomSql "select count(*) from primary where source is null or trim(source) = ''" = 0
    ]
  DQDL

  target_table {
    database_name = aws_glue_catalog_database.ai_data.name
    table_name    = aws_glue_catalog_table.docs_metadata.name
  }

  tags = { Component = "03.02" }
}

# ---------------------------------------------------------------- service role for evaluation runs

data "aws_iam_policy_document" "glue_dq_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["glue.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "glue_dq" {
  name               = local.glue_dq_role_name
  assume_role_policy = data.aws_iam_policy_document.glue_dq_assume.json
  tags               = { Component = "03.02" }
}

data "aws_iam_policy_document" "glue_dq_run" {
  statement {
    sid       = "ReadData"
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.data.arn}/glue/*"]
  }
  statement {
    sid       = "ListData"
    actions   = ["s3:ListBucket"]
    resources = [aws_s3_bucket.data.arn]
    condition {
      test     = "StringLike"
      variable = "s3:prefix"
      values   = ["glue/*"]
    }
  }
  statement {
    sid       = "ResultsWrite" # ResultsS3Prefix output of a run
    actions   = ["s3:PutObject"]
    resources = ["${aws_s3_bucket.data.arn}/glue/dq-results/*"]
  }
  statement {
    sid       = "Kms"
    actions   = ["kms:Decrypt", "kms:GenerateDataKey"]
    resources = [aws_kms_key.main.arn]
  }
  statement {
    sid = "Catalog"
    actions = [
      "glue:GetDatabase", "glue:GetTable", "glue:GetTables", "glue:GetPartitions",
      "glue:GetDataQualityRuleset", "glue:PublishDataQualityResult"
    ]
    resources = ["*"] # catalog ARNs need account + region + names; tighten per database in production
  }
  statement {
    sid       = "Logs"
    actions   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["arn:aws:logs:${var.region}:${local.account_id}:log-group:/aws-glue/*"]
  }
  statement {
    sid       = "Metrics"
    actions   = ["cloudwatch:PutMetricData"]
    resources = ["*"] # PutMetricData has no resource ARN; Glue publishes its own namespace - verify and add a namespace condition
  }
}

resource "aws_iam_role_policy" "glue_dq_run" {
  name   = "dq-run"
  role   = aws_iam_role.glue_dq.id
  policy = data.aws_iam_policy_document.glue_dq_run.json
}

# ---------------------------------------------------------------- app policy (least privilege)

data "aws_iam_policy_document" "app_glue_dq" {
  statement {
    sid = "Runs"
    actions = [
      "glue:StartDataQualityRulesetEvaluationRun", "glue:GetDataQualityRulesetEvaluationRun",
      "glue:GetDataQualityResult", "glue:BatchGetDataQualityResult", "glue:ListDataQualityResults",
      "glue:StartDataQualityRuleRecommendationRun", "glue:GetDataQualityRuleRecommendationRun"
    ]
    resources = ["*"] # run ids are not known up front
  }
  statement {
    sid       = "Rulesets"
    actions   = ["glue:GetDataQualityRuleset", "glue:CreateDataQualityRuleset", "glue:UpdateDataQualityRuleset"]
    resources = ["arn:aws:glue:${var.region}:${local.account_id}:dataQualityRuleset/*"]
  }
  statement {
    sid       = "Catalog" # runs and ruleset creation validate against the table
    actions   = ["glue:GetDatabase", "glue:GetTable", "glue:GetPartitions"]
    resources = ["*"]
  }
  statement {
    sid       = "PassRole" # starting a run hands the role to Glue
    actions   = ["iam:PassRole"]
    resources = [aws_iam_role.glue_dq.arn]
    condition {
      test     = "StringEquals"
      variable = "iam:PassedToService"
      values   = ["glue.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy" "app_glue_dq" {
  name   = "glue-dq"
  role   = aws_iam_role.app.id
  policy = data.aws_iam_policy_document.app_glue_dq.json
}

output "glue_database" {
  value = aws_glue_catalog_database.ai_data.name
}

output "glue_dq_ruleset_name" {
  value = aws_glue_data_quality_ruleset.docs_metadata.name
}

output "glue_dq_role_arn" {
  value = aws_iam_role.glue_dq.arn
}
