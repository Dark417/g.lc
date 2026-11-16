# opensearch.03serverless Serverless Collections

> OCU-billed collections with three access policies, reached through Signature Version 4 (SigV4).

## Index

- [1. Collections And Types](#1-collections-and-types)
- [2. Compute And Billing](#2-compute-and-billing)
- [3. What You Give Up](#3-what-you-give-up)
- [4. The Three Policies](#4-the-three-policies)
  - [4.1 Encryption Policy](#41-encryption-policy)
  - [4.2 Network Policy](#42-network-policy)
  - [4.3 Data-Access Policy](#43-data-access-policy)
  - [4.4 This Repo's Choice](#44-this-repos-choice)
- [5. SigV4 Client](#5-sigv4-client)

## 1. Collections And Types

A collection groups indexes under one type, one policy set, and one endpoint.

- **Types** (immutable)
  - `SEARCH`: full text, low-latency queries
  - `TIMESERIES`: logs, append-heavy, newest data hot (provider default)
  - `VECTORSEARCH`: k-Nearest Neighbors (k-NN); what Bedrock Knowledge Base (KB) uses

```python
# app/config/_02rag_02opensearch.py
collection_name: str = "a-vectors"
# terraform output aoss_collection_endpoint, host part only (no https://)
collection_endpoint: str = "COLLECTION_ID.us-east-1.aoss.amazonaws.com"
service: str = "aoss"  # "aoss" = Serverless, "es" = managed domain (SigV4 service name)
```

## 2. Compute And Billing

Indexing and search scale separately in OpenSearch Compute Units (OCUs) over S3-persisted data.

- 1 OCU = 6 gibibytes (GiB) memory + matching Virtual Central Processing Unit (vCPU) (per Amazon Web Services (AWS) docs)
- Data persists in Simple Storage Service (S3); OCUs cache hot data
- A minimum OCU floor bills 24/7 even without traffic
  - Exact floor and fractional OCUs: pricing page
- Account-level maximum OCU setting caps cost runaway
- `standby_replicas = DISABLED` (dev): single Availability Zone (AZ), about half the floor; immutable
- **Lecture 17 warning**
  - A tutorial collection left running is the classic surprise bill
  - The KB quick-create flow creates a collection for you
    - ⇒ delete it with the KB

## 3. What You Give Up

Serverless removes knobs along with operations.

- No shard/replica settings
- No Index State Management (ISM) (TIMESERIES has lifecycle retention policies)
- No custom plugins
- Fewer k-NN knobs exposed
- No `?refresh` ⇒ writes visible after a delay
  - Seconds, order of magnitude
- Some Application Programming Interfaces (APIs) differ per collection type (check "supported operations")
- Early VECTORSEARCH collections rejected client-supplied `_id` on index/bulk
  - If yours does, drop `_id` and delete by query on the stored `doc_id` field

## 4. The Three Policies

Encryption, network, and data access each gate a different thing.

### 4.1 Encryption Policy

Required before the collection exists.

- AWS-owned key or a Customer Managed Key (CMK)
- Matched by collection name pattern
- The key is fixed at creation ⇒ wrong key = recreate the collection

### 4.2 Network Policy

Controls from where the endpoint is reachable.

- Options
  - Public endpoint
  - Virtual Private Cloud (VPC) endpoints (`aws_opensearchserverless_vpc_endpoint`)
  - AWS service access (`SourceServices: bedrock.amazonaws.com`)
- Separate rules for the collection endpoint and Dashboards

### 4.3 Data-Access Policy

Grants per principal (role Amazon Resource Name (ARN)).

- Index permissions: `aoss:CreateIndex`, `ReadDocument`, `WriteDocument`, …
- Collection permissions
- Identity and Access Management (IAM) must also allow `aoss:APIAccessAll` on the collection
  - ⇒ both gates must pass

### 4.4 This Repo's Choice

Private access for the app, service access for Bedrock.

- VPC endpoint for the app + Bedrock service access for the KB, no public endpoint
- **Trade-off**
  - Public + data-access policy is simpler
  - Private removes the internet path but depends on Bedrock service access
- **Fallback** if a Region rejects `SourceServices`
  - `AllowFromPublic = true`, still SigV4 + data-access gated
- Terraform: [modules/02rag_02opensearch](../../terraform/modules/02rag_02opensearch/main.tf)

## 5. SigV4 Client

Every Amazon OpenSearch Serverless (AOSS) or domain call is signed with refreshing AWS credentials.

```python
# app/infra/_02rag_02opensearch.py
@lru_cache
def opensearch_client() -> OpenSearch:
    s = get_opensearch_settings()
    credentials = aws.session().get_credentials()  # refreshes itself (role / SSO); never freeze keys
    auth = AWSV4SignerAuth(credentials, aws.session().region_name, s.service)  # "aoss" or "es"
    return OpenSearch(
        hosts=[{"host": s.collection_endpoint, "port": s.port}],
        http_auth=auth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,  # required for AWSV4SignerAuth
        pool_maxsize=20,
        timeout=s.timeout_s,
    )
```

- **Catch**: IAM `aoss:APIAccessAll` is necessary but not sufficient
  - The data-access policy must name the role, or every call returns 403
