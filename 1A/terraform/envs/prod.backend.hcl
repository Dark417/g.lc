# prod backend — mock values. Usage: terraform init -backend-config=envs/prod.backend.hcl
bucket         = "a-tfstate-333333333333"
key            = "1A/prod/terraform.tfstate"
region         = "us-east-1"
dynamodb_table = "a-tflock-prod"
encrypt        = true
