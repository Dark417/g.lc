# 5aws — AWS: Bedrock, AgentCore And Strands Together

> How the AWS pieces fit: models and guardrails (Bedrock), the hosting and platform services (AgentCore), and the open-source framework (Strands).
> Group 5 (frameworks). Overview and comparison: [5frameworks.md](5frameworks.md). Related: [1architecture.md](1architecture.md) §6.
> Concept level, no code (AGENTS.md §8b). Last updated: 2026-11-16. Cells marked `*` come from background knowledge and were not re-checked.

## Index
- [0. One-minute version](#0-one-minute-version)
- [1. Concept: three layers](#1-concept-three-layers)
- [2. Strands: the framework](#2-strands-the-framework)
- [3. AgentCore: the platform services](#3-agentcore-the-platform-services)
- [4. How the pieces work together](#4-how-the-pieces-work-together)
- [5. Bedrock Agents vs AgentCore vs Strands](#5-bedrock-agents-vs-agentcore-vs-strands)
- [6. What you still own](#6-what-you-still-own)
- [7. System design view: choosing](#7-system-design-view-choosing)
- [8. Failure modes](#8-failure-modes)
- [Where this fits](#where-this-fits)
- [References](#references)

---

## 0. One-minute version
- **What:** Bedrock supplies models, guardrails and retrieval. Strands is the open-source agent loop. AgentCore is the set of managed services to run, secure, remember and observe agents.
- **Why:** each solves a different layer. You can mix them, and AgentCore doesn't require Strands.
- **How:** write the agent in Strands (or another framework), run it on AgentCore Runtime, attach Memory, Gateway, Identity and Observability, and call Bedrock models.
- **Catch:** convenient and AWS-specific. "Harness" also names an AgentCore product (a managed loop), which isn't the same as our general term.
- 🗣 "Bedrock is the models, Strands is the loop, AgentCore is the operating environment."

---

## 1. Concept: three layers
`boundary` ★★★

| Layer | Piece | Role | Our term |
|---|---|---|---|
| Models and safety | Amazon Bedrock | model access (many providers), Guardrails, Knowledge Bases | model API (plus a gateway-like role) |
| Framework | Strands Agents SDK | agent loop, tools, sessions, multi-agent patterns | harness library |
| Platform | Bedrock AgentCore | runtime, memory, identity, gateway, tools, observability, policy, evaluations | managed runtime and control plane |

- **Picture it:** a support agent for an internal HR system.
  - Strands code defines the agent, its tools and a conversation manager.
  - AgentCore Runtime hosts it with an isolated session per user.
  - AgentCore Gateway exposes the HR API as MCP tools.
  - AgentCore Identity gets a user-scoped token for the HR system.
  - Memory remembers preferences; Observability traces runs; Policy blocks out-of-bounds tool calls.
- 🗣 "I pick the framework for control flow and AgentCore for who runs and secures it."

---

## 2. Strands: the framework
`AI` ★★★

- **Plain idea:** a model-driven agent loop with tools, plus helpers for multi-agent work.
- **Sessions:** session managers persist conversation messages, agent state and conversation-manager state. Backends: local files, S3, a custom repository, or AgentCore Memory (short- and long-term). `session_id` names each session.
- **Limit:** session managers aren't thread-safe; add external locking. Plan cleanup and permissions for the storage.
- **Multi-agent patterns**

| Pattern | Who decides the next step | Use |
|---|---|---|
| Workflow | you (dependencies you define) | repeatable processes |
| Graph | you define structure; conditional edges route | branching, review loops, approvals |
| Agents as tools | the orchestrator model | clear specialist roles |
| Swarm | the agents hand work to each other | open-ended exploration; harder to debug |

- **Graph and swarm persist** orchestrator state and flow history, so they resume after a restart. Individual agent histories aren't saved through that path.
- **Context control:** conversation managers (sliding window, summarizing)*.
- **Models and safety:** Bedrock models by default; other providers supported*; Bedrock Guardrails can attach to the model*.
- **Human approval:** interrupts exist in recent releases*; check the docs.
- 🗣 "Strands: pick workflow or graph if you can draw the steps; swarm only for open-ended work."

---

## 3. AgentCore: the platform services
`software` ★★★

| Service | What it does | Harness concern it covers |
|---|---|---|
| Runtime | serverless hosting with session isolation; long-running async runs; supports CrewAI, LangGraph, LlamaIndex, ADK, OpenAI Agents SDK, Strands and custom code; MCP and A2A | deployment and isolation |
| Memory | short-term (multi-turn) and long-term memory shared across agents; TTL, namespaces, metadata filters | session history and long-term memory |
| Gateway | turns APIs, Lambda functions and services into MCP tools; connects existing MCP servers | tools, MCP from existing services |
| Identity | agent identity and access; works with Cognito, Okta, Entra ID, Auth0 | on-behalf-of credentials ([4access.md](4access.md)) |
| Code Interpreter | isolated sandbox for Python, JavaScript, TypeScript | sandbox |
| Browser | managed cloud browser | web actions |
| Observability | traces, debugging, metrics; exports OpenTelemetry | tracing ([4observability.md](4observability.md)) |
| Policy | deterministic rules intercepting every tool call through Gateway; natural-language or Cedar-style rules; works with Bedrock Guardrails | permissions and guardrails |
| Evaluations | automated scoring of agent and tool quality over sessions, traces and spans; custom evaluators; A/B testing | evals ([4evals.md](4evals.md)) |
| Registry | governed catalog of agents, MCP servers and tools | discovery and approval |
| Harness | a managed agent loop: define model, prompt and tools in one API call; each session in an isolated microVM | the loop itself, managed |
| Optimization, Payments | recommendations and A/B for prompts and tool descriptions; agent micro-payments | extras |

- **Dated facts from the release notes I read:** Policy became generally available in March 2026; Harness in June 2026; Evaluations added support for several frameworks across mid-2026.
- **Building MCP from existing services:** Gateway is the path on AWS. Point it at an API (OpenAPI spec*), a Lambda or a service, and it serves them as MCP tools with auth. Compare with writing your own MCP server ([3mcp-full-picture.md](3mcp-full-picture.md)).
- 🗣 "AgentCore is a menu. I take Runtime and Gateway first, Memory and Observability next, Policy and Evaluations when I go to production."

---

## 4. How the pieces work together
`boundary` ★★★

1. The client calls your BFF, which invokes the agent on **AgentCore Runtime** with a session ID. Runtime keeps sessions isolated.
2. The **Strands** agent loads history from **AgentCore Memory** through its session manager, and long-term facts for this user.
3. It calls a **Bedrock** model; **Guardrails** screen input and output.
4. The model requests a tool. The call goes to **Gateway**, where **Policy** checks it deterministically.
5. **Identity** supplies a user-scoped token so the backend sees the user, not a shared account.
6. Spans go to **Observability** (and your own OpenTelemetry backend); **Evaluations** score sampled sessions.
7. The reply streams back; for long work, Runtime's extended runs plus a queue take over.

- **Your code still provides:** the BFF, the edge stream, tenant rules, the eval set and cost budgets.

---

## 5. Bedrock Agents vs AgentCore vs Strands
`boundary` ★★

| Option | What it is | Good at | Weak at | Choose when |
|---|---|---|---|---|
| Bedrock Agents* | older configuration-driven managed agents | quick standard agents, console setup | escape hatches when needs grow | simple agents, little code |
| Strands | code-first framework | control, multi-agent patterns, portability | you host and operate unless on AgentCore | you want code control |
| AgentCore (any framework) | managed platform | isolation, memory, identity, policy, evals | AWS-specific; many services to learn | production on AWS |
| Harness (AgentCore) | managed loop by API | fastest start; no loop code | less control | prototypes and standard tool agents |

- **Default:** Strands for the loop, AgentCore Runtime plus Gateway plus Identity for production, Memory when you need cross-session recall, Policy before write tools ship.

---

## 6. What you still own
`boundary` ★★

- The edge: BFF, auth, SSE ([0edge-com.md](0edge-com.md)).
- Business tool design and tool descriptions; the APIs behind Gateway.
- The eval set and release gate; Evaluations scores, you decide what good means.
- Cost and quota policy per user; Bedrock rate limits.
- Data retention and deletion across Memory and logs.
- Cross-cloud portability: a thin interface over Memory and Gateway, if that matters.

---

## 7. System design view: choosing
`boundary` ★★★

| Decision | Options | How to decide |
|---|---|---|
| Hosting | AgentCore Runtime, ECS or Lambda | Runtime for session isolation and long runs; ECS for control or cost |
| Memory | AgentCore Memory, DynamoDB or Aurora with your own logic | managed unless portability or custom extraction matters |
| Tools | Gateway, your own MCP servers, in-process | Gateway for existing APIs; own server for custom logic |
| Safety | Bedrock Guardrails, Policy, both | both: Guardrails for content, Policy for tool calls |
| Orchestration | Strands graph or workflow, Step Functions | Step Functions when the steps are mostly service calls |
| Framework | Strands, LangGraph, others on Runtime | team skills; Runtime accepts several |

- **Deciding variable:** how much operating work you want AWS to take, against how much AWS-specific design you accept.
- **Default for an AWS shop:** Strands on AgentCore Runtime, Gateway for tools, Identity for tokens, Observability to CloudWatch plus your own OpenTelemetry backend, Policy and Evaluations before launch.

---

## 8. Failure modes
`boundary`

| Failure | Trigger | Detect | Fix |
|---|---|---|---|
| Concurrent session writes | two requests on one Strands session | corrupt history | external lock or queue per session |
| Memory sprawl | everything saved forever | cost and irrelevant recall | TTL, namespaces, extraction rules |
| Policy bypass | tools called outside Gateway | audit shows unchecked calls | route all tool calls through the gate |
| Service sprawl | adopting every AgentCore service at once | long onboarding, unclear owners | adopt in order: Runtime, Gateway, Identity, Memory |
| Naming confusion | "harness" means two things | design reviews diverge | say "AgentCore Harness" or "our harness" |
| Lock-in | Memory and Gateway shape your data | migration estimate | thin interface; export plan |

---

## Where this fits
- **Place:** L9 of [1a-bp.md](../1a-bp.md); the AWS ecosystem for the target roles.
- **Time it deserves:** 30 minutes; §1, §3 and §4.
- **I should be able to…**
  - Name each layer and say which AgentCore service covers each harness concern.
  - Walk a request through Runtime, Memory, Bedrock, Gateway, Policy and Identity.
  - Choose between Bedrock Agents, Strands and the AgentCore Harness.

## References
1. [What is Amazon Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html) — service list.
2. [AgentCore release notes](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/release-notes.md) — dated additions.
3. [Strands — session management](https://strandsagents.com/docs/user-guide/concepts/agents/session-management/) — managers and limits.
4. [Who decides the next step: Strands multi-agent patterns](https://builder.aws.com/content/3LUbHxhsYgloMVN8Isrcp6q1ALB/who-decides-the-next-step-multi-agent-patterns-in-strands-agents) — workflow, graph, agents as tools, swarm.
5. [Strands Agents](https://strandsagents.com/) — framework docs.
