# locals — shared data sources, the env-scoped name prefix, and common tags.

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  # AWS names are "<project_prefix>-<env>-<thing>": a-dev-guardrail, a-prod-kb, a-uat-vectors.
  # (The old flat stack used "a-<thing>"; the Java / Python config must read the env-scoped names from outputs.)
  prefix     = "${var.project_prefix}-${var.env}"
  account_id = data.aws_caller_identity.current.account_id

  common_tags = {
    Project = "1A"
    Env     = var.env
    Managed = "terraform"
  }
}
