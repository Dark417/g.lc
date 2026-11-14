output "workgroup" {
  value = aws_redshiftserverless_workgroup.x.workgroup_name
}

output "database" {
  value = aws_redshiftserverless_namespace.x.db_name
}

output "s3_role_arn" {
  value = aws_iam_role.redshift_s3.arn
}
