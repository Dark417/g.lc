# modules/base_kms — one customer-managed key (CMK) that encrypts every data store at rest.
# Foundation: its ARN is wired into every component module as var.kms_key_arn.
# Why a CMK instead of the AWS-managed default: you control the key policy, rotation, and can revoke access
# (crypto-shredding). Cost: ~$1/key/month + per-request charges (AWS KMS pricing page, order of magnitude).

resource "aws_kms_key" "main" {
  description             = "${var.prefix} data-at-rest key"
  enable_key_rotation     = true                        # yearly automatic rotation; old versions stay usable for decrypt
  deletion_window_in_days = var.deletion_window_in_days # minimum safety window (7) before a deleted key is gone for good; prod waits longer

  tags = { Component = "base_kms" }
}

resource "aws_kms_alias" "main" {
  name          = "alias/${var.prefix}-data"
  target_key_id = aws_kms_key.main.key_id
}
