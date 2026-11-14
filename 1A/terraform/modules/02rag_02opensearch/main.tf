# modules/02rag_02opensearch — vector store for the RAG components (lectures 17, 53–59).
# Creates:
#   - encryption policy (shared CMK), network policy (VPC endpoint + Bedrock service access)
#   - OpenSearch Serverless VPC endpoint in the private subnets (base_network)
#   - collection a-<env>-vectors, type VECTORSEARCH
#   - data-access policy for the app role and the Knowledge Base service role
#   - aws_iam_role.kb: the Bedrock KB service role (02rag_04knowledge_bases attaches its permissions policy and uses it) → iam.tf
#   - app policy: aoss:APIAccessAll on this collection                                                                 → iam.tf
# Used by: app/infra/_02rag_02opensearch (index + queries), app/infra/_02rag_04knowledge_bases via
#   modules/02rag_04knowledge_bases.
#
# The vector INDEX is not created here:
#   - the AWS provider manages collections and policies, not indexes
#   - Python app/infra/_02rag_02opensearch.create_kb_index creates "a-kb-index" (embedding/text/metadata)
#   - alternative: the opensearch-project/opensearch provider (opensearch_index resource) with SigV4 "aoss"
# Apply order: collection (this module) → index (Python) → knowledge base (02rag_04knowledge_bases).
#
# COST (lecture 17 "don't leave OpenSearch running"):
#   - Serverless bills OCU-hours for indexing and search even with zero traffic, plus storage
#   - a minimum OCU floor applies per account/collection group: check the OpenSearch Serverless pricing page
#   - destroy the collection when not in use; standby_replicas = "DISABLED" (var, per env) lowers the floor for dev
#   - base_billing_alarm is the tripwire

locals {
  aoss_collection = "${var.prefix}-vectors" # 3–32 chars, lowercase; policy resources reference this name
}

# ---------------------------------------------------------------- security policies (must exist before the collection)

# Encryption policy: one per collection pattern; fixes the key at creation time (can't switch key later).
resource "aws_opensearchserverless_security_policy" "encryption" {
  name        = "${var.prefix}-vectors-enc"
  type        = "encryption"
  description = "CMK encryption for ${local.aoss_collection}"
  policy = jsonencode({
    Rules = [{
      ResourceType = "collection"
      Resource     = ["collection/${local.aoss_collection}"]
    }]
    AWSOwnedKey = false # true = AWS-owned key (free, no key policy control); false = our CMK (audit, revoke)
    KmsARN      = var.kms_key_arn
  })
}

# Network: VPC-only access for the app + "AWS service private access" for Bedrock.
# Trade-off considered:
#   - AllowFromPublic = true: simplest, works with every client; still gated by SigV4 + the data-access policy
#   - VPC endpoint only: no internet path to the data plane, but Bedrock KB runs outside your VPC
#     ⇒ SourceServices = ["bedrock.amazonaws.com"] lets the KB reach a private collection
# Chosen: private (VPC endpoint + Bedrock service access). If your Region rejects SourceServices,
# fall back to AllowFromPublic = true and rely on the data-access policy (verify in the AOSS network-policy docs).
# Dashboards stay off: no "dashboard" resource type in the rule.
resource "aws_opensearchserverless_security_policy" "network" {
  name        = "${var.prefix}-vectors-net"
  type        = "network"
  description = "VPC endpoint + Bedrock service access for ${local.aoss_collection}"
  policy = jsonencode([{
    Rules = [{
      ResourceType = "collection"
      Resource     = ["collection/${local.aoss_collection}"]
    }]
    AllowFromPublic = false
    SourceVPCEs     = [aws_opensearchserverless_vpc_endpoint.main.id]
    SourceServices  = ["bedrock.amazonaws.com"]
  }])
}

# AOSS-specific interface endpoint (not a generic aws_vpc_endpoint). Reuses the base_network endpoints SG (443 from app).
resource "aws_opensearchserverless_vpc_endpoint" "main" {
  name               = "${var.prefix}-aoss-vpce"
  vpc_id             = var.vpc_id
  subnet_ids         = var.private_subnet_ids
  security_group_ids = [var.endpoints_security_group_id]
}

# ---------------------------------------------------------------- collection

resource "aws_opensearchserverless_collection" "vectors" {
  name        = local.aoss_collection
  type        = "VECTORSEARCH" # SEARCH (full text) | TIMESERIES (logs, default) | VECTORSEARCH (k-NN, used by Bedrock KB)
  description = "Vector store for the 1A knowledge base"

  # ENABLED (default) = replicas in a standby AZ: production availability, roughly double the OCU floor.
  # DISABLED = single-AZ, about half the minimum OCUs: fine for dev, not for production. Immutable after create.
  standby_replicas = var.standby_replicas

  tags = { Component = "02rag_02opensearch" }

  # The collection can't be created until a matching encryption policy exists (network policy too, to be reachable).
  depends_on = [
    aws_opensearchserverless_security_policy.encryption,
    aws_opensearchserverless_security_policy.network,
  ]
}

# ---------------------------------------------------------------- data-access policy (who may touch indexes/documents)

# IAM alone is not enough on AOSS: a principal needs BOTH aoss:APIAccessAll (IAM) AND a data-access rule.
resource "aws_opensearchserverless_access_policy" "data" {
  name        = "${var.prefix}-vectors-data"
  type        = "data"
  description = "App: manage + query indexes; KB: read/write documents"
  policy = jsonencode([
    {
      Description = "app role: create/delete the KB index, bulk load, query, search pipelines"
      Rules = [
        {
          ResourceType = "index"
          Resource     = ["index/${local.aoss_collection}/*"]
          Permission = [
            "aoss:CreateIndex",
            "aoss:DeleteIndex",
            "aoss:UpdateIndex",
            "aoss:DescribeIndex",
            "aoss:ReadDocument",
            "aoss:WriteDocument",
          ]
        },
        {
          ResourceType = "collection"
          Resource     = ["collection/${local.aoss_collection}"]
          Permission = [
            "aoss:DescribeCollectionItems",
            "aoss:CreateCollectionItems",
            "aoss:UpdateCollectionItems",
          ]
        },
      ]
      Principal = [var.app_role_arn]
    },
    {
      Description = "KB service role: ingestion writes, retrieval reads; no index create/delete"
      Rules = [
        {
          ResourceType = "index"
          Resource     = ["index/${local.aoss_collection}/*"]
          Permission   = ["aoss:DescribeIndex", "aoss:ReadDocument", "aoss:WriteDocument", "aoss:UpdateIndex"]
        },
        {
          ResourceType = "collection"
          Resource     = ["collection/${local.aoss_collection}"]
          Permission   = ["aoss:DescribeCollectionItems"]
        },
      ]
      Principal = [aws_iam_role.kb.arn]
    },
  ])
}
