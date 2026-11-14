from app.db.database import init_db
from app.tools.db_tools import build_db_tools
from app.tools.local_tools import calculate, get_current_time


def test_calculate():
    assert calculate("12 * (3 + 4)")["result"] == 84
    assert calculate("__import__('os')")["status"] == "error"
    assert calculate("1/0")["status"] == "error"


def test_get_current_time():
    assert get_current_time("UTC")["status"] == "ok"
    assert get_current_time("Mars/Olympus")["status"] == "error"


def test_db_tools(tmp_path):
    db = str(tmp_path / "app.db")
    init_db(db)
    init_db(db)  # idempotent
    describe_schema, list_customers, get_customer_orders, run_sql_query = build_db_tools(db)

    assert set(describe_schema()["tables"]) == {"customers", "orders"}
    assert [c["name"] for c in list_customers("enterprise")["customers"]] == ["Ada Lovelace"]
    assert len(list_customers("")["customers"]) == 5
    assert len(get_customer_orders("ada")["orders"]) == 3
    assert get_customer_orders("nobody")["status"] == "not_found"

    agg = run_sql_query("SELECT tier, COUNT(*) AS n FROM customers GROUP BY tier ORDER BY tier")
    assert agg["rows"] == [
        {"tier": "enterprise", "n": 1},
        {"tier": "free", "n": 2},
        {"tier": "pro", "n": 2},
    ]
    assert run_sql_query("DELETE FROM orders")["status"] == "error"
    assert run_sql_query("SELECT 1; DROP TABLE orders")["status"] == "error"
    assert run_sql_query("SELECT * FROM nope")["status"] == "error"
