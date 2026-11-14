output "bootstrap_brokers_iam" {
  value = aws_msk_cluster.x.bootstrap_brokers_sasl_iam
}

output "cluster_arn" {
  value = aws_msk_cluster.x.arn
}
