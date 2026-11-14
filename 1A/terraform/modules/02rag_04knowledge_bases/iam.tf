# 02rag_04knowledge_bases IAM — KB service role permissions + the app-role query/ingestion policy.

# ---------------------------------------------------------------- KB service role permissions

data "aws_iam_policy_document" "kb" {
  statement {
    sid       = "EmbedChunks"
    actions   = ["bedrock:InvokeModel"]
    resources = [local.kb_embed_arn]
  }
  statement {
    sid       = "ListSourcePrefix"
    actions   = ["s3:ListBucket"]
    resources = [var.data_bucket_arn]
    condition {
      test     = "StringLike"
      variable = "s3:prefix"
      values   = ["${local.kb_docs_prefix}*"]
    }
  }
  statement {
    sid       = "ReadSourceDocs" # documents + <file>.metadata.json sidecars
    actions   = ["s3:GetObject"]
    resources = ["${var.data_bucket_arn}/${local.kb_docs_prefix}*"]
  }
  statement {
    sid       = "VectorStore" # data-plane gate; the 02rag_02opensearch data-access policy narrows it per index
    actions   = ["aoss:APIAccessAll"]
    resources = [var.aoss_collection_arn]
  }
  statement {
    sid       = "Kms" # S3 SSE-KMS objects + data source transient-data encryption
    actions   = ["kms:Decrypt", "kms:GenerateDataKey"]
    resources = [var.kms_key_arn]
  }
}

resource "aws_iam_role_policy" "kb" {
  name   = "knowledge-base"
  role   = var.kb_role_id
  policy = data.aws_iam_policy_document.kb.json
}

# ---------------------------------------------------------------- app IAM policy (this component only)

data "aws_iam_policy_document" "app_kb" {
  statement {
    sid       = "Query"
    actions   = ["bedrock:Retrieve", "bedrock:RetrieveAndGenerate"]
    resources = [aws_bedrockagent_knowledge_base.main.arn]
  }
  statement {
    sid       = "Ingestion" # sync = ingestion job, per data source
    actions   = ["bedrock:StartIngestionJob", "bedrock:GetIngestionJob", "bedrock:ListIngestionJobs"]
    resources = [aws_bedrockagent_knowledge_base.main.arn]
  }
  statement {
    sid = "DataSourceAsCode" # create_data_source demo (config as code); drop in production
    actions = [
      "bedrock:CreateDataSource",
      "bedrock:GetDataSource",
    ]
    resources = [aws_bedrockagent_knowledge_base.main.arn]
  }
  statement {
    sid     = "Generator" # RetrieveAndGenerate calls the model as the caller
    actions = ["bedrock:InvokeModel"]
    resources = [
      "arn:aws:bedrock:${var.region}:${var.account_id}:inference-profile/${var.kb_generator_profile}",
      # A cross-region profile routes to the foundation model in any profile Region ⇒ allow it in all of them.
      "arn:aws:bedrock:*::foundation-model/${local.kb_generator_model_id}",
    ]
  }
  statement {
    sid       = "Rerank" # Retrieve with rerankingConfiguration
    actions   = ["bedrock:InvokeModel"]
    resources = local.kb_rerank_models
  }
  statement {
    sid       = "RerankApi"
    actions   = ["bedrock:Rerank"] # no resource-level scoping documented for Rerank; verify in the service authorization reference
    resources = ["*"]
  }
  statement {
    sid       = "Guardrail" # guardrailConfiguration in RetrieveAndGenerate (guardrail itself is 04safety_01guardrails)
    actions   = ["bedrock:ApplyGuardrail"]
    resources = ["arn:aws:bedrock:${var.region}:${var.account_id}:guardrail/*"]
  }
}

resource "aws_iam_role_policy" "app_kb" {
  name   = "knowledge-base"
  role   = var.app_role_id
  policy = data.aws_iam_policy_document.app_kb.json
}
