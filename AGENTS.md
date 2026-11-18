# AGENTS

> Operating instructions for local agents working in this repository.
> Last updated: 2026-11-18

## Index

- [Local Agent Instructions](#local-agent-instructions)
- [Project Understanding](#project-understanding)
- [Repo Structure](#repo-structure)
- [Global Rules](#global-rules)
- [Oracle Loop Status](#oracle-loop-status-updated-2026-09-09)
- [Topic Files](#topic-files)
- [Update Rule](#update-rule-update-ai)
- [Message Log Rule](#message-log-rule)
- [Agent Naming](#agent-naming)
- [Skill Naming](#skill-naming)
- [LeetCode Notes and Solutions Guide](#leetcode-notes--solutions-guide)

## Local Agent Instructions

### Role

- Codex handles local coding and documentation.
- Claude is a separate claude.ai project that owns:
  - Project management.
  - Syncing.
  - Job tracking.
  - Scheduling.

### Before Any Task

1. Read `D:\2Alfred\1D\AGENTS.md`.
2. Read `D:\2Alfred\1D\0sys\rule-Agent Instructions.md` in full.
   - This file is the source of truth for the local agent workflow.
3. If a required path is missing, list `D:\2Alfred\1D` and locate the current file.
   - The actual local files and paths take precedence.
   - Never guess a path.
4. Read these files under `D:\2Alfred\1D\0sys` only as needed:
   - `rule-Doc Gen Format.md` for documentation format.
   - `1sys.md` for system and sync rules.
   - `0me.md` for user facts.
   - `Dictionary.md` for user abbreviations.

### Hard Rules

- These rules apply even when the Alfred files are unreachable.
- Follow the Git rules under [Global Rules](#global-rules).
- Use only the shell or scripts for local file work.
  - Never open Explorer or any file or folder window.
- Delete files only when the user explicitly asks.
  - If a file needs to be removed from its current location, move it to `_to_delete/` in the same folder and tell the user.
- Edit the existing document in place.
  - Keep one copy of each document.
- Treat these Claude-owned paths under `D:\2Alfred\1D` as read-only:
  - `0sys\*`
  - `1Log` (`0sys\1Log.md`)
  - `1BP` (`1OAA\1BP.md`)
  - `1klg-map` (`1OAA\1klg-map.md`)
  - `1T\oi.md`
  - `1T\jd.md` and `1T\jd\`
  - `1T\1bq\2bq-itv.md`
  - `zTN\0TN-log.md`
- For each file created, moved, renamed, or deleted in `1D`, queue one line in `D:\1lc\back-to-claude.md`.
  - Add it under `## Queue`, newest first.
  - Format the line as `yymmdd-hh:mm · <what changed>`.
  - Claude picks it up from the queue.
- Never print or commit API keys.

### Style

- Reply in Chinese when the user writes Chinese.
- Reply in English when the user writes English.
- Keep technical terms in English.
- Write docs in Markdown.
  - Start with a linked index.
  - Use bullets with one idea per line.
  - Give the plain idea before the mechanism.
  - Use status emojis consistently, such as ✅ verified, ❌ incorrect, and ⚠️ needs confirmation.
  - Link the item or question text directly to its detail.
  - Omit a separate `Where` column.
  - When details repeat the same fields, group by topic and use one row per item.
  - For each company’s interview questions, use two detail tables in order:
    1. Behavioral questions (BQ).
    2. Technical questions.
  - Preserve what I said, feedback, the better answer, and follow-ups in distinct columns.
- Start replies with the answer.
  - Skip preambles and recaps.
- Be factual.
  - Correct the user directly when a claim is wrong.

### User Profile

- Backend software engineer with about five years of experience.
  - Java 17
  - Spring Boot
  - Python
  - Amazon Web Services (AWS)
- Interview targets
  - Google L4
  - Amazon SDE II
  - Meta E4
- Preparation priorities
  - Coding
  - System design

## Project Understanding

This repository is mostly:

- LeetCode training solutions + logs under `24_G/` and `26U/`
- System design prep under `1sd/`

Goal: reach Google L4 interview-ready depth (with L5 visibility) using structured practice artifacts.

## Repo Structure

- `26U/`: topic notes + `26u-log.md`
- `24_G/`: historical LeetCode solutions
- `1sd/`: system design prep (merged from old `1sd` + `1sd2` on 2026-11-13)
  - Top-level docs use a single-digit prefix with no dot: `1sd.md` (flow), `2messaging.md`, `3persistence.md`, `3storage-by-question.md`, `4api.md`, `5reliability-security.md`, `6lld.md`, `1qs.md`; a `1` suffix marks the Chinese copy (`1sd1.md`, `2messaging1.md`)
  - `1sd/hello-interview/`: Hello Interview video docs (`hiNN.name-r.md` raw, `hiNN.name.md` own design), `sd-img/`, `_src/`
  - `1sd/_tools/`: video-doc scripts (`yt-excal.js`)
  - `1sd/1sd02/`: older knowledge graph (`00.base/`, domain question packets)
- `1A/`: AI and agentic-AI knowledge docs (`A` = AI / agentic AI, `klg` = knowledge/concepts); default home for any A-klg request, e.g. `1A/1.aa-msg.md` (agent component messaging)
  - Knowledge + code tree mirrors `1x/` (shared `AGENTS.md`); knowledge docs live in `1A/a-md/` (renamed from `x-md/` on 2026-11-14), code blocks mainly Python, no Java blocks
  - Also holds `A/` (agent chat apps), `claudecode/`, `mcp/`, and `apis` (local keys, gitignored, never commit)
- `2de/`: data engineering (Databricks, Spark, Glue, Snowflake, k8s, ...), moved from the retired `1sde/`; to be reorganized later
  - Knowledge topics from `1sde/` now migrate into `1x/x-md/` groups
- `1x/`: knowledge + code (`X` = standalone concepts): `x-md/<group>/` flat concept files with Java + Python blocks (groups `00java` `01core` `02messaging` `03db` `04dissys` `05analytics` `06framework`), `ddd/` sample projects, `java/` + `python/` (layer-first, `_03db_01aurora` packages), `terraform/` (project with `envs/` + `modules/`); manifests `x.md`, `task.md` (Queue / Backlog / Finish + Java/Python guide), `1tf.md`
  - `1x/AGENTS.md` and `1A/AGENTS.md` are one shared rule file kept byte-identical; edit one → copy to the other (`cmp` to verify)
  - Work in `1x/` → `1x` column of its §1 table; work in `1A/` → `1A` column
- `back-to-claude.md`: message log the user writes from the IDE or locally to send back to Claude
  - Two tiers: `## Queue` and `## Finish`
  - Local agents (IDE, Claude Code, Codex) write only to Queue, newest on top: `yymmdd-hh:mm · <ask>`
  - Claude Cowork acts on Queue entries and moves each to Finish with ✅ + one-line result
- `1o/`: Oracle OCI PKI loop prep (`0.1o.md` loop/role notes, `1.coding/`, `2.sd/` ranked system-design bank, `3.bq.md`, `4.1o-arch.md`)
- `.agents/rules.md`: knowledge-file authoring rules (format, method, doc structure, question format, quality bar, topic pair rule)
- `CLAUDE.md`: Claude Code entry point; imports `AGENTS.md` and `.agents/rules.md` (there is no `.claude/` dir; all skills live in `.agents/skills/`)
- `.agents/skills/`: official repository-scoped reusable workflows (`verb-object` naming)
- `AGENTS.md` files: durable global or directory-scoped role and workflow instructions
- `msg-log.md`: prepend one row per chat

## Global Rules

- Push only when the user explicitly says "push" in the current message.
  - Commit only when asked; a finished task, a passing check, or an earlier "push" never implies a new push.

- Codex and Claude Code share one rule tree: `AGENTS.md` + `.agents/` (rules, skills); `CLAUDE.md` only imports it.
  - Follow the [local agent instructions](#local-agent-instructions) first.
  - Use `.agents/rules.md` for repository-specific content and formatting rules.
  - Skills live only in `.agents/skills/`; never recreate `.claude/skills/`.
  - Persist durable instructions in `AGENTS.md` (and the closest scoped `AGENTS.md`), not in `CLAUDE.md`.
- Keep quality bar high for Google-style interviews.
- Prefer depth + tradeoffs + failure handling over shallow summaries.
- Use index-first, details-later structure in knowledge docs.
- For **every Markdown draft and update**, apply `.agents/rules.md` §3 before writing and review the changed content against it before finishing.
  - Use layered bullets for parallel concepts, statements, and keywords; give each its own line, including keyword-level siblings.
  - Split multiple sentences into separate lines; nest supporting details beneath their parent concept.
  - Write explanatory prose as nested bullets instead of long paragraphs.
  - Use standalone arrow lines for flows: `→` for the next action or step, `⇒` for a consequence, and `↔` only for a bidirectional interaction.
  - Never combine a bullet marker with a flow arrow; preserve separate rendered lines with Markdown hard breaks.
  - Preserve tables, code blocks, headings, and explicitly required specialized layouts.
- In knowledge notes, use knowledge sections plus interview questions, with an L4 baseline and additive L5 extras for each item when that format is requested.
- For pure-core-Java concurrency guides, use Java language and Java SE/JDK APIs without external libraries.
  - Present a prioritized concept catalog before concept snippets and grouped application cases.
  - Give each case its context, invariant, flow, core code, composed primitives, and failure boundaries.
  - Label Java release requirements and preview APIs; distinguish JDBC interfaces from the database/driver needed to execute them.
- For concept/implementation document pairs, keep implementation code in the implementation companion.
  - Keep conceptual diagrams and interview explanations in the concept file.
  - Precede every implementation item with pseudocode or a semantic arrow flow.
  - Apply the same ordering to variants and follow-ups before their Python/Java code pair.
- When generating or updating any knowledge file (system design, technology deep dive, interview notes), read and follow `.agents/rules.md` (format, mechanism-first method, comparison rule, doc structure, question format, quality bar).
- When the user says `in xx/{topic}/ explain {topic}`, generate the two-file pair defined in `.agents/rules.md` §10: `{topic}.md` (concept + 30–50 L4/L5 questions) and `{topic}1.md` (Python + Java/Spring Boot implementation snippets, same section order).
- When the user writes `++:`, treat the following text as durable instructions/rules to add to `AGENTS.md` and any relevant workflow file.
- For design patterns (`1x` `01core.02patterns`), keep the requested catalog in one guide.
  - Group the 23 GoF patterns by type in classic catalog order.
  - Explain each pattern's:
    - Problem and mechanism.
    - Everyday analogy.
    - Common uses.
    - Pros and cons.
  - Follow its explanation with Java, then Python, using classic examples and meaningful variations.
  - Connect relevant variations to production concerns such as transactions, idempotency, and ACID boundaries.

## Oracle Loop Status (updated 2026-09-09)

- Round 1 (HackerRank coding) is passed.
- Final round is scheduled next: 4 rounds in about 4 hours.
  - 2 system design rounds.
  - 1 bar-raiser round (key interviewer / "bartender").
  - 1 coding round.
- Preparation focus is **system design** in `1o/2.sd/`.
  - Goal: pass the SD rounds and sound like a solid IC3 at minimum, with IC4-level signals where they cost nothing.
  - The req targets IC3; IC4 is unlikely to be negotiable, but prepare to the higher bar to raise the pass probability.
  - Label depth in the Oracle bank as `IC3 baseline` and `IC4 stretch` (prep labels, not Oracle's official rubric).
  - Every SD answer must make sense end to end: mechanism, numbers that force decisions, failure behavior, and tradeoffs with flip conditions.
- Question files under `1o/2.sd/` follow the scoped `1o/2.sd/AGENTS.md` (naming, structure, quality checklist).

## Topic Files

- `26U/1.sw.md`: sliding window (`sw`)
- `26U/0.nc150-java.md`: Java syntax toolkit + NeetCode 150 in Java (converted from `26U/0.nc150.md`)
- `26U/1.java-oop.md`: Java OOP / object-oriented design interview questions
- `26U/1.ds-design-java.md`: data structure design in Java (converted from `26U/1.ds-design.md`), plus a `## Synchronization` section of concurrent-design questions

## Update Rule (`update-ai`)

For every chat:

1. Check if user added durable instructions.
2. Persist global rules in `AGENTS.md`.
3. Persist role- or directory-specific rules in the closest applicable `AGENTS.md`.
4. Persist reusable workflow rules in `.agents/skills/*/SKILL.md`.
5. Keep edits minimal and non-duplicative.

## Message Log Rule

For every chat, prepend to `msg-log.md` with:

- `time` = `yymmdd-hh:mm`
- `user-input` short ask summary
- `response` concise result summary

## Agent Naming

Use real roles, preferably `-ist` when natural. Example: `engineer`, `product-manager`, `strategist`, `architect`.

## Skill Naming

Use `verb-object` format. Example: `push-git`, `update-ai`, `ask-sd-question`.

## LeetCode Notes + Solutions Guide

(From old `INSTRUCTIONS.md`, moved here.)

### Index

Track weekly additions with the `常` table in this file context; weeks start Monday.

| Month | Total | W1  | W2  | W3  | W4  | W5  |
| ----- | ----- | --- | --- | --- | --- | --- |
| Jan   | 71    | 0   | 0   | 13  | 58  | 0   |
| Feb   | 21    | 21  | 0   | 0   | 0   | 0   |

### Core conventions

- Keep topic files structured and indexed.
- When updating questions, update both index and solution block anchors.
- Work relative to `26U/` and log updates in `26U/26u-log.md`.
- Similar/extended questions go below parent in index and solution area.

### Content Update Patterns

- If the user provides a fully formatted question, keep the index entry and solution block aligned with repo conventions.
- If the user pastes raw question details into a topic file and says `update this file` or `update`, find newly added questions in the detail section, normalize their format, add matching entries to the top index, and keep solution order aligned with the index.
- For every chat request related to a format rule, add the rule to the proper place in `AGENTS.md`, mirror it into the relevant workflow file when applicable, then apply it to the current file.
- In a single topic file, both the index section and details/solutions section must be grouped by difficulty in this order: `### Hard`, `### Medium`, `### Easy`.
- When the user appends a new question to a specific detail difficulty section, append the matching index entry to that same difficulty section; if the question is placed under the wrong difficulty, move it to the correct difficulty without asking.
- After formatting a fully documented new question, prepend its linked bullet to the current day in `26U/0.26u-log.md` and refresh both summary tables.
- If the user says `update`, `update record`, or `update log`, add every manually provided question to today's section in `26U/0.26u-log.md`, and add individually edited solution code to the date indicated by the file's recent modification timestamp.
- Inspect solution changes from the past few days when updating the record; do not log bulk whole-file/list additions requested as an entire-file update (for example, adding a complete prefix-sum list).
- If the user manually inserts raw log items under a day in `26U/0.26u-log.md`, preserve the user-provided date, normalize only the question entries, and refresh both summary tables.

### File layout

1. Title
2. Index (`## Index` or `## Category`)
3. `## Solutions (Python)`
4. Optional notes/logs

### Index format

Each entry: 3 lines + blank line

1. `[E/M/H] [N. Name](#lc-XXXX)` with a Markdown hard break (`two trailing spaces`); the link must target that question's detail anchor in the same topic file
2. Two-space short description with a Markdown hard break (`two trailing spaces`)
3. Two-space backtick tags
4. Blank line

Anchors in solutions must match: `<a id="lc-XXXX"></a>`.

### Solution block format

1. `<a id="lc-XXXX"></a>`
2. `#### N. [Title](https://leetcode.com/problems/slug/) [E/M/H]`; the title link must target the LeetCode problem page
3. Plain description line with a Markdown hard break (`two trailing spaces`), no bullet
4. Backtick tags line

Add `##### Approach 1: ...`, keep 2-3 approaches max, and runnable `class Solution:`.
End each code block with `# Time: ..., Space: ...`.

- In Python solutions, use built-in generic annotations such as `list[int]`; do not import or use `typing.List`.
- Start Python code on the line immediately after every opening Python code fence; do not insert a blank line after the opening fence.
- Place the `# Time: ..., Space: ...` comment immediately after the final code line; do not insert a blank line before it.
- Use ordinary dictionaries with `dict.get` or `setdefault`; do not import or use `defaultdict` in Python examples.

### Additional rules

- When a topic file aggregates a company question bank plus an extra/OJ list (e.g. `26U/1o/1.coding/1.coding0.md`): within every topic section, list the curated question-bank entries first, then a `---` horizontal rule, then the OJ-only extras — in both the index and the details/solutions section, keeping the two orders aligned.
- Aggregated company-bank files use the standard 3-line index entry format (name link line, then description on its own line, then tags on its own line, each with a Markdown hard break).
- First-hand report files (e.g. `26U/1o/1.coding/0.1p3a.md`): every index entry's name links to its local detail anchor; entries are 3 lines — linked `N. Name` (+ ★★/★★★ after the name when asked by 2/3+ reports; single-report entries unmarked, no ×N counters), then `[E/M]` + 要点, then the anchor link. No ⟂ marker. Preserve user strikethroughs (`~~...~~`) on index entries across any regeneration.
- Solution/detail blocks in those files: `#### N. [Name](url) ...` heading, tags on the immediately following line (no blank line between, two trailing spaces for a hard break), then `Description:`.
- In each block: the interview-primary solution comes first; then a labeled `Follow-up —` section with the second approach / extension / variant (prefer follow-ups actually asked in reports).
- Unless the user specifies a narrower scope, apply coding-question Markdown formatting and link updates to **all coding-question documents in the repository**, including nested folders.
  - Index question titles link to the matching detail anchor in the same file.
  - Detail question titles link to the actual LeetCode problem page.
  - Preserve existing anchors and add missing anchors when required for local navigation.
  - Preserve solution code, question wording, ordering, and source evidence during link-only updates.
  - Keep original sources for custom questions without an actual LeetCode equivalent.
  - Practice logs, inventories, and study plans retain their record/reference role instead of receiving invented solution sections.
- Keep solution order aligned with index.
- Parse pasted tags by splitting on known keywords and removing suffix noise (`N+`).
- `26U/Tiktok.md`: keep `## Category` on top and add matching headings for each indexed question.

### `26U/26u-log.md`

- One bullet per question under date section.
- Format: `- [E/M/H] [N. Title](/26U/<file>.md#lc-XXXX)`
- Log only fully documented solutions.
- When the user says `update log`, update `26U` log content in `26U/0.26u-log.md`.
- Treat `update` and `update record` as log-update requests too: log manually provided questions under today and individually edited solution code under the edit date inferred from recent file timestamps.
- Exclude bulk whole-file/list additions from practice records when the user requested the entire file update; only later individual question/code edits qualify.
- Keep two summary tables at the beginning of `26U/0.26u-log.md`: the monthly cadence table first, then a per-day month table with columns `Month | 1 | 2 | ... | 30 | 31`.
- When updating any day section in `26U/0.26u-log.md`, update both summary tables together.
- If the user manually adds entries under a specific day/date in `26U/0.26u-log.md`, do not change that date; only format the question entries under it.
- When question formatting or entries change within a specific day/date section, update the second table's single-day count for that date first, then recompute the first table's week sums and month total from the updated per-day row.
- Derive the first summary table from the second one: add the per-day counts into Monday-start week buckets for `W1..W5`, and sum the full month total from the same per-day row.
- If a question already exists in `26U/0.26u-log.md`, append ` - 2`, ` - 3`, and so on to the repeated log titles based on chronological attempt count.
- Both summary tables should list months in descending order, with the newest month prepended in future updates.
- If the user manually inserts raw items under a day, format those items into the standard linked bullet format before updating either summary table.
- Treat `26U/0.26u-log.md` as time-descending. If the user manually prepended entries for earlier days, preserve their placement at the top, normalize the affected log format, and then recompute both summary tables at the beginning of the file.

### Git push behavior

- Treat `push` as the `push-git` workflow.
When asked to push: stage all, concise commit message, push to `main` unless user says otherwise.
