"""`workbench` MCP server: tickets in SQLite + a text utility.

Every framework attaches it through its own MCP client (see app/mcp/clients.py), so this is
the one tool surface that is *not* wrapped by us; each framework discovers the tools itself.

Run:
  python -m app.mcp.server                 stdio (spawned by an agent)
  python -m app.mcp.server --http 8765     streamable HTTP at http://127.0.0.1:8765/mcp
# PRODUCTION: deploy the HTTP form behind AgentCore Gateway (AWS) or on Cloud Run (GCP) with
# auth in front; clients switch from stdio params to a URL.
"""

import argparse
import sqlite3
import time
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from app.config import get_settings

mcp = FastMCP("workbench")


def _db() -> sqlite3.Connection:
    path = Path(get_settings().data_path) / "tickets.db"
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute(
        "CREATE TABLE IF NOT EXISTS tickets (id INTEGER PRIMARY KEY, title TEXT, body TEXT, "
        "priority TEXT, status TEXT DEFAULT 'open', created REAL)"
    )
    return conn


@mcp.tool()
def create_ticket(title: str, body: str, priority: str = "medium") -> dict:
    """Create a work ticket (e.g. a follow-up to evaluate a service). Returns the new ticket.

    Args:
        title: Short summary.
        body: Details and links.
        priority: low, medium, or high.
    """
    if priority not in {"low", "medium", "high"}:
        priority = "medium"
    with _db() as conn:
        cur = conn.execute(
            "INSERT INTO tickets(title, body, priority, created) VALUES (?,?,?,?)",
            (title, body, priority, time.time()),
        )
        row = conn.execute("SELECT * FROM tickets WHERE id=?", (cur.lastrowid,)).fetchone()
    return dict(row)


@mcp.tool()
def list_tickets(status: str = "open") -> list[dict]:
    """List tickets by status.

    Args:
        status: open, closed, or all.
    """
    with _db() as conn:
        if status == "all":
            rows = conn.execute("SELECT * FROM tickets ORDER BY id DESC LIMIT 50").fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM tickets WHERE status=? ORDER BY id DESC LIMIT 50", (status,)
            ).fetchall()
    return [dict(r) for r in rows]


@mcp.tool()
def get_ticket(ticket_id: int) -> dict:
    """Get one ticket by id.

    Args:
        ticket_id: The ticket number.
    """
    with _db() as conn:
        row = conn.execute("SELECT * FROM tickets WHERE id=?", (ticket_id,)).fetchone()
    return dict(row) if row else {"error": f"ticket {ticket_id} not found"}


@mcp.tool()
def word_count(text: str) -> dict:
    """Count words, characters, and lines in a text.

    Args:
        text: Any text.
    """
    return {"words": len(text.split()), "characters": len(text), "lines": text.count("\n") + 1}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--http", type=int, metavar="PORT", help="serve streamable HTTP")
    args = parser.parse_args()
    if args.http:
        mcp.settings.port = args.http
        mcp.run(transport="streamable-http")
    else:
        mcp.run()  # stdio


if __name__ == "__main__":
    main()
