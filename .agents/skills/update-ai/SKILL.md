---
name: update-ai
description: Persist durable instruction updates into AGENTS.md, agent files, or skill files. Use for every chat to capture reusable rules.
---

# update-ai

1. Review latest user message and current instruction files.
2. Identify durable new rules/patterns.
3. Route updates using official Codex repository conventions:
- Global -> root `AGENTS.md`
- Role- or directory-specific -> the closest applicable `AGENTS.md`
- Reusable workflow -> `.agents/skills/<skill>/SKILL.md`
4. Keep edits minimal and avoid duplication.
   - For every Markdown draft and update, apply `.agents/rules.md` §3 before writing and review changed prose before finishing.
   - Use layered bullets down to keyword-level siblings.
   - Write explanatory prose as nested bullets instead of long paragraphs.
   - Use separate rendered arrow lines for flow steps and consequences, without bullet markers.
5. Treat `++:` in a user message as a durable instruction/rule request and persist it to `AGENTS.md` plus any relevant workflow file.
6. For topic-file updates:
- if the user says `update this file` or `update` after adding raw question details, inspect the current topic file detail section for newly added questions
- normalize out-of-sync question details to the standard solution block format
- add matching entries to the top index section
- keep index order aligned with solution order
- for format-rule requests, persist the rule in the proper `AGENTS.md` section, mirror it here when workflow-related, then apply it to the current file
- for a line-break-only pass, preserve code exactly and change only whitespace in study notes
  - preserve existing wording, links, anchors, question order, and log counts
  - separate existing title, description, and tag content without adding missing fields
  - limit root-file requests to direct children of the named directory
- group both topic-file index and solution/detail sections by `### Hard`, `### Medium`, `### Easy` in that order
- append new questions to the matching difficulty group in both index and details; if the user put a question in the wrong difficulty group, move it to the correct group without asking
- index entries must render as three separate lines by adding Markdown hard breaks after the title/link line and description line
- unless the user specifies a narrower scope, apply coding-question Markdown formatting and link updates across all coding-question documents in the repository, including nested folders
  - index question titles link to their matching local detail anchors
  - detail question titles link to the actual LeetCode problem pages
  - preserve anchors, code, question wording, ordering, and original source evidence
  - retain original sources for custom questions without a LeetCode equivalent
  - preserve the reference role of logs, inventories, and study plans without inventing solution sections
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
