# Claude Agent SDK and the Claude API

The Claude Agent SDK (Python claude-agent-sdk, TypeScript @anthropic-ai/claude-agent-sdk) exposes the agent loop that powers Claude Code as a library. The Claude API (Messages API) is the lower-level alternative.

## Agent SDK entry points

- query(prompt, options) runs one task and streams messages (AssistantMessage, ResultMessage, ...).
- ClaudeSDKClient keeps a bidirectional session: send follow-ups, interrupt, and continue the same conversation.
- ClaudeAgentOptions configures system_prompt, allowed_tools / disallowed_tools, mcp_servers, hooks, can_use_tool, permission_mode, agents (subagents), cwd, env, and max_turns.

## Tools and MCP

- Built-in tools include Read, Write, Edit, Bash, Glob, Grep, WebFetch, and Task (to run subagents).
- Custom tools are MCP tools. create_sdk_mcp_server builds an in-process MCP server from @tool functions; external servers attach as stdio, SSE, or HTTP entries in mcp_servers.
- MCP tool names follow mcp__<server>__<tool>, and allowed_tools can pre-approve them.

## Control

- Hooks: PreToolUse, PostToolUse, UserPromptSubmit, Stop, SubagentStop, PreCompact, and more. A PreToolUse hook can return permissionDecision "deny" with a reason.
- can_use_tool(tool_name, input, context) returns PermissionResultAllow (optionally with updated input) or PermissionResultDeny.
- Subagents: AgentDefinition(description, prompt, tools, model). The main agent delegates via the Task tool; each subagent has its own context window.

## Sessions

- Every run has a session id (in ResultMessage.session_id). Pass resume=<id> to continue it, fork_session=True to branch it, or continue_conversation=True for the most recent one.
- Sessions are stored by the CLI as JSONL under ~/.claude/projects on the machine that ran them.

## Cloud providers

- Amazon Bedrock: CLAUDE_CODE_USE_BEDROCK=1 plus AWS credentials and region.
- Google Vertex AI: CLAUDE_CODE_USE_VERTEX=1, CLOUD_ML_REGION, ANTHROPIC_VERTEX_PROJECT_ID.
- Telemetry: CLAUDE_CODE_ENABLE_TELEMETRY=1 with OTEL_METRICS_EXPORTER / OTEL_LOGS_EXPORTER and OTEL_EXPORTER_OTLP_ENDPOINT.

## Messages API tool runner

- The anthropic Python SDK's client.beta.messages.tool_runner runs the tool-use loop for @beta_tool / @beta_async_tool functions and stops when Claude stops calling tools.
- Clients: Anthropic (Claude API), AnthropicBedrockMantle (Claude in Amazon Bedrock, model ids prefixed anthropic.), AnthropicVertex (Claude on Vertex AI).
