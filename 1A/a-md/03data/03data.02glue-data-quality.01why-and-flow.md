# 03data.02glue-data-quality Why And Flow

> Why Glue Data Quality exists, how a quality gate flows, the Glue basics it builds on, and where Data Wrangler fits.

## Index

- [1. Why It Was Created](#1-why-it-was-created)
  - [1.1 The Pain](#11-the-pain)
  - [1.2 Generative Artificial Intelligence (GenAI) Use Cases](#12-generative-artificial-intelligence-genai-use-cases)
- [2. Picture](#2-picture)
- [3. Glue In One Paragraph](#3-glue-in-one-paragraph)
- [4. Data Wrangler](#4-data-wrangler)

## 1. Why It Was Created

Glue Data Quality (DQ) turns ad-hoc quality scripts into managed rules on a catalog table.

### 1.1 The Pain

- Quality checks lived in ad-hoc Spark/Structured Query Language (SQL) scripts per pipeline
- Open-source tools (Deequ) needed Spark expertise and plumbing
- Glue DQ is built on Deequ (Glue docs)
  - Exposed as managed rules and a Domain-Specific Language (DSL)

### 1.2 Generative Artificial Intelligence (GenAI) Use Cases

- Check the document-metadata table before ingest into a knowledge base
- Check fine-tuning datasets
  - No empty completions
  - Unique ids
  - Label balance
- Gate nightly Extract, Transform, Load (ETL) that builds the corpus

## 2. Picture

A run evaluates the ruleset against the table and the score decides whether ingestion continues.

```text
 S3 glue/docs_metadata/*.parquet
        │  catalog table a_ai_data.docs_metadata (crawler or terraform)
        ▼
 DQDL ruleset ──► evaluation run (Glue Spark, role a-glue-dq)
                      │
          ┌───────────┼───────────────┐
          ▼           ▼               ▼
   result (RuleResults) CloudWatch   optional S3 results
   Pass/Fail + score    metrics      (ResultsS3Prefix)
          ▼
   gate: score >= threshold → continue ingestion, else alert
```

Notice three outputs per run: the result object, CloudWatch metrics, and an optional Simple Storage Service (S3) copy.

## 3. Glue In One Paragraph

You know Glue already; DQ only needs three pieces of it.

- **Data Catalog**: metadata over S3
  - Databases, tables, partitions
- **Crawler**: infers schema and partitions
  - Terraform declares tables when the schema is known
- **ETL** (Glue Studio, lecture 44): visual Spark jobs
  - The same DQ can run as a node

The slice settings name the catalog target and cap the run cost.

```python
# app/config/_03data_02glue_data_quality.py
class GlueDqSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="A_GLUE_DQ_", env_file=".env", extra="ignore")

    database: str = "a_ai_data"
    table: str = "docs_metadata"
    ruleset_name: str = "a-docs-metadata-dq"
    role_arn: str = ""  # terraform output glue_dq_role_arn
    number_of_workers: int = 2  # Glue default is 5; fewer = cheaper, slower (check the minimum)
    timeout_minutes: int = 30  # Glue default 2880 (48 h); cap it, a stuck run keeps billing
    results_s3_prefix: str = ""  # e.g. s3://<bucket>/glue/dq-results/ ; empty = no S3 copy
    gate_min_score: float = 0.95  # fraction of rules that must pass for the gate
    poll_deadline_s: float = 1800.0
```

```python
# app/infra/_03data_02glue_data_quality.py
def _data_source() -> dict[str, Any]:
    cfg = get_glue_dq_settings()
    return {"GlueTable": {"DatabaseName": cfg.database, "TableName": cfg.table}}
```

- **Catch**: a stale catalog breaks rules
  - Re-crawl or update the table after file changes

## 4. Data Wrangler

Lectures 40–42 cover a console tool; it is a paragraph here only.

- **SageMaker Data Wrangler** (in Canvas / Studio): visual data prep
  - Built-in transforms
  - Quick-model
  - Export to a pipeline
- Skipped in code
  - It is a console tool with no stable Application Programming Interface (API) surface to show
- When to mention it
  - Tabular Machine Learning (ML) prep
  - For GenAI corpora use Glue/DQ instead
