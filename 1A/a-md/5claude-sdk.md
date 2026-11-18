# 5claude-sdk — Claude Agent SDK

> The Claude Agent SDK as a harness: the Claude Code loop as a library, with sessions, subagents, hooks, permissions and MCP.
> Group 5 (frameworks). Overview and comparison: [5frameworks.md](5frameworks.md).
> Concept level, no code (AGENTS.md §8b). Last updated: 2026-11-16.
> **Source note:** most details come from a third-party summary of the SDK's changelogs (late 2026). Version numbers move fast; check the official docs before quoting.

## Index
- [0. One-minute version](#0-one-minute-version)
- [1. Concept](#1-concept)
- [2. How the SDK manages the harness concerns](#2-how-the-sdk-manages-the-harness-concerns)
- [3. Permissions: the order of checks](#3-permissions-the-order-of-checks)
- [4. Subagents](#4-subagents)
- [5. Running it in production](#5-running-it-in-production)
- [6. What you still own](#6-what-you-still-own)
- [7. System design view: choosing](#7-system-design-view-choosing)
- [8. Failure modes](#8-failure-modes)
- [Where this fits](#where-this-fits)
- [References](#references)

---

## 0. One-minute version
- **What:** the SDK runs the same agent loop as Claude Code, as a library you call from Python or TypeScript.
- **Why:** you get a mature model-driven loop with file, shell and search tools, context compaction, subagents and permissions, without writing them.
- **How:** you configure tools, MCP servers, subagents, hooks and a permission mode; the SDK runs a subprocess and streams messages back.
- **Catch:** it is built for an agent that owns a working directory. Multi-tenant servers need care: isolation, session storage and permissions are yours.
- 🗣 "The Claude Agent SDK is a ready model-driven harness. I add hosting, isolation and storage."

---

## 1. Concept
`AI` ★★★

- **Plain idea:** Claude Code without the terminal. The loop, tools and permissions are the same; your code is the client.
- **Picture it:** a code-review service.
  1. A pull request arrives; your server starts an SDK session in a fresh working directory with the repo checked out.
  2. The agent reads files, runs tests, calls a review subagent for security checks.
  3. A hook blocks any write outside the directory.
  4. The result streams to your service, which posts comments.
- **How it works**
  1. The SDK starts the Claude Code runtime as a subprocess.
  2. Your options set tools, permission mode, MCP servers, subagents and hooks.
  3. The loop runs; messages stream to your code.
  4. The transcript is saved so the session can resume.
- **The catch**
  - The agent has real file and shell power. Permission mode and sandboxing decide the blast radius.
  - Configuration loaded from the environment (settings files, `CLAUDE.md`) can leak into a multi-tenant setup if you don't turn it off.
- 🗣 "The SDK is single-agent-owner by design. For many users, I put one isolated process or container per session."

---

## 2. How the SDK manages the harness concerns
`boundary` ★★★

| Concern | How it's handled |
|---|---|
| Loop | the Claude Code loop; limits via max turns and a spend cap |
| Context | the SDK manages the window and auto-compacts; `CLAUDE.md` and settings files add standing instructions |
| Session history | saved as local transcripts; you can continue the latest, resume by ID, or fork into a new session |
| Shared or remote sessions | `SessionStore` mirrors transcripts to your backend so another host can resume; the SDK writes locally first and never deletes from your store |
| Run state | the transcript; file edits are not part of it, so file checkpointing is separate |
| Long-term memory | `CLAUDE.md` files and per-subagent memory; for user-level recall you build your own store and tool |
| Tools | built-in file, shell and search tools; in-process MCP tools; external MCP servers; tool search loads tools on demand |
| Human approval | permission modes, a permission callback, and hooks that can allow, deny, ask or defer |
| Guardrails | hooks around tool calls and results; a hook can fail closed if it errors |
| Tracing | telemetry and hook events; you export to your own backend |
| Edge | messages stream to your process; you build the BFF and SSE |
| Hosting | your container, process or sandbox |

- **Deferred approvals:** a hook can "defer" a tool call, which ends the turn so you can collect an approval elsewhere and resume.
- **Session keys derive from the working directory.** Resuming from a different directory can miss the session.

---

## 3. Permissions: the order of checks
`boundary` ★★★

- **Plain idea:** many layers can say yes or no. Learn which wins.
- **Order (per the summary I read):** hooks, then deny rules, then ask rules, then the permission mode, then allow rules, then the permission callback.
- **Consequences**
  - A hook's deny holds even in the most permissive mode.
  - An allow rule earlier in the chain means the callback is never called for that tool.
  - A "don't ask" mode denies anything that would prompt, so the callback never runs.
- **Modes (six):** default, don't-ask, accept-edits, bypass, plan, auto.
- **Production advice from the summary:** set the mode explicitly; defaults have changed between releases. Use deny rules for tools you must block, because an allow list doesn't restrict the bypass mode.
- 🗣 "Hooks first, deny beats allow, and I set the permission mode explicitly."

---

## 4. Subagents
`AI` ★★★

- **What:** helper agents defined in options, each with its own tools, model, turn limit and permissions. They run in a fresh context and return a summary.
- **Controls reported:** nesting depth (default 3), concurrent subagents (default 20), a spend cap that ends the run, background execution, per-subagent MCP servers.
- **Permissions:** a subagent inherits the parent's mode and can't escalate to the bypass mode.
- **Large fan-out:** a workflow tool coordinates dozens to hundreds of agents, subject to normal permission checks.
- **Pattern:** agents-as-tools ([1orchestration.md](1orchestration.md)): the lead keeps control; context isolation is the main benefit.
- 🗣 "Subagents give me clean context and least privilege per task, with a budget cap."

---

## 5. Running it in production
`software` ★★

- **One process per session** (or per tenant). The subprocess has file and shell access.
- **Isolation:** container or sandbox per session; no shared writable directories; no host secrets in the environment.
- **Auth:** API-key based for shipped products; cloud-provider options exist for Bedrock, Vertex and Foundry.
- **Session storage:** mirror transcripts to your store if sessions must survive the host. Retention is your job. A store and "don't persist" modes conflict.
- **Pin versions:** the SDK moves quickly.
- **Settings isolation:** by default the SDK reads user, project and local settings and `CLAUDE.md` files. For multi-tenant use, turn that off and configure in code; managed policy settings still load.
- **Warm start:** pre-warming reduces cold-start latency.
- **Environment:** in TypeScript, passing your own environment replaces the default, so include the existing variables.

---

## 6. What you still own
`boundary` ★★

- Hosting, isolation and scaling per session.
- Session persistence, locking and retention.
- The BFF, SSE edge and auth ([0edge-com.md](0edge-com.md)).
- Tenant boundaries and credentials for tools ([4access.md](4access.md)).
- Tracing export, eval gate and cost reporting.
- A policy for what `CLAUDE.md` and settings are allowed in each tenant.

---

## 7. System design view: choosing
`boundary` ★★★

| Decision | Options | How to decide |
|---|---|---|
| Use the SDK or build a loop | SDK, own loop on the messages API | SDK for coding or file-centric agents; own loop for tight control or many tenants |
| Isolation | process, container, microVM, hosted sandbox | microVM or hosted for untrusted input |
| Sessions | local files, mirrored store | mirrored store for multi-host or resumable work |
| Approvals | callback, hooks, plan mode | hooks for fixed rules; callback for human prompts |
| Cost control | turn limits, spend cap | both, per run and per subagent |

- **Choose it when:** the agent works on files and code, you want Claude Code's behavior in your product, and a container per session is acceptable.
- **Look elsewhere when:** you need explicit graph checkpoints (LangGraph or ADK workflows), thousands of cheap concurrent chat sessions, or a managed runtime out of the box.
- **Default:** SDK in a container or microVM per session, explicit permission mode, hooks for deny rules, a mirrored session store, spend and turn caps, traces exported to your backend.

---

## 8. Failure modes
`boundary`

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Permissive default | mode left unset | unexpected writes in traces | set the mode explicitly; deny rules |
| Callback never called | earlier allow rule or "don't ask" mode | approvals missing | review the order of checks |
| Cross-tenant leak | shared settings files and working directories | one tenant's instructions in another's run | isolate per tenant; disable ambient settings |
| Session lost on host change | local transcripts only | resume fails on another host | session store; same working directory |
| Hook error lets action through | the default continues on hook failure | a failed hook, action still ran | fail-closed option on hooks |
| Runaway cost | no caps on turns or spend | spend per run | max turns and spend limits |

---

## Where this fits
- **Place:** L9 of [1a-bp.md](../1a-bp.md); the model-driven loop SDK in group 5.
- **Time it deserves:** 25 minutes; §2, §3 and §5.
- **I should be able to…**
  - Say where sessions live and how to make them survive a host change.
  - Explain the order of permission checks and one trap in it.
  - Describe subagent controls and why isolation is the benefit.
  - Say what changes when serving many tenants.

## References
1. [Claude Agent SDK in late 2026](https://www.developersdigest.tech/blog/claude-agent-sdk-whats-new-2026) — sessions, subagents, hooks, permissions, deployment (third-party summary).
2. [Anthropic — Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) — agent design background.
3. [Model Context Protocol](https://modelcontextprotocol.io/) — tool servers the SDK can use.
