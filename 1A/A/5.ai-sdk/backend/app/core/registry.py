"""AdapterRegistry: framework name -> adapter, imported lazily.

Importing app.main does not import ADK, LangGraph, Strands, and the Claude SDK. Each adapter
module is imported on first use, so startup is fast and a broken optional dependency disables
one framework instead of the whole service.
"""

import importlib
import logging
from collections.abc import Callable

from app.config import Settings
from app.core.adapter import AgentAdapter

log = logging.getLogger(__name__)

# name -> "module:factory". The factory takes Settings and returns an adapter.
BUILTIN_ADAPTERS: dict[str, str] = {
    "adk": "app.adapters.adk.adapter:build",
    "langgraph": "app.adapters.langgraph.adapter:build",
    "strands": "app.adapters.strands.adapter:build",
    "claude": "app.adapters.claude.adapter:build",
    "diy": "app.adapters.diy.adapter:build",
}


class UnknownTarget(LookupError):
    pass


class AdapterRegistry:
    def __init__(self, settings: Settings, specs: dict[str, str] | None = None):
        self._settings = settings
        self._specs = dict(BUILTIN_ADAPTERS if specs is None else specs)
        self._instances: dict[str, AgentAdapter] = {}
        self._errors: dict[str, str] = {}

    def register(self, adapter: AgentAdapter) -> None:
        """Register an instance directly (tests, plugins)."""
        self._instances[adapter.name] = adapter
        self._specs.setdefault(adapter.name, "")
        self._errors.pop(adapter.name, None)

    def names(self) -> list[str]:
        return list(self._specs)

    def get(self, name: str) -> AgentAdapter:
        if name in self._instances:
            return self._instances[name]
        spec = self._specs.get(name)
        if not spec:
            raise UnknownTarget(f"unknown framework {name!r}; known: {', '.join(self._specs)}")
        module_name, _, attr = spec.partition(":")
        try:
            factory: Callable[[Settings], AgentAdapter] = getattr(
                importlib.import_module(module_name), attr
            )
            adapter = factory(self._settings)
        except Exception as e:  # import or construction failure: report, don't crash the app
            self._errors[name] = f"{type(e).__name__}: {e}"
            log.exception("adapter %s failed to load", name)
            raise
        self._instances[name] = adapter
        return adapter

    def error(self, name: str) -> str | None:
        return self._errors.get(name)

    def resolve(self, framework: str, pattern: str, provider: str) -> AgentAdapter:
        adapter = self.get(framework)
        names = [p.name for p in adapter.patterns()]
        if pattern not in names:
            raise UnknownTarget(
                f"{framework} has no pattern {pattern!r}; patterns: {', '.join(names)}"
            )
        if provider not in adapter.providers():
            raise UnknownTarget(f"{framework} does not support provider {provider!r}")
        return adapter
