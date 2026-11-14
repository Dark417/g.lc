"""RunScope: per-run context for framework-neutral tools.

Tools are plain functions shared by four frameworks, so they cannot take ADK's ToolContext or
LangGraph's RunnableConfig. RunService sets this ContextVar before the adapter starts; asyncio
copies it into every task and to_thread call the frameworks spawn, so tools see the right user,
session, and provider services.
"""

from contextvars import ContextVar
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.providers.profile import ProviderProfile


@dataclass(frozen=True)
class RunScope:
    user_id: str
    session_id: str
    provider: "ProviderProfile"


_current: ContextVar[RunScope | None] = ContextVar("run_scope", default=None)
_default: RunScope | None = None


def set_default_scope(scope: RunScope) -> None:
    """For hosts that run one agent outside RunService (ADK AgentEvaluator, Vertex Agent Engine).

    All callers then share one user identity, so per-user memory is not isolated there.
    """
    global _default
    _default = scope


def set_scope(scope: RunScope):
    return _current.set(scope)


def reset_scope(token) -> None:
    try:
        _current.reset(token)
    except ValueError:  # generator closed from another context (client disconnect): nothing to undo
        pass


def current_scope() -> RunScope:
    scope = _current.get() or _default
    if scope is None:
        raise RuntimeError("tool called outside a run (no RunScope set)")
    return scope
