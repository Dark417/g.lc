# glue-data-quality Tradeoffs

> When Glue Data Quality (DQ) is the right gate, the knobs that cap cost, how it compares, and how it fails.

## Index

- [1. When To Use / Not](#1-when-to-use--not)
- [2. Knobs And Best Practices](#2-knobs-and-best-practices)
- [3. Comparison](#3-comparison)
- [4. Failure Modes](#4-failure-modes)

## 1. When To Use / Not

Glue DQ fits batch corpora already in the catalog.

- **Use**
  - Batch corpora feeding Retrieval-Augmented Generation (RAG)/fine-tuning in a Glue-friendly format
    - Parquet, Comma-Separated Values (CSV), JavaScript Object Notation (JSON)
  - Need audit trail and CloudWatch metrics without running Spark yourself
- **Don't use**
  - Per-request validation ⇒ plain code (Pydantic) or a guardrail
  - Semantic quality (is the answer correct?) ⇒ evaluations
    - See [evaluations](../04safety/evaluations.00index.md)
  - Tiny data ⇒ Great Expectations in a notebook is cheaper

## 2. Knobs And Best Practices

Each rule names the failure it prevents.

- **Cap workers and timeout** on every run
  - Defaults: 5 workers, 2,880 min
  - Prevents runaway cost
- **Idempotent start** with `ClientToken`
  - Prevents a second run on retry
- **Enable `CloudWatchMetricsEnabled`** and alarm on a failing score
- **Keep thresholds in the ruleset**, not in code
  - Version rulesets in Terraform
- **Start from recommendations**
  - Prune noisy rules
  - Add business rules by hand
- **Ceiling `CustomSql`** with a sample size on large tables
  - It scans
- **Scope the service role** to the data prefix and Customer Managed Key (CMK) only

## 3. Comparison

The deciding variable is where the data and pipeline already run.

| Option | What it is | Strength | Weakness | Choose when |
|---|---|---|---|---|
| Glue Data Quality | Managed Data Quality Definition Language (DQDL) on Glue (Deequ) | No infra; catalog-native; metrics | Spark startup and Data Processing Unit (DPU) cost; Glue-bound | Batch lake data on Amazon Web Services (AWS) |
| Great Expectations | Python expectation suite | Rich, portable, works anywhere | You run and schedule it | Notebooks, Pandas, non-AWS |
| Deequ | Spark library | Scales; the engine under Glue DQ | You wire Spark | Custom Spark pipelines |
| Databricks Delta Live Tables (DLT) expectations | Inline expectations in pipelines | Per-row drop/fail in the pipeline | Databricks only | You are already on Databricks |

Pick: Glue Data Quality for catalog tables on AWS, unless you need portability (Great Expectations) or you live in Databricks (DLT).

## 4. Failure Modes

Permission and schema errors fail loudly; cost and shallow rules fail quietly.

**Loud failures**

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Run fails to start | Caller lacks `iam:PassRole` for the role | `AccessDenied` | Allow PassRole on the glue role only |
| Run fails immediately | Role cannot read Simple Storage Service (S3) prefix or CMK | Run `ErrorString` | Grant s3:GetObject on the prefix and kms:Decrypt |
| Ruleset rejected | DQDL syntax or column not in table | `InvalidInputException` | Validate; compare with catalog schema |
| Stale schema | Catalog not updated after file change | Rule errors on missing columns | Re-crawl or update table |

**Quiet failures**

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Surprise bill | Many runs, high workers | Glue cost in Cost Explorer | Cap workers/timeout; schedule |
| Duplicate runs | Retry without token | Two run ids | Pass `ClientToken` |
| All rules green, bad corpus | Rules check shape, not meaning | Eval metrics drop | Add semantic evals |
