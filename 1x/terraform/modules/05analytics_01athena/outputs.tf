output "workgroup" {
  value = aws_athena_workgroup.x.name
}

output "glue_database" {
  value = aws_glue_catalog_database.lake.name
}
