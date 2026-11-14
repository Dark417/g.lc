# modules/02rag_04knowledge_bases — managed RAG: S3 kb-docs/ → parse → chunk → embed (Titan V2) → OpenSearch Serverless.
# Lectures 15, 16, 21 (retrieval), 38 (structured stores: doc only), 80 (keeping it fresh: Python).
# Creates:
#   - permissions policy on the KB role (role defined in 02rag_02opensearch so the AOSS data-access policy can name it) → iam.tf
#   - aws_bedrockagent_knowledge_base.main  a-<env>-kb  (VECTOR, Titan V2 1024 dims, storage = collection a-<env>-vectors)
#   - aws_bedrockagent_data_source.s3       a-<env>-kb-docs (S3 prefix kb-docs/, hierarchical chunking)
#   - app policy: Retrieve, RetrieveAndGenerate, ingestion jobs, generator model, rerank, guardrail                   → iam.tf
# Used by: app/infra/_02rag_04knowledge_bases (A_KB_KNOWLEDGE_BASE_ID / A_KB_DATA_SOURCE_ID = outputs).
#
# APPLY ORDER (a KB validates its index at create time):
#   1. 02rag_02opensearch collection + policies   terraform apply -target=module._02rag_02opensearch ...
#   2. vector index a-kb-index                     python: app/infra/_02rag_02opensearch.create_kb_index
#   3. this module                                 terraform apply
# The shared index contract (index name, field names, 1024 dims) must match 02rag_02opensearch Python config.
# Root main.tf sets depends_on = [module._02rag_02opensearch] so the AOSS data-access policy exists first.

locals {
  kb_name        = "${var.prefix}-kb"
  kb_docs_prefix = "kb-docs/"
  kb_embed_arn   = "arn:aws:bedrock:${var.region}::foundation-model/${var.kb_embed_model_id}"
  # Generator for RetrieveAndGenerate: a cross-region inference profile (var.kb_generator_profile);
  # its foundation model is the profile id without the geography prefix.
  kb_generator_model_id = replace(var.kb_generator_profile, "/^(us|eu|apac|global)\\./", "")
  kb_rerank_models = [
    "arn:aws:bedrock:${var.region}::foundation-model/amazon.rerank-v1:0",
    "arn:aws:bedrock:${var.region}::foundation-model/cohere.rerank-v3-5:0",
  ]
}

# ---------------------------------------------------------------- knowledge base

resource "aws_bedrockagent_knowledge_base" "main" {
  name        = local.kb_name
  description = "1A RAG knowledge base over s3://<data bucket>/kb-docs/"
  role_arn    = var.kb_role_arn

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
      collection_arn    = var.aoss_collection_arn
      vector_index_name = var.kb_index_name
      field_mapping {
        vector_field   = "embedding" # = A_OPENSEARCH_VECTOR_FIELD
        text_field     = "text"      # chunk text; BM25 field for HYBRID search
        metadata_field = "metadata"  # Bedrock-managed JSON metadata
      }
    }
  }

  tags = { Component = "02rag_04knowledge_bases" }

  # The role must be able to reach the index when the KB is created (create-time validation).
  # (The AOSS data-access policy is ordered by the module-level depends_on in root main.tf.)
  depends_on = [
    aws_iam_role_policy.kb,
  ]
}

# ---------------------------------------------------------------- data source (S3 kb-docs/)

resource "aws_bedrockagent_data_source" "s3" {
  knowledge_base_id = aws_bedrockagent_knowledge_base.main.id
  name              = "${var.prefix}-kb-docs"
  description       = "S3 kb-docs/ prefix; sidecar <file>.metadata.json gives filterable attributes"

  # DELETE: vectors of this data source are removed when the data source is deleted.
  # RETAIN (provider default): vectors stay in the index ⇒ orphans that still answer queries.
  data_deletion_policy = "DELETE"

  data_source_configuration {
    type = "S3" # also WEB, CONFLUENCE, SHAREPOINT, SALESFORCE, CUSTOM (direct ingestion API)
    s3_configuration {
      bucket_arn         = var.data_bucket_arn
      inclusion_prefixes = [local.kb_docs_prefix] # one prefix per data source
    }
  }

  # Encrypts transient data during ingestion with our CMK (KB role has kms:GenerateDataKey/Decrypt).
  server_side_encryption_configuration {
    kms_key_arn = var.kms_key_arn
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
