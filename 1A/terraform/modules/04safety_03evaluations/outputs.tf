output "bedrock_eval_role_arn" {
  value = aws_iam_role.bedrock_eval.arn # A_EVALS_ROLE_ARN
}

output "eval_datasets_s3_uri" {
  value = "s3://${var.data_bucket_name}/${local.eval_dataset_prefix}"
}

output "eval_results_s3_uri" {
  value = "s3://${var.data_bucket_name}/${local.eval_results_prefix}"
}
