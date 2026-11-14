# 02rag_02opensearch IAM — the KB service role (trust only) + the app-role data-plane policy.

# ---------------------------------------------------------------- KB service role (permissions attached in 02rag_04knowledge_bases)

data "aws_iam_policy_document" "kb_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["bedrock.amazonaws.com"]
    }
    # Confused-deputy guard: only knowledge bases in this account may assume the role.
    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [var.account_id]
    }
    condition {
      test     = "ArnLike"
      variable = "aws:SourceArn"
      values   = ["arn:aws:bedrock:${var.region}:${var.account_id}:knowledge-base/*"]
    }
  }
}

# Defined here (not in 02rag_04knowledge_bases) because the data-access policy in main.tf must name it before the KB exists.
resource "aws_iam_role" "kb" {
  name               = "${var.prefix}-kb"
  assume_role_policy = data.aws_iam_policy_document.kb_assume.json
  tags               = { Component = "02rag_02opensearch" }
}

# ---------------------------------------------------------------- app IAM policy (this component only)

data "aws_iam_policy_document" "app_opensearch" {
  statement {
    sid       = "DataPlane"
    actions   = ["aoss:APIAccessAll"] # data-plane gate; the data-access policy narrows it per index
    resources = [aws_opensearchserverless_collection.vectors.arn]
  }
}

resource "aws_iam_role_policy" "app_opensearch" {
  name   = "opensearch-serverless"
  role   = var.app_role_id
  policy = data.aws_iam_policy_document.app_opensearch.json
}
