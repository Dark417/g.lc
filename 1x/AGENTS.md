# AGENTS — 1x and 1A Shared Rules

> One rule file for both knowledge + code workspaces, `1x/` (general tech) and `1A/` (AI on AWS).

- Applies to Claude Code and Codex, from the PC, the cloud, or the phone
- Also obey the root `AGENTS.md` and `.agents/rules.md`
  - This file wins inside `1x/` and `1A/` when they disagree
- Terraform has its own scoped rules: `terraform/AGENTS.md` in each workspace

## Index

- [0. Sync Rule](#0-sync-rule)
- [1. Workspaces](#1-workspaces)
- [2. What A Workspace Holds](#2-what-a-workspace-holds)
- [3. Layout](#3-layout)
- [4. Naming](#4-naming)
- [5. Manifest And Project Mirror](#5-manifest-and-project-mirror)
- [6. Status And The Finish Rule](#6-status-and-the-finish-rule)
- [7. task.md Protocol](#7-taskmd-protocol)
- [8. Knowledge Docs In x-md](#8-knowledge-docs-in-x-md)
- [9. Code Rules: Shared](#9-code-rules-shared)
- [10. Java Rules](#10-java-rules)
- [11. Python Rules](#11-python-rules)
- [12. Terraform Rules](#12-terraform-rules)
- [13. Checks Before Commit Or PR](#13-checks-before-commit-or-pr)
- [14. Adding A New Component](#14-adding-a-new-component)
- [15. Delegation](#15-delegation)

---

## 0. Sync Rule

`1x/AGENTS.md` and `1A/AGENTS.md` are the same file, kept byte-identical.

- Edit either one → copy it over the other in the same change
  → `cp 1x/AGENTS.md 1A/AGENTS.md` (or the reverse)  
  → verify with `cmp 1x/AGENTS.md 1A/AGENTS.md`
- Workspace differences live only in the §1 table and in `1A`-/`1x`-tagged bullets
  - Never fork the file into two diverging versions
- Same for `terraform/AGENTS.md`: keep the two copies aligned in rules; only names differ

## 1. Workspaces

Pick the column of the folder you are working in; every other rule is shared.

| Item | `1x/` | `1A/` |
| --- | --- | --- |
| Meaning | `X` = standalone tech knowledge | `A` = AI knowledge, mostly agentic AI on AWS |
| Manifest | `x.md` (mirror `1D/X/XMap.md`) | `a.md` (mirror `1D/A/AMap.md`) + lecture map |
| Task ID / branch | `X-NNN` · `x/X-NNN-<slug>` | `A-NNN` · `a/A-NNN-<slug>` |
| Primary language | Java + Python, equal | Python; Java only on backend call paths |
| Knowledge doc folder | `x-md/` | `a-md/` |
| Knowledge doc code blocks | Java first, then Python | Python only, no Java blocks |

| Item | `1x/` | `1A/` |
| --- | --- | --- |
| Java base package | `com.lc.x` | `com.lc.a` |
| Slice switch | `x.<slice>.enabled` · `X_ENABLED` | `a.<slice>.enabled` · `A_ENABLED` |
| AWS name prefix | `x-<env>-<thing>` | `a-<env>-<thing>` |
| Ports | 8080 · 8000 | 8081 · 8001 |
| Source | chats, hiNN questions | AIP-C01 lectures (`X.AIP-C01/`) |

- When working in `1x/` → use the `1x` column, `x.md`, `X-NNN`
- When working in `1A/` → use the `1A` column, `a.md`, `A-NNN`
  - Older notes at the `1A/` root (`1.aa-msg.md`, `X.AIP-C01/`, ...) keep their own formats

## 2. What A Workspace Holds

Each workspace pairs knowledge docs with code that demonstrates them.

- ✅ **Knowledge docs**: concept explained, then code blocks, in `x-md/`
- ✅ **Code**: runnable-shape examples of how a component works
  - Java (Spring Boot) in `java/`
  - Python (FastAPI) in `python/`
  - Cloud resources (Terraform) in `terraform/`
- A concept with code carries `[C]` in the manifest line
- Which code a concept gets
  - `1x` general concept (SOLID, retries, any database) → Java + Python
  - `1x` Java-only concept (Spring IoC, JVM) → Java only
  - `1x` Python-only concept (asyncio, FastAPI DI) → Python only
  - `1A` every coded concept → Python
    - Java only where a Spring backend calls it (today: Converse, Guardrails)
  - Cloud service → Terraform module is required, in the same change
    - The code never creates cloud resources; Terraform declares them
- Sync model
  - Codex (cloud / phone) works through PRs; the user merges, then pulls on the PC
  - When the PC is on, agents may write directly

## 3. Layout

Both workspaces share one layout.

```text
1x/ or 1A/
  AGENTS.md     shared rules (this file, synced)
  x.md | a.md   master manifest
  task.md       Index, Queue, Backlog, Finish + Java/Python guide
  1tf.md        Terraform guide: checks + module index
  x-md/ | a-md/ knowledge docs, one folder per group, flat files
  java/         one Maven project, layer-first packages
  python/       one FastAPI project, layer-first packages
  terraform/    one Terraform project: base files, envs/, modules/
```

- One project per language, no per-concept sub-projects
- Manifests index everything; every change updates them
  - `x.md` / `a.md`: all concepts, status, files
  - `task.md`: tasks plus the Java and Python slice tables
  - `1tf.md`: one row per Terraform module
  - A slice is not finished until each manifest it touches lists it

## 4. Naming

Every item has a group and a component number, written two ways.

- **Group**: two digits + short name, e.g. `03db`
- **Component**: two digits + short name, e.g. `01aurora`
- Markdown names use a dot: `03db.01aurora`
- Code names use an underscore: `03db_01aurora`
  - Java packages and Python modules need a leading underscore: `_03db_01aurora`
    - Why: identifiers cannot start with a digit
  - Terraform module dir `modules/03db_01aurora/`, block label `_03db_01aurora`
- Multi-word names
  - Markdown: hyphen, `01bedrock.03prompt-management`
  - Code: underscore, `_01bedrock_03prompt_management`
- Sub-concept files add a third number: full name `03db.01aurora.04locking`
- Knowledge doc file names (x-md) drop what the folder already says
  - `1x`: drop the group prefix → `x-md/03db/01aurora.04locking.md`
    - Group with one component (`01core`): drop the component too → `x-md/01core/01srp.md`
    - Why: the folder already names the group; short names read faster
  - `1A`: full name for now → `a-md/01bedrock/01bedrock.01converse.07tool-use.md`
  - The H1 keeps the full name: `# 03db.01aurora.04locking Locking`
  - Code names (Java, Python, Terraform) keep the full group + component
- Rename rule
  - Every file follows this naming; a mismatch is a bug to fix
  - Renaming → `git mv`, then update every reference (manifests, links, imports, Terraform)
  - Extend groups at the end; renumber only on the user's word, then rename everything in one change

### 4.1 Groups In 1x

| GG | Group | Covers |
| --- | --- | --- |
| 00 | `00java` | Java language and JVM core |
| 01 | `01core` | Design principles and patterns |
| 02 | `02messaging` | Kinesis, Kafka, SQS / SNS, Flink |
| 03 | `03db` | Databases and storage (Aurora, DynamoDB, S3, MongoDB) |

| GG | Group | Covers |
| --- | --- | --- |
| 04 | `04dissys` | Distributed systems concepts, tech choice |
| 05 | `05analytics` | Analytics and warehouses (Athena, Redshift) |
| 06 | `06framework` | Spring IoC, FastAPI |
| — | `ddd/` | Domain-driven design sample projects (Stripe POCs), outside numbering |

### 4.2 Groups In 1A

| GG | Group | AIP-C01 lectures |
| --- | --- | --- |
| 01 | `01bedrock` | 7–12, 22, 27–34 |
| 02 | `02rag` | 13–21, 53–59 |
| 03 | `03data` | 38–39, 43–52 |
| 04 | `04safety` | 21, 23–26, 34, 49–51 |

| GG | Group | AIP-C01 lectures |
| --- | --- | --- |
| 05 | `05ops` | 46 (later 127–136, 195–206) |
| 06 | `06agents` (planned) | 97–125 |
| 07 | `07integration` (planned) | 152–187 |
| 08 | `08governance` (planned) | 188–234 |

- `1A` other folders, outside numbering: `A/` (agent chat apps), `claudecode/`, `mcp/`, `apis` (local keys, gitignored)

### 4.3 Terraform Foundation

- Foundation modules have no number: `base_<name>`, e.g. `base_network`, `base_kms`, `base_iam`
  - Infra only, no x-md; lecture 5 billing alarm in 1A is `base_billing_alarm`

### 4.4 Where A Name Appears

| Place | Example |
| --- | --- |
| Knowledge doc (1x) | `x-md/03db/01aurora.04locking.md` |
| Java | `com.lc.x.infra._03db_01aurora.AuroraJdbcRepository` |
| Python | `app/infra/_03db_01aurora.py` |
| Terraform | `terraform/modules/03db_01aurora/main.tf` |

## 5. Manifest And Project Mirror

`x.md` (1x) or `a.md` (1A) is the master index of the workspace.

- Master = the file in git
  - Codex can only reach git, so git is the source of truth
- Mirror = the claude.ai Project doc (§1 table); keep identical
  - Changed the manifest and can reach the Project → update the mirror too
  - Can't reach it (Codex, phone) → leave it; the next Claude session copies it over
  - Claude at the start of workspace work → diff the two; copy master → mirror
- Shape
  - Index first: groups, each item one line with `[C]` and status
  - Detail section per group: files, what the code shows, date, source
  - The user may reorder lines; keep their order, append new items at the group end
- Register coded items in the Project log (`1D/X/0X-log.md` or `1D/A/0A-log.md`) §4
- `1A` only: the lecture map covers every lecture in scope (coded, doc only, or skipped + why)

## 6. Status And The Finish Rule

Status marks are shared by manifests and task tables.

| Mark | Meaning |
| --- | --- |
| ⬜ planned | Listed, nothing written |
| 🔧 wip | Started, incomplete |
| ✅ gen | Generated and passes §13 checks = **finish** |
| ▶ ran | Executed against real AWS / local containers |
| 🎓 reviewed | The user read it and can explain it |

- An item is **finished** (✅) when any of these holds
  - Its PR is merged
  - Local work is done and §13 checks pass: the agent marks it itself
  - The user says it is finished
- `ran` and `reviewed` are set only by the user, or on the user's explicit word

## 7. task.md Protocol

`task.md` is the work queue; it reads like an index.

- Sections, in this fixed order
  1. `## Index`: grouped links to every Queue task, then Backlog and Finish
  2. `## Queue`: `todo` / `doing` tasks with spec and finish criteria
  3. `## Backlog`: ideas not yet specified
  4. `## Finish`: finished tasks, newest first, with date
  5. `## Guide`: Java and Python build/run notes + slice tables
- User adds new text to `task.md` (any wording, anywhere)
  → turn it into a task with the next free ID  
  → put it in Queue (or Backlog if it is only an idea)  
  → add its line to the Index
- Picking a task
  → take the top `todo` in Queue, unless the user names one  
  → set it to `doing`; branch per §1  
  → do the work, run §13 checks  
  → PR title `<ID>: <title>`
- ✅ After each round of coding
  → every task that is finished leaves Queue  
  → it moves to the top of Finish as `YYYY-MM-DD · <ID> <title>: <one-line result>`  
  → its Index line moves under Finish  
  → update the manifest status and the Guide slice tables in the same change
- Never delete tasks; unfinished work stays in Queue as `doing`

## 8. Knowledge Docs In x-md

Knowledge lives in `x-md/<group>/` (`1A`: `a-md/<group>/`) as many flat files, one per sub-concept.

- Files of one component (`1x` short names, §4; `1A` keeps the `01bedrock.` prefix)
  - `01aurora.00index.md`: one-minute version, grouped index of all files, Code map
  - `01aurora.01<slug>.md` … `NN<slug>.md`: one sub-concept each
  - `01aurora.98tradeoffs.md`: when to use, knobs, comparison, failure modes
  - `01aurora.99interview.md`: interview questions, L4 + L5 extra
  - Single-component group (`01core`): `00index.md`, `01srp.md` … `99interview.md`
- Every file: index first, then details
  - `# <full md name> <Title>` → `> purpose` → `## Index` (grouped, layered, linked) → numbered sections
- Every concept: explain first, then code, then the catch
  - Explanation: layered bullets, plain idea before the technical name
  - Code blocks
    - `1x`: Java first, then Python
    - `1A`: Python only, even where Java code exists
  - First line of each block names the real file: `// infra/_03db_01aurora/AuroraJdbcRepository.java`
  - Excerpts come from the repo code with the same names; comment the non-obvious lines
  - No repo code for it → short snippet marked `illustrative`
- The Code map in `00index` links each concept file ↔ Java class/method ↔ Python function
  - Code changes → update the matching x-md block and Code map in the same change
- Formatting: `.agents/rules.md` §3 and the `doc-formatting` skill
  - Status and checklist marker ✅ is welcome
  - Every claim carries its limit; numbers are sourced or marked "order of magnitude"

## 9. Code Rules: Shared

Code is layer-first in both languages: layer on top, one component inside each layer.

```text
config   component settings: *Config, *Properties, pydantic settings
api      inbound adapter: REST endpoints, thin, HTTP <-> service
service  application: use cases, transactions, orchestration
domain   core: models + ports (interfaces), no SDK imports
infra    outbound adapter: the SDK / driver code = the showcase
concept  pure-concept slices with no outbound system (principles, patterns)
shared   cross-component helpers (AWS clients, retry)
```

- Required per slice: `domain` + `infra`; others only where they teach something
- Pure-concept slices go in `concept/<comp>/`
  - Each concept shows `Violation` then `Fix`, plus a runnable demo
- `1A` stores an AI component needs (vectors, history, eval results)
  - Port in `domain`, one adapter in `infra`; the store itself is only Terraform
- `1A` configuration as code
  - Every console screen the course demos → the same settings via SDK and Terraform
- Showcase style
  - One public method per concept or scenario
  - Each method opens with a 1–3 line comment: what, when, the catch
  - Methods grouped with banner comments in x-md order
  - Retries, pagination, partial failures, idempotency are shown, not skipped
- Never run against AWS
  - Code compiles; all AWS resources are assumed to exist (Terraform)
- Config only from environment / application config
  - No secrets, account IDs, or real endpoints
  - Names match Terraform outputs
- A slice is off by default; the base app starts with no cloud access

## 10. Java Rules

- Java 17 language level, Spring Boot 3, Maven, AWS SDK for Java v2
- Packages: `<base>.<layer>._<comp>`, e.g. `com.lc.x.service._03db_01aurora`
  - `<base>.shared` for cross-component config and the retry helper
  - Resources per component: `src/main/resources/_03db_01aurora/`
- Slice beans guarded by `@ConditionalOnProperty(name = "<x|a>.<slice>.enabled", havingValue = "true")`
- Records for models, constructor injection, no Lombok
- SDK v2 sync clients unless the concept is async

## 11. Python Rules

- Python 3.11+, FastAPI, boto3 (+ psycopg 3, confluent-kafka in 1x; opensearch-py in 1A)
- Modules: `app/<layer>/_<comp>.py`, e.g. `app/infra/_03db_01aurora.py`
  - More than one file in a layer → package `app/<layer>/_<comp>/`
  - `app/shared/` for base config and AWS clients
  - `1A` slice settings: `app/config/_<comp>.py` (pydantic-settings, env prefix `A_<SLICE>_`)
- Absolute imports: `from app.domain._03db_01aurora import Order`
- `app/main.py` mounts a router only when its slice is in `X_ENABLED` / `A_ENABLED`
- Type hints everywhere; dataclass or Pydantic models; built-in generics

## 12. Terraform Rules

Each workspace has one Terraform project; details in `terraform/AGENTS.md`.

```text
terraform/
  versions.tf backend.tf providers.tf variables.tf locals.tf main.tf outputs.tf
  envs/      local | dev | uat | prod  .tfvars + .backend.hcl (mock values)
  modules/   <code name>/ main.tf iam.tf variables.tf outputs.tf
```

- Base files hold the project; `main.tf` calls one module per component
- `modules/base_*` = foundation (no number): network, KMS, the shared app role
- One module = one component
  - `main.tf`: the component resources
  - `iam.tf`: that component's IAM roles and policies, all in one file
- Environments: `local`, `dev`, `uat`, `prod`
  - Values differ only through `envs/<env>.tfvars`
  - `local` points at LocalStack; `prod` gets protection, multi-AZ, longer retention
- Never `plan` or `apply`

## 13. Checks Before Commit Or PR

- Python: `cd python && python -m compileall -q app`
  - Then enable all slices and print `sorted(app.openapi()['paths'])`
  - Use `app.openapi()` paths, not `app.routes[].path`
- Java: `cd java && mvn -q -DskipTests compile`
- Terraform: `cd terraform && terraform fmt -check -recursive && terraform init -backend=false && terraform validate`
- AGENTS sync: `cmp 1x/AGENTS.md 1A/AGENTS.md`
- A check that can't run here → say so; never claim it passed

## 14. Adding A New Component

→ Pick the number: next free component in its group (§4)  
→ Add a `⬜ planned` line to the manifest and a Queue task  
→ Write the x-md files, then infra, then domain / service / api  
→ Terraform module if it is a cloud component  
→ Run §13 checks  
→ Finish per §7: manifest ✅, Finish entry, Guide tables, `1tf.md`, Project log + mirror

## 15. Delegation

- Split independent slices across subagents when the work is large
- Model by difficulty
  - Complicated (knowledge + multi-scenario code, transactions, concurrency) → Opus, high reasoning
  - Simpler (CRUD showcase, manifest edits, renames, formatting) → Sonnet, medium reasoning
- Subagents never edit shared files
  - `x.md` / `a.md`, `task.md`, `1tf.md`, `AGENTS.md`, `application.yml`, `app/main.py`, `app/shared/`
  - The coordinating agent owns those and merges once all slices land
