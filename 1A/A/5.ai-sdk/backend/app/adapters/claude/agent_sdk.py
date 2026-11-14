"""Claude Agent SDK patterns: the Claude Code agent loop as a library.

  agent_sdk     ClaudeSDKClient + in-process MCP tools + hooks + can_use_tool
  subagents     query() + AgentDefinition subagents reached through the Task tool
  external_mcp  query() + stdio MCP servers (our workbench, optional Playwright MCP)

Provider = environment variables for the CLI child process (not a client object):
  raw      ANTHROPIC_API_KEY
  bedrock  CLAUDE_CODE_USE_BEDROCK=1 + AWS_REGION (+ AWS credentials from the default chain)
  vertex   CLAUDE_CODE_USE_VERTEX=1 + CLOUD_ML_REGION + ANTHROPIC_VERTEX_PROJECT_ID (+ ADC)
"""

import json
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from claude_agent_sdk import (
    AgentDefinition,
    AssistantMessage,
    ClaudeAgentOptions,
    HookMatcher,
    PermissionResultAllow,
    PermissionResultDeny,
    ResultMessage,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
)

from app.adapters.claude.tools import mcp_name, sdk_server, short_name
from app.config import Settings
from app.core.adapter import RunContext
from app.mcp.clients import server_specs
from app.providers.profile import ProviderProfile
from app.schemas import Event
from app.telemetry import claude_cli_otel_env
from app.tools import SENSITIVE, tools_for

log = logging.getLogger(__name__)

SYSTEM = (
    "You are an engineering research assistant. Use your tools instead of guessing: calculator "
    "for math, search_docs for agent frameworks and cloud services, browse for URLs, run_cli for "
    "allowlisted commands. Cite the `source` of passages you use. Be concise."
)


# ---------------------------------------------------------------------------- provider


def provider_env(profile: ProviderProfile) -> dict[str, str]:
    s = profile.settings
    if profile.name == "bedrock":
        env = {"CLAUDE_CODE_USE_BEDROCK": "1", "AWS_REGION": s.aws_region}
        if s.bedrock_claude_code_model:
            env["ANTHROPIC_MODEL"] = s.bedrock_claude_code_model
        return env
    if profile.name == "vertex":
        return {
            "CLAUDE_CODE_USE_VERTEX": "1",
            "CLOUD_ML_REGION": s.vertex_claude_region,
            "ANTHROPIC_VERTEX_PROJECT_ID": s.google_cloud_project,
        }
    return {"ANTHROPIC_API_KEY": s.anthropic_api_key}


def provider_model(profile: ProviderProfile) -> str | None:
    s = profile.settings
    if profile.name == "bedrock":
        return s.bedrock_claude_code_model or None  # None: the CLI's Bedrock default
    if profile.name == "vertex":
        return s.vertex_claude_model
    return s.anthropic_model


# ---------------------------------------------------------------------------- hooks & permissions


def make_hooks(deny: set[str]) -> dict[str, list[HookMatcher]]:
    """Hooks run in our process at fixed points of the CLI's loop."""

    async def add_context(input_data: dict, tool_use_id: str | None, context: Any) -> dict:
        # UserPromptSubmit: extra context the model sees with the user's prompt.
        return {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": f"Current UTC time: {datetime.now(UTC):%Y-%m-%d %H:%M}.",
            }
        }

    async def policy(input_data: dict, tool_use_id: str | None, context: Any) -> dict:
        # PreToolUse: deterministic deny-list, evaluated before the permission system.
        name = short_name(input_data.get("tool_name", ""))
        if name in deny:
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"tool {name!r} is disabled by policy",
                }
            }
        return {}

    async def audit(input_data: dict, tool_use_id: str | None, context: Any) -> dict:
        # PostToolUse: observe (could also redact or annotate the result).
        log.info("claude tool %s done", input_data.get("tool_name"))
        return {}

    async def before_compaction(input_data: dict, tool_use_id: str | None, context: Any) -> dict:
        # PreCompact: the CLI is about to summarise the conversation (trigger "auto" when the
        # context window fills, "manual" for /compact). Last chance to archive the full transcript;
        # with a session_store it is already mirrored, so we only record that it happened.
        log.info("claude compaction (%s)", input_data.get("trigger"))
        return {}

    return {
        "UserPromptSubmit": [HookMatcher(hooks=[add_context])],
        "PreToolUse": [HookMatcher(matcher="^mcp__", hooks=[policy])],
        "PostToolUse": [HookMatcher(hooks=[audit])],
        "PreCompact": [HookMatcher(hooks=[before_compaction])],
    }


def make_can_use_tool(options: dict):
    """Called for tools *not* in allowed_tools (here: the sensitive ones). A human approval UI,
    a policy engine, or (as here) a request option decides."""

    async def can_use_tool(tool_name: str, tool_input: dict, context: Any):
        name = short_name(tool_name)
        if name in SENSITIVE and not options.get("approve_sensitive", True):
            return PermissionResultDeny(message=f"{name} needs approval; it was not granted")
        return PermissionResultAllow()

    return can_use_tool


# ---------------------------------------------------------------------------- options per pattern


