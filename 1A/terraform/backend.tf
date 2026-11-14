# backend — remote state in S3 + lock table, partial configuration.
# Values (bucket, key, region, lock table) come from envs/<env>.backend.hcl:
#   terraform init -backend-config=envs/dev.backend.hcl
# One state per env (different key, and in practice a different account + bucket).
# Checks run `terraform init -backend=false`, so no state bucket is needed to validate. Never applied (AGENTS.md).

terraform {
  backend "s3" {}
}
