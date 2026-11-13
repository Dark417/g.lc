# 00.02 kms — one customer-managed key (CMK) that encrypts every data store at rest.
# Why a CMK instead of the AWS-managed default: you control the key policy, rotation, and can revoke access
# (crypto-shredding). Cost: ~$1/key/month + per-request charges (AWS KMS pricing page, order of magnitude).

resource "aws_kms_key" "main" {
  description             = "${local.prefix} data-at-rest key"
  enable_key_rotation     = true # yearly automatic rotation; old versions stay usable for decrypt
  deletion_window_in_days = 7    # minimum safety window before a deleted key is gone for good

  tags = { Component = "00.02" }
}

resource "aws_kms_alias" "main" {
  name          = "alias/${local.prefix}-data"
  target_key_id = aws_kms_key.main.key_id
}

output "kms_key_arn" {
  value = aws_kms_key.main.arn
}
