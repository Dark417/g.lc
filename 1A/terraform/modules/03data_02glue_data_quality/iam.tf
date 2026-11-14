# 03data_02glue_data_quality IAM — Glue service role for evaluation runs + the app-role policy.

# ---------------------------------------------------------------- service role for evaluation runs

data "aws_iam_policy_document" "glue_dq_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["glue.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "glue_dq" {
  name               = local.glue_dq_role_name
  assume_role_policy = data.aws_iam_policy_document.glue_dq_assume.json
  tags               = { Component = "03data_02glue_data_quality" }
}

data "aws_iam_policy_document" "glue_dq_run" {
  statement {
    sid       = "ReadData"
    actions   = ["s3:GetObject"]
    resources = ["${var.data_bucket_arn}/glue/*"]
  }
  statement {
    sid       = "ListData"
    actions   = ["s3:ListBucket"]
    resources = [var.data_bucket_arn]
    condition {
      test     = "StringLike"
      variable = "s3:prefix"
      values   = ["glue/*"]
    }
  }
  statement {
    sid       = "ResultsWrite" # ResultsS3Prefix output of a run
    actions   = ["s3:PutObject"]
    resources = ["${var.data_bucket_arn}/glue/dq-results/*"]
  }
  statement {
    sid       = "Kms"
    actions   = ["kms:Decrypt", "kms:GenerateDataKey"]
    resources = [var.kms_key_arn]
  }
  statement {
    sid = "Catalog"
    actions = [
      "glue:GetDatabase", "glue:GetTable", "glue:GetTables", "glue:GetPartitions",
      "glue:GetDataQualityRuleset", "glue:PublishDataQualityResult"
    ]
    resources = ["*"] # catalog ARNs need account + region + names; tighten per database in production
  }
  statement {
    sid       = "Logs"
    actions   = ["logs:CreateLogGroup", "logs:CreateLogStream", "logs:PutLogEvents"]
    resources = ["arn:aws:logs:${var.region}:${var.account_id}:log-group:/aws-glue/*"]
  }
  statement {
    sid       = "Metrics"
    actions   = ["cloudwatch:PutMetricData"]
    resources = ["*"] # PutMetricData has no resource ARN; Glue publishes its own namespace - verify and add a namespace condition
  }
}

resource "aws_iam_role_policy" "glue_dq_run" {
  name   = "dq-run"
  role   = aws_iam_role.glue_dq.id
  policy = data.aws_iam_policy_document.glue_dq_run.json
}

# ---------------------------------------------------------------- app policy (least privilege)

data "aws_iam_policy_document" "app_glue_dq" {
  statement {
    sid = "Runs"
    actions = [
      "glue:StartDataQualityRulesetEvaluationRun", "glue:GetDataQualityRulesetEvaluationRun",
      "glue:GetDataQualityResult", "glue:BatchGetDataQualityResult", "glue:ListDataQualityResults",
      "glue:StartDataQualityRuleRecommendationRun", "glue:GetDataQualityRuleRecommendationRun"
    ]
    resources = ["*"] # run ids are not known up front
  }
  statement {
    sid       = "Rulesets"
    actions   = ["glue:GetDataQualityRuleset", "glue:CreateDataQualityRuleset", "glue:UpdateDataQualityRuleset"]
    resources = ["arn:aws:glue:${var.region}:${var.account_id}:dataQualityRuleset/*"]
  }
  statement {
    sid       = "Catalog" # runs and ruleset creation validate against the table
    actions   = ["glue:GetDatabase", "glue:GetTable", "glue:GetPartitions"]
    resources = ["*"]
  }
  statement {
    sid       = "PassRole" # starting a run hands the role to Glue
    actions   = ["iam:PassRole"]
    resources = [aws_iam_role.glue_dq.arn]
    condition {
      test     = "StringEquals"
      variable = "iam:PassedToService"
      values   = ["glue.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy" "app_glue_dq" {
  name   = "glue-dq"
  role   = var.app_role_id
  policy = data.aws_iam_policy_document.app_glue_dq.json
}
