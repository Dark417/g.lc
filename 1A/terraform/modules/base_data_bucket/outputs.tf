output "bucket" {
  description = "Bucket name, a-<env>-ai-data-<account>"
  value       = aws_s3_bucket.data.bucket
}

output "bucket_arn" {
  value = aws_s3_bucket.data.arn
}
