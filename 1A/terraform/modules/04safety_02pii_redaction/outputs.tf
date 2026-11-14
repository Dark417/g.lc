output "comprehend_pii_role_arn" {
  value = aws_iam_role.comprehend_pii.arn # A_PII_DATA_ACCESS_ROLE_ARN
}

output "pii_input_s3_uri" {
  value = "s3://${var.data_bucket_name}/${local.pii_input_prefix}"
}

output "pii_output_s3_uri" {
  value = "s3://${var.data_bucket_name}/${local.pii_output_prefix}"
}
