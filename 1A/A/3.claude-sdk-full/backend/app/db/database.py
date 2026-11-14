"""SQLite access. stdlib sqlite3: boring, zero deps, fine for a tutorial and for read-mostly tools.

PRODUCTION: Postgres via SQLAlchemy/psycopg with a connection pool, and a read-only DB role for
anything the agent can run. Never hand the agent a read-write connection.
"""

import sqlite3
from pathlib import Path

from app.db import seed

SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def connect(db_path: str) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str) -> None:
    """Create tables and insert mock data if the DB is empty. Safe to call on every startup."""
    with connect(db_path) as conn:
        conn.executescript(SCHEMA_PATH.read_text())
        if conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0] == 0:
            conn.executemany("INSERT INTO customers VALUES (?,?,?,?,?)", seed.CUSTOMERS)
            conn.executemany("INSERT INTO orders VALUES (?,?,?,?,?,?)", seed.ORDERS)


def rows_to_dicts(rows: list[sqlite3.Row]) -> list[dict]:
    return [dict(r) for r in rows]
