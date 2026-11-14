output "app_role_arn" {
  value = aws_iam_role.app.arn
}

output "app_role_id" {
  description = "Role name/id; component modules attach aws_iam_role_policy to it"
  value       = aws_iam_role.app.id
}
