# 03db.03s3 — data-lake bucket (raw/curated zones) + Athena results bucket.
# Used by: java/python _03db_03s3 (object ops), _02messaging_01kinesis (Firehose lands here),
# _05analytics_01athena (queries it), _05analytics_02redshift (COPY / UNLOAD).
# Per-env knobs: lifecycle days (raw tiering, noncurrent expiry, results expiry).

locals {
  component = "03db.03s3"
}

resource "aws_s3_bucket" "lake" {
  bucket = "${var.prefix}-lake-${var.account_id}" # bucket names are global: suffix with the account
  tags   = { Component = local.component }
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
      kms_master_key_id = var.kms_key_arn
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
      days          = var.raw_ia_days
      storage_class = "STANDARD_IA" # cheaper storage, per-GB retrieval fee; min 30-day charge
    }
    transition {
      days          = var.raw_glacier_days
      storage_class = "GLACIER_IR"
    }
    noncurrent_version_expiration {
      noncurrent_days = var.noncurrent_expiration_days
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

# Separate bucket for Athena query results: different lifecycle (delete after a few days).
resource "aws_s3_bucket" "athena_results" {
  bucket = "${var.prefix}-athena-results-${var.account_id}"
  tags   = { Component = local.component }
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
      days = var.athena_results_expiration_days
    }
  }
}
