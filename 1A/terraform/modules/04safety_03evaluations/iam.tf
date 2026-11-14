# 04safety_03evaluations IAM — evaluation service role + the app-role policy.

# ================================================================ evaluation service role

data "aws_iam_policy_document" "bedrock_eval_trust" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["bedrock.amazonaws.com"]
    }
    # Confused-deputy guard: only evaluation jobs in this account may assume the role.
    condition {
      test     = "StringEquals"
      variable = "aws:SourceAccount"
      values   = [var.account_id]
    }
    condition {
      test     = "ArnLike"
      variable = "aws:SourceArn"
      values   = ["arn:aws:bedrock:${var.region}:${var.account_id}:evaluation-job/*"]
    }
  }
}

resource "aws_iam_role" "bedrock_eval" {
  name               = "${var.prefix}-bedrock-eval"
  assume_role_policy = data.aws_iam_policy_document.bedrock_eval_trust.json
  tags               = { Component = "04safety_03evaluations" }
}

data "aws_iam_policy_document" "bedrock_eval_access" {
  statement {
    sid       = "ListEvalPrefixes"
    actions   = ["s3:ListBucket"]
    resources = [var.data_bucket_arn]
    condition {
      test     = "StringLike"
      variable = "s3:prefix"
      values   = ["${local.eval_dataset_prefix}*", "${local.eval_results_prefix}*"]
    }
  }
  statement {
    sid       = "ReadDatasets"
    actions   = ["s3:GetObject"]
    resources = ["${var.data_bucket_arn}/${local.eval_dataset_prefix}*"]
  }
  statement {
    sid       = "WriteResults"
    actions   = ["s3:PutObject", "s3:GetObject"] # GetObject: the job re-reads partial results it wrote
    resources = ["${var.data_bucket_arn}/${local.eval_results_prefix}*"]
  }

  # Generator + judge inference. Cross-Region inference profiles fan out to several Regions -> Region "*".
  statement {
    sid     = "InvokeGeneratorAndJudge"
    actions = ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream", "bedrock:GetInferenceProfile"]
    resources = [
      "arn:aws:bedrock:*::foundation-model/*",
      "arn:aws:bedrock:*:${var.account_id}:inference-profile/*",
    ]
  }

  # RAG evaluation: the job calls the knowledge base itself (retrieve-only or retrieve-and-generate).
  statement {
    sid       = "QueryKnowledgeBases"
    actions   = ["bedrock:Retrieve", "bedrock:RetrieveAndGenerate"]
    resources = ["arn:aws:bedrock:${var.region}:${var.account_id}:knowledge-base/*"]
  }

  # Datasets are SSE-KMS (bucket default) and results are written with customerEncryptionKeyId = the same CMK.
  statement {
    sid       = "UseDataKey"
    actions   = ["kms:Decrypt", "kms:GenerateDataKey", "kms:DescribeKey"]
    resources = [var.kms_key_arn]
  }
}

resource "aws_iam_role_policy" "bedrock_eval_access" {
  name   = "s3-models-kb-kms"
  role   = aws_iam_role.bedrock_eval.id
  policy = data.aws_iam_policy_document.bedrock_eval_access.json
}

# ================================================================ app IAM (least privilege)

data "aws_iam_policy_document" "app_evals" {
  statement {
    sid = "EvaluationJobs"
    actions = [
      "bedrock:CreateEvaluationJob",
      "bedrock:GetEvaluationJob",
      "bedrock:StopEvaluationJob",
    ]
    resources = ["arn:aws:bedrock:${var.region}:${var.account_id}:evaluation-job/*"]
  }

  # List APIs cannot be scoped to a resource ARN.
  statement {
    sid       = "ListJobs"
    actions   = ["bedrock:ListEvaluationJobs"]
    resources = ["*"]
  }

  statement {
    sid       = "PassEvalRole"
    actions   = ["iam:PassRole"]
    resources = [aws_iam_role.bedrock_eval.arn]
    condition {
      test     = "StringEquals"
      variable = "iam:PassedToService"
      values   = ["bedrock.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy" "app_evals" {
  name   = "evaluations"
  role   = var.app_role_id
  policy = data.aws_iam_policy_document.app_evals.json
}
