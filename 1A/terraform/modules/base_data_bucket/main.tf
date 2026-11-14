# modules/base_data_bucket — one S3 bucket shared by every 1A component, one prefix per component.
# Shared by 2+ components, so it lives in the foundation (terraform/AGENTS.md §3).
#
# Prefix layout (the Python / Java config uses these exact prefixes):
#   kb-docs/          02rag_04knowledge_bases source documents (+ <file>.metadata.json sidecars)
#   customization/    01bedrock_02customization fine-tuning train/validation JSONL + job output
#   bda/input|output  03data_01data_automation Bedrock Data Automation
#   glue/             03data_02glue_data_quality sample table
#   transcribe/       03data_03transcribe audio in, transcripts out
#   comprehend/       03data_04comprehend / 04safety_02pii_redaction async PII jobs in/out
#   evals/            04safety_03evaluations datasets + results
#   invocation-logs/  05ops_01observability Bedrock model invocation logs (large payloads)

resource "aws_s3_bucket" "data" {
  bucket = "${var.prefix}-ai-data-${var.account_id}" # bucket names are global: suffix with the account
  tags   = { Component = "base_data_bucket" }
}

resource "aws_s3_bucket_public_access_block" "data" {
  bucket                  = aws_s3_bucket.data.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "data" {
  bucket = aws_s3_bucket.data.id
  rule {
    object_ownership = "BucketOwnerEnforced" # ACLs off; access is IAM / bucket policy only
  }
}

resource "aws_s3_bucket_versioning" "data" {
  bucket = aws_s3_bucket.data.id
  versioning_configuration {
    status = "Enabled" # protects source docs against overwrite; old versions cost storage
  }
}

# Versioning keeps every overwrite forever unless a lifecycle rule expires old versions.
# Per env: short in local/dev (cheap), long in prod (undo window for source docs).
resource "aws_s3_bucket_lifecycle_configuration" "data" {
  bucket = aws_s3_bucket.data.id

  rule {
    id     = "expire-noncurrent-versions"
    status = "Enabled"
    filter {} # whole bucket

    noncurrent_version_expiration {
      noncurrent_days = var.noncurrent_version_days
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 7 # orphaned multipart parts are billed but invisible
    }
  }

  depends_on = [aws_s3_bucket_versioning.data]
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data" {
  bucket = aws_s3_bucket.data.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = var.kms_key_arn
    }
    bucket_key_enabled = true # one data key per bucket-period instead of per object: far fewer KMS calls
  }
}
