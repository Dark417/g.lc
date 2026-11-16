# Cloud Equivalents — What To Call Each SD Component

- Purpose: one lookup table of the same building block across AWS, GCP, Azure, and OCI
- Plus: how to name components in an SD interview without sounding AWS-biased
- Names checked against vendor docs as of 2026; ⚠ = verify before relying on it

## Index
- [1. Naming rule for the interview](#1-naming-rule-for-the-interview)
- [2. API gateway: what to actually say](#2-api-gateway-what-to-actually-say)
- [3. Edge and entry](#3-edge-and-entry)
- [4. Compute](#4-compute)
- [5. Storage](#5-storage)
- [6. Databases](#6-databases)
- [7. Messaging and streaming](#7-messaging-and-streaming)
- [8. Analytics and data processing](#8-analytics-and-data-processing)
- [9. Security and identity](#9-security-and-identity)
- [10. Observability and ops](#10-observability-and-ops)
- [11. AI building blocks](#11-ai-building-blocks)
- [12. Close-but-not-equal pairs](#12-close-but-not-equal-pairs)
- [References](#references)

---

## 1. Naming rule for the interview
- Plain idea: say the **role** first, then **one example** as a hint
  - "a blob store, like S3" / "a distributed log, like Kafka"
  - The role is what's graded; the example shows you've used something real
- Three tiers of names

| Tier | Example | When to use |
|---|---|---|
| Generic role | API gateway, load balancer, blob store, CDN, cache, queue | Default for every box on the board |
| Open-source tech | Kafka, Redis, Postgres, Cassandra, Elasticsearch, Flink | Freely: vendor-neutral, and interviewers expect you to know internals |
| Cloud product | S3, DynamoDB, Kinesis, Lambda, SQS | Only when its specific behavior shapes the design, and you can defend it |

- When a cloud product name is fine
  - It's become the generic word: "S3-like blob store" is understood at Oracle, Microsoft, Google
  - You use a property that only it has, and you say so
    - "DynamoDB conditional writes give us the lock"
    - "SQS visibility timeout gives us redelivery"
  - Add "or the equivalent on your stack" once; no need to repeat it
- When to avoid it
  - The name replaces the mechanism: "we use Lambda" without cold starts, concurrency limits, idempotent handlers
  - The company's interviewers may push: "how does that work underneath?" (very common at Google)
    - A managed service is never an excuse to skip the mechanism
- At the target company
  - Knowing their native names is a small bonus, not required
  - Oracle: OCI Object Storage, OCI Streaming; Google: GCS, Spanner, Bigtable, Pub/Sub
  - Use them only if fluent; a wrong product name costs more than a generic one
- Kafka vs Kinesis is a choice, not a synonym
  - Pick by properties: retention and replay, partition count, consumer groups, ops burden
  - 🗣 "A partitioned log, Kafka here; on AWS Kinesis behaves the same way for this use case, with shard limits I'd plan around."
- 🗣 Default line: "I'll keep components generic and name a concrete tech where its behavior matters."

## 2. API gateway: what to actually say
- Plain idea: the one front door that does the cross-cutting checks so services don't repeat them
- The full list (know it, don't recite it)
  - Auth (token validation), rate limiting, routing to services
  - TLS termination, request validation, response caching
  - Request/response transforms, API versioning, metrics and logging
- In the interview: say **2–3**, chosen for this problem
  - Default trio: **auth, rate limiting, routing**
  - Add one if the problem needs it
    - Public API with abuse risk → rate limiting per API key moves to the front
    - Many clients / versions → versioning and transforms
    - Uploads → "large payloads bypass the gateway via presigned URLs"
- Skip in the first pass: TLS termination, load balancing
  - Mention only if asked "what's the difference between a gateway and a load balancer?"
  - 🗣 "The LB spreads traffic across instances of one service; the gateway decides which service and whether the call is allowed. In practice an L7 LB sits in front of or inside the gateway."
- 🗣 Board line: "API gateway: auth, rate limits, routing. Nothing stateful."

## 3. Edge and entry
| Generic (say this) | Open source | AWS | GCP | Azure | OCI |
|---|---|---|---|---|---|
| DNS | BIND, CoreDNS | Route 53 | Cloud DNS | Azure DNS | OCI DNS |
| CDN | Varnish | CloudFront | Cloud CDN | Azure Front Door | Partner CDN (Akamai) ⚠ |
| L7 load balancer | NGINX, Envoy, HAProxy | Application Load Balancer | Cloud Load Balancing (Application LB) | Application Gateway; Front Door (global) | OCI Load Balancer |
| L4 load balancer | HAProxy, IPVS | Network Load Balancer | Cloud Load Balancing (Network LB) | Azure Load Balancer | OCI Network Load Balancer |
| API gateway | Kong, Envoy | API Gateway | API Gateway; Apigee | API Management | OCI API Gateway |
| WAF / DDoS | ModSecurity | AWS WAF; Shield | Cloud Armor | Azure WAF; DDoS Protection | OCI WAF |

## 4. Compute
| Generic (say this) | Open source | AWS | GCP | Azure | OCI |
|---|---|---|---|---|---|
| VMs | KVM | EC2 | Compute Engine | Virtual Machines | OCI Compute |
| Kubernetes | Kubernetes | EKS | GKE | AKS | OKE |
| Serverless containers | Knative | Fargate; App Runner | Cloud Run | Container Apps | Container Instances |
| Functions | OpenFaaS | Lambda | Cloud Run functions (was Cloud Functions) | Azure Functions | OCI Functions |
| Container registry | Harbor | ECR | Artifact Registry | Container Registry (ACR) | Container Registry (OCIR) |
| Batch jobs | Kubernetes Jobs | AWS Batch | Batch | Azure Batch | OCI Batch ⚠ |

## 5. Storage
| Generic (say this) | Open source | AWS | GCP | Azure | OCI |
|---|---|---|---|---|---|
| Blob / object store | MinIO, Ceph | S3 | Cloud Storage (GCS) | Blob Storage | Object Storage |
| Block disk | Ceph RBD | EBS | Persistent Disk; Hyperdisk | Managed Disks | Block Volume |
| Shared file system | NFS | EFS; FSx | Filestore | Azure Files; NetApp Files | File Storage |
| Cold archive | — | S3 Glacier classes | Archive storage class | Archive tier | Archive Storage |

- 🗣 "Blob store for the bytes, database for the metadata, CDN in front for reads."

## 6. Databases
| Generic (say this) | Open source | AWS | GCP | Azure | OCI |
|---|---|---|---|---|---|
| Relational (single-region) | Postgres, MySQL | RDS; Aurora | Cloud SQL; AlloyDB | Azure SQL Database; Database for PostgreSQL | Autonomous Database; Database with PostgreSQL; MySQL HeatWave |
| Distributed SQL (global) | CockroachDB, YugabyteDB | Aurora DSQL | Spanner | Cosmos DB for PostgreSQL (Citus) | Globally Distributed Autonomous Database |
| Key-value / wide-column | Cassandra, ScyllaDB | DynamoDB; Keyspaces | Bigtable | Cosmos DB | NoSQL Database |
| Document | MongoDB | DocumentDB | Firestore | Cosmos DB (NoSQL / MongoDB API) | Autonomous JSON Database |
| In-memory cache | Redis, Valkey, Memcached | ElastiCache; MemoryDB | Memorystore | Azure Cache for Redis / Managed Redis | OCI Cache |
| Search index | Elasticsearch, OpenSearch | OpenSearch Service | No first-party ES; Elastic Cloud on GCP | Azure AI Search | Search with OpenSearch |

| Generic (say this) | Open source | AWS | GCP | Azure | OCI |
|---|---|---|---|---|---|
| Time-series | InfluxDB, TimescaleDB | Timestream | Bigtable (pattern) | Data Explorer | — |
| Graph | Neo4j, JanusGraph | Neptune | Spanner Graph | Cosmos DB (Gremlin) | Oracle Graph (in Autonomous DB) |
| Geospatial | PostGIS | Aurora PostGIS; Location Service | BigQuery GIS; Cloud SQL PostGIS | Azure Maps; PostGIS | Oracle Spatial |

## 7. Messaging and streaming
| Generic (say this) | Open source | AWS | GCP | Azure | OCI |
|---|---|---|---|---|---|
| Work queue | RabbitMQ | SQS | Pub/Sub (pull); Cloud Tasks | Service Bus queues; Queue Storage | OCI Queue |
| Pub/sub fan-out | NATS | SNS | Pub/Sub | Service Bus topics; Event Grid | Notifications |
| Partitioned log (Kafka) | Apache Kafka | MSK | Managed Service for Apache Kafka | Event Hubs (Kafka API) | Streaming (Kafka-compatible) |
| Native stream | Pulsar | Kinesis Data Streams | Pub/Sub (ordering keys) | Event Hubs | Streaming |
| Stream to blob store | Kafka Connect | Data Firehose | Pub/Sub Cloud Storage subscription | Event Hubs Capture | Connector Hub |
| Event bus / router | — | EventBridge | Eventarc | Event Grid | Events |

| Generic (say this) | Open source | AWS | GCP | Azure | OCI |
|---|---|---|---|---|---|
| Stream processing | Flink, Kafka Streams | Managed Service for Apache Flink | Dataflow (Beam) | Stream Analytics | Data Flow (Spark Streaming) |
| Workflow / saga orchestrator | Temporal, Airflow | Step Functions; MWAA | Workflows; Cloud Composer | Durable Functions; Logic Apps | Data Integration ⚠ |
| Scheduler (cron) | cron, Airflow | EventBridge Scheduler | Cloud Scheduler | Functions timer; Logic Apps | Resource Scheduler ⚠ |

- 🗣 "Queue when each message is work for one consumer; log when many consumers read the same history and need replay."

## 8. Analytics and data processing
| Generic (say this) | Open source | AWS | GCP | Azure | OCI |
|---|---|---|---|---|---|
| Data warehouse | ClickHouse, Druid | Redshift | BigQuery | Synapse; Fabric Warehouse | Autonomous Data Warehouse |
| SQL on the data lake | Trino, Presto | Athena | BigQuery external tables; BigLake | Synapse serverless SQL | ADW external tables ⚠ |
| Batch processing (Spark) | Spark | EMR; Glue | Dataproc | Databricks; Synapse Spark | Data Flow |
| Catalog / governance | Hive Metastore, Unity Catalog | Glue Data Catalog; Lake Formation | Dataplex | Purview | Data Catalog |
| Table format | Iceberg, Delta, Hudi | S3 Tables (Iceberg) | BigLake Iceberg | OneLake (Delta) | — |
| Real-time OLAP | Druid, Pinot | — | — | Data Explorer | — |

## 9. Security and identity
| Generic (say this) | Open source | AWS | GCP | Azure | OCI |
|---|---|---|---|---|---|
| Identity and access | Keycloak | IAM; Cognito (end users) | Cloud IAM; Identity Platform | Entra ID; Azure RBAC | IAM (Identity Domains) |
| Key management | HashiCorp Vault | KMS; CloudHSM | Cloud KMS; Cloud HSM | Key Vault; Managed HSM | Vault |
| Secrets | Vault | Secrets Manager | Secret Manager | Key Vault | Vault (secrets) |
| Certificates / private CA | step-ca | ACM; Private CA | Certificate Manager; CA Service | Key Vault certificates | Certificates |

## 10. Observability and ops
| Generic (say this) | Open source | AWS | GCP | Azure | OCI |
|---|---|---|---|---|---|
| Metrics and alerts | Prometheus, Grafana | CloudWatch | Cloud Monitoring | Azure Monitor | Monitoring |
| Logs | ELK, Loki | CloudWatch Logs | Cloud Logging | Log Analytics | Logging |
| Tracing | OpenTelemetry, Jaeger | X-Ray | Cloud Trace | Application Insights | APM |
| Infra as code | Terraform | CloudFormation; CDK | Infrastructure Manager | Bicep / ARM | Resource Manager (Terraform) |

## 11. AI building blocks
| Generic (say this) | Open source | AWS | GCP | Azure | OCI |
|---|---|---|---|---|---|
| Hosted LLM API | vLLM (self-host) | Bedrock | Vertex AI | Azure OpenAI; AI Foundry | Generative AI |
| ML platform | Kubeflow, MLflow | SageMaker | Vertex AI | Azure Machine Learning | Data Science |
| Vector search | pgvector, FAISS, Milvus | OpenSearch; Aurora pgvector; S3 Vectors | Vertex AI Vector Search; AlloyDB | Azure AI Search; Cosmos DB vector | AI Vector Search (Oracle Database 23ai) |
| Agent runtime | ADK, LangGraph | Bedrock AgentCore | Vertex AI Agent Engine | AI Foundry Agent Service | Generative AI Agents |

## 12. Close-but-not-equal pairs
> Same row in the tables above, different behavior. These are the follow-up traps.

| Pair | The difference that matters |
|---|---|
| Kafka vs Kinesis | Kafka: partitions are cheap, retention as long as disk allows, you run brokers (or MSK). Kinesis: per-shard throughput limits, retention up to 365 days, no brokers to run |
| SQS vs Pub/Sub | SQS: one queue, visibility timeout, FIFO groups. Pub/Sub: topic + many subscriptions, push or pull, ordering keys |
| DynamoDB vs Bigtable vs Cosmos DB | DynamoDB: PK/SK items, conditional writes, transactions. Bigtable: one sorted row key, no secondary indexes. Cosmos DB: five consistency levels, multi-API |
| Spanner vs Aurora | Spanner: global strong consistency with TrueTime, horizontal writes. Aurora: one writer per cluster, readers replicate from shared storage |
| Lambda vs Cloud Run | Lambda: one request per instance, 15-min max. Cloud Run: many concurrent requests per container, longer timeouts |
| SNS vs EventBridge | SNS: fan-out at high throughput. EventBridge: content-based routing rules, schema registry, lower throughput per target |

- Check exact limits in the vendor docs before quoting numbers; treat these as orders of magnitude

## References
- [AWS to Azure services comparison — Microsoft Learn](https://learn.microsoft.com/en-us/azure/architecture/aws-professional/services)
- [Compare AWS and Azure services to Google Cloud — Google Cloud docs](https://cloud.google.com/docs/get-started/aws-azure-gcp-service-comparison)
- [OCI services overview — Oracle docs](https://docs.oracle.com/en-us/iaas/Content/services.htm)
