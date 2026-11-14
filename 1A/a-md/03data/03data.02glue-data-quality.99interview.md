# 03data.02glue-data-quality Interview

> Interview questions on Glue Data Quality, with Level 4 (L4) answers and Level 5 (L5) extras.

## Index

- [1. Core Questions](#1-core-questions)
  - [Q1 Data Quality Definition Language (DQDL) And Evaluation](#q1-data-quality-definition-language-dqdl-and-evaluation)
  - [Q2 Catalog Ruleset Vs ETL Transform](#q2-catalog-ruleset-vs-etl-transform)
  - [Q3 Why Data Quality Matters For Retrieval-Augmented Generation (RAG)](#q3-why-data-quality-matters-for-retrieval-augmented-generation-rag)
  - [Q4 Starting Rules On A New Table](#q4-starting-rules-on-a-new-table)
  - [Q5 Alerting On Data Quality](#q5-alerting-on-data-quality)
- [2. L5-Only Questions](#2-l5-only-questions)
  - [Q6 Nightly RAG Ingestion Gate](#q6-nightly-rag-ingestion-gate)
  - [Q7 Glue Data Quality (DQ) Vs Great Expectations](#q7-glue-data-quality-dq-vs-great-expectations)

## 1. Core Questions

Each answer gives the L4 baseline, then what L5 adds.

### Q1 Data Quality Definition Language (DQDL) And Evaluation

**Q:** What is DQDL and how are rules evaluated?

**L4 answer**

- A Domain-Specific Language (DSL): rule type + column + expression
- Evaluated by a Glue run over a catalog table
- Each rule returns Pass/Fail

**L5 extra**

- Engine is Spark/Deequ ⇒ batch, cost per Data Processing Unit (DPU)
- Row-level outcomes only through the Extract, Transform, Load (ETL) transform

### Q2 Catalog Ruleset Vs ETL Transform

**Q:** Catalog ruleset vs `EvaluateDataQuality` in an ETL job?

**L4 answer**

- Catalog = standalone checks on a table
- ETL = checks inside the pipeline
  - Can split good and bad rows

**L5 extra**

- Choose on whether you need to stop or route rows before writing
- Both emit the same result object

### Q3 Why Data Quality Matters For Retrieval-Augmented Generation (RAG)

**Q:** Why does data quality matter for RAG?

**L4 answer**

- These degrade embeddings and retrieval
  - Duplicates
  - Empty or truncated text
  - Wrong languages

**L5 extra**

- Garbage enters the index permanently
  - Fixing costs a re-embed
- Gate before ingestion; keep metrics per release

### Q4 Starting Rules On A New Table

**Q:** How do you get started with rules on a new table?

**L4 answer**

- Run a recommendation run
- Review it
- Store the ruleset

**L5 extra**

- Recommendations overfit the sample
- Tune thresholds with domain knowledge

### Q5 Alerting On Data Quality

**Q:** How would you alert on data quality?

**L4 answer**

- Enable CloudWatch metrics and alarm on the score

**L5 extra**

- Gate the pipeline on the score
- Page on trend, not single dips

## 2. L5-Only Questions

These test design ownership and ambiguity.

### Q6 Nightly RAG Ingestion Gate

**Q:** Design a quality gate for a nightly RAG ingestion.

**L5 answer**

→ Crawl → evaluate ruleset  
→ Score ≥ threshold ⇒ start Knowledge Base (KB) ingestion  
→ Else stop + alert

- Quarantine failing partitions, ingest the rest
- Track score per run id with the KB data-source version

### Q7 Glue Data Quality (DQ) Vs Great Expectations

**Q:** Glue DQ vs Great Expectations for a team on Amazon Web Services (AWS) with Pandas jobs?

**L5 answer**

- Glue DQ if data sits in the catalog and pipelines already use Glue
- Great Expectations if jobs are not Spark and portability matters
- Deciding factors
  - Cost
  - Ownership
  - Where the results get consumed
