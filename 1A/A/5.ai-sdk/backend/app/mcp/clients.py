"""MCP server specs, in one neutral shape, converted by each adapter into its client type.

workbench   our server (app/mcp/server.py), always on, stdio
playwright  Microsoft's Playwright MCP (`npx @playwright/mcp`), optional, stdio
            -> the agent drives a browser step by step (navigate, snapshot, click, type)
            instead of our one-shot `browse` tool.
"""

import sys
from dataclasses import dataclass, field

from app.config import BACKEND_DIR, Settings


@dataclass(frozen=True)
class McpServerSpec:
    name: str
    command: str
    args: list[str]
    env: dict[str, str] = field(default_factory=dict)
    cwd: str | None = None
    description: str = ""

    def as_claude_config(self) -> dict:
        """Claude Agent SDK `mcp_servers` entry (stdio)."""
        return {"type": "stdio", "command": self.command, "args": self.args, "env": self.env}


def workbench(settings: Settings) -> McpServerSpec:
    return McpServerSpec(
        name="workbench",
        command=sys.executable,
        args=["-m", "app.mcp.server"],
        env=settings.subprocess_env({"PYTHONPATH": str(BACKEND_DIR)}),
        cwd=str(BACKEND_DIR),
        description="tickets + word_count (our FastMCP server)",
    )


def playwright(settings: Settings) -> McpServerSpec:
    args = ["-y", "@playwright/mcp@latest", "--headless", "--isolated"]
    if settings.playwright_chromium_path:
        args += ["--executable-path", settings.playwright_chromium_path]
    return McpServerSpec(
        name="playwright",
        command="npx",
        args=args,
        env=settings.subprocess_env(),
        description="Playwright MCP: browser_navigate, browser_snapshot, browser_click, ...",
    )


def server_specs(settings: Settings, include_external: bool = True) -> list[McpServerSpec]:
    specs = [workbench(settings)]
    if include_external and settings.playwright_mcp_enabled:
        specs.append(playwright(settings))
    return specs
