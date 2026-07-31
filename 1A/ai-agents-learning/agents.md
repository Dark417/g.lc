# agents.md — AI Agents Learning Workspace

This folder is a **temporary learning sandbox** inside the `1sd` repo. It will
be moved out into its own repo later. Treat everything here as scratch space
for understanding how to design and build an AI-agent service.

## What is this file?

`agents.md` (sister convention to `AGENTS.md` / `CLAUDE.md`) is a top-level
guide that any coding agent or human reads first when entering a project. It
should answer: *what is this project, where do things live, how do I run/test,
what conventions matter?*

Same idea as `CLAUDE.md` but vendor-neutral. Many tools (Cursor, Codex, Aider,
Claude Code via fallback) will read whichever one exists.

## Layout

```
ai-agents-learning/
├── agents.md                 ← you are here
├── .ai/                      ← agent-facing config, not app code
│   ├── skills/               ← reusable skill packs (procedure + assets)
│   ├── agents/               ← named agent definitions (role, model, tools)
│   ├── hooks/                ← event hooks (PreToolUse, PostToolUse, Stop, …)
│   ├── mcp/                  ← MCP server configs (stdio / http)
│   └── tools/                ← local tool definitions / wrappers
└── tutorial/                 ← the actual learning material (read in order)
    ├── 01-core-components.md
    ├── 02-agent-paradigms.md
    ├── 03-frameworks.md
    ├── 04-architecture-combinations.md
    ├── 05-agent-flows.md
    ├── 06-use-case-recommendations.md
    └── 07-mcp-and-config.md
```

## How to use

1. Read `tutorial/01..07` in order. Each builds on the previous.
2. When a tutorial references a config example, the matching file lives in
   `.ai/` (e.g. `.ai/mcp/mcp.json`, `.ai/skills/example-skill/SKILL.md`).
3. By the end of `07`, you should be able to: (a) name every component of an
   agent service, (b) pick an architecture for a given use case, and
   (c) wire MCP servers + tools + hooks into a real project structure.

## Conventions

- Markdown only. No code to run yet — this is a study repo.
- Examples are illustrative; versions/APIs drift, so verify before copying.
- If you add a new tutorial doc, keep the numeric prefix so order stays clear.
