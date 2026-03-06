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
5. Summarize what was changed.
