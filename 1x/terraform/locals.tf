# locals — shared data sources, naming prefix, common tags.

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  # AWS names are "<project>-<env>-<thing>", e.g. x-dev-orders, x-prod-clicks.
  # The Java/Python config must use the env-qualified names (see outputs.tf).
  prefix     = "${var.project_prefix}-${var.env}"
  account_id = data.aws_caller_identity.current.account_id
  azs        = slice(data.aws_availability_zones.available.names, 0, var.az_count)

  common_tags = {
    Project = "1x"
    Env     = var.env
    Managed = "terraform"
  }
}
