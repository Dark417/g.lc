# local backend — state in LocalStack S3 + DynamoDB lock. Usage: terraform init -backend-config=envs/local.backend.hcl
bucket                      = "a-tfstate-local"
key                         = "1A/local/terraform.tfstate"
region                      = "us-east-1"
dynamodb_table              = "a-tflock-local"
encrypt                     = true
access_key                  = "test"
secret_key                  = "test"
use_path_style              = true
skip_credentials_validation = true
skip_requesting_account_id  = true
skip_metadata_api_check     = true
endpoints = {
  s3       = "http://localhost:4566"
  dynamodb = "http://localhost:4566"
  sts      = "http://localhost:4566"
}
