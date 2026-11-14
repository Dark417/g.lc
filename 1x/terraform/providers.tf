# providers — AWS provider + default tags. Local env points every service at LocalStack.

provider "aws" {
  region = var.region

  # Guard rail: refuse to run against any account other than the env's own (mock ids in envs/*.tfvars).
  allowed_account_ids = [var.aws_account_id]

  # LocalStack accepts any static credentials and needs path-style S3 URLs; real envs use the normal chain.
  access_key                  = var.use_localstack ? "test" : null
  secret_key                  = var.use_localstack ? "test" : null
  skip_credentials_validation = var.use_localstack
  skip_metadata_api_check     = var.use_localstack
  s3_use_path_style           = var.use_localstack

  dynamic "endpoints" {
    for_each = var.use_localstack ? [var.localstack_endpoint] : []
    content {
      athena             = endpoints.value
      dynamodb           = endpoints.value
      ec2                = endpoints.value
      firehose           = endpoints.value
      glue               = endpoints.value
      iam                = endpoints.value
      kafka              = endpoints.value
      kinesis            = endpoints.value
      kms                = endpoints.value
      logs               = endpoints.value
      rds                = endpoints.value
      redshiftserverless = endpoints.value
      s3                 = endpoints.value
      secretsmanager     = endpoints.value
      sts                = endpoints.value
    }
  }

  # default_tags land on every taggable resource: cost allocation + ownership.
  default_tags {
    tags = local.common_tags
  }
}
