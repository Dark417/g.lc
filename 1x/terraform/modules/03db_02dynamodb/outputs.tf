output "orders_table" {
  value = aws_dynamodb_table.orders.name
}

output "orders_stream_arn" {
  value = aws_dynamodb_table.orders.stream_arn
}

output "idempotency_table" {
  value = aws_dynamodb_table.idempotency.name
}
