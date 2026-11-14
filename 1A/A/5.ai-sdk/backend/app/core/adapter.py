"""The adapter contract every framework implements.

An adapter turns one RunContext into a stream of neutral Events. Everything framework-specific
(agent classes, session services, model classes, event shapes) stays inside the adapter.
"""

from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Protocol

from app.config import Settings
from app.schemas import Event, RunRequest

if TYPE_CHECKING:
    from app.core.sessions import SessionRecord
    from app.providers.profile import ProviderProfile


@dataclass(frozen=True)
class PatternInfo:
    name: str
    description: str
    components: tuple[str, ...]


@dataclass
class RunContext:
    request: RunRequest
    provider: "ProviderProfile"
    session: "SessionRecord"
    settings: Settings
    # Adapter-private scratch space that lives for one run (e.g. collected usage).
    extras: dict = field(default_factory=dict)


class AgentAdapter(Protocol):
    name: str
    description: str

    def patterns(self) -> list[PatternInfo]: ...

    def providers(self) -> list[str]: ...

    def run(self, ctx: RunContext) -> AsyncIterator[Event]: ...


class AdapterError(Exception):
    """Raised by an adapter for a user-facing problem (bad pattern options, missing config)."""


class StateOps(Protocol):
    """Optional adapter capabilities behind the state API (docs/design/07-state-and-memory.md).

    An adapter implements any subset; the API returns 501 for the rest. Each method reads the
    framework's *own* store, so the answer shows how that framework models state.
    """

    async def history(self, rec: "SessionRecord", profile: "ProviderProfile") -> list[dict]: ...

    async def checkpoints(self, rec: "SessionRecord", profile: "ProviderProfile") -> list[dict]: ...

    async def fork(
        self,
        rec: "SessionRecord",
        profile: "ProviderProfile",
        checkpoint_id: str,
        new: "SessionRecord",
    ) -> None: ...

    async def memories(
        self, user_id: str, profile: "ProviderProfile", query: str
    ) -> list[dict]: ...

    async def forget(self, rec: "SessionRecord", profile: "ProviderProfile") -> None: ...
