# 03db.03s3 IAM — app-role object + bucket-level access to the lake and Athena results buckets.

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
  role   = var.app_role_id
  policy = data.aws_iam_policy_document.app_s3.json
}
