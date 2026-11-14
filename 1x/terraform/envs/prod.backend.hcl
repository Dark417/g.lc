# prod state — mock bucket/table in the env's own (fake) account. Used as:
#   terraform init -backend-config=envs/prod.backend.hcl
bucket         = "x-tfstate-333333333333"
key            = "1x/prod/terraform.tfstate"
region         = "us-east-1"
dynamodb_table = "x-tflock"
encrypt        = true
