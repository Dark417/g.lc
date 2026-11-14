output "prompt_id" {
  description = "A_PROMPTS_PROMPT_ID"
  value       = aws_bedrockagent_prompt.main.id
}

output "prompt_arn" {
  description = "Base ARN (DRAFT). Production config pins <prompt_arn>:<version> after CreatePromptVersion."
  value       = aws_bedrockagent_prompt.main.arn
}
