# Claude Code entry point

- Read and follow [AGENTS.md](../AGENTS.md) and [.agents/rules.md](../.agents/rules.md) for every task; they are the source of truth for content and format rules.
- Both Codex and Claude Code use both trees: `AGENTS.md` + `.agents/` and `CLAUDE.md` + `.claude/`.
  - Skills live in `.agents/skills/` and `.claude/skills/`; either tool may invoke either set.
  - Directory-scoped `AGENTS.md` files (for example `1o/2.sd/AGENTS.md`) apply to the files under them.
- Persist durable instructions in `AGENTS.md`, not here.
