# 04.02 redshift — Redshift Serverless namespace + workgroup, and the IAM role Redshift uses for COPY/UNLOAD.
# Used by: java/python x04_02_redshift through the Redshift Data API (HTTPS, no JDBC connection pool needed).

resource "aws_security_group" "redshift" {
  name   = "${local.prefix}-redshift"
  vpc_id = aws_vpc.main.id

  ingress {
    description     = "Redshift from the app (JDBC path; the Data API does not need this)"
    from_port       = 5439
    to_port         = 5439
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  tags = { Component = "04.02" }
}

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
  name               = "${local.prefix}-redshift-s3"
  assume_role_policy = data.aws_iam_policy_document.redshift_assume.json
  tags               = { Component = "04.02" }
}

data "aws_iam_policy_document" "redshift_s3" {
  statement {
    actions   = ["s3:GetObject", "s3:PutObject", "s3:ListBucket", "s3:GetBucketLocation"]
    resources = [aws_s3_bucket.lake.arn, "${aws_s3_bucket.lake.arn}/*"]
  }
  statement {
    actions   = ["kms:Decrypt", "kms:GenerateDataKey"]
    resources = [aws_kms_key.main.arn]
  }
}

resource "aws_iam_role_policy" "redshift_s3" {
  name   = "s3-lake"
  role   = aws_iam_role.redshift_s3.id
  policy = data.aws_iam_policy_document.redshift_s3.json
}

resource "aws_redshiftserverless_namespace" "x" {
  namespace_name        = "${local.prefix}-ns"
  db_name               = "xdw"
  admin_username        = "x_admin"
  manage_admin_password = true # password lives in Secrets Manager, rotated by AWS
  kms_key_id            = aws_kms_key.main.arn
  iam_roles             = [aws_iam_role.redshift_s3.arn]
  default_iam_role_arn  = aws_iam_role.redshift_s3.arn # lets SQL say IAM_ROLE default

  tags = { Component = "04.02" }
}

resource "aws_redshiftserverless_workgroup" "x" {
  workgroup_name = "${local.prefix}-dw"
  namespace_name = aws_redshiftserverless_namespace.x.namespace_name

  # RPU = Redshift Processing Unit. Base = capacity the warehouse starts with for each query burst.
  # 8 is the minimum; more RPUs = faster big queries, higher per-second cost (billed only while queries run).
  base_capacity = 8
  max_capacity  = 64 # hard ceiling on scale-up = cost guardrail

  subnet_ids          = aws_subnet.private[*].id
  security_group_ids  = [aws_security_group.redshift.id]
  publicly_accessible = false

  config_parameter {
    parameter_key   = "enable_case_sensitive_identifier"
    parameter_value = "false"
  }

  tags = { Component = "04.02" }
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
  role   = aws_iam_role.app.id
  policy = data.aws_iam_policy_document.app_redshift.json
}

output "redshift_workgroup" {
  value = aws_redshiftserverless_workgroup.x.workgroup_name
}

output "redshift_database" {
  value = aws_redshiftserverless_namespace.x.db_name
}

output "redshift_s3_role_arn" {
  value = aws_iam_role.redshift_s3.arn
}
