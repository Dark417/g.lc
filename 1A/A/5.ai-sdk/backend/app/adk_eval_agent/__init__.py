"""ADK-native view of the `single` pattern, for `adk eval` / AgentEvaluator and `adk web`.

ADK's tooling loads an agent *module* exposing `root_agent`, so this package builds one from the
same pattern code the adapter uses (raw provider, no MCP subprocesses).
"""

from . import agent  # noqa: F401
