# dev backend — mock values. Usage: terraform init -backend-config=envs/dev.backend.hcl
bucket         = "a-tfstate-111111111111"
key            = "1A/dev/terraform.tfstate"
region         = "us-east-1"
dynamodb_table = "a-tflock-dev"
encrypt        = true
