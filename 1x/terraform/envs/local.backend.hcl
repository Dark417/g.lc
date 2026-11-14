# local state — LocalStack S3 + DynamoDB lock (start LocalStack first). Used as:
#   terraform init -backend-config=envs/local.backend.hcl
bucket         = "x-tfstate-000000000000"
key            = "1x/local/terraform.tfstate"
region         = "us-east-1"
dynamodb_table = "x-tflock"
encrypt        = true

endpoints = {
  s3       = "http://localhost:4566"
  dynamodb = "http://localhost:4566"
  sts      = "http://localhost:4566"
}
access_key                  = "test"
secret_key                  = "test"
use_path_style              = true
skip_credentials_validation = true
skip_requesting_account_id  = true
skip_metadata_api_check     = true
