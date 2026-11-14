# uat state — mock bucket/table in the env's own (fake) account. Used as:
#   terraform init -backend-config=envs/uat.backend.hcl
bucket         = "x-tfstate-222222222222"
key            = "1x/uat/terraform.tfstate"
region         = "us-east-1"
dynamodb_table = "x-tflock"
encrypt        = true
