# versions — Terraform + AWS provider pins for the whole 1A stack.
# Used by: the root module and every module under modules/. Never applied (see AGENTS.md).
# Provider 6.x: needed for the newer Bedrock resources (guardrails, knowledge bases, prompts, flows).

terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.70"
    }
  }
}
