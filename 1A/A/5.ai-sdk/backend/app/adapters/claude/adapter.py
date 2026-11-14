"""Claude adapter: the Agent SDK (three patterns) and the Messages API tool runner (one)."""

import dataclasses
from collections.abc import AsyncIterator, Callable
from typing import Any

from claude_agent_sdk import (
    ClaudeSDKClient,
    delete_session,
    delete_session_via_store,
    fork_session,
    fork_session_via_store,
    get_session_messages,
    get_session_messages_from_store,
    query,
)

from app.adapters.claude.agent_sdk import OPTION_BUILDERS, SdkTranslator
from app.adapters.claude.messages_api import ClientFactory, default_client, run_messages_api
from app.config import Settings
from app.core.adapter import AdapterError, PatternInfo, RunContext
from app.schemas import Event

PATTERNS = [
    PatternInfo(
        "agent_sdk",
        "Claude Code's agent loop with our tools in-process, hooks, and a permission callback.",
        (
            "ClaudeSDKClient",
            "create_sdk_mcp_server + @tool",
            "HookMatcher: UserPromptSubmit / PreToolUse / PostToolUse",
            "can_use_tool",
            "allowed_tools",
            "session_id / resume",
            "env-selected provider",
        ),
    ),
    PatternInfo(
        "subagents",
        "The main agent delegates to researcher and calculator subagents via the Task tool.",
        (
            "query()",
            "AgentDefinition",
            "Task tool",
            "per-subagent tool scoping",
            "forward_subagent_text",
        ),
    ),
    PatternInfo(
        "external_mcp",
        "Our workbench MCP server (and Playwright MCP if enabled) attached as stdio servers.",
        (
            "mcp_servers (stdio)",
            "mcp__<server>__<tool> naming",
            "wildcard allowed_tools",
            "@playwright/mcp",
        ),
    ),
    PatternInfo(
        "messages_api",
        "The bare Messages API tool loop; we own history. Provider = client class.",
        (
            "client.beta.messages.tool_runner",
            "@beta_async_tool",
            "async_mcp_tool",
            "AsyncAnthropic / AsyncAnthropicBedrockMantle / AsyncAnthropicVertex",
        ),
    ),
]


class ClaudeAdapter:
    name = "claude"
    description = "Claude Agent SDK (Claude Code loop) and the Claude Messages API tool runner."

    def __init__(
        self,
        settings: Settings,
        *,
        client_cls: Callable[..., Any] = ClaudeSDKClient,
        query_fn: Callable[..., Any] = query,
        messages_client: ClientFactory = default_client,
    ):
        self.settings = settings
        self.client_cls = client_cls
        self.query_fn = query_fn
        self.messages_client = messages_client
        self._session_store = None

    @property
    def session_store(self):
        """RedisSessionStore when REDIS_URL is set; otherwise sessions live only on local disk."""
        if self._session_store is None and self.settings.redis_url:
            from app.adapters.claude.session_store import RedisSessionStore
            from app.state.cache import redis_client

            self._session_store = RedisSessionStore(redis_client(self.settings.redis_url))
        return self._session_store

    @property
    def workdir(self) -> str:
        return str(self.settings.data_path / "claude_workdir")

    def patterns(self) -> list[PatternInfo]:
        return PATTERNS

    def providers(self) -> list[str]:
        return ["raw", "bedrock", "vertex"]

    async def run(self, ctx: RunContext) -> AsyncIterator[Event]:
        pattern = ctx.request.pattern
        if pattern == "messages_api":
            async for event in run_messages_api(ctx, self.messages_client):
                yield event
            return
        ctx.extras["session_store"] = self.session_store
        options = OPTION_BUILDERS[pattern](ctx, self.settings)
        translate = SdkTranslator()
        if pattern == "agent_sdk":
            # ClaudeSDKClient: a live, bidirectional session (needed for can_use_tool, interrupts,
            # follow-ups on the same connection).
            async with self.client_cls(options=options) as client:
                await client.query(ctx.request.message)
                async for msg in client.receive_response():
                    for event in translate(msg):
                        yield event
        else:
            async for msg in self.query_fn(prompt=ctx.request.message, options=options):
                for event in translate(msg):
                    yield event
        result = translate.result
        if result is None:
            yield Event(type="error", message="the Claude CLI ended without a result")
            return
        ctx.session.native["claude_session_id"] = result.session_id
        if result.is_error:
            yield Event(
                type="error", message=f"claude: {result.subtype}: {result.result or result.errors}"
            )
            return
        yield Event(
            type="done",
            output=result.result,
            data={
                "usage": result.usage,
                "cost_usd": result.total_cost_usd,
                "turns": result.num_turns,
            },
        )

    # ------------------------------------------------------------------ StateOps

    async def history(self, rec, profile) -> list[dict]:
        if rec.pattern == "messages_api":  # stateless API: the history is the one we kept
            return [
                {
                    "role": m["role"],
                    "text": m["content"]
                    if isinstance(m["content"], str)
                    else _blocks_text(m["content"]),
                }
                for m in rec.native.get("messages", [])
            ]
        messages = await self._session_messages(rec)
        return [
            {
                "role": m["type"],
                "uuid": m["uuid"],
                "text": _blocks_text(m["message"].get("content")),
            }
            for m in messages
        ]

    async def checkpoints(self, rec, profile) -> list[dict]:
        """Every transcript message is a fork point (fork_session(up_to_message_id=...))."""
        messages = await self._session_messages(rec)
        return [
            {
                "checkpoint_id": m["uuid"],
                "role": m["type"],
                "text": _blocks_text(m["message"].get("content"))[:80],
            }
            for m in reversed(messages)
        ]

    async def fork(self, rec, profile, checkpoint_id: str, new) -> None:
        sid = self._claude_sid(rec)
        if self.session_store is not None:
            result = await fork_session_via_store(
                self.session_store, sid, directory=self.workdir, up_to_message_id=checkpoint_id
            )
        else:
            result = fork_session(sid, directory=self.workdir, up_to_message_id=checkpoint_id)
        new.native["claude_session_id"] = result.session_id

    async def forget(self, rec, profile) -> None:
        sid = rec.native.get("claude_session_id")
        if not sid:
            return
        if self.session_store is not None:
            await delete_session_via_store(self.session_store, sid, directory=self.workdir)
        else:
            delete_session(sid, directory=self.workdir)

    def _claude_sid(self, rec) -> str:
        sid = rec.native.get("claude_session_id")
        if not sid:
            raise AdapterError("this session has no Claude transcript yet")
        return sid

    async def _session_messages(self, rec) -> list[dict]:
        sid = self._claude_sid(rec)
        if self.session_store is not None:
            msgs = await get_session_messages_from_store(
                self.session_store, sid, directory=self.workdir
            )
        else:
            msgs = get_session_messages(sid, directory=self.workdir)
        return [dataclasses.asdict(m) if dataclasses.is_dataclass(m) else dict(m) for m in msgs]


def _blocks_text(content) -> str:
    if isinstance(content, str):
        return content
    return " ".join(
        b.get("text", "") for b in content or [] if isinstance(b, dict) and b.get("type") == "text"
    )


def build(settings: Settings) -> ClaudeAdapter:
    return ClaudeAdapter(settings)
