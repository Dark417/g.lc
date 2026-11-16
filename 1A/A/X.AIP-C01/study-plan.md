# AWS AIP-C01 28 天学习计划 / 28-Day Study Plan — AWS Certified Generative AI Developer – Professional

## 目录 / Index

- **中文**
  - [0. 怎么用这个文件](#zh-0)
  - [1. 考试速览](#zh-1)
  - [2. 四周总览](#zh-2)
  - [3. 每日模板](#zh-3)
  - [4. 28 天计划](#zh-4)
  - [5. 考纲全图（技能 → 天）](#zh-5)
  - [6. 每周检查点](#zh-6)
  - [7. 落后了怎么办](#zh-7)
- **English**
  - [0. How to use this file](#en-0)
  - [1. Exam at a glance](#en-1)
  - [2. Four-week overview](#en-2)
  - [3. Daily template](#en-3)
  - [4. The 28 days](#en-4)
  - [5. Full syllabus map (skill → day)](#en-5)
  - [6. Weekly checkpoints](#en-6)
  - [7. If you fall behind](#en-7)
- [References](#refs)

---

<a id="zh-0"></a>

## 0. 怎么用这个文件

- 每天对应一组**官方技能编号**（例如 1.4.2）。
  - 编号来自 AWS 官方考纲，一共 5 个域、20 个任务、98 个技能。
- 每天做完，在 [§5 考纲全图](#zh-5) 里给对应技能打勾，并自评 1–5 分。
  - 1 = 没听过；3 = 能解释；5 = 能在场景题里选对并说出为什么。
- 每周末跑一次 [§6 检查点](#zh-6)，看是否按计划推进。
- **前提：**
  - 每天 3 小时，28 天连续，约 84 小时。
  - 这 4 周 AIP 是唯一主线。
    - 如果同时学 CCAR-F，每天再加 1–1.5 小时，或把本计划拉长到约 6 周。
  - 你已经在第 1 周学 Bedrock —— D1–D2 正好对上。
- 技能描述是我的简写；原文以 AWS 官方考纲为准。

---

<a id="zh-1"></a>

## 1. 考试速览

| 项目 | 内容                                                                     |
| ---- | ------------------------------------------------------------------------ |
| 题目 | 65 scored + 10 unscored                                                  |
| 题型 | multiple choice（4 选 1）；multiple response（5 个以上选项，全对才得分） |
| 及格 | 750 / 1000，compensatory scoring（不要求每个域都及格）                   |
| 时长 | 第三方来源说 180 或 205 分钟 —— 预约时核实                               |
| 不考 | model development and training、advanced ML、feature engineering         |

| 域                                              | 权重 | 约多少题 | 本计划天数               |
| ----------------------------------------------- | ---- | -------- | ------------------------ |
| D1 FM Integration, Data Management & Compliance | 31%  | ~20      | 8 天（D1–D8）            |
| D2 Implementation & Integration                 | 26%  | ~17      | 6 天（D9–D14）           |
| D3 AI Safety, Security & Governance             | 20%  | ~13      | 3 天（D15–D17）          |
| D4 Operational Efficiency & Optimization        | 12%  | ~8       | 3 天（D18–D20）          |
| D5 Testing, Validation & Troubleshooting        | 11%  | ~7       | 2 天（D23–D24）          |
| 模拟考 + 复盘 + 考试                            | —    | —        | 6 天（D21–D22、D25–D28） |

---

<a id="zh-2"></a>

## 2. 四周总览

```
W1  D1–D7   ███ D1 FM integration：Bedrock、model selection、customization、data pipelines、vector stores、retrieval、prompt engineering
W2  D8–D14  ███ D1 复盘 → D2 implementation：agents、deployment、enterprise integration、FM APIs、app patterns
W3  D15–D21 ███ D3 safety & governance → D4 cost / performance / monitoring → 第 1 次完整模拟考
W4  D22–D28 ███ 复盘 → D5 evaluation & troubleshooting → 模拟考 #2、#3 → 考试
```

---

<a id="zh-3"></a>

## 3. 每日模板（3 小时）

| 块   | 时长    | 做什么                                 |
| ---- | ------- | -------------------------------------- |
| A 学 | 90 分钟 | Udemy 对应章节（1.5 倍速）+ 官方文档   |
| B 做 | 60 分钟 | console 或代码 lab；产出当天的"产出物" |
| C 测 | 30 分钟 | 10–15 道当天主题的练习题 + 写错题本    |

- 错题本格式："我选了 X 因为……；正确是 Y 因为……；区分点是……"。
- 模拟考那天：A + B 合并做完整考试，C 做初步复盘。

---

<a id="zh-4"></a>

## 4. 28 天计划

### W1 —— D1 FM Integration（31%）

| 天  | 主题                               | 技能                      | 重点服务 / 概念                                                                                                                                                                                   | 产出物（做完的标准）                                                                 |
| --- | ---------------------------------- | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| D1  | Bedrock basics + baseline          | 1.1.1、1.2.1、1.3.3       | Model families, model access, Converse API, inference params, on-demand calls; Bedrock request JSON                                                                                               | 用 Converse API 调两个模型并对比输出；official practice set 做基线分                 |
| D2  | Model selection + resilience       | 1.2.2、1.2.3              | AppConfig / Lambda / API Gateway to switch models; cross-Region inference; Step Functions circuit breaker; graceful degradation                                                                   | 一张 "model switch + failover" 架构图                                                |
| D3  | Customization + lifecycle + design | 1.1.2、1.1.3、1.2.4       | Fine-tuning, continued pretraining, distillation, custom model import; SageMaker LoRA / adapters; Model Registry; rollback; Well-Architected GenAI Lens                                           | 决策表：什么时候用 RAG / prompting / fine-tuning / distillation                      |
| D4  | Data pipelines for FMs             | 1.3.1、1.3.2、1.3.4       | Glue Data Quality, Data Wrangler, Lambda validation; multimodal (Transcribe, SageMaker Processing, Bedrock multimodal); Comprehend entity extraction                                              | 一张 validate → process → enhance 流程图                                             |
| D5  | Vector stores                      | 1.4.1–1.4.5、1.5.3        | Knowledge Bases; OpenSearch (Neural plugin, sharding, multi-index); Aurora pgvector; DynamoDB metadata; S3 metadata; incremental sync, scheduled refresh                                          | 建一个 Knowledge Base；vector store 选型表                                           |
| D6  | Retrieval mechanisms               | 1.5.1、1.5.2、1.5.4–1.5.6 | Chunking: fixed / hierarchical / semantic; Titan embeddings; hybrid search; Bedrock reranker models; query expansion / decomposition; retrieval via function calling and MCP                      | 同一份文档用两种 chunking 对比检索结果；RAG 决策表（chunking × store × search type） |
| D7  | Prompt engineering + governance    | 1.6.1–1.6.6               | Prompt Management (templates, parameters, approval); Guardrails; DynamoDB conversation history; Comprehend intent recognition; Prompt Flows; CloudTrail / CloudWatch Logs audit; chain-of-thought | 在 Prompt Management 里建一个带版本的 template；**W1 检查点**（见 §6）               |

### W2 —— D1 复盘 + D2 Implementation & Integration（26%）

| 天  | 主题                                          | 技能                | 重点服务 / 概念                                                                                                                                                                                                   | 产出物                                                    |
| --- | --------------------------------------------- | ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| D8  | D1 review                                     | 全部 D1             | 重做错题；补 §5 里自评 ≤2 的技能                                                                                                                                                                                  | 30 道 D1 混合题；更新 3 张决策表                          |
| D9  | Agents I: build                               | 2.1.1、2.1.6、2.1.7 | Bedrock Agents (action groups, OpenAPI, Lambda, return-of-control, memory); Strands Agents; Agent Squad; MCP (stateless Lambda / ECS MCP servers, MCP clients)                                                    | 一个带 1 个 action group 的 Bedrock Agent                 |
| D10 | Agents II: reasoning + safety + collaboration | 2.1.2–2.1.5         | ReAct / chain-of-thought with Step Functions; stop conditions, Lambda timeouts, IAM boundaries, circuit breakers; multi-model coordination / ensembles; human-in-the-loop (Step Functions + API Gateway feedback) | 带 human approval 步骤的 Step Functions 流程图            |
| D11 | Deployment strategies                         | 2.2.1–2.2.3         | Lambda on-demand vs Bedrock provisioned throughput vs SageMaker endpoints; container deployment (memory, GPU, token capacity); smaller models; API-based model cascading                                          | 部署选型表：traffic shape × latency × cost                |
| D12 | Enterprise integration                        | 2.3.1–2.3.5         | Event-driven architecture, legacy APIs, EventBridge, API Gateway microservices; identity federation, RBAC, least privilege; Outposts / Wavelength for data residency; CodePipeline / CodeBuild; GenAI gateway     | 一张 "GenAI gateway + CI/CD" 企业架构图                   |
| D13 | FM API integration                            | 2.4.1–2.4.4         | Bedrock APIs + SDKs, SQS async; streaming (WebSockets, SSE, API Gateway chunked transfer); exponential backoff, rate limiting, fallback, X-Ray; static / dynamic / metrics-based routing                          | 写一个带 backoff retry + fallback model 的 streaming 调用 |
| D14 | App patterns + dev tools                      | 2.5.1–2.5.6         | API Gateway streaming, token limits, timeout retries; Amplify, OpenAPI, Prompt Flows; Bedrock Data Automation; Q Developer; prompt chaining; CloudWatch Logs Insights                                             | **W2 检查点**                                             |

### W3 —— D3 Safety & Governance（20%）+ D4 Efficiency（12%）

| 天  | 主题                                  | 技能                      | 重点服务 / 概念                                                                                                                                                                                                                                                                      | 产出物                                                         |
| --- | ------------------------------------- | ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------- |
| D15 | Input / output safety + hallucination | 3.1.1–3.1.3               | Guardrails: content filters, denied topics, word filters, PII filters, contextual grounding, automated reasoning; Step Functions + Lambda custom moderation; KB grounding; JSON Schema structured output; text-to-SQL                                                                | 配一个 Guardrail，测通过 / 拦截各 3 个例子                     |
| D16 | Defense in depth + data privacy       | 3.1.4、3.1.5、3.2.1–3.2.3 | Comprehend pre-filter, Lambda post-processing, API Gateway response filtering; prompt injection / jailbreak detection, adversarial testing; VPC endpoints, IAM, Lake Formation; Macie, Comprehend PII, data masking, S3 Lifecycle                                                    | 一张 layered defense 图（input → model → output）              |
| D17 | Governance + responsible AI           | 3.3.1–3.3.4、3.4.1–3.4.3  | SageMaker model cards; Glue lineage, Data Catalog; CloudTrail; misuse / drift / bias monitoring, token-level redaction; agent tracing for transparency; Prompt Management + Flows A/B for fairness                                                                                   | compliance checklist；**30 道 D3 题**                          |
| D18 | Cost optimization                     | 4.1.1–4.1.4               | Token estimation, context pruning, prompt compression, response limits; tiered models by query complexity; batching, capacity planning, provisioned throughput; semantic caching, request hashing, prompt caching                                                                    | cost lever 表（按省钱多少排序）                                |
| D19 | Performance optimization              | 4.2.1–4.2.6               | Latency-optimized models, pre-computation, parallel requests, streaming; index optimization, query preprocessing, hybrid search custom scoring; batch inference, concurrent invocations; temperature / top-k / top-p; capacity planning, auto-scaling                                | latency breakdown 图：retrieval / prefill / generation / tools |
| D20 | Monitoring                            | 4.3.1–4.3.6               | CloudWatch: token usage, hallucination rate, response quality; model invocation logs; anomaly detection for token bursts / response drift; cost anomalies; tool-call and multi-agent observability; vector store operations; golden datasets, output diffing, reasoning-path tracing | 一个 dashboard 的指标清单；**30 道 D4 题**                     |
| D21 | **完整模拟考 #1**                     | 全部                      | 计时、一次做完                                                                                                                                                                                                                                                                       | 各域分数；**W3 检查点**                                        |

### W4 —— D5 Testing & Troubleshooting（11%）+ 模拟考 + 考试

| 天  | 主题                                                     | 技能          | 重点服务 / 概念                                                                                                                                                                                                                                                                                 | 产出物                                                         |
| --- | -------------------------------------------------------- | ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| D22 | Review mock #1                                           | 最弱的 2 个域 | 每个选项都复盘，包括做对的                                                                                                                                                                                                                                                                      | 错题本；补 §5 里 ≤2 分的技能                                   |
| D23 | Evaluation systems                                       | 5.1.1–5.1.9   | Bedrock Model Evaluation (automatic / human / LLM-as-a-judge); RAG evaluation; A/B, canary testing; feedback and annotation; regression testing, automated quality gates; agent evaluation (task completion, tool usage); reporting; deployment validation (hallucination rate, semantic drift) | 一张 pre-release eval gate 流程图                              |
| D24 | Troubleshooting                                          | 5.2.1–5.2.5   | Context window overflow, truncation, dynamic chunking; API error logging, request validation; prompt testing, version comparison; retrieval diagnostics (embedding quality, drift, chunking fixes); CloudWatch Logs, X-Ray, schema validation                                                   | troubleshooting 决策树：symptom → cause → fix；**30 道 D5 题** |
| D25 | **完整模拟考 #2**（新题）                                | 全部          | 计时                                                                                                                                                                                                                                                                                            | 分数 + 复盘                                                    |
| D26 | Service comparison sheet + 弱项                          | 全部          | 对照官方 in-scope services 清单，每一对写 "when X instead of Y"                                                                                                                                                                                                                                 | 速查表                                                         |
| D27 | **完整模拟考 #3**（新题，或 AWS official practice exam） | 全部          | 计时；门槛检查                                                                                                                                                                                                                                                                                  | 考 / 不考                                                      |
| D28 | **考试** 或 轻复习 + 改约                                | —             | 没过门槛就只看错题本和速查表，约下一个时间                                                                                                                                                                                                                                                      | 结果                                                           |

---

<a id="zh-5"></a>

## 5. 考纲全图（技能 → 天）

- 打勾列：做完写 ✓；自评列：1–5。

### D1 FM Integration, Data Management & Compliance（31%）

| 技能                                              | 简述                                                     | 关键服务 / 概念                                                                   | 天  | ✓   | 自评 |
| ------------------------------------------------- | -------------------------------------------------------- | --------------------------------------------------------------------------------- | --- | --- | ---- |
| **1.1 Analyze requirements and design solutions** |                                                          |                                                                                   |     |     |      |
| 1.1.1                                             | Architecture aligned to business + technical constraints | Model choice, integration patterns, deployment strategies                         | D1  |     |      |
| 1.1.2                                             | Proof of concept for feasibility, performance, value     | Bedrock                                                                           | D3  |     |      |
| 1.1.3                                             | Standardized components for reuse                        | Well-Architected GenAI Lens                                                       | D3  |     |      |
| **1.2 Select and configure FMs**                  |                                                          |                                                                                   |     |     |      |
| 1.2.1                                             | Assess and choose FMs per use case                       | Benchmarks, capability, limitations                                               | D1  |     |      |
| 1.2.2                                             | Switch models / providers without code changes           | Lambda, API Gateway, AppConfig                                                    | D2  |     |      |
| 1.2.3                                             | Keep running through service disruptions                 | Circuit breaker, cross-Region inference, graceful degradation                     | D2  |     |      |
| 1.2.4                                             | Customized model deployment + lifecycle                  | SageMaker, LoRA, Model Registry, rollback, retirement                             | D3  |     |      |
| **1.3 Data validation and processing pipelines**  |                                                          |                                                                                   |     |     |      |
| 1.3.1                                             | Data quality validation                                  | Glue Data Quality, Data Wrangler, Lambda, CloudWatch                              | D4  |     |      |
| 1.3.2                                             | Process text, image, audio, tabular                      | Bedrock multimodal, SageMaker Processing, Transcribe                              | D4  |     |      |
| 1.3.3                                             | Format inputs per model requirements                     | Bedrock request JSON, conversation format                                         | D1  |     |      |
| 1.3.4                                             | Improve input quality                                    | Bedrock reformatting, Comprehend entities, Lambda normalization                   | D4  |     |      |
| **1.4 Vector stores**                             |                                                          |                                                                                   |     |     |      |
| 1.4.1                                             | Vector store architecture                                | KB hierarchy, OpenSearch Neural, RDS + S3, DynamoDB                               | D5  |     |      |
| 1.4.2                                             | Metadata framework for precision                         | S3 metadata, custom attributes, tags                                              | D5  |     |      |
| 1.4.3                                             | High-performance vector stores                           | OpenSearch sharding, multi-index, hierarchical indexing                           | D5  |     |      |
| 1.4.4                                             | Connect external sources                                 | Document systems, knowledge bases, internal wikis                                 | D5  |     |      |
| 1.4.5                                             | Keep vector data current                                 | Incremental updates, change detection, auto sync, scheduled refresh               | D5  |     |      |
| **1.5 Retrieval mechanisms**                      |                                                          |                                                                                   |     |     |      |
| 1.5.1                                             | Document chunking                                        | Bedrock chunking, fixed / hierarchical                                            | D6  |     |      |
| 1.5.2                                             | Choose and configure embeddings                          | Titan embeddings, Lambda batch generation                                         | D6  |     |      |
| 1.5.3                                             | Deploy vector search                                     | OpenSearch, Aurora pgvector, KB managed store                                     | D5  |     |      |
| 1.5.4                                             | Improve relevance                                        | Semantic search, hybrid search, rerankers                                         | D6  |     |      |
| 1.5.5                                             | Query handling                                           | Query expansion, decomposition, transformation                                    | D6  |     |      |
| 1.5.6                                             | Consistent retrieval access                              | Function calling, MCP clients, standard APIs                                      | D6  |     |      |
| **1.6 Prompt engineering and governance**         |                                                          |                                                                                   |     |     |      |
| 1.6.1                                             | Instruction frameworks to control behavior               | Prompt Management roles, Guardrails, templates                                    | D7  |     |      |
| 1.6.2                                             | Interactive systems that keep context                    | Step Functions clarification, Comprehend intent, DynamoDB history                 | D7  |     |      |
| 1.6.3                                             | Prompt management + governance                           | Parameterized templates, approvals, S3 template repo, CloudTrail, CloudWatch Logs | D7  |     |      |
| 1.6.4                                             | Prompt quality assurance                                 | Lambda output checks, Step Functions edge cases, CloudWatch regression            | D7  |     |      |
| 1.6.5                                             | Iterative prompt refinement                              | Structured inputs, output format, CoT, feedback loops                             | D7  |     |      |
| 1.6.6                                             | Complex prompt systems                                   | Prompt Flows, conditional branching, reusable components, pre/post-processing     | D7  |     |      |

### D2 Implementation & Integration（26%）

| 技能                                         | 简述                                        | 关键服务 / 概念                                                                      | 天  | ✓   | 自评 |
| -------------------------------------------- | ------------------------------------------- | ------------------------------------------------------------------------------------ | --- | --- | ---- |
| **2.1 Agentic AI and tool integration**      |                                             |                                                                                      |     |     |      |
| 2.1.1                                        | Autonomous systems with memory + state      | Strands Agents, Agent Squad, MCP                                                     | D9  |     |      |
| 2.1.2                                        | Step-by-step reasoning for complex problems | Step Functions, ReAct, CoT                                                           | D10 |     |      |
| 2.1.3                                        | Safeguarded workflows                       | Stop conditions, Lambda timeouts, IAM boundaries, circuit breakers                   | D10 |     |      |
| 2.1.4                                        | Multi-model coordination                    | Specialized FMs, ensemble aggregation, model selection                               | D10 |     |      |
| 2.1.5                                        | Human collaboration                         | Step Functions approval, API Gateway feedback                                        | D10 |     |      |
| 2.1.6                                        | Reliable tool integration                   | Strands custom behaviors, standard function defs, Lambda error handling + validation | D9  |     |      |
| 2.1.7                                        | Model extension frameworks                  | Stateless Lambda MCP servers, ECS MCP servers, MCP client libraries                  | D9  |     |      |
| **2.2 Deployment strategies**                |                                             |                                                                                      |     |     |      |
| 2.2.1                                        | Deploy per app needs                        | Lambda on-demand, provisioned throughput, SageMaker endpoints                        | D11 |     |      |
| 2.2.2                                        | LLM-specific deployment issues              | Containers (memory, GPU, token capacity), loading strategies                         | D11 |     |      |
| 2.2.3                                        | Balance performance vs resources            | Right-size model, smaller models, API cascading                                      | D11 |     |      |
| **2.3 Enterprise integration**               |                                             |                                                                                      |     |     |      |
| 2.3.1                                        | Connect to existing enterprise systems      | Legacy APIs, event-driven, data sync                                                 | D12 |     |      |
| 2.3.2                                        | Add GenAI to existing apps                  | API Gateway microservices, Lambda webhooks, EventBridge                              | D12 |     |      |
| 2.3.3                                        | Secure access frameworks                    | Identity federation, RBAC, least privilege                                           | D12 |     |      |
| 2.3.4                                        | Cross-jurisdiction compliance               | Outposts, Wavelength, secure cloud-to-on-prem routing                                | D12 |     |      |
| 2.3.5                                        | CI/CD + GenAI gateway                       | CodePipeline, CodeBuild, automated tests, central abstraction layer                  | D12 |     |      |
| **2.4 FM API integration**                   |                                             |                                                                                      |     |     |      |
| 2.4.1                                        | Flexible model interaction                  | Bedrock APIs, SDKs, SQS, API Gateway request validation                              | D13 |     |      |
| 2.4.2                                        | Real-time interaction                       | Streaming APIs, WebSockets, SSE, chunked transfer                                    | D13 |     |      |
| 2.4.3                                        | Resilience                                  | Exponential backoff, rate limiting, fallback, X-Ray                                  | D13 |     |      |
| 2.4.4                                        | Intelligent routing                         | Static routes, Step Functions dynamic routing, metrics-based, request transforms     | D13 |     |      |
| **2.5 App integration patterns + dev tools** |                                             |                                                                                      |     |     |      |
| 2.5.1                                        | GenAI-specific API interfaces               | API Gateway streaming, token limits, timeout retries                                 | D14 |     |      |
| 2.5.2                                        | Accessible AI interfaces                    | Amplify, OpenAPI, Prompt Flows                                                       | D14 |     |      |
| 2.5.3                                        | Business system enhancements                | Lambda CRM, Step Functions doc processing, Bedrock Data Automation                   | D14 |     |      |
| 2.5.4                                        | Developer productivity                      | Q Developer, AI component testing                                                    | D14 |     |      |
| 2.5.5                                        | Advanced GenAI apps                         | Strands, Agent Squad, Step Functions agent patterns, prompt chaining                 | D14 |     |      |
| 2.5.6                                        | Faster troubleshooting                      | CloudWatch Logs Insights, X-Ray, Q Developer                                         | D14 |     |      |

### D3 AI Safety, Security & Governance（20%）

| 技能                              | 简述                          | 关键服务 / 概念                                                                                       | 天  | ✓   | 自评 |
| --------------------------------- | ----------------------------- | ----------------------------------------------------------------------------------------------------- | --- | --- | ---- |
| **3.1 Input and output safety**   |                               |                                                                                                       |     |     |      |
| 3.1.1                             | Block harmful inputs          | Guardrails, Step Functions + Lambda moderation, real-time validation                                  | D15 |     |      |
| 3.1.2                             | Block harmful outputs         | Guardrails on responses, toxicity evals, text-to-SQL                                                  | D15 |     |      |
| 3.1.3                             | Reduce hallucinations         | KB grounding, confidence scoring, semantic similarity, JSON Schema                                    | D15 |     |      |
| 3.1.4                             | Defense in depth              | Comprehend pre-filter, Guardrails, Lambda post-processing, API Gateway filtering                      | D16 |     |      |
| 3.1.5                             | Adversarial threat detection  | Prompt-injection / jailbreak detection, sanitization, safety classifiers, automated adversarial tests | D16 |     |      |
| **3.2 Data security and privacy** |                               |                                                                                                       |     |     |      |
| 3.2.1                             | Protected AI environments     | VPC endpoints, IAM, Lake Formation, CloudWatch                                                        | D16 |     |      |
| 3.2.2                             | Protect sensitive data        | Comprehend, Macie PII, Bedrock privacy features, Guardrails, S3 Lifecycle                             | D16 |     |      |
| 3.2.3                             | Privacy while keeping utility | Masking, anonymization, Comprehend PII, Guardrails                                                    | D16 |     |      |
| **3.3 Governance and compliance** |                               |                                                                                                       |     |     |      |
| 3.3.1                             | Compliance frameworks         | SageMaker model cards, Glue lineage, metadata tags, CloudWatch Logs decision logs                     | D17 |     |      |
| 3.3.2                             | Data source tracking          | Glue Data Catalog, source tags, CloudTrail                                                            | D17 |     |      |
| 3.3.3                             | Organizational governance     | Align with policies, regulations, responsible-AI principles                                           | D17 |     |      |
| 3.3.4                             | Continuous monitoring + audit | Misuse / drift / violation detection, bias drift, alerts, token-level redaction                       | D17 |     |      |
| **3.4 Responsible AI**            |                               |                                                                                                       |     |     |      |
| 3.4.1                             | Transparency                  | Reasoning displays, confidence metrics, source attribution, agent tracing                             | D17 |     |      |
| 3.4.2                             | Fairness evaluation           | CloudWatch fairness metrics, Prompt Management / Flows A/B, LLM-as-judge                              | D17 |     |      |
| 3.4.3                             | Policy-compliant systems      | Policy-based Guardrails, model cards, Lambda compliance checks                                        | D17 |     |      |

### D4 Operational Efficiency & Optimization（12%）

| 技能                             | 简述                           | 关键服务 / 概念                                                                                | 天  | ✓   | 自评 |
| -------------------------------- | ------------------------------ | ---------------------------------------------------------------------------------------------- | --- | --- | ---- |
| **4.1 Cost optimization**        |                                |                                                                                                |     |     |      |
| 4.1.1                            | Token efficiency               | Token estimation, context pruning, prompt compression, response limits                         | D18 |     |      |
| 4.1.2                            | Cost-aware model selection     | Tiering by complexity, price-performance measurement                                           | D18 |     |      |
| 4.1.3                            | Resource utilization           | Batching, capacity planning, auto-scaling, provisioned throughput                              | D18 |     |      |
| 4.1.4                            | Caching                        | Semantic cache, result fingerprinting, edge cache, request hashing, prompt caching             | D18 |     |      |
| **4.2 Performance optimization** |                                |                                                                                                |     |     |      |
| 4.2.1                            | Latency-cost tradeoffs         | Pre-computation, latency-optimized models, parallel requests, streaming, benchmarks            | D19 |     |      |
| 4.2.2                            | Retrieval performance          | Index optimization, query preprocessing, hybrid scoring                                        | D19 |     |      |
| 4.2.3                            | Throughput                     | Token processing, batch inference, concurrent invocation management                            | D19 |     |      |
| 4.2.4                            | Use-case tuning                | Model params, A/B tests, temperature / top-k / top-p                                           | D19 |     |      |
| 4.2.5                            | Resource allocation            | Token capacity planning, utilization monitoring, auto-scaling                                  | D19 |     |      |
| 4.2.6                            | System performance             | API call profiling, vector query optimization, LLM latency reduction                           | D19 |     |      |
| **4.3 Monitoring**               |                                |                                                                                                |     |     |      |
| 4.3.1                            | Holistic observability         | Ops metrics, tracing, FM interaction tracing, business dashboards                              | D20 |     |      |
| 4.3.2                            | GenAI-specific monitoring      | CloudWatch token / hallucination / quality; invocation logs; anomaly detection; cost anomalies | D20 |     |      |
| 4.3.3                            | Actionable insights            | Dashboards, compliance monitoring, audit logs, user interaction tracking                       | D20 |     |      |
| 4.3.4                            | Tool performance               | Call patterns, tool-call observability, multi-agent tracking                                   | D20 |     |      |
| 4.3.5                            | Vector store operations        | Vector DB monitoring, automated index optimization, data quality checks                        | D20 |     |      |
| 4.3.6                            | GenAI-specific troubleshooting | Golden datasets for hallucinations, output diffing, reasoning-path tracing                     | D20 |     |      |

### D5 Testing, Validation & Troubleshooting（11%）

| 技能                       | 简述                         | 关键服务 / 概念                                                                  | 天  | ✓   | 自评 |
| -------------------------- | ---------------------------- | -------------------------------------------------------------------------------- | --- | --- | ---- |
| **5.1 Evaluation systems** |                              |                                                                                  |     |     |      |
| 5.1.1                      | Assessment beyond classic ML | Relevance, factual accuracy, consistency, fluency                                | D23 |     |      |
| 5.1.2                      | Find optimal configurations  | Bedrock Model Evaluations, A/B, canary, multi-model, cost-performance            | D23 |     |      |
| 5.1.3                      | User-centered evaluation     | Feedback UI, ratings, annotation workflows                                       | D23 |     |      |
| 5.1.4                      | Quality assurance process    | Continuous eval, regression tests, automated quality gates                       | D23 |     |      |
| 5.1.5                      | Multi-perspective evaluation | RAG eval, LLM-as-judge, human feedback                                           | D23 |     |      |
| 5.1.6                      | Retrieval quality testing    | Relevance scoring, context matching, retrieval latency                           | D23 |     |      |
| 5.1.7                      | Agent performance            | Completion rate, tool use, Bedrock Agent evals, reasoning quality                | D23 |     |      |
| 5.1.8                      | Stakeholder reporting        | Visualizations, automated reports, model comparisons                             | D23 |     |      |
| 5.1.9                      | Deployment validation        | Synthetic user flows, hallucination rate, semantic drift, consistency checks     | D23 |     |      |
| **5.2 Troubleshooting**    |                              |                                                                                  |     |     |      |
| 5.2.1                      | Content handling             | Context overflow, dynamic chunking, truncation analysis                          | D24 |     |      |
| 5.2.2                      | API integration issues       | Error logging, request validation, response analysis                             | D24 |     |      |
| 5.2.3                      | Prompt issues                | Prompt test frameworks, version comparison, systematic refinement                | D24 |     |      |
| 5.2.4                      | Retrieval issues             | Relevance analysis, embedding quality, drift, chunking fixes, search performance | D24 |     |      |
| 5.2.5                      | Prompt maintenance           | Template tests, CloudWatch Logs, X-Ray, schema validation                        | D24 |     |      |

---

<a id="zh-6"></a>

## 6. 每周检查点

| 时间           | 检查什么                      | 达标线                            | 没达标怎么办                |
| -------------- | ----------------------------- | --------------------------------- | --------------------------- |
| W1 末（D7）    | D1 技能自评 + 30 道 D1 题     | 正确率 ≥70%；D1 技能 ≥80% 自评 ≥3 | D8 全天补 D1                |
| W2 末（D14）   | D2 技能自评 + 30 道 D2 题     | 正确率 ≥70%                       | 从 D18–D19 各挤 1 小时补 D2 |
| W3 末（D21）   | 完整模拟考 #1                 | 总分 ≥70%，没有域 <60%            | D22 修最弱的 2 个域         |
| W4（D25、D27） | 完整模拟考 #2、#3（都是新题） | **连续 2 次 ≥80%，没有域 <70%**   | 推迟考试 1 周（见 §7）      |

- "新题" = 没做过的题。重复刷同一套，分数上升只说明记住了。
- 你 DVA 是 750 险过，这次门槛定在 80%。

---

<a id="zh-7"></a>

## 7. 落后了怎么办

- 落后 1 天：当周 C 块（30 分钟做题）减半，补上。
- 落后 2–3 天：砍掉 D26 速查表那天，并入 D22。
- 落后 4 天以上：把考试推迟 1 周，在第 5 周做一次"复盘 + 模拟考 #4"。
- 不要砍的：D21、D25、D27 三次完整模拟考 —— 它们是唯一能证明你准备好了的东西。

---

---

# English Version

<a id="en-0"></a>

## 0. How to use this file

- Each day maps to a set of **official skill IDs** (for example 1.4.2).
  - IDs come from the AWS exam guide: 5 domains, 20 tasks, 98 skills.
- When you finish a day, tick its skills in [§5 syllabus map](#en-5) and rate yourself 1–5.
  - 1 = never heard of it; 3 = can explain it; 5 = can pick the right answer in a scenario and say why.
- At each week's end, run the [§6 checkpoint](#en-6) to see whether you're on track.
- **Assumptions:**
  - 3 h/day, 28 consecutive days, ~84 h.
  - AIP is the only main track for these 4 weeks.
    - If you run CCAR-F in parallel, add 1–1.5 h/day, or stretch this plan to ~6 weeks.
  - You're already in week 1 on Bedrock — D1–D2 match that.
- Skill descriptions are my shorthand; the AWS exam guide wording is authoritative.

---

<a id="en-1"></a>

## 1. Exam at a glance

| Item         | Detail                                                                      |
| ------------ | --------------------------------------------------------------------------- |
| Questions    | 65 scored + 10 unscored                                                     |
| Types        | Multiple choice (1 of 4); multiple response (5+ options, all must be right) |
| Pass         | 750 / 1000, compensatory (no per-domain pass required)                      |
| Time         | Third-party sources say 180 or 205 min — verify when booking                |
| Out of scope | Model development and training, advanced ML, feature engineering            |

| Domain                                          | Weight | ~Questions | Days in this plan         |
| ----------------------------------------------- | ------ | ---------- | ------------------------- |
| D1 FM Integration, Data Management & Compliance | 31%    | ~20        | 8 days (D1–D8)            |
| D2 Implementation & Integration                 | 26%    | ~17        | 6 days (D9–D14)           |
| D3 AI Safety, Security & Governance             | 20%    | ~13        | 3 days (D15–D17)          |
| D4 Operational Efficiency & Optimization        | 12%    | ~8         | 3 days (D18–D20)          |
| D5 Testing, Validation & Troubleshooting        | 11%    | ~7         | 2 days (D23–D24)          |
| Mocks + review + exam                           | —      | —          | 6 days (D21–D22, D25–D28) |

---

<a id="en-2"></a>

## 2. Four-week overview

```
W1  D1–D7   ███ D1 FM integration: Bedrock, model choice, customization, data, vector stores, retrieval, prompts
W2  D8–D14  ███ D1 review → D2 implementation: agents, deployment, enterprise integration, APIs, app patterns
W3  D15–D21 ███ D3 safety & governance → D4 cost/performance/monitoring → full mock #1
W4  D22–D28 ███ Review → D5 evaluation & troubleshooting → mocks #2, #3 → exam
```

---

<a id="en-3"></a>

## 3. Daily template (3 h)

| Block   | Time   | What                                                    |
| ------- | ------ | ------------------------------------------------------- |
| A Learn | 90 min | Matching Udemy section (1.5×) + official docs           |
| B Build | 60 min | Console or code lab; produce the day's output           |
| C Test  | 30 min | 10–15 practice questions on the day's topic + error log |

- Error log format: "I picked X because…; correct is Y because…; the tell is…".
- Mock days: A + B become one full exam; C is a first-pass review.

---

<a id="en-4"></a>

## 4. The 28 days

### W1 — D1 FM Integration (31%)

| Day | Topic                              | Skills                    | Key services / concepts                                                                                                                                                           | Output (done when)                                                                              |
| --- | ---------------------------------- | ------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| D1  | Bedrock basics + baseline          | 1.1.1, 1.2.1, 1.3.3       | Model families, model access, Converse API, inference params, on-demand calls; Bedrock request JSON                                                                               | Call two models via Converse and compare; baseline score on the official practice set           |
| D2  | Model choice + resilience          | 1.2.2, 1.2.3              | AppConfig / Lambda / API Gateway to switch models; cross-Region inference; Step Functions circuit breaker; graceful degradation                                                   | One "model switch + failover" architecture diagram                                              |
| D3  | Customization + lifecycle + design | 1.1.2, 1.1.3, 1.2.4       | Fine-tuning, continued pretraining, distillation, custom import; SageMaker LoRA/adapters; Model Registry; rollback; Well-Architected GenAI Lens                                   | Decision table: when RAG / prompting / fine-tune / distill                                      |
| D4  | Data pipelines for FMs             | 1.3.1, 1.3.2, 1.3.4       | Glue Data Quality, Data Wrangler, Lambda validation; multimodal (Transcribe, SageMaker Processing, Bedrock multimodal); Comprehend entities                                       | One validate → process → enhance flow diagram                                                   |
| D5  | Vector stores                      | 1.4.1–1.4.5, 1.5.3        | Knowledge Bases; OpenSearch (Neural plugin, sharding, multi-index); Aurora pgvector; DynamoDB metadata; S3 metadata; incremental sync, scheduled refresh                          | Build one Knowledge Base; vector store selection table                                          |
| D6  | Retrieval mechanisms               | 1.5.1, 1.5.2, 1.5.4–1.5.6 | Chunking: fixed / hierarchical / semantic; Titan embeddings; hybrid search; Bedrock reranker models; query expansion / decomposition; retrieval via function calling and MCP      | Compare two chunking strategies on one doc; RAG decision table (chunking × store × search type) |
| D7  | Prompt engineering + governance    | 1.6.1–1.6.6               | Prompt Management (templates, params, approval); Guardrails; DynamoDB conversation history; Comprehend intent; Prompt Flows; CloudTrail / CloudWatch Logs audit; chain-of-thought | One versioned template in Prompt Management; **W1 checkpoint** (§6)                             |

### W2 — D1 review + D2 Implementation & Integration (26%)

| Day | Topic                                         | Skills              | Key services / concepts                                                                                                                                                                         | Output                                                     |
| --- | --------------------------------------------- | ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| D8  | D1 review                                     | All D1              | Redo wrong answers; fill skills rated ≤2 in §5                                                                                                                                                  | 30 mixed D1 Qs; update the 3 decision tables               |
| D9  | Agents I: build                               | 2.1.1, 2.1.6, 2.1.7 | Bedrock Agents (action groups, OpenAPI, Lambda, return-of-control, memory); Strands Agents; Agent Squad; MCP (stateless Lambda / ECS MCP servers, MCP clients)                                  | A Bedrock Agent with one action group                      |
| D10 | Agents II: reasoning + safety + collaboration | 2.1.2–2.1.5         | ReAct / CoT with Step Functions; stop conditions, Lambda timeouts, IAM boundaries, circuit breakers; multi-model coordination / ensembles; human review (Step Functions + API Gateway feedback) | Step Functions flow diagram with a human-approval step     |
| D11 | Deployment strategies                         | 2.2.1–2.2.3         | Lambda on-demand vs Bedrock provisioned throughput vs SageMaker endpoints; container deployment (memory, GPU, token capacity); smaller models; API-based cascading                              | Deployment selection table: traffic shape × latency × cost |
| D12 | Enterprise integration                        | 2.3.1–2.3.5         | Event-driven, legacy APIs, EventBridge, API Gateway microservices; identity federation, RBAC, least privilege; Outposts / Wavelength for residency; CodePipeline / CodeBuild; GenAI gateway     | One "GenAI gateway + CI/CD" enterprise diagram             |
| D13 | FM API integration                            | 2.4.1–2.4.4         | Bedrock APIs + SDKs, SQS async; streaming (WebSockets, SSE, API Gateway chunked transfer); exponential backoff, rate limiting, fallback, X-Ray; static / dynamic / metrics-based routing        | A streaming call with backoff retry + fallback model       |
| D14 | App patterns + dev tools                      | 2.5.1–2.5.6         | API Gateway streaming, token limits, timeout retries; Amplify, OpenAPI, Prompt Flows; Bedrock Data Automation; Q Developer; prompt chaining; CloudWatch Logs Insights                           | **W2 checkpoint**                                          |

### W3 — D3 Safety & Governance (20%) + D4 Efficiency (12%)

| Day | Topic                                 | Skills                    | Key services / concepts                                                                                                                                                                                                                                              | Output                                                      |
| --- | ------------------------------------- | ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| D15 | Input / output safety + hallucination | 3.1.1–3.1.3               | Guardrails: content filters, denied topics, word filters, PII, contextual grounding, automated reasoning; Step Functions + Lambda custom moderation; KB grounding; JSON Schema output; text-to-SQL                                                                   | Configure a Guardrail; test 3 pass and 3 block cases        |
| D16 | Defense in depth + data privacy       | 3.1.4, 3.1.5, 3.2.1–3.2.3 | Comprehend pre-filter, Lambda post-processing, API Gateway response filtering; prompt-injection / jailbreak detection, adversarial testing; VPC endpoints, IAM, Lake Formation; Macie, Comprehend PII, masking, S3 Lifecycle                                         | One layered-defense diagram (input → model → output)        |
| D17 | Governance + responsible AI           | 3.3.1–3.3.4, 3.4.1–3.4.3  | SageMaker model cards; Glue lineage, Data Catalog; CloudTrail; misuse / drift / bias monitoring, token-level redaction; agent tracing for transparency; Prompt Management + Flows A/B for fairness                                                                   | Compliance checklist; **30 D3 Qs**                          |
| D18 | Cost optimization                     | 4.1.1–4.1.4               | Token estimation, context pruning, prompt compression, response limits; tiered models by complexity; batching, capacity planning, provisioned throughput; semantic caching, request hashing, prompt caching                                                          | Cost-lever table ranked by savings                          |
| D19 | Performance optimization              | 4.2.1–4.2.6               | Latency-optimized models, pre-computation, parallel requests, streaming; index optimization, query preprocessing, hybrid scoring; batch inference, concurrent invocations; temperature / top-k / top-p; capacity planning, auto-scaling                              | Latency breakdown: retrieval / prefill / generation / tools |
| D20 | Monitoring                            | 4.3.1–4.3.6               | CloudWatch: token usage, hallucination rate, response quality; model invocation logs; anomaly detection for token bursts / drift; cost anomalies; tool-call and multi-agent observability; vector store ops; golden datasets, output diffing, reasoning-path tracing | Metric list for one dashboard; **30 D4 Qs**                 |
| D21 | **Full mock #1**                      | All                       | Timed, one sitting                                                                                                                                                                                                                                                   | Per-domain scores; **W3 checkpoint**                        |

### W4 — D5 Testing & Troubleshooting (11%) + mocks + exam

| Day | Topic                                                   | Skills            | Key services / concepts                                                                                                                                                                                                                                                      | Output                                                    |
| --- | ------------------------------------------------------- | ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| D22 | Review mock #1                                          | 2 weakest domains | Review every option, including ones you got right                                                                                                                                                                                                                            | Error log; fill skills rated ≤2 in §5                     |
| D23 | Evaluation systems                                      | 5.1.1–5.1.9       | Bedrock Model Evaluation (automatic / human / LLM-as-judge); RAG evaluation; A/B, canary; feedback and annotation; regression tests, automated quality gates; agent evaluation (completion, tool use); reporting; deployment validation (hallucination rate, semantic drift) | One "pre-release eval gate" flow diagram                  |
| D24 | Troubleshooting                                         | 5.2.1–5.2.5       | Context overflow, truncation, dynamic chunking; API error logging, request validation; prompt testing, version comparison; retrieval diagnostics (embedding quality, drift, chunking fixes); CloudWatch Logs, X-Ray, schema validation                                       | Troubleshooting tree: symptom → cause → fix; **30 D5 Qs** |
| D25 | **Full mock #2** (fresh)                                | All               | Timed                                                                                                                                                                                                                                                                        | Score + review                                            |
| D26 | Service comparison sheet + weak areas                   | All               | Walk the official in-scope service list; for each pair, "when X instead of Y"                                                                                                                                                                                                | Cheat sheet                                               |
| D27 | **Full mock #3** (fresh, or AWS official practice exam) | All               | Timed; gate check                                                                                                                                                                                                                                                            | Go / no-go                                                |
| D28 | **Exam** or light review + rebook                       | —                 | If gate missed: error log and cheat sheet only; book the next slot                                                                                                                                                                                                           | Result                                                    |

---

<a id="en-5"></a>

## 5. Full syllabus map (skill → day)

- Tick column: write ✓ when done; rating column: 1–5.

### D1 FM Integration, Data Management & Compliance (31%)

| Skill                                             | Short                                                    | Key services / concepts                                                           | Day | ✓   | Rating |
| ------------------------------------------------- | -------------------------------------------------------- | --------------------------------------------------------------------------------- | --- | --- | ------ |
| **1.1 Analyze requirements and design solutions** |                                                          |                                                                                   |     |     |        |
| 1.1.1                                             | Architecture aligned to business + technical constraints | Model choice, integration patterns, deployment strategies                         | D1  |     |        |
| 1.1.2                                             | Proof of concept for feasibility, performance, value     | Bedrock                                                                           | D3  |     |        |
| 1.1.3                                             | Standardized components for reuse                        | Well-Architected GenAI Lens                                                       | D3  |     |        |
| **1.2 Select and configure FMs**                  |                                                          |                                                                                   |     |     |        |
| 1.2.1                                             | Assess and choose FMs per use case                       | Benchmarks, capability, limitations                                               | D1  |     |        |
| 1.2.2                                             | Switch models / providers without code changes           | Lambda, API Gateway, AppConfig                                                    | D2  |     |        |
| 1.2.3                                             | Keep running through service disruptions                 | Circuit breaker, cross-Region inference, graceful degradation                     | D2  |     |        |
| 1.2.4                                             | Customized model deployment + lifecycle                  | SageMaker, LoRA, Model Registry, rollback, retirement                             | D3  |     |        |
| **1.3 Data validation and processing pipelines**  |                                                          |                                                                                   |     |     |        |
| 1.3.1                                             | Data quality validation                                  | Glue Data Quality, Data Wrangler, Lambda, CloudWatch                              | D4  |     |        |
| 1.3.2                                             | Process text, image, audio, tabular                      | Bedrock multimodal, SageMaker Processing, Transcribe                              | D4  |     |        |
| 1.3.3                                             | Format inputs per model requirements                     | Bedrock request JSON, conversation format                                         | D1  |     |        |
| 1.3.4                                             | Improve input quality                                    | Bedrock reformatting, Comprehend entities, Lambda normalization                   | D4  |     |        |
| **1.4 Vector stores**                             |                                                          |                                                                                   |     |     |        |
| 1.4.1                                             | Vector store architecture                                | KB hierarchy, OpenSearch Neural, RDS + S3, DynamoDB                               | D5  |     |        |
| 1.4.2                                             | Metadata framework for precision                         | S3 metadata, custom attributes, tags                                              | D5  |     |        |
| 1.4.3                                             | High-performance vector stores                           | OpenSearch sharding, multi-index, hierarchical indexing                           | D5  |     |        |
| 1.4.4                                             | Connect external sources                                 | Document systems, knowledge bases, internal wikis                                 | D5  |     |        |
| 1.4.5                                             | Keep vector data current                                 | Incremental updates, change detection, auto sync, scheduled refresh               | D5  |     |        |
| **1.5 Retrieval mechanisms**                      |                                                          |                                                                                   |     |     |        |
| 1.5.1                                             | Document chunking                                        | Bedrock chunking, fixed / hierarchical                                            | D6  |     |        |
| 1.5.2                                             | Choose and configure embeddings                          | Titan embeddings, Lambda batch generation                                         | D6  |     |        |
| 1.5.3                                             | Deploy vector search                                     | OpenSearch, Aurora pgvector, KB managed store                                     | D5  |     |        |
| 1.5.4                                             | Improve relevance                                        | Semantic search, hybrid search, rerankers                                         | D6  |     |        |
| 1.5.5                                             | Query handling                                           | Query expansion, decomposition, transformation                                    | D6  |     |        |
| 1.5.6                                             | Consistent retrieval access                              | Function calling, MCP clients, standard APIs                                      | D6  |     |        |
| **1.6 Prompt engineering and governance**         |                                                          |                                                                                   |     |     |        |
| 1.6.1                                             | Instruction frameworks to control behavior               | Prompt Management roles, Guardrails, templates                                    | D7  |     |        |
| 1.6.2                                             | Interactive systems that keep context                    | Step Functions clarification, Comprehend intent, DynamoDB history                 | D7  |     |        |
| 1.6.3                                             | Prompt management + governance                           | Parameterized templates, approvals, S3 template repo, CloudTrail, CloudWatch Logs | D7  |     |        |
| 1.6.4                                             | Prompt quality assurance                                 | Lambda output checks, Step Functions edge cases, CloudWatch regression            | D7  |     |        |
| 1.6.5                                             | Iterative prompt refinement                              | Structured inputs, output format, CoT, feedback loops                             | D7  |     |        |
| 1.6.6                                             | Complex prompt systems                                   | Prompt Flows, conditional branching, reusable components, pre/post-processing     | D7  |     |        |

### D2 Implementation & Integration (26%)

| Skill                                        | Short                                       | Key services / concepts                                                              | Day | ✓   | Rating |
| -------------------------------------------- | ------------------------------------------- | ------------------------------------------------------------------------------------ | --- | --- | ------ |
| **2.1 Agentic AI and tool integration**      |                                             |                                                                                      |     |     |        |
| 2.1.1                                        | Autonomous systems with memory + state      | Strands Agents, Agent Squad, MCP                                                     | D9  |     |        |
| 2.1.2                                        | Step-by-step reasoning for complex problems | Step Functions, ReAct, CoT                                                           | D10 |     |        |
| 2.1.3                                        | Safeguarded workflows                       | Stop conditions, Lambda timeouts, IAM boundaries, circuit breakers                   | D10 |     |        |
| 2.1.4                                        | Multi-model coordination                    | Specialized FMs, ensemble aggregation, model selection                               | D10 |     |        |
| 2.1.5                                        | Human collaboration                         | Step Functions approval, API Gateway feedback                                        | D10 |     |        |
| 2.1.6                                        | Reliable tool integration                   | Strands custom behaviors, standard function defs, Lambda error handling + validation | D9  |     |        |
| 2.1.7                                        | Model extension frameworks                  | Stateless Lambda MCP servers, ECS MCP servers, MCP client libraries                  | D9  |     |        |
| **2.2 Deployment strategies**                |                                             |                                                                                      |     |     |        |
| 2.2.1                                        | Deploy per app needs                        | Lambda on-demand, provisioned throughput, SageMaker endpoints                        | D11 |     |        |
| 2.2.2                                        | LLM-specific deployment issues              | Containers (memory, GPU, token capacity), loading strategies                         | D11 |     |        |
| 2.2.3                                        | Balance performance vs resources            | Right-size model, smaller models, API cascading                                      | D11 |     |        |
| **2.3 Enterprise integration**               |                                             |                                                                                      |     |     |        |
| 2.3.1                                        | Connect to existing enterprise systems      | Legacy APIs, event-driven, data sync                                                 | D12 |     |        |
| 2.3.2                                        | Add GenAI to existing apps                  | API Gateway microservices, Lambda webhooks, EventBridge                              | D12 |     |        |
| 2.3.3                                        | Secure access frameworks                    | Identity federation, RBAC, least privilege                                           | D12 |     |        |
| 2.3.4                                        | Cross-jurisdiction compliance               | Outposts, Wavelength, secure cloud-to-on-prem routing                                | D12 |     |        |
| 2.3.5                                        | CI/CD + GenAI gateway                       | CodePipeline, CodeBuild, automated tests, central abstraction layer                  | D12 |     |        |
| **2.4 FM API integration**                   |                                             |                                                                                      |     |     |        |
| 2.4.1                                        | Flexible model interaction                  | Bedrock APIs, SDKs, SQS, API Gateway request validation                              | D13 |     |        |
| 2.4.2                                        | Real-time interaction                       | Streaming APIs, WebSockets, SSE, chunked transfer                                    | D13 |     |        |
| 2.4.3                                        | Resilience                                  | Exponential backoff, rate limiting, fallback, X-Ray                                  | D13 |     |        |
| 2.4.4                                        | Intelligent routing                         | Static routes, Step Functions dynamic routing, metrics-based, request transforms     | D13 |     |        |
| **2.5 App integration patterns + dev tools** |                                             |                                                                                      |     |     |        |
| 2.5.1                                        | GenAI-specific API interfaces               | API Gateway streaming, token limits, timeout retries                                 | D14 |     |        |
| 2.5.2                                        | Accessible AI interfaces                    | Amplify, OpenAPI, Prompt Flows                                                       | D14 |     |        |
| 2.5.3                                        | Business system enhancements                | Lambda CRM, Step Functions doc processing, Bedrock Data Automation                   | D14 |     |        |
| 2.5.4                                        | Developer productivity                      | Q Developer, AI component testing                                                    | D14 |     |        |
| 2.5.5                                        | Advanced GenAI apps                         | Strands, Agent Squad, Step Functions agent patterns, prompt chaining                 | D14 |     |        |
| 2.5.6                                        | Faster troubleshooting                      | CloudWatch Logs Insights, X-Ray, Q Developer                                         | D14 |     |        |

### D3 AI Safety, Security & Governance (20%)

| Skill                             | Short                         | Key services / concepts                                                                               | Day | ✓   | Rating |
| --------------------------------- | ----------------------------- | ----------------------------------------------------------------------------------------------------- | --- | --- | ------ |
| **3.1 Input and output safety**   |                               |                                                                                                       |     |     |        |
| 3.1.1                             | Block harmful inputs          | Guardrails, Step Functions + Lambda moderation, real-time validation                                  | D15 |     |        |
| 3.1.2                             | Block harmful outputs         | Guardrails on responses, toxicity evals, text-to-SQL                                                  | D15 |     |        |
| 3.1.3                             | Reduce hallucinations         | KB grounding, confidence scoring, semantic similarity, JSON Schema                                    | D15 |     |        |
| 3.1.4                             | Defense in depth              | Comprehend pre-filter, Guardrails, Lambda post-processing, API Gateway filtering                      | D16 |     |        |
| 3.1.5                             | Adversarial threat detection  | Prompt-injection / jailbreak detection, sanitization, safety classifiers, automated adversarial tests | D16 |     |        |
| **3.2 Data security and privacy** |                               |                                                                                                       |     |     |        |
| 3.2.1                             | Protected AI environments     | VPC endpoints, IAM, Lake Formation, CloudWatch                                                        | D16 |     |        |
| 3.2.2                             | Protect sensitive data        | Comprehend, Macie PII, Bedrock privacy features, Guardrails, S3 Lifecycle                             | D16 |     |        |
| 3.2.3                             | Privacy while keeping utility | Masking, anonymization, Comprehend PII, Guardrails                                                    | D16 |     |        |
| **3.3 Governance and compliance** |                               |                                                                                                       |     |     |        |
| 3.3.1                             | Compliance frameworks         | SageMaker model cards, Glue lineage, metadata tags, CloudWatch Logs decision logs                     | D17 |     |        |
| 3.3.2                             | Data source tracking          | Glue Data Catalog, source tags, CloudTrail                                                            | D17 |     |        |
| 3.3.3                             | Organizational governance     | Align with policies, regulations, responsible-AI principles                                           | D17 |     |        |
| 3.3.4                             | Continuous monitoring + audit | Misuse / drift / violation detection, bias drift, alerts, token-level redaction                       | D17 |     |        |
| **3.4 Responsible AI**            |                               |                                                                                                       |     |     |        |
| 3.4.1                             | Transparency                  | Reasoning displays, confidence metrics, source attribution, agent tracing                             | D17 |     |        |
| 3.4.2                             | Fairness evaluation           | CloudWatch fairness metrics, Prompt Management / Flows A/B, LLM-as-judge                              | D17 |     |        |
| 3.4.3                             | Policy-compliant systems      | Policy-based Guardrails, model cards, Lambda compliance checks                                        | D17 |     |        |

### D4 Operational Efficiency & Optimization (12%)

| Skill                            | Short                          | Key services / concepts                                                                        | Day | ✓   | Rating |
| -------------------------------- | ------------------------------ | ---------------------------------------------------------------------------------------------- | --- | --- | ------ |
| **4.1 Cost optimization**        |                                |                                                                                                |     |     |        |
| 4.1.1                            | Token efficiency               | Token estimation, context pruning, prompt compression, response limits                         | D18 |     |        |
| 4.1.2                            | Cost-aware model selection     | Tiering by complexity, price-performance measurement                                           | D18 |     |        |
| 4.1.3                            | Resource utilization           | Batching, capacity planning, auto-scaling, provisioned throughput                              | D18 |     |        |
| 4.1.4                            | Caching                        | Semantic cache, result fingerprinting, edge cache, request hashing, prompt caching             | D18 |     |        |
| **4.2 Performance optimization** |                                |                                                                                                |     |     |        |
| 4.2.1                            | Latency-cost tradeoffs         | Pre-computation, latency-optimized models, parallel requests, streaming, benchmarks            | D19 |     |        |
| 4.2.2                            | Retrieval performance          | Index optimization, query preprocessing, hybrid scoring                                        | D19 |     |        |
| 4.2.3                            | Throughput                     | Token processing, batch inference, concurrent invocation management                            | D19 |     |        |
| 4.2.4                            | Use-case tuning                | Model params, A/B tests, temperature / top-k / top-p                                           | D19 |     |        |
| 4.2.5                            | Resource allocation            | Token capacity planning, utilization monitoring, auto-scaling                                  | D19 |     |        |
| 4.2.6                            | System performance             | API call profiling, vector query optimization, LLM latency reduction                           | D19 |     |        |
| **4.3 Monitoring**               |                                |                                                                                                |     |     |        |
| 4.3.1                            | Holistic observability         | Ops metrics, tracing, FM interaction tracing, business dashboards                              | D20 |     |        |
| 4.3.2                            | GenAI-specific monitoring      | CloudWatch token / hallucination / quality; invocation logs; anomaly detection; cost anomalies | D20 |     |        |
| 4.3.3                            | Actionable insights            | Dashboards, compliance monitoring, audit logs, user interaction tracking                       | D20 |     |        |
| 4.3.4                            | Tool performance               | Call patterns, tool-call observability, multi-agent tracking                                   | D20 |     |        |
| 4.3.5                            | Vector store operations        | Vector DB monitoring, automated index optimization, data quality checks                        | D20 |     |        |
| 4.3.6                            | GenAI-specific troubleshooting | Golden datasets for hallucinations, output diffing, reasoning-path tracing                     | D20 |     |        |

### D5 Testing, Validation & Troubleshooting (11%)

| Skill                      | Short                        | Key services / concepts                                                          | Day | ✓   | Rating |
| -------------------------- | ---------------------------- | -------------------------------------------------------------------------------- | --- | --- | ------ |
| **5.1 Evaluation systems** |                              |                                                                                  |     |     |        |
| 5.1.1                      | Assessment beyond classic ML | Relevance, factual accuracy, consistency, fluency                                | D23 |     |        |
| 5.1.2                      | Find optimal configurations  | Bedrock Model Evaluations, A/B, canary, multi-model, cost-performance            | D23 |     |        |
| 5.1.3                      | User-centered evaluation     | Feedback UI, ratings, annotation workflows                                       | D23 |     |        |
| 5.1.4                      | Quality assurance process    | Continuous eval, regression tests, automated quality gates                       | D23 |     |        |
| 5.1.5                      | Multi-perspective evaluation | RAG eval, LLM-as-judge, human feedback                                           | D23 |     |        |
| 5.1.6                      | Retrieval quality testing    | Relevance scoring, context matching, retrieval latency                           | D23 |     |        |
| 5.1.7                      | Agent performance            | Completion rate, tool use, Bedrock Agent evals, reasoning quality                | D23 |     |        |
| 5.1.8                      | Stakeholder reporting        | Visualizations, automated reports, model comparisons                             | D23 |     |        |
| 5.1.9                      | Deployment validation        | Synthetic user flows, hallucination rate, semantic drift, consistency checks     | D23 |     |        |
| **5.2 Troubleshooting**    |                              |                                                                                  |     |     |        |
| 5.2.1                      | Content handling             | Context overflow, dynamic chunking, truncation analysis                          | D24 |     |        |
| 5.2.2                      | API integration issues       | Error logging, request validation, response analysis                             | D24 |     |        |
| 5.2.3                      | Prompt issues                | Prompt test frameworks, version comparison, systematic refinement                | D24 |     |        |
| 5.2.4                      | Retrieval issues             | Relevance analysis, embedding quality, drift, chunking fixes, search performance | D24 |     |        |
| 5.2.5                      | Prompt maintenance           | Template tests, CloudWatch Logs, X-Ray, schema validation                        | D24 |     |        |

---

<a id="en-6"></a>

## 6. Weekly checkpoints

| When          | Check                          | Pass line                                | If missed                           |
| ------------- | ------------------------------ | ---------------------------------------- | ----------------------------------- |
| End W1 (D7)   | D1 self-ratings + 30 D1 Qs     | ≥70% correct; ≥80% of D1 skills rated ≥3 | Spend all of D8 on D1               |
| End W2 (D14)  | D2 self-ratings + 30 D2 Qs     | ≥70% correct                             | Borrow 1 h each from D18–D19 for D2 |
| End W3 (D21)  | Full mock #1                   | ≥70% overall, no domain <60%             | D22 fixes the 2 weakest domains     |
| W4 (D25, D27) | Full mocks #2, #3 (both fresh) | **≥80% twice in a row, no domain <70%**  | Push the exam 1 week (§7)           |

- "Fresh" = questions you haven't seen. Rising scores on a repeated set only show memory.
- Your DVA was a narrow 750 pass; this time the bar is 80%.

---

<a id="en-7"></a>

## 7. If you fall behind

- 1 day behind: halve block C (30-min questions) that week to catch up.
- 2–3 days behind: drop D26 (cheat sheet) and fold it into D22.
- 4+ days behind: push the exam 1 week; use week 5 for "review + mock #4".
- Never drop: the three full mocks (D21, D25, D27) — they're the only proof you're ready.

---

<a id="refs"></a>

## References

1. AWS AIP-C01 exam guide (overview, weights) — https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01.html
2. Domain 1 tasks and skills — https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01-domain1.html
3. Domain 2 tasks and skills — https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01-domain2.html
4. Domain 3 tasks and skills — https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01-domain3.html
5. Domain 4 tasks and skills — https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01-domain4.html
6. Domain 5 tasks and skills — https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01-domain5.html
7. In-scope AWS services — https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/aip-01-in-scope-services.html
8. Amazon Bedrock user guide — https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html
