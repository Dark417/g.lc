# 03.03 s3 — data-lake bucket (raw/curated zones) + Athena results bucket.
# Used by: java/python x03_03_s3 (object ops), x05_01_kinesis (Firehose lands here), x04_01_athena (queries it),
# x04_02_redshift (COPY / UNLOAD).

resource "aws_s3_bucket" "lake" {
  bucket = "${local.prefix}-lake-${local.account_id}" # bucket names are global: suffix with the account
  tags   = { Component = "03.03" }
}

resource "aws_s3_bucket_public_access_block" "lake" {
  bucket                  = aws_s3_bucket.lake.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_ownership_controls" "lake" {
  bucket = aws_s3_bucket.lake.id
  rule {
    object_ownership = "BucketOwnerEnforced" # ACLs off; access is IAM/bucket policy only
  }
}

resource "aws_s3_bucket_versioning" "lake" {
  bucket = aws_s3_bucket.lake.id
  versioning_configuration {
    status = "Enabled" # protects against overwrite/delete; costs storage for old versions
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "lake" {
  bucket = aws_s3_bucket.lake.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.main.arn
    }
    bucket_key_enabled = true # one data key per bucket-period -> far fewer KMS calls (cost)
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "lake" {
  bucket = aws_s3_bucket.lake.id

  rule {
    id     = "raw-tiering"
    status = "Enabled"
    filter {
      prefix = "raw/"
    }
    transition {
      days          = 30
      storage_class = "STANDARD_IA" # cheaper storage, per-GB retrieval fee; min 30-day charge
    }
    transition {
      days          = 180
      storage_class = "GLACIER_IR"
    }
    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }

  rule {
    id     = "abort-incomplete-multipart"
    status = "Enabled"
    filter {}
    abort_incomplete_multipart_upload {
      days_after_initiation = 7 # orphaned parts are billed until aborted
    }
  }
}

# Separate bucket for Athena query results: different lifecycle (delete after 7 days).
resource "aws_s3_bucket" "athena_results" {
  bucket = "${local.prefix}-athena-results-${local.account_id}"
  tags   = { Component = "03.03" }
}

resource "aws_s3_bucket_public_access_block" "athena_results" {
  bucket                  = aws_s3_bucket.athena_results.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "athena_results" {
  bucket = aws_s3_bucket.athena_results.id
  rule {
    id     = "expire-results"
    status = "Enabled"
    filter {}
    expiration {
      days = 7
    }
  }
}

# ---------------------------------------------------------------- app access

data "aws_iam_policy_document" "app_s3" {
  statement {
    actions   = ["s3:GetObject", "s3:GetObjectVersion", "s3:PutObject", "s3:DeleteObject", "s3:AbortMultipartUpload", "s3:ListMultipartUploadParts"]
    resources = ["${aws_s3_bucket.lake.arn}/*", "${aws_s3_bucket.athena_results.arn}/*"]
  }
  statement {
    actions   = ["s3:ListBucket", "s3:ListBucketVersions", "s3:GetBucketLocation", "s3:ListBucketMultipartUploads"]
    resources = [aws_s3_bucket.lake.arn, aws_s3_bucket.athena_results.arn]
  }
}

resource "aws_iam_role_policy" "app_s3" {
  name   = "s3"
  role   = aws_iam_role.app.id
  policy = data.aws_iam_policy_document.app_s3.json
}

output "lake_bucket" {
  value = aws_s3_bucket.lake.bucket
}

output "athena_results_bucket" {
  value = aws_s3_bucket.athena_results.bucket
}
