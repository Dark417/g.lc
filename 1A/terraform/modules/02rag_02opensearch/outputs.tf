output "aoss_collection_endpoint" {
  description = "https://<id>.<region>.aoss.amazonaws.com → A_OPENSEARCH_COLLECTION_ENDPOINT (host part)"
  value       = aws_opensearchserverless_collection.vectors.collection_endpoint
}

output "aoss_collection_arn" {
  value = aws_opensearchserverless_collection.vectors.arn
}

output "aoss_collection_id" {
  value = aws_opensearchserverless_collection.vectors.id
}

output "kb_role_arn" {
  value = aws_iam_role.kb.arn
}

output "kb_role_id" {
  description = "KB service role name; 02rag_04knowledge_bases attaches its permissions policy to it"
  value       = aws_iam_role.kb.id
}

output "data_access_policy_name" {
  description = "AOSS data-access policy; the KB must not be created before it exists (create-time validation)"
  value       = aws_opensearchserverless_access_policy.data.name
}
