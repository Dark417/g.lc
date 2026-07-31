---
name: pr-review
description: Procedure for reviewing a pull request end-to-end.
---

1. Fetch PR with `mcp__github__pull_request_read`.
2. Diff against base; load changed files with `Read`.
3. Apply the reviewer rubric (see `.ai/agents/reviewer.md`).
4. Post a single summary comment, then per-line comments for blockers/majors.
5. Stop after one round — don't relitigate accepted style choices.
