output "flow_id" {
  description = "A_FLOWS_FLOW_ID"
  value       = aws_bedrockagent_flow.main.id
}

output "flow_arn" {
  value = aws_bedrockagent_flow.main.arn
}

output "flow_role_arn" {
  description = "A_FLOWS_EXECUTION_ROLE_ARN (CreateFlow from Python)"
  value       = aws_iam_role.flow.arn
}
