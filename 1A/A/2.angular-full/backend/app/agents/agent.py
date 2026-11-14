"""Module-level `root_agent` for ADK's own tooling: `adk web`, `adk run`, `adk eval`.

The FastAPI app does NOT import this; it builds the same tree in app/main.py so it controls
startup order. This module exists so ADK's CLI and evaluator can find the agent by import path:
    uv run adk web app/agents
    uv run adk eval app/agents evals/tools
"""

from app.agents.factory import build_root_agent
from app.config import get_settings
from app.db.database import init_db
from app.rag.factory import build_retriever
from app.tools.mcp_tools import build_mcp_toolset

_settings = get_settings()
init_db(_settings.db_path)

root_agent = build_root_agent(
    _settings,
    retriever=build_retriever(_settings),
    mcp_toolset=build_mcp_toolset(_settings),
)
