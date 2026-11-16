# 1A Task Queue

> Work queue for 1A agents (Claude Code, Codex, phone), plus the Java and Python guide.

- Protocol: [AGENTS.md §7](AGENTS.md#7-taskmd-protocol)
  - Default pick = top `todo` in Queue, unless the user names an ID
  - Branch `a/A-NNN-<slug>`, PR title `A-NNN: <title>`
  - ✅ After each round: finished tasks leave Queue → top of Finish, same change updates `a.md`, Guide tables, `1tf.md`
- New text the user drops anywhere here → becomes a Queue task + Index line

## Index

- [Queue](#queue)
  - base
    - [A-091 Env-aware resource names in app config](#a-091-env-aware-resource-names-in-app-config)
- [Backlog](#backlog)
  - 06agents: A-060 · A-061 · A-062 · A-063 · A-064
  - 07integration: A-070 · A-071 · A-072
  - 08governance: A-080 · A-081
- [Finish](#finish)
  - A-092 Move-in · A-090 Restructure · A-010..A-050 17 concepts · A-000..A-003 base
- [Guide](#guide)
  - [Java](#java) · [Python](#python)

---

## Queue

### A-091 Env-aware resource names in app config

- Status: `todo`
- Why: Terraform names now carry the env (`a-dev-guardrail`, `a-dev-ai-data-<acct>`), but `application.yml` and `app/config/*.py` defaults still say `a-guardrail`
- Do: default names to the `local` env, override per env through `A_<SLICE>_*` vars that match `terraform output`
- Finish when: Java + Python defaults equal `terraform output` names for `local`; checks pass

## Backlog

> Promote to Queue with a full spec when the lectures are learned.

- A-060 [C] 06agents.01bedrock-agents — classic agents + action groups (lectures 98–101; deprecation noted)
- A-061 [C] 06agents.02multi-agent — multi-agent workflows + agent memory (102–103)
- A-062 [C] 06agents.03strands — Strands Agents + Agent Squad (104–105)
- A-063 [C] 06agents.04agentcore — runtime, memory, gateway, identity, policies, evaluators (106–113)
- A-064 [C] 06agents.05mcp-tools — MCP + OpenAPI tools + human in the loop (114–116)
- A-070 [C] 07integration.01token-efficiency — caching, model selection, cross-region inference (126–136)
- A-071 [C] 07integration.02lambda-apigw — Lambda + API Gateway + AppConfig dynamic model selection (153–161)
- A-072 [C] 07integration.03step-functions — prompt chaining + circuit breaker (162–165)
- A-080 [C] 08governance.01tracing — agent tracing, CloudTrail, X-Ray (189, 201–206)
- A-081 [C] 08governance.02security — least privilege, masking, KMS, Secrets Manager, Cognito, PrivateLink (208–234)

## Finish

- 2026-11-13 · A-092 Move-in: `A/` (agent chat apps), `claudecode/`, `mcp/` from `1a-all-you-can-think`; `apis` copied (gitignored); Terraform foundation → unnumbered `base_*` modules
- 2026-11-13 · A-090 Restructure: group names (`01bedrock`, `02rag`, …), layer-first Java + Python with `_GGgroup_CCcomp` packages, `docs/` → `x-md/<group>/` flat concept files with Python blocks, Terraform project (base files, `envs/` local/dev/uat/prod, `modules/`), shared AGENTS.md synced with 1x, `1java.md` + `1python.md` merged into this Guide
- 2026-11-13 · A-050 [C] observability (lecture 46)
- 2026-11-13 · A-040..A-042 [C] 04safety: guardrails (Python + Java), pii-redaction, evaluations (lectures 21, 23–26, 34, 49–51)
- 2026-11-13 · A-030..A-033 [C] 03data: data-automation, glue-data-quality, transcribe, comprehend (lectures 38–39, 43–52)
- 2026-11-13 · A-020..A-023 [C] 02rag: embeddings, opensearch, chunking, knowledge-bases (lectures 13–21, 53–59)
- 2026-11-13 · A-010..A-014 [C] 01bedrock: converse (Python + Java), customization, prompt-management, prompt-flows, prompt-engineering (lectures 7–12, 22, 27–34)
- 2026-11-13 · Checks for the 17 concepts: `mvn compile`, compileall + 91-route import, `terraform validate` passed
- 2026-11-13 · A-003 Terraform foundation `base_*`; `terraform validate` passed (1.9.8, aws 6.73.0)
- 2026-11-13 · A-002 Java base: Spring Boot 3.5.16, Java 17, SDK BOM 2.59.0 (`bedrockruntime`, `bedrock`, `bedrockagentruntime`)
- 2026-11-13 · A-001 Python base: FastAPI, `A_ENABLED` slice mounting, base `config.py`, `aws.py` (adaptive retries, 60 s read timeout), `retry.py`
- 2026-11-13 · A-000 Skeleton: `AGENTS.md`, `terraform/AGENTS.md`, `a.md`, `task.md`, guides

---

## Guide

Build, run, and slice tables for both code projects (was `1java.md` + `1python.md`).

### Java

- Project: `java/` — one Maven project, Spring Boot 3.5.x, Java 17
- Scope: the backend call path only (a Spring service calling Bedrock); everything else is Python
- Compile: `cd 1A/java && mvn -q -DskipTests compile`
- Run (all slices off): `mvn spring-boot:run` (port 8081)
- Enable a slice: `--a.guardrails.enabled=true` (or env `A_GUARDRAILS_ENABLED=true`)

```text
java/src/main/java/com/lc/a/
  AApplication.java
  shared/                          AwsConfig, Retry
  config/_01bedrock_01converse/    ConverseConfig, ConverseProperties
  api/<comp>/                      ConverseController, GuardrailController
  domain/<comp>/                   records, exceptions
  infra/_04safety_01guardrails/    GuardrailClient
  service/<comp>/                  ConverseService, DemoTools, GuardedChatService
```

| Component | Layers | Status |
| --- | --- | --- |
| `_01bedrock_01converse` | config, api, domain, service | ✅ A-010 |
| `_04safety_01guardrails` | api, domain, infra, service | ✅ A-040 |

### Python

- Project: `python/` — one FastAPI project, Python 3.11+, the primary 1A language
- Windows: `cd 1A\python; py -m venv .venv; .venv\Scripts\activate; pip install -e .`
- Linux/macOS: `cd 1A/python && python -m venv .venv && . .venv/bin/activate && pip install -e .`
- Check: `python -m compileall -q app`
- Run: `uvicorn app.main:app --reload --port 8001`; enable slices with `A_ENABLED=converse,guardrails`
- Slice settings: env prefix `A_<SLICE>_` (e.g. `A_GUARDRAILS_GUARDRAIL_ID`), defined in `app/config/_<comp>.py`

```text
python/app/
  main.py                            SLICES: A_ENABLED name -> module name
  shared/                            config.py, aws.py, retry.py
  config/_04safety_01guardrails.py   pydantic settings
  api/ domain/ infra/ service/       one _<comp>.py per layer
  service/_02rag_01embeddings/       similarity.py   (helper packages)
  service/_02rag_03chunking/         chunkers.py
  infra/_02rag_03chunking/           bedrock_config.py
  service/_04safety_03evaluations/   __init__.py (service) + metrics.py
```

| Component | `A_ENABLED` | Status |
| --- | --- | --- |
| `_01bedrock_01converse` | `converse` | ✅ A-010 |
| `_01bedrock_02customization` | `customization` | ✅ A-011 |
| `_01bedrock_03prompt_management` | `prompts` | ✅ A-012 |
| `_01bedrock_04prompt_flows` | `flows` | ✅ A-013 |
| `_01bedrock_05prompt_engineering` | `prompting` | ✅ A-014 |
| `_02rag_01embeddings` | `embeddings` | ✅ A-020 |

| Component | `A_ENABLED` | Status |
| --- | --- | --- |
| `_02rag_02opensearch` | `opensearch` | ✅ A-021 |
| `_02rag_03chunking` | `chunking` | ✅ A-022 |
| `_02rag_04knowledge_bases` | `kb` | ✅ A-023 |
| `_03data_01data_automation` | `bda` | ✅ A-030 |
| `_03data_02glue_data_quality` | `glue_dq` | ✅ A-031 |
| `_03data_03transcribe` | `transcribe` | ✅ A-032 |

| Component | `A_ENABLED` | Status |
| --- | --- | --- |
| `_03data_04comprehend` | `comprehend` | ✅ A-033 |
| `_04safety_01guardrails` | `guardrails` | ✅ A-040 |
| `_04safety_02pii_redaction` | `pii` | ✅ A-041 |
| `_04safety_03evaluations` | `evals` | ✅ A-042 |
| `_05ops_01observability` | `observability` | ✅ A-050 |
