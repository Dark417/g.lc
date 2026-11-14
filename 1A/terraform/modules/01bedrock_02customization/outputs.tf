output "customization_role_arn" {
  description = "A_CUSTOMIZATION_ROLE_ARN"
  value       = aws_iam_role.customization.arn
}

output "customization_s3_prefix" {
  description = "A_CUSTOMIZATION_S3_PREFIX"
  value       = "s3://${var.data_bucket_name}/${local.customization_prefix}/"
}
