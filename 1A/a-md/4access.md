# 4access — Identity, Permissions, Approval, Audit And Rollback

> Who the agent acts as, what it may do, when a human decides, how every action is recorded, and how to undo it.
> Group 4 (quality and safety). Related: [4guardrails.md](4guardrails.md), [0edge-com.md](0edge-com.md) §6, [1harness.md](1harness.md).
> Concept level, no code (AGENTS.md §8b). Last updated: 2026-11-16.

## Index
- [0. One-minute version](#0-one-minute-version)
- [1. Concept](#1-concept)
- [2. Identity: acting as whom](#2-identity-acting-as-whom)
- [3. Permissions: layers of "may it?"](#3-permissions-layers-of-may-it)
- [4. Approval design](#4-approval-design)
- [5. Audit and rollback](#5-audit-and-rollback)
- [6. Sandboxing](#6-sandboxing)
- [7. System design view: choosing and building](#7-system-design-view-choosing-and-building)
- [8. Failure modes](#8-failure-modes)
- [Where this fits](#where-this-fits)
- [References](#references)

---

## 0. One-minute version
- **What:** the controls on what an agent may do: identity, permission checks, human approval, audit and rollback.
- **Why:** an agent with tools can change real things. Its power must not exceed the user's, and every action must be explainable and, where possible, reversible.
- **How:** carry the user's identity to each tool, check permissions in code at every call, pause for approval by risk, log everything, and make writes undoable.
- **Catch:** a shared service account with broad rights turns a prompt trick into a data breach.
- 🗣 "The agent acts as the user, with less power than the user, and leaves a trail I can replay or undo."

---

## 1. Concept
`boundary` ★★★

- **Plain idea:** like a new assistant given a badge. The badge says who they work for, what doors open, what needs a manager's signature, and every door use is logged.
- **Picture it:** a finance agent asked "pay invoice 17".
  - Identity: it acts on behalf of Dana, an accounts clerk.
  - Permission: Dana may pay up to $5,000; this invoice is $4,200, allowed.
  - Approval: payments over $1,000 need a manager's click; the manager approves.
  - Audit: who asked, which invoice, what was shown, who approved, the payment ID, and the trace ID are stored.
  - Rollback: a void-payment action exists if it was wrong.
- **How it works**
  1. Authenticate the user at the edge.
  2. Give each tool call a credential scoped to that user and tool.
  3. Check policy in code: tool, arguments, data scope, limits.
  4. Route risky calls to approval.
  5. Record the decision and the result.
- **The catch:** every layer needs a deny path the model can't talk its way around.
- 🗣 "Identity, permission, approval, audit, rollback: five questions before an agent touches anything real."

---

## 2. Identity: acting as whom
`boundary` ★★★

| Identity | What it is | Use |
|---|---|---|
| User identity | the signed-in person | decides what data and actions are allowed |
| Agent identity | the agent's own workload credential | lets services know which agent called |
| Delegated (on-behalf-of) credential | a token for this user, this tool, short life | each tool call acts as the user |
| Shared service account | one broad credential | avoid; it ignores who is asking |

- **Why on-behalf-of beats a shared account:** if a user can't read a record, the agent acting for them can't either. A prompt trick can't widen it.
- **Tokens for tools**
  - Exchange the user's token for a narrow one per downstream system.
  - Bind tokens to one audience (one tool server). Never pass the user's token through to another service; that is the confused-deputy problem.
- **MCP servers:** the MCP authorization model uses OAuth with audience-bound tokens. The server validates tokens meant for itself.
- **Agent-to-agent:** each side authenticates the other and scopes what it returns.
- **Managed options:** AWS Bedrock AgentCore Identity (works with Cognito, Okta, Entra ID, Auth0); the same job done by your own identity provider and a token exchange.
- 🗣 "Every tool call carries a credential for this user and this tool, not a master key."

---

## 3. Permissions: layers of "may it?"
`boundary` ★★★

```
 request -> [1 tool allowlist for this agent and role]
         -> [2 argument rules: amount, scope, destination]
         -> [3 data rules: tenant and row filters in the query]
         -> [4 quota and rate limits]
         -> [5 environment limits: sandbox, network egress]
         -> allow | deny | ask a human
```

| Layer | Example | Enforced where |
|---|---|---|
| Tool allowlist | a support agent can't call `delete_user` | harness tool registry |
| Argument rules | refund ≤ $500 for tier-1 | tool-call hook or policy engine |
| Data rules | query includes the tenant ID from the token, never from the prompt | data access layer |
| Quotas | 20 writes per hour per user | harness or gateway |
| Environment | code runs without network or secrets | sandbox |

- **Deny wins.** Evaluate in an order where an explicit deny cannot be overridden by an allow further down. Example: Claude Agent SDK checks hooks, then deny rules, ask rules, the permission mode, allow rules, then a callback.
- **Policy as data:** a policy engine (Cedar, OPA) or a managed one such as AgentCore Policy, which intercepts every tool call through a gateway with deterministic rules. Rules change without code deploys and can be audited.
- **Never take identity from the model.** The user and tenant come from the token, not from tool arguments the model wrote.
- **Least privilege per agent:** a researcher sub-agent gets read tools; the executor gets write tools; they don't share.
- 🗣 "Policy runs in code at every tool call. The tenant ID comes from the token, never from the model."

---

## 4. Approval design
`boundary` ★★★

- **Plain idea:** approval is a decision aid for the risky tail of actions, not a toll on every action.
- **Decide by blast radius and reversibility**

| Action class | Example | Handling |
|---|---|---|
| Read, low sensitivity | search docs | auto-allow, log |
| Read, sensitive | pull customer records | allow by role; log; may need purpose |
| Reversible write | draft an email, create a ticket | auto-allow with log and undo |
| Costly or irreversible write | payment, delete, external send | human approval |
| Forbidden | disable audit, change own permissions | always deny |

- **What a good approval request shows:** what will happen, why, with which values, what the impact is, what it can't undo, and an expiry.
- **Options:** approve, reject, edit then approve, ask for more detail. Free text becomes a decision through a parsing step.
- **Who approves:** a role, not "anyone". The requester can't approve their own action (separation of duties). Check the approver's rights when the answer arrives.
- **Fatigue is a real failure:** too many prompts train people to click yes. Auto-allow the safe majority; reserve prompts for the risky tail; batch where possible.
- **Sticky decisions:** "always allow this for the session" is convenient, narrows prompts, and widens risk. Scope them tightly and log them.
- **Mechanics:** pause and save state, ask over the stream, resume on the answer ([0edge-com.md](0edge-com.md) §6). Store the paused state server side. A saved run state sent through the browser can be tampered with unless you authenticate it.
- **Stale approvals:** if the state changed after the request (the invoice amount moved), reject the old approval and ask again.
- **Async approvals:** a Slack or email request with an expiry and escalation path suits non-urgent work.
- 🗣 "Prompt the human for the risky tail only, show them exactly what will happen, and check on the answer that they're allowed to say yes."

---

## 5. Audit and rollback
`software` ★★

- **Audit log: one record per action**

| Field | Why |
|---|---|
| Who asked (user), acting as whom | accountability |
| Agent, version, trace ID | link to the full story ([4observability.md](4observability.md)) |
| Tool, arguments, result | what was done |
| Policy decision and version | why it was allowed |
| Approval: who, when, what they saw | proof of consent |
| Time, idempotency key | ordering and de-duplication |

- **Properties:** append-only, tamper-evident, retained by rule, separated from the agent's own write access.
- **Rollback patterns**

| Pattern | How | Fits |
|---|---|---|
| Dry-run (plan, then apply) | agent proposes a diff; a human or check applies it | bulk edits, infrastructure |
| Soft delete and versioning | keep the old value | data changes |
| Compensating action | a defined "undo" call (void, refund, cancel) | payments, bookings |
| Undo window | hold sends for N minutes | email, messages |
| File checkpoints | snapshot before edits | coding agents |
| Kill switch | disable an agent or tool instantly via flag | any incident |

- **Idempotency keys** make retries safe; they also make rollbacks traceable.
- 🗣 "If an action can't be undone, it needs a human. If it can, I make sure the undo exists."

---

## 6. Sandboxing
`software` ★★

- **Plain idea:** code or browser actions run in a box so a mistake or an attack stays inside it.
- **What the box limits:** files, network egress, secrets, CPU and time, and lifetime (ephemeral per session).
- **Options**

| Option | Isolation | Notes |
|---|---|---|
| Container | process-level | cheap; weaker against hostile code |
| MicroVM (Firecracker style) | VM-level | stronger; used by managed runtimes such as AgentCore |
| Hosted sandboxes (E2B, Modal, Daytona, Cloudflare, Vercel) | provider-managed | quick; check data policy |
| Local process without confinement | none | development only for trusted input |

- **Rules:** no secrets in the sandbox; egress allowlist; results come back as data through the harness; destroy after the session.
- 🗣 "Untrusted input plus code execution means a real sandbox, not a container I hope holds."

---

## 7. System design view: choosing and building
`boundary` ★★★

| Decision | Options | How to decide |
|---|---|---|
| Credential model | shared account, per-user token exchange | per-user for anything touching user data |
| Policy engine | in-code checks, Cedar or OPA, managed (AgentCore Policy) | engine when rules change often or need audit |
| Approval trigger | none, by tool, by arguments, by risk score | by action class: blast radius and reversibility |
| Approval channel | in-app, Slack, email | in-app for live work; async for batch |
| Audit store | app DB, log pipeline, immutable store | immutable and separated for regulated work |
| Rollback | none, compensating, versioned | design the undo before the tool ships |
| Isolation | container, microVM, hosted sandbox | microVM or hosted for untrusted code |

- **Default:** per-user delegated tokens; tool allowlist plus argument rules in code; approval only for costly or irreversible writes; append-only audit with trace IDs; a compensating action for every write tool; microVM or hosted sandbox for code execution; a kill switch per agent.

---

## 8. Failure modes
`boundary`

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Confused deputy | tool forwards a token meant for another service | audit shows token reuse | audience-bound tokens; no passthrough |
| Over-broad service account | one key for all users | access review; leak test | per-user tokens; least privilege |
| Tenant from the prompt | tenant ID taken from tool arguments | cross-tenant eval fails | derive from token; filter in query |
| Approval fatigue | prompts on everything | approval rate near 100%, short think time | approval only for the risky tail |
| Tampered or replayed approval | state round-tripped through the client | audit mismatch | server-side state; sign and expire |
| No undo | write tool without compensation | incident with no recovery path | require an undo before launch |
| Missing audit | actions logged only in the app | can't reconstruct an incident | append-only log with trace IDs |
| Policy bypass path | a code path skips the hook | unchecked calls in audit | route every tool through one gate; test it |

---

## Where this fits
- **Place:** L6 of [1a-bp.md](../1a-bp.md). The safety half of the control plane, with [4guardrails.md](4guardrails.md).
- **Time it deserves:** 25 minutes; §2, §3 and §4.
- **I should be able to…**
  - Explain on-behalf-of credentials and why a shared service account is dangerous.
  - List the permission layers and say where each is enforced.
  - Decide which actions need approval using blast radius and reversibility.
  - Describe an audit record and one rollback pattern per kind of write.

## References
1. [MCP specification — authorization](https://modelcontextprotocol.io/specification) — OAuth, audience-bound tokens, no token passthrough.
2. [Amazon Bedrock AgentCore docs](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html) — Identity, Gateway, Policy.
3. [Cedar policy language](https://www.cedarpolicy.com/) — policy as data.
4. [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/) — excessive agency.
5. [Simon Willison — the lethal trifecta](https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/) — private data, untrusted content, outward channels.
