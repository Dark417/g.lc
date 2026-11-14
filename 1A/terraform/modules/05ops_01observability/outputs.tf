output "invocation_log_group" {
  value = aws_cloudwatch_log_group.invocations.name
}

output "obs_metric_namespace" {
  value = local.obs_namespace
}
