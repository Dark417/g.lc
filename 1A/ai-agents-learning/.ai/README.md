# `.ai/` — Agent-facing configuration

This folder holds configuration consumed by the agent harness (Claude
Code, Cursor, custom runtimes). It is **not** application code.

| Path | What it is |
|---|---|
| `settings.json` | Model, permissions, env, hooks (project scope, committed). |
| `mcp/mcp.json` | MCP server registrations (stdio / http / streamable-http). |
| `agents/*.md` | Named sub-agent definitions (role, model, tools, prompt). |
| `skills/<name>/SKILL.md` | Reusable procedure packs, lazy-loaded by name. |
| `hooks/*.sh` | Event hooks: PreToolUse, PostToolUse, etc. |
| `tools/*.json` | Local tool schemas (when not exposed via MCP). |

See `tutorial/07-mcp-and-config.md` in this repo for the conventions
and `tutorial/01-core-components.md` for the conceptual layer they map to.

Secrets: never commit them. Use environment variables and the `${VAR}`
expansion supported in JSON configs.
