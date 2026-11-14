output "app_role_arn" {
  value = aws_iam_role.app.arn
}

output "app_role_id" {
  value = aws_iam_role.app.id # role name; components attach aws_iam_role_policy to it
}
