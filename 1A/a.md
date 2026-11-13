# a — AI Knowledge Map (1A manifest)

- Master index of the 1A knowledge + code tree
- Mirror: claude.ai Project `1D/A/AMap.md` (keep identical; this file is master — [AGENTS.md §4](AGENTS.md#4-manifest-amd-and-the-project-amap))
- `[C]` = has code (Python, + Java on backend call paths, + Terraform for cloud components)
- Status: ⬜ planned · 🔧 wip · ✅ gen (done) · ▶ ran · 🎓 reviewed
- Source: AIP-C01 course lectures 1–59 (learned so far); later lectures are planned groups
- Last updated: 2026-11-13

## Index
- [Catalog](#catalog)
- [00 Foundation](#00-foundation)
- [01 Bedrock core and prompting](#01-bedrock-core-and-prompting)
- [02 RAG and vector stores](#02-rag-and-vector-stores)
- [03 Data for GenAI](#03-data-for-genai)
- [04 Safety, PII, and evaluation](#04-safety-pii-and-evaluation)
- [05 Operations and observability](#05-operations-and-observability)
- [06–08 Planned groups](#0608-planned-groups)
- [Lecture map](#lecture-map)
- [Change log](#change-log)

### Catalog
- 00 Foundation
  - ✅ 00.00–00.05 Providers, network + Bedrock endpoint, KMS, IAM, billing alarm, data bucket (Terraform only)
- 01 Bedrock core and prompting
  - 🔧 [C] 01.01 Bedrock Converse API — A-010
  - 🔧 [C] 01.02 Model customization (fine-tuning, LoRA) — A-011
  - 🔧 [C] 01.03 Prompt management — A-012
  - 🔧 [C] 01.04 Prompt flows — A-013
  - 🔧 [C] 01.05 Prompt engineering and structured output — A-014
- 02 RAG and vector stores
  - 🔧 [C] 02.01 Embeddings and vector search — A-020
  - 🔧 [C] 02.02 OpenSearch as a vector store — A-021
  - 🔧 [C] 02.03 Chunking — A-022
  - 🔧 [C] 02.04 Bedrock Knowledge Bases — A-023
- 03 Data for GenAI
  - 🔧 [C] 03.01 Bedrock Data Automation — A-030
  - 🔧 [C] 03.02 Glue Data Quality — A-031
  - 🔧 [C] 03.03 Transcribe — A-032
  - 🔧 [C] 03.04 Comprehend — A-033
- 04 Safety, PII, and evaluation
  - 🔧 [C] 04.01 Bedrock Guardrails — A-040
  - 🔧 [C] 04.02 PII detection and redaction — A-041
  - 🔧 [C] 04.03 Evaluations (RAG, model, guardrail) — A-042
- 05 Operations and observability
  - 🔧 [C] 05.01 GenAI observability — A-050
- 06 Agents · 07 Integration and orchestration · 08 Governance and security
  - ⬜ planned (lectures 97+) — backlog A-060..A-080

---

## 00 Foundation
- ✅ 00.00–00.05 (Terraform only)
  - `terraform/00.00.providers.tf` — aws provider ~> 6.70, variables, `local.prefix = "a"`, default tags
  - `terraform/00.01.network.tf` — VPC, 2 private subnets, app SG, S3/DynamoDB gateway endpoints, `bedrock-runtime` PrivateLink endpoint
  - `terraform/00.02.kms.tf` — CMK `alias/a-data`
  - `terraform/00.03.iam.tf` — app role `a-app`; components attach their own policies
  - `terraform/00.04.billing-alarm.tf` — SNS `a-alerts` + EstimatedCharges alarm (lecture 5)
  - `terraform/00.05.data-bucket.tf` — shared bucket `a-ai-data-<account>`, one prefix per component
  - 2026-11-13 · Claude · `terraform validate` passed (Terraform 1.9.8, aws 6.73.0)

## 01 Bedrock core and prompting
- 🔧 [C] 01.01 Bedrock Converse API — A-010 · lectures 7–10, 22
  - Doc `docs/01.01.bedrock-converse.md` · Python `app/a01_01_converse/` · Java `com.lc.a.a01_01_converse` · TF `01.01.bedrock-converse.tf`
- 🔧 [C] 01.02 Model customization — A-011 · lectures 11–12
  - Doc `docs/01.02.model-customization.md` · Python `app/a01_02_customization/` · TF `01.02.model-customization.tf`
- 🔧 [C] 01.03 Prompt management — A-012 · lecture 27
  - Doc `docs/01.03.prompt-management.md` · Python `app/a01_03_prompt_management/` · TF `01.03.prompt-management.tf`
- 🔧 [C] 01.04 Prompt flows — A-013 · lecture 28
  - Doc `docs/01.04.prompt-flows.md` · Python `app/a01_04_prompt_flows/` · TF `01.04.prompt-flows.tf`
- 🔧 [C] 01.05 Prompt engineering and structured output — A-014 · lectures 29–34
  - Doc `docs/01.05.prompt-engineering.md` · Python `app/a01_05_prompt_engineering/` · no TF (uses 01.01 permissions)

## 02 RAG and vector stores
- 🔧 [C] 02.01 Embeddings and vector search — A-020 · lectures 13, 14, 20
  - Doc `docs/02.01.embeddings-vector-search.md` · Python `app/a02_01_embeddings/` · no TF (uses 01.01 permissions)
- 🔧 [C] 02.02 OpenSearch as a vector store — A-021 · lectures 17, 53–59
  - Doc `docs/02.02.opensearch-vector-store.md` · Python `app/a02_02_opensearch/` · TF `02.02.opensearch-serverless.tf`
- 🔧 [C] 02.03 Chunking — A-022 · lectures 18–19
  - Doc `docs/02.03.chunking.md` · Python `app/a02_03_chunking/` · no TF (chunking config lives on the 02.04 data source)
- 🔧 [C] 02.04 Bedrock Knowledge Bases — A-023 · lectures 15, 16, 21, 38
  - Doc `docs/02.04.knowledge-bases.md` · Python `app/a02_04_knowledge_bases/` · TF `02.04.knowledge-bases.tf`

## 03 Data for GenAI
- 🔧 [C] 03.01 Bedrock Data Automation — A-030 · lectures 38–39
  - Doc `docs/03.01.data-automation.md` · Python `app/a03_01_data_automation/` · TF `03.01.data-automation.tf`
- 🔧 [C] 03.02 Glue Data Quality — A-031 · lectures 43–45 (40–42 doc mention)
  - Doc `docs/03.02.glue-data-quality.md` · Python `app/a03_02_glue_data_quality/` · TF `03.02.glue-data-quality.tf`
- 🔧 [C] 03.03 Transcribe — A-032 · lectures 47–48
  - Doc `docs/03.03.transcribe.md` · Python `app/a03_03_transcribe/` · TF `03.03.transcribe.tf`
- 🔧 [C] 03.04 Comprehend — A-033 · lectures 49–52
  - Doc `docs/03.04.comprehend.md` · Python `app/a03_04_comprehend/` · TF `03.04.comprehend.tf`

## 04 Safety, PII, and evaluation
- 🔧 [C] 04.01 Bedrock Guardrails — A-040 · lectures 23–25, 34
  - Doc `docs/04.01.guardrails.md` · Python `app/a04_01_guardrails/` · Java `com.lc.a.a04_01_guardrails` · TF `04.01.guardrails.tf`
- 🔧 [C] 04.02 PII detection and redaction — A-041 · lectures 26, 49–51 (+47 tie-in)
  - Doc `docs/04.02.pii-redaction.md` · Python `app/a04_02_pii_redaction/`
- 🔧 [C] 04.03 Evaluations (RAG, model, guardrail) — A-042 · lecture 21 (+190–192 preview)
  - Doc `docs/04.03.evaluations.md` · Python `app/a04_03_evaluations/` · TF `04.03.evaluations.tf`

## 05 Operations and observability
- 🔧 [C] 05.01 GenAI observability — A-050 · lecture 46 (+195–206 preview)
  - Doc `docs/05.01.genai-observability.md` · Python `app/a05_01_observability/` · TF `05.01.observability.tf`

## 06–08 Planned groups
- ⬜ 06 Agents — lectures 97–125 (Bedrock Agents, multi-agent, memory, Strands, AgentCore, MCP, HITL, Amazon Quick)
- ⬜ 07 Integration and orchestration — lectures 126–136, 152–187 (caching, cross-region inference, Lambda, API Gateway, Step Functions, AppConfig, queues/events)
- ⬜ 08 Governance and security — lectures 188–234 (tracing, CloudTrail, X-Ray, Lake Formation, IAM, KMS, Macie, Cognito, WAF, VPC/PrivateLink)
- The old 1x backlog items X-027..X-029 (Bedrock, Step Functions + Bedrock, agent SDKs) now belong here

## Lecture map
| Lectures | Concept | Treatment |
|---|---|---|
| 1–4 | Course intro, materials, signup | Skipped: logistics |
| 5 | Billing alarm | Terraform `00.04` |
| 6 | Section intro | Skipped: intro |
| 7–10 | Bedrock overview, model access, playground, Converse API | Coded `01.01` |
| 11–12 | Fine-tuning, LoRA | Coded `01.02` (high level: before the model) |
| 13–14 | RAG, vector stores and semantic search | Coded `02.01` |
| 15–16 | Knowledge Bases + hands-on | Coded `02.04` |
| 17 | Don't leave OpenSearch running | Folded into `02.02` (cost) + `00.04` alarm |
| 18–19 | Chunking strategies, chunking in Bedrock | Coded `02.03` |
| 20 | Optimizing vector store and embeddings | Coded `02.01` |
| 21 | Evaluating RAG performance | Coded `04.03` (+ retrieval side in `02.04`) |
| 22 | Multimodal models and pipelines | Coded in `01.01` (image / document blocks) |
| 23–25 | Guardrails, Automated Reasoning, hands-on | Coded `04.01` |
| 26 | Token-level redaction | Coded `04.02` |
| 27 | Prompt Management | Coded `01.03` |
| 28 | Prompt Flows | Coded `01.04` |
| 29–34 | Structured output, prompt engineering, misuse and bias | Coded `01.05` (+ prompt-attack filter in `04.01`) |
| 35 | Enterprise integration | Doc mention in `01.01`; full topic in group 07 |
| 36 | Well-Architected GenAI Lens | Skipped: checklist, no mechanism to code |
| 37 | Section intro | Skipped: intro |
| 38 | Dealing with structured data | Doc in `02.04` (structured KB) + `03.01` |
| 39 | Bedrock Data Automation | Coded `03.01` |
| 40–42 | SageMaker Data Wrangler + demo | Doc paragraph in `03.02`; console tool, no code |
| 43–45 | Glue, Glue Studio, Glue Data Quality | Coded `03.02` |
| 46 | CloudWatch metrics | Coded `05.01` |
| 47–48 | Transcribe + hands-on | Coded `03.03` |
| 49–50 | Comprehend + hands-on | Coded `03.04` (NLP) + `04.02` (PII) |
| 51 | Comprehend + Lambda + Bedrock | Coded `03.04` routing + `04.02` pipeline |
| 52 | Comprehend Medical | Coded `03.04` (+ PHI in `04.02`) |
| 53 | Intro to OpenSearch in GenAI | Skipped: article intro |
| 54–59 | OpenSearch Service, index mgmt, performance, Serverless, vector store tuning | Coded `02.02` |

## Change log
- 2026-11-13 · Created the 1A tree (rules, manifests, base projects, foundation Terraform); 17 concepts from lectures 1–59 in progress