def _base_options(ctx: RunContext, settings: Settings) -> dict[str, Any]:
    rec, profile = ctx.session, ctx.provider
    claude_sid = rec.native.get("claude_session_id")
    session = {"resume": claude_sid} if claude_sid else {"session_id": str(uuid.UUID(rec.id))}
    workdir = settings.data_path / "claude_workdir"
    workdir.mkdir(exist_ok=True)
    return {
        "model": provider_model(profile),
        "env": {**provider_env(profile), **claude_cli_otel_env(settings, rec.id, rec.user_id)},
        "cwd": str(workdir),
        "setting_sources": [],  # ignore ~/.claude settings on a server
        "max_turns": settings.max_llm_calls,
        # Mirror transcripts to a shared store so any replica can resume (see session_store.py).
        "session_store": ctx.extras.get("session_store"),
        **session,
    }


def agent_sdk_options(ctx: RunContext, settings: Settings) -> ClaudeAgentOptions:
    functions = tools_for(ctx.provider)
    safe = [mcp_name(f.__name__) for f in functions if f.__name__ not in SENSITIVE]
    return ClaudeAgentOptions(
        **_base_options(ctx, settings),
        system_prompt=SYSTEM,
        mcp_servers={"tools": sdk_server(functions)},
        tools=[],  # no built-in file/bash tools: this is not a coding agent
        allowed_tools=safe,  # pre-approved; sensitive tools fall through to can_use_tool
        hooks=make_hooks(set(ctx.request.options.get("deny_tools", []))),
        can_use_tool=make_can_use_tool(ctx.request.options),
    )


def subagents_options(ctx: RunContext, settings: Settings) -> ClaudeAgentOptions:
    functions = tools_for(ctx.provider, ["search_docs", "browse", "calculator", "current_time"])
    agents = {
        "researcher": AgentDefinition(
            description="Researches agent frameworks and cloud services in the docs and on the web.",
            prompt=f"{SYSTEM} Return concise notes with sources.",
            tools=[mcp_name("search_docs"), mcp_name("browse")],
        ),
        "calculator": AgentDefinition(
            description="Does exact arithmetic.",
            prompt="Compute exactly with the calculator tool. Reply with the expression and result.",
            tools=[mcp_name("calculator")],
        ),
    }
    return ClaudeAgentOptions(
        **_base_options(ctx, settings),
        system_prompt=(
            "You coordinate subagents. Delegate research to `researcher` and math to `calculator` "
            "with the Task tool, then write the final answer from their results."
        ),
        mcp_servers={"tools": sdk_server(functions)},
        agents=agents,
        tools=["Task"],
        allowed_tools=["Task", *[mcp_name(f.__name__) for f in functions]],
        permission_mode="dontAsk",
        forward_subagent_text=True,
    )


def external_mcp_options(ctx: RunContext, settings: Settings) -> ClaudeAgentOptions:
    specs = server_specs(settings)
    return ClaudeAgentOptions(
        **_base_options(ctx, settings),
        system_prompt=(
            "You manage work tickets with the workbench tools and, when available, drive a real "
            "browser with the playwright tools. Confirm what you did."
        ),
        mcp_servers={s.name: s.as_claude_config() for s in specs},
        tools=[],
        allowed_tools=[f"mcp__{s.name}__*" for s in specs],
        permission_mode="dontAsk",
    )


OPTION_BUILDERS = {
    "agent_sdk": agent_sdk_options,
    "subagents": subagents_options,
    "external_mcp": external_mcp_options,
}


# ---------------------------------------------------------------------------- translation


def _result_value(content: Any) -> Any:
    if isinstance(content, list):
        content = "\n".join(c.get("text", "") for c in content if isinstance(c, dict))
    if isinstance(content, str):
        try:
            return json.loads(content)
        except ValueError:
            return content
    return content


class SdkTranslator:
    def __init__(self) -> None:
        self.tool_names: dict[str, str] = {}
        self.subagents: dict[str, str] = {}  # Task tool_use_id -> subagent type
        self.last_agent: str | None = None
        self.result: ResultMessage | None = None

    def _agent(self, parent_id: str | None) -> str:
        return "main" if parent_id is None else self.subagents.get(parent_id, "subagent")

    def __call__(self, msg: Any) -> list[Event]:
        out: list[Event] = []
        if isinstance(msg, AssistantMessage | UserMessage):
            agent = self._agent(msg.parent_tool_use_id)
            if agent != self.last_agent:
                out.append(Event(type="agent", agent=agent))
                self.last_agent = agent
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, ToolUseBlock):
                    self.tool_names[block.id] = block.name
                    if block.name in ("Task", "Agent"):
                        self.subagents[block.id] = block.input.get("subagent_type", "subagent")
                    out.append(
                        Event(
                            type="tool_call",
                            agent=agent,
                            name=short_name(block.name),
                            id=block.id,
                            args=block.input,
                        )
                    )
                elif isinstance(block, TextBlock) and block.text.strip():
                    out.append(Event(type="message", agent=agent, text=block.text))
        elif isinstance(msg, UserMessage) and isinstance(msg.content, list):
            for block in msg.content:
                if isinstance(block, ToolResultBlock):
                    name = short_name(self.tool_names.get(block.tool_use_id, ""))
                    result = _result_value(block.content)
                    if block.is_error:
                        result = {"status": "error", "error": result}
                    out.append(
                        Event(
                            type="tool_result",
                            agent=agent,
                            name=name,
                            id=block.tool_use_id,
                            result=result,
                        )
                    )
        elif isinstance(msg, ResultMessage):
            self.result = msg
        return out
