# 00.05 data-bucket — one S3 bucket shared by every 1A component, one prefix per component.
# Shared by 2+ components, so it lives in the foundation (terraform/AGENTS.md §3).
#
# Prefix layout (the Python / Java config uses these exact prefixes):
#   kb-docs/          02.04 knowledge-base source documents (+ <file>.metadata.json sidecars)
#   customization/    01.02 fine-tuning train/validation JSONL + job output
#   bda/input|output  03.01 Bedrock Data Automation
#   glue/             03.02 Glue Data Quality sample table
#   transcribe/       03.03 audio in, transcripts out
#   comprehend/       03.04 async PII jobs in/out
#   evals/            04.03 evaluation datasets + results
#   invocation-logs/  05.01 Bedrock model invocation logs (large payloads)

resource "aws_s3_bucket" "data" {
  bucket = "${local.prefix}-ai-data-${local.account_id}" # bucket names are global: suffix with the account
  tags   = { Component = "00.05" }
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

resource "aws_s3_bucket_server_side_encryption_configuration" "data" {
  bucket = aws_s3_bucket.data.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.main.arn
    }
    bucket_key_enabled = true # one data key per bucket-period instead of per object: far fewer KMS calls
  }
}

# The app reads and writes its own prefixes; service roles (KB, BDA, Transcribe, ...) get their own grants.
data "aws_iam_policy_document" "app_data" {
  statement {
    actions   = ["s3:ListBucket"]
    resources = [aws_s3_bucket.data.arn]
  }
  statement {
    actions   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
    resources = ["${aws_s3_bucket.data.arn}/*"]
  }
}

resource "aws_iam_role_policy" "app_data" {
  name   = "data-bucket"
  role   = aws_iam_role.app.id
  policy = data.aws_iam_policy_document.app_data.json
}

output "data_bucket" {
  value = aws_s3_bucket.data.bucket
}
