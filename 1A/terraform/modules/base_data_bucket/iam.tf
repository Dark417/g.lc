# base_data_bucket IAM — app-role access to the shared bucket.
# The app reads and writes its own prefixes; service roles (KB, BDA, Transcribe, ...) get their own grants
# in their own module's iam.tf.

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
  role   = var.app_role_id
  policy = data.aws_iam_policy_document.app_data.json
}
