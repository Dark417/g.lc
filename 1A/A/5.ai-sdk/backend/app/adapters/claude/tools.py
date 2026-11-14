"""Neutral tools -> the two Claude tool shapes.

Agent SDK: custom tools are MCP tools. `@tool(name, description, schema)` + create_sdk_mcp_server
          runs them in-process; Claude sees them as mcp__tools__<name>.
Messages API: `beta_async_tool` builds the JSON schema from the signature + docstring; the tool
          runner calls it and feeds the result back.
"""

import functools
import inspect
import json
from typing import Any

from anthropic import beta_async_tool
from claude_agent_sdk import SdkMcpTool, create_sdk_mcp_server, tool
from pydantic import create_model

from app.tools import ToolFn

SERVER = "tools"


def mcp_name(fn_name: str, server: str = SERVER) -> str:
    return f"mcp__{server}__{fn_name}"


def short_name(name: str) -> str:
    """mcp__tools__calculator -> calculator (for neutral events and eval trajectories)."""
    return name.split("__")[-1] if name.startswith("mcp__") else name


def _json_schema(fn: ToolFn) -> dict[str, Any]:
    params = inspect.signature(fn).parameters
    model = create_model(fn.__name__, **{n: (p.annotation, ...) for n, p in params.items()})
    return model.model_json_schema()


def as_sdk_tool(fn: ToolFn) -> SdkMcpTool:
    @tool(fn.__name__, inspect.getdoc(fn) or fn.__name__, _json_schema(fn))
    async def handler(args: dict) -> dict:
        result = await fn(**args)
        return {"content": [{"type": "text", "text": json.dumps(result, default=str)}]}

    return handler


def sdk_server(functions: list[ToolFn]):
    return create_sdk_mcp_server(
        name=SERVER, version="0.1.0", tools=[as_sdk_tool(f) for f in functions]
    )


def as_beta_tool(fn: ToolFn):
    """Our tools return dicts; the runner wants text, so serialise. functools.wraps keeps the
    signature and docstring the schema is built from."""

    @functools.wraps(fn)
    async def wrapper(**kwargs):
        return json.dumps(await fn(**kwargs), default=str)

    return beta_async_tool(wrapper)
