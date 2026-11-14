output "lake_bucket" {
  value = aws_s3_bucket.lake.bucket
}

output "lake_bucket_arn" {
  value = aws_s3_bucket.lake.arn # Firehose + Redshift COPY/UNLOAD roles scope to this
}

output "athena_results_bucket" {
  value = aws_s3_bucket.athena_results.bucket
}

output "athena_results_bucket_arn" {
  value = aws_s3_bucket.athena_results.arn
}
