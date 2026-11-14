"""Claude Messages API with the SDK's tool runner: the bare agent loop, state kept by us.

Provider = a different client class (not env vars as in the Agent SDK):
  raw      AsyncAnthropic(api_key)
  bedrock  AsyncAnthropicBedrockMantle(aws_region)  Claude in Amazon Bedrock, `anthropic.` model ids
  vertex   AsyncAnthropicVertex(project_id, region)  Claude on Vertex AI

Conversation state lives in our SessionRecord (`native["messages"]`): the Messages API is
stateless, so whoever calls it owns history. ILLUSTRATION: process memory; PRODUCTION: a DB row
per session (Postgres JSONB, DynamoDB, Firestore).
"""

import json
from collections.abc import AsyncIterator, Callable
from contextlib import AsyncExitStack
from typing import Any

from app.adapters.claude.tools import as_beta_tool
from app.core.adapter import RunContext
from app.mcp.clients import server_specs
from app.providers.profile import ProviderProfile
from app.schemas import Event
from app.tools import tools_for

SYSTEM = (
    "You are an engineering research assistant. Use tools instead of guessing. Cite the `source` "
    "of passages you use from search_docs. Be concise."
)

ClientFactory = Callable[[ProviderProfile], Any]


def default_client(profile: ProviderProfile):
    s = profile.settings
    if profile.name == "bedrock":
        from anthropic import AsyncAnthropicBedrockMantle

        return AsyncAnthropicBedrockMantle(aws_region=s.aws_region)
    if profile.name == "vertex":
        from anthropic import AsyncAnthropicVertex

        return AsyncAnthropicVertex(
            project_id=s.google_cloud_project, region=s.vertex_claude_region
        )
    from anthropic import AsyncAnthropic

    return AsyncAnthropic(api_key=s.anthropic_api_key)


def model_for(profile: ProviderProfile) -> str:
    s = profile.settings
    if profile.name == "bedrock":
        return s.bedrock_anthropic_model
    if profile.name == "vertex":
        return s.vertex_claude_model
    return s.anthropic_model


async def mcp_tools(ctx: RunContext, stack: AsyncExitStack) -> list:
    """Our workbench MCP server as runner tools via anthropic.lib.tools.mcp."""
    from anthropic.lib.tools.mcp import async_mcp_tool
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    tools = []
    for spec in server_specs(ctx.settings, include_external=False):
        params = StdioServerParameters(
            command=spec.command, args=spec.args, env=spec.env, cwd=spec.cwd
        )
        read, write = await stack.enter_async_context(stdio_client(params))
        session = await stack.enter_async_context(ClientSession(read, write))
        await session.initialize()
        tools += [async_mcp_tool(t, session) for t in (await session.list_tools()).tools]
    return tools


def _block_dict(block: Any) -> dict:
    return block.model_dump(exclude_none=True) if hasattr(block, "model_dump") else dict(block)


async def run_messages_api(ctx: RunContext, client_factory: ClientFactory) -> AsyncIterator[Event]:
    profile, rec = ctx.provider, ctx.session
    history: list[dict] = rec.native.setdefault("messages", [])
    history.append({"role": "user", "content": ctx.request.message})
    names: dict[str, str] = {}
    last_text: str | None = None
    yield Event(type="agent", agent="claude")
    async with AsyncExitStack() as stack:
        tools = [as_beta_tool(f) for f in tools_for(profile)]
        if ctx.request.options.get("mcp", True):
            tools += await mcp_tools(ctx, stack)
        runner = client_factory(profile).beta.messages.tool_runner(
            model=model_for(profile),
            max_tokens=4096,
            system=SYSTEM,
            tools=tools,
            messages=list(history),
            max_iterations=ctx.settings.max_llm_calls,
        )
        async for message in runner:
            # Mirror history: the runner keeps its own copy and does not expose it.
            history.append(
                {"role": "assistant", "content": [_block_dict(b) for b in message.content]}
            )
            for block in message.content:
                if block.type == "tool_use":
                    names[block.id] = block.name
                    yield Event(
                        type="tool_call",
                        agent="claude",
                        name=block.name,
                        id=block.id,
                        args=block.input,
                    )
                elif block.type == "text" and block.text.strip():
                    last_text = block.text
                    yield Event(type="message", agent="claude", text=block.text)
            response = await runner.generate_tool_call_response()  # cached: tools run once
            if response is not None:
                history.append(response)
                for part in response["content"]:
                    content = part.get("content")
                    text = (
                        content
                        if isinstance(content, str)
                        else " ".join(
                            c.get("text", "") for c in content or [] if isinstance(c, dict)
                        )
                    )
                    try:
                        result = json.loads(text)
                    except ValueError:
                        result = text
                    yield Event(
                        type="tool_result",
                        agent="claude",
                        name=names.get(part["tool_use_id"]),
                        id=part["tool_use_id"],
                        result=result,
                    )
    yield Event(type="done", output=last_text)
