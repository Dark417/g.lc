# 00.00 providers — Terraform + AWS provider, shared variables, locals, default tags.
# Used by: every other file in this folder. Never applied (see AGENTS.md).
# Provider 6.x: needed for the newer Bedrock resources (guardrails, knowledge bases, prompts, flows).

terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.70"
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
  description = "Name prefix; the Java/Python config uses names like a-guardrail, a-kb"
  type        = string
  default     = "a"
}

variable "env" {
  description = "Environment tag (dev, stage, prod)"
  type        = string
  default     = "dev"
}

variable "az_count" {
  description = "Number of AZs for private subnets; 2 is enough for endpoints + OpenSearch standby"
  type        = number
  default     = 2
}

# ---------------------------------------------------------------- provider

provider "aws" {
  region = var.region

  # default_tags land on every taggable resource: cost allocation + ownership.
  default_tags {
    tags = {
      Project = "1A"
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

variable "alert_email" {
  description = "Email that receives cost and GenAI alarms (SNS subscription must be confirmed by hand)"
  type        = string
  default     = "alerts@example.com"
}

