"""ADK callbacks (per agent) and a plugin (per app).

Callbacks: attached to individual agents. Returning a value from a before_* callback skips
the real step: before_tool returning a dict replaces the tool call with that result.
Plugin: registered once on the App; the same hooks fire for every agent, sub-agent, and tool.
"""

import logging
from datetime import UTC, datetime
from typing import Any

from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.plugins.base_plugin import BasePlugin
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext

log = logging.getLogger(__name__)


def add_run_context(callback_context: CallbackContext, llm_request: LlmRequest) -> None:
    """before_model_callback: inject dynamic context into every model call of this agent."""
    llm_request.append_instructions(
        [
            f"Current UTC time: {datetime.now(UTC):%Y-%m-%d %H:%M}. User id: {callback_context.user_id}."
        ]
    )
    return None  # continue with the (modified) request


def tool_policy(deny: set[str]):
    """before_tool_callback factory: deny tools by name for this run (RunRequest.options.deny_tools).

    Enforcement belongs here, not in the prompt: the model may still *ask* for a denied tool.
    """

    def before_tool(tool: BaseTool, args: dict[str, Any], tool_context: ToolContext):
        if tool.name in deny:
            return {"status": "denied", "error": f"tool {tool.name!r} is disabled by policy"}
        return None

    return before_tool


class AuditPlugin(BasePlugin):
    """App-wide: logs every model and tool call and totals token usage per invocation."""

    def __init__(self) -> None:
        super().__init__(name="audit")
        self.usage: dict[str, dict[str, int]] = {}

    async def after_model_callback(
        self, *, callback_context: CallbackContext, llm_response: LlmResponse
    ) -> LlmResponse | None:
        um = llm_response.usage_metadata
        if um is not None:
            u = self.usage.setdefault(
                callback_context.invocation_id, {"input_tokens": 0, "output_tokens": 0}
            )
            u["input_tokens"] += um.prompt_token_count or 0
            u["output_tokens"] += um.candidates_token_count or 0
        return None

    async def before_tool_callback(
        self, *, tool: BaseTool, tool_args: dict[str, Any], tool_context: ToolContext
    ) -> dict | None:
        log.info("adk tool %s by %s args=%s", tool.name, tool_context.agent_name, list(tool_args))
        return None
