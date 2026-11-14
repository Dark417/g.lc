# providers — the AWS provider, default tags, and the LocalStack switch for env = local.
#
# LocalStack (var.use_localstack = true, envs/local.tfvars):
#   - fake static credentials, no account-id / metadata lookups, path-style S3
#   - every service the stack uses is pointed at one edge endpoint (var.localstack_endpoint)
#   - Bedrock (runtime, agent, guardrails, data automation) and OpenSearch Serverless are NOT emulated by
#     LocalStack: those modules only validate locally; exercise them against a real dev account
# Real envs: allowed_account_ids stops a dev tfvars from ever touching the prod account.

provider "aws" {
  region = var.region

  allowed_account_ids = var.use_localstack ? null : [var.aws_account_id]

  access_key                  = var.use_localstack ? "test" : null
  secret_key                  = var.use_localstack ? "test" : null
  skip_credentials_validation = var.use_localstack
  skip_requesting_account_id  = var.use_localstack
  skip_metadata_api_check     = var.use_localstack
  s3_use_path_style           = var.use_localstack

  dynamic "endpoints" {
    for_each = var.use_localstack ? [var.localstack_endpoint] : []
    content {
      cloudwatch = endpoints.value
      comprehend = endpoints.value
      ec2        = endpoints.value
      glue       = endpoints.value
      iam        = endpoints.value
      kms        = endpoints.value
      logs       = endpoints.value
      s3         = endpoints.value
      sns        = endpoints.value
      sts        = endpoints.value
      transcribe = endpoints.value
    }
  }

  # default_tags land on every taggable resource: cost allocation + ownership.
  default_tags {
    tags = local.common_tags
  }
}
