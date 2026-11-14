"""A small MCP server exposing "external" support tools (weather, ticketing).

MCP (Model Context Protocol) is a standard for exposing tools to any agent runtime over a
transport (stdio or HTTP). This file is the *server*; app/tools/mcp_tools.py is the *client* side
that plugs it into ADK.

Run standalone:
    python -m app.mcp.server            # stdio (what the backend spawns)
    python -m app.mcp.server --http     # streamable-http on :8001/mcp (production shape)

ILLUSTRATION: the tools return canned data. PRODUCTION: same server, real API calls inside the
tool bodies, deployed as its own container and reached via MCP_TRANSPORT=http.
"""

import sys

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("support-tools", host="0.0.0.0", port=8001)

_WEATHER = {
    "berlin": {"temp_c": 14, "condition": "overcast"},
    "london": {"temp_c": 16, "condition": "light rain"},
    "tokyo": {"temp_c": 24, "condition": "sunny"},
}

_TICKETS: dict[str, dict] = {
    "T-1001": {"id": "T-1001", "status": "open", "subject": "Backpack strap broke"},
    "T-1002": {"id": "T-1002", "status": "resolved", "subject": "Refund not received"},
}


@mcp.tool()
def get_weather(city: str) -> dict:
    """Get current weather for a city (useful for trip-planning questions)."""
    data = _WEATHER.get(city.strip().lower())
    if not data:
        return {"status": "not_found", "message": f"no weather data for {city!r}"}
    return {"status": "ok", "city": city, **data}


@mcp.tool()
def lookup_ticket(ticket_id: str) -> dict:
    """Look up a customer support ticket by id, e.g. "T-1001"."""
    ticket = _TICKETS.get(ticket_id.strip().upper())
    if not ticket:
        return {"status": "not_found", "message": f"no ticket {ticket_id!r}"}
    return {"status": "ok", "ticket": ticket}


@mcp.tool()
def create_ticket(subject: str, customer_email: str) -> dict:
    """Open a new support ticket for a customer. Returns the new ticket id."""
    ticket_id = f"T-{1000 + len(_TICKETS) + 1}"
    _TICKETS[ticket_id] = {
        "id": ticket_id,
        "status": "open",
        "subject": subject,
        "customer_email": customer_email,
    }
    return {"status": "ok", "ticket": _TICKETS[ticket_id]}


if __name__ == "__main__":
    mcp.run(transport="streamable-http" if "--http" in sys.argv else "stdio")
