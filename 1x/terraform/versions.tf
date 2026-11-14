# versions — Terraform core + provider pins for the whole 1x stack.
# Used by: every module in modules/. Never applied (see AGENTS.md).

terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.80"
    }
  }
}
