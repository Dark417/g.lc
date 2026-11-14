"""Agent callbacks.

- before_agent: role gating layer 1. Resolve the role from the server-side admin list by
  user_id and store it in user-scoped state. Works for the portal and for ADK's dev UI alike.
- before_tool: role gating layer 3. Deny admin tools for non-admins even if the model tries.
- after_agent: write the turn into long-term memory.
"""

import logging

from app.agents.toolsets import ROLE_KEY

log = logging.getLogger(__name__)


def make_before_agent(admins: set[str]):
    def before_agent(callback_context):
        role = "admin" if (callback_context.user_id or "").lower() in admins else "user"
        if callback_context.state.get(ROLE_KEY) != role:
            callback_context.state[ROLE_KEY] = role
        return None

    return before_agent


def make_before_tool(admin_tool_names: set[str]):
    def before_tool(tool, args, tool_context):
        if tool.name in admin_tool_names and tool_context.state.get(ROLE_KEY) != "admin":
            log.warning("denied %s for %s", tool.name, tool_context.user_id)
            return {"status": "forbidden", "message": f"{tool.name} requires the admin role."}
        return None

    return before_tool


async def save_to_memory(callback_context):
    try:
        await callback_context.add_session_to_memory()
    except Exception:  # memory is best-effort; never fail the user's turn over it
        log.exception("add_session_to_memory failed")
    return None
