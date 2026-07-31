# 07 — MCP, Tooling, and Project Configuration

This last doc is the practical one: **how do tools and configs actually
live inside a repo?** We cover MCP (the protocol), tool design, and the
file layout your agent client (Claude Code, Cursor, custom runtime)
should read.

---

## What is MCP, briefly

**Model Context Protocol** is an open standard (from Anthropic, late
2024) for connecting LLM clients to *tools*, *resources*, and *prompts*
hosted in external servers. Think "LSP for AI tools":

- An **MCP server** exposes a set of tools (`search_jira`,
  `read_file`), resources (`file://...`, `db://...`), and prompt
  templates.
- An **MCP client** (Claude Code, Cursor, Claude Desktop, Continue, …)
  connects to one or more servers and lets the model call them.
- Transport is **stdio** (server is a local subprocess) or **HTTP / SSE
  / streamable-HTTP** (server is remote, can be auth'd).

Why it matters: you write the tool once as an MCP server, and any
MCP-compatible client can use it. No more re-wiring tools per framework.

### MCP vs raw tool calling

| Feature | Raw tool calling | MCP |
|---|---|---|
| Discovery | hard-coded in your app | client lists from server at runtime |
| Reuse across clients | rewrite per framework | one server, many clients |
| Auth | bespoke | server-handled (incl. OAuth) |
| Resources (files, DB rows) | ad hoc | first-class concept |
| Prompts / templates | scattered | versioned in server |

Use MCP for anything you want to share across editor/agent/Claude
Desktop/coworkers. Use raw tools for things that are *intrinsic* to your
app logic.

---

## Project layout for agent config

Convention (used by Claude Code and increasingly others):

```
your-project/
├── agents.md                 # what is this project (human + agent)
├── .ai/                      # vendor-neutral; or .claude/ for Claude-specific
│   ├── settings.json         # model, permissions, env, hooks
│   ├── settings.local.json   # gitignored personal overrides
│   ├── mcp/
│   │   └── mcp.json          # MCP server registrations
│   ├── agents/
│   │   ├── reviewer.md       # named sub-agent definitions
│   │   └── planner.md
│   ├── skills/
│   │   └── pr-review/
│   │       └── SKILL.md      # "how-to" pack, lazy-loaded
│   ├── hooks/
│   │   └── pre-tool-use.sh   # event hook scripts
│   └── tools/
│       └── grep_repo.py      # native tool wrappers (if any)
└── src/                      # your actual app
```

Two real-world variants:

- **Claude Code** uses `.claude/` with `settings.json`, `agents/`,
  `skills/`, `hooks/`, plus `.mcp.json` at repo root. The structure
  above mirrors that but vendor-neutral.
- **Cursor / Aider / Codex** read `agents.md` or `AGENTS.md`. Cursor
  also has `.cursor/rules/*.mdc`.

It's fine to keep **both** an `agents.md` (cross-tool readme) and a
vendor-specific config folder; they don't conflict.

### Three scopes for configs

1. **User scope** (`~/.claude/settings.json` or similar) — your machine,
   all projects. Personal preferences, personal API keys via env.
2. **Project scope** (`.ai/settings.json`, committed) — shared with the
   team, lives in git. The team's MCP servers, hooks, allowed tools.
3. **Local scope** (`.ai/settings.local.json`, **gitignored**) —
   per-developer overrides on top of project settings.

Rule: secrets never go in committed files. Use env vars + `${VAR}`
expansion inside JSON, or a secret manager.

---

## Designing a tool (whether raw or MCP)

A good tool is:

- **Narrow**: one verb, predictable side effects.
- **Schema-typed**: JSON Schema for args, with `description` per field
  (the model reads these as docs).
- **Idempotent or two-phase**: if it mutates, support `dry_run` or
  `preview` + `commit`.
- **Loud on failure**: return a structured error the model can read
  (`{ "error": "rate_limited", "retry_after": 30 }`).
- **Cheap to call**: tools that block 20s wreck the loop.

Anatomy:

```jsonc
{
  "name": "search_orders",
  "description": "Search the orders table by customer email or order ID. Read-only.",
  "input_schema": {
    "type": "object",
    "properties": {
      "email":    { "type": "string", "description": "Customer email" },
      "order_id": { "type": "string", "description": "Order ID, format ORD-xxxx" },
      "limit":    { "type": "integer", "default": 10, "maximum": 100 }
    },
    "anyOf": [{ "required": ["email"] }, { "required": ["order_id"] }]
  }
}
```

---

## Adding MCP servers — example configs

### Project `.ai/mcp/mcp.json` (stdio + HTTP examples)

```jsonc
{
  "mcpServers": {
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "${workspaceFolder}"]
    },
    "github": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "${GITHUB_TOKEN}" }
    },
    "postgres": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres",
               "postgres://readonly:${PG_PW}@db.internal/app?sslmode=require"]
    },
    "linear": {
      "type": "http",
      "url": "https://mcp.linear.app/mcp"
    },
    "company-tools": {
      "type": "streamable-http",
      "url": "https://tools.example.com/mcp",
      "headers": { "Authorization": "Bearer ${COMPANY_MCP_TOKEN}" }
    }
  }
}
```

Notes:
- Prefer **read-only** credentials for any DB / SaaS connection.
- Pin the version of `npx` packages (`@modelcontextprotocol/server-x@1.4.0`)
  once you go to prod.
- For remote MCP, prefer OAuth flows where the server supports them.

### `.ai/settings.json` (permissions, env, hooks)

```jsonc
{
  "model": "claude-sonnet-4-6",
  "env": {
    "TZ": "UTC"
  },
  "permissions": {
    "allow": [
      "Bash(npm test*)",
      "Bash(npm run lint*)",
      "Read(./**)",
      "mcp__github__list_issues",
      "mcp__github__pull_request_read"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(git push --force*)"
    ]
  },
  "hooks": {
    "PreToolUse": [
      { "matcher": "Bash", "command": ".ai/hooks/pre-bash.sh" }
    ],
    "PostToolUse": [
      { "matcher": "Edit|Write", "command": ".ai/hooks/format.sh" }
    ]
  }
}
```

### `.ai/agents/reviewer.md` (a sub-agent definition)

```markdown
---
name: reviewer
description: Reviews diffs for security and style. Use after every commit.
tools: [Read, Grep, mcp__github__pull_request_read]
model: claude-haiku-4-5
---
You are a strict code reviewer. Flag issues by severity (blocker / major /
minor / nit). Cite file and line. Don't suggest unrelated cleanups.
```

### `.ai/skills/pr-review/SKILL.md` (a skill pack)

```markdown
---
name: pr-review
description: Procedure for reviewing a pull request end-to-end.
---
1. Fetch PR with mcp__github__pull_request_read.
2. Diff against base; load changed files with Read.
3. Apply the reviewer rubric (see `rubric.md` in this folder).
4. Post a single summary comment, then per-line comments.
```

Skills differ from agents: a **skill** is a procedure you load *into*
an existing agent; an **agent** is a separate persona with its own
prompt/tools/model.

### `.ai/hooks/pre-bash.sh` (example hook)

```bash
#!/usr/bin/env bash
# Block destructive commands even if the model tries them.
cmd="$CLAUDE_TOOL_INPUT_command"
case "$cmd" in
  *"rm -rf "*|*"git push --force"*|*"DROP TABLE"*)
    echo "blocked: $cmd" >&2
    exit 2 ;;
esac
```

Hooks (PreToolUse, PostToolUse, UserPromptSubmit, Stop, SessionStart,
SessionEnd, Notification) are how you enforce policy and integrate with
existing CI — they're shell commands the harness runs around tool calls.

---

## Best practices for configs

1. **Commit the project config; gitignore secrets.** Use env expansion.
2. **Pin MCP server versions.** They evolve fast.
3. **Start with deny-all, allow specific tools.** Allowlist is safer
   than denylist for unknowns.
4. **Co-locate the skill/agent next to its docs.** A skill folder is a
   tiny self-contained README + assets.
5. **Hooks for invariants, prompts for guidance.** Don't ask the model
   nicely not to `rm -rf`; block it in a hook.
6. **Keep `agents.md` short.** Link out to deep docs. Long top-level
   instructions get ignored or cached badly.
7. **One MCP server per concern.** Don't build a "do-everything" server;
   split per integration.
8. **Local-only experiments go in `settings.local.json`.** Keeps team
   config clean.
9. **Document the *why* of permissions.** `// allowed: tests must run
   to merge` next to `Bash(npm test*)`.
10. **Re-evaluate quarterly.** Models, MCP servers, and frameworks
    change quickly; pruned config beats accumulated config.

---

## Putting it all together — a worked example

> "We're building an internal support agent that answers questions about
> our docs and can open Jira tickets."

- **Use-case row** (`06`): A1-style support → Level 5–6, Flow 3 (router)
  + Flow 4 (ReAct).
- **Components** (`01`): LLM, Controller, Tools, Embeddings, Vector DB,
  Docs, Reranker, Guardrails, Traces. (Skip Planner, Multi-agent, Async.)
- **Frameworks** (`03`): Anthropic SDK + LangGraph for the loop;
  pgvector; Voyage embeddings + Cohere rerank; Langfuse traces.
- **Tools** (this doc): two MCP servers — `docs` (read-only RAG over our
  wiki) and `jira` (create/update tickets, scoped token).
- **Config** (this doc):
  - `.ai/mcp/mcp.json` registers both servers.
  - `.ai/settings.json` allows `mcp__docs__*` and `mcp__jira__create_*`,
    denies `mcp__jira__delete_*`.
  - `.ai/hooks/pre-tool-use.sh` requires user confirmation for any
    Jira mutation.
  - `.ai/agents/triage.md` is the front-of-house agent; routes to
    `.ai/agents/ticketer.md` for create-ticket intent.

That's everything you need to get an MVP into a teammate's hands and
know what to add next.

---

## Where to read next (outside this repo)

- Anthropic — *Building Effective Agents* (2024 essay)
- Anthropic — Model Context Protocol spec & SDKs
- LangGraph docs — patterns for cyclic agent graphs
- Hugging Face — *AI Agents Course* (free)
- Lilian Weng — *LLM Powered Autonomous Agents* (blog)
- Chip Huyen — *AI Engineering* (book, 2024)
- OpenTelemetry — GenAI semantic conventions
