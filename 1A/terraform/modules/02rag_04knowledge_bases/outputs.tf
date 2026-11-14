output "kb_id" {
  description = "A_KB_KNOWLEDGE_BASE_ID"
  value       = aws_bedrockagent_knowledge_base.main.id
}

output "kb_arn" {
  value = aws_bedrockagent_knowledge_base.main.arn
}

output "kb_data_source_id" {
  description = "A_KB_DATA_SOURCE_ID"
  value       = aws_bedrockagent_data_source.s3.data_source_id
}
