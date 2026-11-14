# 05analytics.02redshift IAM — the service role Redshift assumes for COPY/UNLOAD, and app-role Data API access.

# ---------------------------------------------------------------- Redshift service role

# Role that the Redshift service assumes to read/write S3 during COPY and UNLOAD.
data "aws_iam_policy_document" "redshift_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["redshift.amazonaws.com", "redshift-serverless.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "redshift_s3" {
  name               = "${var.prefix}-redshift-s3"
  assume_role_policy = data.aws_iam_policy_document.redshift_assume.json
  tags               = { Component = local.component }
}

data "aws_iam_policy_document" "redshift_s3" {
  statement {
    actions   = ["s3:GetObject", "s3:PutObject", "s3:ListBucket", "s3:GetBucketLocation"]
    resources = [var.lake_bucket_arn, "${var.lake_bucket_arn}/*"]
  }
  statement {
    actions   = ["kms:Decrypt", "kms:GenerateDataKey"]
    resources = [var.kms_key_arn]
  }
}

resource "aws_iam_role_policy" "redshift_s3" {
  name   = "s3-lake"
  role   = aws_iam_role.redshift_s3.id
  policy = data.aws_iam_policy_document.redshift_s3.json
}

# ---------------------------------------------------------------- app access

data "aws_iam_policy_document" "app_redshift" {
  statement {
    sid = "DataApi"
    actions = [
      "redshift-data:ExecuteStatement", "redshift-data:BatchExecuteStatement",
      "redshift-data:DescribeStatement", "redshift-data:GetStatementResult",
      "redshift-data:CancelStatement", "redshift-data:ListStatements",
    ]
    resources = ["*"] # Data API statement ARNs are created per call; scope by workgroup below
  }
  statement {
    sid       = "TempCreds"
    actions   = ["redshift-serverless:GetCredentials"]
    resources = [aws_redshiftserverless_workgroup.x.arn]
  }
}

resource "aws_iam_role_policy" "app_redshift" {
  name   = "redshift"
  role   = var.app_role_id
  policy = data.aws_iam_policy_document.app_redshift.json
}
