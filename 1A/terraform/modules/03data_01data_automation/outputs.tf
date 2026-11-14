output "bda_project_arn" {
  value = aws_bedrockdataautomation_project.docs.arn
}

output "bda_blueprint_arn" {
  value = aws_bedrockdataautomation_blueprint.invoice.arn
}
