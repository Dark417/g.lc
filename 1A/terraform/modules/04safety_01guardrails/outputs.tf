output "guardrail_id" {
  value = aws_bedrock_guardrail.main.guardrail_id # A_GUARDRAILS_GUARDRAIL_ID / a.guardrails.guardrail-id
}

output "guardrail_arn" {
  value = aws_bedrock_guardrail.main.guardrail_arn
}

output "guardrail_version" {
  value = aws_bedrock_guardrail_version.v1.version # "1"; A_GUARDRAILS_GUARDRAIL_VERSION
}

output "guardrail_name" {
  value = aws_bedrock_guardrail.main.name
}
