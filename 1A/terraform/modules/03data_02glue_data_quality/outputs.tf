output "glue_database" {
  value = aws_glue_catalog_database.ai_data.name
}

output "glue_dq_ruleset_name" {
  value = aws_glue_data_quality_ruleset.docs_metadata.name
}

output "glue_dq_role_arn" {
  value = aws_iam_role.glue_dq.arn
}
