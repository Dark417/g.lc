"""The ADK agent definition.

Kept free of HTTP concerns so it can be run with `adk web` / `adk run` for debugging,
and reused by the eval tooling in later projects.
"""

from google.adk.agents import Agent

from app.config import get_settings


def build_agent() -> Agent:
    settings = get_settings()
    return Agent(
        name="chatbot",
        model=settings.model,
        description="A friendly general-purpose assistant.",
        instruction=(
            "You are a concise, friendly assistant. Answer directly. "
            "If you don't know something, say so. Keep replies under 150 words "
            "unless the user asks for detail."
        ),
    )


# `adk web` and `adk run` look for a module-level `root_agent`.
root_agent = build_agent()
