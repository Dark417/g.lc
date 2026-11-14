output "converse_app_profile_arn" {
  description = "modelId for cost-tagged calls (A_CONVERSE_APP_PROFILE_ARN)"
  value       = aws_bedrock_inference_profile.app.arn
}

output "converse_system_profile_ids" {
  description = "Cross-Region inference profile IDs the app may call (A_TEXT_MODEL_ID / A_FAST_MODEL_ID)"
  value       = [for id in var.converse_model_ids : "${var.converse_profile_prefix}.${id}"]
}
