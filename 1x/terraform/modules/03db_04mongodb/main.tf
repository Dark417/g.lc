# 03db.04mongodb — Amazon DocumentDB (MongoDB-compatible API) as the AWS store for the MongoDB slice.
# Used by: java _03db_04mongodb, python _03db_04mongodb (X_MONGODB_URI = the cluster endpoint, TLS + CA bundle).
# Local dev runs real MongoDB instead: 1x/local/mongodb/docker-compose.yml (single-node replica set rs0).
# Per-env knobs: instance class, instance count, deletion protection, backup retention, log retention.
#
# DocumentDB is NOT MongoDB: an Aurora-style shared storage layer behind a MongoDB wire-protocol front end.
# Gaps that matter to this slice's code (verify against the DocumentDB "functional differences" page):
#   - No retryable writes        -> URI must carry retryWrites=false; app code owns idempotent retries
#   - Change streams are off      -> enable per collection: db.adminCommand({modifyChangeStreams: 1, ...});
#                                    history kept for change_stream_log_retention_duration (below)
#   - No sharding / mongos        -> scale reads with replicas, writes by instance size (or Elastic Clusters)
#   - Partial aggregation support -> e.g. $setWindowFields, $merge subsets, $dateTrunc: check per version
#   - No tag-set read preference  -> analytics isolation = a dedicated replica + its instance endpoint
#   - Indexes: no wildcard; partial/TTL/text supported with limits; collation not supported
#   - Transactions: 1 minute limit, readConcern "snapshot" only; writes majority-acknowledged by storage

locals {
  component = "03db.04mongodb"
  port      = 27017
}

resource "aws_docdb_subnet_group" "docdb" {
  name       = "${var.prefix}-docdb"
  subnet_ids = var.subnet_ids
  tags       = { Component = local.component }
}

resource "aws_security_group" "docdb" {
  name        = "${var.prefix}-docdb"
  description = "DocumentDB: MongoDB wire protocol from the app only"
  vpc_id      = var.vpc_id
  tags        = { Component = local.component }
}

# Separate rule resource (not an inline block) so other modules can add rules without fighting this one.
resource "aws_vpc_security_group_ingress_rule" "docdb_from_app" {
  security_group_id            = aws_security_group.docdb.id
  description                  = "MongoDB protocol from the app security group"
  ip_protocol                  = "tcp"
  from_port                    = local.port
  to_port                      = local.port
  referenced_security_group_id = var.app_security_group_id
  tags                         = { Component = local.component }
}

# Cluster parameter group: settings shared by every instance.
resource "aws_docdb_cluster_parameter_group" "docdb" {
  name        = "${var.prefix}-docdb5"
  family      = "docdb5.0"
  description = "x DocumentDB 5.0: TLS required, audit + profiler on"

  parameter {
    name  = "tls" # reject plain-text connections; clients need tls=true + the RDS CA bundle
    value = "enabled"
  }

  parameter {
    name  = "audit_logs" # DDL + auth events to CloudWatch (exported below)
    value = "enabled"
  }

  parameter {
    name  = "profiler" # log operations slower than profiler_threshold_ms: the slow-query log
    value = "enabled"
  }

  parameter {
    name  = "profiler_threshold_ms"
    value = "200"
  }

  parameter {
    name  = "change_stream_log_retention_duration" # seconds of change-stream history = the resume window
    value = tostring(var.change_stream_retention_hours * 3600)
  }

  parameter {
    name  = "ttl_monitor" # TTL index deletes (soft-delete purge); disabling stops expiry silently
    value = "enabled"
  }

  tags = { Component = local.component }
}

# Exported logs. Created here (names fixed by DocumentDB) so retention and encryption are ours.
resource "aws_cloudwatch_log_group" "docdb" {
  for_each          = toset(["audit", "profiler"])
  name              = "/aws/docdb/${var.prefix}-docdb/${each.key}"
  retention_in_days = var.log_retention_days
  kms_key_id        = var.kms_key_arn
  tags              = { Component = local.component }
}

resource "aws_docdb_cluster" "docdb" {
  cluster_identifier = "${var.prefix}-docdb"
  engine             = "docdb"
  engine_version     = "5.0.0"
  port               = local.port
  master_username    = "x_admin"

  # AWS creates and rotates the master password in Secrets Manager; it never touches Terraform state or code.
  manage_master_user_password = true

  db_subnet_group_name            = aws_docdb_subnet_group.docdb.name
  vpc_security_group_ids          = [aws_security_group.docdb.id]
  db_cluster_parameter_group_name = aws_docdb_cluster_parameter_group.docdb.name

  storage_encrypted = true
  kms_key_id        = var.kms_key_arn
  storage_type      = var.storage_type # "standard" (pay per I/O) or "iopt1" (I/O-optimized: I/O-heavy, predictable bill)

  backup_retention_period         = var.backup_retention_days # point-in-time restore window (1-35 days)
  preferred_backup_window         = "07:00-08:00"
  preferred_maintenance_window    = "sun:08:30-sun:09:30"
  deletion_protection             = var.deletion_protection
  skip_final_snapshot             = false
  final_snapshot_identifier       = "${var.prefix}-docdb-final"
  enabled_cloudwatch_logs_exports = ["audit", "profiler"]

  tags = { Component = local.component }

  depends_on = [aws_cloudwatch_log_group.docdb] # log groups first, or DocumentDB creates them with no retention
}

# Instance 0 = first failover choice. Storage is 6 copies across 3 AZs regardless of instance count;
# instances are compute only, so 1 instance = no HA compute (failover means replacing the instance).
resource "aws_docdb_cluster_instance" "docdb" {
  count              = var.instance_count
  identifier         = "${var.prefix}-docdb-${count.index}"
  cluster_identifier = aws_docdb_cluster.docdb.id
  instance_class     = var.instance_class
  promotion_tier     = count.index
  ca_cert_identifier = "rds-ca-rsa2048-g1" # matches the RDS global CA bundle the app trusts

  auto_minor_version_upgrade      = true
  enable_performance_insights     = var.performance_insights
  performance_insights_kms_key_id = var.performance_insights ? var.kms_key_arn : null

  tags = { Component = local.component }
}
