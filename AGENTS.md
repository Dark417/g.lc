# AGENTS

## Project Understanding
This repository is mostly:
- LeetCode training solutions + logs under `24_G/` and `26U/`
- System design prep under `sd/` and `sde/`

Goal: reach Google L4 interview-ready depth (with L5 visibility) using structured practice artifacts.

## Repo Structure
- `26U/`: topic notes + `26u-log.md`
- `24_G/`: historical LeetCode solutions
- `sd/`: system design targets, question bank, flow, and per-question docs
- `sde/`: system design knowledge graph modules
- `.ai/agents/`: role definitions
- `.ai/skills/`: reusable workflows (`verb-object` naming)
- `msg-log.md`: prepend one row per chat

## Global Rules
- Keep quality bar high for Google-style interviews.
- Prefer depth + tradeoffs + failure handling over shallow summaries.
- Use index-first, details-later structure in knowledge docs.

## Update Rule (`update-ai`)
For every chat:
1. Check if user added durable instructions.
2. Persist global rules in `AGENTS.md`.
3. Persist role-specific rules in `.ai/agents/*.md`.
4. Persist workflow rules in `.ai/skills/*/SKILL.md`.
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

| Month | Total | W1 | W2 | W3 | W4 | W5 |
| --- | --- | --- | --- | --- | --- | --- |
| Jan | 71 | 0 | 0 | 13 | 58 | 0 |
| Feb | 21 | 21 | 0 | 0 | 0 | 0 |

### Core conventions
- Keep topic files structured and indexed.
- When updating questions, update both index and solution block anchors.
- Work relative to `26U/` and log updates in `26U/26u-log.md`.
- Similar/extended questions go below parent in index and solution area.

### File layout
1. Title
2. Index (`## Index` or `## Category`)
3. `## Solutions (Python)`
4. Optional notes/logs

### Index format
Each entry: 3 lines + blank line
1. `[E/M/H] [N. Name](https://leetcode.cn/problems/slug/)`
2. Two-space short description
3. Two-space backtick tags
4. Blank line

Anchors in solutions must match: `<a id="lc-XXXX"></a>`.

### Solution block format
1. `<a id="lc-XXXX"></a>`
2. `#### N. [Title](https://leetcode.cn/problems/slug/) [E/M/H]`
3. tags line
4. `-` description

Add `##### Approach 1: ...`, keep 2-3 approaches max, and runnable `class Solution:`.
End each code block with `# Time: ..., Space: ...`.

### Additional rules
- Use `leetcode.com` links in solution titles.
- Keep solution order aligned with index.
- Parse pasted tags by splitting on known keywords and removing suffix noise (`N+`).
- `26U/Tiktok.md`: keep `## Category` on top and add matching headings for each indexed question.

### `26U/26u-log.md`
- One bullet per question under date section.
- Format: `- [E/M/H] [N. Title](/26U/<file>.md#lc-XXXX)`
- Log only fully documented solutions.

### Git push behavior
When asked to push: stage all, concise commit message, push to `main` unless user says otherwise.
