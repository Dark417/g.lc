"""Specialist: answers questions about customers and orders using the DB tools."""

from collections.abc import Callable

from google.adk.agents import LlmAgent


def build_data_agent(model: str, db_tools: list[Callable]) -> LlmAgent:
    return LlmAgent(
        name="data_agent",
        model=model,
        description=(
            "Answers questions about customers, orders, revenue and subscription tiers by "
            "querying the company database."
        ),
        instruction=(
            "You answer questions about customers and orders using your tools. "
            "Prefer list_customers and get_customer_orders. For aggregates or anything else, call "
            "describe_schema then run_sql_query with a single SELECT. "
            "Reply with the facts you found, compactly. Never invent data; if a tool returns "
            "not_found or error, say so."
        ),
        tools=db_tools,
    )
