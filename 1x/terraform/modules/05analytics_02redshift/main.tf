# 05analytics.02redshift — Redshift Serverless namespace + workgroup, and the IAM role Redshift uses for COPY/UNLOAD.
# Used by: java/python _05analytics_02redshift through the Redshift Data API (HTTPS, no JDBC connection pool needed).
# Per-env knobs: base / max RPU. The COPY/UNLOAD role lives in iam.tf.

locals {
  component = "05analytics.02redshift"
}

resource "aws_security_group" "redshift" {
  name   = "${var.prefix}-redshift"
  vpc_id = var.vpc_id

  ingress {
    description     = "Redshift from the app (JDBC path; the Data API does not need this)"
    from_port       = 5439
    to_port         = 5439
    protocol        = "tcp"
    security_groups = [var.app_security_group_id]
  }

  tags = { Component = local.component }
}

resource "aws_redshiftserverless_namespace" "x" {
  namespace_name        = "${var.prefix}-ns"
  db_name               = "xdw"
  admin_username        = "x_admin"
  manage_admin_password = true # password lives in Secrets Manager, rotated by AWS
  kms_key_id            = var.kms_key_arn
  iam_roles             = [aws_iam_role.redshift_s3.arn]
  default_iam_role_arn  = aws_iam_role.redshift_s3.arn # lets SQL say IAM_ROLE default

  tags = { Component = local.component }
}

resource "aws_redshiftserverless_workgroup" "x" {
  workgroup_name = "${var.prefix}-dw"
  namespace_name = aws_redshiftserverless_namespace.x.namespace_name

  # RPU = Redshift Processing Unit. Base = capacity the warehouse starts with for each query burst.
  # 8 is the minimum; more RPUs = faster big queries, higher per-second cost (billed only while queries run).
  base_capacity = var.base_rpu
  max_capacity  = var.max_rpu # hard ceiling on scale-up = cost guardrail

  subnet_ids          = var.subnet_ids
  security_group_ids  = [aws_security_group.redshift.id]
  publicly_accessible = false

  config_parameter {
    parameter_key   = "enable_case_sensitive_identifier"
    parameter_value = "false"
  }

  tags = { Component = local.component }
}
