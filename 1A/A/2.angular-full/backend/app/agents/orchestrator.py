"""The root agent: an orchestrator that keeps control and calls specialists as tools.

Two ways to compose agents in ADK:
- `tools=[AgentTool(child)]`: the parent calls the child like a function, gets its answer back,
  and keeps talking to the user. Good when the parent should combine results. (Used here.)
- `sub_agents=[child]`: the parent *transfers* the conversation to the child, which then talks to
  the user directly until it transfers back. Good for routing to a persona. (Not used here.)

The "agent loop" itself is ADK's Runner: model call -> function call(s) -> tool result(s) ->
model call ... -> final text. app/services/chat_service.py exposes each step as a TraceEvent.
"""

from google.adk.agents import BaseAgent, LlmAgent
from google.adk.tools import AgentTool

from app.tools.local_tools import calculate, get_current_time


def build_orchestrator(model: str, specialists: list[BaseAgent]) -> LlmAgent:
    return LlmAgent(
        name="orchestrator",
        model=model,
        description="Front-door assistant for Acme Outdoor.",
        instruction=(
            "You are the assistant for Acme Outdoor, an outdoor-gear store.\n"
            "Route work to your tools:\n"
            "- data_agent: anything about customers, orders, revenue, tiers.\n"
            "- knowledge_agent: policies (returns, shipping, warranty, product care), weather, "
            "support tickets.\n"
            "- writer: when the user wants a polished piece of text written.\n"
            "- calculate / get_current_time: math and dates; never do arithmetic in your head.\n"
            "You may call several tools for one question and combine their answers. "
            "Be concise, and say so when something is unknown."
        ),
        tools=[calculate, get_current_time, *[AgentTool(agent=a) for a in specialists]],
    )
