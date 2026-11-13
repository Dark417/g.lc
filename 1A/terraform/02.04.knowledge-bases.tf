# 02.04 knowledge-bases — managed RAG: S3 kb-docs/ → parse → chunk → embed (Titan V2) → OpenSearch Serverless.
# Lectures 15, 16, 21 (retrieval), 38 (structured stores: doc only), 80 (keeping it fresh: Python).
# Creates:
#   - permissions policy on aws_iam_role.kb (role defined in 02.02 so the AOSS data-access policy can name it)
#   - aws_bedrockagent_knowledge_base.main  a-kb  (VECTOR, Titan V2 1024 dims, storage = collection a-vectors)
#   - aws_bedrockagent_data_source.s3       a-kb-docs (S3 prefix kb-docs/, hierarchical chunking)
#   - app policy: Retrieve, RetrieveAndGenerate, ingestion jobs, generator model, rerank, guardrail
# Used by: app/a02_04_knowledge_bases (A_KB_KNOWLEDGE_BASE_ID / A_KB_DATA_SOURCE_ID = outputs below).
#
# APPLY ORDER (a KB validates its index at create time):
#   1. 02.02 collection + policies       terraform apply -target=aws_opensearchserverless_collection.vectors ...
#   2. vector index a-kb-index            python: app/a02_02_opensearch/infra.create_kb_index
#   3. this file                          terraform apply
# The shared index contract (index name, field names, 1024 dims) must match 02.02 Python config.

locals {
  kb_name           = "${local.prefix}-kb"
  kb_docs_prefix    = "kb-docs/"
  kb_index_name     = "a-kb-index" # = A_OPENSEARCH_INDEX_NAME
  kb_embed_model_id = "amazon.titan-embed-text-v2:0"
  kb_embed_arn      = "arn:aws:bedrock:${var.region}::foundation-model/${local.kb_embed_model_id}"
  # Generator for RetrieveAndGenerate: a cross-region inference profile (= app.shared.config text_model_id).
  kb_generator_profile = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
  kb_rerank_models = [
    "arn:aws:bedrock:${var.region}::foundation-model/amazon.rerank-v1:0",
    "arn:aws:bedrock:${var.region}::foundation-model/cohere.rerank-v3-5:0",
  ]
}

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
    resources = [aws_s3_bucket.data.arn]
    condition {
      test     = "StringLike"
      variable = "s3:prefix"
      values   = ["${local.kb_docs_prefix}*"]
    }
  }
  statement {
    sid       = "ReadSourceDocs" # documents + <file>.metadata.json sidecars
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.data.arn}/${local.kb_docs_prefix}*"]
  }
  statement {
    sid       = "VectorStore" # data-plane gate; the 02.02 data-access policy narrows it per index
    actions   = ["aoss:APIAccessAll"]
    resources = [aws_opensearchserverless_collection.vectors.arn]
  }
  statement {
    sid       = "Kms" # S3 SSE-KMS objects + data source transient-data encryption
    actions   = ["kms:Decrypt", "kms:GenerateDataKey"]
    resources = [aws_kms_key.main.arn]
  }
}

resource "aws_iam_role_policy" "kb" {
  name   = "knowledge-base"
  role   = aws_iam_role.kb.id
  policy = data.aws_iam_policy_document.kb.json
}

# ---------------------------------------------------------------- knowledge base

resource "aws_bedrockagent_knowledge_base" "main" {
  name        = local.kb_name
  description = "1A RAG knowledge base over s3://<data bucket>/kb-docs/"
  role_arn    = aws_iam_role.kb.arn

  knowledge_base_configuration {
    type = "VECTOR" # VECTOR (embeddings) | KENDRA (GenAI index) | SQL (Redshift text-to-SQL, lecture 38)
    vector_knowledge_base_configuration {
      embedding_model_arn = local.kb_embed_arn
      embedding_model_configuration {
        bedrock_embedding_model_configuration {
          dimensions          = 1024      # Titan V2: 256 | 512 | 1024; must equal the index knn_vector dimension
          embedding_data_type = "FLOAT32" # FLOAT32 | BINARY (32x smaller; index must use data_type binary + hamming)
        }
      }
    }
  }

  storage_configuration {
    type = "OPENSEARCH_SERVERLESS" # also OPENSEARCH_MANAGED_CLUSTER, RDS (Aurora pgvector), S3_VECTORS, PINECONE, NEPTUNE_ANALYTICS, MONGO_DB_ATLAS, REDIS_ENTERPRISE_CLOUD
    opensearch_serverless_configuration {
      collection_arn    = aws_opensearchserverless_collection.vectors.arn
      vector_index_name = local.kb_index_name
      field_mapping {
        vector_field   = "embedding" # = A_OPENSEARCH_VECTOR_FIELD
        text_field     = "text"      # chunk text; BM25 field for HYBRID search
        metadata_field = "metadata"  # Bedrock-managed JSON metadata
      }
    }
  }

  tags = { Component = "02.04" }

  # The role must be able to reach the index when the KB is created (create-time validation).
  depends_on = [
    aws_iam_role_policy.kb,
    aws_opensearchserverless_access_policy.data,
  ]
}

