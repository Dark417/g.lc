# 00.00 providers — Terraform + AWS provider, shared variables, locals, default tags.
# Used by: every other file in this folder. Never applied (see AGENTS.md).

terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.80"
    }
  }

  # A real stack would use a remote backend (S3 + lock). Left local on purpose: this repo is never applied.
}

# ---------------------------------------------------------------- variables

variable "region" {
  description = "AWS region for every resource"
  type        = string
  default     = "us-east-1"
}

variable "prefix" {
  description = "Name prefix; the Java/Python config uses names like x-orders, x-clicks"
  type        = string
  default     = "x"
}

variable "env" {
  description = "Environment tag (dev, stage, prod)"
  type        = string
  default     = "dev"
}

variable "az_count" {
  description = "Number of AZs for private subnets; 3 lets Aurora/MSK survive one AZ loss"
  type        = number
  default     = 3
}

# ---------------------------------------------------------------- provider

provider "aws" {
  region = var.region

  # default_tags land on every taggable resource: cost allocation + ownership.
  default_tags {
    tags = {
      Project = "1x"
      Env     = var.env
      Managed = "terraform"
    }
  }
}

# ---------------------------------------------------------------- shared data + locals

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}
data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  prefix     = var.prefix
  account_id = data.aws_caller_identity.current.account_id
  azs        = slice(data.aws_availability_zones.available.names, 0, var.az_count)
}
