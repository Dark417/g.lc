"""MCP server: exposes the compliance knowledge base to any MCP client
(Claude Code, Claude Desktop, Gemini CLI, another ADK agent via McpToolset).

Read-only by design: the backend maps the service token to role "user", so admin writes are
impossible through MCP even if a tool were added by mistake.

    python -m app.server            # stdio (local clients spawn it)
    python -m app.server --http     # streamable-http on :$PORT/mcp (Cloud Run)
"""

from mcp.server.fastmcp import FastMCP

from app.client import BackendClient
from app.config import get_settings

INSTRUCTIONS = (
    "Tools for a company's compliance knowledge base. Use check_proposal to decide whether "
    "something is allowed: it returns a verdict (COMPLIANT, CONDITIONALLY_COMPLIANT, "
    "NON_COMPLIANT, NEEDS_MORE_INFO) with per-rule findings and evidence. Hard rules cannot be "
    "waived; flexible rules list conditions or who can approve an exception. Report the verdict "
    "as returned; do not soften it."
)


def _slim_rule(r: dict) -> dict:
    keys = ("code", "title", "statement", "severity", "category", "rationale", "exception_process")
    return {k: r.get(k, "") for k in keys}


def build_server(client: BackendClient | None = None) -> FastMCP:
    settings = get_settings()
    backend = client or BackendClient(settings)
    mcp = FastMCP(
        "compliance-kb", instructions=INSTRUCTIONS, host=settings.host, port=settings.port
    )

    @mcp.tool()
    async def check_proposal(proposal: str, context: str = "") -> dict:
        """Check whether a proposal complies with company rules. Include every relevant fact
        (audience, data collected, markets, approvals obtained). Returns the verdict with
        blocking rules, conditions, missing information, and per-rule findings with evidence."""
        v = await backend.assess(proposal, context)
        v["findings"] = [f for f in v.get("findings", []) if f.get("status") != "not_applicable"]
        return v

    @mcp.tool()
    async def search_rules(query: str) -> list[dict]:
        """Find active compliance rules relevant to a topic, e.g. "children's data" or "discounts"."""
        return [_slim_rule(r) for r in await backend.search_rules(query)]

    @mcp.tool()
    async def get_rule(code: str) -> dict:
        """Get one rule by code, e.g. "PRIV-003"."""
        r = await backend.get_rule(code)
        return _slim_rule(r) if r else {"status": "not_found", "code": code}

    @mcp.tool()
    async def list_rules(category: str = "", severity: str = "") -> list[dict]:
        """List active rules. Filter by category (e.g. "privacy") and severity ("hard" or "flexible")."""
        return [
            {k: r[k] for k in ("code", "title", "severity", "category")}
            for r in await backend.list_rules(category, severity)
        ]

    @mcp.tool()
    async def list_documents(category: str = "") -> list[dict]:
        """List compliance documents (id, title, category, status)."""
        return [
            {k: d[k] for k in ("id", "title", "category", "format", "status")}
            for d in await backend.list_documents(category)
        ]

    @mcp.tool()
    async def get_document_summary(document_id: str) -> dict:
        """Summary, key points, and outline of one document (use list_documents for ids)."""
        d = await backend.get_document(document_id)
        if d is None:
            return {"status": "not_found", "document_id": document_id}
        keys = (
            "id",
            "title",
            "category",
            "summary",
            "key_points",
            "outline",
            "extracted_rule_codes",
        )
        return {k: d.get(k) for k in keys}

    @mcp.tool()
    async def search_documents(query: str) -> list[dict]:
        """Search policy documents for passages relevant to a question, with source labels."""
        return await backend.search_documents(query)

    return mcp


def main(argv: list[str] | None = None) -> None:
    import os
    import sys

    argv = sys.argv[1:] if argv is None else argv
    settings = get_settings()
    if "PORT" in os.environ:  # Cloud Run
        settings.port = int(os.environ["PORT"])
    http = "--http" in argv or settings.transport == "http"
    build_server().run(transport="streamable-http" if http else "stdio")


if __name__ == "__main__":
    main()
