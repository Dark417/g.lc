# modules/03data_02glue_data_quality — Glue Data Catalog + Data Quality ruleset, lectures 43-45.
# Creates: catalog database a_<env>_ai_data, table docs_metadata (parquet under s3 glue/docs_metadata/),
#          DQDL ruleset a-<env>-docs-metadata-dq, Glue service role for evaluation runs, app policy (→ iam.tf).
# Used by: python app/{api,service,infra}/_03data_02glue_data_quality (slice "glue_dq").
# Catch: Data Quality runs are Spark jobs billed per DPU-hour; the code caps workers and timeout.

locals {
  glue_dq_ruleset_name = "${var.prefix}-docs-metadata-dq"
  glue_dq_role_name    = "${var.prefix}-glue-dq"
}

resource "aws_glue_catalog_database" "ai_data" {
  name        = "${replace(var.prefix, "-", "_")}_ai_data" # Glue database names: lowercase + underscore
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
    location      = "s3://${var.data_bucket_name}/glue/docs_metadata/"
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

  tags = { Component = "03data_02glue_data_quality" }
}
