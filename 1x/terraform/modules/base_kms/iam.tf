# base_kms IAM — app-role access to the shared CMK.

# Every component encrypts with the shared CMK, so the app needs to use it.
data "aws_iam_policy_document" "app_kms" {
  statement {
    actions   = ["kms:Decrypt", "kms:GenerateDataKey", "kms:DescribeKey"]
    resources = [aws_kms_key.main.arn]
  }
}

resource "aws_iam_role_policy" "app_kms" {
  name   = "kms"
  role   = var.app_role_id
  policy = data.aws_iam_policy_document.app_kms.json
}
