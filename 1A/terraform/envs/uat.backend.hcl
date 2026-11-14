# uat backend — mock values. Usage: terraform init -backend-config=envs/uat.backend.hcl
bucket         = "a-tfstate-222222222222"
key            = "1A/uat/terraform.tfstate"
region         = "us-east-1"
dynamodb_table = "a-tflock-uat"
encrypt        = true
