# 03.01 aurora-postgres — Aurora PostgreSQL cluster: 1 writer + 1 reader, Serverless v2 capacity.
# Used by: java x03_01_aurora, python x03_01_aurora (writer endpoint for writes, reader endpoint for reads).

locals {
  aurora_db_name  = "xdb"
  aurora_app_user = "x_app" # DB user that logs in with an IAM auth token (created by SQL: GRANT rds_iam TO x_app)
}

resource "aws_db_subnet_group" "aurora" {
  name       = "${local.prefix}-aurora"
  subnet_ids = aws_subnet.private[*].id
  tags       = { Component = "03.01" }
}

resource "aws_security_group" "aurora" {
  name   = "${local.prefix}-aurora"
  vpc_id = aws_vpc.main.id

  ingress {
    description     = "Postgres from the app only"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  tags = { Component = "03.01" }
}

# Cluster parameter group: knobs that apply to every instance.
resource "aws_rds_cluster_parameter_group" "aurora" {
  name   = "${local.prefix}-aurora-pg16"
  family = "aurora-postgresql16"

  parameter {
    name  = "log_min_duration_statement" # log queries slower than 500 ms: first stop for slow-query hunts
    value = "500"
  }

  parameter {
    name  = "idle_in_transaction_session_timeout" # kill sessions that hold a txn open > 60 s (lock + vacuum blocker)
    value = "60000"
  }

  parameter {
    name         = "rds.force_ssl" # reject non-TLS connections
    value        = "1"
    apply_method = "pending-reboot"
  }

  tags = { Component = "03.01" }
}

resource "aws_rds_cluster" "aurora" {
  cluster_identifier = "${local.prefix}-aurora"
  engine             = "aurora-postgresql"
  engine_mode        = "provisioned" # required for Serverless v2 instances
  engine_version     = "16.4"
  database_name      = local.aurora_db_name
  master_username    = "x_admin"

  # AWS creates and rotates the master password in Secrets Manager; it never touches Terraform state or code.
  manage_master_user_password   = true
  master_user_secret_kms_key_id = aws_kms_key.main.key_id

  iam_database_authentication_enabled = true # app connects with a 15-min IAM token instead of a password

  db_subnet_group_name            = aws_db_subnet_group.aurora.name
  vpc_security_group_ids          = [aws_security_group.aurora.id]
  db_cluster_parameter_group_name = aws_rds_cluster_parameter_group.aurora.name

  storage_encrypted = true
  kms_key_id        = aws_kms_key.main.arn

  # Storage is 6 copies across 3 AZs regardless of instance count; instances are compute only.
  serverlessv2_scaling_configuration {
    min_capacity = 0.5 # ACUs; 1 ACU ~ 2 GiB RAM. Low floor = cheap idle, but cold-ish buffer cache
    max_capacity = 8   # ceiling caps cost; raise when CPU/ACU utilization sits near max
  }

  backup_retention_period         = 7 # point-in-time restore window (days)
  preferred_backup_window         = "07:00-08:00"
  copy_tags_to_snapshot           = true
  deletion_protection             = true
  skip_final_snapshot             = false
  final_snapshot_identifier       = "${local.prefix}-aurora-final"
  enabled_cloudwatch_logs_exports = ["postgresql"]

  tags = { Component = "03.01" }
}

# Writer + reader. Aurora picks a reader as the new writer on failover (promotion tier decides order).
resource "aws_rds_cluster_instance" "aurora" {
  count              = 2
  identifier         = "${local.prefix}-aurora-${count.index}"
  cluster_identifier = aws_rds_cluster.aurora.id
  engine             = aws_rds_cluster.aurora.engine
  engine_version     = aws_rds_cluster.aurora.engine_version
  instance_class     = "db.serverless"
  promotion_tier     = count.index # 0 = first choice for failover target

  performance_insights_enabled    = true
  performance_insights_kms_key_id = aws_kms_key.main.arn

  tags = { Component = "03.01" }
}

# ---------------------------------------------------------------- app access

data "aws_iam_policy_document" "app_aurora" {
  statement {
    sid       = "IamDbAuth"
    actions   = ["rds-db:connect"]
    resources = ["arn:aws:rds-db:${var.region}:${local.account_id}:dbuser:${aws_rds_cluster.aurora.cluster_resource_id}/${local.aurora_app_user}"]
  }
}

resource "aws_iam_role_policy" "app_aurora" {
  name   = "aurora"
  role   = aws_iam_role.app.id
  policy = data.aws_iam_policy_document.app_aurora.json
}

# ---------------------------------------------------------------- outputs

output "aurora_writer_endpoint" {
  value = aws_rds_cluster.aurora.endpoint # always points at the current writer (DNS flips on failover)
}

output "aurora_reader_endpoint" {
  value = aws_rds_cluster.aurora.reader_endpoint # round-robin DNS over readers
}

output "aurora_master_secret_arn" {
  value = aws_rds_cluster.aurora.master_user_secret[0].secret_arn
}
