# 02.02 opensearch-serverless — vector store for the RAG components (lectures 17, 53–59).
# Creates:
#   - encryption policy (CMK aws_kms_key.main), network policy (VPC endpoint + Bedrock service access)
#   - OpenSearch Serverless VPC endpoint in the private subnets
#   - collection a-vectors, type VECTORSEARCH
#   - data-access policy for the app role and the Knowledge Base service role
#   - aws_iam_role.kb: the Bedrock KB service role (02.04 attaches its permissions policy and uses it)
#   - app policy: aoss:APIAccessAll on this collection
# Used by: app/a02_02_opensearch (index + queries), app/a02_04_knowledge_bases via terraform/02.04.
#
# The vector INDEX is not created here:
#   - the AWS provider manages collections and policies, not indexes
#   - Python app/a02_02_opensearch/infra.create_kb_index creates "a-kb-index" (embedding/text/metadata)
#   - alternative: the opensearch-project/opensearch provider (opensearch_index resource) with SigV4 "aoss"
# Apply order: collection (this file) → index (Python) → knowledge base (02.04).
#
# COST (lecture 17 "don't leave OpenSearch running"):
#   - Serverless bills OCU-hours for indexing and search even with zero traffic, plus storage
#   - a minimum OCU floor applies per account/collection group: check the OpenSearch Serverless pricing page
#   - destroy the collection when not in use; standby_replicas = "DISABLED" below lowers the floor for dev
#   - 00.04 billing alarm is the tripwire

locals {
  aoss_collection = "${local.prefix}-vectors" # 3–32 chars, lowercase; policy resources reference this name
}

# ---------------------------------------------------------------- security policies (must exist before the collection)

# Encryption policy: one per collection pattern; fixes the key at creation time (can't switch key later).
resource "aws_opensearchserverless_security_policy" "encryption" {
  name        = "${local.prefix}-vectors-enc"
  type        = "encryption"
  description = "CMK encryption for ${local.aoss_collection}"
  policy = jsonencode({
    Rules = [{
      ResourceType = "collection"
      Resource     = ["collection/${local.aoss_collection}"]
    }]
    AWSOwnedKey = false # true = AWS-owned key (free, no key policy control); false = our CMK (audit, revoke)
    KmsARN      = aws_kms_key.main.arn
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
  name        = "${local.prefix}-vectors-net"
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

# AOSS-specific interface endpoint (not a generic aws_vpc_endpoint). Reuses the 00.01 endpoints SG (443 from app).
resource "aws_opensearchserverless_vpc_endpoint" "main" {
  name               = "${local.prefix}-aoss-vpce"
  vpc_id             = aws_vpc.main.id
  subnet_ids         = aws_subnet.private[*].id
  security_group_ids = [aws_security_group.endpoints.id]
}

# ---------------------------------------------------------------- collection

resource "aws_opensearchserverless_collection" "vectors" {
  name        = local.aoss_collection
  type        = "VECTORSEARCH" # SEARCH (full text) | TIMESERIES (logs, default) | VECTORSEARCH (k-NN, used by Bedrock KB)
  description = "Vector store for the 1A knowledge base"

  # ENABLED (default) = replicas in a standby AZ: production availability, roughly double the OCU floor.
  # DISABLED = single-AZ, about half the minimum OCUs: fine for dev, not for production. Immutable after create.
  standby_replicas = "DISABLED"

  tags = { Component = "02.02" }

  # The collection can't be created until a matching encryption policy exists (network policy too, to be reachable).
  depends_on = [
    aws_opensearchserverless_security_policy.encryption,
    aws_opensearchserverless_security_policy.network,
  ]
}

# ---------------------------------------------------------------- KB service role (permissions attached in 02.04)

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
      values   = [local.account_id]
    }
    condition {
      test     = "ArnLike"
      variable = "aws:SourceArn"
      values   = ["arn:aws:bedrock:${var.region}:${local.account_id}:knowledge-base/*"]
    }
  }
}

# Defined here (not in 02.04) because the data-access policy below must name it before the KB exists.
resource "aws_iam_role" "kb" {
  name               = "${local.prefix}-kb"
  assume_role_policy = data.aws_iam_policy_document.kb_assume.json
  tags               = { Component = "02.02" }
}

# ---------------------------------------------------------------- data-access policy (who may touch indexes/documents)

# IAM alone is not enough on AOSS: a principal needs BOTH aoss:APIAccessAll (IAM) AND a data-access rule.
resource "aws_opensearchserverless_access_policy" "data" {
  name        = "${local.prefix}-vectors-data"
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
      Principal = [aws_iam_role.app.arn]
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

# ---------------------------------------------------------------- app IAM policy (this component only)

data "aws_iam_policy_document" "app_opensearch" {
  statement {
    sid       = "DataPlane"
    actions   = ["aoss:APIAccessAll"] # data-plane gate; the data-access policy above narrows it per index
    resources = [aws_opensearchserverless_collection.vectors.arn]
  }
}

resource "aws_iam_role_policy" "app_opensearch" {
  name   = "opensearch-serverless"
  role   = aws_iam_role.app.id
  policy = data.aws_iam_policy_document.app_opensearch.json
}

# ---------------------------------------------------------------- outputs

output "aoss_collection_endpoint" {
  description = "https://<id>.<region>.aoss.amazonaws.com → A_OPENSEARCH_COLLECTION_ENDPOINT (host part)"
  value       = aws_opensearchserverless_collection.vectors.collection_endpoint
}

output "aoss_collection_arn" {
  value = aws_opensearchserverless_collection.vectors.arn
}

output "aoss_collection_id" {
  value = aws_opensearchserverless_collection.vectors.id
}

output "kb_role_arn" {
  value = aws_iam_role.kb.arn
}
