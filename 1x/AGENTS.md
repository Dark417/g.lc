# 1x — Agent Rules (Knowledge + Code)

- Scope: everything under `1x/`
- Applies to Claude Code and Codex, from the PC, the cloud, or the phone
- Also obey the root `AGENTS.md` and `.agents/rules.md`
  - This file wins inside `1x/` when the two disagree
- Terraform has its own scoped rules: [terraform/AGENTS.md](terraform/AGENTS.md)

## Index
- [1. What 1x is](#1-what-1x-is)
- [2. Layout](#2-layout)
- [3. Numbering](#3-numbering)
- [4. Manifest: x.md and the Project XMap](#4-manifest-xmd-and-the-project-xmap)
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

## 1. What 1x is
- `X` = knowledge
  - Concepts that exist on their own, not for a specific product
  - Example: Aurora, DynamoDB, Kafka, SOLID, Spring IoC, design patterns
- Two kinds of content
  1. Knowledge docs: pure concepts + interview questions, in `docs/`
  2. Code: runnable-shape examples that show how a component works
     - Java (Spring Boot) in `java/`
     - Python (FastAPI) in `python/`
     - Cloud resources (Terraform) in `terraform/`
- A concept with code carries `[C]` at the start of its manifest line
  - `[C]` = coded
- Which code a concept gets (language rule)
  - General concept (SOLID, DRY, retries, any database) → Java + Python
  - Java-only concept (Spring IoC / DI / AOP, JVM, Java language features) → Java only
  - Python-only concept (asyncio, FastAPI DI, GIL) → Python only
  - Cloud service (Aurora, DynamoDB, S3, Kinesis, MSK, Bedrock, ...) → Terraform is required
    - Add `terraform/GG.CC.<name>.tf` in the same change when it does not exist yet
    - The code never creates cloud resources itself; Terraform declares them
- One doc may hold several sibling concepts
  - Example: `02.01.core-principles.md` = SOLID + general principles + Spring principles
  - Mark each section with its language scope (`Java + Python` or `Java only`)
- Sync model
  - The repo is on GitHub
  - Codex (cloud / phone) works through PRs; the user merges, then pulls on the PC
  - When the PC is on, agents may write directly

## 2. Layout
```
1x/
  AGENTS.md        rules (this file)
  x.md             master manifest = index of all knowledge (mirror: Project 1D/X/XMap.md)
  task.md          to-do queue that Codex can pick from
  1java.md         Java manifest: build guide + slice index
  1python.md       Python manifest: setup guide + slice index
  1tf.md           Terraform manifest: checks + file index
  docs/            knowledge concept docs, GG.CC.<name>.md
  java/            one Maven project (Spring Boot 3, Java 17)
  python/          one FastAPI project (Python 3.11+)
  terraform/       one Terraform root, one component per file
```
- One project per language
  - Every slice lives inside it, flat
  - No per-concept sub-projects, no Maven modules
- Manifests: four files index everything, and every change updates them
  - `x.md` = master manifest (all concepts, status, files)
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

| GG | Group |
|---|---|
| 00 | Foundation (providers, network, KMS, IAM) |
| 01 | Language core (Java, Python) |
| 02 | Design principles and patterns (SOLID, GoF) |
| 03 | Databases and storage |
| 04 | Analytics and warehouses |
| 05 | Streaming and messaging |
| 06 | Frameworks (Spring IoC, FastAPI) |
| 07 | Distributed systems concepts |
| 08 | AI and agents (Bedrock, ADK, RAG, MCP) |

- Where the number appears
  - Doc: `docs/03.01.aurora-postgres.md`
  - Terraform: `terraform/03.01.aurora-postgres.tf`
  - Java package: `com.lc.x.x03_01_aurora` (identifiers can't start with a digit, so prefix `x`, dots become `_`)
  - Python package: `app/x03_01_aurora/`
- Names: lowercase, hyphens in file names, underscores in code identifiers

## 4. Manifest: x.md and the Project XMap
- `x.md` is the master index of everything in 1x
  - Mirror: claude.ai Project doc `1D/X/XMap.md`; the two must stay identical
- Master = `x.md` in git
  - Codex can only reach git, so git is the source of truth
- Sync rule
  - Any agent that changes `x.md` → also updates `1D/X/XMap.md` when it can reach the Project
  - Can't reach the Project (Codex, phone) → leave it; the next Claude session copies `x.md` over
  - Claude, at the start of 1x work → diff the two; copy `x.md` → XMap if they differ
- Shape
  - Index first: groups, each item one line with `[C]` marker and status
  - Detail section per group: files, what the code shows, date, source
  - The user may reorder lines; keep their order, append new items at the end of the group
- Also register coded items in Project `1D/X/0X-log.md` §4 (one row per slice)

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
- `task.md` = the queue; each task has an ID `X-NNN`, status, spec, acceptance criteria
- Picking a task (Codex or Claude)
  → take the top `todo` task unless the user names one  
  → set it to `doing` in the same branch  
  → branch `x/X-NNN-<slug>`  
  → do the work, run §11 checks  
  → in the same PR: mark the task `done`, update `x.md` status, update `1java.md` / `1python.md` / `1tf.md` indexes  
  → PR title `X-NNN: <title>`
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
  - Concept slices with no outbound system (principles, patterns, language core)
    - Organize by concept instead: one sub-package / module per concept group (`solid`, `general`, `spring`)
    - Each concept shows `Violation` then `Fix` side by side, plus a runnable `demo` entry point
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
  - Names match Terraform outputs (e.g. table `x-orders`, stream `x-clicks`)
- A slice is off by default
  - Enabled by config (`x.<slice>.enabled=true` in Java, `X_ENABLED=<slice>,...` in Python)
  - The base app starts with no cloud access

## 9. Java rules
- Java 17 language level, Spring Boot 3, Maven, AWS SDK for Java v2
- Base package `com.lc.x`
  - `com.lc.x.shared` for cross-slice config (AWS clients, retry helper)
  - Slice: `com.lc.x.x03_01_aurora.{api,service,domain,infra}`
- Beans of a slice are guarded with `@ConditionalOnProperty(name = "x.<slice>.enabled", havingValue = "true")`
- Prefer records for models, constructor injection, no Lombok
- Use SDK v2 sync clients unless the concept is async (then show the async client too)

## 10. Python rules
- Python 3.11+, FastAPI, boto3, psycopg 3, confluent-kafka
- Package `app/`
  - `app/shared/` for config and AWS sessions
  - Slice: `app/x03_01_aurora/{domain.py,service.py,infra.py,api.py}`
- Routers are mounted in `app/main.py` only when the slice is in `X_ENABLED`
- Type hints everywhere; `dataclass` or Pydantic for models; built-in generics (`list[int]`)

## 11. Checks before commit or PR
- Python: `cd 1x/python && python -m compileall -q app` and `X_ENABLED=<slices> python -c "from app.main import app; print(sorted(app.openapi()['paths']))"`
  - Use `app.openapi()` paths, not `app.routes[].path`: newer FastAPI puts router objects without `.path` in `app.routes`
- Java: `cd 1x/java && mvn -q -DskipTests compile`
- Terraform: `cd 1x/terraform && terraform fmt -check && terraform init -backend=false && terraform validate`
  - Never `plan` or `apply`
- A check that can't run in the environment (no Maven, no terraform) → say so in the PR body; never claim it passed

## 12. Adding a new component
→ Pick the number: next free `CC` in its group (§3)  
→ Add a `⬜ planned` line to `x.md` (and a task to `task.md` if not doing it now)  
→ Write the doc, then infra showcase, then domain/service/api  
→ Terraform file if it is a cloud component (`terraform/AGENTS.md`)  
→ Run §11 checks  
→ Update `x.md` (✅), the three guides, `0X-log` row, Project XMap

## 13. Delegation
- Split independent slices across subagents when the work is large
- Model by difficulty
  - Complicated (knowledge doc + multi-scenario code, transactions, concurrency) → Opus, high reasoning
  - Simpler (single-service CRUD showcase, manifest edits, formatting) → Sonnet, medium reasoning
- Subagents never edit shared files (`x.md`, `task.md`, the three language manifests, `application.yml`, `app/main.py`)
  - The coordinating agent owns those and merges once all slices land

