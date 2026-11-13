# 1A — Agent Rules (AI Knowledge + Code)

- Scope: the knowledge + code tree in `1A/` (`AGENTS.md`, `a.md`, `task.md`, the three guides, `docs/`, `java/`, `python/`, `terraform/`)
  - Older notes at the `1A/` root (`1.aa-msg.md`, `X.AIP-C01/`, ...) keep their own formats
- Sibling of `1x/`: same rules and structure, adapted to AI
- Applies to Claude Code and Codex, from the PC, the cloud, or the phone
- Also obey the root `AGENTS.md` and `.agents/rules.md`
  - This file wins inside `1A/` when the two disagree
- Terraform has its own scoped rules: [terraform/AGENTS.md](terraform/AGENTS.md)

## Index
- [1. What 1A is](#1-what-1a-is)
- [2. Layout](#2-layout)
- [3. Numbering](#3-numbering)
- [4. Manifest: a.md and the Project AMap](#4-manifest-amd-and-the-project-amap)
- [5. Status and the done rule](#5-status-and-the-done-rule)
- [6. task.md protocol](#6-taskmd-protocol)
- [7. Knowledge doc rules](#7-knowledge-doc-rules)
- [8. Code rules: shared](#8-code-rules-shared)
- [9. Java rules](#9-java-rules)
- [10. Python rules](#10-python-rules)
- [11. Checks before commit or PR](#11-checks-before-commit-or-pr)
- [12. Adding a new component](#12-adding-a-new-component)
- [13. Delegation](#13-delegation)

---

## 1. What 1A is
- `A` = AI knowledge, usually agentic AI, on AWS
  - Concepts that exist on their own, not for a specific product
  - Example: Converse API, Guardrails, PII redaction, Knowledge Bases, OpenSearch vectors, agents, evaluations
- Source map: the AIP-C01 course lecture list (`X.AIP-C01/`)
  - Lectures are aggregated into concepts; a concept is not one-per-video
  - Intro, logistics, and console-only lectures are skipped; `a.md` §Lecture map records every skip and why
- Two kinds of content
  1. Knowledge docs: pure concepts + interview questions, in `docs/`
  2. Code: runnable-shape examples that show how a component works
     - Python (FastAPI + boto3) in `python/` = the primary language
     - Java (Spring Boot) in `java/` = the backend call path only
     - Cloud resources (Terraform) in `terraform/`
- A concept with code carries `[C]` at the start of its manifest line
  - `[C]` = coded
- Which code a concept gets (language rule)
  - Every coded AI concept → Python
    - Why: the AWS GenAI samples, agent SDKs (Strands, AgentCore), and eval tools are Python-first
  - Java only where a Spring backend calls the component in production
    - Today: `01.01` Converse (incl. streaming) and `04.01` Guardrails (`ApplyGuardrail`, `guardrailConfig`)
    - Add Java for a new concept only when it is on a backend request path
  - Cloud service (Bedrock, OpenSearch, Comprehend, Transcribe, Glue, ...) → Terraform is required
    - Add `terraform/GG.CC.<name>.tf` in the same change when it does not exist yet
    - The code never creates cloud resources itself; Terraform declares them
- One doc may hold several sibling concepts
  - Example: `04.02.pii-redaction.md` = Comprehend PII + Guardrails sensitive-info + Transcribe redaction
  - Mark each section with its language scope (`Python` or `Python + Java`)
- Sync model
  - The repo is on GitHub
  - Codex (cloud / phone) works through PRs; the user merges, then pulls on the PC
  - When the PC is on, agents may write directly

## 2. Layout
```
1A/
  AGENTS.md        rules (this file)
  a.md             master manifest = index of all knowledge + lecture map (mirror: Project 1D/A/AMap.md)
  task.md          to-do queue that Codex can pick from
  1java.md         Java manifest: build guide + slice index
  1python.md       Python manifest: setup guide + slice index
  1tf.md           Terraform manifest: checks + file index
  docs/            knowledge concept docs, GG.CC.<name>.md
  java/            one Maven project (Spring Boot 3, Java 17), backend call path only
  python/          one FastAPI project (Python 3.11+), primary
  terraform/       one Terraform root, one component per file
```
- One project per language
  - Every slice lives inside it, flat
  - No per-concept sub-projects, no Maven modules
- Manifests: four files index everything, and every change updates them
  - `a.md` = master manifest (all concepts, status, files, lecture map)
  - `1java.md`, `1python.md`, `1tf.md` = per-language manifests (one row per slice / `.tf` file)
  - A slice is not done until each manifest it touches lists it
- `docs/` = knowledge concept files only
  - Pure concepts + interview questions; code lives in `java/`, `python/`, `terraform/`

## 3. Numbering
- Plain idea: a two-level number orders every concept, the same in every folder
- Format: `GG.CC.<name>`
  - `GG` = group, two digits
  - `CC` = component inside the group, two digits
  - Optional third level: `GG.CC.SS` (e.g. `03.02.01` = DynamoDB single-table design)
- `00` = foundation that others depend on
  - Created first; mostly Terraform (providers, network, KMS, IAM)
- Group table (extend at the end; never renumber an existing item)

| GG | Group | AIP-C01 lectures |
|---|---|---|
| 00 | Foundation (providers, network, KMS, IAM, billing alarm, data bucket) | 5 |
| 01 | Bedrock core and prompting | 7–12, 22, 27–34 |
| 02 | RAG and vector stores | 13–21, 53–59 |
| 03 | Data for GenAI | 38–39, 43–52 |
| 04 | Safety, PII, and evaluation | 21, 23–26, 34, 49–51 |
| 05 | Operations and observability | 46 (later 127–136, 195–206) |
| 06 | Agents (planned) | 97–125 |
| 07 | Integration and orchestration (planned) | 152–187 |
| 08 | Governance and security (planned) | 188–234 |

- Where the number appears
  - Doc: `docs/04.01.guardrails.md`
  - Terraform: `terraform/04.01.guardrails.tf`
  - Java package: `com.lc.a.a04_01_guardrails` (identifiers can't start with a digit, so prefix `a`, dots become `_`)
  - Python package: `app/a04_01_guardrails/`
- Names: lowercase, hyphens in file names, underscores in code identifiers

## 4. Manifest: a.md and the Project AMap
- `a.md` is the master index of everything in the 1A tree
  - Mirror: claude.ai Project doc `1D/A/AMap.md`; the two must stay identical
- Master = `a.md` in git
  - Codex can only reach git, so git is the source of truth
- Sync rule
  - Any agent that changes `a.md` → also updates `1D/A/AMap.md` when it can reach the Project
  - Can't reach the Project (Codex, phone) → leave it; the next Claude session copies `a.md` over
  - Claude, at the start of 1A work → diff the two; copy `a.md` → AMap if they differ
- Shape
  - Index first: groups, each item one line with `[C]` marker and status
  - Detail section per group: files, what the code shows, date, source
  - The user may reorder lines; keep their order, append new items at the end of the group
- Also register coded items in Project `1D/A/0A-log.md` §4 (one row per slice)
- Lecture map: a table `Lectures | Concept | Treatment (coded / doc only / skipped + why)` covering every lecture in scope

## 5. Status and the done rule
| Mark | Meaning |
|---|---|
| ⬜ planned | Listed, nothing written |
| 🔧 wip | Started, incomplete |
| ✅ gen | Generated and passes §11 checks = **done** |
| ▶ ran | Executed against real AWS / local containers |
| 🎓 reviewed | The user read it and can explain it |

- An item is **done** (✅) when any of these holds
  - Its PR is merged
  - Local work finished and §11 checks pass: the agent marks it itself
  - The user says it is done
- `ran` and `reviewed` are set only by the user, or on the user's explicit word

## 6. task.md protocol
- `task.md` = the queue; each task has an ID `A-NNN`, status, spec, acceptance criteria
- Picking a task (Codex or Claude)
  → take the top `todo` task unless the user names one  
  → set it to `doing` in the same branch  
  → branch `a/A-NNN-<slug>`  
  → do the work, run §11 checks  
  → in the same PR: mark the task `done`, update `a.md` status, update `1java.md` / `1python.md` / `1tf.md` indexes  
  → PR title `A-NNN: <title>`
- New ideas from a chat go to the bottom of `task.md` as `todo`
- Never delete tasks; done tasks move to the Done section with the date

## 7. Knowledge doc rules
- Location: `docs/GG.CC.<name>.md`
- Follow `.agents/rules.md` §3 formatting (layered bullets, standalone arrow lines)
- Shape (compact v1; expand on request)
  ```
  # GG.CC <Topic>
  ## Index
  ## 0. One-minute version   (what, why, how, catch, 🗣)
  ## 1. Concept               (plain idea, picture, mechanism)
  ## 2. When to use / not
  ## 3. Knobs and best practices
  ## 4. Comparison            (table + "Default: X, unless Y")
  ## 5. Failure modes         (Failure | Trigger | Detect | Fix)
  ## 6. Interview questions   (L4 + L5 extra)
  ## 7. Code map              (which method shows which concept)
  ## References
  ```
- Section 0 must stand alone: it is the pre-interview review
- Every claim carries its limit; numbers are sourced (doc + date) or marked "order of magnitude"
- The doc explains; the code demonstrates
  - No long code in docs; link to the method instead (§7 Code map)

## 8. Code rules: shared
- Goal: one place that shows how a component works, end to end
  - Exhaustive over the major functions and scenarios
  - When exhaustive is too much: at least the major usage, and list the gaps in the doc's Code map
- Layers (hexagonal / DDD-lite), same names in Java and Python

```
api      (inbound adapter)  REST endpoints, thin, maps HTTP <-> service
service  (application)      use cases, transactions, orchestration
domain   (core)             models + ports (interfaces), no SDK imports
infra    (outbound adapter) the SDK / driver code = the showcase
```

  - Required per slice: `domain` + `infra`
  - `service` + `api`: only where they teach something (transactions, idempotency, pagination contracts)
  - Pure-logic slices with no outbound system (chunkers, prompt templates, similarity math)
    - `domain` + one logic module is enough; still expose an `api` router in Python
- Databases and other stores the AI component needs (vector store, conversation history, eval results)
  - Write the port (interface) in `domain` and one adapter in `infra`
  - Show how to call it; do not build the store itself beyond its Terraform
- Configuration as code is part of the showcase
  - Every console screen the course demos (guardrail policies, PII rules, chunking, KB data sources)
    → show the same settings through the SDK (`create_*` / `update_*`) and Terraform
  - Name each knob, its allowed values, its default, and what it trades
- Showcase style
  - One public method per concept or scenario
  - Every method starts with a 1–3 line comment: what it shows, when to use it, the catch
  - Group methods with banner comments in the order of the doc
  - Retries, pagination, partial failures, and idempotency are shown, not skipped
- Never run
  - Code is written to compile, not executed against AWS by agents
  - All AWS resources are assumed to exist (they are defined in `terraform/`)
- Config only from environment / application config
  - No secrets, account IDs, or real endpoints in code
  - Names match Terraform outputs (e.g. guardrail `a-guardrail`, collection `a-vectors`)
- A slice is off by default
  - Enabled by config (`a.<slice>.enabled=true` in Java, `A_ENABLED=<slice>,...` in Python)
  - The base app starts with no cloud access

## 9. Java rules
- Java 17 language level, Spring Boot 3, Maven, AWS SDK for Java v2 (`bedrockruntime`, `bedrock`, `bedrockagentruntime`)
- Base package `com.lc.a`
  - `com.lc.a.shared` for cross-slice config (AWS region + credentials, retry helper)
  - Slice: `com.lc.a.a04_01_guardrails.{api,service,domain,infra}`
- Beans of a slice are guarded with `@ConditionalOnProperty(name = "a.<slice>.enabled", havingValue = "true")`
- Prefer records for models, constructor injection, no Lombok
- Use SDK v2 sync clients unless the concept is async (then show the async client too)

## 10. Python rules
- Python 3.11+, FastAPI, boto3, opensearch-py
- Package `app/`
  - `app/shared/` for base config (region, data bucket, default model IDs) and AWS clients
  - Slice: `app/a04_01_guardrails/{config.py,domain.py,service.py,infra.py,api.py}`
  - Slice-specific settings go in the slice's own `config.py` (pydantic-settings, env prefix `A_<SLICE>_`)
- Routers are mounted in `app/main.py` only when the slice is in `A_ENABLED`
- Type hints everywhere; `dataclass` or Pydantic for models; built-in generics (`list[int]`)

## 11. Checks before commit or PR
- Python: `cd 1A/python && python -m compileall -q app` and `A_ENABLED=<slices> python -c "from app.main import app; print(sorted(app.openapi()['paths']))"`
- Java: `cd 1A/java && mvn -q -DskipTests compile`
- Terraform: `cd 1A/terraform && terraform fmt -check && terraform init -backend=false && terraform validate`
  - Never `plan` or `apply`
- A check that can't run in the environment (no Maven, no terraform) → say so in the PR body; never claim it passed

## 12. Adding a new component
→ Pick the number: next free `CC` in its group (§3)  
→ Add a `⬜ planned` line to `a.md` and its lectures to the lecture map (and a task to `task.md` if not doing it now)  
→ Write the doc, then infra showcase, then domain/service/api  
→ Terraform file if it is a cloud component (`terraform/AGENTS.md`)  
→ Run §11 checks  
→ Update `a.md` (✅), the three guides, `0A-log` row, Project AMap

## 13. Delegation
- Split independent slices across subagents when the work is large
- Model by difficulty
  - Complicated (knowledge doc + multi-scenario code, transactions, concurrency) → Opus, high reasoning
  - Simpler (single-service CRUD showcase, manifest edits, formatting) → Sonnet, medium reasoning
- Subagents never edit shared files (`a.md`, `task.md`, the three language manifests, `application.yml`, `app/main.py`, `app/shared/`)
  - The coordinating agent owns those and merges once all slices land

