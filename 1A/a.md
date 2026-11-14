# a — AI Knowledge Map (1A manifest)

- Master index of the 1A knowledge + code tree
- Mirror: claude.ai Project `1D/A/AMap.md` (keep identical; this file is master — [AGENTS.md §5](AGENTS.md#5-manifest-and-project-mirror))
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
  - ✅ base_* (5 modules) Providers, network + Bedrock endpoint, KMS, IAM, billing alarm, data bucket (Terraform only)
- 01 Bedrock core and prompting
  - ✅ [C] 01bedrock.01converse Bedrock Converse API — A-010
  - ✅ [C] 01bedrock.02customization Model customization (fine-tuning, LoRA) — A-011
  - ✅ [C] 01bedrock.03prompt-management Prompt management — A-012
  - ✅ [C] 01bedrock.04prompt-flows Prompt flows — A-013
  - ✅ [C] 01bedrock.05prompt-engineering Prompt engineering and structured output — A-014
- 02 RAG and vector stores
  - ✅ [C] 02rag.01embeddings Embeddings and vector search — A-020
  - ✅ [C] 02rag.02opensearch OpenSearch as a vector store — A-021
  - ✅ [C] 02rag.03chunking Chunking — A-022
  - ✅ [C] 02rag.04knowledge-bases Bedrock Knowledge Bases — A-023
- 03 Data for GenAI
  - ✅ [C] 03data.01data-automation Bedrock Data Automation — A-030
  - ✅ [C] 03data.02glue-data-quality Glue Data Quality — A-031
  - ✅ [C] 03data.03transcribe Transcribe — A-032
  - ✅ [C] 03data.04comprehend Comprehend — A-033
- 04 Safety, PII, and evaluation
  - ✅ [C] 04safety.01guardrails Bedrock Guardrails — A-040
  - ✅ [C] 04safety.02pii-redaction PII detection and redaction — A-041
  - ✅ [C] 04safety.03evaluations Evaluations (RAG, model, guardrail) — A-042
- 05 Operations and observability
  - ✅ [C] 05ops.01observability GenAI observability — A-050
- 06 Agents · 07 Integration and orchestration · 08 Governance and security
  - ⬜ planned (lectures 97+) — backlog A-060..A-080

---

## 00 Foundation
- ✅ base_* (5 modules) (Terraform only)
  - Base files `versions.tf` `backend.tf` `providers.tf` `variables.tf` `locals.tf` `main.tf` `outputs.tf` — aws provider, `local.prefix = "a-<env>"`, default tags; envs `local` `dev` `uat` `prod`
  - `modules/base_network/` — VPC, private subnets, app SG, S3/DynamoDB gateway endpoints, `bedrock-runtime` PrivateLink endpoint
  - `modules/base_kms/` — CMK `alias/a-<env>-data`
  - `modules/base_iam/` — app role `a-<env>-app`; components attach their own policies
  - `modules/base_billing_alarm/` — SNS alerts + EstimatedCharges alarm (lecture 5)
  - `modules/base_data_bucket/` — shared bucket `a-<env>-ai-data-<account>`, one prefix per component
  - 2026-11-13 · Claude · `terraform validate` passed (Terraform 1.9.8, aws 6.73.0)

## 01 Bedrock core and prompting
- ✅ [C] 01bedrock.01converse Bedrock Converse API — A-010 · lectures 7–10, 22
  - a-md `a-md/01bedrock/01bedrock.01converse.*` · Python `app/<layer>/_01bedrock_01converse.py` · Java `com.lc.a.<layer>._01bedrock_01converse` · TF `modules/01bedrock_01converse/`
- ✅ [C] 01bedrock.02customization Model customization — A-011 · lectures 11–12
  - a-md `a-md/01bedrock/01bedrock.02customization.*` · Python `app/<layer>/_01bedrock_02customization.py` · TF `modules/01bedrock_02customization/`
- ✅ [C] 01bedrock.03prompt-management Prompt management — A-012 · lecture 27
  - a-md `a-md/01bedrock/01bedrock.03prompt-management.*` · Python `app/<layer>/_01bedrock_03prompt_management.py` · TF `modules/01bedrock_03prompt_management/`
- ✅ [C] 01bedrock.04prompt-flows Prompt flows — A-013 · lecture 28
  - a-md `a-md/01bedrock/01bedrock.04prompt-flows.*` · Python `app/<layer>/_01bedrock_04prompt_flows.py` · TF `modules/01bedrock_04prompt_flows/`
- ✅ [C] 01bedrock.05prompt-engineering Prompt engineering and structured output — A-014 · lectures 29–34
  - a-md `a-md/01bedrock/01bedrock.05prompt-engineering.*` · Python `app/<layer>/_01bedrock_05prompt_engineering.py` · no TF (uses 01.01 permissions)

## 02 RAG and vector stores
- ✅ [C] 02rag.01embeddings Embeddings and vector search — A-020 · lectures 13, 14, 20
  - a-md `a-md/02rag/02rag.01embeddings.*` · Python `app/<layer>/_02rag_01embeddings.py` · no TF (uses 01.01 permissions)
- ✅ [C] 02rag.02opensearch OpenSearch as a vector store — A-021 · lectures 17, 53–59
  - a-md `a-md/02rag/02rag.02opensearch.*` · Python `app/<layer>/_02rag_02opensearch.py` · TF `modules/02rag_02opensearch/`
- ✅ [C] 02rag.03chunking Chunking — A-022 · lectures 18–19
  - a-md `a-md/02rag/02rag.03chunking.*` · Python `app/<layer>/_02rag_03chunking.py` · no TF (chunking config lives on the 02.04 data source)
- ✅ [C] 02rag.04knowledge-bases Bedrock Knowledge Bases — A-023 · lectures 15, 16, 21, 38
  - a-md `a-md/02rag/02rag.04knowledge-bases.*` · Python `app/<layer>/_02rag_04knowledge_bases.py` · TF `modules/02rag_04knowledge_bases/`

## 03 Data for GenAI
- ✅ [C] 03data.01data-automation Bedrock Data Automation — A-030 · lectures 38–39
  - a-md `a-md/03data/03data.01data-automation.*` · Python `app/<layer>/_03data_01data_automation.py` · TF `modules/03data_01data_automation/`
- ✅ [C] 03data.02glue-data-quality Glue Data Quality — A-031 · lectures 43–45 (40–42 doc mention)
  - a-md `a-md/03data/03data.02glue-data-quality.*` · Python `app/<layer>/_03data_02glue_data_quality.py` · TF `modules/03data_02glue_data_quality/`
- ✅ [C] 03data.03transcribe Transcribe — A-032 · lectures 47–48
  - a-md `a-md/03data/03data.03transcribe.*` · Python `app/<layer>/_03data_03transcribe.py` · TF `modules/03data_03transcribe/`
- ✅ [C] 03data.04comprehend Comprehend — A-033 · lectures 49–52
  - a-md `a-md/03data/03data.04comprehend.*` · Python `app/<layer>/_03data_04comprehend.py` · TF `modules/03data_04comprehend/`

## 04 Safety, PII, and evaluation
- ✅ [C] 04safety.01guardrails Bedrock Guardrails — A-040 · lectures 23–25, 34
  - a-md `a-md/04safety/04safety.01guardrails.*` · Python `app/<layer>/_04safety_01guardrails.py` · Java `com.lc.a.<layer>._04safety_01guardrails` · TF `modules/04safety_01guardrails/`
- ✅ [C] 04safety.02pii-redaction PII detection and redaction — A-041 · lectures 26, 49–51 (+47 tie-in)
  - a-md `a-md/04safety/04safety.02pii-redaction.*` · Python `app/<layer>/_04safety_02pii_redaction.py` · TF `modules/04safety_02pii_redaction/` (Comprehend async job role)
- ✅ [C] 04safety.03evaluations Evaluations (RAG, model, guardrail) — A-042 · lecture 21 (+190–192 preview)
  - a-md `a-md/04safety/04safety.03evaluations.*` · Python `app/<layer>/_04safety_03evaluations.py` · TF `modules/04safety_03evaluations/`

## 05 Operations and observability
- ✅ [C] 05ops.01observability GenAI observability — A-050 · lecture 46 (+195–206 preview)
  - a-md `a-md/05ops/05ops.01observability.*` · Python `app/<layer>/_05ops_01observability.py` · TF `modules/05ops_01observability/`

## 06–08 Planned groups
- ⬜ 06 Agents — lectures 97–125 (Bedrock Agents, multi-agent, memory, Strands, AgentCore, MCP, HITL, Amazon Quick)
- ⬜ 07 Integration and orchestration — lectures 126–136, 152–187 (caching, cross-region inference, Lambda, API Gateway, Step Functions, AppConfig, queues/events)
- ⬜ 08 Governance and security — lectures 188–234 (tracing, CloudTrail, X-Ray, Lake Formation, IAM, KMS, Macie, Cognito, WAF, VPC/PrivateLink)
- The old 1x backlog items X-027..X-029 (Bedrock, Step Functions + Bedrock, agent SDKs) now belong here

## Lecture map
| Lectures | Concept | Treatment |
|---|---|---|
| 1–4 | Course intro, materials, signup | Skipped: logistics |
| 5 | Billing alarm | Terraform `base_billing_alarm` |
| 6 | Section intro | Skipped: intro |
| 7–10 | Bedrock overview, model access, playground, Converse API | Coded `01bedrock.01converse` |
| 11–12 | Fine-tuning, LoRA | Coded `01bedrock.02customization` (high level: before the model) |
| 13–14 | RAG, vector stores and semantic search | Coded `02rag.01embeddings` |
| 15–16 | Knowledge Bases + hands-on | Coded `02rag.04knowledge-bases` |
| 17 | Don't leave OpenSearch running | Folded into `02rag.02opensearch` (cost) + `base_billing_alarm` alarm |
| 18–19 | Chunking strategies, chunking in Bedrock | Coded `02rag.03chunking` |
| 20 | Optimizing vector store and embeddings | Coded `02rag.01embeddings` |
| 21 | Evaluating RAG performance | Coded `04safety.03evaluations` (+ retrieval side in `02rag.04knowledge-bases`) |
| 22 | Multimodal models and pipelines | Coded in `01bedrock.01converse` (image / document blocks) |
| 23–25 | Guardrails, Automated Reasoning, hands-on | Coded `04safety.01guardrails` |
| 26 | Token-level redaction | Coded `04safety.02pii-redaction` |
| 27 | Prompt Management | Coded `01bedrock.03prompt-management` |
| 28 | Prompt Flows | Coded `01bedrock.04prompt-flows` |
| 29–34 | Structured output, prompt engineering, misuse and bias | Coded `01bedrock.05prompt-engineering` (+ prompt-attack filter in `04safety.01guardrails`) |
| 35 | Enterprise integration | Doc mention in `01bedrock.01converse`; full topic in group 07 |
| 36 | Well-Architected GenAI Lens | Skipped: checklist, no mechanism to code |
| 37 | Section intro | Skipped: intro |
| 38 | Dealing with structured data | Doc in `02rag.04knowledge-bases` (structured KB) + `03data.01data-automation` |
| 39 | Bedrock Data Automation | Coded `03data.01data-automation` |
| 40–42 | SageMaker Data Wrangler + demo | Doc paragraph in `03data.02glue-data-quality`; console tool, no code |
| 43–45 | Glue, Glue Studio, Glue Data Quality | Coded `03data.02glue-data-quality` |
| 46 | CloudWatch metrics | Coded `05ops.01observability` |
| 47–48 | Transcribe + hands-on | Coded `03data.03transcribe` |
| 49–50 | Comprehend + hands-on | Coded `03data.04comprehend` (NLP) + `04safety.02pii-redaction` (PII) |
| 51 | Comprehend + Lambda + Bedrock | Coded `03data.04comprehend` routing + `04safety.02pii-redaction` pipeline |
| 52 | Comprehend Medical | Coded `03data.04comprehend` (+ PHI in `04safety.02pii-redaction`) |
| 53 | Intro to OpenSearch in GenAI | Skipped: article intro |
| 54–59 | OpenSearch Service, index mgmt, performance, Serverless, vector store tuning | Coded `02rag.02opensearch` |

## Change log
- 2026-11-13 · A-090 Restructure: group names, layer-first code (`_GGgroup_CCcomp`), `docs/` → `x-md/` (156 flat files, Python blocks), Terraform project with `envs/` + `modules/`, shared AGENTS.md
- 2026-11-13 · Done: 17 concepts (01.01–05.01), each doc + Python + Terraform where cloud; Java for 01.01 and 04.01; checks: `mvn compile`, compileall + 91-route import, `terraform validate` (20 files, aws 6.73.0)
- 2026-11-13 · Created the 1A tree (rules, manifests, base projects, foundation Terraform); 17 concepts from lectures 1–59 started
