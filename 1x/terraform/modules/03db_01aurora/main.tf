# 03db.01aurora — Aurora PostgreSQL cluster: 1 writer + readers, Serverless v2 capacity.
# Used by: java _03db_01aurora, python _03db_01aurora (writer endpoint for writes, reader endpoint for reads).
# Per-env knobs: min/max ACU, instance count, deletion protection, backup + log retention.

locals {
  component       = "03db.01aurora"
  aurora_db_name  = "xdb"
  aurora_app_user = "x_app" # DB user that logs in with an IAM auth token (created by SQL: GRANT rds_iam TO x_app)
}

resource "aws_db_subnet_group" "aurora" {
  name       = "${var.prefix}-aurora"
  subnet_ids = var.subnet_ids
  tags       = { Component = local.component }
}

resource "aws_security_group" "aurora" {
  name   = "${var.prefix}-aurora"
  vpc_id = var.vpc_id

  ingress {
    description     = "Postgres from the app only"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [var.app_security_group_id]
  }

  tags = { Component = local.component }
}

# Cluster parameter group: knobs that apply to every instance.
resource "aws_rds_cluster_parameter_group" "aurora" {
  name   = "${var.prefix}-aurora-pg16"
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

  tags = { Component = local.component }
}

# Exported postgresql log. Created here (name is fixed by RDS) so retention is ours, not "never expire".
resource "aws_cloudwatch_log_group" "aurora" {
  name              = "/aws/rds/cluster/${var.prefix}-aurora/postgresql"
  retention_in_days = var.log_retention_days
  kms_key_id        = var.kms_key_arn
  tags              = { Component = local.component }
}

resource "aws_rds_cluster" "aurora" {
  cluster_identifier = "${var.prefix}-aurora"
  engine             = "aurora-postgresql"
  engine_mode        = "provisioned" # required for Serverless v2 instances
  engine_version     = "16.4"
  database_name      = local.aurora_db_name
  master_username    = "x_admin"

  # AWS creates and rotates the master password in Secrets Manager; it never touches Terraform state or code.
  manage_master_user_password   = true
  master_user_secret_kms_key_id = var.kms_key_id

  iam_database_authentication_enabled = true # app connects with a 15-min IAM token instead of a password

  db_subnet_group_name            = aws_db_subnet_group.aurora.name
  vpc_security_group_ids          = [aws_security_group.aurora.id]
  db_cluster_parameter_group_name = aws_rds_cluster_parameter_group.aurora.name

  storage_encrypted = true
  kms_key_id        = var.kms_key_arn

  # Storage is 6 copies across 3 AZs regardless of instance count; instances are compute only.
  serverlessv2_scaling_configuration {
    min_capacity = var.min_acu # ACUs; 1 ACU ~ 2 GiB RAM. Low floor = cheap idle, but cold-ish buffer cache
    max_capacity = var.max_acu # ceiling caps cost; raise when CPU/ACU utilization sits near max
  }

  backup_retention_period         = var.backup_retention_days # point-in-time restore window (days)
  preferred_backup_window         = "07:00-08:00"
  copy_tags_to_snapshot           = true
  deletion_protection             = var.deletion_protection
  skip_final_snapshot             = false
  final_snapshot_identifier       = "${var.prefix}-aurora-final"
  enabled_cloudwatch_logs_exports = ["postgresql"]

  tags = { Component = local.component }

  depends_on = [aws_cloudwatch_log_group.aurora] # log group first, or RDS creates it with no retention
}

# Writer + reader(s). Aurora picks a reader as the new writer on failover (promotion tier decides order).
resource "aws_rds_cluster_instance" "aurora" {
  count              = var.instance_count
  identifier         = "${var.prefix}-aurora-${count.index}"
  cluster_identifier = aws_rds_cluster.aurora.id
  engine             = aws_rds_cluster.aurora.engine
  engine_version     = aws_rds_cluster.aurora.engine_version
  instance_class     = "db.serverless"
  promotion_tier     = count.index # 0 = first choice for failover target

  performance_insights_enabled    = true
  performance_insights_kms_key_id = var.kms_key_arn

  tags = { Component = local.component }
}
