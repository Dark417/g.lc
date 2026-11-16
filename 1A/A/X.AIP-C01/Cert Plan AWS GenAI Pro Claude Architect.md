# 认证计划 / Cert Plan — AWS GenAI Developer Pro + Claude Architect

## 目录 / Index

- **中文**
  - [0. 结论](#zh-0)
  - [1. 先做这两件事](#zh-1)
  - [2. 四个考试对比](#zh-2)
  - [3. 重叠地图（为什么能并行）](#zh-3)
  - [4. 小时数估算](#zh-4)
  - [5. 考纲](#zh-5)
  - [6. 每日模板](#zh-6)
  - [7. 周计划](#zh-7)
  - [8. 报名门槛](#zh-8)
  - [9. Udemy 之外的学习方式](#zh-9)
  - [10. 时间护栏](#zh-10)
  - [11. 其他厂商证书（NVIDIA、Databricks、微软、谷歌）](#zh-11)
- **English**
  - [0. Bottom line](#en-0)
  - [1. Two checks first](#en-1)
  - [2. The four exams compared](#en-2)
  - [3. Overlap map](#en-3)
  - [4. Hours estimate](#en-4)
  - [5. Syllabus](#en-5)
  - [6. Daily template](#en-6)
  - [7. Plan](#en-7)
  - [8. Book-it gates](#en-8)
  - [9. Learning beyond Udemy](#en-9)
  - [10. Guardrail on time](#en-10)
  - [11. Other vendor certs (NVIDIA, Databricks, Microsoft, Google)](#en-11)
- [References](#refs)

**前提：** 每天 3 小时，每周 6 天，1 天休息。
- 计划负荷 ≈ 每周 18 小时专注学习。
- 周次是相对的（W1.D1 = 你开始的那天）。

---

<a id="zh-0"></a>
## 0. 结论

- **AIP-C01 + CCAR-F 并行 → 约 7 周。**
  - CCAR-F 先拿，W4 结束。
  - AIP-C01 在 W7 结束拿。
- **再加 CCAR-P → 总共约 10 周。**
  - W8–W10，有门槛（见 §7）。
- **CCDV-F → 跳过**（可选，CCAR-F 之后约 12–15 小时）。
- **用你 AWS DVA 的结果校准：**
  - 业余 2 个月 ≈ 60–90 小时；750 分 = 刚过 720 及格线。
  - AIP-C01 是 Professional 级，及格线更高（750）→ 要预留更多时间，不是更少。
  - 你的 Bedrock / Agent / RAG 实战经验能抵掉一部分。
- **下面的小时数都是估算** —— W1 诊断测试后重新调整。

---

<a id="zh-1"></a>
## 1. 先做这两件事（W1.D1，30 分钟）

| 检查项 | 为什么重要 | 去哪看 |
|---|---|---|
| **Claude 考试报名资格** | 有的指南说报名需要 Claude Partner Network 组织邮箱；也有的显示开放 Pearson VUE。你目前在找工作——投入 40+ 小时前先确认 | anthropic.skilljar.com 认证页面 |
| **AIP-C01 考试时长** | 第三方来源说法不一（180 vs 205 分钟）；影响模拟考计时 | AWS 预约页面 |

- 更正我上一条回答：
  - **CCAR-F 不是 CCAR-P 的前置要求** —— 两个是独立证书。
  - 先 F 后 P 仍是我的建议，不是硬规定。

---

<a id="zh-2"></a>
## 2. 四个考试对比

| | **AWS GenAI Dev Pro (AIP-C01)** | **Claude Developer F (CCDV-F)** | **Claude Architect F (CCAR-F)** | **Claude Architect P (CCAR-P)** |
|---|---|---|---|---|
| 级别 | Professional | Foundations | Foundations（301 级） | Professional |
| 题数 | 65 计分 + 10 不计分 | 53 | 60 | 63 |
| 时长 | 180–205 分钟（待核实） | 120 分钟 | 120 分钟 | 120 分钟 |
| 及格 | 750 / 1000 | 720 / 1000 | 720 / 1000 | 720 / 1000 |
| 费用 | $300（AWS Pro 标准价；待核实） | $125 | $125 | $175 |
| 有效期 | 3 年（AWS 标准） | 12 个月 | 12 个月（免费续证测评） | 12 个月 |
| 风格 | 约束下选服务 | 代码优先，API 机制 | 架构判断，场景题 | 企业级判断，场景题 |
| 最重的域 | D1 基础模型集成、数据、合规 31% | 应用与集成 33.1% | Agent 架构与编排 27% | 集成 19% |
| 厂商中立价值 | 中（AWS 专属服务） | 低 | 中 | 中–高 |
| 对你的市场信号 | **高** —— 银行/企业都用 Bedrock | 低（你已超过这个水平） | **高** —— 架构师头衔 | **高** —— 资深，但较新、知名度低 |
| 你的短板 | AWS 服务名、Guardrails、评测服务 | API 细节 | Claude Code 配置、Agent SDK | 治理、干系人、规模化评测 |
| 选择 | **考** | 跳过 | **先考** | **考，有门槛** |

**决定变量：** 每小时学习换来的信号。
- AIP-C01 和 CCAR-F 约 40% 概念重叠 → 并行效率高。
- CCDV-F 基本是在代码层面重考 CCAR-F 的内容。

---

<a id="zh-3"></a>
## 3. 重叠地图 —— 为什么能并行

| 概念 | AIP-C01 | CCAR-F | CCAR-P | 学一次，用在 |
|---|---|---|---|---|
| RAG：分块、向量库、混合检索、重排 | D1 (31%) | — | 集成 | AIP + CCAR-P |
| Agent / 编排 / 多 Agent | D2 (26%) | D1 (27%) | 方案设计 | 三个都用 |
| 工具设计、最小权限、MCP | D2/D3 | D2 (18%) | 集成 | 三个都用 |
| Guardrails、PII、注入、治理 | D3 (20%) | D2/D5 | 治理 | 三个都用 |
| 成本、延迟、缓存、选模型 | D4 (12%) | D5 (15%) | 模型与上下文 | 三个都用 |
| 评测、测试、排障 | D5 (11%) | D4/D5 | 评测与优化 | AIP + CCAR-P |
| 结构化输出、提示工程 | D1/D2 | D4 (20%) | 模型与上下文 | 三个都用 |
| Claude Code 配置、CI/CD | — | D3 (20%) | 开发效率 (7%) | 仅 CCAR-F |

**规则：** 哪条线先碰到某个概念，就在那条线上学透；另一条线只补厂商对应关系。

---

<a id="zh-4"></a>
## 4. 小时数估算（针对你）

| 证书 | 单独学的小时数 | 单独学周数 @ 18 小时/周 | 在其他证书之后的增量 | 本计划安排 |
|---|---|---|---|---|
| AIP-C01 | 70–85 | 4–5 | — | W1–W7（并行） |
| CCAR-F | 35–45 | 2–2.5 | — | W1–W4 |
| CCAR-P | 45–60 | 2.5–3.5 | AIP + CCAR-F 之后 25–35 | W8–W10 |
| CCDV-F | 30–40 | 2 | CCAR-F 之后 12–15 | 可选 |

- Udemy AIP 课程：20+ 小时视频。
  - 加上笔记、实验、回看，实际成本 ≈ 视频时长 2 倍 → 约 40 小时。
  - 模拟题 + 复盘再加约 25–30 小时。

---

<a id="zh-5"></a>
## 5. 考纲

### 5.1 AIP-C01 —— AWS GenAI Developer Pro

| 域 | 权重 | 必须覆盖 |
|---|---|---|
| D1 基础模型集成、数据管理与合规 | 31% | Bedrock 模型家族 + 推理参数 · Converse API · 按需 vs 预置吞吐 vs 批量 vs 跨区域推理配置 · Knowledge Bases（解析、分块：固定 / 分层 / 语义，嵌入） · 向量库选项（OpenSearch Serverless、Aurora pgvector，其他看 in-scope 清单） · 混合检索、元数据过滤、重排 · 数据新鲜度 / KB 同步 · 定制化决策（微调 / 继续预训练 / 蒸馏 / 自定义导入 vs RAG） |
| D2 实现与集成 | 26% | Bedrock Agents（action groups、Lambda、OpenAPI、return-of-control） · 多 Agent 协作 · AgentCore（核实是否在范围内） · Prompt Management、Flows · Lambda / Step Functions / API Gateway / SQS 模式 · 流式响应 · Bedrock vs SageMaker 端点/JumpStart · Q Business、Q Developer |
| D3 AI 安全与治理 | 20% | Guardrails（内容过滤、禁止话题、词过滤、PII 过滤、上下文事实校验、自动推理） · IAM 最小权限 · KMS · VPC 端点 / PrivateLink · 调用日志 · CloudTrail · Macie · 提示注入防御 · 数据驻留 · 审计 / 血缘 |
| D4 运营效率与优化 | 12% | Token 成本模型 · 提示缓存 · 智能提示路由 · 批量推理 · 延迟优化推理 · 语义缓存 · 配额、限流、并发 |
| D5 测试、验证与排障 | 11% | Bedrock 模型评测（自动 / 人工 / LLM 评审） · RAG 评测 · 黄金集、CI 回归 · CloudWatch、X-Ray · 排查检索质量、429、token 上限 |

- AWS 明确不考：模型开发/训练、高级 ML、特征工程。
- 背服务名之前，先查官方 **in-scope / out-of-scope 服务** 页面。

### 5.2 CCAR-F —— Claude Architect Foundations

| 域 | 权重 | 必须覆盖 |
|---|---|---|
| D1 Agent 架构与编排 | 27% | Agent 循环 + `stop_reason` 处理 · tool_use / tool_result 循环 · 协调者–子 Agent 模式 · 子 Agent 间的上下文传递 · 任务分解 · hooks · 会话 / 恢复 · 升级路径 |
| D2 工具设计与 MCP 集成 | 18% | 工具描述即规格 · `tool_choice`（auto / any / 指定） · 结构化工具报错 · 按 Agent 分配最小权限工具 · MCP 服务端 / 客户端 · 项目级 vs 用户级（`.mcp.json`） |
| D3 Claude Code 配置与工作流 | 20% | CLAUDE.md 层级（用户 / 项目 / 子目录） · 路径作用域规则 · 斜杠命令、skills、子 Agent · 计划模式 vs 直接执行 · CI 中无头 `-p`、JSON 输出、权限 |
| D4 提示工程与结构化输出 | 20% | 明确标准而非模糊指令 · 用少样本示例规定格式和边界情况 · 用 tool_use + JSON schema 强制结构 · 校验–重试循环 · 可空字段防止编造 · Message Batches API 取舍 · 多轮 / 独立复核 |
| D5 上下文管理与可靠性 | 15% | 长对话策略 · 固定的"案件事实"块 · 裁剪工具输出 · 中间信息丢失 · 多 Agent 中的错误传播 · 人工复核 + 置信度校准 · 来源 / 引用 |

### 5.3 CCAR-P —— Claude Architect Professional

| 域 | 权重 | 必须覆盖 |
|---|---|---|
| D1 方案设计与架构 | 17% | 业务问题 → 端到端架构 · 分解 · 多 Agent 设计 · 对齐业务价值 · 什么时候**不该**用 Claude |
| D2 模型、提示与上下文工程 | 13% | 模型档位取舍 · 系统提示 · guardrails · 上下文策略 · 提示缓存 |
| D3 集成 | 19% | 安全分析 · 规模化可观测性 · RAG 管道设计 + 检索失败诊断 · 选择接入协议（API / SDK / MCP） |
| D4 评测、测试与优化 | 16% | 指标 · 数据集 · 测试框架 · A/B 测试 · 诊断线上系统 |
| D5 治理、安全与风险 | 14% | 最小权限 · 数据处理 · 合规（含欧盟 AI 法案时间线） · 风险登记册 |
| D6 | 14% | 我的来源里未确认名称 —— 以官方指南为准 |
| D7 开发效率 / 生命周期 | 7% | 团队用的 Claude 工具（Claude Code） · AI 辅助工作流 · 运维排障 |

- 已知缺口：没有官方完整模拟考 —— 只有几道样题。

### 5.4 CCDV-F（可选）—— 域权重参考

- 应用与集成 33.1% · 模型选择与优化 16.8% · Agent 与工作流 14.7% · 提示与上下文 11% · 工具与 MCP 10.6% · 安全 8.1% · Claude Code 3.1% · 评测/测试/调试 2.6%。

---

<a id="zh-6"></a>
## 6. 每日模板（3 小时）

| 块 | 时长 | 用途 |
|---|---|---|
| A | 90 分钟 | 主线（深度：文档、实验、模拟考） |
| B | 75 分钟 | 副线（视频、阅读、刷题） |
| C | 15 分钟 | 错题本 + 闪卡（永远放最后） |

- 阶段 1（W1–W4）：A = CCAR-F，B = AIP。
- 阶段 2（W5–W7）：A = AIP，B = AIP 练习或 CCAR-P 重叠阅读。
- 阶段 3（W8–W10）：A + B = CCAR-P。
- D7 = 休息；最多 30 分钟闪卡。

---

<a id="zh-7"></a>
## 7. 周计划

### 阶段 1 —— CCAR-F 主线，AIP 副线

**W1 —— 考纲、诊断、Agent 循环、Bedrock 基础**

| 天 | A 块 —— CCAR-F | B 块 —— AIP | 产出 |
|---|---|---|---|
| D1 | §1 资格检查 · 读官方 CCAR-F 指南 · 把任务描述转成清单 · 20 题诊断 | 读 AIP 官方指南 + in-scope 服务清单 · 用 Skill Builder 官方练习题做基线 | 两份清单，自评 1–5 |
| D2 | Messages API：`stop_reason`、tool_use → tool_result 循环 · **实验：** 手写一个 2 工具的 Agent 循环 | Udemy：Bedrock 基础、模型家族、推理参数、Converse API | 能跑的循环脚本 |
| D3 | Claude Agent SDK：循环、子 Agent、hooks、会话/恢复 · **实验：** SDK Agent + 1 个 PreToolUse hook | Udemy：调用方式 —— 按需、预置、批量、跨区域、流式 | hook 演示 |
| D4 | D1 深入：协调者/子 Agent、上下文传递、分解、升级 | Udemy：Bedrock 提示工程、Prompt Management、Flows | 笔记 |
| D5 | D1 练习：25 道场景题 → 错题本 | Udemy：Knowledge Bases I —— 解析、分块策略、嵌入 | 错题本 v1 |
| D6 | 重做错题 · 写一页"Agent 架构决策表" | Knowledge Bases II —— 向量库、混合检索、元数据过滤、重排 | 决策表 |
| D7 | 休息 | | |

**W2 —— 工具、MCP、Claude Code；AWS Agents + 集成**

| 天 | A 块 —— CCAR-F | B 块 —— AIP | 产出 |
|---|---|---|---|
| D1 | D2：工具描述、`tool_choice`、结构化报错、最小权限 | Bedrock Agents：action groups、Lambda、OpenAPI、return-of-control | 笔记 |
| D2 | MCP：原语、传输、`.mcp.json` 项目级 vs 用户级 · **实验：** 把 edgar-mcp 接进 Claude Code | AgentCore 组件（核实范围） · Bedrock 多 Agent 协作 | MCP 接通 |
| D3 | D3：CLAUDE.md 层级、路径作用域规则、导入 · **实验：** 项目 CLAUDE.md + 规则 | Lambda / Step Functions / API Gateway / SQS 模式、流式 | 仓库配置 |
| D4 | 斜杠命令、skills、子 Agent、计划模式 vs 直接执行 | 编排选择：Bedrock Agents vs Step Functions vs 自定义循环 | 对比表 |
| D5 | CI 里的 Claude Code：`-p`、JSON 输出、权限 · **实验：** GitHub Action 无头代码评审 | 30 道 AIP 题（D1/D2） | CI action |
| D6 | 40 道混合 CCAR-F 题（D2 + D3）→ 错题本 | 复盘 AIP 错题 · RAG 决策表（分块 × 库 × 检索类型） | RAG 决策表 |
| D7 | 休息 | | |

**W3 —— 提示、结构化输出、可靠性；AWS 安全 + 治理**

| 天 | A 块 —— CCAR-F | B 块 —— AIP | 产出 |
|---|---|---|---|
| D1 | D4：明确标准、少样本处理格式/边界、控制误报 | Guardrails：过滤器、禁止话题、PII、上下文事实校验、自动推理 | 笔记 |
| D2 | 结构化输出：tool_use + JSON schema、校验–重试、可空字段 · **实验：** 带重试的抽取 | 安全：IAM、KMS、PrivateLink、调用日志、CloudTrail、数据驻留 | 抽取脚本 |
| D3 | Message Batches API 取舍 · 多轮 / 独立复核 | AWS 负责任 AI：毒性/偏见评测、Macie、注入防御 | 笔记 |
| D4 | D5：长对话、案件事实块、裁剪、中间信息丢失 | 治理：审计、血缘、合规映射 | 笔记 |
| D5 | D5：错误传播、升级标准、置信度校准、来源 | 30 道 AIP 题（D3） | 错题本 |
| D6 | **CCAR-F 模拟考 #1**（60 题，120 分钟，计时） | 按域复盘模拟考 | 各域分数 |
| D7 | 休息 | | |

**W4 —— CCAR-F 收尾**

| 天 | A 块 —— CCAR-F | B 块 —— AIP | 产出 |
|---|---|---|---|
| D1 | 修补最弱的 2 个域（指南任务描述 + 文档） | 评测：Bedrock 模型评测、LLM 评审、RAG 评测 | 笔记 |
| D2 | 场景练习：每个考试场景写出"架构修复"的决策树 | 排障：429、配额、token 上限、延迟 | 场景表 |
| D3 | **模拟考 #2**（计时） | 复盘 #2 | 分数 |
| D4 | 弱域修补 · 易错点清单（CI 参数、MCP 作用域、CLAUDE.md 层级） | 只做闪卡 | 易错点清单 |
| D5 | **模拟考 #3** · 门槛检查（见下） | 轻度复习 | 考 / 不考 |
| D6 | **参加 CCAR-F**（没过门槛就推到 W5.D2） | — | 结果 |
| D7 | 休息 | | |

### 阶段 2 —— AIP 主线

**W5 —— AIP 深入（D1、D2）**

| 天 | A 块 —— AIP（120 分钟） | B 块（45 分钟） | 产出 |
|---|---|---|---|
| D1 | 重做官方练习题 → 新基线 · 学完剩余 Udemy 章节 | 读 CCAR-P 指南；标出重叠 | 基线变化 |
| D2 | 定制化决策：微调 / 继续预训练 / 蒸馏 / 导入 vs RAG | CCAR-P D2：模型档位取舍 | 决策表 |
| D3 | 数据管理：S3、Glue、KB 同步、新鲜度、元数据 | AIP 闪卡 | 笔记 |
| D4 | Bedrock vs SageMaker 端点/JumpStart · Q Business、Q Developer | AIP 闪卡 | 对比表 |
| D5 | **练习考 #1**（完整，计时） | — | 分数 |
| D6 | 逐个选项复盘 #1 | — | 错题本 |
| D7 | 休息 | | |

**W6 —— AIP D3–D5 + 优化**

| 天 | A 块 —— AIP | B 块 | 产出 |
|---|---|---|---|
| D1 | D4 成本：token 模型、提示缓存、提示路由、批量、预置 vs 按需 | CCAR-P D4：评测指标、A/B | 成本表 |
| D2 | D4 性能：延迟优化推理、流式、语义缓存、并发 | CCAR-P D5：治理 | 笔记 |
| D3 | D5：CI 中的评测管道、黄金集、检索排障 | AIP 闪卡 | 笔记 |
| D4 | **练习考 #2** | — | 分数 |
| D5 | 复盘 #2 · 弱项修补 | — | 错题本 |
| D6 | **练习考 #3** + 复盘 | — | 分数 |
| D7 | 休息 | | |

**W7 —— AIP 收尾**

| 天 | A + B 块 | 产出 |
|---|---|---|
| D1 | 复盘 #3 · 弱项修补 | 错题本 |
| D2 | **练习考 #4** + 复盘 | 分数 |
| D3 | 服务对比速查表（每对 in-scope 服务：什么时候用 X 不用 Y） | 速查表 |
| D4 | **练习考 #5** 或 AWS 官方练习考 | 分数 |
| D5 | 门槛检查 · 轻度复习 | 考 / 不考 |
| D6 | **参加 AIP-C01** | 结果 |
| D7 | 休息 | |

### 阶段 3 —— CCAR-P（有门槛）

**只在以下条件都满足时开始：** 两个考试都通过 **并且** 做完主力项目后还有时间。否则推迟到进入 AI 岗位约 6 个月后。

| 天 | W8 | W9 | W10 |
|---|---|---|---|
| D1 | 官方指南 + 诊断 | D5 治理、安全与风险 | 修补最弱的域 |
| D2 | D1 方案设计：分解、多 Agent、业务价值、何时不用 Claude | D7 开发效率 / 生命周期 | 写 5 个端到端场景答案 |
| D3 | D3 集成：安全分析、规模化可观测性 | D6（按官方指南） | 修补第二弱的域 |
| D4 | D3 集成：RAG 设计 + 失败诊断、协议选择 | **模拟考 #2** + 复盘 | **模拟考 #3** · 门槛检查 |
| D5 | D4 评测/测试（复用 AIP D5 笔记） · D2 模型与上下文 | 弱域修补 | 轻度复习 |
| D6 | **模拟考 #1** + 复盘 | 干系人场景：范围谈判、风险取舍 | **参加 CCAR-P** |
| D7 | 休息 | 休息 | 休息 |

---

<a id="zh-8"></a>
## 8. 报名门槛

| 考试 | 什么时候报名 |
|---|---|
| AIP-C01 | 连续 2 套**新的**完整练习考 ≥80%，没有任何域低于 70% |
| CCAR-F / CCAR-P | 一套新模拟考 ≥85%，每个域 ≥75% |

- "新的" = 没见过的题。
  - 重复刷同一套分数上升，测的是记忆，不是实力。
- 你 DVA 的 750 是险过 —— 这次门槛定高一点。

---

<a id="zh-9"></a>
## 9. Udemy 之外的学习方式 —— 按每小时回报排序

| 排名 | 方法 | 带来什么 | 用在 |
|---|---|---|---|
| 1 | **把官方考纲当清单** | 真正的考试范围；每条任务描述都变成一条自测 | 全部 |
| 2 | **在你自己的项目里做实验** | 场景题考的判断力；同时是作品集 | CCAR-F（Agent SDK、Claude Code CI、MCP），AIP（Bedrock KB、Guardrails） |
| 3 | **练习考 + 完整错题本** | 考试判断力；快速找到短板 | 全部 —— 一开始就当诊断用，不只是最后 |
| 4 | **免费官方课程** | 厂商自己的讲法 | Anthropic Academy（anthropic.skilljar.com）；AWS Skill Builder 备考计划 + 官方练习题 |
| 5 | **带着问题读文档** | 考试考的精确行为和默认值 | Bedrock 用户指南；Claude 文档；Claude Code 文档；MCP 规范 |
| 6 | **让 Claude 当考官** | 快速场景练习；逼你讲清取舍 | 贴一条任务描述 → 让它出 5 道场景题 → 你作答 → 让它打分 |
| 7 | **间隔重复闪卡** | 记住服务名、限制、参数 | AWS 服务对比；Claude Code 参数和配置层级 |
| 8 | **AWS Workshop Studio / re:Invent 演讲** | 端到端的 Bedrock 实操模式 | AIP D1/D2 |
| 9 | 学习指南 / 书 | 汇总的干扰项模式 | Leanpub CCAR-F/P 指南、Tutorials Dojo 学习路径 |

- 效率规则：
  - 视频 1.5 倍速；一到演示就停下来自己动手做。
  - 错题本用自己的话写："我选了 X 因为……；正确是 Y 因为……"。
  - 两条线按概念交叉学（§3），不按厂商分开学。

---

### 9.1 Udemy 课程选择（2026-10-26 查看）

| 用途 | 课程 | 讲师 | 评分 / 评分人数 | 规模 | 选择 |
|---|---|---|---|---|---|
| 视频（主） | Claude Certified Architect Foundations: Complete Course | Anton Voroniuk | 4.6 / 1,075 | 9 小时 | **买** —— 动手做工具、Agent、MCP、Claude Code、评测，时长合适 |
| 练习题（主） | Claude Certified Architect Foundations - 6 Practice Exams | Frank Kane | 4.4 / 5,192 | 360 题 | **买** —— 评分人数最多；附官方文档链接 |
| 练习题（第二套，用来测"新题"） | Claude Certified Architect (CCA-F, CCAR-F) - 6 Exams | Jacob Bushong | 4.3 / 80 | 360 题 | W4 门槛检查前再买 |
| 视频（备选） | Claude Certified Architect (CCAR-F) - 2026 Exam Prep | Jacob Bushong | 4.3 / 4,043 | 15 小时 | 更全但更长；评分略低 |
| 视频（备选） | Ultimate Anthropic Claude Certified Architect - Foundations | Frank Kane, Puria Izady | 4.5 / 102 | 8.5 小时 + 2 套模拟 | 新课，样本小 |
| 避开 | Practice Exams … CCAR-F（Abhishek Singh / Maarek） | — | 3.8 / 91 | 360 题 | 评分最低 |
| CCAR-P 以后 | CCAR-P Exam Prep（Jacob Bushong）+ CCAR-P Practice Exam Pack（Frank Kane） | — | 4.6 / 625；4.5 / 197 | 12.5 小时；189 题 | 到阶段 3 再买 |

- 规则：一套视频 + 一套练习题就够；第二套练习题只用来测没见过的题。
- 5.0 分、几十个评分以内的新课先不买 —— 样本太小。

<a id="zh-10"></a>
## 10. 时间护栏

- 证书是为主力项目服务的，不是替代它。
- CCAR-F 的实验（Agent SDK、Claude Code CI、MCP）**直接做在**主力项目仓库里。
  - 同样的时间算两份：备考 + 作品集。

---

<a id="zh-11"></a>
## 11. 其他厂商证书 —— NVIDIA、Databricks、微软、谷歌

### 11.1 结论

- **是的，你选的两个（AWS AIP-C01 + Claude Architect）就是对你目标最有用的两个。**
- **值得加的第三个：Databricks Generative AI Engineer Associate。**
  - 便宜（约 15–25 小时），贴你的 Databricks / Lakehouse 背景。
- **NVIDIA：**
  - NCP-GENL（LLM Professional）→ **跳过**。偏模型训练和 GPU 优化，不是你的方向。
  - NCP-AAI（Agentic AI Professional）→ **可选，以后再说**。方向对，但还没正式开放。
- **微软 AI-103 → 看目标公司用不用 Azure。** 不用就跳过。
- **谷歌 → 跳过**，除非你主攻 GCP 公司。

### 11.2 每个证书考的是技术栈哪一层

```
越靠近产品 / 应用层（你的方向）
┌─────────────────────────────────────────────────────┐
│ 方案架构、治理、干系人        CCAR-P                │
│ Agent 架构、工具、MCP         CCAR-F · NCP-AAI      │
│ 云上 GenAI 集成（托管服务）   AIP-C01 · AI-103      │
│ Lakehouse 上的 RAG / Agent    Databricks GenAI      │
│ 传统 ML 管道 + MLOps          Google PMLE           │
│ 模型优化、微调、GPU 加速      NCP-GENL              │
└─────────────────────────────────────────────────────┘
越靠近 GPU / 训练层（不是你的方向）
```

### 11.3 对比表

| 选项 | 是什么 | 优势 | 劣势 | 什么时候选 |
|---|---|---|---|---|
| **AWS AIP-C01** | AWS GenAI Developer Pro；65 题；750 分及格 | 银行/企业大量用 Bedrock；Professional 级 | 绑定 AWS 服务名 | **已选** —— 主攻 AWS 企业 |
| **Claude CCAR-F / P** | Anthropic 架构师认证；60 / 63 题；120 分钟 | 唯一直接考"Agent 架构判断"的；架构师头衔 | 新（2026 年 3 月才推出）；有效期 12 个月 | **已选** —— 架构师方向 |
| **Databricks GenAI Engineer Associate** | 45 题，90 分钟，$200，有效 2 年；建议 6 个月实战 | 考 Lakehouse 上的 RAG、Agent、治理、评测；贴你的 Databricks 背景 | Associate 级；只对 Databricks 生态有信号 | **加** —— 你的数据 + AI 定位最直接的证明 |
| **NVIDIA NCP-GENL** | Generative AI LLMs Professional；60–70 题，120 分钟，$200，有效 2 年；建议 2–3 年 LLM 经验 | NVIDIA 品牌在 AI 基础设施圈很强 | 约一半考的是模型优化 17%、GPU 加速 14%、微调 13%、LLM 架构 6% —— 训练/推理层，你的目标明确不做 | **跳过** —— 除非转推理/GPU 方向 |
| **NVIDIA NCA-GENL** | Generative AI LLMs Associate；50–60 题，60 分钟，$125 | 入门级，便宜 | 核心 ML 知识占 30%；对你太初级，信号弱 | **跳过** |
| **NVIDIA NCP-AAI** | Agentic AI Professional；60–70 题，120 分钟，$200；官网标"即将推出" | 方向对：Agent 架构 15%、开发 15%、评测 13%、部署 13% | 尚未开放；NVIDIA 平台占 7%；应用层招聘方认知度不如 AWS | **可选** —— 正式开放后，若目标是 NVIDIA 合作方 |
| **微软 AI-103** | Azure AI App and Agent Developer Associate；替代 6 月 30 日退役的 AI-102；2026 年 4 月开始 beta | 很多银行和大企业用 Azure / Foundry | 只对 Azure 公司有信号；价格待核实 | **看情况** —— 目标公司用 Azure 时 |
| **微软 AB-620 / AB-100** | Copilot Studio Agent 开发 / Agentic AI 业务方案架构师 Expert | 微软生态里的 Agent 证书 | 偏 Copilot Studio 低代码 | **跳过** —— 不是你的技术栈 |
| **谷歌 PMLE** | Professional ML Engineer；50–60 题，2 小时，$200；建议 3+ 年 | 已更新到 Gemini Enterprise Agent Platform | 大部分考传统 ML 管道、模型服务、MLOps | **跳过** —— 除非主攻 GCP |
| **谷歌 Generative AI Leader** | 偏业务的 GenAI 认证 | 门槛低 | 非技术；对工程师信号很弱 | **跳过** |
| **LangChain Academy** | 学完课程给证书，无监考 | 免费，内容实用 | 不是监考考试，招聘方不当证书看 | 只当学习材料用 |

### 11.4 怎么排优先级

| 优先级 | 证书 | 理由 |
|---|---|---|
| 1 | AWS AIP-C01 | 企业市场最大；Professional 级 |
| 2 | Claude CCAR-F → CCAR-P | 唯一直接对应"AI 架构师"的证书 |
| 3 | Databricks GenAI Associate | 便宜、贴背景、证明"数据 + AI" |
| 4 | 微软 AI-103 | 只在面 Azure 公司时 |
| 5 | NVIDIA NCP-AAI | 只在正式开放 + 目标是 NVIDIA 合作方时 |
| — | NCP-GENL、NCA-GENL、谷歌、LangChain | 跳过 |

- **决定变量：目标雇主用哪家云。**
  - AWS 公司 → 1 + 2 就够。
  - Azure 公司 → 1 换成 AI-103。
  - Databricks 客户（很多银行和保险）→ 加 3。
- **Databricks 证书放在 AIP-C01 之后**（W8 左右），用 1 周：
  - 约 40% 内容和 AIP 的 RAG / 评测 / 治理重叠。
  - 先考它会打乱主线。

### 11.5 提醒

- 证书只是辅助信号，不是主要信号。
  - 3 个以上同类证书的边际价值很低。
  - 面试官更看重：一个上线的系统 + 评测数据 + 成本模型 + 设计文档。
- 停在 3 个技术证书（AIP-C01 + CCAR-F + Databricks）就够了。
  - CCAR-P 等进入 AI 岗位后再考。

---
---

# English Version

**Budget assumed:** 3 h/day, 6 days/week, 1 rest day.
- Planned load ≈ 18 focused h/week.
- Weeks are relative (W1.D1 = whenever you start).

---

<a id="en-0"></a>
## 0. Bottom line

- **Parallel AIP-C01 + CCAR-F → ~7 weeks.**
  - CCAR-F lands first, end of W4.
  - AIP-C01 lands end of W7.
- **+ CCAR-P → ~10 weeks total.**
  - W8–W10, gated (see §7).
- **CCDV-F → skip** (optional add-on, ~12–15 h after CCAR-F).
- **Calibration from your AWS DVA result:**
  - 2 months part-time ≈ 60–90 h; 750 = just over the 720 pass line.
  - AIP-C01 is Professional level with a higher pass bar (750) → budget more hours, not fewer.
  - Your Bedrock / agent / RAG hands-on offsets part of that.
- **Hour figures below are estimates** — re-plan after the W1 diagnostics.

---

<a id="en-1"></a>
## 1. Do these two checks first (W1.D1, 30 min)

| Check | Why it matters | Where |
|---|---|---|
| **Claude exam eligibility** | Some guides say registration needs a Claude Partner Network org email; others show open Pearson VUE delivery. You're between jobs — confirm before sinking 40+ h | anthropic.skilljar.com certification pages |
| **AIP-C01 exam length** | Third-party sources conflict (180 vs 205 min); affects mock-exam timing | AWS booking page |

- Correction to my last answer:
  - **CCAR-F is not a prerequisite for CCAR-P** — they're separate credentials.
  - Order is still my recommendation, not a rule.

---

<a id="en-2"></a>
## 2. The four exams compared

| | **AWS GenAI Dev Pro (AIP-C01)** | **Claude Developer F (CCDV-F)** | **Claude Architect F (CCAR-F)** | **Claude Architect P (CCAR-P)** |
|---|---|---|---|---|
| Level | Professional | Foundations | Foundations (301-level) | Professional |
| Items | 65 scored + 10 unscored | 53 | 60 | 63 |
| Time | 180–205 min (verify) | 120 min | 120 min | 120 min |
| Pass | 750 / 1000 | 720 / 1000 | 720 / 1000 | 720 / 1000 |
| Fee | $300 (standard AWS Pro; verify) | $125 | $125 | $175 |
| Validity | 3 yrs (AWS standard) | 12 mo | 12 mo (free renewal assessment) | 12 mo |
| Style | Service selection under constraints | Code-first API mechanics | Architecture judgment, scenario-driven | Enterprise judgment, scenario-driven |
| Heaviest domain | D1 FM Integration, Data, Compliance 31% | Applications & Integration 33.1% | Agentic Architecture & Orchestration 27% | Integration 19% |
| Vendor-neutral value | Medium (AWS-specific services) | Low | Medium | Medium–high |
| Market signal for you | **High** — banks/enterprises run Bedrock | Low (you're past it) | **High** — architect title | **High** — senior, but newer and less known |
| Your gap | AWS service names, Guardrails, eval services | API minutiae | Claude Code config, Agent SDK | Governance, stakeholder, eval-at-scale |
| Pick | **Take** | Skip | **Take first** | **Take, gated** |

**Deciding variable:** signal per study hour.
- AIP-C01 + CCAR-F share ~40% of concepts → parallel is efficient.
- CCDV-F mostly re-tests what CCAR-F covers, at the code level.

---

<a id="en-3"></a>
## 3. Overlap map — why parallel works

| Concept | AIP-C01 | CCAR-F | CCAR-P | Study once, apply to |
|---|---|---|---|---|
| RAG: chunking, vector store, hybrid, rerank | D1 (31%) | — | Integration | AIP + CCAR-P |
| Agents / orchestration / multi-agent | D2 (26%) | D1 (27%) | Solution Design | All three |
| Tool design, least privilege, MCP | D2/D3 | D2 (18%) | Integration | All three |
| Guardrails, PII, injection, governance | D3 (20%) | D2/D5 | Governance | All three |
| Cost, latency, caching, model selection | D4 (12%) | D5 (15%) | Models & Context | All three |
| Evaluation, testing, troubleshooting | D5 (11%) | D4/D5 | Eval & Optimisation | AIP + CCAR-P |
| Structured output, prompt engineering | D1/D2 | D4 (20%) | Models & Context | All three |
| Claude Code config, CI/CD | — | D3 (20%) | Dev productivity (7%) | CCAR-F only |

**Rule:** learn the concept on whichever track hits it first; on the other track, only learn the vendor mapping.

---

<a id="en-4"></a>
## 4. Hours estimate (for you)

| Cert | Solo hours | Solo weeks @ 18 h/wk | Incremental if done after others | In this plan |
|---|---|---|---|---|
| AIP-C01 | 70–85 | 4–5 | — | W1–W7 (parallel) |
| CCAR-F | 35–45 | 2–2.5 | — | W1–W4 |
| CCAR-P | 45–60 | 2.5–3.5 | 25–35 after AIP + CCAR-F | W8–W10 |
| CCDV-F | 30–40 | 2 | 12–15 after CCAR-F | Optional |

- Udemy AIP course: 20+ h of video.
  - Real cost ≈ 2× video once you add notes, labs, and replays → ~40 h.
  - Practice exams + review add another ~25–30 h.

---

<a id="en-5"></a>
## 5. Syllabus

### 5.1 AIP-C01 — AWS GenAI Developer Pro

| Domain | Weight | Must cover |
|---|---|---|
| D1 FM Integration, Data Mgmt & Compliance | 31% | Bedrock model families + inference params · Converse API · on-demand vs provisioned throughput vs batch vs cross-region inference profiles · Knowledge Bases (parsing, chunking: fixed / hierarchical / semantic, embeddings) · vector store options (OpenSearch Serverless, Aurora pgvector, others per in-scope list) · hybrid search, metadata filters, reranking · data freshness / KB sync · customization decision (fine-tune / continued pretraining / distillation / custom import vs RAG) |
| D2 Implementation & Integration | 26% | Bedrock Agents (action groups, Lambda, OpenAPI, return-of-control) · multi-agent collaboration · AgentCore (verify in-scope) · Prompt Management, Flows · Lambda / Step Functions / API Gateway / SQS patterns · streaming responses · Bedrock vs SageMaker endpoints/JumpStart · Q Business, Q Developer |
| D3 AI Safety, Security & Governance | 20% | Guardrails (content filters, denied topics, word filters, PII filters, contextual grounding, automated reasoning) · IAM least privilege · KMS · VPC endpoints / PrivateLink · invocation logging · CloudTrail · Macie · prompt-injection defenses · data residency · audit / lineage |
| D4 Operational Efficiency & Optimization | 12% | Token cost model · prompt caching · intelligent prompt routing · batch inference · latency-optimized inference · semantic caching · quotas, throttling, concurrency |
| D5 Testing, Validation & Troubleshooting | 11% | Bedrock model evaluation (automatic / human / LLM-as-judge) · RAG evaluation · golden sets, regression in CI · CloudWatch, X-Ray · debugging retrieval quality, 429s, token limits |

- Out of scope per AWS: model development/training, advanced ML, feature engineering.
- Always check the official **in-scope / out-of-scope services** pages before memorizing a service.

### 5.2 CCAR-F — Claude Architect Foundations

| Domain | Weight | Must cover |
|---|---|---|
| D1 Agentic Architecture & Orchestration | 27% | Agent loop + `stop_reason` handling · tool_use / tool_result cycle · coordinator–subagent patterns · context passing between subagents · task decomposition · hooks · sessions / resume · escalation paths |
| D2 Tool Design & MCP Integration | 18% | Tool descriptions as spec · `tool_choice` (auto / any / specific) · structured tool errors · least-privilege tool distribution per agent · MCP servers / clients · project vs user scope (`.mcp.json`) |
| D3 Claude Code Configuration & Workflows | 20% | CLAUDE.md hierarchy (user / project / subdirectory) · path-scoped rules · slash commands, skills, subagents · plan mode vs direct execution · headless `-p` in CI, JSON output, permissions |
| D4 Prompt Engineering & Structured Output | 20% | Explicit criteria over vague instructions · few-shot for format and edge cases · tool_use + JSON schema to force structure · validation–retry loops · nullable fields to stop fabrication · Message Batches API tradeoffs · multi-pass / independent review |
| D5 Context Management & Reliability | 15% | Long-conversation strategy · persistent "case facts" block · trimming tool output · lost-in-the-middle · error propagation in multi-agent · human review + confidence calibration · provenance / citations |

### 5.3 CCAR-P — Claude Architect Professional

| Domain | Weight | Must cover |
|---|---|---|
| D1 Solution Design & Architecture | 17% | Business problem → end-to-end architecture · decomposition · multi-agent design · business-value alignment · when **not** to use Claude |
| D2 Models, Prompting & Context Engineering | 13% | Model-tier tradeoffs · system prompts · guardrails · context strategies · prompt caching |
| D3 Integration | 19% | Security analysis · observability at scale · RAG pipeline design + retrieval-failure diagnosis · choosing the connection protocol (API / SDK / MCP) |
| D4 Evaluation, Testing & Optimisation | 16% | Metrics · datasets · test frameworks · A/B tests · diagnosing live systems |
| D5 Governance, Safety & Risk | 14% | Least privilege · data handling · compliance (incl. EU AI Act timelines) · risk registers |
| D6 | 14% | Name not confirmed in my sources — read from the official guide |
| D7 Dev Productivity / Lifecycle | 7% | Claude tooling for teams (Claude Code) · AI-assisted workflows · operational debugging |

- Known gap: no official full-length practice exam — only sample questions.

### 5.4 CCDV-F (optional) — domain weights for reference

- Applications & Integration 33.1% · Model Selection & Optimization 16.8% · Agents & Workflows 14.7% · Prompt & Context 11% · Tools & MCPs 10.6% · Security & Safety 8.1% · Claude Code 3.1% · Eval/Testing/Debugging 2.6%.

---

<a id="en-6"></a>
## 6. Daily template (3 h)

| Block | Time | Purpose |
|---|---|---|
| A | 90 min | Primary track (deep work: docs, labs, mocks) |
| B | 75 min | Secondary track (video, reading, drills) |
| C | 15 min | Error log + flashcards (always last) |

- Phase 1 (W1–W4): A = CCAR-F, B = AIP.
- Phase 2 (W5–W7): A = AIP, B = AIP practice or CCAR-P overlap reading.
- Phase 3 (W8–W10): A + B = CCAR-P.
- D7 = rest; at most 30 min of flashcards.

---

<a id="en-7"></a>
## 7. Plan

### Phase 1 — CCAR-F primary, AIP secondary

**W1 — Blueprints, diagnostics, agent loop, Bedrock basics**

| Day | Block A — CCAR-F | Block B — AIP | Output |
|---|---|---|---|
| D1 | §1 eligibility checks · read official CCAR-F guide · turn task statements into a checklist · 20-Q diagnostic | Read AIP official guide + in-scope services list · Skill Builder official practice set as baseline | Two checklists, self-rated 1–5 |
| D2 | Messages API: `stop_reason`, tool_use → tool_result loop · **Lab:** hand-roll a 2-tool agent loop | Udemy: Bedrock fundamentals, model families, inference params, Converse API | Working loop script |
| D3 | Claude Agent SDK: loop, subagents, hooks, sessions/resume · **Lab:** SDK agent + 1 PreToolUse hook | Udemy: invocation options — on-demand, provisioned, batch, cross-region, streaming | Hook demo |
| D4 | D1 deep: coordinator/subagent, context passing, decomposition, escalation | Udemy: prompt engineering on Bedrock, Prompt Management, Flows | Notes |
| D5 | D1 drill: 25 scenario Qs → error log | Udemy: Knowledge Bases I — parsing, chunking strategies, embeddings | Error log v1 |
| D6 | Redo wrong Qs · write 1-page "agentic architecture decision sheet" | Knowledge Bases II — vector stores, hybrid search, metadata filters, reranking | Decision sheet |
| D7 | Rest | | |

**W2 — Tools, MCP, Claude Code; AWS agents + integration**

| Day | Block A — CCAR-F | Block B — AIP | Output |
|---|---|---|---|
| D1 | D2: tool descriptions, `tool_choice`, structured errors, least privilege | Bedrock Agents: action groups, Lambda, OpenAPI, return-of-control | Notes |
| D2 | MCP: primitives, transports, `.mcp.json` project vs user scope · **Lab:** wire edgar-mcp into Claude Code | AgentCore components (verify scope) · Bedrock multi-agent collaboration | MCP wired |
| D3 | D3: CLAUDE.md hierarchy, path-scoped rules, imports · **Lab:** project CLAUDE.md + rules | Lambda / Step Functions / API Gateway / SQS patterns, streaming | Repo config |
| D4 | Slash commands, skills, subagents, plan mode vs direct | Orchestration choice: Bedrock Agents vs Step Functions vs custom loop | Comparison table |
| D5 | Claude Code in CI: `-p`, JSON output, permissions · **Lab:** GitHub Action with headless review | 30 AIP Qs on D1/D2 | CI action |
| D6 | 40 mixed CCAR-F Qs (D2 + D3) → error log | Review AIP wrongs · RAG decision sheet (chunking × store × search type) | RAG sheet |
| D7 | Rest | | |

**W3 — Prompting, structured output, reliability; AWS safety + governance**

| Day | Block A — CCAR-F | Block B — AIP | Output |
|---|---|---|---|
| D1 | D4: explicit criteria, few-shot for format/edge cases, false-positive control | Guardrails: filters, denied topics, PII, contextual grounding, automated reasoning | Notes |
| D2 | Structured output: tool_use + JSON schema, validation–retry, nullable fields · **Lab:** extraction with retry | Security: IAM, KMS, PrivateLink, invocation logging, CloudTrail, residency | Extraction script |
| D3 | Message Batches API tradeoffs · multi-pass / independent review | Responsible AI on AWS: eval for toxicity/bias, Macie, injection defenses | Notes |
| D4 | D5: long conversations, case-facts block, trimming, lost-in-the-middle | Governance: audit, lineage, compliance mapping | Notes |
| D5 | D5: error propagation, escalation criteria, confidence calibration, provenance | 30 AIP Qs on D3 | Error log |
| D6 | **CCAR-F mock #1** (60 Q, 120 min, timed) | Review mock per domain | Domain scores |
| D7 | Rest | | |

**W4 — CCAR-F closeout**

| Day | Block A — CCAR-F | Block B — AIP | Output |
|---|---|---|---|
| D1 | Repair 2 weakest domains (guide task statements + docs) | Evaluation: Bedrock model eval, LLM-as-judge, RAG eval | Notes |
| D2 | Scenario drill: for each exam scenario, write the decision tree for the "architectural fix" | Troubleshooting: 429s, quotas, token limits, latency | Scenario sheet |
| D3 | **Mock #2** (timed) | Review mock #2 | Scores |
| D4 | Weak-domain repair · gotcha list (CI flags, MCP scope, CLAUDE.md levels) | Flashcards only | Gotcha list |
| D5 | **Mock #3** · gate check (below) | Light review | Go / no-go |
| D6 | **Sit CCAR-F** (slip to W5.D2 if gate missed) | — | Result |
| D7 | Rest | | |

### Phase 2 — AIP primary

**W5 — AIP depth (D1, D2)**

| Day | Block A — AIP (120 min) | Block B (45 min) | Output |
|---|---|---|---|
| D1 | Re-take official practice set → new baseline · finish remaining Udemy sections | Read CCAR-P guide; mark overlap | Baseline delta |
| D2 | Customization decision: fine-tune / continued pretraining / distillation / import vs RAG | CCAR-P D2: model-tier tradeoffs | Decision table |
| D3 | Data management: S3, Glue, KB sync, freshness, metadata | AIP flashcards | Notes |
| D4 | Bedrock vs SageMaker endpoints/JumpStart · Q Business, Q Developer | AIP flashcards | Comparison table |
| D5 | **Practice exam #1** (full, timed) | — | Score |
| D6 | Review every option of exam #1 | — | Error log |
| D7 | Rest | | |

**W6 — AIP D3–D5 + optimization**

| Day | Block A — AIP | Block B | Output |
|---|---|---|---|
| D1 | D4 cost: token model, prompt caching, prompt routing, batch, provisioned vs on-demand | CCAR-P D4: eval metrics, A/B | Cost sheet |
| D2 | D4 performance: latency-optimized inference, streaming, semantic cache, concurrency | CCAR-P D5: governance | Notes |
| D3 | D5: eval pipelines in CI, golden sets, retrieval troubleshooting | AIP flashcards | Notes |
| D4 | **Practice exam #2** | — | Score |
| D5 | Review #2 · weak-area repair | — | Error log |
| D6 | **Practice exam #3** + review | — | Score |
| D7 | Rest | | |

**W7 — AIP closeout**

| Day | Block A + B | Output |
|---|---|---|
| D1 | Review #3 · weak-area repair | Error log |
| D2 | **Practice exam #4** + review | Score |
| D3 | Service-comparison cheat sheet (when X vs Y for every in-scope pair) | Cheat sheet |
| D4 | **Practice exam #5** or AWS official practice exam | Score |
| D5 | Gate check · light review | Go / no-go |
| D6 | **Sit AIP-C01** | Result |
| D7 | Rest | |

### Phase 3 — CCAR-P (gated)

**Start only if:** both exams passed **and** runway remains after the flagship build. Otherwise defer until ~6 months into an AI role.

| Day | W8 | W9 | W10 |
|---|---|---|---|
| D1 | Official guide + diagnostic | D5 Governance, Safety & Risk | Repair weakest domain |
| D2 | D1 Solution Design: decomposition, multi-agent, business value, when not to use Claude | D7 Dev productivity / lifecycle | Write 5 end-to-end scenario answers |
| D3 | D3 Integration: security analysis, observability at scale | D6 (per official guide) | Repair second-weakest domain |
| D4 | D3 Integration: RAG design + failure diagnosis, protocol choice | **Mock #2** + review | **Mock #3** · gate check |
| D5 | D4 Eval/Testing (reuse AIP D5 notes) · D2 Models & Context | Weak-domain repair | Light review |
| D6 | **Mock #1** + review | Stakeholder scenarios: scope negotiation, risk tradeoffs | **Sit CCAR-P** |
| D7 | Rest | Rest | Rest |

---

<a id="en-8"></a>
## 8. Book-it gates

| Exam | Book when |
|---|---|
| AIP-C01 | ≥80% on 2 consecutive **fresh** full practice exams, no domain below 70% |
| CCAR-F / CCAR-P | ≥85% on a fresh mock, every domain ≥75% |

- "Fresh" = questions you haven't seen.
  - Rising scores on repeated sets measure memory, not readiness.
- Your DVA 750 was a narrow pass — set the bar higher this time.

---

<a id="en-9"></a>
## 9. How to learn beyond Udemy — ranked by return per hour

| Rank | Method | What it gives you | Use for |
|---|---|---|---|
| 1 | **Official exam guide as a checklist** | The actual scope; every task statement becomes a self-test line | All |
| 2 | **Build labs in your own project** | Judgment the scenario questions reward; doubles as portfolio | CCAR-F (Agent SDK, Claude Code CI, MCP), AIP (Bedrock KB, Guardrails) |
| 3 | **Practice exams + full error log** | Exam judgment; finds gaps fast | All — start early as diagnostic, not only at the end |
| 4 | **Free official courses** | Vendor's own framing of the material | Anthropic Academy (anthropic.skilljar.com); AWS Skill Builder exam prep plan + official practice set |
| 5 | **Docs, read with a question in hand** | Exact behavior + defaults the exams test | Bedrock user guide; Claude docs; Claude Code docs; MCP spec |
| 6 | **Drill with Claude as examiner** | Fast scenario reps; forces you to explain tradeoffs | Paste a task statement → ask for 5 scenario questions → answer → get graded |
| 7 | **Spaced-repetition flashcards** | Retention of service names, limits, flags | AWS service pairs; Claude Code flags and config levels |
| 8 | **AWS Workshop Studio / re:Invent talks** | Hands-on Bedrock patterns, end-to-end | AIP D1/D2 |
| 9 | Study guides / books | Consolidated distractor patterns | Leanpub CCAR-F/P guides, Tutorials Dojo study path |

- Efficiency rules:
  - Video at 1.5×; stop and do the thing when a demo starts.
  - Write the error log in your own words: "chose X because …; correct is Y because …".
  - Interleave the two tracks by concept (§3), not by vendor.

---

### 9.1 Udemy course picks (checked 2026-10-26)

| Use | Course | Instructor | Rating / ratings | Size | Pick |
|---|---|---|---|---|---|
| Video (main) | Claude Certified Architect Foundations: Complete Course | Anton Voroniuk | 4.6 / 1,075 | 9 h | **Buy** — hands-on with tools, agents, MCP, Claude Code, evals; right length |
| Practice (main) | Claude Certified Architect Foundations - 6 Practice Exams | Frank Kane | 4.4 / 5,192 | 360 Q | **Buy** — most ratings; links to official docs |
| Practice (second set, for "fresh" questions) | Claude Certified Architect (CCA-F, CCAR-F) - 6 Exams | Jacob Bushong | 4.3 / 80 | 360 Q | Buy before the W4 gate check |
| Video (alt) | Claude Certified Architect (CCAR-F) - 2026 Exam Prep | Jacob Bushong | 4.3 / 4,043 | 15 h | Broader but longer; slightly lower rating |
| Video (alt) | Ultimate Anthropic Claude Certified Architect - Foundations | Frank Kane, Puria Izady | 4.5 / 102 | 8.5 h + 2 mocks | New, small sample |
| Avoid | Practice Exams … CCAR-F (Abhishek Singh / Maarek) | — | 3.8 / 91 | 360 Q | Lowest rating |
| CCAR-P later | CCAR-P Exam Prep (Jacob Bushong) + CCAR-P Practice Exam Pack (Frank Kane) | — | 4.6 / 625; 4.5 / 197 | 12.5 h; 189 Q | Buy at Phase 3 |

- Rule: one video course + one practice set is enough; the second practice set is only for unseen questions.
- Skip new courses with a 5.0 rating from a few dozen reviews — the sample is too small.

<a id="en-10"></a>
## 10. Guardrail on time

- The certs support the flagship build; they don't replace it.
- Use CCAR-F labs (Agent SDK, Claude Code CI, MCP) **inside** the flagship repo.
  - Same hours count twice: exam prep + portfolio.

---

<a id="en-11"></a>
## 11. Other vendor certs — NVIDIA, Databricks, Microsoft, Google

### 11.1 Bottom line

- **Yes — the two you picked (AWS AIP-C01 + Claude Architect) are the two most useful for your goal.**
- **Worth adding as a third: Databricks Generative AI Engineer Associate.**
  - Cheap (~15–25 h), and it matches your Databricks / lakehouse background.
- **NVIDIA:**
  - NCP-GENL (LLM Professional) → **skip**. It leans to model training and GPU optimization, which isn't your direction.
  - NCP-AAI (Agentic AI Professional) → **optional, later**. Right direction, but not open yet.
- **Microsoft AI-103 → depends on whether your target employers run Azure.** Otherwise skip.
- **Google → skip**, unless you're targeting GCP shops.

### 11.2 Which layer of the stack each cert tests

```
Closer to product / application layer (your direction)
┌─────────────────────────────────────────────────────┐
│ Solution architecture, governance   CCAR-P           │
│ Agent architecture, tools, MCP      CCAR-F · NCP-AAI │
│ Cloud GenAI integration (managed)   AIP-C01 · AI-103 │
│ RAG / agents on the lakehouse       Databricks GenAI │
│ Classic ML pipelines + MLOps        Google PMLE      │
│ Model optimization, tuning, GPU     NCP-GENL         │
└─────────────────────────────────────────────────────┘
Closer to GPU / training layer (not your direction)
```

### 11.3 Comparison

| Option | What it is | Strength | Weakness | Choose when |
|---|---|---|---|---|
| **AWS AIP-C01** | AWS GenAI Developer Pro; 65 Q; pass 750 | Banks/enterprises run Bedrock; Professional level | Tied to AWS service names | **Already picked** — AWS enterprise targets |
| **Claude CCAR-F / P** | Anthropic architect certs; 60 / 63 Q; 120 min | Only exam that directly tests agent-architecture judgment; architect title | New (launched Mar 2026); 12-month validity | **Already picked** — architect track |
| **Databricks GenAI Engineer Associate** | 45 Q, 90 min, $200, valid 2 yrs; 6 months hands-on recommended | Tests RAG, agents, governance, evaluation on the lakehouse; matches your Databricks background | Associate level; signal only inside the Databricks ecosystem | **Add** — most direct proof of your "data + AI" positioning |
| **NVIDIA NCP-GENL** | Generative AI LLMs Professional; 60–70 Q, 120 min, $200, valid 2 yrs; 2–3 yrs LLM experience recommended | Strong NVIDIA brand in AI infra circles | About half is model optimization 17%, GPU acceleration 14%, fine-tuning 13%, LLM architecture 6% — the training/serving layer your goal excludes | **Skip** — unless you move to inference/GPU work |
| **NVIDIA NCA-GENL** | Generative AI LLMs Associate; 50–60 Q, 60 min, $125 | Entry level, cheap | Core ML knowledge 30%; too junior for you, weak signal | **Skip** |
| **NVIDIA NCP-AAI** | Agentic AI Professional; 60–70 Q, 120 min, $200; NVIDIA page says "coming soon" | Right direction: agent architecture 15%, development 15%, evaluation 13%, deployment 13% | Not open yet; NVIDIA platform 7%; less recognized than AWS by app-layer hiring managers | **Optional** — once open, if targeting NVIDIA partners |
| **Microsoft AI-103** | Azure AI App and Agent Developer Associate; replaces AI-102 (retired Jun 30, 2026); beta from Apr 2026 | Many banks and large enterprises run Azure / Foundry | Signal only at Azure shops; price to verify | **Depends** — when target employers run Azure |
| **Microsoft AB-620 / AB-100** | Copilot Studio agent builder / Agentic AI Business Solutions Architect Expert | Agent certs inside the Microsoft ecosystem | Leans to low-code Copilot Studio | **Skip** — not your stack |
| **Google PMLE** | Professional ML Engineer; 50–60 Q, 2 h, $200; 3+ yrs recommended | Updated for Gemini Enterprise Agent Platform | Mostly classic ML pipelines, model serving, MLOps | **Skip** — unless targeting GCP |
| **Google Generative AI Leader** | Business-oriented GenAI cert | Low bar | Non-technical; weak signal for engineers | **Skip** |
| **LangChain Academy** | Completion certificates, not proctored | Free, practical content | Not a proctored exam; hiring managers don't count it as a cert | Use as study material only |

### 11.4 Priority order

| Priority | Cert | Why |
|---|---|---|
| 1 | AWS AIP-C01 | Largest enterprise market; Professional level |
| 2 | Claude CCAR-F → CCAR-P | Only cert that maps directly to "AI architect" |
| 3 | Databricks GenAI Associate | Cheap, fits your background, proves "data + AI" |
| 4 | Microsoft AI-103 | Only when interviewing at Azure shops |
| 5 | NVIDIA NCP-AAI | Only once open + targeting NVIDIA partners |
| — | NCP-GENL, NCA-GENL, Google, LangChain | Skip |

- **Deciding variable: which cloud your target employers run.**
  - AWS shops → 1 + 2 is enough.
  - Azure shops → swap 1 for AI-103.
  - Databricks customers (many banks and insurers) → add 3.
- **Put Databricks after AIP-C01** (around W8), one week:
  - ~40% overlaps AIP's RAG / evaluation / governance content.
  - Doing it first would break the main track.

### 11.5 Caution

- Certs are a supporting signal, not the main one.
  - A fourth cert of the same kind adds little.
  - Interviewers weigh one shipped system + eval numbers + cost model + design docs more.
- Stop at three technical certs (AIP-C01 + CCAR-F + Databricks).
  - Take CCAR-P after you're in an AI role.

---

<a id="refs"></a>
## References

1. AWS AIP-C01 official exam guide — https://docs.aws.amazon.com/aws-certification/latest/ai-professional-01/ai-professional-01.html
2. Anthropic Academy (free courses, cert registration) — https://anthropic.skilljar.com
3. CCAR-F / CCAR-P exam facts + free lessons — https://claudecertificationguide.com/architect-foundations
4. CCAR-F / CCDV-F exam guide transcriptions — https://claudearchitectcertification.com/exam-guide/ccdv-f
5. Anthropic courses repo (labs) — https://github.com/anthropics/courses
6. AIP-C01 study path — https://tutorialsdojo.com/aws-certified-generative-ai-developer-professional-study-path-aip-c01-exam-guide/
7. CCAR-F / CCAR-P study guide — https://leanpub.com/cca-f
8. NVIDIA NCP-GENL (Generative AI LLMs Professional) — https://www.nvidia.com/en-us/learn/certification/generative-ai-llm-professional/
9. NVIDIA NCA-GENL (Generative AI LLMs Associate) — https://www.nvidia.com/en-us/learn/certification/generative-ai-llm-associate/
10. NVIDIA NCP-AAI (Agentic AI Professional) — https://nvidia.com/en-us/learn/certification/agentic-ai-professional
11. Databricks GenAI Engineer Associate exam guide (Mar 2026) — https://www.databricks.com/sites/default/files/2026-03/Databricks-Certified-Generative-AI-Engineer-Associate-Exam-Guide-Mar26.pdf
12. Microsoft 2026 certification retirements (AI-102 → AI-103) — https://vladtalkstech.com/microsoft-learning-and-credential-news/microsoft-certification-retirements-2026/
13. Google Cloud Professional ML Engineer — https://cloud.google.com/learn/certification/machine-learning-engineer
14. Agentic AI certification landscape — https://rickhigh.substack.com/p/the-agentic-ai-certification-landscape