# ---------------------------------------------------------------- data source (S3 kb-docs/)

resource "aws_bedrockagent_data_source" "s3" {
  knowledge_base_id = aws_bedrockagent_knowledge_base.main.id
  name              = "${local.prefix}-kb-docs"
  description       = "S3 kb-docs/ prefix; sidecar <file>.metadata.json gives filterable attributes"

  # DELETE: vectors of this data source are removed when the data source is deleted.
  # RETAIN (provider default): vectors stay in the index ⇒ orphans that still answer queries.
  data_deletion_policy = "DELETE"

  data_source_configuration {
    type = "S3" # also WEB, CONFLUENCE, SHAREPOINT, SALESFORCE, CUSTOM (direct ingestion API)
    s3_configuration {
      bucket_arn         = aws_s3_bucket.data.arn
      inclusion_prefixes = [local.kb_docs_prefix] # one prefix per data source
    }
  }

  # Encrypts transient data during ingestion with our CMK (KB role has kms:GenerateDataKey/Decrypt).
  server_side_encryption_configuration {
    kms_key_arn = aws_kms_key.main.arn
  }

  # Chunking is fixed for the life of the data source (AWS KB docs): a change here means a new data source
  # (expect Terraform to plan a replacement) and a full re-ingest. Alternatives, same block:
  #   FIXED_SIZE:   fixed_size_chunking_configuration { max_tokens = 300, overlap_percentage = 20 }
  #   SEMANTIC:     semantic_chunking_configuration { max_token = 300, buffer_size = 0, breakpoint_percentile_threshold = 95 }
  #   NONE:         no sub-block (one chunk per file; pair with a custom_transformation_configuration Lambda)
  # Parsing (optional, default = text extraction):
  #   parsing_configuration { parsing_strategy = "BEDROCK_FOUNDATION_MODEL" bedrock_foundation_model_configuration { model_arn = ... } }
  vector_ingestion_configuration {
    chunking_configuration {
      chunking_strategy = "HIERARCHICAL"
      hierarchical_chunking_configuration {
        level_configuration {
          max_tokens = 1500 # parent: returned to the model (context)
        }
        level_configuration {
          max_tokens = 300 # child: embedded and matched (precision)
        }
        overlap_tokens = 60 # repeated between neighbouring chunks of one level
      }
    }
  }
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
      "arn:aws:bedrock:${var.region}:${local.account_id}:inference-profile/${local.kb_generator_profile}",
      # A cross-region profile routes to the foundation model in any profile Region ⇒ allow it in all of them.
      "arn:aws:bedrock:*::foundation-model/anthropic.claude-sonnet-4-5-20250929-v1:0",
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
    sid       = "Guardrail" # guardrailConfiguration in RetrieveAndGenerate (guardrail itself is 04.01)
    actions   = ["bedrock:ApplyGuardrail"]
    resources = ["arn:aws:bedrock:${var.region}:${local.account_id}:guardrail/*"]
  }
}

resource "aws_iam_role_policy" "app_kb" {
  name   = "knowledge-base"
  role   = aws_iam_role.app.id
  policy = data.aws_iam_policy_document.app_kb.json
}

# ---------------------------------------------------------------- outputs

output "kb_id" {
  description = "A_KB_KNOWLEDGE_BASE_ID"
  value       = aws_bedrockagent_knowledge_base.main.id
}

output "kb_arn" {
  value = aws_bedrockagent_knowledge_base.main.arn
}

output "kb_data_source_id" {
  description = "A_KB_DATA_SOURCE_ID"
  value       = aws_bedrockagent_data_source.s3.data_source_id
}
