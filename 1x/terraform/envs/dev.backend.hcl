# dev state — mock bucket/table in the env's own (fake) account. Used as:
#   terraform init -backend-config=envs/dev.backend.hcl
bucket         = "x-tfstate-111111111111"
key            = "1x/dev/terraform.tfstate"
region         = "us-east-1"
dynamodb_table = "x-tflock"
encrypt        = true
