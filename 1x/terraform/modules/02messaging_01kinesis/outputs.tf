output "stream" {
  value = aws_kinesis_stream.clicks.name
}

output "stream_arn" {
  value = aws_kinesis_stream.clicks.arn
}

output "firehose_direct" {
  value = aws_kinesis_firehose_delivery_stream.events_direct.name
}
