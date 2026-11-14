output "endpoint" {
  value = aws_docdb_cluster.docdb.endpoint # always the current primary (DNS flips on failover)
}

output "reader_endpoint" {
  value = aws_docdb_cluster.docdb.reader_endpoint # load-balanced over replicas
}

output "port" {
  value = aws_docdb_cluster.docdb.port
}

output "cluster_identifier" {
  value = aws_docdb_cluster.docdb.cluster_identifier # x-<env>-docdb
}

output "master_secret_arn" {
  value = aws_docdb_cluster.docdb.master_user_secret[0].secret_arn
}

output "security_group_id" {
  value = aws_security_group.docdb.id
}
