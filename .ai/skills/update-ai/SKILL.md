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
5. For `26U/0.26u-log.md` updates, normalize any manually added raw day entries into linked bullets, then refresh both top summary tables:
- monthly cadence table first
- per-day month table second
- if the user manually added entries under a specific day/date, keep that date exactly as-is and only format the question entries under it
- when a specific day/date section changes, update that date's single-day count in the second table first
- derive the first table from the second by summing Monday-start week buckets and the month total from the per-day row
- append ` - 2`, ` - 3`, and so on to repeated `26U/0.26u-log.md` question titles based on chronological attempt count
- both in descending month order with newest month prepended
6. Summarize what was changed.
