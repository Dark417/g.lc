output "vpc_id" {
  value = aws_vpc.main.id
}

output "private_subnet_ids" {
  value = aws_subnet.private[*].id
}

output "app_security_group_id" {
  description = "SG the app carries; data-store SGs allow it by reference"
  value       = aws_security_group.app.id
}

output "endpoints_security_group_id" {
  description = "SG for interface endpoints (443 from the app); reused by the 02rag_02opensearch VPC endpoint"
  value       = aws_security_group.endpoints.id
}
