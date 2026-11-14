"""Entry point for ADK's own tooling: the dev UI mounted at /dev-ui, `adk web`, `adk run`.

ADK's loader imports this package and picks up `app` (an ADK App with plugins). It is built from
the same process-wide container as the REST API, so both share sessions, memory, and artifacts.
"""

from app.agents.builder import build_app
from app.container import get_container

app = build_app(get_container())
root_agent = app.root_agent
