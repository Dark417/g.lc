# glue-data-quality Glue Data Quality

> Gate a Generative Artificial Intelligence (GenAI) corpus before embedding or training: Data Quality Definition Language (DQDL) rules on a catalog table, evaluated by a Glue run.

## Index

- [1. Source And Scope](#1-source-and-scope)
- [2. One-Minute Version](#2-one-minute-version)
- [3. Component Map](#3-component-map)
  - Concepts
    - [01 Why And Flow](glue-data-quality.01why-and-flow.md): pain, use cases, picture, Glue basics, Data Wrangler
    - [02 DQDL](glue-data-quality.02dqdl.md): rule types, expressions, ruleset as code
    - [03 Evaluation Runs](glue-data-quality.03evaluation-runs.md): catalog vs Extract, Transform, Load (ETL), run, poll, gate
    - [04 Recommendations And Results](glue-data-quality.04recommendations-results.md): outcomes, score, history, proposals
  - Decide and defend
    - [98 Tradeoffs](glue-data-quality.98tradeoffs.md): when to use, knobs, comparison, failure modes
    - [99 Interview](glue-data-quality.99interview.md): Level 4 (L4) + Level 5 (L5) questions
- [4. Code Map](#4-code-map)
- [References](#references)

## 1. Source And Scope

Lectures AIP-C01 #43–#45 (slides p.102–108); #40–#42 Data Wrangler (slides p.92–101) are a paragraph only.

- **Scope**: Python + Terraform
- **Terraform**: [modules/03data_02glue_data_quality](../../terraform/modules/03data_02glue_data_quality/main.tf)
  - `a_ai_data` database
  - `docs_metadata` table
  - `a-docs-metadata-dq` ruleset
  - Evaluation role
- **Code**: Python layers `app/*/_03data_02glue_data_quality.py` (slice `glue_dq`)
- **Numbers**: Amazon Web Services (AWS) Glue Developer Guide, read 2026-11
  - "Check the quota page" where unsure

## 2. One-Minute Version

Data quality for GenAI means gating the corpus before embedding or training.

- **What**
  - Glue Data Quality = rules on your data, written in DQDL
  - Evaluated by a Glue (Spark) run
  - Rules attach to a Data Catalog table, or run inside a Glue ETL job
- **Why**
  - Bad inputs poison Retrieval-Augmented Generation (RAG) and fine-tuning
    - Duplicates, empty text, wrong language, truncated files
  - Catch them before embedding or training, when fixing is cheap
- **How**
  - Describe data in the catalog (crawler or Terraform)
  - Write a ruleset (DQDL)
  - Start an evaluation run
  - Read per-rule Pass/Fail and a score
  - Or ask for recommendations: Glue profiles the table and proposes rules
  - Metrics go to CloudWatch; results are queryable by result id
- **Catch**
  - Runs are Spark jobs billed per Data Processing Unit (DPU)-hour with a startup cost ⇒ not a per-record gate
    - Check the pricing page
  - Rules see a table, not one document ⇒ batch pipelines, not request-time validation
  - Recommended rules are a starting point, not a contract
- 🗣 "Data quality for GenAI = gate the corpus before embedding or training."
- 🗣 "DQDL is declarative: rule type, column, expression; the run returns Pass or Fail per rule."
- 🗣 "Recommendations bootstrap the ruleset; humans own thresholds."

## 3. Component Map

The files follow the life of a ruleset: write it, run it, read it, improve it.

```text
 01 why-and-flow ──► 02 dqdl ──► 03 evaluation-runs
                                       │
                      04 recommendations-results
 98 tradeoffs · 99 interview  (decide and defend)
```

Recommendations feed back into the DQDL ruleset after human review.

## 4. Code Map

Every concept file maps to one Python function in the new layer-first layout.

| Concept file | Python path | Function |
|---|---|---|
| 02 rules as data → DQDL string | `app/domain/_03data_02glue_data_quality.py` | `Rule`, `build_ruleset`, `default_rules` |
| 02 create or update ruleset | `app/infra/_03data_02glue_data_quality.py` | `upsert_ruleset` |
| 03 start evaluation (idempotent) | `app/infra/_03data_02glue_data_quality.py` | `start_evaluation` |
| 03 poll a run | `app/infra/_03data_02glue_data_quality.py` | `wait_for_evaluation`, `_wait` |
| 03 quality gate use case | `app/service/_03data_02glue_data_quality.py` | `evaluate_gate` |

| Concept file | Python path | Function |
|---|---|---|
| 04 fetch rule outcomes | `app/infra/_03data_02glue_data_quality.py` | `get_rule_outcomes` |
| 04 list past results | `app/infra/_03data_02glue_data_quality.py` | `list_results` |
| 04 recommendation run | `app/infra/_03data_02glue_data_quality.py` | `start_recommendation`, `wait_for_recommendation` |
| 03 Representational State Transfer (REST) (`/glue_dq`) | `app/api/_03data_02glue_data_quality.py` | `ruleset`, `gate`, `results` |
| 01 settings (`A_GLUE_DQ_`) | `app/config/_03data_02glue_data_quality.py` | `GlueDqSettings` |

- **Gaps** (no repo code)
  - `EvaluateDataQuality` in a Glue ETL script, row-level outcomes
  - Scheduled runs, anomaly detection
  - Data Wrangler (console)

## References

- [aws-samples/aws-glue-samples](https://github.com/aws-samples/aws-glue-samples)
- [Glue Data Quality user guide](https://docs.aws.amazon.com/glue/latest/dg/glue-data-quality.html)
- [DQDL reference](https://docs.aws.amazon.com/glue/latest/dg/dqdl.html)
- [AWS Big Data blog: Glue Data Quality](https://aws.amazon.com/blogs/big-data/)
