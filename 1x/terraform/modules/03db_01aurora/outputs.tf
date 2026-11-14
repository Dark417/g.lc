output "writer_endpoint" {
  value = aws_rds_cluster.aurora.endpoint # always points at the current writer (DNS flips on failover)
}

output "reader_endpoint" {
  value = aws_rds_cluster.aurora.reader_endpoint # round-robin DNS over readers
}

output "master_secret_arn" {
  value = aws_rds_cluster.aurora.master_user_secret[0].secret_arn
}
