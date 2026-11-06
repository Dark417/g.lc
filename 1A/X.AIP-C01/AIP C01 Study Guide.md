# AIP-C01 学习指南 / Study Guide — AWS GenAI Developer Pro（主线）+ CCAR-F（脉冲副线）

## 目录 / Index

- **中文**
  - [0. 结论](#zh-0)
  - [1. 官方考试指南（先看这个）](#zh-1)
  - [2. 四个考试对比 + 总分（DVA = 100）](#zh-2)
  - [3. 考试地图](#zh-3)
  - [4. 真正要学的东西（分层）](#zh-4)
  - [5. 关键对比表](#zh-5)
  - [6. 题干关键词 → 答案](#zh-6)
  - [7. 全职 4 周计划](#zh-7)
  - [8. CCAR-F 脉冲规则](#zh-8)
  - [9. 报名门槛 + 备考失败模式](#zh-9)
  - [10. 对旧计划的更正](#zh-10)
- **English**
  - [0. Bottom line](#en-0)
  - [1. Official exam guide (read first)](#en-1)
  - [2. Four exams compared + total score (DVA = 100)](#en-2)
  - [3. Exam map](#en-3)
  - [4. What you actually need to learn (tiered)](#en-4)
  - [5. Key comparison tables](#en-5)
  - [6. Question keyword → answer](#en-6)
  - [7. Full-time 4-week plan](#en-7)
  - [8. CCAR-F pulse rules](#en-8)
  - [9. Book-it gate + study failure modes](#en-9)
  - [10. Corrections to the old plan](#en-10)
- [References](#refs)

---

<a id="zh-0"></a>
## 0. 结论

- **难度总分（DVA = 100）：**
  - AIP-C01 ≈ **140**
  - CCAR-F ≈ **75**
  - CCAR-P ≈ **110**
- **全职节奏下：**
  - AIP-C01 → 约 **3–4 周**（约 90–110 小时）。
  - CCAR-F → 脉冲式并行，AIP 考完后 **1 周收尾**。
  - CCAR-P → 以后再说（进 AI 岗位后）。
- **假设：** 全职 = 每天约 6 小时专注，每周 6 天。
  - AIP 主线 ≈ 每周 27 小时。
  - CCAR-F 脉冲 ≤ 每周 6 小时。
- **最关键的一点：**
  - AIP 不是"背服务名"的考试。
  - 是"几个都对的选项里，挑最符合约束的那个"。
  - 所以本指南的核心是 §5 对比表 + §6 关键词表。

---

<a id="zh-1"></a>
## 1. 官方考试指南（先看这个）

- **官方考试指南（主入口）：**
  - https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01.html
- **子页面（逐个打开）：**
  - 域 1–5 任务描述：从主入口的 Topics 进入
  - **In-scope 服务清单**：https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/aip-01-in-scope-services.html
  - Out-of-scope 服务清单：同目录 `aip-01-out-of-scope-services.html`
  - 技术和概念清单：同目录 `ai-professional-01-technologies-concepts.html`
- **认证主页（报名、时长、价格）：**
  - https://aws.amazon.com/certification/certified-generative-ai-developer-professional/
- **考试格式（官方指南）：**
  - 65 道计分题 + 10 道不计分题 = 75 题。
  - 单选（1 对 3 错）+ 多选（5 个以上选项选 2 个以上，全对才得分）。
  - 750 / 1000 及格；补偿式计分（不需要每个域都过）。
- **官方指南没写的：**
  - 时长：第三方来源一致说 GA 版 **180 分钟**；beta 版是 85 题 / 205 分钟。→ 报名页确认。
  - 价格：第三方说 **$300**（AWS Professional 标准价）。→ 报名页确认。
- **官方建议背景：**
  - 2 年以上 AWS / 开源生产应用经验。
  - 1 年 GenAI 实战。
  - 你都满足。
- **明确不考：**
  - 模型开发和训练。
  - 高级 ML 技巧。
  - 数据工程 / 特征工程。

---

<a id="zh-2"></a>
## 2. 四个考试对比 + 总分（DVA = 100）

### 2.1 基本信息

| | **DVA-C02**（已过） | **AIP-C01** | **CCAR-F** | **CCAR-P** |
|---|---|---|---|---|
| 级别 | Associate | Professional | Foundations | Professional |
| 题数 | 65（50 计分） | 75（65 计分） | 60 | 63 |
| 时长 | 130 分钟 | 180 分钟（待核实） | 120 分钟 | 120 分钟 |
| 每题时间 | 2.0 分钟 | 2.4 分钟 | 2.0 分钟 | 1.9 分钟 |
| 及格 | 720 | **750** | 720 | 720 |
| 费用 | $150 | $300（待核实） | $125 | $175 |
| 有效期 | 3 年 | 3 年 | 12 个月 | 12 个月 |
| 风格 | 服务用法 + API 细节 | 约束下选架构 | Agent 架构判断 | 企业级方案判断 |
| 你的备考小时数 | 60–90（业余 2 个月，实际） | **90–110** | 30–45 | 45–60（单独）；AIP + F 之后 25–35 |
| 全职日历时间 | — | **3–4 周** | 脉冲 + 1 周收尾 | 2 周 |

- CCAR-F / P 数字来自你的旧计划；Claude 考试页面再确认一次。

### 2.2 难度打分（每个维度 DVA = 100）

| 维度 | DVA | AIP | CCAR-F | CCAR-P | 为什么 |
|---|---|---|---|---|---|
| 广度（要认识的服务 / 话题） | 100 | 170 | 50 | 80 | AIP in-scope 清单约 120 个服务，含整套 ML 服务；CCAR-F 只考 Claude 一个栈 |
| 判断深度（多个选项都"能用"） | 100 | 160 | 120 | 170 | Pro 级题干长，约束多；CCAR-P 考企业取舍 |
| 考场耐力（题数 × 时长 × 及格线） | 100 | 140 | 90 | 95 | AIP 3 小时 + 750 线；有考生反馈模拟考做不完 |
| 对你的新鲜度 | 100 | 110 | 60 | 130 | AWS 底座你会；Claude Code / MCP 你天天用；治理和干系人是新的 |
| 你的备考小时数 | 100 | 125 | 50 | 70 | 按上表中位数 |
| **总分（平均）** | **100** | **≈140** | **≈75** | **≈110** | |

- 这是我的判断，不是测量值。
  - 用途：排优先级和分配时间。
  - W1 诊断后按真实分数调整。
- **读法：**
  - AIP ≈ DVA 的 1.4 倍 → 全职 3–4 周合理，业余会是 2–3 个月。
  - CCAR-F 比 DVA 简单 → 脉冲式可行，**前提是有模拟考兜底**（见 §8）。

---

<a id="zh-3"></a>
## 3. 考试地图 —— 一个参考架构覆盖五个域

```
                 ┌────────────── D3 安全治理 20% ──────────────┐
                 │ Guardrails · IAM · KMS · PrivateLink · Macie│
用户 ─► API Gateway ─► Lambda / Step Functions ─► Bedrock ──────┤
  (流式 / WebSocket)   (编排、HITL、熔断)     (Converse,       │
                          │                    Agents,          │
        D2 实现集成 26%   │                    AgentCore)       │
                          ▼                       │             │
               ┌──── D1 基础模型 + 数据 31% ────┐ │             │
               │ S3 → 解析 → 分块 → 嵌入 →      │◄┘             │
               │ 向量库 (OpenSearch / pgvector) │               │
               │ 混合检索 · 元数据过滤 · 重排   │               │
               │ Prompt Management / Flows      │               │
               └────────────────────────────────┘               │
                 ┌──── D4 成本性能 12% ────┐  ┌── D5 评测排障 11% ──┐
                 │ 提示缓存 · 路由 · 批量  │  │ Bedrock Evaluations │
                 │ 预置吞吐 · 跨区域推理   │  │ 调用日志 · X-Ray    │
                 └─────────────────────────┘  └─────────────────────┘
```

- 每学一个服务，问自己：它在这张图的哪个框？替代它的是什么？

---

<a id="zh-4"></a>
## 4. 真正要学的东西（分层）

### 4.1 第 0 层 —— 你已经会，只补 GenAI 的差异（约 10% 时间）

| 服务 | 你已会的 | 只需补的 GenAI 差异 |
|---|---|---|
| Lambda | 事件、超时、并发 | 15 分钟上限 → 长 Agent 任务要换 Step Functions；做无状态 MCP 服务器 |
| API Gateway | REST / HTTP、限流 | 流式响应、WebSocket、集成超时上限（核实当前值）、请求校验 |
| SQS / EventBridge / SNS | 异步、解耦 | 异步 FM 调用削峰；文档变更 → 触发 KB 同步 |
| Step Functions | 状态机 | ReAct 循环、停止条件、熔断、`waitForTaskToken` 做人工审批 |
| DynamoDB / ElastiCache | KV、缓存 | 对话历史；语义缓存 |
| IAM / KMS / VPC | 最小权限、加密 | 按模型 ID 限制 `bedrock:InvokeModel`；Bedrock VPC 端点 |
| CloudWatch / X-Ray / CloudTrail | 监控、追踪、审计 | token 指标、模型调用日志、Logs Insights 查提示词 |
| CodePipeline / CodeBuild | CI/CD | 提示词和模型版本也是可部署物；部署前质量门槛 |

### 4.2 第 1 层 —— 必须精通（Bedrock 核心，约 60% 的分）

- **调用（D1/D2/D4）**
  - `InvokeModel` vs `Converse` / `ConverseStream`
    - Converse = 统一接口，换模型不改代码；支持工具调用。
  - 推理参数：temperature、top-p、top-k、max tokens、stop sequences。
  - 调用模式：按需 / 预置吞吐 / 批量 / 跨区域推理配置 / 延迟优化（见 §5.1）。
  - 提示缓存、智能提示路由。
- **Knowledge Bases（D1，最重）**
  - 数据源：S3、网页爬虫、Confluence、SharePoint 等连接器。
  - 解析：默认解析 vs FM 解析 vs Bedrock Data Automation（表格、图片多的 PDF）。
  - 分块：固定大小 / 分层 / 语义 / 不分块 / 自定义 Lambda。
  - 嵌入：Titan Text Embeddings V2（256 / 512 / 1024 维）；维度 = 精度 vs 存储成本。
  - 向量库选项（见 §5.2）。
  - 检索：混合检索、元数据过滤、重排模型、查询分解。
  - `Retrieve` vs `RetrieveAndGenerate`：要自己控制生成就用前者。
  - 同步：数据源变化 → 摄取任务（增量）。
- **Guardrails（D3）**
  - 内容过滤（含提示攻击过滤）、禁止话题、词过滤、敏感信息过滤（PII 屏蔽 / 遮蔽 + 正则）。
  - 上下文事实校验：grounding 阈值 + relevance 阈值 → 防幻觉。
  - 自动推理检查：用形式化规则校验回答。
  - `ApplyGuardrail` API：不调用模型也能单独用（可用于非 Bedrock 模型）。
- **Agent（D2）**
  - Bedrock Agents：action groups（OpenAPI schema vs function details）、Lambda、return-of-control、挂 KB、会话属性、trace。
  - 多 Agent 协作：supervisor 模式。
  - **AgentCore**（已确认在范围内）：Runtime、Gateway、Memory、Identity、Observability、Code Interpreter、Browser。
  - **Strands Agents**、**AWS Agent Squad**（官方指南点名）。
  - **MCP**：Lambda = 无状态轻量工具；ECS = 复杂 / 有状态工具。
- **Prompt Management + Prompt Flows（D1）**
  - 参数化模板、版本、审批流。
  - Flows：顺序链、条件分支、前后处理节点。
- **评测（D5）**
  - Bedrock Evaluations：自动 / 人工 / LLM 评审 / RAG 评测（只检索 vs 检索 + 生成）。
  - Agent 评测：任务完成率、工具使用效果。
  - 黄金集、回归测试、部署质量门槛。
- **可观测（D4/D5）**
  - 模型调用日志（完整请求 / 响应 → S3 / CloudWatch Logs）。
  - CloudWatch 指标：调用数、延迟、输入 / 输出 token、限流。

### 4.3 第 2 层 —— 只要知道"什么时候选它"（一行判断规则）

| 服务 | 判断规则 |
|---|---|
| SageMaker AI 端点 / JumpStart | Bedrock 没有的模型、要自定义容器 / GPU 控制 |
| SageMaker Model Registry | 自定义 / 微调模型的版本和回滚 |
| LoRA / adapters | 微调后低成本部署多个领域版本 |
| Bedrock Custom Model Import | 自己的开源权重想用 Bedrock 的无服务器调用 |
| Comprehend | 实体抽取、意图识别、PII 检测（模型调用前的便宜预处理） |
| Macie | S3 里的 PII 发现（数据入库前） |
| Kendra vs Knowledge Bases | 已有企业搜索 + 丰富连接器 → Kendra；要 RAG 定制化 → KB |
| Q Business / Q Developer | 员工问答助手（买）/ 写代码助手 |
| Lex / Connect | 对话机器人 / 呼叫中心 |
| Textract / Transcribe / Bedrock Data Automation | 文档 OCR / 语音转文字 / 多模态自动抽取 |
| Glue Data Quality / Data Catalog | 数据质量校验 / 数据血缘和来源登记 |
| Lake Formation | 细粒度数据访问控制 |
| A2I (Augmented AI) | 托管的人工复核流程 |
| SageMaker Clarify / Model Monitor | 偏见检测 / 漂移监控 |
| AppConfig | 不改代码切换模型 / 提示词配置 |
| Outposts / Wavelength | 数据必须留在本地 / 边缘低延迟 |
| Amplify | 快速做前端 UI |

### 4.4 第 3 层 —— 概念（不绑服务，题目会换着包装考）

- 检索：分块权衡、嵌入维度、混合检索、重排、查询扩展 / 分解、中间信息丢失。
- 推理模式：ReAct、思维链、提示链、模型级联（小模型先、大模型兜底）。
- 成本：token 估算、上下文裁剪、响应长度限制、语义缓存 vs 精确缓存 vs 提示缓存。
- 可靠性：指数退避 + 抖动、熔断、优雅降级、跨区域。
- 质量：幻觉检测（黄金集、grounding 分数、输出比对）、LLM 评审、漂移。
- 安全：提示注入、越狱、纵深防御（前置过滤 → 模型护栏 → 后置校验）。

### 4.5 跳过

- 模型训练内部原理、SageMaker 训练任务细节。
- 特征工程。
- SageMaker Neo 深入（知道是"边缘编译优化"就够）。

---

<a id="zh-5"></a>
## 5. 关键对比表

### 5.1 Bedrock 调用模式

| 选项 | 是什么 | 优势 | 劣势 | 什么时候选 |
|---|---|---|---|---|
| 按需 | 按 token 付费 | 零承诺，弹性 | 有配额，会被 429 限流 | 流量不稳定、起步阶段 |
| 预置吞吐 | 买模型单元，按小时计费 | 吞吐稳定可预期；自定义模型通常需要它 | 有承诺期，闲置也付钱 | 稳定高流量；部署微调模型 |
| 批量推理 | S3 输入 → 异步任务 → S3 输出 | 支持的模型比按需便宜约 50%（定价页，待核实） | 非实时（小时级） | 离线大批量：摘要、分类、打标 |
| 跨区域推理配置 | 自动把请求路由到多个区域 | 吞吐更高；本区域没有的模型也能用 | 数据会跨区域（合规要看） | 限流 / 区域没有该模型 |
| 延迟优化推理 | 特定模型的低延迟版本 | 首 token 更快 | 只有部分模型 / 区域 | 实时交互、对延迟敏感 |
| 提示缓存 | 缓存重复的提示前缀 | AWS 称缓存部分成本最多降约 90%（待核实） | 只对前缀稳定的提示有效；有 TTL | 长系统提示、多轮同文档问答 |
| 智能提示路由 | 同家族模型间按难度路由 | 自动省钱 | 只在同家族内路由 | 难度差异大的混合流量 |

- **决定变量：** 流量是否可预测 + 是否需要实时。

### 5.2 向量库

| 选项 | 是什么 | 优势 | 劣势 | 什么时候选 |
|---|---|---|---|---|
| OpenSearch Serverless | KB 默认托管向量库 | 混合检索；KB 一键创建 | 有最低 OCU 成本 | 默认选择；要混合检索 |
| OpenSearch Service（托管集群） | 自管集群 + Neural 插件 | 分片、多索引可控 | 运维量大 | 超大规模、要调分片 |
| Aurora PostgreSQL + pgvector | 关系库加向量 | 和业务数据同库；SQL 过滤 | 超大规模性能不如专用引擎 | 已有 Postgres；向量 + 关系联合查询 |
| Neptune Analytics | 图数据库 | GraphRAG：实体关系 | 小众，学习成本 | 多跳关系问题 |
| 第三方（Pinecone、Redis、MongoDB Atlas） | KB 支持的外部库 | 团队已在用 | AWS 外部，额外合规面 | 已有投资 |

- **决定变量：** 要不要混合检索 + 是否已有 Postgres。
- S3 Vectors 不在 in-scope 清单里（2026-10-27 查看）→ 先别花时间。

### 5.3 Agent 编排选项

| 选项 | 是什么 | 优势 | 劣势 | 什么时候选 |
|---|---|---|---|---|
| Step Functions + Converse | 代码定义流程，LLM 填步骤 | 确定性、可审计、易 HITL | 开放式任务写起来僵 | 流程固定（大多数企业场景） |
| Bedrock Agents | 托管 Agent | 最少运维；action groups + KB | 定制有限，较黑盒 | "运维最少"的题干 |
| AgentCore | 托管 Agent 运行时 + 基础设施 | 任意框架；记忆、身份、网关、可观测 | 组件多，要自己组装 | 自带框架（Strands / LangGraph）上生产 |
| Strands Agents | AWS 开源 SDK，模型驱动循环 | 代码少；原生 MCP | 是 SDK，不是托管 | 写自定义 Agent，常配 AgentCore |
| Agent Squad | AWS 开源多 Agent 路由框架 | 意图分类 → 分派到专家 Agent | 偏路由，不是深度协作 | 多个专家 Agent 选一个 |

- **决定变量：** 流程是否在设计时已知。已知 → Step Functions；未知 → Agent。

---

<a id="zh-6"></a>
## 6. 题干关键词 → 答案（考前背这张）

| 题干出现 | 通常答案 |
|---|---|
| "运维开销最小" | 托管 Bedrock 功能（KB、Agents、Guardrails），不自建 |
| "该区域没有这个模型" / "限流" | 跨区域推理配置 |
| "稳定、可预测的大流量" / "部署微调模型" | 预置吞吐 |
| "不需要实时" / "数百万文档" | 批量推理 |
| "不改代码就能换模型" | Converse API + AppConfig |
| "回答要基于来源，减少幻觉" | KB grounding + Guardrails 上下文事实校验 |
| "输出不能含 PII" | Guardrails 敏感信息过滤（遮蔽） |
| "入库前发现 S3 中的 PII" | Macie |
| "调用前便宜地识别实体 / 意图" | Comprehend |
| "人工审批后才执行" | Step Functions `waitForTaskToken` 或 A2I |
| "长的重复系统提示" | 提示缓存 |
| "相同 / 相似问题反复问" | 语义缓存（ElastiCache / OpenSearch） |
| "关键词 + 语义" | 混合检索（OpenSearch） |
| "文档有章节结构" | 分层分块 |
| "文档频繁更新" | 事件驱动增量同步（S3 事件 → 摄取任务） |
| "从结构化数据得到确定结果" | 文本转 SQL，不用 RAG |
| "完整的请求 / 响应分析" | 模型调用日志 |
| "跨服务追踪" | X-Ray |
| "轻量无状态工具" / "复杂有状态工具" | Lambda 上的 MCP / ECS 上的 MCP |
| "数据必须留在本地" | Outposts |
| "评测 RAG 质量" | Bedrock 评测 RAG 评测任务 |

- 规则：每道错题都要能补成这张表的一行。

---

<a id="zh-7"></a>
## 7. 全职 4 周计划

### 7.1 每日模板（约 6 小时）

| 块 | 时长 | 内容 |
|---|---|---|
| A | 2.5 小时 | AIP 深度：文档 + 实验 |
| B | 2 小时 | AIP 课程视频 / 刷题 |
| C | 15 分钟 | 错题本 + 闪卡 |
| P | 0–90 分钟 | CCAR-F 脉冲（可选，见 §8） |

- D7 = 休息。
- 视频 1.5 倍速；一到演示就停下来自己做。

### 7.2 W1 —— Bedrock 核心 + RAG（D1，31%）

| 天 | A 块 | B 块 | 产出 |
|---|---|---|---|
| D1 | 官方指南 → 清单（每个 Skill 一行，自评 1–5） · in-scope 清单过一遍 | Skill Builder 官方练习题做基线 | 清单 + 基线分 |
| D2 | **实验：** boto3 调 `Converse` + 工具调用 + `ConverseStream` | 课程：Bedrock 基础、模型家族、推理参数 | 能跑的脚本 |
| D3 | 调用模式全读一遍 → 用自己的话重写 §5.1 | 课程：调用方式、定价 | 自己版本的 §5.1 |
| D4 | **实验：** S3 上建 KB，两种分块策略，比较检索结果 | 课程：KB I —— 解析、分块、嵌入 | 分块对比笔记 |
| D5 | **实验：** 元数据过滤 + 重排；`Retrieve` vs `RetrieveAndGenerate` | 课程：KB II —— 向量库、混合检索 | 检索笔记 |
| D6 | Prompt Management、Flows、数据校验（Glue DQ、Comprehend） | 30 道 D1 题 → 错题本 | 错题本 v1 |

### 7.3 W2 —— Agent + 集成 + 部署（D2，26%）

| 天 | A 块 | B 块 | 产出 |
|---|---|---|---|
| D1 | **实验：** Bedrock Agent + 1 个 action group + return-of-control | 课程：Bedrock Agents、多 Agent 协作 | Agent 演示 |
| D2 | AgentCore 各组件 · Strands · Agent Squad · MCP（Lambda vs ECS） · **可选实验：** Strands Agent + 1 个 MCP 工具部署到 AgentCore Runtime | 读官方文档（课程可能比这些服务旧） | §5.3 自己版本 |
| D3 | Step Functions 模式：ReAct、停止条件、熔断、任务令牌 HITL · API Gateway 流式 · SQS 异步 · AppConfig | 课程：集成章节 | 模式笔记 |
| D4 | 部署：SageMaker 端点、JumpStart、Model Registry、LoRA、自定义模型导入、模型级联 · Q Developer / Q Business / BDA | 课程：部署章节 | 判断规则表 §4.3 |
| D5 | 40 道 D2 题 → 错题本 | 复盘错题 → 补 §6 | 错题本 |
| D6 | **练习考 #1**（完整计时，诊断用） | 按域复盘 | 各域分数 |

### 7.4 W3 —— 安全、治理、运维、评测（D3 20% + D4 12% + D5 11%）

| 天 | A 块 | B 块 | 产出 |
|---|---|---|---|
| D1 | **实验：** Guardrail（PII 遮蔽 + 事实校验）+ 单独调 `ApplyGuardrail` | 课程：Guardrails | Guardrail 演示 |
| D2 | 安全：VPC 端点、IAM 按模型限制、KMS、Lake Formation、Macie、数据保留 · 治理：模型卡、Glue 血缘、CloudTrail | 课程：安全治理 | 笔记 |
| D3 | 成本 / 性能：token 估算、三种缓存、路由 / 级联、批量、预置容量、推理参数 | 课程：优化章节 | 成本表 |
| D4 | **实验：** 一个 LLM 评审评测任务 · 模型调用日志 → Logs Insights 查询 | 课程：评测、监控 | 评测结果 |
| D5 | 排障：上下文溢出、截断、429 / 配额、检索漂移、嵌入不匹配 | 40 道 D3–D5 题 | 错题本 |
| D6 | **练习考 #2**（新题） | 复盘 | 分数 |

### 7.5 W4 —— 收尾

| 天 | 内容 | 产出 |
|---|---|---|
| D1 | 复盘 #2 · 修补最弱 2 个域 | 错题本 |
| D2 | **练习考 #3**（新题）+ 复盘 | 分数 |
| D3 | 速查表：§6 + 每对 in-scope 相似服务"什么时候 X 不用 Y" | 速查表 |
| D4 | **练习考 #4** 或 AWS 官方练习考 | 分数 |
| D5 | 门槛检查（§9）· 轻度复习 | 考 / 不考 |
| D6 | **参加 AIP-C01**（没过门槛 → 推到 W5.D3） | 结果 |

---

<a id="zh-8"></a>
## 8. CCAR-F 脉冲规则

- **为什么可以脉冲式：**
  - 难度 ≈ 75（低于 DVA）。
  - 大部分是你每天在用的东西（Claude Code、MCP、Agent SDK）。
- **风险（直说）：**
  - 考的是 Claude 特定的默认行为和措辞（CLAUDE.md 层级、`tool_choice`、`stop_reason`、Batches API）。
  - "我天天用"≠"我知道考试要的那个答案"。
  - 没有测量的脉冲 = 永远觉得快准备好了。
- **规则：**
  - 时间：只在 AIP A + B 块之后；每周 ≤ 6 小时。
  - 选题：跟着当周 AIP 主题走（概念只学一次）：
    - W1 → 工具调用、结构化输出（JSON schema + 校验重试）
    - W2 → Agent 循环、子 Agent、hooks、MCP 作用域、Claude Code 配置
    - W3 → 上下文管理、评测、Batches API
  - 研究 / 支线：只在脉冲块里做。
    - 要求：有产出（笔记、仓库里的配置、一个小实验）。
  - 测量：每 2 周做 1 套 CCAR-F 模拟考（20–30 题即可）。
- **AIP 考完后：**
  - 1 周收尾：2 套完整新模拟考 + 门槛 → 参加 CCAR-F。
- **时机：**
  - CCAR-F 有效期 12 个月 → 尽量靠近求职季考。

---

<a id="zh-9"></a>
## 9. 报名门槛 + 备考失败模式

### 9.1 门槛

| 考试 | 什么时候报名 |
|---|---|
| AIP-C01 | 连续 2 套**新**完整练习考 ≥ 80%，没有域 < 70% |
| CCAR-F | 1 套新模拟考 ≥ 85%，每个域 ≥ 75% |

- "新" = 没见过的题。重复刷同一套 = 测记忆。
- DVA 750 是险过；这次 Pro 线是 750 → 门槛定高。

### 9.2 失败模式

| 失败 | 触发 | 怎么发现 | 应对 |
|---|---|---|---|
| 知道服务，不会挑 | 只看视频不做题 | 分数卡在 65–70%；错题写"两个都对" | 每道错题补一行 §6 规则 |
| 刷题刷成记忆 | 同一套重复做 | 换新套分数掉 > 10 分 | 只有新题计入门槛 |
| 课程过时 | 视频早于 AgentCore / Strands / Agent Squad 上线 | 课程更新日期早于官方指南 | 这几项只读官方文档 |
| 时间不够 | 3 小时 75 题，Pro 题干长 | 模拟考做不完 | 每题 2.4 分钟；超过 3 分钟标记跳过 |
| 脉冲吃掉主线 | 支线研究很有意思 | 每周时间记录 CCAR-F > 6 小时 | 硬上限；AIP 块先做 |

---

<a id="zh-10"></a>
## 10. 对旧计划的更正

- **AgentCore：** 旧计划写"核实是否在范围内" → **已确认在 in-scope 清单里**。
- **考试时长：** 旧计划写"180 vs 205" → beta 是 85 题 / 205 分钟；GA 是 75 题，第三方一致说 180 分钟。
- **旧计划漏掉的（官方指南点名）：**
  - Strands Agents、AWS Agent Squad、MCP（Lambda vs ECS）。
  - Bedrock Data Automation、Kiro、Amazon Quick。
  - Well-Architected Tool 的 Generative AI Lens。
- **节奏：** 旧计划按每周 18 小时 → AIP 7 周；现在全职 → 3–4 周。

---
---

# English Version

<a id="en-0"></a>
## 0. Bottom line

- **Difficulty score (DVA = 100):**
  - AIP-C01 ≈ **140**
  - CCAR-F ≈ **75**
  - CCAR-P ≈ **110**
- **At full-time pace:**
  - AIP-C01 → about **3–4 weeks** (~90–110 h).
  - CCAR-F → pulse in parallel, then a **1-week closeout** after AIP.
  - CCAR-P → later (once you're in an AI role).
- **Assumption:** full-time = ~6 focused h/day, 6 days/week.
  - AIP main track ≈ 27 h/week.
  - CCAR-F pulse ≤ 6 h/week.
- **The one thing that matters most:**
  - AIP is not a "memorize service names" exam.
  - It's "several options work; pick the one that best fits the constraints."
  - So the core of this guide is the §5 comparison tables + the §6 keyword table.

---

<a id="en-1"></a>
## 1. Official exam guide (read first)

- **Official exam guide (main entry):**
  - https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01.html
- **Sub-pages (open each one):**
  - Domain 1–5 task statements: via Topics on the main page
  - **In-scope services**: https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/aip-01-in-scope-services.html
  - Out-of-scope services: same folder, `aip-01-out-of-scope-services.html`
  - Technologies and concepts: same folder, `ai-professional-01-technologies-concepts.html`
- **Cert home page (booking, length, price):**
  - https://aws.amazon.com/certification/certified-generative-ai-developer-professional/
- **Exam format (official guide):**
  - 65 scored + 10 unscored = 75 questions.
  - Multiple choice (1 right, 3 wrong) + multiple response (pick 2+ of 5+; all must be right).
  - Pass 750 / 1000; compensatory scoring (no per-domain pass needed).
- **Not in the official guide:**
  - Length: third-party sources agree the GA exam is **180 min**; the beta was 85 Q / 205 min. → confirm on the booking page.
  - Price: third parties say **$300** (standard AWS Pro). → confirm on the booking page.
- **Recommended background:**
  - 2+ years building production apps on AWS / open source.
  - 1 year hands-on GenAI.
  - You meet both.
- **Explicitly out of scope:**
  - Model development and training.
  - Advanced ML techniques.
  - Data engineering / feature engineering.

---

<a id="en-2"></a>
## 2. Four exams compared + total score (DVA = 100)

### 2.1 Basics

| | **DVA-C02** (passed) | **AIP-C01** | **CCAR-F** | **CCAR-P** |
|---|---|---|---|---|
| Level | Associate | Professional | Foundations | Professional |
| Items | 65 (50 scored) | 75 (65 scored) | 60 | 63 |
| Time | 130 min | 180 min (verify) | 120 min | 120 min |
| Time per Q | 2.0 min | 2.4 min | 2.0 min | 1.9 min |
| Pass | 720 | **750** | 720 | 720 |
| Fee | $150 | $300 (verify) | $125 | $175 |
| Validity | 3 yrs | 3 yrs | 12 mo | 12 mo |
| Style | Service usage + API details | Architecture under constraints | Agent-architecture judgment | Enterprise solution judgment |
| Your prep hours | 60–90 (actual, 2 months part-time) | **90–110** | 30–45 | 45–60 solo; 25–35 after AIP + F |
| Full-time calendar | — | **3–4 weeks** | Pulse + 1-week closeout | 2 weeks |

- CCAR-F / P numbers come from your old plan; re-check on the Claude exam pages.

### 2.2 Difficulty score (each dimension DVA = 100)

| Dimension | DVA | AIP | CCAR-F | CCAR-P | Why |
|---|---|---|---|---|---|
| Breadth (services / topics to know) | 100 | 170 | 50 | 80 | AIP in-scope list ≈ 120 services, incl. the whole ML set; CCAR-F is one stack |
| Judgment depth (several options "work") | 100 | 160 | 120 | 170 | Pro stems are long with many constraints; CCAR-P tests enterprise tradeoffs |
| Exam stamina (items × time × pass bar) | 100 | 140 | 90 | 95 | AIP is 3 h + a 750 bar; candidates report not finishing mocks |
| Newness to you | 100 | 110 | 60 | 130 | You know the AWS base; you use Claude Code / MCP daily; governance and stakeholders are new |
| Your prep hours | 100 | 125 | 50 | 70 | Midpoints from the table above |
| **Total (average)** | **100** | **≈140** | **≈75** | **≈110** | |

- This is my judgment, not a measurement.
  - Use it to set priority and split time.
  - Re-calibrate after the W1 diagnostic.
- **How to read it:**
  - AIP ≈ 1.4× DVA → 3–4 weeks full-time is reasonable; part-time would be 2–3 months.
  - CCAR-F is easier than DVA → pulse-style works, **as long as mocks keep you honest** (see §8).

---

<a id="en-3"></a>
## 3. Exam map — one reference architecture covers all five domains

```
                 ┌──────── D3 Safety & Governance 20% ─────────┐
                 │ Guardrails · IAM · KMS · PrivateLink · Macie│
User ─► API Gateway ─► Lambda / Step Functions ─► Bedrock ──────┤
  (stream / WebSocket)  (orchestration, HITL,   (Converse,      │
                         circuit breaker)        Agents,        │
        D2 Implementation 26% │                  AgentCore)     │
                          ▼                       │             │
               ┌──── D1 FM + Data 31% ──────────┐ │             │
               │ S3 → parse → chunk → embed →   │◄┘             │
               │ vector store (OpenSearch/pgvec)│               │
               │ hybrid · metadata filter · rerank              │
               │ Prompt Management / Flows      │               │
               └────────────────────────────────┘               │
                 ┌──── D4 Cost & Perf 12% ──┐  ┌── D5 Eval & Debug 11% ┐
                 │ prompt cache · routing   │  │ Bedrock Evaluations   │
                 │ batch · provisioned · CRI│  │ invocation logs · X-Ray│
                 └──────────────────────────┘  └───────────────────────┘
```

- For every service you study, ask: which box is it in, and what replaces it?

---

<a id="en-4"></a>
## 4. What you actually need to learn (tiered)

### 4.1 Tier 0 — you already know it; only add the GenAI delta (~10% of time)

| Service | What you know | GenAI delta to add |
|---|---|---|
| Lambda | Events, timeouts, concurrency | 15-min cap → long agent runs move to Step Functions; stateless MCP servers |
| API Gateway | REST / HTTP, throttling | Streaming responses, WebSocket, integration timeout cap (verify current), request validation |
| SQS / EventBridge / SNS | Async, decoupling | Smooth FM call bursts; doc change → trigger KB sync |
| Step Functions | State machines | ReAct loop, stop conditions, circuit breaker, `waitForTaskToken` for human approval |
| DynamoDB / ElastiCache | KV, cache | Conversation history; semantic cache |
| IAM / KMS / VPC | Least privilege, encryption | Restrict `bedrock:InvokeModel` by model ID; Bedrock VPC endpoints |
| CloudWatch / X-Ray / CloudTrail | Monitoring, tracing, audit | Token metrics, model invocation logs, Logs Insights over prompts |
| CodePipeline / CodeBuild | CI/CD | Prompts and model versions are deployables; quality gates before deploy |

### 4.2 Tier 1 — must master (Bedrock core, ~60% of points)

- **Invocation (D1/D2/D4)**
  - `InvokeModel` vs `Converse` / `ConverseStream`
    - Converse = one interface; swap models without code changes; supports tool use.
  - Inference params: temperature, top-p, top-k, max tokens, stop sequences.
  - Modes: on-demand / provisioned / batch / cross-region inference profiles / latency-optimized (see §5.1).
  - Prompt caching, intelligent prompt routing.
- **Knowledge Bases (D1, heaviest)**
  - Data sources: S3, web crawler, Confluence, SharePoint, and other connectors.
  - Parsing: default vs FM parsing vs Bedrock Data Automation (table- and image-heavy PDFs).
  - Chunking: fixed / hierarchical / semantic / none / custom Lambda.
  - Embeddings: Titan Text Embeddings V2 (256 / 512 / 1024 dims); dims = accuracy vs storage cost.
  - Vector store options (see §5.2).
  - Retrieval: hybrid search, metadata filters, reranker models, query decomposition.
  - `Retrieve` vs `RetrieveAndGenerate`: use the former when you control generation.
  - Sync: source changes → ingestion job (incremental).
- **Guardrails (D3)**
  - Content filters (incl. prompt-attack filter), denied topics, word filters, sensitive-info filters (PII block / mask + regex).
  - Contextual grounding check: grounding threshold + relevance threshold → anti-hallucination.
  - Automated reasoning checks: validate answers against formal rules.
  - `ApplyGuardrail` API: works without invoking a model (usable for non-Bedrock models).
- **Agents (D2)**
  - Bedrock Agents: action groups (OpenAPI schema vs function details), Lambda, return-of-control, attached KB, session attributes, trace.
  - Multi-agent collaboration: supervisor pattern.
  - **AgentCore** (confirmed in scope): Runtime, Gateway, Memory, Identity, Observability, Code Interpreter, Browser.
  - **Strands Agents**, **AWS Agent Squad** (named in the official guide).
  - **MCP**: Lambda = stateless lightweight tools; ECS = complex / stateful tools.
- **Prompt Management + Prompt Flows (D1)**
  - Parameterized templates, versions, approval workflows.
  - Flows: sequential chains, conditional branches, pre/post-processing nodes.
- **Evaluation (D5)**
  - Bedrock Evaluations: automatic / human / LLM-as-judge / RAG eval (retrieve-only vs retrieve-and-generate).
  - Agent eval: task completion rate, tool-use effectiveness.
  - Golden sets, regression tests, deployment quality gates.
- **Observability (D4/D5)**
  - Model invocation logging (full request / response → S3 / CloudWatch Logs).
  - CloudWatch metrics: invocations, latency, input / output tokens, throttles.

### 4.3 Tier 2 — only know "when to pick it" (one-line rule)

| Service | Decision rule |
|---|---|
| SageMaker AI endpoints / JumpStart | Model not on Bedrock; need custom container / GPU control |
| SageMaker Model Registry | Versioning and rollback for custom / fine-tuned models |
| LoRA / adapters | Cheap deployment of several domain variants after fine-tuning |
| Bedrock Custom Model Import | Your own open-weight model with Bedrock's serverless invocation |
| Comprehend | Entities, intent, PII detection (cheap pre-processing before the FM) |
| Macie | PII discovery in S3 (before ingestion) |
| Kendra vs Knowledge Bases | Existing enterprise search + many connectors → Kendra; customizable RAG → KB |
| Q Business / Q Developer | Employee Q&A assistant (buy) / coding assistant |
| Lex / Connect | Chatbot / contact center |
| Textract / Transcribe / Bedrock Data Automation | Document OCR / speech-to-text / multimodal auto-extraction |
| Glue Data Quality / Data Catalog | Data quality checks / lineage and source registration |
| Lake Formation | Fine-grained data access |
| A2I (Augmented AI) | Managed human review workflow |
| SageMaker Clarify / Model Monitor | Bias detection / drift monitoring |
| AppConfig | Swap model / prompt config without code changes |
| Outposts / Wavelength | Data must stay on-prem / edge low latency |
| Amplify | Quick front-end UI |

### 4.4 Tier 3 — concepts (not tied to a service; re-wrapped across questions)

- Retrieval: chunking tradeoffs, embedding dims, hybrid search, reranking, query expansion / decomposition, lost-in-the-middle.
- Reasoning patterns: ReAct, chain-of-thought, prompt chaining, model cascading (small first, large as fallback).
- Cost: token estimation, context pruning, response-length limits, semantic vs exact vs prompt caching.
- Reliability: exponential backoff + jitter, circuit breaker, graceful degradation, cross-region.
- Quality: hallucination detection (golden sets, grounding scores, output diffing), LLM-as-judge, drift.
- Security: prompt injection, jailbreak, defense in depth (pre-filter → model guardrail → post-validation).

### 4.5 Skip

- Model training internals, SageMaker training job details.
- Feature engineering.
- SageMaker Neo depth (knowing "edge compilation/optimization" is enough).

---

<a id="en-5"></a>
## 5. Key comparison tables

### 5.1 Bedrock invocation modes

| Option | What it is | Strength | Weakness | Choose when |
|---|---|---|---|---|
| On-demand | Pay per token | No commitment, elastic | Quotas; 429 throttling | Spiky traffic, early stage |
| Provisioned throughput | Buy model units, hourly | Predictable throughput; usually required for custom models | Commitment; pay when idle | Steady high volume; serving fine-tuned models |
| Batch inference | S3 in → async job → S3 out | ~50% cheaper than on-demand for supported models (pricing page; verify) | Not real-time (hours) | Offline bulk: summarize, classify, tag |
| Cross-region inference profile | Auto-routes across regions | Higher throughput; reach models not in your region | Data crosses regions (check compliance) | Throttling / model not in region |
| Latency-optimized inference | Low-latency variant of select models | Faster TTFT | Only some models / regions | Real-time, latency-sensitive |
| Prompt caching | Caches repeated prompt prefixes | AWS claims up to ~90% lower cost on cached portion (verify) | Only for stable prefixes; TTL | Long system prompts; multi-turn over one doc |
| Intelligent prompt routing | Routes within a model family by difficulty | Automatic savings | Same family only | Mixed-difficulty traffic |

- **Deciding variable:** is traffic predictable + does it need real-time?

### 5.2 Vector stores

| Option | What it is | Strength | Weakness | Choose when |
|---|---|---|---|---|
| OpenSearch Serverless | KB default managed store | Hybrid search; one-click from KB | Minimum OCU cost | Default; need hybrid search |
| OpenSearch Service (managed cluster) | Self-managed cluster + Neural plugin | Control over shards, multi-index | Ops burden | Very large scale; shard tuning |
| Aurora PostgreSQL + pgvector | Relational DB + vectors | Same DB as business data; SQL filters | Behind dedicated engines at very large scale | Postgres already in place; vector + relational joins |
| Neptune Analytics | Graph DB | GraphRAG: entity relationships | Niche; learning cost | Multi-hop relationship questions |
| Third party (Pinecone, Redis, MongoDB Atlas) | External stores KB supports | Team already uses it | Outside AWS; extra compliance surface | Existing investment |

- **Deciding variable:** do you need hybrid search + is Postgres already there?
- S3 Vectors isn't on the in-scope list (checked 2026-10-27) → don't spend time on it yet.

### 5.3 Agent orchestration options

| Option | What it is | Strength | Weakness | Choose when |
|---|---|---|---|---|
| Step Functions + Converse | Code defines the flow, LLM fills steps | Deterministic, auditable, easy HITL | Stiff for open-ended tasks | Flow is fixed (most enterprise cases) |
| Bedrock Agents | Managed agent | Least ops; action groups + KB | Limited customization, black-box-ish | "Least operational overhead" stems |
| AgentCore | Managed agent runtime + infra | Any framework; memory, identity, gateway, observability | Many parts to assemble | Bring-your-own framework (Strands / LangGraph) to prod |
| Strands Agents | AWS open-source SDK, model-driven loop | Little code; native MCP | An SDK, not managed | Custom agents, often on AgentCore |
| Agent Squad | AWS open-source multi-agent router | Intent classification → dispatch to specialist | Routing, not deep collaboration | Pick one of several specialist agents |

- **Deciding variable:** is the flow known at design time? Known → Step Functions; unknown → agent.

---

<a id="en-6"></a>
## 6. Question keyword → answer (memorize before the exam)

| Stem says | Usual answer |
|---|---|
| "Least operational overhead" | Managed Bedrock feature (KB, Agents, Guardrails), not self-built |
| "Model not available in region" / "throttling" | Cross-region inference profile |
| "Steady, predictable high volume" / "serve fine-tuned model" | Provisioned throughput |
| "Not real-time" / "millions of documents" | Batch inference |
| "Switch models without code changes" | Converse API + AppConfig |
| "Ground answers in sources, reduce hallucination" | KB grounding + Guardrails contextual grounding check |
| "Output must not contain PII" | Guardrails sensitive-info filter (mask) |
| "Find PII in S3 before ingestion" | Macie |
| "Cheaply detect entities / intent before the call" | Comprehend |
| "Human approval before execution" | Step Functions `waitForTaskToken` or A2I |
| "Long repeated system prompt" | Prompt caching |
| "Same / similar questions repeated" | Semantic cache (ElastiCache / OpenSearch) |
| "Keyword + semantic" | Hybrid search (OpenSearch) |
| "Documents have section structure" | Hierarchical chunking |
| "Documents update often" | Event-driven incremental sync (S3 event → ingestion job) |
| "Deterministic results from structured data" | Text-to-SQL, not RAG |
| "Full request / response analysis" | Model invocation logging |
| "Trace across services" | X-Ray |
| "Lightweight stateless tool" / "complex stateful tool" | MCP on Lambda / MCP on ECS |
| "Data must stay on-prem" | Outposts |
| "Evaluate RAG quality" | Bedrock Evaluations RAG eval job |

- Rule: every wrong answer should become one new row in this table.

---

<a id="en-7"></a>
## 7. Full-time 4-week plan

### 7.1 Daily template (~6 h)

| Block | Time | Content |
|---|---|---|
| A | 2.5 h | AIP depth: docs + labs |
| B | 2 h | AIP course video / drills |
| C | 15 min | Error log + flashcards |
| P | 0–90 min | CCAR-F pulse (optional, see §8) |

- D7 = rest.
- Video at 1.5×; stop and do it yourself when a demo starts.

### 7.2 W1 — Bedrock core + RAG (D1, 31%)

| Day | Block A | Block B | Output |
|---|---|---|---|
| D1 | Official guide → checklist (one line per Skill, self-rate 1–5) · skim in-scope list | Skill Builder official practice set as baseline | Checklist + baseline |
| D2 | **Lab:** boto3 `Converse` + tool use + `ConverseStream` | Course: Bedrock basics, model families, inference params | Working script |
| D3 | Read all invocation modes → rewrite §5.1 in your own words | Course: invocation options, pricing | Your §5.1 |
| D4 | **Lab:** KB on S3, two chunking strategies, compare retrieval | Course: KB I — parsing, chunking, embeddings | Chunking notes |
| D5 | **Lab:** metadata filter + reranker; `Retrieve` vs `RetrieveAndGenerate` | Course: KB II — vector stores, hybrid search | Retrieval notes |
| D6 | Prompt Management, Flows, data validation (Glue DQ, Comprehend) | 30 D1 Qs → error log | Error log v1 |

### 7.3 W2 — Agents + integration + deployment (D2, 26%)

| Day | Block A | Block B | Output |
|---|---|---|---|
| D1 | **Lab:** Bedrock Agent + 1 action group + return-of-control | Course: Bedrock Agents, multi-agent collaboration | Agent demo |
| D2 | AgentCore parts · Strands · Agent Squad · MCP (Lambda vs ECS) · **Optional lab:** Strands agent + 1 MCP tool on AgentCore Runtime | Official docs (the course may predate these) | Your §5.3 |
| D3 | Step Functions patterns: ReAct, stop conditions, circuit breaker, task-token HITL · API Gateway streaming · SQS async · AppConfig | Course: integration sections | Pattern notes |
| D4 | Deployment: SageMaker endpoints, JumpStart, Model Registry, LoRA, custom model import, cascading · Q Developer / Q Business / BDA | Course: deployment sections | Rule table §4.3 |
| D5 | 40 D2 Qs → error log | Review wrongs → add §6 rows | Error log |
| D6 | **Practice exam #1** (full, timed, diagnostic) | Review per domain | Domain scores |

### 7.4 W3 — Safety, governance, ops, eval (D3 20% + D4 12% + D5 11%)

| Day | Block A | Block B | Output |
|---|---|---|---|
| D1 | **Lab:** Guardrail (PII mask + grounding check) + standalone `ApplyGuardrail` | Course: Guardrails | Guardrail demo |
| D2 | Security: VPC endpoints, IAM by model ID, KMS, Lake Formation, Macie, retention · Governance: model cards, Glue lineage, CloudTrail | Course: security & governance | Notes |
| D3 | Cost / perf: token estimation, three cache types, routing / cascading, batch, provisioned sizing, inference params | Course: optimization | Cost sheet |
| D4 | **Lab:** one LLM-as-judge eval job · invocation logs → Logs Insights query | Course: eval, monitoring | Eval result |
| D5 | Troubleshooting: context overflow, truncation, 429 / quotas, retrieval drift, embedding mismatch | 40 D3–D5 Qs | Error log |
| D6 | **Practice exam #2** (fresh) | Review | Score |

### 7.5 W4 — Closeout

| Day | Content | Output |
|---|---|---|
| D1 | Review #2 · repair 2 weakest domains | Error log |
| D2 | **Practice exam #3** (fresh) + review | Score |
| D3 | Cheat sheet: §6 + "when X not Y" for every similar in-scope pair | Cheat sheet |
| D4 | **Practice exam #4** or AWS official practice exam | Score |
| D5 | Gate check (§9) · light review | Go / no-go |
| D6 | **Sit AIP-C01** (gate missed → slip to W5.D3) | Result |

---

<a id="en-8"></a>
## 8. CCAR-F pulse rules

- **Why pulse-style works:**
  - Difficulty ≈ 75 (below DVA).
  - Most of it is what you use daily (Claude Code, MCP, Agent SDK).
- **The risk, plainly:**
  - It tests Claude-specific defaults and wording (CLAUDE.md hierarchy, `tool_choice`, `stop_reason`, Batches API).
  - "I use it every day" ≠ "I know the answer the exam wants."
  - A pulse with no measurement = forever feeling almost ready.
- **Rules:**
  - Time: only after AIP blocks A + B; ≤ 6 h/week.
  - Topics: follow that week's AIP theme (learn each concept once):
    - W1 → tool use, structured output (JSON schema + validate-retry)
    - W2 → agent loop, subagents, hooks, MCP scope, Claude Code config
    - W3 → context management, eval, Batches API
  - Research / side quests: only inside the pulse block.
    - Requirement: an output (note, config in your repo, small lab).
  - Measurement: one CCAR-F mock every 2 weeks (20–30 Qs is fine).
- **After AIP:**
  - 1-week closeout: 2 full fresh mocks + gate → sit CCAR-F.
- **Timing:**
  - CCAR-F is valid 12 months → sit it close to your job-search window.

---

<a id="en-9"></a>
## 9. Book-it gate + study failure modes

### 9.1 Gate

| Exam | Book when |
|---|---|
| AIP-C01 | ≥ 80% on 2 consecutive **fresh** full practice exams, no domain < 70% |
| CCAR-F | ≥ 85% on a fresh mock, every domain ≥ 75% |

- "Fresh" = unseen questions. Repeating a set measures memory.
- DVA 750 was a narrow pass; the Pro bar is 750 → set the gate high.

### 9.2 Failure modes

| Failure | Trigger | Detection | Mitigation |
|---|---|---|---|
| Know services, can't choose | Watching video without drills | Scores stuck at 65–70%; error log says "both looked right" | Add one §6 rule per wrong answer |
| Drills become memory | Repeating the same set | Score drops > 10 pts on a new set | Only fresh sets count for the gate |
| Stale course | Video predates AgentCore / Strands / Agent Squad | Course update date older than the guide | Official docs only for those |
| Running out of time | 75 Qs in 3 h, long Pro stems | Unfinished mocks | 2.4 min/Q pace; flag and move at 3 min |
| Pulse eats main track | Side research is fun | Weekly log shows CCAR-F > 6 h | Hard cap; AIP blocks first |

---

<a id="en-10"></a>
## 10. Corrections to the old plan

- **AgentCore:** old plan said "verify in scope" → **confirmed on the in-scope list**.
- **Exam length:** old plan said "180 vs 205" → beta was 85 Q / 205 min; GA is 75 Q, and third parties agree on 180 min.
- **Missing from the old plan (named in the official guide):**
  - Strands Agents, AWS Agent Squad, MCP (Lambda vs ECS).
  - Bedrock Data Automation, Kiro, Amazon Quick.
  - Well-Architected Tool Generative AI Lens.
- **Pace:** old plan assumed 18 h/week → AIP in 7 weeks; full-time → 3–4 weeks.

---

<a id="refs"></a>
## References

1. AIP-C01 official exam guide — https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01.html
2. AIP-C01 in-scope services — https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/aip-01-in-scope-services.html
3. AWS cert page (booking, duration, price) — https://aws.amazon.com/certification/certified-generative-ai-developer-professional/
4. Amazon Bedrock samples (labs) — https://github.com/aws-samples/amazon-bedrock-samples
5. Strands Agents SDK — https://github.com/strands-agents/sdk-python
6. Amazon Bedrock AgentCore samples — https://github.com/awslabs/amazon-bedrock-agentcore-samples
7. AWS Agent Squad — https://github.com/awslabs/agent-squad
8. Tutorials Dojo AIP-C01 study path — https://tutorialsdojo.com/aws-certified-generative-ai-developer-professional-study-path-aip-c01-exam-guide/
