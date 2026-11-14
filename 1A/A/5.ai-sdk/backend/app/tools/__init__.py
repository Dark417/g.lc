"""Framework-neutral tools.

Each is an async function with typed parameters and a Google-style docstring. Adapters wrap them:
  ADK        FunctionTool(fn)
  LangGraph  StructuredTool.from_function(coroutine=fn, parse_docstring=True)
  Strands    strands.tool(fn)
  Claude SDK @claude_agent_sdk.tool(...) inside create_sdk_mcp_server
  Messages   anthropic.beta_async_tool(fn)
"""

import inspect
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any

from app.tools.basic import calculator, current_time
from app.tools.browser import browse
from app.tools.cli import run_cli
from app.tools.code import run_code
from app.tools.knowledge import recall, remember, search_docs

if TYPE_CHECKING:
    from app.providers.profile import ProviderProfile

ToolFn = Callable[..., Awaitable[dict[str, Any]]]

ALL_TOOLS: dict[str, ToolFn] = {
    "calculator": calculator,
    "current_time": current_time,
    "search_docs": search_docs,
    "remember": remember,
    "recall": recall,
    "run_cli": run_cli,
    "browse": browse,
    "run_code": run_code,
}

# Tools that act on the outside world; frameworks put an approval or policy gate in front of them.
SENSITIVE = {"run_cli", "run_code"}


def tools_for(provider: "ProviderProfile", names: list[str] | None = None) -> list[ToolFn]:
    """The neutral tool set for a run. `run_code` only where a sandbox exists."""
    chosen = names or list(ALL_TOOLS)
    return [
        ALL_TOOLS[n]
        for n in chosen
        if n in ALL_TOOLS and (n != "run_code" or provider.code_sandbox is not None)
    ]


def describe() -> list[dict[str, str]]:
    return [
        {"name": n, "description": (inspect.getdoc(f) or "").split("\n")[0]}
        for n, f in ALL_TOOLS.items()
    ]


__all__ = ["ALL_TOOLS", "SENSITIVE", "ToolFn", "describe", "tools_for", *ALL_TOOLS]
