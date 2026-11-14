"""Strands adapter: build the Agent / Swarm / Graph, attach MCP clients, stream events."""

import asyncio
from collections.abc import AsyncIterator
from contextlib import AsyncExitStack

from app.adapters.strands.models import StrandsModelFactory, default_strands_model
from app.adapters.strands.patterns import PATTERNS, StrandsKit
from app.adapters.strands.translate import TranslateState, final_output, translate
from app.config import Settings
from app.core.adapter import PatternInfo, RunContext
from app.mcp.clients import server_specs
from app.schemas import Event


async def open_mcp_clients(settings: Settings, stack: AsyncExitStack) -> list:
    """Start one Strands MCPClient per server and return their tools.

    MCPClient runs its MCP session on a background thread; start/stop block, so they go to a
    worker thread. The exit stack stops every client after the run.
    """
    from mcp import StdioServerParameters
    from mcp.client.stdio import stdio_client
    from strands.tools.mcp import MCPClient

    tools = []
    for spec in server_specs(settings):
        params = StdioServerParameters(
            command=spec.command, args=spec.args, env=spec.env, cwd=spec.cwd
        )
        client = MCPClient(lambda p=params: stdio_client(p))
        await asyncio.to_thread(client.start)
        stack.push_async_callback(asyncio.to_thread, client.stop, None, None, None)
        tools.extend(await asyncio.to_thread(client.list_tools_sync))
    return tools


class StrandsAdapter:
    name = "strands"
    description = "Strands Agents (AWS): model-driven loop, hooks, sessions, Swarm and Graph."

    def __init__(self, settings: Settings, model_factory: StrandsModelFactory | None = None):
        self.settings = settings
        self.model_factory = model_factory or default_strands_model

    def patterns(self) -> list[PatternInfo]:
        return [p.info for p in PATTERNS.values()]

    def providers(self) -> list[str]:
        return ["raw", "bedrock", "vertex"]

    async def run(self, ctx: RunContext) -> AsyncIterator[Event]:
        req, profile = ctx.request, ctx.provider
        pattern = PATTERNS[req.pattern]
        async with AsyncExitStack() as stack:
            mcp_tools = (
                await open_mcp_clients(self.settings, stack)
                if pattern.uses_mcp and req.options.get("mcp", True)
                else []
            )
            kit = StrandsKit(
                profile=profile,
                settings=self.settings,
                options=req.options,
                model_for=lambda role: self.model_factory(profile, req.vendor, role),
                session_id=ctx.session.id,
                user_id=req.user_id,
                mcp_tools=mcp_tools,
            )
            runnable = pattern.build(kit)
            st = TranslateState()
            default_agent = getattr(runnable, "name", None) or req.pattern
            async for raw in runnable.stream_async(req.message):
                for event in translate(raw, default_agent, st):
                    yield event
            yield Event(type="done", output=final_output(st.result), data=_usage(st.result))

    # ------------------------------------------------------------------ StateOps

    async def history(self, rec, profile) -> list[dict]:
        """Read straight from the session repository (File / S3 / AgentCore), as a new Agent would."""
        from app.adapters.strands.memory import AGENT_ID
        from app.adapters.strands.state import session_manager

        sm = session_manager(profile.name, self.settings, rec.id, rec.user_id)
        agent_id = AGENT_ID if rec.pattern == "memory" else "default"
        messages = await asyncio.to_thread(sm.list_messages, rec.id, agent_id)
        stored = await asyncio.to_thread(sm.read_agent, rec.id, agent_id)
        out = []
        for m in messages:
            for block in m.message.get("content", []):
                if "text" in block:
                    out.append({"role": m.message["role"], "text": block["text"]})
                elif "toolUse" in block:
                    out.append({"role": "assistant", "tool_call": block["toolUse"]["name"]})
        return out + [{"role": "state", "state": dict(stored.state) if stored else {}}]

    async def forget(self, rec, profile) -> None:
        from app.adapters.strands.state import session_manager

        sm = session_manager(profile.name, self.settings, rec.id, rec.user_id)
        await asyncio.to_thread(sm.delete_session, rec.id)


def _usage(result) -> dict | None:
    usage = getattr(result, "accumulated_usage", None)
    if usage is None:
        metrics = getattr(result, "metrics", None)
        usage = getattr(metrics, "accumulated_usage", None)
    return {"usage": dict(usage)} if usage else None


def build(settings: Settings) -> StrandsAdapter:
    return StrandsAdapter(settings)
