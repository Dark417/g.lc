# 1A — Task Queue

- Agents pick from here (Claude Code cloud, Codex, phone)
- Protocol: [AGENTS.md §6](AGENTS.md#6-taskmd-protocol)
  - Default pick = top `todo` in Queue, unless the user names an ID
  - Branch `a/A-NNN-<slug>`, PR title `A-NNN: <title>`
  - Same PR: task → `done`, `a.md` status, the three guides (`1java.md`, `1python.md`, `1tf.md`)
- Rules for every slice: [AGENTS.md §7–§11](AGENTS.md#7-knowledge-doc-rules)

## Index
- [Queue](#queue)
- [Backlog](#backlog)
- [Done](#done)

---

## Queue
> All rows below finished 2026-11-13 (kept as the lectures 1–59 record); next work comes from the Backlog.

| ID | Concept | Lectures | Status |
|---|---|---|---|
| A-010 | [C] 01.01 Bedrock Converse API (Python + Java) | 7–10, 22 | `done` |
| A-011 | [C] 01.02 Model customization | 11–12 | `done` |
| A-012 | [C] 01.03 Prompt management | 27 | `done` |
| A-013 | [C] 01.04 Prompt flows | 28 | `done` |
| A-014 | [C] 01.05 Prompt engineering and structured output | 29–34 | `done` |
| A-020 | [C] 02.01 Embeddings and vector search | 13, 14, 20 | `done` |
| A-021 | [C] 02.02 OpenSearch as a vector store | 17, 53–59 | `done` |
| A-022 | [C] 02.03 Chunking | 18–19 | `done` |
| A-023 | [C] 02.04 Bedrock Knowledge Bases | 15, 16, 21, 38 | `done` |
| A-030 | [C] 03.01 Bedrock Data Automation | 38–39 | `done` |
| A-031 | [C] 03.02 Glue Data Quality | 43–45 | `done` |
| A-032 | [C] 03.03 Transcribe | 47–48 | `done` |
| A-033 | [C] 03.04 Comprehend | 49–52 | `done` |
| A-040 | [C] 04.01 Bedrock Guardrails (Python + Java) | 23–25, 34 | `done` |
| A-041 | [C] 04.02 PII detection and redaction | 26, 49–51 | `done` |
| A-042 | [C] 04.03 Evaluations (RAG, model, guardrail) | 21 | `done` |
| A-050 | [C] 05.01 GenAI observability | 46 | `done` |

- Done when (every row): AGENTS §11 checks pass; doc §7 Code map lists every scenario and gap

## Backlog
> Promote to Queue with a full spec when the lectures are learned.

- A-060 [C] 06.01 Bedrock Agents classic + action groups (lectures 98–101; deprecation noted)
- A-061 [C] 06.02 Multi-agent workflows + agent memory (102–103)
- A-062 [C] 06.03 Strands Agents + Agent Squad (104–105)
- A-063 [C] 06.04 AgentCore: runtime, memory, gateway, identity, policies, evaluators (106–113)
- A-064 [C] 06.05 MCP + OpenAPI tools + human in the loop (114–116)
- A-070 [C] 07.01 Token efficiency, caching, model selection, cross-region inference (126–136)
- A-071 [C] 07.02 Lambda + API Gateway + AppConfig dynamic model selection (153–161)
- A-072 [C] 07.03 Step Functions prompt chaining + circuit breaker (162–165)
- A-080 [C] 08.01 Tracing and audit: agent tracing, CloudTrail, X-Ray (189, 201–206)
- A-081 [C] 08.02 Security: least privilege, masking, KMS, Secrets Manager, Cognito, PrivateLink (208–234)

## Done
- 2026-11-13 · A-000 Skeleton: `AGENTS.md`, `terraform/AGENTS.md`, `a.md`, `task.md`, guides
- 2026-11-13 · A-001 Python base: FastAPI, `A_ENABLED` slice mounting, base `config.py`, `aws.py` (adaptive retries, 60 s read timeout), `retry.py`; compileall + import check passed
- 2026-11-13 · A-002 Java base: Spring Boot 3.5.16, Java 17, SDK BOM 2.59.0 (`bedrockruntime`, `bedrock`, `bedrockagentruntime`); `mvn compile` passed
- 2026-11-13 · A-003 Terraform foundation `00.00`–`00.05`; `terraform validate` passed (1.9.8, aws 6.73.0)
- 2026-11-13 · A-010..A-014, A-020..A-023, A-030..A-033, A-040..A-042, A-050: 17 concepts done (lectures 5–59); `mvn compile`, compileall + 91-route import, `terraform validate` passed
