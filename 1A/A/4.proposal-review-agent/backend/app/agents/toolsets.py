"""Role gating, layer 2 of 3: admins' tools are invisible to everyone else.

ADK asks each toolset for its tools on every model call, passing the current context. We return
the admin tools only when the session's `user:role` (set server-side by the before_agent
callback) is "admin", so a regular user's model never even sees their schemas.
"""

from collections.abc import Callable

from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.tools import FunctionTool
from google.adk.tools.base_toolset import BaseToolset

ROLE_KEY = "user:role"


class RoleGatedToolset(BaseToolset):
    def __init__(self, functions: list[Callable], *, role: str = "admin") -> None:
        super().__init__()
        self._role = role
        self._tools = [FunctionTool(f) for f in functions]

    @property
    def names(self) -> set[str]:
        return {t.name for t in self._tools}

    async def get_tools(self, readonly_context: ReadonlyContext | None = None) -> list:
        if readonly_context is not None and readonly_context.state.get(ROLE_KEY) == self._role:
            return list(self._tools)
        return []

    async def close(self) -> None:
        return None
