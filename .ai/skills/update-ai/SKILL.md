---
name: update-ai
description: Persist durable instruction updates into AGENTS.md, agent files, or skill files. Use for every chat to capture reusable rules.
---

# update-ai

1. Review latest user message and current instruction files.
2. Identify durable new rules/patterns.
3. Route updates:
- Global -> `AGENTS.md`
- Role-specific -> `.ai/agents/<role>.md`
- Workflow-specific -> `.ai/skills/<skill>/SKILL.md`
4. Keep edits minimal and avoid duplication.
5. Treat `++:` in a user message as a durable instruction/rule request and persist it to `AGENTS.md` plus any relevant workflow file.
6. For topic-file updates:
- if the user says `update this file` or `update` after adding raw question details, inspect the current topic file detail section for newly added questions
- normalize out-of-sync question details to the standard solution block format
- add matching entries to the top index section
- keep index order aligned with solution order
- for format-rule requests, persist the rule in the proper `AGENTS.md` section, mirror it here when workflow-related, then apply it to the current file
- group both topic-file index and solution/detail sections by `### Hard`, `### Medium`, `### Easy` in that order
- append new questions to the matching difficulty group in both index and details; if the user put a question in the wrong difficulty group, move it to the correct group without asking
- index entries must render as three separate lines by adding Markdown hard breaks after the title/link line and description line
- in a single topic Markdown file, each index title must link to its matching local `#lc-XXXX` detail anchor; each solution/detail title must link to the problem on `leetcode.com`
- solution blocks must place the plain description line directly under the title with a Markdown hard break, then the tags line, with no bullet before the description
- Python solution blocks must use built-in generic annotations such as `list[int]` and must not import or use `typing.List`
- Python code must start immediately after the opening Python code fence with no intervening blank line
- the `# Time: ..., Space: ...` comment must immediately follow the final code line with no intervening blank line
- Python examples must use ordinary dictionaries with `dict.get` or `setdefault` and must not import or use `defaultdict`
- when a fully documented question is added, prepend its linked bullet to the current day in `26U/0.26u-log.md` and refresh both summary tables
7. For `26U/0.26u-log.md` updates, normalize any manually added raw day entries into linked bullets, then refresh both top summary tables:
- monthly cadence table first
- per-day month table second
- if the user manually added entries under a specific day/date, keep that date exactly as-is and only format the question entries under it
- when a specific day/date section changes, update that date's single-day count in the second table first
- derive the first table from the second by summing Monday-start week buckets and the month total from the per-day row
- append ` - 2`, ` - 3`, and so on to repeated `26U/0.26u-log.md` question titles based on chronological attempt count
- both in descending month order with newest month prepended
- when the user says `update`, `update record`, or `update log`, add manually provided questions under today and inspect the past few days of file modification timestamps for individually edited solution code, logging each under its edit date
- exclude bulk whole-file/list additions requested as an entire-file update (for example, a complete prefix-sum list); only individual question or code edits count as practice records
8. Summarize what was changed.
