# backend — remote state in S3 with a DynamoDB lock table, one state file per env.
# Partial config on purpose: bucket/key/region/table come from envs/<env>.backend.hcl.
#   terraform init -backend-config=envs/dev.backend.hcl
# Checks in this repo use `terraform init -backend=false`, so no state bucket is ever touched.

terraform {
  backend "s3" {}
}
