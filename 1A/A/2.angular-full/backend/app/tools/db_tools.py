"""Tools that let the agent read the app database.

Built by a factory so the DB path is injected (tests use a temp file) and the tool functions
stay plain functions with good docstrings, which is what the model sees.
"""

import re
import sqlite3
from collections.abc import Callable

from app.db.database import connect, rows_to_dicts

_FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|replace|attach|pragma|vacuum)\b", re.I
)
_MAX_ROWS = 50


def build_db_tools(db_path: str) -> list[Callable]:
    def describe_schema() -> dict:
        """Describe the database tables and columns. Call this before writing SQL."""
        with connect(db_path) as conn:
            rows = conn.execute(
                "SELECT name, sql FROM sqlite_master "
                "WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            ).fetchall()
        return {"status": "ok", "tables": {r["name"]: r["sql"] for r in rows}}

    def list_customers(tier: str) -> dict:
        """List customers, optionally filtered by subscription tier.

        Args:
            tier: "free", "pro", "enterprise", or "" for all tiers.
        """
        sql = "SELECT id, name, email, tier, created_at FROM customers"
        params: tuple = ()
        if tier:
            sql += " WHERE tier = ?"
            params = (tier,)
        with connect(db_path) as conn:
            rows = conn.execute(sql + " ORDER BY id", params).fetchall()
        return {"status": "ok", "customers": rows_to_dicts(rows)}

    def get_customer_orders(customer_name: str) -> dict:
        """Get all orders for a customer by (partial, case-insensitive) name.

        Args:
            customer_name: e.g. "Ada" or "Ada Lovelace".
        """
        with connect(db_path) as conn:
            rows = conn.execute(
                """
                SELECT o.id, o.product, o.amount_usd, o.status, o.ordered_at, c.name AS customer
                FROM orders o JOIN customers c ON c.id = o.customer_id
                WHERE lower(c.name) LIKE lower(?) ORDER BY o.ordered_at DESC
                """,
                (f"%{customer_name}%",),
            ).fetchall()
        if not rows:
            return {
                "status": "not_found",
                "message": f"no orders for customer like {customer_name!r}",
            }
        return {"status": "ok", "orders": rows_to_dicts(rows)}

    def run_sql_query(sql: str) -> dict:
        """Run a read-only SQL SELECT for questions the other tools can't answer.

        Call describe_schema first. Only SELECT statements are allowed; results are capped
        at 50 rows.

        Args:
            sql: A single SELECT statement,
                e.g. "SELECT tier, COUNT(*) FROM customers GROUP BY tier".
        """
        cleaned = sql.strip().rstrip(";")
        if not cleaned.lower().startswith("select") or ";" in cleaned or _FORBIDDEN.search(cleaned):
            return {"status": "error", "message": "only a single SELECT statement is allowed"}
        try:
            with connect(db_path) as conn:
                conn.execute("PRAGMA query_only = ON")  # belt and braces: SQLite refuses writes
                rows = conn.execute(cleaned).fetchmany(_MAX_ROWS)
        except sqlite3.Error as e:
            return {"status": "error", "message": str(e)}
        return {"status": "ok", "row_count": len(rows), "rows": rows_to_dicts(rows)}

    return [describe_schema, list_customers, get_customer_orders, run_sql_query]
